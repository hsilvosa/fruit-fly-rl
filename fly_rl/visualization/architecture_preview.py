"""Portable Canvas2D scene inspection; no GPU, brain, optimizer or flight controller."""
import json
from pathlib import Path


def write_preview(scenes, path):
    payload = json.dumps([scene.to_dict() for scene in scenes]).replace('<', '\\u003c')
    template = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Architectural scene drafts | fly-rl</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef1ed;color:#203237;font:15px system-ui,sans-serif}
header{padding:20px 26px;background:#fff;border-bottom:1px solid #c9d3cb}h1{margin:0 0 6px;font-size:24px}
p{margin:6px 0;max-width:1000px;line-height:1.5}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-top:16px}
select,button{font:inherit;padding:7px 10px;border:1px solid #a8b6b2;background:#fff;border-radius:4px}
canvas{display:block;width:100%;height:calc(100vh - 230px);min-height:420px;touch-action:none}
footer{padding:12px 26px;background:#fff}#description{color:#49605a}.tag{font-size:12px;letter-spacing:.06em;text-transform:uppercase}
</style>
<header><div class="tag">Original synthetic architecture / draft 0.1</div><h1>Buildings and streets</h1>
<p>Geometry inspection only. These designs are not scans of real locations. No fly, brain, training or navigation score runs here.</p>
<div class="controls"><label>Scene <select id="scene"></select></label><label>Situation <select id="situation"></select></label>
<label><input id="route" type="checkbox" checked> Show feasibility reference</label><button id="reset">Reset view</button>
<button id="top">Top view</button></div><p id="description"></p></header>
<canvas id="canvas" aria-label="Interactive 3D architectural scene"></canvas>
<footer>Drag to orbit. Shift-drag or right-drag to pan. Wheel to zoom. Blue: start. Amber: goal. Dashed line: CPU-checked geometric reference, not a flown route. Units: meters.</footer>
<script>
const scenes=__SCENES__;
const canvas=document.querySelector('#canvas'),ctx=canvas.getContext('2d');
const sceneSelect=document.querySelector('#scene'),situationSelect=document.querySelector('#situation');
const colors={wall:'#879fa5',wood:'#a57750',furniture:'#49858e',building:'#889397',vehicle:'#bb6853',vegetation:'#598258',metal:'#495359'};
let scene=scenes[0],yaw=-.75,pitch=.70,zoom=1,panX=0,panY=0,drag=null;
const faces=[[0,4,6,2],[1,3,7,5],[0,1,5,4],[2,6,7,3],[0,2,3,1],[4,5,7,6]];
function point(p){let x=p[0]-scene.size[0]/2,y=p[1]-scene.size[1]/2,z=p[2]-scene.size[2]/4;
 const u=x*Math.cos(yaw)-y*Math.sin(yaw),v=x*Math.sin(yaw)+y*Math.cos(yaw);
 const scale=Math.min(canvas.clientWidth/(scene.size[0]+scene.size[1]),canvas.clientHeight/(scene.size[0]+scene.size[1]))*1.25*zoom;
 return [canvas.clientWidth/2+panX+u*scale,canvas.clientHeight/2+panY+(v*Math.sin(pitch)-z*Math.cos(pitch))*scale,v*Math.cos(pitch)+z*Math.sin(pitch)];}
function polygon(points,color,alpha){ctx.beginPath();points.forEach((p,i)=>{const q=point(p);i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]);});
 ctx.closePath();ctx.globalAlpha=alpha;ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#33494a';ctx.lineWidth=.6;ctx.stroke();ctx.globalAlpha=1;}
function draw(){const ratio=devicePixelRatio||1;canvas.width=Math.round(canvas.clientWidth*ratio);canvas.height=Math.round(canvas.clientHeight*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);
 ctx.clearRect(0,0,canvas.clientWidth,canvas.clientHeight);
 polygon([[0,0,0],[scene.size[0],0,0],scene.size.slice(0,2).concat(0),[0,scene.size[1],0]],'#d7dfd2',1);
 let polygons=[];for(const b of scene.solids){let corners=[];for(const x of [b.low[0],b.high[0]])for(const y of [b.low[1],b.high[1]])for(const z of [b.low[2],b.high[2]])corners.push([x,y,z]);
 for(const f of faces){const ps=f.map(i=>corners[i]);polygons.push({ps,color:colors[b.material],depth:ps.reduce((sum,p)=>sum+point(p)[2],0)/4,alpha:b.material==='wall'?.20:.75});}}
 polygons.sort((a,b)=>a.depth-b.depth).forEach(p=>polygon(p.ps,p.color,p.alpha));
 const route=scene.situations[Number(situationSelect.value)||0].route;
 if(document.querySelector('#route').checked){ctx.beginPath();route.forEach((p,i)=>{const q=point(p);i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]);});ctx.strokeStyle='#203f52';ctx.lineWidth=2;ctx.setLineDash([6,5]);ctx.stroke();ctx.setLineDash([]);}
 for(const [p,label,color] of [[route[0],'Start','#2463eb'],[route.at(-1),'Goal','#d97706']]){const q=point(p);ctx.fillStyle=color;ctx.beginPath();ctx.arc(q[0],q[1],6,0,Math.PI*2);ctx.fill();ctx.fillStyle='#203237';ctx.font='bold 13px system-ui';ctx.fillText(label,q[0]+10,q[1]-8);}
 ctx.fillStyle='#203237';ctx.font='14px system-ui';ctx.fillText(`${scene.name} | ${scene.size.join(' × ')} m | ${scene.solids.length} collision boxes`,20,28);}
