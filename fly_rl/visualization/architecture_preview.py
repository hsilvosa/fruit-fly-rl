"""Portable Canvas2D scene inspection; no GPU, brain, optimizer or flight controller."""
import json
from pathlib import Path

ROUTE_COLORS = ('#1d4ed8', '#b45309', '#047857', '#9d174d', '#6d28d9')
TRANSLUCENT = {'wall': .22, 'building': .32, 'glass': .22, 'water': .6}


def _hex(rgb):
    return '#' + ''.join(f'{round(c * 255):02x}' for c in rgb)


def write_preview(scenes, path, reports=None):
    from fly_rl.simulation.architectural_scenes import MATERIALS, SCENE_VERSION, validate
    reports = reports or [validate(scene) for scene in scenes]
    data = [{**scene.to_dict(), 'report': report} for scene, report in zip(scenes, reports)]
    payload = json.dumps(data, separators=(',', ':')).replace('<', '\\u003c')
    colors = json.dumps({name: _hex(rgb) for name, rgb in MATERIALS.items()})
    template = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Architectural scenes | fly-rl</title>
<style>
:root{--bg:#eef0eb;--panel:#fff;--ink:#1f2d31;--muted:#5a6b68;--line:#cfd6cf;--accent:#1d4ed8}
@media (prefers-color-scheme:dark){:root{--bg:#161b1d;--panel:#20272a;--ink:#e3e8e6;--muted:#9aa8a5;--line:#34403f;--accent:#7aa2ff}}
*{box-sizing:border-box}html,body{margin:0;height:100%}body{background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif;display:grid;grid-template-columns:320px 1fr;height:100vh}
aside{background:var(--panel);border-right:1px solid var(--line);padding:18px 18px 24px;overflow:auto}
h1{font-size:19px;margin:2px 0 4px}.tag{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
label.block{display:block;margin:14px 0 4px;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
select,button{font:inherit;width:100%;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:6px}
.row{display:flex;gap:8px;margin-top:10px}.row button{flex:1}.check{display:flex;gap:8px;align-items:center;margin-top:8px}
input[type=range]{width:100%}p{margin:8px 0}.muted{color:var(--muted)}
.stats{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;margin-top:10px;font-variant-numeric:tabular-nums}.stats dt{color:var(--muted)}.stats dd{margin:0}
.chips span{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:1px 8px;margin:2px 4px 2px 0;font-size:12px}
.legend{display:grid;grid-template-columns:1fr 1fr;gap:3px 10px;margin-top:6px;font-size:12px}.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:6px;vertical-align:-1px;border:1px solid #0003}
main{position:relative;min-width:0}canvas{display:block;width:100%;height:100%;touch-action:none;cursor:grab}
.hint{position:absolute;left:14px;bottom:12px;font-size:12px;color:var(--muted);background:color-mix(in srgb,var(--panel) 85%,transparent);padding:5px 9px;border-radius:6px}
@media (max-width:760px){body{grid-template-columns:1fr;grid-template-rows:auto 70vh;height:auto}aside{border-right:0;border-bottom:1px solid var(--line)}}
</style>
<aside>
<div class="tag">Original synthetic architecture / __VERSION__</div><h1>Buildings and streets</h1>
<p class="muted">Geometry inspection only. These designs are not scans of real places. No fly, brain, training or navigation score runs here.</p>
<label class="block" for="scene">Scene</label><select id="scene"></select>
<p id="sceneText"></p>
<label class="block" for="situation">Situation</label><select id="situation"></select>
<p id="situationText"></p><div class="chips" id="tags"></div>
<dl class="stats" id="stats"></dl>
<label class="block" for="cut">Cutaway height <span id="cutValue"></span></label><input id="cut" type="range" min="0" max="1" step="0.05">
<label class="check"><input id="xray" type="checkbox" checked> See-through walls and buildings</label>
<label class="check"><input id="route" type="checkbox" checked> Show feasibility reference</label>
<label class="check"><input id="allRoutes" type="checkbox" checked> Show other situations faintly</label>
<div class="row"><button id="reset">Reset view</button><button id="top">Top view</button></div>
<label class="block">Materials</label><div class="legend" id="legend"></div>
</aside>
<main><canvas id="canvas" aria-label="Interactive 3D architectural scene"></canvas>
<div class="hint">Drag to orbit · Shift/right-drag to pan · wheel to zoom. Dashed line: CPU-checked geometric reference, not a flown route. Meters.</div></main>
<script>
const scenes=__SCENES__,colors=__COLORS__,translucent=__TRANSLUCENT__,routeColors=__ROUTES__;
const $=s=>document.querySelector(s),canvas=$('#canvas'),ctx=canvas.getContext('2d');
let scene=scenes[0],yaw=-.7,pitch=.62,zoom=1,panX=0,panY=0,drag=null,cut=1;
// Faces as corner indices (corner = 4*xi + 2*yi + zi) with outward normals.
const faces=[[[0,2,6,4],[0,0,-1]],[[1,5,7,3],[0,0,1]],[[0,4,5,1],[0,-1,0]],[[2,3,7,6],[0,1,0]],[[0,1,3,2],[-1,0,0]],[[4,6,7,5],[1,0,0]]];
const light=(()=>{const l=[.45,-.55,.7],n=Math.hypot(...l);return l.map(v=>v/n);})();
function shade(hex,k){const n=parseInt(hex.slice(1),16);return `rgb(${[16,8,0].map(s=>Math.min(255,Math.round(((n>>s)&255)*k))).join(',')})`;}
function scale(){const s=scene.size;return Math.min(canvas.clientWidth,canvas.clientHeight*1.25)/(Math.hypot(s[0],s[1])+s[2]*.4)*zoom;}
function point(p,k){const x=p[0]-scene.size[0]/2,y=p[1]-scene.size[1]/2,z=p[2]-scene.size[2]/3;
 const u=x*Math.cos(yaw)-y*Math.sin(yaw),v=x*Math.sin(yaw)+y*Math.cos(yaw);
 return [canvas.clientWidth/2+panX+u*k,canvas.clientHeight/2+panY+(v*Math.sin(pitch)-z*Math.cos(pitch))*k,v*Math.cos(pitch)+z*Math.sin(pitch)];}
function path(points){ctx.beginPath();points.forEach((q,i)=>i?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));}
function draw(){const ratio=devicePixelRatio||1;canvas.width=Math.round(canvas.clientWidth*ratio);canvas.height=Math.round(canvas.clientHeight*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);
 const W=canvas.clientWidth,H=canvas.clientHeight,k=scale(),dark=matchMedia('(prefers-color-scheme: dark)').matches;ctx.clearRect(0,0,W,H);
 const view=[Math.sin(yaw)*Math.cos(pitch),Math.cos(yaw)*Math.cos(pitch),Math.sin(pitch)],xray=$('#xray').checked,cutZ=cut*scene.size[2];
 const [sx,sy]=scene.size;path([[0,0,0],[sx,0,0],[sx,sy,0],[0,sy,0]].map(p=>point(p,k)));ctx.closePath();ctx.fillStyle=dark?'#2a3234':colors.ground;ctx.fill();
 const step=Math.max(sx,sy)>30?5:1;ctx.strokeStyle=dark?'#ffffff14':'#00000012';ctx.lineWidth=1;
 for(let x=0;x<=sx+1e-6;x+=step){path([point([x,0,0],k),point([x,sy,0],k)]);ctx.stroke();}
 for(let y=0;y<=sy+1e-6;y+=step){path([point([0,y,0],k),point([sx,y,0],k)]);ctx.stroke();}
 const polys=[];
 for(const b of scene.solids){if(b.low[2]>=cutZ-1e-6)continue;const hi=[b.high[0],b.high[1],Math.min(b.high[2],cutZ)];
  const corners=[];for(const x of [b.low[0],hi[0]])for(const y of [b.low[1],hi[1]])for(const z of [b.low[2],hi[2]])corners.push(point([x,y,z],k));
  const alpha=xray&&translucent[b.material]!==undefined?translucent[b.material]:(b.material==='glass'?.3:.95);
  for(const [f,n] of faces){if(n[0]*view[0]+n[1]*view[1]+n[2]*view[2]<=0)continue;const ps=f.map(i=>corners[i]);
   const lit=.62+.45*Math.max(0,n[0]*light[0]+n[1]*light[1]+n[2]*light[2]);
   polys.push({ps,fill:shade(colors[b.material],lit),alpha,depth:(ps[0][2]+ps[1][2]+ps[2][2]+ps[3][2])/4,edge:alpha<.5});}}
 polys.sort((a,b)=>a.depth-b.depth);
 for(const p of polys){path(p.ps);ctx.closePath();ctx.globalAlpha=p.alpha;ctx.fillStyle=p.fill;ctx.fill();ctx.globalAlpha=Math.min(1,p.alpha+.25);ctx.strokeStyle=dark?'#0b0f10':'#2b3a3d';ctx.lineWidth=p.edge?.5:.35;ctx.stroke();}
 ctx.globalAlpha=1;const chosen=Number($('#situation').value)||0;
 if($('#route').checked){scene.situations.forEach((s,i)=>{if(i!==chosen&&!$('#allRoutes').checked)return;const c=routeColors[i%routeColors.length],q=s.route.map(p=>point(p,k));
  ctx.globalAlpha=i===chosen?1:.28;ctx.setLineDash(i===chosen?[7,5]:[3,4]);ctx.lineWidth=i===chosen?2.6:1.6;ctx.strokeStyle=c;path(q);ctx.stroke();ctx.setLineDash([]);
  if(i===chosen){for(const p of [s.route[0],s.route.at(-1)]){ctx.globalAlpha=.6;ctx.lineWidth=1;path([point(p,k),point([p[0],p[1],0],k)]);ctx.stroke();}ctx.globalAlpha=1;
   for(const [p,label,fill] of [[s.route[0],'Start','#2563eb'],[s.route.at(-1),'Goal','#d97706']]){const m=point(p,k);ctx.fillStyle=fill;ctx.beginPath();ctx.arc(m[0],m[1],6.5,0,7);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='600 13px system-ui';ctx.lineWidth=3;ctx.strokeStyle=dark?'#000':'#fff';ctx.strokeText(label,m[0]+10,m[1]-8);ctx.fillStyle=dark?'#fff':'#1f2d31';ctx.fillText(label,m[0]+10,m[1]-8);}}});}
 ctx.globalAlpha=1;}
function describe(){const i=Number($('#situation').value)||0,s=scene.situations[i],r=scene.report.situations[i];
 $('#situationText').textContent=s.description;$('#tags').replaceChildren(...s.tags.map(t=>{const e=document.createElement('span');e.textContent=t;return e;}));
 const rows=[['Scene',scene.size.join(' × ')+' m'],['Kind',scene.kind],['Collision boxes',scene.solids.length],['Route length',r.route_length_m.toFixed(1)+' m'],['Altitude range',r.climb_m.toFixed(1)+' m'],['Tightest clearance',r.min_sampled_clearance_m.toFixed(2)+' m (body centre, sampled)']];
 $('#stats').replaceChildren(...rows.flatMap(([a,b])=>{const t=document.createElement('dt'),d=document.createElement('dd');t.textContent=a;d.textContent=b;return [t,d];}));draw();}
function legend(){const used=[...new Set(scene.solids.map(b=>b.material))].sort();$('#legend').replaceChildren(...used.map(m=>{const e=document.createElement('div'),i=document.createElement('i');i.style.background=colors[m];e.append(i,m);return e;}));}
function setCut(){cut=Number($('#cut').value);$('#cutValue').textContent=cut>=1?'(all)':`(${(cut*scene.size[2]).toFixed(1)} m)`;draw();}
function reset(){yaw=-.7;pitch=.62;zoom=1;panX=panY=0;draw();}
function choose(){scene=scenes[Number($('#scene').value)];$('#sceneText').textContent=scene.description;$('#situation').replaceChildren();scene.situations.forEach((s,i)=>$('#situation').add(new Option(s.name,i)));
 $('#cut').value=1;legend();setCut();reset();describe();}
scenes.forEach((s,i)=>$('#scene').add(new Option(`${s.name} (${s.kind})`,i)));
$('#scene').onchange=choose;$('#situation').onchange=describe;$('#cut').oninput=setCut;
for(const id of ['#route','#xray','#allRoutes'])$(id).onchange=draw;$('#reset').onclick=reset;$('#top').onclick=()=>{pitch=Math.PI/2;yaw=0;draw();};
canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,pan:e.shiftKey||e.button===2};canvas.style.cursor='grabbing';};
canvas.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(drag.pan){panX+=dx;panY+=dy;}else{yaw+=dx*.008;pitch=Math.max(.05,Math.min(Math.PI/2,pitch+dy*.006));}drag.x=e.clientX;drag.y=e.clientY;draw();};
canvas.onpointerup=canvas.onpointercancel=()=>{drag=null;canvas.style.cursor='grab';};
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.3,Math.min(8,zoom*Math.exp(-e.deltaY*.0012)));draw();},{passive:false});
addEventListener('resize',draw);matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);choose();
</script></html>'''
    text = (template.replace('__SCENES__', payload).replace('__COLORS__', colors)
            .replace('__TRANSLUCENT__', json.dumps(TRANSLUCENT)).replace('__ROUTES__', json.dumps(ROUTE_COLORS))
            .replace('__VERSION__', SCENE_VERSION))
    Path(path).write_text(text, encoding='utf-8', newline='\n')


def _figure_grid(count):
    columns = 3 if count > 4 else count
    return (count + columns - 1) // columns, columns


def write_gallery(scenes, path):
    """Oblique 3D views of every scene with all reference routes."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    from fly_rl.simulation.architectural_scenes import MATERIALS

    rows, columns = _figure_grid(len(scenes))
    fig = plt.figure(figsize=(6.4 * columns, 5.6 * rows), facecolor='#f4f5f1')
    light = np.array([.45, -.55, .7]) / np.linalg.norm([.45, -.55, .7])
    normals = np.array([[0, 0, -1], [0, 0, 1], [0, -1, 0], [0, 1, 0], [-1, 0, 0], [1, 0, 0]])
    face_index = ((0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6), (0, 1, 3, 2), (4, 6, 7, 5))
    alpha = {'wall': .2, 'building': .5, 'glass': .2, 'water': .6}
    for index, scene in enumerate(scenes):
        ax = fig.add_subplot(rows, columns, index + 1, projection='3d')
        ax.set_facecolor('#f4f5f1')
        polys, fills, edges = [], [], []
        for b in scene.solids:
            corners = np.array([[x, y, z] for x in (b.low[0], b.high[0])
                                for y in (b.low[1], b.high[1]) for z in (b.low[2], b.high[2])])
            base = np.array(MATERIALS[b.material])
            a = alpha.get(b.material, .92)
            for f, n in zip(face_index, normals):
                lit = .62 + .45 * max(0., float(n @ light))
                polys.append(corners[list(f)])
                fills.append((*np.clip(base * lit, 0, 1), a))
                edges.append((.15, .2, .22, min(1., a + .15)))
        ax.add_collection3d(Poly3DCollection(polys, facecolors=fills, edgecolors=edges, linewidths=.18))
        for i, situation in enumerate(scene.situations):
            route = np.asarray(situation.route)
            color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            ax.plot(*route.T, '--', color=color, linewidth=1.6, zorder=10)
            ax.scatter(*route[0], color=color, s=18, zorder=11)
            ax.scatter(*route[-1], color=color, s=60, marker='*', zorder=11)
        ax.set(xlim=(0, scene.size[0]), ylim=(0, scene.size[1]), zlim=(0, scene.size[2]))
        ax.set_box_aspect(np.array(scene.size, dtype=float))
        ax.view_init(elev=38, azim=-58)
        ax.set_axis_off()
        ax.set_title(f'{scene.name}  ·  {scene.size[0]:g}×{scene.size[1]:g}×{scene.size[2]:g} m  ·  '
                     f'{len(scene.solids)} boxes  ·  {len(scene.situations)} routes', fontsize=11, pad=0)
    fig.suptitle('Architectural drafts 0.2: interiors, multi-level spaces and streets', fontsize=18, y=.985)
    fig.text(.5, .012, 'Original synthetic layouts, not real-location reconstructions. Dashed lines: CPU-checked geometric '
             'references (star = goal); no flights were run.', ha='center', fontsize=10)
    fig.subplots_adjust(top=.93, bottom=.04, left=.01, right=.99, wspace=.02, hspace=.06)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def write_plans(scenes, path, cut=2.):
    """Floor plans cut at `cut` metres: solids below are filled, overhead solids are dashed outlines."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from fly_rl.simulation.architectural_scenes import MATERIALS

    rows, columns = _figure_grid(len(scenes))
    fig, axes = plt.subplots(rows, columns, figsize=(6.4 * columns, 5.9 * rows), facecolor='#ffffff', squeeze=False)
    for ax, scene in zip(axes.flat, scenes):
        sx, sy, sz = scene.size
        ax.add_patch(Rectangle((0, 0), sx, sy, facecolor=MATERIALS['ground'], edgecolor='#555', linewidth=.8))
        below = [b for b in scene.solids if b.low[2] < cut]
        overhead = [b for b in scene.solids if b.low[2] >= cut]
        for b in sorted(below, key=lambda s: s.high[2]):
            color = MATERIALS[b.material]
            fade = .55 + .45 * min(1., b.high[2] / sz)
            ax.add_patch(Rectangle(b.low[:2], b.high[0] - b.low[0], b.high[1] - b.low[1],
                                   facecolor=tuple(c * fade + (1 - fade) for c in color),
                                   edgecolor='#33414533', linewidth=.3,
                                   alpha=.55 if b.material == 'glass' else 1.))
        for b in overhead:
            ax.add_patch(Rectangle(b.low[:2], b.high[0] - b.low[0], b.high[1] - b.low[1], fill=False,
                                   edgecolor='#4b5563', linewidth=.45, linestyle=(0, (3, 2)), alpha=.6))
        for i, situation in enumerate(scene.situations):
            xs, ys = zip(*[(p[0], p[1]) for p in situation.route])
            color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            ax.plot(xs, ys, '--', color=color, linewidth=1.8, label=situation.name)
            ax.plot(xs[0], ys[0], 'o', color=color, markersize=5)
            ax.plot(xs[-1], ys[-1], '*', color=color, markersize=11)
        ax.set(xlim=(-.5, sx + .5), ylim=(-.5, sy + .5), aspect='equal')
        ax.set_title(f'{scene.name} · {sx:g}×{sy:g} m', fontsize=11)
        ax.tick_params(labelsize=7)
        ax.legend(loc='upper center', bbox_to_anchor=(.5, -.06), ncol=3, fontsize=7.5, frameon=False)
    for ax in list(axes.flat)[len(scenes):]:
        ax.set_axis_off()
    fig.suptitle(f'Architectural drafts 0.2: plans cut at {cut:g} m (dashed = overhead; darker = taller)', fontsize=16)
    fig.subplots_adjust(top=.93, bottom=.08, left=.03, right=.99, wspace=.12, hspace=.3)
    fig.savefig(path, dpi=110)
    plt.close(fig)
