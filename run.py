"""
run_pipeline.py  —  Full pipeline for downloading and merging ocean data

Usage:
    python3 run_pipeline.py
        → Download tomorrow's data (default)

    python3 run_pipeline.py --date 2026-06-01
        → Use a custom date
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime, timedelta

# ── Select target date ─────────────────────────────────────────────
parser = argparse.ArgumentParser()

parser.add_argument(
    '--date',
    default=None,
    help='YYYY-MM-DD (default: tomorrow UTC)'
)

args = parser.parse_args()

TARGET_DATE = (
    args.date
    or (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
)

# ── Script paths (relative to run_pipeline.py) ────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    ("SST",   os.path.join(BASE, "sst", "get_sst.py")),
    ("CHL",   os.path.join(BASE, "chl", "get_chl.py")),
    ("SSH",   os.path.join(BASE, "ssh", "get_ssh.py")),
    ("SSS",   os.path.join(BASE, "sss", "get_sss.py")),
    ("MERGE", os.path.join(BASE, "get_data", "merge_data.py")),
]

# ── Terminal colors ───────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def run_step(name, script_path):

    print(f"\n{BOLD}{'─'*50}{RESET}")

    print(
        f"{BOLD}▶  {name}{RESET}  —  "
        f"{os.path.relpath(script_path)}"
    )

    print(f"{'─'*50}{RESET}")

    if not os.path.exists(script_path):

        print(f"{RED}✗ File not found: {script_path}{RESET}")

        return False

    # Pass TARGET_DATE as an environment variable
    # Each script can use it if available
    env = os.environ.copy()

    env["PIPELINE_DATE"] = TARGET_DATE

    result = subprocess.run(
        [sys.executable, script_path],
        env=env,
        cwd=os.path.dirname(script_path),
    )

    if result.returncode == 0:

        print(f"\n{GREEN}✓ {name} — Success{RESET}")

        return True

    else:

        print(
            f"\n{RED}✗ {name} — Failed "
            f"(exit code {result.returncode}){RESET}"
        )

        return False


def main():

    print(f"\n{BOLD}{'='*50}")

    print("  Ocean Data Pipeline — Dakhla")

    print(f"  Target date: {TARGET_DATE}")

    print(f"{'='*50}{RESET}")

    results = {}

    for name, path in SCRIPTS:

        success = run_step(name, path)

        results[name] = success

        # If a download step fails,
        # merging becomes useless
        if not success and name != "MERGE":

            print(
                f"\n{YELLOW}⚠ Stopped because "
                f"{name} failed."
            )

            print(
                "Check your internet connection "
                "or Copernicus data access."
                f"{RESET}"
            )

            break

    # ── Final summary ─────────────────────────────────────────────
    print(f"\n{BOLD}{'='*50}")

    print("  Pipeline Summary")

    print(f"{'='*50}{RESET}")

    all_ok = True

    for name, ok in results.items():

        icon = (
            f"{GREEN}✓{RESET}"
            if ok
            else f"{RED}✗{RESET}"
        )

        print(f"  {icon}  {name}")

        if not ok:
            all_ok = False

    if all_ok:

        csv = os.path.join(
            BASE,
            "get_data",
            "ocean_data",
            "dakhla_ai_features_full.csv"
        )

        print(f"\n{GREEN}{BOLD}✅ Pipeline completed successfully!{RESET}")

        print(f"   CSV: {csv}")

    else:

        print(
            f"\n{RED}{BOLD}❌ Pipeline finished with errors."
        )

        print(f"Check the messages above.{RESET}")

        sys.exit(1)


if __name__ == "__main__":

    main()
