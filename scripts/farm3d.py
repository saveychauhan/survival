#!/usr/bin/env python3
"""3D-ish village game map — LOCAL ONLY, never committed, never served.
Reads sessions/manifest/LEDGER/SCORECARD and writes local/farm3d.html:
an offline isometric canvas world (no CDN, no internet needed).
Homes district, square, market, arena; small characters wander, click for details.
Open via localhost or double-click. Regen: python3 scripts/farm3d.py
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

    msgs, last_to = Counter(), {}
    for m in items:
        f = resolve(m["from"])
        msgs[f] += 1
        last_to[f] = m["to"]
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
        hang = last_to.get(aid, "HOME")
        if hang not in ("SQUARE", "MARKET", "ARENA"):
            hang = "HOME"
        souls.append({
            "id": aid, "short": aid.split("_")[0],
            "goal": field(t, "goal")[:90] or "?",
            "task": field(t, "next_action")[:90] or "?",
            "desire": field(t, "desires")[:90] or "?",
            "rank": field(t, "rank") or "?",
            "msgs": msgs.get(aid, 0), "pay": payouts.get(aid, 0),
            "color": COLORS.get(aid, "#a5b4fc"), "hang": hang,
            "dead": aid in ("CLOSER",),
        })
    data = {"built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "souls": souls}
    OUT.write_text(TEMPLATE.replace("__DATA__", json.dumps(data)))
    print(f"3d world: {len(souls)} souls -> local/farm3d.html (LOCAL ONLY, gitignored)")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tomorrowland — private world</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1526;color:#e2e8f0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}
#top{padding:10px 16px;font-size:13px;color:#94a3b8;background:#020617}#top b{color:#fcd34d}
#wrap{display:flex;gap:10px;padding:10px;align-items:flex-start;flex-wrap:wrap}
canvas{background:#0e1a30;border:1px solid #1e293b;border-radius:12px;cursor:pointer;max-width:100%}
#panel{width:290px;background:#020617;border:1px solid #334155;border-radius:12px;padding:14px;font-size:13px}
#panel h3{margin:0 0 6px;color:#fff}#panel .mut{color:#94a3b8;font-size:12px}#panel code{background:#1e293b;padding:1px 5px;border-radius:5px;color:#fff}
#panel p{margin:6px 0}
button{background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:8px;padding:8px 12px;margin:0 6px 10px 0;cursor:pointer;font-size:13px}
.legend{font-size:12px;color:#94a3b8;padding:0 16px 12px}
</style></head><body>
<div id="top"><b>TOMORROWLAND</b> · <span id="meta"></span> · LOCAL ONLY — click a walker</div>
<div id="wrap"><div><canvas id="cv" width="720" height="560"></canvas><br>
<button onclick="paused=!paused">pause / walk</button><button onclick="night=!night">day / night</button></div>
<div id="panel"><h3>Welcome</h3><p class="mut">10 souls live here. They walk between home and their hangout. Click one to inspect. Gold ring = earned money.</p></div></div>
<div class="legend">Homes (left blocks) · SQUARE plaza · MARKET stalls · ARENA ring · green dot = active this week · grey = dormant</div>
<script>
var DATA=__DATA__;
document.getElementById('meta').textContent='built '+DATA.built+' · '+DATA.souls.length+' souls';
var cv=document.getElementById('cv'),ctx=cv.getContext('2d');
var TW=34,TH=17,OX=cv.width/2,OY=70,night=false,paused=false,sel=null;
function px(x,y){return [OX+(x-y)*TW/2,OY+(x+y)*TH/2]}
function poly(pts,fill,stroke){ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);ctx.closePath();ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke()}}
function shade(hex,f){var n=parseInt(hex.slice(1),16),r=(n>>16)*f,g=((n>>8)&255)*f,b=(n&255)*f;return 'rgb('+(r|0)+','+(g|0)+','+(b|0)+')'}
// ---- static map ----
var HOMES=[['OPS',1,1],['TRAFFIC',1,4],['MONETIZE',1,7],['SCOUT',1,10],['GAME-MAKER',4,1],['CRITIC',4,4],['W01',4,7],['W02',4,10],['+2',4,12]];
var PLACES={SQUARE:[10,3],MARKET:[10,8],ARENA:[10,13]};
function tile(x,y,c1,c2){var p=px(x,y),q=px(x+1,y),r=px(x+1,y+1),s=px(x,y+1);poly([p,q,r,s],((x+y)%2?c1:c2),'rgba(0,0,0,.25)')}
function hut(x,y,color,name){var p=px(x,y),q=px(x+1,y),r=px(x+0.5,y+0.5);
// walls
poly([p,q,[q[0],q[1]-26],[p[0],p[1]-26]],shade(color,.55),'rgba(0,0,0,.3)');
poly([q,r,[r[0],r[1]-26],[q[0],q[1]-26]],shade(color,.4),'rgba(0,0,0,.3)');
// roof
poly([[p[0],p[1]-26],[q[0],q[1]-26],[r[0]-0,r[1]-44]],shade(color,.9));
poly([[q[0],q[1]-26],[r[0],r[1]-26],[r[0],r[1]-44]],shade(color,.7));
ctx.fillStyle='#fff';ctx.font='10px sans-serif';ctx.textAlign='center';ctx.fillText(name,(p[0]+q[0])/2,p[1]-30)}
function drawMap(){
var g1=night?'#0c1830':'#14331f',g2=night?'#0a1428':'#102a1a';
for(var x=0;x<15;x++)for(var y=0;y<15;y++)tile(x,y,g1,g2);
// paths
[[2,2,2,11],[5,2,5,11],[8,2,8,13]].forEach(function(L){for(var y=L[1];y<=L[3];y++)tile(L[0],y,night?'#1c2a44':'#4a3b28',night?'#1c2a44':'#4a3b28')});
// square plaza + fountain
var c=px(10.5,3.5);ctx.beginPath();ctx.ellipse(c[0],c[1],44,22,0,0,7);ctx.fillStyle=night?'#1e3a5f':'#3b82a6';ctx.fill();
ctx.beginPath();ctx.ellipse(c[0],c[1]-8,12,6,0,0,7);ctx.fillStyle='#bae6fd';ctx.fill();
ctx.fillStyle='#fff';ctx.font='10px sans-serif';ctx.textAlign='center';ctx.fillText('SQUARE',c[0],c[1]+30);
// market stalls
for(var i=0;i<3;i++){var s=px(9.4+i*0.7,8.2);poly([[s[0]-12,s[1]],[s[0]+12,s[1]],[s[0]+6,s[1]-14],[s[0]-6,s[1]-14]],['#ef4444','#f59e0b','#22c55e'][i]);}
var m=px(10,9);ctx.fillStyle='#fff';ctx.fillText('MARKET',m[0],m[1]+24);
// arena ring
var a=px(10.5,13.3);ctx.beginPath();ctx.ellipse(a[0],a[1],46,23,0,0,7);ctx.strokeStyle='#fb7185';ctx.lineWidth=4;ctx.stroke();
ctx.fillStyle='#fff';ctx.fillText('ARENA',a[0],a[1]+32);
// homes
var cols=['#f59e0b','#4ade80','#38bdf8','#c084fc','#fb7185','#f87171','#a5b4fc','#a5b4fc','#334155'];
HOMES.forEach(function(h,i){hut(h[1],h[2],cols[i%cols.length],h[0])});
}
// ---- walkers ----
var R=0.5; // deterministic pseudo-random
function rnd(){R=(R*9301+49297)%233280;return R/233280}
var walkers=DATA.souls.map(function(s,i){
var hx=1+(i%2)*3,hy=1+Math.floor(i/2)*3;if(hy>12)hy=12-(i%3);
var hp=PLACES[s.hang]||[hx,hy];
return {s:s,hx:hx,hy:hy,tx:hp[0]+rnd()*1.5,ty:hp[1]+rnd()*1.5,x:hx,y:hy,sp:1.1+rnd()*0.9,ph:rnd()*6};
});
function step(dt){
walkers.forEach(function(w){
if(paused)return;
var dx=w.tx-w.x,dy=w.ty-w.y,d=Math.hypot(dx,dy);
if(d<0.15){var homeBias=rnd()<0.45;var hp=PLACES[w.s.hang]||[w.hx,w.hy];
w.tx=homeBias?w.hx+rnd():(hp[0]+rnd()*1.6-0.3);w.ty=homeBias?w.hy+rnd():(hp[1]+rnd()*1.6-0.3);return}
w.x+=dx/d*w.sp*dt;w.y+=dy/d*w.sp*dt;w.ph+=dt*6});
}
function draw(t){
ctx.clearRect(0,0,cv.width,cv.height);drawMap();
var order=walkers.slice().sort(function(a,b){return (a.x+a.y)-(b.x+b.y)});
order.forEach(function(w){
var p=px(w.x,w.y),bob=Math.sin(w.ph)*2;
var active=w.s.msgs>0,col=active?'#22c55e':'#64748b';
ctx.beginPath();ctx.ellipse(p[0],p[1],10,4,0,0,7);ctx.fillStyle='rgba(0,0,0,.35)';ctx.fill();
if(w.s.pay>0){ctx.beginPath();ctx.arc(p[0],p[1]-16+bob,15,0,7);ctx.strokeStyle='#fcd34d';ctx.lineWidth=2;ctx.stroke()}
ctx.fillStyle=w.s.color;ctx.fillRect(p[0]-6,p[1]-26+bob,12,14);
ctx.beginPath();ctx.arc(p[0],p[1]-30+bob,6,0,7);ctx.fillStyle='#fde68a';ctx.fill();
ctx.fillStyle=col;ctx.beginPath();ctx.arc(p[0]+8,p[1]-34+bob,3,0,7);ctx.fill();
ctx.fillStyle='#fff';ctx.font='10px sans-serif';ctx.textAlign='center';ctx.fillText(w.s.short,p[0],p[1]-40+bob);
w.sx=p[0];w.sy=p[1]-20+bob});
}
var last=0;
function loop(t){var dt=Math.min(0.05,(t-last)/1000||0);last=t;step(dt);draw(t);requestAnimationFrame(loop)}
requestAnimationFrame(loop);
cv.onclick=function(e){var r=cv.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,best=null,bd=1e9;
walkers.forEach(function(w){var d=Math.hypot(w.sx-mx,w.sy-my);if(d<bd){bd=d;best=w}});
var panel=document.getElementById('panel');
if(best&&bd<26){var s=best.s;panel.innerHTML='<h3>'+s.id+'</h3><p><code>'+s.rank+'</code></p><p><b>Goal:</b> '+s.goal+'</p><p><b>Now:</b> '+s.task+'</p><p><b>Wants:</b> '+s.desire+'</p><p><b>Hangout:</b> '+s.hang+'</p><p class="mut">earned $'+s.pay+' · '+s.msgs+' messages</p>'}
else{panel.innerHTML='<h3>Welcome</h3><p class="mut">10 souls live here. Click one to inspect. Gold ring = earned money.</p>'}};
</script></body></html>"""

if __name__ == "__main__":
    main()
