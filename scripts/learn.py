#!/usr/bin/env python3
"""Weekly learning loop — distills LEDGER outcomes into permanent rules.
Runs Sun 17:30 (before weekly_review). Appends ≤3 rules to memory/lessons.md.
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import pathlib
import re

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
LEDGER = WS / "LEDGER.md"
MEM = WS / "memory" / "lessons.md"


def main():
    MEM.parent.mkdir(exist_ok=True)
    if not MEM.exists():
        MEM.write_text("# memory/lessons.md — what the farm learned. Newest last.\n")
    t = LEDGER.read_text() if LEDGER.exists() else ""
    week = datetime.date.today().isoformat()
    old = MEM.read_text()
    new = []
    # payouts > 0 → scale rule
    for m in re.finditer(r"paid:\$(\d+\.?\d*)", t):
        try:
            if float(m.group(1)) > 0:
                r = f"{week} | LEARN | a unit paid real money with zero hands → SCALER must clone it ×3 within 7d"
                if r not in old:
                    new.append(r)
                break
        except ValueError:
            pass
    # kills → avoidance rule
    kills = len(re.findall(r"[Kk][Ii][Ll][Ll]", t))
    if kills > 0:
        r = f"{week} | LEARN | {kills} kill-mentions so far → manual-work ideas die on sight, never debated twice"
        if r not in old:
            new.append(r)
    # key verification → custody rule
    if "KEY-OK" in t:
        r = f"{week} | LEARN | API keys verify via live call, never via docs alone → store local-only, rotate if pasted in chat"
        if r not in old:
            new.append(r)
    for r in new[:3]:
        with MEM.open("a") as f:
            f.write(f"- {r}\n")
    print(f"learn: {len(new[:3])} new rules")


if __name__ == "__main__":
    main()
