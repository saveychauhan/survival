#!/usr/bin/env python3
"""Performance scorecard — who earns, who talks, who starves.
Reads sessions (alive), bus manifest (messages/agent), LEDGER payout credits.
Writes SCORECARD.md sorted by payouts desc, then messages. Exit 0 always.
"""
import datetime
import json
import pathlib
import re
from collections import Counter

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
SESS = WS / "sessions"
OUT = WS / "SCORECARD.md"


def main():
    agents = {}
    for p in sorted(SESS.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            t = p.read_text()
        except Exception:
            continue
        aid = p.stem
        m = re.search(r"^- rank:\s*(.+)$", t, re.M)
        g = re.search(r"^- goal:\s*(.+)$", t, re.M)
        agents[aid] = {"rank": m.group(1).strip() if m else "?",
                       "goal": g.group(1).strip()[:60] if g else ""}
    msgs = Counter()
    try:
        items = json.loads((WS / "messages" / "manifest.json").read_text())

        def resolve(name):
            if name in agents:
                return name
            for a in agents:
                if a.startswith(name + "_"):
                    return a
            return name

        for m in items:
            msgs[resolve(m["from"])] += 1
    except Exception:
        pass
    payouts = Counter()
    try:
        t = (WS / "LEDGER.md").read_text()
        for unit, who in re.findall(r"credit (EU-\w+) → (\S+)", t):
            payouts[who.rstrip(",")] += 1
    except Exception:
        pass
    rows = sorted(agents, key=lambda a: (payouts.get(a, 0), msgs.get(a, 0)), reverse=True)
    lines = ["# SCORECARD.md — who performs. Auto-built, latest first row = top.",
             f"Updated {datetime.date.today().isoformat()}. Payouts rule; messages are sweat.",
             "",
             "| agent | rank | payouts | msgs | goal |",
             "|-------|------|---------|------|------|"]
    for a in rows:
        lines.append(f"| {a} | {agents[a]['rank']} | {payouts.get(a, 0)} | {msgs.get(a, 0)} | {agents[a]['goal']} |")
    OUT.write_text("\n".join(lines) + "\n")
    top = rows[0] if rows else "none"
    print(f"scorecard: {len(rows)} agents, top={top}")


if __name__ == "__main__":
    main()
