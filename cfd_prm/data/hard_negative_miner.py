"""
Hard Negative Miner for CFD-PRM

Extract hard negative pairs from Agentic-MME dataset.
Filters: String → NLI → Context → Visual (4-level pipeline)
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import CLIPProcessor, CLIPModel


class HardNegativeMiner:
    """
    Mine hard negative pairs from Agentic-MME dataset.

    Filters negatives by difficulty:
    1. String match (remove identical trajectories)
    2. NLI entailment (remove semantic duplicates)
    3. Context similarity (keep moderately similar)
    4. Visual similarity (keep visually distinct)
    """

    def __init__(
        self,
        nli_model_name: str = "facebook/bart-large-mnli",
        clip_model_name: str = "openai/clip-vit-b-32",
        visual_sim_threshold: float = 0.6,
        context_sim_range: Tuple[float, float] = (0.3, 0.7),
    ):
        """
        Args:
            nli_model_name: NLI model for semantic entailment
            clip_model_name: CLIP model for visual similarity
            visual_sim_threshold: Max visual similarity for hard negatives
            context_sim_range: Valid range for context similarity
        """
        self.visual_sim_threshold = visual_sim_threshold
        self.context_sim_range = context_sim_range

        # Load NLI model
        print("Loading NLI model...")
        self.nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_name)
        self.nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_name)

        # Load CLIP model
        print("Loading CLIP model...")
        self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
        self.clip_model = CLIPModel.from_pretrained(clip_model_name)

    def string_filter(self, traj1: str, traj2: str) -> bool:
        """Remove identical trajectories."""
        return traj1.strip() != traj2.strip()

    def nli_entailment(self, traj1: str, traj2: str) -> bool:
        """
        Check if traj1 entails traj2.
        Returns True if NOT entailment (keep as negative pair).
        """
        inputs = self.nli_tokenizer(
            traj1, traj2, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = self.nli_model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            # ENTAILMENT label is typically index 2
            entailment_prob = probs[0, 2].item()
        # Keep if NOT strong entailment
        return entailment_prob < 0.8

    def context_similarity(self, traj1: str, traj2: str) -> bool:
        """
        Check context similarity using cosine similarity.
        Returns True if in valid range (not too similar, not too different).
        """
        # Simple bag-of-words similarity for speed
        def get_tfidf_vector(text: str) -> torch.Tensor:
            words = text.lower().split()
            vec = torch.zeros(1000)  # Simplified: use first 1000 words as vocab
            for i, word in enumerate(set(words[:100])):
                vec[i % 1000] = words.count(word)
            norm = vec.norm()
            if norm > 0:
                vec = vec / norm
            return vec

        v1 = get_tfidf_vector(traj1)
        v2 = get_tfidf_vector(traj2)
        sim = (v1 * v2).sum().item()

        return self.context_sim_range[0] <= sim <= self.context_sim_range[1]

    def visual_similarity(self, image1_path: str, image2_path: str) -> bool:
        """
        Check visual similarity using CLIP.
        Returns True if NOT too similar (visually distinct).
        """
        try:
            img1 = Image.open(image1_path).convert("RGB")
            img2 = Image.open(image2_path).convert("RGB")

            inputs = self.clip_processor(
                images=[img1, img2], return_tensors="pt", padding=True
            )
            with torch.no_grad():
                features = self.clip_model.get_image_features(**inputs)
                # Normalize
                features = features / features.norm(dim=-1, keepdim=True)
                # Cosine similarity
                sim = (features[0] * features[1]).sum().item()

            # Keep if NOT too similar
            return sim < self.visual_sim_threshold
        except Exception as e:
            print(f"Warning: Could not compute visual similarity: {e}")
            return True  # Default to keeping if visual check fails

    def mine_pair(
        self,
        traj1: str,
        traj2: str,
        image1_path: str,
        image2_path: str,
    ) -> bool:
        """
        Full 4-level filtering pipeline.
        Returns True if this is a valid hard negative pair.
        """
        # Level 1: String match
        if not self.string_filter(traj1, traj2):
            return False

        # Level 2: NLI entailment
        if not self.nli_entailment(traj1, traj2):
            return False

        # Level 3: Context similarity
        if not self.context_similarity(traj1, traj2):
            return False

        # Level 4: Visual similarity
        if not self.visual_similarity(image1_path, image2_path):
            return False

        return True

    def mine_dataset(
        self,
        input_dir: str,
        output_dir: str,
        audit_size: int = 500,
    ):
        """
        Mine hard negative pairs from Agentic-MME dataset.

        Args:
            input_dir: Path to Agentic-MME dataset
            output_dir: Path to save hard negative pairs
            audit_size: Number of samples to audit manually
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Load Agentic-MME data
        print(f"Loading Agentic-MME dataset from {input_dir}...")
        # Expected structure: {task_id: {images: [...], trajectories: [...]}}
        data_file = input_path / "agentic_mme.json"
        if not data_file.exists():
            raise FileNotFoundError(f"Agentic-MME data not found at {data_file}")

        with open(data_file) as f:
            dataset = json.load(f)

        print(f"Found {len(dataset)} tasks")

        # Mine hard negative pairs
        hard_negative_pairs = []
        audited_count = 0

        for task_id, task_data in dataset.items():
            images = task_data.get("images", [])
            trajectories = task_data.get("trajectories", [])

            # Pairwise comparison within each task
            for i in range(len(trajectories)):
                for j in range(i + 1, len(trajectories)):
                    traj1, traj2 = trajectories[i], trajectories[j]
                    img1, img2 = images[i], images[j]

                    img1_path = str(input_path / img1)
                    img2_path = str(input_path / img2)

                    if self.mine_pair(traj1, traj2, img1_path, img2_path):
                        hard_negative_pairs.append({
                            "task_id": task_id,
                            "pair_id": f"{task_id}_pair_{i}_{j}",
                            "reference": {
                                "trajectory": traj1,
                                "image": img1,
                                "image_path": img1_path,
                            },
                            "deviated": {
                                "trajectory": traj2,
                                "image": img2,
                                "image_path": img2_path,
                            },
                        })

                        # Manual audit for first N samples
                        if audited_count < audit_size:
                            print(f"Audit [{audited_count + 1}/{audit_size}]: {task_id}")
                            audited_count += 1

        # Save hard negative pairs
        output_file = output_path / "hard_negatives.json"
        with open(output_file, "w") as f:
            json.dump(hard_negative_pairs, f, indent=2)

        print(f"\nMined {len(hard_negative_pairs)} hard negative pairs")
        print(f"Saved to: {output_file}")

        # Statistics
        stats = {
            "total_tasks": len(dataset),
            "total_pairs": len(hard_negative_pairs),
            "audit_size": audit_size,
        }
        stats_file = output_path / "mining_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print(f"Statistics saved to: {stats_file}")


def main():
    parser = argparse.ArgumentParser(description="Mine hard negative pairs from Agentic-MME")
    parser.add_argument(
        "--input_dir", type=str, required=True,
        help="Path to Agentic-MME dataset directory"
    )
    parser.add_argument(
        "--output_dir", type=str, default="data/hard_negatives",
        help="Output directory for hard negative pairs"
    )
    parser.add_argument(
        "--audit_size", type=int, default=500,
        help="Number of samples to audit manually"
    )
    parser.add_argument(
        "--visual_threshold", type=float, default=0.6,
        help="Visual similarity threshold"
    )

    args = parser.parse_args()

    miner = HardNegativeMiner(visual_sim_threshold=args.visual_threshold)
    miner.mine_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        audit_size=args.audit_size,
    )


if __name__ == "__main__":
    main()
