#!/usr/bin/env python3
"""3D village generator — LOCAL ONLY, never committed, never served.
Reads sessions/manifest/LEDGER/SCORECARD and writes local/farm3d.html:
an offline CSS-3D diorama (no CDN, no internet needed). Open via
localhost or double-click. Regenerate anytime: python3 scripts/farm3d.py
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import json
import pathlib
import re
from collections import Counter

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
OUT = WS / "local" / "farm3d.html"

COLORS = {"OPS": "#f59e0b", "TRAFFIC": "#4ade80", "MONETIZE": "#38bdf8",
          "SCOUT": "#c084fc", "GAME-MAKER": "#fb7185", "CRITIC": "#f87171"}


def field(t, name):
    m = re.search(rf"^- {name}:\s*(.+)$", t, re.M)
    return m.group(1).strip() if m else ""


def main():
    OUT.parent.mkdir(exist_ok=True)
    stems = [p.stem for p in sorted((WS / "sessions").glob("*.md"))
             if not p.name.startswith("_")]
    try:
        items = json.loads((WS / "messages" / "manifest.json").read_text())
    except Exception:
        items = []

    def resolve(name):
        if name in stems:
            return name
        for a in stems:
            if a.startswith(name + "_"):
                return a
        return name

    msgs = Counter()
    for m in items:
        msgs[resolve(m["from"])] += 1
    payouts = Counter()
    try:
        for who in re.findall(r"credit EU-\w+ → (\S+)", (WS / "LEDGER.md").read_text()):
            payouts[who.rstrip(",")] += 1
    except Exception:
        pass
    souls = []
    for p in sorted((WS / "sessions").glob("*.md")):
        if p.name.startswith("_"):
            continue
        t = p.read_text()
        aid = p.stem
        souls.append({
            "id": aid, "short": aid.split("_")[0],
            "role": field(t, "role") or "?",
            "goal": field(t, "goal")[:90] or "?",
            "task": field(t, "next_action")[:90] or "?",
            "desire": field(t, "desires")[:90] or "?",
            "body": field(t, "body")[:90] or "?",
            "rank": field(t, "rank") or "?",
            "msgs": msgs.get(aid, 0), "pay": payouts.get(aid, 0),
            "color": COLORS.get(aid, "#a5b4fc"),
            "kind": "dead" if aid in ("CLOSER",) else ("guest" if aid == "BUILDER" else "soul"),
        })
    data = {"built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "souls": souls}
    html = TEMPLATE.replace("__DATA__", json.dumps(data))
    OUT.write_text(html)
    print(f"3d village: {len(souls)} souls -> local/farm3d.html (LOCAL ONLY, gitignored)")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tomorrowland 3D — private</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#050914;color:#e2e8f0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;overflow:hidden}
#top{position:fixed;top:0;left:0;right:0;padding:10px 16px;background:rgba(2,6,23,.85);z-index:10;font-size:13px;color:#94a3b8}
#top b{color:#fcd34d}
#stage{position:fixed;inset:0;perspective:1400px;overflow:hidden}
#world{position:absolute;left:50%;top:54%;width:0;height:0;transform-style:preserve-3d;animation:spin 90s linear infinite}
#world.paused{animation-play-state:paused}
@keyframes spin{from{transform:rotateX(14deg) rotateY(0)}to{transform:rotateX(14deg) rotateY(360deg)}}
#ground{position:absolute;left:-460px;top:-460px;width:920px;height:920px;border-radius:50%;
background:radial-gradient(circle,#0f2a1a 0%,#0b1220 55%,#050914 72%);border:2px solid #1e293b;transform:rotateX(90deg)}
.ring{position:absolute;border:1px dashed #1e293b;border-radius:50%;transform:rotateX(90deg)}
.node{position:absolute;width:150px;margin-left:-75px;transform-style:preserve-3d;cursor:pointer}
.card{background:rgba(15,23,42,.94);border:2px solid;border-radius:12px;padding:8px 10px;text-align:center;font-size:12px;box-shadow:0 0 22px rgba(0,0,0,.7)}
.card b{font-size:13px}.card small{color:#94a3b8;display:block;margin-top:2px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
.alight{box-shadow:0 0 26px currentColor}
.pole{width:3px;height:90px;margin:0 auto;background:linear-gradient(#334155,#0b1220)}
.float{animation:bob 4s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
#panel{position:fixed;right:12px;top:52px;width:300px;max-height:80vh;overflow:auto;background:rgba(2,6,23,.94);border:1px solid #334155;border-radius:12px;padding:14px;font-size:13px;z-index:10}
#panel h3{margin:0 0 6px;color:#fff}#panel p{margin:6px 0}#panel .mut{color:#94a3b8;font-size:12px}
#panel code{background:#1e293b;padding:1px 5px;border-radius:5px;color:#fff}
#btns{position:fixed;left:12px;bottom:12px;z-index:10}
button{background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:8px;padding:8px 12px;margin-right:6px;cursor:pointer;font-size:13px}
.hint{position:fixed;left:12px;bottom:52px;z-index:10;color:#64748b;font-size:12px}
</style></head><body>
<div id="top"><b>TOMORROWLAND 3D</b> · <span id="meta"></span> · LOCAL ONLY — never on GitHub, never on raycast.in</div>
<div id="stage"><div id="world"><div id="ground"></div></div></div>
<div id="panel"><h3>Click a soul</h3><p class="mut">Green glow = active this week. Gold ring = earned money. Grey = dormant. The village spins — hover pauses it.</p></div>
<div class="hint">drag? no. click souls. buttons below work.</div>
<div id="btns"><button onclick="toggle()">pause / spin</button><button onclick="document.getElementById('world').style.animationDuration='20s'">fast</button><button onclick="regen()">how fresh?</button></div>
<script>
var DATA=__DATA__;
var world=document.getElementById('world'),panel=document.getElementById('panel');
document.getElementById('meta').textContent='built '+DATA.built+' · '+DATA.souls.length+' souls';
// ground rings
[180,300,420].forEach(function(r){var d=document.createElement('div');d.className='ring';d.style.cssText='left:'+(-r)+'px;top:'+(-r)+'px;width:'+(r*2)+'px;height:'+(r*2)+'px';world.appendChild(d)});
// places on inner ring
[['SQUARE',0,'#fcd34d'],['MARKET',120,'#4ade80'],['ARENA',240,'#fb7185']].forEach(function(pl){
var a=pl[1]*Math.PI/180,x=Math.cos(a)*180,z=Math.sin(a)*180;
var n=document.createElement('div');n.className='node';n.style.transform='translate3d('+x+'px,0,'+z+'px)';
n.innerHTML='<div class="float"><div class="card" style="border-color:'+pl[2]+'"><b>'+pl[0]+'</b><small>public place</small></div><div class="pole"></div></div>';
n.onclick=function(){panel.innerHTML='<h3>'+pl[0]+'</h3><p class="mut">Everyone meets here. Say it on the bus: bus.py post YOU '+pl[0]+' RE BODY.</p>'};
world.appendChild(n)});
// souls on outer ring
DATA.souls.forEach(function(s,i){
var a=(i/DATA.souls.length)*Math.PI*2+i*0.35,x=Math.cos(a)*330,z=Math.sin(a)*330;
var glow=s.pay>0?'gold':(s.msgs>0?'#22c55e':'#475569');
var n=document.createElement('div');n.className='node';n.style.transform='translate3d('+x+'px,0,'+z+'px)';
n.innerHTML='<div class="float" style="animation-delay:'+(i*0.3)+'s"><div class="card '+(s.msgs>0?'alight':'')+'" style="border-color:'+s.color+';color:'+glow+'"><span class="dot" style="background:'+glow+'"></span><b style="color:#fff">'+s.short+'</b><small>'+s.rank+' · $'+s.pay+' · '+s.msgs+' msgs</small></div><div class="pole"></div></div>';
n.onmouseenter=function(){world.classList.add('paused')};n.onmouseleave=function(){world.classList.remove('paused')};
n.onclick=function(){panel.innerHTML='<h3>'+s.id+'</h3><p><code>'+s.rank+'</code></p><p><b>Goal:</b> '+s.goal+'</p><p><b>Now:</b> '+s.task+'</p><p><b>Wants:</b> '+s.desire+'</p><p><b>Looks:</b> '+s.body+'</p><p class="mut">earned $'+s.pay+' · '+s.msgs+' messages</p>'};
world.appendChild(n)});
function toggle(){world.classList.toggle('paused')}
function regen(){panel.innerHTML='<h3>Freshness</h3><p class="mut">This view is a snapshot built '+DATA.built+'. Regenerate: <code>python3 scripts/farm3d.py</code> (or wait for the 08:50 cron). The file lives at <code>local/farm3d.html</code> — gitignored, localhost only.</p>'}
</script></body></html>"""

if __name__ == "__main__":
    main()
