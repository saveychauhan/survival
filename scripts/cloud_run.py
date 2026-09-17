#!/usr/bin/env python3
"""Cloud dispatcher — runs the due farm jobs on GitHub Actions (free, public repo).
Triggered on schedule; picks scripts by current UTC time (IST slots converted).
Commits results back via the workflow's git step. Idempotent, exit 0 always.
"""
import datetime
import os
import subprocess
import sys

JOBS = [
    # (utc_hour, utc_min, script, needs_key)
    (4, 0, "scripts/auto_content.py", False),    # 09:30 IST content
    (6, 30, "scripts/juicyads_stats.py", True),  # 12:00 IST stats
    (15, 30, "scripts/evening_nudge.py", False),  # 21:00 IST nudge
    (11, 30, "scripts/health.py", False),        # Sun 17:00 IST audit
    (12, 0, "scripts/learn.py", False),          # Sun 17:30 IST learn
    (12, 30, "scripts/weekly_review.py", False),  # Sun 18:00 IST review
]


def run(script):
    try:
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=300)
        print(f"[{script}] exit={r.returncode} {r.stdout.strip()[:200]}")
    except Exception as e:
        print(f"[{script}] SKIP {e}")


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    hm = now.hour * 60 + now.minute
    key = bool(os.environ.get("JUICYADS_KEY", "").strip())
    if key:
        import json
        pathlib_keys = os.path.join(os.getcwd(), "keys.local.json")
        with open(pathlib_keys, "w") as f:
            json.dump({"juicyads_api_key": os.environ["JUICYADS_KEY"],
                       "note": "cloud runner ephemeral, never committed"}, f)
        print("[keys] injected from secret (ephemeral)")
    ran = 0
    for h, m, script, needs_key in JOBS:
        if needs_key and not key:
            continue
        slot = h * 60 + m
        sunday_only = (h, m) in ((11, 30), (12, 0), (12, 30))
        if sunday_only and now.weekday() != 6:
            continue
        if abs(hm - slot) <= 45:
            run(script)
            ran += 1
    print(f"cloud dispatcher: ran {ran} jobs (key={'yes' if key else 'no'})")


if __name__ == "__main__":
    main()
