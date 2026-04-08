"""
VisualPRM400K Data Adapter for CFD-PRM

Converts VisualPRM400K trajectories to CFD-PRM format.
Extracts images, step-level solutions, and correctness labels.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import hashlib


class VisualPRM400KAdapter:
    """
    Adapter for VisualPRM400K dataset.

    Converts VisualPRM400K format to CFD-PRM compatible format.
    Key difference from VisualWebArena: has STEP-LEVEL correctness labels!
    """

    def __init__(
        self,
        data_dir: str,
        output_dir: str,
        min_steps: int = 3,
        max_steps: int = 20,
    ):
        """
        Args:
            data_dir: Path to VisualPRM400K dataset (from HuggingFace)
            output_dir: Output directory for converted data
            min_steps: Minimum trajectory length
            max_steps: Maximum trajectory length
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.min_steps = min_steps
        self.max_steps = max_steps

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset(self) -> List[Dict]:
        """
        Load VisualPRM400K dataset.

        Expected format (from HuggingFace):
        {
            "image": PIL.Image or path,
            "question": str,
            "solution": List[str],  # step-by-step reasoning
            "labels": List[int],    # 1=correct, 0=incorrect per step
            "final_answer": str,
        }
        """
        print(f"Loading VisualPRM400K from {self.data_dir}...")

        # Try multiple formats
        possible_files = [
            self.data_dir / "visualprm400k.json",
            self.data_dir / "visualprm400k.jsonl",
            self.data_dir / "data.json",
            self.data_dir / "train.json",
        ]

        data_file = None
        for path in possible_files:
            if path.exists():
                data_file = path
                break

        if data_file is None:
            # Try loading from HuggingFace datasets
            try:
                from datasets import load_dataset
                dataset = load_dataset("OpenGVLab/VisualPRM400K", split="train")
                print(f"Loaded {len(dataset)} samples from HuggingFace")
                return list(dataset)
            except Exception as e:
                raise FileNotFoundError(
                    f"Could not find VisualPRM400K data at {self.data_dir}\n"
                    f"Please download from: https://huggingface.co/datasets/OpenGVLab/VisualPRM400K\n"
                    f"Error: {e}"
                )

        # Load from file
        if data_file.suffix == ".json":
            with open(data_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
        elif data_file.suffix == ".jsonl":
            data = []
            with open(data_file) as f:
                for line in f:
                    data.append(json.loads(line))
            return data

        raise ValueError(f"Unsupported file format: {data_file.suffix}")

    def find_paired_trajectories(
        self,
        dataset: List[Dict],
    ) -> List[Tuple[Dict, Dict]]:
        """
        Find paired trajectories: reference (all correct) vs deviated (has errors).

        Groups by question, then pairs:
        - Reference: all labels = 1
        - Deviated: at least one label = 0

        Returns:
            List of (reference, deviated) pairs
        """
        # Group by question
        by_question = {}
        for sample in dataset:
            question = sample.get("question", sample.get("problem", ""))
            if question not in by_question:
                by_question[question] = {"all_correct": [], "has_error": []}

            labels = sample.get("labels", [])
            image = sample.get("image", None)

            if all(l == 1 for l in labels):
                by_question[question]["all_correct"].append(sample)
            elif any(l == 0 for l in labels):
                by_question[question]["has_error"].append(sample)

        # Create pairs
        pairs = []
        for question, groups in by_question.items():
            refs = groups["all_correct"]
            devs = groups["has_error"]

            if not refs or not devs:
                continue

            # Pair each reference with each deviated (can be many pairs per question)
            for ref in refs:
                for dev in devs:
                    pairs.append((ref, dev))

        print(f"Found {len(pairs)} paired trajectories from {len(by_question)} questions")
        return pairs

    def find_t_star(self, ref_labels: List[int], dev_labels: List[int]) -> int:
        """
        Find first divergence point t*.

        t* = first step where deviated trajectory has label=0 but reference has label=1
        """
        min_len = min(len(ref_labels), len(dev_labels))
        for t in range(min_len):
            if ref_labels[t] == 1 and dev_labels[t] == 0:
                return t
        # Fallback: first position where they differ
        for t in range(min_len):
            if ref_labels[t] != dev_labels[t]:
                return t
        # If no divergence found, use middle step
        return min_len // 2

    def extract_image(
        self,
        sample: Dict,
        pair_id: str,
        prefix: str,
    ) -> Optional[str]:
        """
        Extract and save image from sample.

        Returns:
            Relative path to saved image
        """
        image = sample.get("image", None)

        if image is None:
            return None

        try:
            # Handle different image formats
            if isinstance(image, str):
                # Path or URL - try to load
                if os.path.exists(image):
                    image = Image.open(image).convert("RGB")
                else:
                    # Assume it's base64 or skip
                    return None
            elif hasattr(image, "convert"):
                # Already PIL Image
                pass
            else:
                return None

            # Generate unique filename
            img_hash = hashlib.md5(f"{pair_id}_{prefix}".encode()).hexdigest()[:12]
            img_filename = f"vprm_{pair_id}_{prefix}_{img_hash}.png"
            img_path = self.images_dir / img_filename

            image.save(img_path, "PNG")

            # Return relative path (from project root)
            return str(img_path.relative_to(self.output_dir.parent))

        except Exception as e:
            print(f"Warning: Could not extract image: {e}")
            return None

    def format_step_text(
        self,
        sample: Dict,
        up_to_step: int,
    ) -> str:
        """
        Format trajectory prefix as text (steps 0 to up_to_step).
        """
        question = sample.get("question", sample.get("problem", ""))
        solution = sample.get("solution", [])

        # Combine question + steps up to t*
        step_texts = solution[:up_to_step + 1]

        trajectory_text = f"Question: {question}\n\n"
        trajectory_text += "Reasoning steps:\n"
        for i, step in enumerate(step_texts):
            trajectory_text += f"  Step {i+1}: {step}\n"

        return trajectory_text

    def convert_pair(
        self,
        reference: Dict,
        deviated: Dict,
        pair_idx: int,
    ) -> List[Dict]:
        """
        Convert a (reference, deviated) pair to CFD-PRM format.

        For each pair:
        - Extract images
        - Find t*
        - Create paired entry with step-level info
        """
        pair_id = f"vprm_pair_{pair_idx}"

        # Extract images
        ref_image_path = self.extract_image(reference, pair_id, "ref")
        dev_image_path = self.extract_image(deviated, pair_id, "dev")

        # Skip if either image extraction failed
        if ref_image_path is None or dev_image_path is None:
            return []

        # Get labels
        ref_labels = reference.get("labels", [])
        dev_labels = deviated.get("labels", [])

        # Find t*
        t_star = self.find_t_star(ref_labels, dev_labels)

        # Format step texts (up to t*)
        ref_traj_text = self.format_step_text(reference, t_star)
        dev_traj_text = self.format_step_text(deviated, t_star)

        # Get final answers
        ref_answer = reference.get("final_answer", reference.get("answer", ""))
        dev_answer = deviated.get("final_answer", deviated.get("answer", ""))

        return [{
            "pair_id": pair_id,
            "t_star": t_star,
            "reference": {
                "image_path": ref_image_path,
                "trajectory": ref_traj_text,
                "answer": ref_answer,
                "labels": ref_labels,
            },
            "deviated": {
                "image_path": dev_image_path,
                "trajectory": dev_traj_text,
                "answer": dev_answer,
                "labels": dev_labels,
            },
            "metadata": {
                "question": reference.get("question", ""),
                "num_steps": len(ref_labels),
                "t_star": t_star,
            }
        }]

    def convert(
        self,
        max_pairs: int = 50000,
    ) -> Dict[str, str]:
        """
        Full conversion pipeline.

        Args:
            max_pairs: Maximum number of pairs to create

        Returns:
            Dictionary of output file paths
        """
        # Load dataset
        dataset = self.load_dataset()
        print(f"Loaded {len(dataset)} raw samples")

        # Find paired trajectories
        pairs = self.find_paired_trajectories(dataset)
        print(f"Found {len(pairs)} potential pairs")

        # Limit pairs
        if len(pairs) > max_pairs:
            print(f"Limiting to {max_pairs} pairs...")
            pairs = pairs[:max_pairs]

        # Convert pairs
        all_converted = []
        for i, (ref, dev) in enumerate(pairs):
            if i % 1000 == 0:
                print(f"Converting pair {i}/{len(pairs)}...")

            converted = self.convert_pair(ref, dev, i)
            all_converted.extend(converted)

        print(f"\nConverted {len(all_converted)} pairs")

        # Save pairs
        pairs_file = self.output_dir / "visualprm400k_pairs.json"
        with open(pairs_file, "w") as f:
            json.dump(all_converted, f, indent=2)

        # Save statistics
        stats = {
            "raw_samples": len(dataset),
            "paired_trajectories": len(pairs),
            "converted_pairs": len(all_converted),
            "images_saved": len(list(self.images_dir.glob("*.png"))),
            "avg_t_star": sum(p["t_star"] for p in all_converted) / len(all_converted) if all_converted else 0,
            "avg_steps": sum(p["metadata"]["num_steps"] for p in all_converted) / len(all_converted) if all_converted else 0,
        }

        stats_file = self.output_dir / "conversion_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print(f"\nConversion complete!")
        print(f"  Raw samples: {stats['raw_samples']}")
        print(f"  Paired trajectories: {stats['paired_trajectories']}")
        print(f"  Converted pairs: {stats['converted_pairs']}")
        print(f"  Images: {stats['images_saved']}")
        print(f"  Avg t*: {stats['avg_t_star']:.1f}")
        print(f"\nOutput files:")
        print(f"  Pairs: {pairs_file}")
        print(f"  Stats: {stats_file}")

        return {
            "pairs": str(pairs_file),
            "stats": str(stats_file),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Convert VisualPRM400K to CFD-PRM format"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Path to VisualPRM400K dataset",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/visualprm400k",
        help="Output directory for converted data",
    )
    parser.add_argument(
        "--min_steps",
        type=int,
        default=3,
        help="Minimum trajectory length",
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=20,
        help="Maximum trajectory length",
    )
    parser.add_argument(
        "--max_pairs",
        type=int,
        default=50000,
        help="Maximum number of pairs to create",
    )

    args = parser.parse_args()

    adapter = VisualPRM400KAdapter(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        min_steps=args.min_steps,
        max_steps=args.max_steps,
    )

    adapter.convert(max_pairs=args.max_pairs)


if __name__ == "__main__":
    main()
