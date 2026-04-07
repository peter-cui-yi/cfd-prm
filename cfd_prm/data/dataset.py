"""
Dataset loader for CFD-PRM training

Loads hard negative pairs and constructs training batches.
"""

import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
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
    ):
        """
        Args:
            data_path: Path to hard_negatives.json
            model_name: Qwen2.5-VL model name
            max_length: Maximum sequence length
            image_size: Image resize size
        """
        self.data_path = Path(data_path)
        self.max_length = max_length
        self.image_size = image_size

        # Load processor
        self.processor = AutoProcessor.from_pretrained(model_name)

        # Load data
        with open(self.data_path) as f:
            self.pairs = json.load(f)

        print(f"Loaded {len(self.pairs)} hard negative pairs")

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> Dict:
        pair = self.pairs[idx]

        # Reference trajectory
        ref_image_path = pair["reference"]["image_path"]
        ref_traj = pair["reference"]["trajectory"]

        # Deviated trajectory
        dev_image_path = pair["deviated"]["image_path"]
        dev_traj = pair["deviated"]["trajectory"]

        # Load images
        ref_image = Image.open(ref_image_path).convert("RGB")
        dev_image = Image.open(dev_image_path).convert("RGB")

        # Prepare inputs for reference
        ref_input = self._prepare_input(ref_image, ref_traj)

        # Prepare inputs for deviated
        dev_input = self._prepare_input(dev_image, dev_traj)

        return {
            "reference": ref_input,
            "deviated": dev_input,
            "pair_id": pair["pair_id"],
            "task_id": pair["task_id"],
        }

    def _prepare_input(self, image: Image.Image, trajectory: str) -> Dict:
        """Prepare (image, text) input for Qwen2.5-VL."""
        # Format conversation for Qwen2.5-VL
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

        # Squeeze batch dimension
        for key in inputs:
            if isinstance(inputs[key], torch.Tensor):
                inputs[key] = inputs[key].squeeze(0)

        return inputs


def collate_fn(batch: List[Dict]) -> Dict:
    """
    Collate function for DataLoader.

    Pads sequences and stacks tensors.
    """
    batch_size = len(batch)

    # Combine reference and deviated into a single batch
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
        input_ids[i, :seq_len] = inp["input_ids"][0]
        attention_mask[i, :seq_len] = inp["attention_mask"][0]

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
        image_grid_thw = torch.cat(image_grid_thw_list, dim=0)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "pixel_values": pixel_values,
        "image_grid_thw": image_grid_thw,
        "labels": torch.tensor(labels, dtype=torch.float),
        "pair_ids": pair_ids,
        "task_ids": task_ids,
    }


def create_dataloader(
    data_path: str,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct",
    max_length: int = 512,
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

    Returns:
        DataLoader instance
    """
    dataset = CFDPRMDataset(
        data_path=data_path,
        model_name=model_name,
        max_length=max_length,
    )

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=True,
    )

    return dataloader
