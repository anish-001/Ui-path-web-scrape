#!/usr/bin/env python3
"""
run_pipeline.py
───────────────
Master orchestrator for collecting RPA-related data from the UiPath forum.

Executes:
  1. Forum Data Harvesting (src/uipath_forum_collector.py)

Usage:
  python3 run_pipeline.py --all
  python3 run_pipeline.py --dry-run
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
OUTPUTS_DIR = ROOT_DIR / "outputs"

PIPELINE_STEPS = [
    {
        "step": 1,
        "name": "Forum Data Harvesting",
        "script": SRC_DIR / "uipath_forum_collector.py",
        "args": [
            "--pages", "5",
            "--delay", "1.0"
        ],
        "expected_output": OUTPUTS_DIR / "uipath_forum_posts.csv",
        "description": (
            "Harvests public topic threads from forum.uipath.com "
            "via the Discourse JSON API using predefined search queries."
        )
    },
]


def print_banner():
    print("=" * 78)
    print("  RPA Bot Adaptation After SAP S/4HANA Migration: Data Collection")
    print("=" * 78)


def execute_step(step_info: dict, dry_run: bool = False):
    print(f"\n[Step {step_info['step']}] {step_info['name']}")
    print(f"  Description: {step_info['description']}")
    print(f"  Script:      {step_info['script'].name}")
    print(f"  Target:      {step_info['expected_output'].name}")

    if dry_run:
        print("  [DRY-RUN] Command skipped.")
        return True

    cmd = [sys.executable, str(step_info["script"])] + step_info["args"]
    t0 = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            check=True,
            text=True,
            capture_output=True
        )

        elapsed = time.time() - t0
        print(f"  ✓ Finished in {elapsed:.2f}s")

        if result.stdout.strip():
            for line in result.stdout.strip().splitlines()[-3:]:
                print(f"    {line}")

        return True

    except subprocess.CalledProcessError as err:
        print(
            f"  ✗ Step {step_info['step']} failed "
            f"with exit code {err.returncode}:"
        )
        print(err.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run the RPA forum data collection pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute the forum data harvesting step."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display the execution plan without running the script."
    )

    args = parser.parse_args()

    print_banner()

    if not args.all and not args.dry_run:
        print(
            "No execution flag provided. "
            "Use --all or --dry-run."
        )
        print("Run with -h for help.\n")
        parser.print_help()
        sys.exit(0)

    selected_steps = [1]

    print(f"Plan: Running step(s) {selected_steps}")
    start_total = time.time()

    for step_cfg in PIPELINE_STEPS:
        if step_cfg["step"] in selected_steps:
            success = execute_step(
                step_cfg,
                dry_run=args.dry_run
            )

            if not success:
                print(
                    f"\nPipeline aborted due to failure "
                    f"in Step {step_cfg['step']}."
                )
                sys.exit(1)

    total_time = time.time() - start_total

    print("\n" + "=" * 78)
    print(
        f"  Data collection completed in {total_time:.2f}s."
    )
    print(
        f"  Output generated in: {OUTPUTS_DIR.resolve()}"
    )
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
