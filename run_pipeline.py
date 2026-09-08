#!/usr/bin/env python3
"""
run_pipeline.py
───────────────
Master orchestrator for the RPA SAP S/4HANA Migration Thematic Analysis Pipeline.

Executes the four pipeline steps in sequence:
  Step 1: Collect raw UiPath forum posts (work/uipath_forum_collector.py)
  Step 2: Generate 8-theme coding matrix (work/prepare_theme_matrix.py)
  Step 3: Build paper-ready quantitative tables (work/build_paper_quant_tables.py)
  Step 4: Compute dataset diagnostics and summary (work/analyze_csvs.py)

Usage:
  python3 run_pipeline.py --all           # Execute full pipeline end-to-end
  python3 run_pipeline.py --step 2 3 4    # Run analysis steps using existing scraped data
  python3 run_pipeline.py --dry-run       # Print execution sequence without running
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
WORK_DIR = ROOT_DIR / "work"
OUTPUTS_DIR = ROOT_DIR / "outputs"

PIPELINE_STEPS = [
    {
        "step": 1,
        "name": "Forum Data Harvesting",
        "script": WORK_DIR / "uipath_forum_collector.py",
        "args": ["--query", '"SAP S/4HANA" "UiPath"', "--pages", "5", "--delay", "1.0"],
        "expected_output": OUTPUTS_DIR / "uipath_forum_posts.csv",
        "description": "Harvests public topic threads from forum.uipath.com via Discourse JSON API."
    },
    {
        "step": 2,
        "name": "Thematic Matrix Feature Extraction",
        "script": WORK_DIR / "prepare_theme_matrix.py",
        "args": [
            "--input", str(OUTPUTS_DIR / "uipath_forum_posts.csv"),
            "--output", str(OUTPUTS_DIR / "uipath_forum_theme_matrix.csv")
        ],
        "expected_output": OUTPUTS_DIR / "uipath_forum_theme_matrix.csv",
        "description": "Applies regex pattern matching for themes T1-T8 and entity mention counts."
    },
    {
        "step": 3,
        "name": "Topic Aggregation & Quantitative Tables",
        "script": WORK_DIR / "build_paper_quant_tables.py",
        "args": [],
        "expected_output": OUTPUTS_DIR / "paper_theme_frequency_table.csv",
        "description": "Rolls up posts into topic-level units and builds publication frequency/co-occurrence tables."
    },
    {
        "step": 4,
        "name": "Dataset Diagnostics & Reporting",
        "script": WORK_DIR / "analyze_csvs.py",
        "args": [],
        "expected_output": OUTPUTS_DIR / "csv_analysis_summary.md",
        "description": "Calculates temporal spread, median word counts, and generates diagnostic markdown report."
    }
]


def print_banner():
    print("=" * 78)
    print("  RPA Bot Adaptation After SAP S/4HANA Migration: Research Pipeline")
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
        result = subprocess.run(cmd, cwd=ROOT_DIR, check=True, text=True, capture_output=True)
        elapsed = time.time() - t0
        print(f"  ✓ Finished in {elapsed:.2f}s")
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines()[-3:]:
                print(f"    {line}")
        return True
    except subprocess.CalledProcessError as err:
        print(f"  ✗ Step {step_info['step']} failed with exit code {err.returncode}:")
        print(err.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run the RPA SAP Thematic Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--all", action="store_true", help="Execute all pipeline steps (1-4)")
    parser.add_argument("--step", type=int, nargs="+", choices=[1, 2, 3, 4], help="Run specific step numbers (e.g. --step 2 3 4)")
    parser.add_argument("--dry-run", action="store_true", help="Display execution plan without running scripts")
    args = parser.parse_args()

    print_banner()

    if not args.all and not args.step:
        print("No execution flag provided. Use --all or --step [1 2 3 4].")
        print("Run with -h for help.\n")
        parser.print_help()
        sys.exit(0)

    selected_steps = [1, 2, 3, 4] if args.all else sorted(args.step)

    print(f"Plan: Running step(s) {selected_steps}")
    start_total = time.time()

    for step_cfg in PIPELINE_STEPS:
        if step_cfg["step"] in selected_steps:
            success = execute_step(step_cfg, dry_run=args.dry_run)
            if not success:
                print(f"\nPipeline aborted due to failure in Step {step_cfg['step']}.")
                sys.exit(1)

    total_time = time.time() - start_total
    print("\n" + "=" * 78)
    print(f"  Pipeline execution completed in {total_time:.2f}s.")
    print(f"  Outputs generated in: {OUTPUTS_DIR.resolve()}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
