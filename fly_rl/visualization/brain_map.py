"""An independent window with real soma positions and activity-linked colors."""
from fly_rl.atomic_io import replace_file
import numpy as np
from fly_rl.connectome.anatomy import load_anatomy,display_positions

class BrainMap:
    bounds=(0.,1.,.42,.78)
    def __init__(self,app,data,offscreen=False):
        from panda3d.core import NodePath,Camera,OrthographicLens,Geom,GeomNode,GeomVertexData,GeomVertexFormat,GeomPoints,WindowProperties,TextNode
        self.app=app;self.anatomy=load_anatomy(data);self.points=display_positions(self.anatomy['raw_positions'])
        from fly_rl.visualization.neural_trace import NeuralTrace
        self.trace=NeuralTrace();self.region_filter='ALL';self.class_filter='ALL'
        self.region_options=['ALL']+sorted(set(self.anatomy['regions']))
        self.class_options=['ALL']+sorted(set(self.anatomy['classes']))
        self.mask=np.ones(len(self.points),dtype=bool);self.trace_node=None;self.trace_drawn_step=None
        properties=WindowProperties();properties.setSize(800,900);properties.setTitle('Fly RL | MaleCNS brain activity')
        self.win=app.openWindow(props=properties,type='offscreen' if offscreen else 'onscreen',makeCamera=False,gsg=app.win.getGsg(),requireWindow=True)
        if self.win is None: raise RuntimeError('Could not open the brain activity window')
        self.win.setClearColor((.012,.02,.035,1))
        self.offscreen=offscreen;self.drag=False;self.last_mouse=None;self.closed=False;self.watcher=None;self.input_root=None
        from direct.showbase.DirectObject import DirectObject
        self.events=DirectObject()
        if not offscreen:
            thrower=app.setupMouse(self.win,fMultiWin=True);thrower.node().setPrefix('brain-')
            self.watcher=thrower.getParent().node();self.input_root=thrower.getParent().getParent()
            self.events.accept('brain-mouse1',self.start_drag);self.events.accept('brain-mouse1-up',self.end_drag)
            self.events.accept('brain-wheel_up',self.zoom_by,[1]);self.events.accept('brain-wheel_down',self.zoom_by,[-1])
            self.events.accept('brain-g',self.cycle_filter,['region',1]);self.events.accept('brain-shift-g',self.cycle_filter,['region',-1])
            self.events.accept('brain-h',self.cycle_filter,['class',1]);self.events.accept('brain-shift-h',self.cycle_filter,['class',-1])
            self.events.accept('brain-a',self.clear_filters)
            self.events.accept('brain-m',self.cycle);self.events.accept('brain-b',app.toggle_brain)
            self.events.accept('brain-space',app.toggle_pause);self.events.accept('brain-escape',app.toggle_brain)
            self.events.accept('window-event',self.window_event)
        self.mode='activity';self.selected=None;self.last_step=None;self.neural=None;self.has_activity=False
        self.scene=NodePath('anatomical-map');self.pivot=self.scene.attachNewNode('anatomy-orbit')
        self.lens=OrthographicLens();self.zoom=1.;self.fit_lens();self.lens.setNearFar(.1,20)
        self.camera=self.scene.attachNewNode(Camera('brain-camera',self.lens));self.camera.setPos(0,-4,0);self.camera.lookAt(0,0,0);self.camera.node().setScene(self.scene)
        self.region=self.win.makeDisplayRegion(*self.bounds);self.region.setSort(5);self.region.setCamera(self.camera)
        self.region.setClearColorActive(True);self.region.setClearColor((.012,.02,.035,1));self.region.setClearDepthActive(True)
        fmt=GeomVertexFormat.getV3c4();self.data=GeomVertexData('official-somas',fmt,Geom.UHDynamic)
        self.data.setNumRows(len(self.points))
        self.vertices=np.empty(len(self.points),dtype=[('vertex','<f4',(3,)),('color','u1',(4,))])
        self.vertices['vertex']=self.points;self.vertices['color']=[35,55,74,255]
        self.data.modifyArray(0).modifyHandle().setData(self.vertices.tobytes())
        primitive=GeomPoints(Geom.UHStatic);primitive.addConsecutiveVertices(0,len(self.points));primitive.closePrimitive()
        geometry=Geom(self.data);geometry.addPrimitive(primitive);self.geometry=geometry;node=GeomNode('neuronal-somas');node.addGeom(geometry)
        self.cloud=self.pivot.attachNewNode(node);self.cloud.setRenderModeThickness(2.);self.cloud.setLightOff()
        self.ui=NodePath('brain-window-ui');self.ui_camera=app.makeCamera2d(self.win);self.ui_camera.node().setScene(self.ui)
        from direct.gui.OnscreenText import OnscreenText
        self.header=OnscreenText(text='',parent=self.ui,pos=(-.94,.91),scale=.035,fg=(.7,.94,.86,1),align=TextNode.ALeft,mayChange=True)
        self.trace_label=OnscreenText(text='Select a soma to record its trace',parent=self.ui,pos=(-.94,-.20),scale=.028,fg=(.8,.86,.95,1),align=TextNode.ALeft,mayChange=True)
        self.trace_ticks=OnscreenText(text='',parent=self.ui,pos=(-.9,-.56),scale=.025,fg=(.5,.6,.7,1),align=TextNode.ALeft,mayChange=True)
        self.instructions=OnscreenText(text='',parent=self.ui,pos=(-.94,-.62),scale=.027,fg=(.7,.94,.86,1),align=TextNode.ALeft,mayChange=True)

    def select_body(self,body_id):
        matches=np.flatnonzero(self.anatomy['ids']==body_id)
        if not len(matches): raise ValueError(f'Body {body_id} has no soma in this anatomical map')
        self.selected=int(matches[0]);self.trace.select(int(body_id),int(self.anatomy['indices'][self.selected]))
        self.last_step=None;self.trace_drawn_step=None
        if self.trace_node is not None: self.trace_node.removeNode();self.trace_node=None
        if self.app.flight_record: self.app.flight_record.event('brain-selection',self.app.steps,{'body_id':int(body_id)})

    def cycle_filter(self,kind,direction=1):
        field='region_filter' if kind=='region' else 'class_filter'
        options=self.region_options if kind=='region' else self.class_options
        setattr(self,field,options[(options.index(getattr(self,field))+direction)%len(options)])
        self.apply_filters()

    def clear_filters(self):
        self.region_filter=self.class_filter='ALL';self.apply_filters()

    def apply_filters(self):
        from panda3d.core import Geom,GeomPoints
        self.mask=(self.anatomy['regions']==self.region_filter) if self.region_filter!='ALL' else np.ones(len(self.points),dtype=bool)
        if self.class_filter!='ALL': self.mask &= self.anatomy['classes']==self.class_filter
        primitive=GeomPoints(Geom.UHStatic);primitive.setIndexType(Geom.NTUint32)
        primitive.modifyVertices().modifyHandle().setData(np.flatnonzero(self.mask).astype(np.uint32).tobytes())
        primitive.closePrimitive();self.geometry.setPrimitive(0,primitive)
        if self.mask.all(): self.cloud.setPos(0,0,0);self.zoom=1.
        elif self.mask.any():
            visible=self.points[self.mask];center=(visible.min(axis=0)+visible.max(axis=0))*.5
            self.cloud.setPos(*(-center))
            l,r,b,t=self.bounds;aspect=self.win.getXSize()*(r-l)/(self.win.getYSize()*(t-b))
            extent=np.ptp(visible,axis=0);height=max(extent[2],extent[0]/aspect,.1)*1.3
            self.zoom=float(np.clip(3.1/height,.4,12.))
        self.fit_lens();self.last_step=None
        self.header.setText(self.text())
        if self.app.flight_record: self.app.flight_record.event('brain-filter',self.app.steps,{
            'region':self.region_filter,'superclass':self.class_filter,'visible_somas':int(self.mask.sum())})

    def observe(self,neural):
        return self.trace.sample(neural,self.app.room_id,self.app.env.worlds[0])

    def draw_trace(self):
        from panda3d.core import LineSegs
        if not self.trace.rows:
            self.trace_label.setText('Select a soma to record its trace');return
        rows=list(self.trace.rows);step=rows[-1]['decision_step']
        if self.trace_drawn_step==step: return
        self.trace_drawn_step=step
        if self.trace_node is not None: self.trace_node.removeNode()
        lines=LineSegs();lines.setThickness(1.5)
        xleft=-.9;xright=.9;span=max(rows[-1]['seconds']-rows[0]['seconds'],1.)
        # Activity and commands share a signed [-1,1] scale; both precede the action.
        for key,axis,color in [('activity',None,(1.,.65,.18,1)),('action',0,(.2,.85,.85,1)),('action',3,(.7,.5,1.,1)),('action',2,(.4,1.,.4,1)),('action',1,(1.,.4,.7,1))]:
            lines.setColor(*color);previous=None
            for row in rows:
                value=row[key] if axis is None else row[key][axis]
                point=(xleft+(row['seconds']-rows[0]['seconds'])/span*(xright-xleft),0,-.42+float(value)*.10)
                if previous is None or row['episode_id']!=previous['episode_id'] or row['decision_step']-previous['decision_step']>5: lines.moveTo(*point)
                else: lines.drawTo(*point)
                previous=row
        lines.setColor(.25,.3,.38,1);lines.setThickness(1)
        lines.moveTo(xleft,0,-.42);lines.drawTo(xright,0,-.42)
        self.trace_node=self.ui.attachNewNode(lines.create())
        self.trace_ticks.setText(f"t={rows[0]['seconds']:.2f} to {rows[-1]['seconds']:.2f}s / gaps at episode boundaries")
        self.trace_label.setText(f"Body {self.trace.body_id} / {len(rows)} samples / last {rows[-1]['seconds']-rows[0]['seconds']:.1f}s\nOrange: activity / cyan: forward / purple: yaw\nGreen: vertical / pink: bank command / range [-1,1]")

    def visible(self,value):
        if self.closed: return
        self.region.setActive(value)
        if not self.offscreen:
            from panda3d.core import WindowProperties
            properties=WindowProperties();properties.setMinimized(not value)
            if value: properties.setForeground(True)
            self.win.requestProperties(properties)
        self.end_drag()

    def window_event(self,win):
        if win==self.win and not win.getProperties().getOpen():
            self.app.brain_visible=False;self.app.brain_text.hide();self.close()

    def close(self):
        if self.closed: return
        self.closed=True;self.events.ignoreAll()
        if self.input_root is not None: self.input_root.removeNode()
        if self.win in self.app.winList: self.app.closeWindow(self.win)
        self.scene.removeNode();self.ui.removeNode()

    def start_drag(self):
        if self.watcher and self.watcher.hasMouse():
            mouse=self.watcher.getMouse();point=np.array([mouse.x,mouse.y])
            if self.contains(point): self.pick(point);self.drag=True;self.last_mouse=point

    def end_drag(self): self.drag=False;self.last_mouse=None

    def update_input(self):
        if self.watcher is None or not self.watcher.hasMouse() or not self.win.getProperties().getForeground():
            self.end_drag();return
        if self.drag:
            mouse=self.watcher.getMouse();point=np.array([mouse.x,mouse.y])
            if self.last_mouse is not None: self.rotate(*(point-self.last_mouse))
            self.last_mouse=point

    def capture(self,path):
        from panda3d.core import PNMImage,StringStream
        if self.closed or not self.win.isValid(): return False
        picture=PNMImage();stream=StringStream()
        if not self.win.getScreenshot(picture) or not picture.write(stream,path.name): return False
        payload=stream.getData()
        if not payload: return False
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_name(path.stem+'.tmp'+path.suffix)
        temporary.write_bytes(payload);replace_file(temporary, path)
        return True
    def contains(self,point):
        x,y=(np.asarray(point)+1)*.5;l,r,b,t=self.bounds
        return l<=x<=r and b<=y<=t
    def rotate(self,dx,dy): self.pivot.setH(self.pivot.getH()+dx*150);self.pivot.setP(self.pivot.getP()-dy*150)
    def fit_lens(self):
        l,r,b,t=self.bounds
        aspect=self.win.getXSize()*(r-l)/(self.win.getYSize()*(t-b))
        self.lens.setFilmSize(3.1*aspect/self.zoom,3.1/self.zoom)
    def zoom_by(self,direction):
        self.zoom=float(np.clip(self.zoom*np.exp(direction*.12),.4,12.))
        self.fit_lens()
    def cycle(self):
        self.mode={'activity':'change','change':'sensitivity','sensitivity':'activity'}[self.mode];self.last_step=None
    def update(self,neural):
        if self.closed: return
        self.update_input();self.fit_lens();self.draw_trace()
        self.header.setText(self.text());self.instructions.setText(self.footer())
        if neural.last is None:
            if self.has_activity:
                self.vertices['color']=[35,55,74,255]
                self.data.modifyArray(0).modifyHandle().setData(self.vertices.tobytes())
            self.last_step=None;self.neural=None;self.has_activity=False
            self.header.setText(self.text());self.instructions.setText(self.footer())
            return
        if self.last_step==neural.last['decision_step']: return
        self.neural=neural;self.last_step=neural.last['decision_step'];self.has_activity=True
        self.header.setText(self.text());self.instructions.setText(self.footer())
        array={'activity':neural.snapshot,'change':neural.delta,'sensitivity':neural.sensitivity}[self.mode]
        values=array[self.anatomy['indices']]
        scale={'activity':1.,'change':.25,'sensitivity':max(float(np.max(np.abs(values))),1e-12)}[self.mode]
        intensity=np.clip(np.abs(values)/scale,0,1)**.6
        positive=values>=0
        warm=np.array([255,139,35]);cool=np.array([60,160,255]);base=np.array([24,36,48])
        colors=base+(np.where(positive[:,None],warm,cool)-base)*intensity[:,None]
        self.vertices['color'][:,:3]=colors.astype(np.uint8);self.vertices['color'][:,3]=255
        if self.selected is not None: self.vertices['color'][self.selected]=[255,255,255,255]
        self.data.modifyArray(0).modifyHandle().setData(self.vertices.tobytes())

    def pick(self,point):
        l,r,b,t=self.bounds;x,y=(np.asarray(point)+1)*.5
        target=np.array([2*(x-l)/(r-l)-1,2*(y-b)/(t-b)-1])
        matrix=self.cloud.getMat(self.camera)
        matrix=np.array([[matrix.getCell(i,j) for j in range(4)] for i in range(4)])
        camera_points=np.column_stack([self.points,np.ones(len(self.points))])@matrix
        film=self.lens.getFilmSize();projected=camera_points[:,[0,2]]/np.array([film.x/2,film.y/2])
        pixels=np.array([self.win.getXSize()*(r-l)/2,self.win.getYSize()*(t-b)/2])
        distances=np.linalg.norm((projected-target)*pixels,axis=1)
        distances[~self.mask]=np.inf
        index=int(np.argmin(distances));self.selected=index if distances[index]<12 else None
        if self.selected is not None:
            self.select_body(int(self.anatomy['ids'][self.selected]))
        else: self.trace.select(None,None)
        self.trace_drawn_step=None
        if self.trace_node is not None: self.trace_node.removeNode();self.trace_node=None
        self.last_step=None
    def text(self):
        source=self.anatomy['source'];names={'activity':'Signed modeled activity','change':'Change since previous sample','sensitivity':'Local action sensitivity (relative scale)'}
        if self.neural is not None and self.neural.last is not None and self.neural.last.get('sensitivity_available') is False:
            names['sensitivity']='Sensitivity unavailable for explicit planner'
        phase='' if self.neural is None or self.neural.last is None else f"Decision {self.neural.last['decision_step']} / before action"
        return (f"MaleCNS / real soma positions\n{source['located_neurons']:,}/{self.anatomy['total_neurons']:,} located\n"
            f"{source['unlocated_neurons']:,} without coordinates\n{names[self.mode]} / {phase}\nG neuromere: {self.region_filter} / H class: {self.class_filter}\nVisible: {int(self.mask.sum()):,} somas / A: clear filters")

    def footer(self):
        selected='Click a soma to inspect its body ID'
        if self.selected is not None:
            i=self.selected;idx=self.anatomy['indices'][i]
            value='' if self.neural is None else f'Activity {self.neural.snapshot[idx]:+.4f}'
            selected=f"Body {self.anatomy['ids'][i]} / {self.anatomy['types'][i]}\n{value}"
        if self.trace.rows:
            last=self.trace.rows[-1];selected+=f"\nSpeed {last['speed']:.2f} / bank {last['bank']:+.2f} / target {last['target_distance']:.2f}"
        return (selected+'\nOrange + / blue - / white selected\nDrag: orbit / wheel: zoom / M: mode\nG/H: next filter / Shift+G/H: previous / A: all\nB: hide / SPACE: pause\nSomata only; modeled activity, not measured firing.')
