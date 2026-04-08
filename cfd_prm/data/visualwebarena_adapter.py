"""
VisualWebArena Data Adapter for CFD-PRM

Converts VisualWebArena trajectories to CFD-PRM format.
Extracts screenshots, action sequences, and success labels.
"""

import os
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import hashlib


class VisualWebArenaAdapter:
    """
    Adapter for VisualWebArena dataset.

    Converts VWA trajectory format to CFD-PRM compatible format.
    """

    def __init__(
        self,
        vwa_dir: str,
        output_dir: str,
        min_steps: int = 3,
        max_steps: int = 50,
    ):
        """
        Args:
            vwa_dir: Path to VisualWebArena repository
            output_dir: Output directory for converted data
            min_steps: Minimum trajectory length
            max_steps: Maximum trajectory length
        """
        self.vwa_dir = Path(vwa_dir)
        self.output_dir = Path(output_dir)
        self.min_steps = min_steps
        self.max_steps = max_steps

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_trajectories(self) -> List[Dict]:
        """
        Load trajectories from VisualWebArena.

        VWA stores trajectories in JSON/JSONL format with:
        - task_id, task description
        - states (screenshots, DOM)
        - actions (clicks, type, select)
        - success/failure label
        """
        trajectories = []

        # Look for trajectory files
        # Common locations in VWA repo
        possible_paths = [
            self.vwa_dir / "data" / "trajectories.json",
            self.vwa_dir / "data" / "trajectories.jsonl",
            self.vwa_dir / "data" / "visualwebarena_trajectories.json",
            self.vwa_dir / "trajectories.json",
            self.vwa_dir / "agentbench" / "trajectories.json",
        ]

        traj_file = None
        for path in possible_paths:
            if path.exists():
                traj_file = path
                break

        if traj_file is None:
            raise FileNotFoundError(
                f"Could not find VisualWebArena trajectories.\n"
                f"Searched: {[str(p) for p in possible_paths]}\n"
                f"Please ensure VisualWebArena is properly installed."
            )

        print(f"Loading trajectories from {traj_file}...")

        # Load based on format
        if traj_file.suffix == ".json":
            with open(traj_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    trajectories = data
                elif isinstance(data, dict) and "trajectories" in data:
                    trajectories = data["trajectories"]
        elif traj_file.suffix == ".jsonl":
            with open(traj_file) as f:
                for line in f:
                    trajectories.append(json.loads(line))
        else:
            # Try JSON first
            try:
                with open(traj_file) as f:
                    data = json.load(f)
                    trajectories = data if isinstance(data, list) else data.get("trajectories", [])
            except json.JSONDecodeError:
                # Try JSONL
                with open(traj_file) as f:
                    for line in f:
                        trajectories.append(json.loads(line))

        print(f"Loaded {len(trajectories)} raw trajectories")
        return trajectories

    def extract_screenshot(
        self,
        trajectory: Dict,
        step_idx: int,
        task_id: str,
    ) -> Optional[str]:
        """
        Extract and save screenshot for a trajectory step.

        Returns:
            Relative path to saved image, or None if extraction failed
        """
        # VWA stores screenshots in various formats
        states = trajectory.get("states", [])
        if step_idx >= len(states):
            return None

        state = states[step_idx]

        # Try different screenshot field names
        screenshot = None
        screenshot_fields = [
            "screenshot", "image", "observation", "visual",
            "screenshot_base64", "image_base64", "img_base64",
        ]

        for field in screenshot_fields:
            if field in state:
                screenshot = state[field]
                break

        if screenshot is None:
            # Try nested access
            if "observation" in state and "image" in state["observation"]:
                screenshot = state["observation"]["image"]

        if screenshot is None:
            return None

        # Decode and save
        try:
            # Handle base64 encoded images
            if isinstance(screenshot, str):
                import base64
                # Remove data URL prefix if present
                if screenshot.startswith("data:"):
                    screenshot = screenshot.split(",")[1]

                image_data = base64.b64decode(screenshot)
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(screenshot, Image.Image):
                image = screenshot
            else:
                return None

            # Generate unique filename
            img_hash = hashlib.md5(
                f"{task_id}_step{step_idx}".encode()
            ).hexdigest()[:12]
            img_filename = f"vwa_{task_id}_{img_hash}.png"
            img_path = self.images_dir / img_filename

            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(img_path, "PNG")

            # Return relative path
            return str(img_path.relative_to(self.output_dir.parent.parent))

        except Exception as e:
            print(f"Warning: Could not extract screenshot: {e}")
            return None

    def format_trajectory_text(
        self,
        trajectory: Dict,
        step_idx: int,
        task_id: str,
    ) -> str:
        """
        Format trajectory up to step_idx as text description.

        Creates a natural language description of actions taken.
        """
        actions = trajectory.get("actions", trajectory.get("action_history", []))
        task_desc = trajectory.get("instruction", trajectory.get("task", ""))

        # Format action history up to current step
        action_texts = []
        for i, action in enumerate(actions[:step_idx + 1]):
            action_type = action.get("type", action.get("action_type", "unknown"))
            action_text = action.get("text", action.get("value", ""))
            element = action.get("element", action.get("target", ""))

            if action_type == "click":
                action_texts.append(f"Clicked on {element or 'element'}")
            elif action_type == "type":
                action_texts.append(f"Typed '{action_text}' into {element or 'field'}")
            elif action_type == "select":
                action_texts.append(f"Selected '{action_text}' from {element or 'dropdown'}")
            elif action_type == "navigate":
                action_texts.append(f"Navigated to {action_text or 'URL'}")
            elif action_type == "scroll":
                direction = action_text or "down"
                action_texts.append(f"Scrolled {direction}")
            else:
                action_texts.append(f"Action: {action_type}")

        # Combine task + actions
        trajectory_text = f"Task: {task_desc}\n\n"
        trajectory_text += "Actions taken:\n" + "\n".join(
            f"  {i+1}. {a}" for i, a in enumerate(action_texts)
        )

        return trajectory_text

    def convert_trajectory(
        self,
        trajectory: Dict,
    ) -> List[Dict]:
        """
        Convert a single VWA trajectory to CFD-PRM format.

        Creates multiple (image, trajectory_text) pairs per trajectory
        for step-level supervision.

        Returns:
            List of CFD-PRM format entries
        """
        task_id = trajectory.get(
            "task_id",
            trajectory.get("id", trajectory.get("idx", "unknown"))
        )
        task_id = str(task_id)

        success = trajectory.get("success", trajectory.get("label", 0))
        states = trajectory.get("states", [])
        actions = trajectory.get("actions", trajectory.get("action_history", []))

        # Filter by trajectory length
        num_steps = min(len(states), len(actions))
        if num_steps < self.min_steps or num_steps > self.max_steps:
            return []

        # Convert to CFD-PRM format
        converted = []

        for step_idx in range(num_steps):
            # Extract screenshot
            img_path = self.extract_screenshot(trajectory, step_idx, task_id)

            # Skip if no screenshot
            if img_path is None:
                continue

            # Format trajectory text
            traj_text = self.format_trajectory_text(
                trajectory, step_idx, task_id
            )

            converted.append({
                "task_id": task_id,
                "step_idx": step_idx,
                "image_path": img_path,
                "trajectory": traj_text,
                "success": success,
                "is_final_step": (step_idx == num_steps - 1),
            })

        return converted

    def create_hard_negative_pairs(
        self,
        converted_data: List[Dict],
    ) -> List[Dict]:
        """
        Create hard negative pairs from converted trajectories.

        Pairs successful trajectories with failed ones for similar tasks.
        Groups by task type/domain for meaningful comparisons.
        """
        # Group by task type
        task_groups = {}
        for entry in converted_data:
            task_id = entry["task_id"]
            # Group by task prefix (first part before underscore/hyphen)
            task_prefix = task_id.split("_")[0].split("-")[0]
            if task_prefix not in task_groups:
                task_groups[task_prefix] = {"success": [], "failure": []}

            if entry["success"]:
                task_groups[task_prefix]["success"].append(entry)
            else:
                task_groups[task_prefix]["failure"].append(entry)

        # Create pairs
        pairs = []
        pair_id = 0

        for task_prefix, groups in task_groups.items():
            successes = groups["success"]
            failures = groups["failure"]

            # Pair each failure with closest success
            for fail_entry in failures:
                for succ_entry in successes:
                    pair_id += 1
                    pairs.append({
                        "task_id": f"{task_prefix}_pair_{pair_id}",
                        "pair_id": f"vwa_{task_prefix}_{pair_id}",
                        "difficulty": "hard",  # Will be refined by miner
                        "reference": {
                            "trajectory": succ_entry["trajectory"],
                            "image": Path(succ_entry["image_path"]).name,
                            "image_path": succ_entry["image_path"],
                            "success": True,
                            "step_idx": succ_entry["step_idx"],
                        },
                        "deviated": {
                            "trajectory": fail_entry["trajectory"],
                            "image": Path(fail_entry["image_path"]).name,
                            "image_path": fail_entry["image_path"],
                            "success": False,
                            "step_idx": fail_entry["step_idx"],
                        },
                    })

        print(f"Created {len(pairs)} hard negative pairs")
        return pairs

    def convert(
        self,
        skip_screenshots: bool = False,
    ) -> Dict[str, str]:
        """
        Full conversion pipeline.

        Args:
            skip_screenshots: If True, skip screenshot extraction (text-only)

        Returns:
            Dictionary of output file paths
        """
        import io  # Import here for base64 handling

        # Load VWA trajectories
        trajectories = self.load_trajectories()

        # Convert each trajectory
        all_converted = []
        for i, traj in enumerate(trajectories):
            if i % 100 == 0:
                print(f"Converting trajectory {i}/{len(trajectories)}...")

            converted = self.convert_trajectory(traj)
            all_converted.extend(converted)

        print(f"Converted {len(all_converted)} trajectory steps")

        # Save converted data (step-level)
        step_file = self.output_dir / "visualwebarena_steps.json"
        with open(step_file, "w") as f:
            json.dump(all_converted, f, indent=2)

        # Create hard negative pairs
        pairs = self.create_hard_negative_pairs(all_converted)

        # Save pairs
        pairs_file = self.output_dir / "hard_negatives.json"
        with open(pairs_file, "w") as f:
            json.dump(pairs, f, indent=2)

        # Save statistics
        stats = {
            "total_trajectories": len(trajectories),
            "total_steps": len(all_converted),
            "total_pairs": len(pairs),
            "images_saved": len(list(self.images_dir.glob("*.png"))),
            "success_trajectories": sum(
                1 for t in trajectories
                if t.get("success", t.get("label", 0))
            ),
            "failure_trajectories": sum(
                1 for t in trajectories
                if not t.get("success", t.get("label", 1))
            ),
        }

        stats_file = self.output_dir / "conversion_stats.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

        print(f"\nConversion complete!")
        print(f"  Trajectories: {stats['total_trajectories']}")
        print(f"  Steps: {stats['total_steps']}")
        print(f"  Hard negative pairs: {stats['total_pairs']}")
        print(f"  Images: {stats['images_saved']}")
        print(f"\nOutput files:")
        print(f"  Steps: {step_file}")
        print(f"  Pairs: {pairs_file}")
        print(f"  Stats: {stats_file}")

        return {
            "steps": str(step_file),
            "pairs": str(pairs_file),
            "stats": str(stats_file),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Convert VisualWebArena to CFD-PRM format"
    )
    parser.add_argument(
        "--vwa_dir",
        type=str,
        required=True,
        help="Path to VisualWebArena repository",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/visualwebarena",
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
        default=50,
        help="Maximum trajectory length",
    )
    parser.add_argument(
        "--skip_screenshots",
        action="store_true",
        help="Skip screenshot extraction (text-only mode)",
    )

    args = parser.parse_args()

    adapter = VisualWebArenaAdapter(
        vwa_dir=args.vwa_dir,
        output_dir=args.output_dir,
        min_steps=args.min_steps,
        max_steps=args.max_steps,
    )

    adapter.convert(skip_screenshots=args.skip_screenshots)


if __name__ == "__main__":
    main()
