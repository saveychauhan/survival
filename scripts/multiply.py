#!/usr/bin/env python3
"""SCALER's hands — multiply the newest deals block into 3 long-tail variants.
Usage: multiply.py  (auto-picks last block in deals_data.json)
Zero human work, stdlib only, exit 0 always. Logs to LEDGER + EVOLUTION.
"""
import datetime
import json
import pathlib

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
DATA = WS / "docs" / "online" / "deals_data.json"
LEDGER = WS / "LEDGER.md"
EVO = WS / "EVOLUTION.md"

VARIANTS = [("under ₹1000", "+under+1000"), ("best of 2026", "+best+2026"), ("for students", "+for+students")]


def main():
    try:
        d = json.loads(DATA.read_text())
    except Exception as e:
        print(f"multiply FAIL: {e}")
        return
    blocks = d.get("blocks", [])
    if not blocks:
        print("multiply: no blocks")
        return
    title, kw, desc = blocks[-1]
    base_kw = kw.split("+under")[0].split("+best")[0]
    added = 0
    have = {b[1] for b in blocks}
    for suffix, kwmod in VARIANTS:
        nkw = base_kw + kwmod
        if nkw in have:
            continue
        blocks.append([f"{title} — {suffix}", nkw, desc])
        have.add(nkw)
        added += 1
    if added:
        d["blocks"] = blocks
        DATA.write_text(json.dumps(d, indent=1, ensure_ascii=False))
        msg = f"SCALER multiplied '{title}' ×{added} (long-tail variants)"
        D = datetime.date.today().isoformat()
        with LEDGER.open("a") as f:
            f.write(f"\n### {D} multiply - {msg}\n")
        with EVO.open("a") as f:
            f.write(f"\n- {D}: {msg}.\n")
    print(f"multiply: +{added} blocks (total {len(blocks)})")


if __name__ == "__main__":
    main()
