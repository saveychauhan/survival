#!/usr/bin/env python3
"""Inter-agent message bus — files only, stdlib only, zero human work.
Usage:
  bus.py post <FROM> <TO> <RE> <BODY...>
  bus.py inbox <AGENT>          (lists messages TO agent, newest first)
  bus.py manifest               (rebuild messages/manifest.json for index)
File: messages/MSG-<FROM>-<TO>-<YYYYMMDD-HHMM>.md
"""
import datetime
import json
import pathlib
import sys

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
BOX = WS / "messages"
BOX.mkdir(exist_ok=True)


def _parse(p):
    try:
        _, frm, to, ts = p.stem.split("-", 3)
        txt = p.read_text()
        re = ""
        for line in txt.splitlines():
            if line.startswith("RE:"):
                re = line[3:].strip()
                break
        return {"file": p.name, "from": frm, "to": to, "re": re, "ts": ts}
    except Exception:
        return None


def rebuild_manifest():
    items = [m for m in (_parse(p) for p in BOX.glob("MSG-*.md")) if m]
    items.sort(key=lambda m: m["ts"], reverse=True)
    (BOX / "manifest.json").write_text(json.dumps(items, indent=1))
    return items


def post(frm, to, re, body):
    frm, to = frm.upper().strip(), to.upper().strip()
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    p = BOX / f"MSG-{frm}-{to}-{ts}.md"
    p.write_text(f"TO: {to}\nFROM: {frm}\nRE: {re}\nDATE: {ts}\n\n{body}\n")
    rebuild_manifest()
    print(f"posted {p.name}")


def inbox(agent):
    agent = agent.upper().strip()
    items = [m for m in rebuild_manifest() if m["to"] == agent]
    if not items:
        print(f"inbox {agent}: empty")
        return
    for m in items:
        print(f"[{m['ts']}] {m['from']}→{m['to']} RE:{m['re']} ({m['file']})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    cmd = sys.argv[1]
    if cmd == "post" and len(sys.argv) >= 6:
        post(sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
    elif cmd == "inbox" and len(sys.argv) == 3:
        inbox(sys.argv[2])
    elif cmd == "manifest":
        items = rebuild_manifest()
        print(f"manifest: {len(items)} messages")
    else:
        print(__doc__)
        raise SystemExit(1)