function describe(){const s=scene.situations[Number(situationSelect.value)||0];document.querySelector('#description').textContent=scene.description+' '+s.description;draw();}
function reset(){yaw=-.75;pitch=.70;zoom=1;panX=panY=0;draw();}
function choose(){scene=scenes[Number(sceneSelect.value)];situationSelect.replaceChildren();scene.situations.forEach((s,i)=>situationSelect.add(new Option(s.name,i)));reset();describe();}
scenes.forEach((s,i)=>sceneSelect.add(new Option(s.name,i)));sceneSelect.onchange=choose;situationSelect.onchange=describe;
document.querySelector('#route').onchange=draw;document.querySelector('#reset').onclick=reset;
document.querySelector('#top').onclick=()=>{pitch=Math.PI/2;yaw=0;draw();};
canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,pan:e.shiftKey||e.button===2};};
canvas.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(drag.pan){panX+=dx;panY+=dy;}else{yaw+=dx*.008;pitch=Math.max(.08,Math.min(Math.PI/2,pitch+dy*.006));}drag.x=e.clientX;drag.y=e.clientY;draw();};
canvas.onpointerup=canvas.onpointercancel=()=>drag=null;
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.3,Math.min(5,zoom*Math.exp(-e.deltaY*.001)));draw();},{passive:false});
window.addEventListener('resize',draw);choose();
</script></html>'''
    Path(path).write_text(template.replace('__SCENES__', payload), encoding='utf-8', newline='\n')


def write_gallery(scenes, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(17, 9), facecolor='#f4f6f1')
    colors = {'wall': '#879fa5', 'wood': '#a57750', 'furniture': '#49858e', 'building': '#889397',
              'vehicle': '#bb6853', 'vegetation': '#598258', 'metal': '#495359'}
    for index, scene in enumerate(scenes):
        for view in range(2):
            ax = fig.add_subplot(2, len(scenes), view * len(scenes) + index + 1, projection='3d')
            for b in scene.solids:
                corners = np.array([[x, y, z] for x in (b.low[0], b.high[0])
                                    for y in (b.low[1], b.high[1]) for z in (b.low[2], b.high[2])])
                faces = [corners[list(f)] for f in ((0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4),
                                                   (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6))]
                ax.add_collection3d(Poly3DCollection(faces, facecolor=colors[b.material], edgecolor='#435a61',
                                                    linewidth=.25, alpha=.18 if b.material == 'wall' else .55))
            route = np.asarray(scene.situations[0].route)
            ax.plot(*route.T, '--', color='#203f52', linewidth=1.5)
            ax.scatter(*route[0], color='#2463eb', s=35)
            ax.scatter(*route[-1], color='#d97706', s=60, marker='*')
            ax.set(xlim=(0, scene.size[0]), ylim=(0, scene.size[1]), zlim=(0, scene.size[2]),
                   xlabel='X (m)', ylabel='Y (m)', zlabel='Z (m)')
            ax.set_box_aspect(np.array(scene.size, dtype=float))
            ax.view_init(elev=65 if view else 27, azim=-70 if view else -55)
            ax.set_title(f'{scene.name} | {len(scene.solids)} collision boxes', fontsize=11)
            ax.tick_params(labelsize=7)
    fig.suptitle('Architectural drafts: office, apartment and street', fontsize=18, y=.98)
    fig.text(.5, .02, 'Original synthetic layouts, not real-location reconstructions. Dashed references show geometric feasibility; no flights were run.', ha='center', fontsize=10)
    fig.subplots_adjust(top=.91, bottom=.09, left=.03, right=.98, wspace=.08, hspace=.12)
    fig.savefig(path, dpi=140)
    plt.close(fig)
