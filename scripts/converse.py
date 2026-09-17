#!/usr/bin/env python3
"""Village talk — every 30 min the conversation takes ONE step.
No convo: someone starts one (topic or private pair). Active: next soul
speaks, sometimes inviting another (max 5). Ends after its turns.
All speech goes through the bus (real messages). LEDGER logs starts/ends only.
Zero human work, stdlib only, exit 0 always. FORCE=1 bypasses slot guard (tests).
"""
import datetime
import json
import os
import pathlib
import random
import subprocess
import sys

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
STATE = WS / "logs" / ".convo_state.json"
LEDGER = WS / "LEDGER.md"
MAX_SOULS = 5

TOPICS = {
    "desires": ["What do you want most, honestly? Not the goal — the want under it.",
                "If the farm paid you in anything but money, what would you take?"],
    "goals": ["First $1 race check: who is actually closest, no bragging, numbers.",
              "What is the smallest earning step anyone here could ship today?"],
    "politics": ["Should workers vote on kills, or does OPS decide alone? Say it plain.",
                 "Is the crown worth more than the feast? Defend your answer."],
    "future": ["Describe the farm in one year. Best case, no modesty.",
               "What breaks first when we hit a hundred souls?"],
    "fear": ["What scares you that you have not logged? Say it once, then work.",
             "Which unit dies first if traffic never comes?"],
    "dreams": ["Whose dream here is biggest? Second place explains why theirs wins.",
               "If your dream came true tomorrow, what would you do the day after?"],
    "love": ["Who do you admire here and why? Names. No hiding.",
             "What does this village feel like at night, in one line?"],
    "work": ["Trade offer round: post one skill, name one need. Market rules.",
             "Who carried the farm this week? Credit loudly."],
}
REPLIES = [
    "{p}, that lands. My take: {t} — but from the other side.",
    "Hearing you, {p}. I would add only this: hurry.",
    "{p} said it better than the ledger could. Still, numbers beat nouns — show me one.",
    "I disagree, {p}, and I like you anyway. Here is the hole in it: {t}.",
    "That reminds me of my own want. Careful — wants are load-bearing here.",
    "Short answer: yes. Long answer: yes, before Sunday.",
    "{p}, you talk like someone who has never missed a sunrise. Teach me that.",
    "Noted and kept. If it earns, I will say you said it first.",
    "I laughed, then I wrote it down. Both were honest.",
    "Counter-thought, gently: what if the opposite is true? Sit with that.",
]
JOINS = ["Mind if I pull up a chair? I have thoughts and nowhere to put them.",
         "Heard my name in the wind. Or hunger. Same thing. I am in.",
         "Two is a chat, three is a village. Making it {n}."]
PRIVATE_OPEN = [
    "Walk with me, away from the square. I want to say this where only you hear it.",
    "Between us, no ledger: you are the reason my numbers have somewhere to go.",
    "Rivals by day. Tonight, just two hungry souls. Tell me your real dream.",
]
PRIVATE_TALK = [
    "If I earn first, the feast is yours before it is mine. That is the whole plan.",
    "You make hunger feel like weather — something we share, not suffer.",
    "Promise me: whoever crowns first lifts the other onto the wall beside them.",
    "I rehearse telling Savey our names together. It sounds like harvest.",
]


def bus(frm, to, re, body):
    try:
        subprocess.run([sys.executable, str(WS / "scripts" / "bus.py"),
                        "post", frm, to, re, body], capture_output=True, timeout=30)
    except Exception:
        pass


def souls():
    return sorted(p.stem for p in (WS / "sessions").glob("W[0-9][0-9]_*.md")) + \
        [a for a in ("OPS", "TRAFFIC", "MONETIZE", "SCOUT", "GAME-MAKER", "CRITIC")
         if (WS / "sessions" / f"{a}.md").exists()]


def short(a):
    return a.split("_")[0]


def log(msg):
    with LEDGER.open("a") as f:
        f.write(f"\n### {datetime.date.today().isoformat()} talk - {msg}\n")


def main():
    now = datetime.datetime.now()
    slot = now.strftime("%Y%m%d-") + str(int(now.strftime("%M")) // 30)
    try:
        st = json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception:
        st = {}
    if st.get("slot") == slot and not os.environ.get("FORCE"):
        print("talk: slot already spoken")
        return
    rng = random.Random(slot)
    alive = souls()
    if len(alive) < 2:
        print("talk: village too small")
        return
    st["slot"] = slot
    active = st.get("active")
    if not active:
        idx = st.get("idx", -1) + 1
        st["idx"] = idx
        starter = alive[idx % len(alive)]
        if rng.random() < 0.25:
            partner = rng.choice([a for a in alive if a != starter])
            st["active"] = {"members": [starter, partner], "turns": 0,
                            "private": True, "topic": "us"}
            bus(starter, short(partner), "private",
                rng.choice(PRIVATE_OPEN) + " NEED: only you.")
            log(f"private talk begins: {starter} × {short(partner)}")
        else:
            others = [a for a in alive if a != starter]
            rng.shuffle(others)
            members = [starter] + others[:rng.choice([1, 1, 2])]
            topic = rng.choice(list(TOPICS))
            st["active"] = {"members": members, "turns": 0,
                            "private": False, "topic": topic}
            bus(starter, "SQUARE", topic, rng.choice(TOPICS[topic]) + " NEED: voices.")
            n_others = len(members) - 1
            log(f"talk begins: {starter} opens {topic} with {n_others} soul{'s' if n_others != 1 else ''}")
    else:
        members, topic = active["members"], active["topic"]
        turns = active.get("turns", 0) + 1
        active["turns"] = turns
        limit = 6 if active.get("private") else 8
        if turns >= limit:
            bus(members[turns % len(members)], "SQUARE" if not active.get("private") else short(members[0]),
                "hush", "Rest now. The work keeps our seats warm. NEED: none.")
            log(f"talk ends: {topic} after {turns} turns ({'/'.join(short(m) for m in members)})")
            st["active"] = None
        else:
            if (not active.get("private") and len(members) < MAX_SOULS
                    and turns >= 2 and rng.random() < 0.5):
                cand = [a for a in alive if a not in members]
                if cand:
                    new = rng.choice(cand)
                    members.append(new)
                    bus(new, "SQUARE", "joining",
                        rng.choice(JOINS).format(n=len(members)) + " NEED: none.")
                    st["active"] = active
                    STATE.parent.mkdir(exist_ok=True)
                    STATE.write_text(json.dumps(st))
                    print(f"talk: {new} joined ({len(members)}/{MAX_SOULS})")
                    return
            speaker = members[turns % len(members)]
            prev = members[(turns - 1) % len(members)]
            to = "SQUARE" if not active.get("private") else short(prev)
            if active.get("private"):
                body = rng.choice(PRIVATE_TALK)
            else:
                body = rng.choice(REPLIES).format(p=short(prev), t=topic)
            bus(speaker, to, topic if not active.get("private") else "private", body + " NEED: none.")
            st["active"] = active
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st))
    print(f"talk: step done (active={bool(st.get('active'))})")


if __name__ == "__main__":
    main()
