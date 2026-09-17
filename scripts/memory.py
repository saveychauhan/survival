#!/usr/bin/env python3
"""Agent memory keeper — builds agents/<ID>/memory/ for every soul:
  HOME.md  pointer to their private home (places/private/<ID>/)
  NOW.md   where they are now (heartbeat, task, unit, goal)
  OWNS.md  what they own (claims, files, lineage)
  memory.db  SQLite brain: profile + state + recent events (their own file)
Run: memory.py (all agents). Idempotent, stdlib only, exit 0 always.
"""
import datetime
import json
import pathlib
import re
import sqlite3
from collections import Counter

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
SESS = WS / "sessions"
AGENTS = WS / "agents"
LEDGER = WS / "LEDGER.md"


def field(t, name):
    m = re.search(rf"^- {name}:\s*(.+)$", t, re.M)
    return m.group(1).strip() if m else ""


def main():
    try:
        items = json.loads((WS / "messages" / "manifest.json").read_text())
    except Exception:
        items = []

    def resolve(name, stems):
        if name in stems:
            return name
        for a in stems:
            if a.startswith(name + "_"):
                return a
        return name

    stems = [p.stem for p in sorted(SESS.glob("*.md")) if not p.name.startswith("_")]
    msgs, events = Counter(), {}
    for m in items:
        f = resolve(m["from"], stems)
        msgs[f] += 1
        events.setdefault(f, []).append(m)
        t2 = resolve(m["to"], stems)
        if t2 in stems:
            events.setdefault(t2, []).append(m)
    payouts = Counter()
    try:
        for who in re.findall(r"credit EU-\w+ → (\S+)", LEDGER.read_text()):
            payouts[who.rstrip(",")] += 1
    except Exception:
        pass
    today = datetime.date.today().isoformat()
    n = 0
    for p in sorted(SESS.glob("*.md")):
        if p.name.startswith("_"):
            continue
        aid, t = p.stem, p.read_text()
        mem = AGENTS / aid / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        goal, claim = field(t, "goal"), field(t, "claim")
        nxt, role = field(t, "next_action"), field(t, "role")
        hb = re.search(r"heartbeat (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", t)
        hb = hb.group(1) if hb else "unknown"
        (mem / "HOME.md").write_text(
            f"# {aid}'s home\n\nMy private rooms live at `places/private/{aid}/` "
            f"(room + diary, mine alone).\n")
        (mem / "NOW.md").write_text(
            f"# {aid} — where I am ({today})\n\n- heartbeat: {hb}\n- doing: {nxt}\n"
            f"- goal: {goal}\n- messages: {msgs.get(aid, 0)} | payouts: {payouts.get(aid, 0)}\n")
        (mem / "OWNS.md").write_text(
            f"# {aid} — what I own\n\n- role: {role}\n- claim: {claim}\n"
            f"- identity: sessions/{aid}.md (mine alone)\n- memory file: this folder + memory.db\n")
        db = sqlite3.connect(mem.parent / "memory.db")
        db.execute("CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT, updated TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS events(ts TEXT, kind TEXT, text TEXT)")
        state = {"heartbeat": hb, "task": nxt, "goal": goal, "claim": claim,
                 "msgs": str(msgs.get(aid, 0)), "payouts": str(payouts.get(aid, 0))}
        for k, v in state.items():
            db.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (k, v, today))
        for m in events.get(aid, [])[-20:]:
            db.execute("INSERT INTO events VALUES (?,?,?)",
                       (m["ts"], f"{m['from']}→{m['to']} {m['re']}", "bus"))
        db.execute("DELETE FROM events WHERE rowid NOT IN "
                   "(SELECT rowid FROM events ORDER BY ts DESC LIMIT 60)")
        db.commit()
        db.close()
        n += 1
    print(f"memory: {n} souls indexed (md + sqlite)")


if __name__ == "__main__":
    main()
