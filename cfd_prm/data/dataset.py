"""
Dataset loader for CFD-PRM training

Loads hard negative pairs and constructs training batches.
"""

import os
import json
import torch
from torch.utils.data import Dataset, DataLoader, DistributedSampler
from typing import Dict, List, Tuple, Optional
from PIL import Image
from transformers import AutoProcessor
from pathlib import Path


class CFDPRMDataset(Dataset):
    """
    Dataset for CFD-PRM training.

    Loads hard negative pairs and prepares (image, trajectory) inputs.
    """

    def __init__(
        self,
        data_path: str,
        model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct",
        max_length: int = 512,
        image_size: int = 224,
        max_pairs: Optional[int] = None,
    ):
        """
        Args:
            data_path: Path to hard_negatives.json
            model_name: Qwen2.5-VL model name
            max_length: Maximum sequence length
            image_size: Image resize size
            max_pairs: Limit number of pairs loaded (None = all)
        """
        self.data_path = Path(data_path)
        self.max_length = max_length
        self.image_size = image_size

        # Load processor
        self.processor = AutoProcessor.from_pretrained(model_name)

        # Load data
        with open(self.data_path) as f:
            self.pairs = json.load(f)

        # Optionally limit pairs
        if max_pairs is not None and max_pairs < len(self.pairs):
            self.pairs = self.pairs[:max_pairs]
            print(f"Limited to {max_pairs} pairs")

        print(f"Loaded {len(self.pairs)} hard negative pairs")

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> Dict:
        pair = self.pairs[idx]

        # Reference trajectory
        ref_image_path = pair["reference"].get("image_path", "")
        ref_traj = pair["reference"]["trajectory"]

        # Deviated trajectory
        dev_image_path = pair["deviated"].get("image_path", "")
        dev_traj = pair["deviated"]["trajectory"]

        # Handle both string and list trajectories
        if isinstance(ref_traj, list):
            ref_traj = " | ".join(ref_traj)
        if isinstance(dev_traj, list):
            dev_traj = " | ".join(dev_traj)

        # Resolve image paths relative to data directory
        # Note: Skip images if not all pairs have them — mixed batches cause token mismatches
        ref_image = None  # self._load_image(ref_image_path)
        dev_image = None  # self._load_image(dev_image_path)

        # Prepare inputs for reference
        ref_input = self._prepare_input(ref_image, ref_traj)

        # Prepare inputs for deviated
        dev_input = self._prepare_input(dev_image, dev_traj)

        # Return as a single paired item — this ensures ref/dev stay together
        # regardless of DataLoader shuffling
        return {
            "reference": ref_input,
            "deviated": dev_input,
            "pair_id": pair["pair_id"],
            "task_id": pair.get("task_id", pair.get("question", "")),
        }

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from path, resolving relative to data directory if needed."""
        if not image_path:
            return None
        # Try absolute path first
        p = Path(image_path)
        if not p.exists():
            # Try relative to data directory
            p = self.data_path.parent / image_path
        if not p.exists():
            return None
        try:
            return Image.open(p).convert("RGB")
        except Exception:
            return None

    def _prepare_input(self, image: Optional[Image.Image], trajectory: str) -> Dict:
        """Prepare (image, text) input for Qwen2.5-VL."""
        # Format conversation for Qwen2.5-VL
        if image is not None:
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": f"Trajectory: {trajectory}\n\nIs this trajectory correct? Answer YES or NO."},
                    ],
                }
            ]
            
            # Apply chat template and process
            text = self.processor.apply_chat_template(conversation, tokenize=False)
            inputs = self.processor(
                text=text,
                images=[image],
                return_tensors="pt",
                padding=True,
            )
        else:
            # Text-only mode
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Trajectory: {trajectory}\n\nIs this trajectory correct? Answer YES or NO."},
                    ],
                }
            ]
            
            text = self.processor.apply_chat_template(conversation, tokenize=False)
            inputs = self.processor(
                text=text,
                return_tensors="pt",
                padding=True,
            )

        # Squeeze batch dimension
        for key in inputs:
            if isinstance(inputs[key], torch.Tensor):
                inputs[key] = inputs[key].squeeze(0)

        return inputs


def collate_fn(batch: List[Dict]) -> Dict:
    """
    Collate function for DataLoader.

    Each batch item is a complete (reference, deviated) pair.
    Creates interleaved batches: [ref_0, dev_0, ref_1, dev_1, ...]
    so the training loop can view as [n_pairs, 2].
    """
    batch_size = len(batch)

    all_inputs = []
    pair_ids = []
    task_ids = []
    labels = []  # 1 for reference, 0 for deviated

    for i, sample in enumerate(batch):
        # Reference (label = 1)
        ref_input = sample["reference"]
        ref_input["pair_idx"] = torch.tensor([i * 2])
        all_inputs.append(ref_input)
        pair_ids.append(sample["pair_id"])
        task_ids.append(sample["task_id"])
        labels.append(1)

        # Deviated (label = 0)
        dev_input = sample["deviated"]
        dev_input["pair_idx"] = torch.tensor([i * 2 + 1])
        all_inputs.append(dev_input)
        labels.append(0)

    # Merge inputs
    max_seq_len = max(inp["input_ids"].shape[-1] for inp in all_inputs)

    input_ids = torch.zeros(batch_size * 2, max_seq_len, dtype=torch.long)
    attention_mask = torch.zeros(batch_size * 2, max_seq_len, dtype=torch.long)

    # Handle pixel_values (may have different shapes)
    pixel_values_list = []
    image_grid_thw_list = []

    for i, inp in enumerate(all_inputs):
        seq_len = inp["input_ids"].shape[-1]
        # After squeeze in _prepare_input, input_ids is 1D [seq_len]
        input_ids[i, :seq_len] = inp["input_ids"]
        attention_mask[i, :seq_len] = inp["attention_mask"]

        if "pixel_values" in inp:
            pixel_values_list.append(inp["pixel_values"])
            if "image_grid_thw" in inp:
                image_grid_thw_list.append(inp["image_grid_thw"])

    # Stack pixel values if available
    pixel_values = None
    image_grid_thw = None
    if pixel_values_list:
        # Pad pixel values if needed
        max_patches = max(pv.shape[0] for pv in pixel_values_list)
        padded_pixel_values = []
        for pv in pixel_values_list:
            if pv.shape[0] < max_patches:
                padding = torch.zeros(max_patches - pv.shape[0], pv.shape[1])
                pv = torch.cat([pv, padding], dim=0)
            padded_pixel_values.append(pv)
        pixel_values = torch.stack(padded_pixel_values)

    if image_grid_thw_list:
        image_grid_thw = torch.stack(image_grid_thw_list, dim=0)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "pixel_values": pixel_values,
        "image_grid_thw": image_grid_thw,
        "labels": torch.tensor(labels, dtype=torch.float),
        "pair_ids": pair_ids,
        "task_ids": task_ids,
    }


class StepLevelCFDPRMDataset(Dataset):
    """
    Dataset for step-level CFD-PRM training.

    Returns raw pairs — the collate function expands each pair into
    individual step-level queries. This keeps DistributedSampler working
    correctly (samples = pairs, not steps).
    """

    def __init__(
        self,
        data_path: str,
        max_pairs: Optional[int] = None,
    ):
        """
        Args:
            data_path: Path to visualprm400k_pairs.json
            max_pairs: Limit number of pairs (None = all)
        """
        self.data_path = Path(data_path)

        with open(self.data_path) as f:
            self.pairs = json.load(f)

        if max_pairs is not None and max_pairs < len(self.pairs):
            self.pairs = self.pairs[:max_pairs]
            print(f"Limited to {max_pairs} pairs")

        print(f"Loaded {len(self.pairs)} pairs for step-level training")

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> Dict:
        return self.pairs[idx]


def step_level_collate_fn(
    batch: List[Dict],
    processor: AutoProcessor,
    max_length: int = 512,
) -> Dict:
    """
    Collate function for step-level CFD-PRM training.

    Expands each pair into individual step queries, tokenizes them,
    and tracks metadata for CFD loss computation.

    Returns:
        input_ids, attention_mask, and metadata dict with:
        - global_pair_idx: which pair each step belongs to
        - side: 0=ref, 1=dev
        - step_idx: position within trajectory
        - t_star: first divergence point for that pair
        - labels: per-step label (0/1)
    """
    step_texts = []
    global_pair_idx_list = []
    side_list = []
    step_idx_list = []
    t_star_list = []
    labels_list = []

    for pair_idx, pair in enumerate(batch):
        t_star = pair["t_star"]
        question = pair.get("question", "")

        # Reference trajectory steps (all labels = 1)
        ref_traj = pair["reference"]["trajectory"]
        ref_labels = pair["reference"]["labels"]
        for step_i, (step_text, label) in enumerate(zip(ref_traj, ref_labels)):
            # Build step-level query: question + steps 1..i
            prefix = "\n".join(ref_traj[:step_i + 1])
            query = (
                f"Question: {question}\n\n"
                f"Step-by-step reasoning:\n{prefix}\n\n"
                f"Is step {step_i + 1} correct? Answer YES or NO."
            )
            conversation = [
                {"role": "user", "content": [{"type": "text", "text": query}]}
            ]
            text = processor.apply_chat_template(conversation, tokenize=False)
            step_texts.append(text)
            global_pair_idx_list.append(pair_idx)
            side_list.append(0)  # ref
            step_idx_list.append(step_i)
            t_star_list.append(t_star)
            labels_list.append(label)

        # Deviated trajectory steps
        dev_traj = pair["deviated"]["trajectory"]
        dev_labels = pair["deviated"]["labels"]
        for step_i, (step_text, label) in enumerate(zip(dev_traj, dev_labels)):
            prefix = "\n".join(dev_traj[:step_i + 1])
            query = (
                f"Question: {question}\n\n"
                f"Step-by-step reasoning:\n{prefix}\n\n"
                f"Is step {step_i + 1} correct? Answer YES or NO."
            )
            conversation = [
                {"role": "user", "content": [{"type": "text", "text": query}]}
            ]
            text = processor.apply_chat_template(conversation, tokenize=False)
            step_texts.append(text)
            global_pair_idx_list.append(pair_idx)
            side_list.append(1)  # dev
            step_idx_list.append(step_i)
            t_star_list.append(t_star)
            labels_list.append(label)

    # Tokenize all step texts at once
    inputs = processor(text=step_texts, return_tensors="pt", padding=True, truncation=True, max_length=max_length)

    metadata = {
        "global_pair_idx": torch.tensor(global_pair_idx_list, dtype=torch.long),
        "side": torch.tensor(side_list, dtype=torch.long),
        "step_idx": torch.tensor(step_idx_list, dtype=torch.long),
        "t_star": torch.tensor(t_star_list, dtype=torch.long),
        "labels": torch.tensor(labels_list, dtype=torch.float),
    }

    return {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "metadata": metadata,
    }


def create_dataloader(
    data_path: str,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct",
    max_length: int = 512,
    max_pairs: Optional[int] = None,
    distributed: bool = False,
    world_size: int = 1,
    rank: int = 0,
    seed: int = 42,
) -> DataLoader:
    """
    Create DataLoader for CFD-PRM training.

    Args:
        data_path: Path to hard_negatives.json
        batch_size: Batch size per GPU
        shuffle: Whether to shuffle data
        num_workers: Number of data loading workers
        model_name: Qwen2.5-VL model name
        max_length: Maximum sequence length
        max_pairs: Limit number of data pairs (None = all)
        distributed: Whether to use DistributedSampler
        world_size: Number of GPUs
        rank: Current GPU rank
        seed: Random seed for DistributedSampler

    Returns:
        DataLoader instance
    """
    dataset = CFDPRMDataset(
        data_path=data_path,
        model_name=model_name,
        max_length=max_length,
        max_pairs=max_pairs,
    )

    if distributed:
        sampler = DistributedSampler(
            dataset, num_replicas=world_size, rank=rank, shuffle=True, seed=seed
        )
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,  # shuffle handled by sampler
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=True,
            sampler=sampler,
        )
    else:
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=True,
        )

    return dataloader
