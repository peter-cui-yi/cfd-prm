"""
VisualPRM400K Data Adapter for CFD-PRM Training

Converts VisualPRM400K conversation format to CFD-PRM paired trajectory format.

VisualPRM400K format:
{
    "id": -1,
    "image": "path/to/image.jpg",
    "conversations": [
        {"from": "system", "value": "..."},
        {"from": "human", "value": "Question + Step 1"},
        {"from": "gpt", "value": "+"},
        {"from": "human", "value": "Step 2"},
        {"from": "gpt", "value": "+"},
        ...
    ]
}

CFD-PRM format (for training):
{
    "pair_id": "unique_id",
    "t_star": 3,
    "reference": {
        "image_path": "...",
        "trajectory": ["step1", "step2", ...],
        "labels": [1, 1, 1, ...],
    },
    "deviated": {
        "image_path": "...",
        "trajectory": ["step1", "step2", ...],
        "labels": [1, 1, 0, ...],
    }
}
"""

import os
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from tqdm import tqdm
import shutil


class VisualPRM400KAdapter:
    """
    Adapter for VisualPRM400K conversation format.
    
    Handles:
    1. Parsing multi-turn conversations
    2. Extracting step-level labels (+, -)
    3. Creating paired trajectories for CFD-PRM
    """
    
    def __init__(
        self,
        annotations_dir: str,
        images_source_dir: str,
        output_dir: str,
        min_steps: int = 2,
        max_steps: int = 20,
    ):
        """
        Args:
            annotations_dir: Directory with annotation JSONL files
            images_source_dir: Directory with extracted images
            output_dir: Output directory for CFD-PRM formatted data
            min_steps: Minimum number of steps in trajectory
            max_steps: Maximum number of steps in trajectory
        """
        self.annotations_dir = Path(annotations_dir)
        self.images_source_dir = Path(images_source_dir)
        self.output_dir = Path(output_dir)
        self.min_steps = min_steps
        self.max_steps = max_steps
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_conversation(self, sample: Dict) -> Optional[Dict]:
        """
        Parse a VisualPRM400K conversation into structured format.
        
        Returns:
            Dict with:
                - question: str
                - steps: List[str]
                - labels: List[int] (1=correct, 0=incorrect)
                - image_path: str
                - sample_id: str
        """
        conversations = sample.get("conversations", [])
        image_path = sample.get("image", "")
        sample_id = sample.get("id", -1)
        
        if len(conversations) < 3:  # Need at least: system + first turn
            return None
        
        # Extract question and steps
        question = None
        steps = []
        labels = []
        
        for i, turn in enumerate(conversations):
            if turn["from"] == "human":
                # First human turn contains question + first step
                if question is None:
                    # Parse question and first step
                    text = turn["value"]
                    if "<image>" in text:
                        text = text.replace("<image>", "").strip()
                    
                    # Split by "### Solution Process:" or similar markers
                    if "### Solution Process:" in text:
                        parts = text.split("### Solution Process:", 1)
                        question = parts[0].replace("### Question:", "").strip()
                        if len(parts) > 1:
                            first_step = parts[1].strip()
                            steps.append(first_step)
                    elif "### Question:" in text:
                        parts = text.split("### Question:", 1)
                        if len(parts) > 1:
                            question_rest = parts[1]
                            if "Solution Process:" in question_rest:
                                q_parts = question_rest.split("Solution Process:", 1)
                                question = q_parts[0].strip()
                                if len(q_parts) > 1:
                                    steps.append(q_parts[1].strip())
                            else:
                                question = question_rest.strip()
                    else:
                        # Assume it's just a question
                        question = text
                else:
                    # Subsequent steps
                    steps.append(turn["value"].strip())
                    
            elif turn["from"] == "gpt":
                # Label for the previous step
                label = turn["value"].strip()
                if label == "+":
                    labels.append(1)
                elif label == "-":
                    labels.append(0)
                else:
                    # Invalid label
                    return None
        
        # Validate
        if question is None or len(steps) == 0 or len(labels) == 0:
            return None
        
        if len(steps) != len(labels):
            # Step/label mismatch
            return None
        
        if len(steps) < self.min_steps or len(steps) > self.max_steps:
            return None
        
        return {
            "question": question,
            "steps": steps,
            "labels": labels,
            "image_path": image_path,
            "sample_id": f"{sample_id}_{hashlib.md5(question.encode()).hexdigest()[:8]}",
        }
    
    def build_image_index(self) -> Dict[str, Path]:
        """
        Build a reverse index: relative_path -> absolute_path.

        Scans all subdirectories under images_source_dir and maps
        every image file to its absolute path using multiple possible
        relative keys (all suffixes of the relative path).

        E.g. for "dataset/A-OKVQA/images/100245.jpg", generates keys:
          - "dataset/A-OKVQA/images/100245.jpg"
          - "A-OKVQA/images/100245.jpg"
          - "images/100245.jpg"
          - "100245.jpg"
        This covers all annotation path variants.
        """
        index = {}
        print("Building image index...")
        for img_path in self.images_source_dir.rglob("*"):
            if img_path.is_file() and img_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
                rel = img_path.relative_to(self.images_source_dir)
                parts = rel.parts
                # Generate all suffixes of the path
                for i in range(len(parts)):
                    key = str(Path(*parts[i:]))
                    index[key] = img_path
        print(f"Indexed {len(index)} image entries")
        return index

    def copy_image(self, image_path: str, image_index: Optional[Dict[str, Path]] = None) -> Optional[str]:
        """
        Copy image from source to output directory.

        If image_index is provided, uses it for fast lookup.
        Otherwise falls back to recursive search.

        Returns:
            Relative path to copied image, or None if not found
        """
        if not image_path:
            return None

        src_path = None

        if image_index is not None:
            # Strategy 1: Direct lookup in index
            if image_path in image_index:
                src_path = image_index[image_path]
            else:
                # Strategy 2: Try just the filename
                fname = Path(image_path).name
                if fname in image_index:
                    src_path = image_index[fname]
                else:
                    return None
        else:
            # Fallback: recursive search (slower, used when no index available)
            p = self.images_source_dir / image_path
            if p.exists():
                src_path = p
            else:
                # Try last two path components
                parts = Path(image_path).parts
                if len(parts) >= 2:
                    short = str(Path(*parts[-2:]))
                    for sub in self.images_source_dir.rglob(short):
                        if sub.is_file():
                            src_path = sub
                            break
                if src_path is None:
                    # Try just the filename
                    fname = Path(image_path).name
                    for sub in self.images_source_dir.rglob(fname):
                        if sub.is_file():
                            src_path = sub
                            break
                if src_path is None:
                    return None

        # Generate unique filename
        img_hash = hashlib.md5(image_path.encode()).hexdigest()[:12]
        img_ext = src_path.suffix or ".jpg"
        img_filename = f"{img_hash}{img_ext}"
        dst_path = self.images_output_dir / img_filename

        # Copy if not already exists
        if not dst_path.exists():
            try:
                shutil.copy2(src_path, dst_path)
            except Exception as e:
                print(f"Warning: Failed to copy {src_path}: {e}")
                return None

        return f"images/{img_filename}"
    
    def load_all_annotations(self) -> List[Dict]:
        """Load all annotation JSONL files."""
        all_samples = []
        
        jsonl_files = list(self.annotations_dir.glob("*.jsonl"))
        print(f"Found {len(jsonl_files)} annotation files")
        
        for jsonl_file in tqdm(jsonl_files, desc="Loading annotations"):
            with open(jsonl_file, "r") as f:
                for line in f:
                    try:
                        sample = json.loads(line)
                        all_samples.append(sample)
                    except json.JSONDecodeError:
                        continue
        
        print(f"Loaded {len(all_samples)} raw samples")
        return all_samples
    
    def find_paired_trajectories(
        self,
        samples: List[Dict],
    ) -> List[Tuple[Dict, Dict]]:
        """
        Find paired trajectories: reference (all correct) vs deviated (has errors).
        
        Groups by question, then creates pairs:
        - Reference: all labels = 1
        - Deviated: has at least one label = 0
        """
        # Parse all samples
        parsed = []
        for sample in tqdm(samples, desc="Parsing conversations"):
            result = self.parse_conversation(sample)
            if result:
                parsed.append(result)
        
        print(f"Parsed {len(parsed)} valid samples")
        
        # Group by question
        by_question = defaultdict(lambda: {"all_correct": [], "has_error": []})
        
        for sample in parsed:
            question = sample["question"]
            labels = sample["labels"]
            
            if all(l == 1 for l in labels):
                by_question[question]["all_correct"].append(sample)
            elif any(l == 0 for l in labels):
                by_question[question]["has_error"].append(sample)
        
        print(f"Found {len(by_question)} unique questions")
        
        # Create pairs
        pairs = []
        for question, groups in by_question.items():
            refs = groups["all_correct"]
            devs = groups["has_error"]
            
            if not refs or not devs:
                continue
            
            # Create pairs (limit to avoid explosion)
            # For each question, pair each ref with each dev
            # But limit total pairs per question
            max_pairs_per_question = 5
            count = 0
            for ref in refs:
                for dev in devs:
                    pairs.append((ref, dev))
                    count += 1
                    if count >= max_pairs_per_question:
                        break
                if count >= max_pairs_per_question:
                    break
        
        print(f"Created {len(pairs)} paired trajectories")
        return pairs
    
    def find_t_star(self, ref_labels: List[int], dev_labels: List[int]) -> int:
        """
        Find first divergence point t*.
        
        t* = first step where deviated has label=0 but reference has label=1
        """
        min_len = min(len(ref_labels), len(dev_labels))
        
        for t in range(min_len):
            if ref_labels[t] == 1 and dev_labels[t] == 0:
                return t
        
        # Fallback: first position where they differ
        for t in range(min_len):
            if ref_labels[t] != dev_labels[t]:
                return t
        
        # If no divergence, use middle step
        return min_len // 2
    
    def convert_pair(
        self,
        reference: Dict,
        deviated: Dict,
        pair_idx: int,
    ) -> Optional[Dict]:
        """
        Convert a (reference, deviated) pair to CFD-PRM format.
        
        Returns:
            CFD-PRM formatted pair, or None if conversion failed
        """
        pair_id = f"vprm_pair_{pair_idx}"
        
        # Copy images
        image_index = getattr(self, '_image_index', None)
        ref_image = self.copy_image(reference["image_path"], image_index)
        dev_image = self.copy_image(deviated["image_path"], image_index)
        
        # Find t*
        t_star = self.find_t_star(reference["labels"], deviated["labels"])
        
        return {
            "pair_id": pair_id,
            "t_star": t_star,
            "question": reference["question"],
            "reference": {
                "image_path": ref_image,
                "trajectory": reference["steps"],
                "labels": reference["labels"],
                "num_steps": len(reference["steps"]),
            },
            "deviated": {
                "image_path": dev_image,
                "trajectory": deviated["steps"],
                "labels": deviated["labels"],
                "num_steps": len(deviated["steps"]),
            },
            "metadata": {
                "source": "visualprm400k",
                "ref_sample_id": reference["sample_id"],
                "dev_sample_id": deviated["sample_id"],
            }
        }
    
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
        # Load all annotations
        all_samples = self.load_all_annotations()

        # Build image index for fast lookup
        image_index = self.build_image_index()
        self._image_index = image_index
        pairs = self.find_paired_trajectories(all_samples)
        
        # Limit pairs
        if len(pairs) > max_pairs:
            print(f"Limiting to {max_pairs} pairs")
            pairs = pairs[:max_pairs]
        
        # Convert pairs
        converted = []
        for i, (ref, dev) in enumerate(tqdm(pairs, desc="Converting pairs")):
            result = self.convert_pair(ref, dev, i)
            if result:
                converted.append(result)
        
        print(f"\nConverted {len(converted)} pairs")
        
        # Save
        output_file = self.output_dir / "visualprm400k_pairs.json"
        with open(output_file, "w") as f:
            json.dump(converted, f, indent=2)
        
        # Statistics
        stats = {
            "raw_samples": len(all_samples),
            "valid_samples": len([s for s in all_samples if self.parse_conversation(s)]),
            "paired_trajectories": len(pairs),
            "converted_pairs": len(converted),
            "images_copied": len(list(self.images_output_dir.glob("*"))),
            "avg_t_star": sum(p["t_star"] for p in converted) / len(converted) if converted else 0,
            "avg_ref_steps": sum(p["reference"]["num_steps"] for p in converted) / len(converted) if converted else 0,
            "avg_dev_steps": sum(p["deviated"]["num_steps"] for p in converted) / len(converted) if converted else 0,
        }
        
        stats_file = self.output_dir / "conversion_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        
        print(f"\nConversion complete!")
        print(f"  Raw samples: {stats['raw_samples']}")
        print(f"  Valid samples: {stats['valid_samples']}")
        print(f"  Paired trajectories: {stats['paired_trajectories']}")
        print(f"  Converted pairs: {stats['converted_pairs']}")
        print(f"  Images copied: {stats['images_copied']}")
        print(f"  Avg t*: {stats['avg_t_star']:.2f}")
        print(f"  Avg reference steps: {stats['avg_ref_steps']:.2f}")
        print(f"  Avg deviated steps: {stats['avg_dev_steps']:.2f}")
        print(f"\nOutput:")
        print(f"  Pairs: {output_file}")
        print(f"  Stats: {stats_file}")
        
        return {
            "pairs": str(output_file),
            "stats": str(stats_file),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Convert VisualPRM400K to CFD-PRM format"
    )
    parser.add_argument(
        "--annotations_dir",
        type=str,
        default="data/visualprm400k/annotations",
        help="Directory with annotation JSONL files",
    )
    parser.add_argument(
        "--images_source_dir",
        type=str,
        default="data/visualprm400k/images",
        help="Directory with extracted images",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/visualprm400k_converted",
        help="Output directory for CFD-PRM formatted data",
    )
    parser.add_argument(
        "--min_steps",
        type=int,
        default=2,
        help="Minimum number of steps in trajectory",
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=20,
        help="Maximum number of steps in trajectory",
    )
    parser.add_argument(
        "--max_pairs",
        type=int,
        default=50000,
        help="Maximum number of pairs to create",
    )
    
    args = parser.parse_args()
    
    adapter = VisualPRM400KAdapter(
        annotations_dir=args.annotations_dir,
        images_source_dir=args.images_source_dir,
        output_dir=args.output_dir,
        min_steps=args.min_steps,
        max_steps=args.max_steps,
    )
    
    adapter.convert(max_pairs=args.max_pairs)


if __name__ == "__main__":
    main()