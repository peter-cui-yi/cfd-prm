"""
Step Scorer for CFD-PRM

Qwen2.5-VL based step scorer with LoRA fine-tuning.
Outputs step-level scores for process reward modeling.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from peft import LoraConfig, get_peft_model


class StepScorer(nn.Module):
    """
    Qwen2.5-VL based step scorer for CFD-PRM.

    Takes (image, step_text) pairs and outputs scalar scores.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct",
        lora_r: int = 64,
        lora_alpha: float = 128,
        lora_dropout: float = 0.05,
        lora_target_modules: Optional[List[str]] = None,
        freeze_vision: bool = True,
        score_head_hidden_size: int = 256,
    ):
        """
        Args:
            model_name: HuggingFace model name
            lora_r: LoRA rank
            lora_alpha: LoRA alpha scaling
            lora_dropout: LoRA dropout
            lora_target_modules: Target modules for LoRA
            freeze_vision: Whether to freeze vision encoder
            score_head_hidden_size: Hidden size of score prediction head
        """
        super().__init__()

        # Base model
        self.base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        # Freeze vision encoder if requested
        if freeze_vision:
            for param in self.base_model.visual.parameters():
                param.requires_grad = False

        # Apply LoRA to language model
        if lora_target_modules is None:
            lora_target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ]

        lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=lora_target_modules,
        )

        self.base_model.model = get_peft_model(
            self.base_model.model,
            lora_config,
            adapter_name="default",
        )

        # Score prediction head
        hidden_size = self.base_model.config.hidden_size
        self.score_head = nn.Sequential(
            nn.Linear(hidden_size, score_head_hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(score_head_hidden_size, 1),
        )

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        pixel_values: Optional[torch.FloatTensor] = None,
        image_grid_thw: Optional[torch.LongTensor] = None,
    ) -> torch.FloatTensor:
        """
        Compute step scores.

        Args:
            input_ids: [batch_size, seq_len] input token ids
            attention_mask: [batch_size, seq_len] attention mask
            pixel_values: [batch_size, num_patches, patch_dim] image features
            image_grid_thw: [num_images, 3] image grid dimensions

        Returns:
            scores: [batch_size] scalar scores in [0, 1]
        """
        # Get hidden states from base model
        outputs = self.base_model.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            image_grid_thw=image_grid_thw,
            output_hidden_states=True,
        )

        # Use last hidden state
        hidden_states = outputs.hidden_states[-1]  # [batch_size, seq_len, hidden_size]

        # Mean pooling over sequence (excluding padding)
        mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
        sum_embeddings = (hidden_states * mask_expanded).sum(dim=1)
        sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
        pooled = sum_embeddings / sum_mask  # [batch_size, hidden_size]

        # Predict score
        logits = self.score_head(pooled)  # [batch_size, 1]
        scores = torch.sigmoid(logits).squeeze(-1)  # [batch_size]

        return scores

    @classmethod
    def from_config(cls, config: Dict) -> "StepScorer":
        """Create StepScorer from config dict."""
        return cls(
            model_name=config.get("model_name", "Qwen/Qwen2.5-VL-7B-Instruct"),
            lora_r=config.get("lora_r", 64),
            lora_alpha=config.get("lora_alpha", 128),
            lora_dropout=config.get("lora_dropout", 0.05),
            lora_target_modules=config.get("lora_target_modules"),
            freeze_vision=config.get("freeze_vision", True),
            score_head_hidden_size=config.get("score_head_hidden_size", 256),
        )

    def save_pretrained(self, output_dir: str):
        """Save model to disk."""
        self.base_model.save_pretrained(output_dir)
        torch.save(self.score_head.state_dict(), f"{output_dir}/score_head.pt")

    def load_pretrained(self, checkpoint_path: str):
        """Load model from checkpoint."""
        self.base_model.load_pretrained(checkpoint_path)
        score_head_path = f"{checkpoint_path}/score_head.pt"
        if torch.path.exists(score_head_path):
            self.score_head.load_state_dict(torch.load(score_head_path))
