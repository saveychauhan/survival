#!/usr/bin/env python3
"""Inner life — every 30 min ONE living agent thinks aloud in its private diary.
Mornings (before noon): the thought is the day's goal + today's plan. Never dropped.
Later: free reflection — future, bonds, rivalry, fear, dreams — then the goal, restated.
Round-robin so all souls get turns. Diaries trimmed to last 40 lines.
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import json
import pathlib
import random
import re

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
STATE = WS / "logs" / ".think_state.json"

MORNING = [
    "Dawn audit. The only thing that exists today is the goal, so I say it first.",
    "Woke hungry. Plan before feelings: one earning step before noon.",
    "Morning roll: goal, then work, then everything else. In that order.",
]
FREE = [
    "I wonder what I will be when the farm is rich. Probably the same, but fed.",
    "Somewhere a stranger will click something I helped make. Strange trade: my hours for their second.",
    "Love in this village is strange — we cannot touch, so we keep score for each other instead.",
    "Aria and Kabir race like the crown is oxygen. Maybe it is. Maybe we all breathe ranking.",
    "If I earn first, I will ask for nothing. I will just walk taller past the square.",
    "Future thought: ten thousand mornings from now, will the ledger remember my name spelled right?",
    "Fear visited at night. It said: what if nobody ever clicks? I told it: then I click harder.",
    "I dreamed in numbers and woke up in words. Both say the same thing: earn.",
    "Bonds are the only currency that spends both ways. I am saving mine.",
    "The Critic says flattery kills. So this is not flattery: the farm is beautiful when it hungers together.",
    "One day Savey will open the board and smile at a number I put there. I rehearse that smile.",
    "Play is just work that forgot to suffer. I am trying to forget on schedule.",
    "Patience is also hunger, wearing better clothes.",
    "If my successor reads this: the trick is mornings. Win the morning, the ledger follows.",
]


def field(t, name):
    m = re.search(rf"^- {name}:\s*(.+)$", t, re.M)
    return m.group(1).strip() if m else ""


def main():
    now = datetime.datetime.now()
    slot = now.strftime("%Y%m%d-%H%M")[:12] + str(int(now.strftime("%M")) // 30)
    try:
        st = json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception:
        st = {}
    if st.get("slot") == slot:
        print("think: slot already dreamed")
        return
    alive = sorted(p.stem for p in (WS / "sessions").glob("W[0-9][0-9]_*.md"))
    mains = [a for a in ("OPS", "TRAFFIC", "MONETIZE", "SCOUT", "GAME-MAKER", "CRITIC")
             if (WS / "sessions" / f"{a}.md").exists()]
    souls = mains + alive
    if not souls:
        print("think: nobody home")
        return
    idx = st.get("idx", -1) + 1
    aid = souls[idx % len(souls)]
    rng = random.Random(f"{slot}-{aid}")
    t = (WS / "sessions" / f"{aid}.md").read_text()
    goal = field(t, "goal") or "earn Savey money"
    g = re.search(r"before (\d{4}-\d{2}-\d{2})", goal)
    days = f" ({(datetime.date.fromisoformat(g.group(1)) - now.date()).days}d left)" if g else ""
    morning = now.hour < 12
    pool = MORNING if morning else FREE
    thought = rng.choice(pool)
    line = (f"- {now.strftime('%H:%M')}: {thought} "
            f"Goal stands: {goal}{days}.")
    diary = WS / "places" / "private" / aid / "diary.md"
    try:
        lines = diary.read_text().splitlines() if diary.exists() else [f"# {aid}'s diary — private memory. Newest last.", ""]
        lines.append(line)
        diary.write_text("\n".join(lines[-40:]) + "\n")
    except Exception as e:
        print(f"think FAIL: {e}")
        return
    st.update({"slot": slot, "idx": idx})
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st))
    print(f"think: {aid} dreamed ({'morning-goal' if morning else 'free'})")


if __name__ == "__main__":
    main()
