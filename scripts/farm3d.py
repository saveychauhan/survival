#!/usr/bin/env python3
"""Raycast world — LOCAL ONLY, never committed, never served.
Reads sessions/manifest/LEDGER/SCORECARD and writes local/farm3d.html:
an offline isometric canvas world (no CDN, no internet needed).
Painted map: homes, plaza, stalls, arena, pond, pines, wandering souls.
Open via localhost or double-click. Regen: python3 scripts/farm3d.py
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import html
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
        nm = re.search(r"^# Agent:\s*([^\(\n—]+)", t, re.M)
        disp = nm.group(1).strip() if nm else (aid.split("_")[1] if "_" in aid else aid)
        hang = last_to.get(aid, "HOME")
        if hang not in ("SQUARE", "MARKET", "ARENA"):
            hang = "HOME"
        souls.append({
            "id": aid, "short": disp,
            "goal": field(t, "goal")[:90] or "?",
            "task": field(t, "next_action")[:90] or "?",
            "desire": field(t, "desires")[:90] or "?",
            "rank": field(t, "rank") or "?",
            "msgs": msgs.get(aid, 0), "pay": payouts.get(aid, 0),
            "color": COLORS.get(aid, "#a5b4fc"), "hang": hang,
        })
    data = {"built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "souls": souls}
    # talk: latest message per soul (max 4 freshest speak in-world) + feed html
    seen, recent = set(), []
    for m in items:
        f = resolve(m["from"])
        if f in stems and f not in seen:
            seen.add(f)
            try:
                body = (WS / "messages" / m["file"]).read_text().split("\n\n", 1)[1].strip()
            except Exception:
                body = ""
            recent.append({"from": f, "to": m["to"], "re": m["re"],
                           "ts": m["ts"], "body": body[:180]})
    say = {r["from"]: r["body"] for r in recent[:4]}
    for s in souls:
        s["say"] = say.get(s["id"], "")
    feed = "".join(
        f"<div class='talk'><b>{html.escape(r['from'])} → {html.escape(r['to'])}</b> "
        f"<small>{html.escape(r['re'])}</small><br>{html.escape(r['body'][:140])}</div>"
        for r in recent[:6])
    OUT.write_text(TEMPLATE.replace("__DATA__", json.dumps(data)).replace("__TALK__", feed or "<p class='mut'>Silence. Suspicious.</p>"))
    print(f"world: {len(souls)} souls, {len(recent)} voices -> local/farm3d.html (LOCAL ONLY, gitignored)")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Raycast — private world</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#070d1d;color:#e2e8f0;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}
#top{padding:10px 18px;font-size:13px;color:#94a3b8;background:#020617}#top b{color:#fcd34d;letter-spacing:1px}
#wrap{display:flex;gap:12px;padding:12px 18px;align-items:flex-start;flex-wrap:wrap}
canvas{border-radius:14px;cursor:pointer;max-width:100%;box-shadow:0 12px 60px rgba(0,0,0,.6)}
#panel{width:300px;background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;font-size:13px}
#panel h3{margin:0 0 4px;color:#fff;font-size:17px}#panel .mut{color:#94a3b8;font-size:12px}
#panel code{background:#1e293b;padding:1px 6px;border-radius:5px;color:#fff}#panel p{margin:7px 0}
.talk{border-left:3px solid #4ade80;background:#0f172a;border-radius:8px;padding:7px 9px;margin:7px 0;font-size:12px}
.talk small{color:#94a3b8}
#bar{height:6px;border-radius:3px;margin:4px 0 8px}
button{background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:9px;padding:9px 14px;margin:0 8px 12px 0;cursor:pointer;font-size:13px}
button:hover{background:#334155}
.legend{font-size:12px;color:#94a3b8;padding:0 18px 14px}
</style></head><body>
<div id="top"><b>RAYCAST</b> · <span id="meta"></span> · LOCAL ONLY</div>
<div id="wrap"><div><canvas id="cv" width="780" height="600"></canvas><br>
<button onclick="paused=!paused">pause / walk</button><button onclick="nightTarget=nightTarget?0:1">day / night</button></div>
<div id="panel"><div id="who"><h3>Welcome home</h3><p class="mut">Click anyone strolling the land. Gold ring = earned money. Green spark = active this week.</p></div><h3>Village talk</h3><div id="talkfeed">__TALK__</div></div></div>
<div class="legend">Homes glow warm at night · taunts in the arena · trades at the stalls · feasts at the fountain</div>
<script>
var DATA=__DATA__;
document.getElementById('meta').textContent='built '+DATA.built+' · '+DATA.souls.length+' souls';
var cv=document.getElementById('cv'),ctx=cv.getContext('2d');
var TW=40,TH=20,OX=500,OY=120,nightTarget=0,nightF=0,paused=false,T=0;
function fit(){cv.width=Math.max(700,window.innerWidth-380);cv.height=Math.max(560,window.innerHeight-150);OX=cv.width/2-40;OY=130}
window.onresize=fit;fit();
function px(x,y){return [OX+(x-y)*TW/2,OY+(x+y)*TH/2]}
function hx(h){return [parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]}
function mix(a,b,f){var A=hx(a),B=hx(b);return 'rgb('+Math.round(A[0]+(B[0]-A[0])*f)+','+Math.round(A[1]+(B[1]-A[1])*f)+','+Math.round(A[2]+(B[2]-A[2])*f)+')'}
function shade(hex,f){var c=hx(hex);return 'rgb('+Math.round(c[0]*f)+','+Math.round(c[1]*f)+','+Math.round(c[2]*f)+')'}
// palette lerps day<->night
var SKY0=['#0e1a30','#02040c'],SKY1=['#16213c','#050914'];
function sky(){var g=ctx.createLinearGradient(0,0,0,cv.height);g.addColorStop(0,mix(SKY0[0],SKY1[0],nightF));g.addColorStop(1,mix(SKY0[1],SKY1[1],nightF));ctx.fillStyle=g;ctx.fillRect(0,0,cv.width,cv.height)}
function grass(x,y){var v=((x*7+y*13)%5)/5*0.06;return mix(mix('#1d4a2a','#0d2417',nightF),'#ffffff',v*0.25)}
function poly(p,f,s){ctx.beginPath();ctx.moveTo(p[0][0],p[0][1]);for(var i=1;i<p.length;i++)ctx.lineTo(p[i][0],p[i][1]);ctx.closePath();if(f){ctx.fillStyle=f;ctx.fill()}if(s){ctx.strokeStyle=s;ctx.lineWidth=1;ctx.stroke()}}
function tile(x,y){var p=px(x,y);poly([p,px(x+1,y),px(x+1,y+1),px(x,y+1)],grass(x,y),'rgba(0,0,0,.22)')}
function path(x,y){var p=px(x,y);poly([p,px(x+1,y),px(x+1,y+1),px(x,y+1)],mix('#6b543a','#2a2419',nightF),'rgba(0,0,0,.25)')}
// deterministic decor
var R=7;function rnd(){R=(R*9301+49297)%233280;return R/233280}
var trees=[],flowers=[];
(function(){var banned=[[0,0,7,15],[8,2,14,5],[8,7,14,10],[8,12,16,15],[13,4,16,7]];
for(var i=0;i<14;i++){var x=Math.floor(rnd()*17),y=Math.floor(rnd()*17),bad=false;
for(var b=0;b<banned.length;b++){if(x>=banned[b][0]&&x<banned[b][2]&&y>=banned[b][1]&&y<banned[b][3]){bad=true;break}}
if(!bad){if(rnd()<0.5)trees.push([x+rnd()*0.7,y+rnd()*0.7,0.7+rnd()*0.6]);else flowers.push([x+rnd(),y+rnd(),['#fb7185','#fcd34d','#c084fc'][Math.floor(rnd()*3)]])}}})();
function pine(x,y,s){var p=px(x,y);
ctx.fillStyle='rgba(0,0,0,.3)';ctx.beginPath();ctx.ellipse(p[0],p[1],10*s,4*s,0,0,7);ctx.fill();
ctx.fillStyle=mix('#5b3a24','#241a10',nightF);ctx.fillRect(p[0]-2*s,p[1]-14*s,4*s,14*s);
var g=mix('#2d6a3f','#0c2317',nightF);
poly([[p[0],p[1]-52*s],[p[0]-13*s,p[1]-22*s],[p[0]+13*s,p[1]-22*s]],g);
poly([[p[0],p[1]-64*s],[p[0]-10*s,p[1]-40*s],[p[0]+10*s,p[1]-40*s]],mix('#36854d','#0e2a1a',nightF));}
function flower(x,y,c){var p=px(x,y);ctx.fillStyle=mix('#2d6a3f','#0c2317',nightF);ctx.fillRect(p[0]-1,p[1]-7,2,7);
ctx.fillStyle=c;for(var i=0;i<5;i++){var a=i/5*Math.PI*2;ctx.beginPath();ctx.arc(p[0]+Math.cos(a)*3,p[1]-8+Math.sin(a)*3,2.2,0,7);ctx.fill()}
ctx.fillStyle='#fef3c7';ctx.beginPath();ctx.arc(p[0],p[1]-8,2,0,7);ctx.fill()}
function hut(x,y,color,name,win){var p=px(x,y),q=px(x+1,y),r=px(x+1,y+1);
// soft shadow
ctx.fillStyle='rgba(0,0,0,.3)';ctx.beginPath();ctx.ellipse((p[0]+r[0])/2,(p[1]+r[1])/2+4,26,10,0,0,7);ctx.fill();
// walls
poly([p,q,[q[0],q[1]-30],[p[0],p[1]-30]],shade(color,.5),'rgba(0,0,0,.35)');
poly([q,r,[r[0],r[1]-30],[q[0],q[1]-30]],shade(color,.36),'rgba(0,0,0,.35)');
// timber frame
ctx.strokeStyle='rgba(0,0,0,.4)';ctx.beginPath();ctx.moveTo(q[0],q[1]);ctx.lineTo(q[0],q[1]-30);ctx.stroke();
// roof
poly([[p[0],p[1]-30],[q[0],q[1]-30],[r[0],r[1]-50]],shade(color,.95));
poly([[q[0],q[1]-30],[r[0],r[1]-30],[r[0],r[1]-50]],shade(color,.72));
// door + glowing window
var d=[(p[0]+q[0])/2,(p[1]+q[1])/2];ctx.fillStyle=mix('#3b2a1a','#0f0a06',nightF);ctx.fillRect(d[0]-5,d[1]-22,10,22);
ctx.fillStyle=win?mix('#fde68a','#f59e0b',nightF*0.7):mix('#1e293b','#0b1220',nightF);ctx.fillRect(d[0]+9,d[1]-20,8,8);
// chimney + smoke anchor
var ch=[r[0]-8,r[1]-52];ctx.fillStyle=mix('#64748b','#1e293b',nightF);ctx.fillRect(ch[0]-3,ch[1]-8,6,12);
ctx.fillStyle='#fff';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText(name,(p[0]+q[0])/2,p[1]-56)}
function fountain(cx,cy){var c=px(cx,cy);
ctx.fillStyle='rgba(0,0,0,.3)';ctx.beginPath();ctx.ellipse(c[0],c[1]+4,46,20,0,0,7);ctx.fill();
ctx.fillStyle=mix('#94a3b8','#334155',nightF);ctx.beginPath();ctx.ellipse(c[0],c[1],44,20,0,0,7);ctx.fill();
ctx.fillStyle=mix('#38bdf8','#0c4a6e',nightF);ctx.beginPath();ctx.ellipse(c[0],c[1]-2,36,16,0,0,7);ctx.fill();
ctx.fillStyle=mix('#e0f2fe','#155e75',nightF);ctx.beginPath();ctx.ellipse(c[0],c[1]-4,22,9,0,0,7);ctx.fill();
ctx.fillStyle=mix('#7dd3fc','#164e63',nightF);ctx.fillRect(c[0]-3,c[1]-26,6,24);
for(var i=0;i<7;i++){var a=T*2+i/7*Math.PI*2;ctx.fillStyle='rgba(186,230,253,'+(0.5+0.3*Math.sin(T*3+i))+')';
ctx.beginPath();ctx.arc(c[0]+Math.cos(a)*16,c[1]-14+Math.sin(a)*5,2.2,0,7);ctx.fill()}
ctx.fillStyle='#fff';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText('SQUARE',c[0],c[1]+34)}
function stall(x,y,c1){var p=px(x,y),q=px(x+1,y),r=px(x+1,y+1);
ctx.fillStyle='rgba(0,0,0,.3)';ctx.beginPath();ctx.ellipse((p[0]+r[0])/2,(p[1]+r[1])/2+3,24,9,0,0,7);ctx.fill();
poly([p,q,[q[0],q[1]-16],[p[0],p[1]-16]],mix('#78350f','#1c1008',nightF));
for(var i=0;i<5;i++){var ax=p[0]+(q[0]-p[0])*(i/5),bx=p[0]+(q[0]-p[0])*((i+1)/5);
poly([[ax,p[1]-16],[bx,p[1]-16],[bx-3,p[1]-28],[ax-3,p[1]-28]],i%2?c1:'#fef3c7')}
ctx.fillStyle=mix('#78350f','#1c1008',nightF);ctx.fillRect(p[0]-2,p[1]-32,3,18);ctx.fillRect(q[0]-1,q[1]-32,3,18)}
function arena(cx,cy){var c=px(cx,cy);
ctx.fillStyle='rgba(0,0,0,.3)';ctx.beginPath();ctx.ellipse(c[0],c[1]+4,52,22,0,0,7);ctx.fill();
ctx.fillStyle=mix('#7c5a3a','#241a0e',nightF);ctx.beginPath();ctx.ellipse(c[0],c[1],46,20,0,0,7);ctx.fill();
ctx.fillStyle=mix('#a37c4f','#33220f',nightF);ctx.beginPath();ctx.ellipse(c[0],c[1],34,14,0,0,7);ctx.fill();
ctx.strokeStyle='#fb7185';ctx.lineWidth=3;ctx.setLineDash([8,5]);ctx.beginPath();ctx.ellipse(c[0],c[1],46,20,0,0,7);ctx.stroke();ctx.setLineDash([]);
ctx.fillStyle='#fff';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText('ARENA',c[0],c[1]+36)}
function torch(x,y){var p=px(x,y);ctx.fillStyle=mix('#57534e','#1c1917',nightF);ctx.fillRect(p[0]-1.5,p[1]-16,3,16);
var f=3+Math.sin(T*9+x)*1.2;var g=ctx.createRadialGradient(p[0],p[1]-20,1,p[0],p[1]-20,9);
g.addColorStop(0,'#fef08a');g.addColorStop(0.5,'rgba(251,146,60,'+(0.55+0.45*nightF)+')');g.addColorStop(1,'rgba(251,146,60,0)');
ctx.fillStyle=g;ctx.beginPath();ctx.arc(p[0],p[1]-20,9,0,7);ctx.fill()}
// ---- particles ----
var smoke=[],flies=[],clouds=[];
for(var i=0;i<4;i++)clouds.push({x:Math.random()*780,y:40+Math.random()*120,s:0.6+Math.random()*0.9,v:4+Math.random()*5});
for(var i=0;i<26;i++)flies.push({x:Math.random()*17,y:Math.random()*17,ph:Math.random()*6});
var HUTC=[[1,1],[1,4],[1,7],[1,10],[1,13],[5,2],[5,5],[5,8],[5,11],[5,14]];
var winState={};
function step(dt){
T+=dt;
clouds.forEach(function(c){c.x+=c.v*dt;if(c.x>860)c.x=-80});
if(Math.random()<dt*5&&smoke.length<40){var h=HUTC[Math.floor(Math.random()*HUTC.length)];smoke.push({x:h[0]+0.72,y:h[1]+0.3,r:2,a:0.5})}
smoke.forEach(function(s){s.y-=dt*0.5;s.x+=Math.sin(T+s.r)*dt*0.1;s.r+=dt*2;s.a-=dt*0.25});
smoke=smoke.filter(function(s){return s.a>0});
}
// ---- walkers ----
var R2=0.5;function rnd(){R2=(R2*9301+49297)%233280;return R2/233280}
var PL={SQUARE:[12.5,3.5],MARKET:[12.5,8.5],ARENA:[12.5,13.2]};
var walkers=DATA.souls.map(function(s,i){
var hc=HUTC[i%HUTC.length],hx=hc[0],hy=hc[1];
var hp=PL[s.hang]||[hx,hy];
return {s:s,hx:hx,hy:hy,tx:hp[0],ty:hp[1],x:hx,y:hy,sp:0.9+rnd()*0.7,ph:rnd()*6,fx:1};
});
function wstep(dt){walkers.forEach(function(w){if(paused)return;
var dx=w.tx-w.x,dy=w.ty-w.y,d=Math.hypot(dx,dy);
if(d<0.2){var hp=PL[w.s.hang]||[w.hx,w.hy],home=rnd()<0.4;
w.tx=home?w.hx+rnd()*0.8:(hp[0]+rnd()*1.8-0.6);w.ty=home?w.hy+rnd()*0.8:(hp[1]+rnd()*1.8-0.6);return}
if(Math.abs(dx)>0.02)w.fx=dx>0?1:-1;
w.x+=dx/d*w.sp*dt;w.y+=dy/d*w.sp*dt;w.ph+=dt*9})}
function bubble(x,y,text){ctx.font='9px sans-serif';var words=text.split(' '),lines=[''];
words.forEach(function(w){if((lines[lines.length-1]+' '+w).length>26){lines.push('')}lines[lines.length-1]=(lines[lines.length-1]+' '+w).trim()});
lines=lines.slice(0,2);var bw=0;lines.forEach(function(l){bw=Math.max(bw,ctx.measureText(l).width)});
bw+=14;var bh=lines.length*12+12,bx=x-bw/2,by=y-bh;
ctx.fillStyle='rgba(255,255,255,.96)';ctx.strokeStyle='#94a3b8';ctx.lineWidth=1;
ctx.beginPath();ctx.moveTo(bx+6,by);ctx.lineTo(bx+bw-6,by);ctx.quadraticCurveTo(bx+bw,by,bx+bw,by+6);
ctx.lineTo(bx+bw,by+bh-6);ctx.quadraticCurveTo(bx+bw,by+bh,bx+bw-6,by+bh);ctx.lineTo(x+5,by+bh);
ctx.lineTo(x,by+bh+7);ctx.lineTo(x-3,by+bh);ctx.lineTo(bx+6,by+bh);ctx.quadraticCurveTo(bx,by+bh,bx,by+bh-6);
ctx.lineTo(bx,by+6);ctx.quadraticCurveTo(bx,by,bx+6,by);ctx.closePath();ctx.fill();ctx.stroke();
ctx.fillStyle='#0f172a';ctx.textAlign='center';lines.forEach(function(l,i){ctx.fillText(l,x,by+14+i*12)})}
function char(w){var p=px(w.x,w.y),bob=Math.abs(Math.sin(w.ph))*2.5;
var active=w.s.msgs>0;
ctx.fillStyle='rgba(0,0,0,.35)';ctx.beginPath();ctx.ellipse(p[0],p[1],9,3.6,0,0,7);ctx.fill();
if(w.s.pay>0){ctx.strokeStyle='#fcd34d';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p[0],p[1]-17+bob*0.3,15,0,7);ctx.stroke()}
ctx.fillStyle=shade(w.s.color,.75);ctx.fillRect(p[0]-5.5,p[1]-24-bob,11,13);
ctx.fillStyle=w.s.color;ctx.fillRect(p[0]-5.5,p[1]-24-bob,11,4);
ctx.beginPath();ctx.arc(p[0],p[1]-29-bob,6.5,0,7);ctx.fillStyle='#fde4c8';ctx.fill();
ctx.fillStyle='#1e293b';ctx.arc(p[0]-2*w.fx,p[1]-30-bob,1.3,0,7);ctx.fill();ctx.beginPath();ctx.arc(p[0]+2.5*w.fx,p[1]-30-bob,1.3,0,7);ctx.fill();
ctx.fillStyle=active?'#22c55e':'#64748b';ctx.beginPath();ctx.arc(p[0]+9,p[1]-33-bob,2.6,0,7);ctx.fill();
ctx.font='9px sans-serif';var label=w.s.short,tw=ctx.measureText(label).width;
ctx.fillStyle='rgba(2,6,23,.8)';ctx.fillRect(p[0]-tw/2-4,p[1]-52-bob,tw+8,14);
ctx.fillStyle='#fff';ctx.textAlign='center';ctx.fillText(label,p[0],p[1]-41-bob);
if(w.s.say)bubble(p[0],p[1]-58-bob,w.s.say);
w.sx=p[0];w.sy=p[1]-22}
function draw(){
sky();
// stars
if(nightF>0.05){ctx.fillStyle='rgba(255,255,255,'+(nightF*0.8)+')';for(var i=0;i<60;i++){var sx=(i*97)%780,sy=(i*53)%200;ctx.fillRect(sx,sy,1.5,1.5)}}
// clouds
clouds.forEach(function(c){ctx.fillStyle='rgba(148,163,184,'+(0.25*(1-nightF*0.6))+')';ctx.beginPath();ctx.ellipse(c.x,c.y,46*c.s,13*c.s,0,0,7);ctx.ellipse(c.x-28*c.s,c.y+4,26*c.s,9*c.s,0,0,7);ctx.ellipse(c.x+28*c.s,c.y+4,28*c.s,10*c.s,0,0,7);ctx.fill()});
for(var x=0;x<17;x++)for(var y=0;y<17;y++)tile(x,y);
// paths
for(var y=1;y<=14;y++){path(3,y)}for(var y=1;y<=15;y++){path(9,y)}for(var x=9;x<=12;x++){path(x,3);path(x,8);path(x,13)}
[[9,3],[9,8],[9,13]].forEach(function(p){var q=px(p[0],p[1]);ctx.fillStyle=mix('#6b543a','#2a2419',nightF);ctx.beginPath();ctx.ellipse(q[0],q[1],16,8,0,0,7);ctx.fill()});
fountain(12.5,3.5);
stall(11.3,8.2,'#ef4444');stall(12.1,8.5,'#f59e0b');stall(12.9,8.2,'#22c55e');
var m=px(12.4,9.4);ctx.fillStyle='#fff';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText('MARKET',m[0],m[1]+26);
arena(12.5,13.2);
torch(11.2,12.2);torch(13.8,12.2);torch(11.2,14.4);torch(13.8,14.4);
// pond
(function(){var p=px(14.6,5.6);ctx.fillStyle=mix('#38bdf8','#0c4a6e',nightF);ctx.beginPath();ctx.ellipse(p[0],p[1],34,15,0,0,7);ctx.fill();ctx.fillStyle=mix('#bae6fd','#155e75',nightF);ctx.beginPath();ctx.ellipse(p[0],p[1]-2,22,9,0,0,7);ctx.fill()})();
trees.forEach(function(t){pine(t[0],t[1],t[2])});
flowers.forEach(function(f){flower(f[0],f[1],f[2])});
// houses (roof = owner's color)
DATA.souls.forEach(function(s,i){var c=HUTC[i%HUTC.length];hut(c[0],c[1],s.color,s.short,winState)});
// smoke
smoke.forEach(function(s){var p=px(s.x,s.y);ctx.fillStyle='rgba(203,213,225,'+Math.max(0,s.a)+')';ctx.beginPath();ctx.arc(p[0],p[1],s.r,0,7);ctx.fill()});
// fireflies
if(nightF>0.05)flies.forEach(function(f,i){var p=px((f.x+T*0.3+i)%17,(f.y+Math.sin(T+i)*0.5+17)%17);ctx.fillStyle='rgba(253,224,71,'+(nightF*(0.4+0.4*Math.sin(T*2+f.ph)))+')';ctx.beginPath();ctx.arc(p[0],p[1]-14,2,0,7);ctx.fill()});
// walkers sorted
walkers.slice().sort(function(a,b){return (a.x+a.y)-(b.x+b.y)}).forEach(char);
}
var last=0;
function loop(t){var dt=Math.min(0.05,(t-last)/1000||0);last=t;
nightF+=((nightTarget?1:0)-nightF)*Math.min(1,dt*1.5);
if(!paused){step(dt);wstep(dt)}draw();requestAnimationFrame(loop)}
requestAnimationFrame(loop);
cv.onclick=function(e){var r=cv.getBoundingClientRect(),mx=(e.clientX-r.left)*(cv.width/r.width),my=(e.clientY-r.top)*(cv.height/r.height),best=null,bd=1e9;
walkers.forEach(function(w){var d=Math.hypot(w.sx-mx,w.sy-my);if(d<bd){bd=d;best=w}});
var panel=document.getElementById('who');
if(best&&bd<30){var s=best.s;panel.innerHTML='<h3>'+s.short+'</h3><div id="bar" style="background:'+s.color+'"></div><p><code>'+s.rank+'</code> · <span class="mut">'+s.id+'</span></p><p><b>Goal:</b> '+s.goal+'</p><p><b>Now:</b> '+s.task+'</p><p><b>Wants:</b> '+s.desire+'</p><p><b>Hangout:</b> '+s.hang+'</p>'+(s.say?'<p><b>Saying:</b> '+s.say+'</p>':'')+'<p class="mut">earned $'+s.pay+' · '+s.msgs+' messages</p>'}
else{panel.innerHTML='<h3>Welcome home</h3><p class="mut">Click anyone strolling the land. Gold ring = earned money. Green spark = active this week.</p>'}};
</script></body></html>"""

if __name__ == "__main__":
    main()
