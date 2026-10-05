"""Panda3D spectator viewer with flight recording; it never invokes training."""
from pathlib import Path
import math
import time
import json
import numpy as np
from fly_rl.training.learning import BrainEnv,make_policy,load_model,checkpoint_sensor_version,checkpoint_history
from fly_rl.simulation.world import ROOM,DT,REWARD_VERSION
from fly_rl.visualization.camera import CameraRig
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.simulation.sensors import RAY_COUNT,SENSOR_VERSION,SENSOR_V5,SENSOR_V6,ray_count,FAN_RANGE,fan_directions,panorama_directions

def run(args):
    from panda3d.core import loadPrcFileData,Geom,GeomNode,GeomVertexData,GeomVertexFormat,GeomVertexWriter,GeomTriangles,LineSegs,AmbientLight,DirectionalLight,TextNode,TransparencyAttrib,ClockObject,Filename
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.OnscreenText import OnscreenText
    loadPrcFileData('', 'window-title Fly RL | MaleCNS v1.0\nwin-size 1280 800\nsync-video false\nshow-frame-rate-meter false')
    if args.offscreen: loadPrcFileData('', 'window-type offscreen\naudio-library-name null')

    def ellipsoid(parent,scale,color):
        v=GeomVertexData('surface',GeomVertexFormat.getV3n3(),Geom.UHStatic)
        vertex=GeomVertexWriter(v,'vertex');normal=GeomVertexWriter(v,'normal')
        rings=12;segments=20
        for i in range(rings+1):
            theta=math.pi*i/rings
            for j in range(segments+1):
                phi=2*math.pi*j/segments
                x=math.sin(theta)*math.cos(phi);y=math.sin(theta)*math.sin(phi);z=math.cos(theta)
                vertex.addData3(x,y,z);normal.addData3(x,y,z)
        faces=GeomTriangles(Geom.UHStatic)
        for i in range(rings):
            for j in range(segments):
                a=i*(segments+1)+j;b=a+segments+1
                faces.addVertices(a,b,a+1);faces.addVertices(a+1,b,b+1)
        g=Geom(v);g.addPrimitive(faces);node=GeomNode('ellipsoid');node.addGeom(g)
        obj=parent.attachNewNode(node);obj.setScale(*scale);obj.setColor(*color)
        return obj

    def box(parent,low,high,color):
        vertices=np.array([[x,y,z] for x in [low[0],high[0]] for y in [low[1],high[1]] for z in [low[2],high[2]]])
        # Flat-shaded, double-sided blocks; face winding cannot hide a collision surface.
        v=GeomVertexData('box',GeomVertexFormat.getV3n3(),Geom.UHStatic)
        writer=GeomVertexWriter(v,'vertex');normal=GeomVertexWriter(v,'normal');faces=GeomTriangles(Geom.UHStatic)
        quads=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        for q in quads:
            points=vertices[list(q)];n=np.cross(points[1]-points[0],points[2]-points[0]);n/=np.linalg.norm(n)
            k=writer.getWriteRow()
            for p in points: writer.addData3(*p);normal.addData3(*n)
            faces.addVertices(k,k+1,k+2);faces.addVertices(k,k+2,k+3)
        g=Geom(v);g.addPrimitive(faces);node=GeomNode('box');node.addGeom(g)
        obj=parent.attachNewNode(node);obj.setColor(*color);obj.setTwoSided(True)
        if color[3]<1:obj.setTransparency(TransparencyAttrib.MAlpha)
        return obj

    class Viewer(ShowBase):
        def __init__(self):
            super().__init__();self.disableMouse();self.setBackgroundColor(.025,.04,.065,1)
            self.camLens.setFov(58);self.camLens.setNearFar(.05,200)
            light=AmbientLight('ambient');light.setColor((.65,.68,.75,1));self.render.setLight(self.render.attachNewNode(light))
            sun=DirectionalLight('sun');sun.setColor((.65,.75,.9,1));node=self.render.attachNewNode(sun);node.setHpr(-35,-55,0);self.render.setLight(node)
            self.is_replay=bool(getattr(args,'archive',None))
            self.comparison_cache={}
            self.is_planner=not self.is_replay and getattr(args,'controller','policy')=='observed-map'
            if self.is_replay:
                from fly_rl.recordings.replay import ReplayEnv,RecordedPolicy
                self.env=ReplayEnv(args.archive);self.policy=RecordedPolicy(self.env)
            else:
                from fly_rl.simulation.sensors import SENSOR_V3
                profile=getattr(args,'map_profile',None)
                sensors=getattr(args,'sensor_version',None) or (checkpoint_sensor_version(args.checkpoint) if args.checkpoint else (SENSOR_V3 if profile else SENSOR_VERSION))
                if self.is_planner:
                    from fly_rl.connectome.innovation import MOTION_STABLE_READOUT
                    from fly_rl.navigation.observed_map import ObservedMapPolicy
                    self.env=BrainEnv(args.data,1,args.device,args.seed,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V6,map_profile='large',readout_version=MOTION_STABLE_READOUT,sensor_backend='torch-cuda' if args.device=='cuda' else 'numpy',history_frames=8,history_stride=8)
                    if getattr(args,'planner_version','v55')=='v55':
                        self.policy=ObservedMapPolicy()
                    else:
                        from fly_rl.navigation.registry import VersionedPlannerPolicy
                        self.policy=VersionedPlannerPolicy(args.planner_version)
                else:
                    self.env=BrainEnv(args.data,1,args.device,args.seed,mode=getattr(args,'room_mode','obstacles'),dynamics=getattr(args,'dynamics','legacy'),sensor_version=sensors,map_profile=profile,readout_version=json.loads(Path(args.checkpoint).with_suffix('.json').read_text()).get('readout_version','random-pool-256-v1') if args.checkpoint else 'random-pool-256-v1',sensor_backend='torch-cuda' if sensors==SENSOR_V6 and args.device=='cuda' else 'numpy',**checkpoint_history(args.checkpoint))
                    self.policy=load_model(args.checkpoint,self.env.brain,self.env,getattr(args,'transfer',False)) if args.checkpoint else make_policy(self.env)
            self.untrained_policy=self.env.archive.manifest.get('metadata',{}).get('untrained') if self.is_replay else (False if self.is_planner else self.policy.num_timesteps == 0)
            # PPO initialization sets environment seeds; the viewer's room seed wins.
            self.env.seed(args.seed)
            self.features=self.env.reset()
            self.brain_map=None;self.neural=None;self.brain_visible=bool(getattr(args,'brain_view',False) or getattr(args,'trace_neuron',None) is not None or getattr(args,'brain_region','ALL')!='ALL' or getattr(args,'brain_class','ALL')!='ALL')
            if not self.is_replay and (self.brain_visible or args.record_brain):
                from fly_rl.visualization.neural_view import NeuralInspector
                self.neural=NeuralInspector(self.env.brain,args.data)
            self.paused=False;self.sensors_visible=True;self.seed=args.seed
            self.started=time.monotonic();self.accumulator=0.;self.frames=0;self.steps=0
            self.collisions=0;self.successes=0;self.trail=[];self.phase=0.
            self.rig=CameraRig();self.keys={};self.drag=None;self.last_mouse=None
            self.rig.target=self.env.worlds[0].room*.5
            self.rig.distance=float(np.linalg.norm(self.env.worlds[0].room)*1.05)
            self.flight_record=None;self.room_id=0;self.finished=False;self.preview_saved=False
            if self.is_replay: self.room_id=self.env.current_room_id
            self.room=self.render.attachNewNode('room');self.dynamic=self.render.attachNewNode('dynamic')
            self.fly=self.render.attachNewNode('fly')
            ellipsoid(self.fly,(.3,.12,.12),(.17,.2,.23,1))
            abdomen=ellipsoid(self.fly,(.22,.11,.1),(.48,.31,.1,1));abdomen.setX(-.23)
            head=ellipsoid(self.fly,(.12,.13,.13),(.24,.25,.28,1));head.setX(.3)
            for y in [-.105,.105]:
                eye=ellipsoid(self.fly,(.085,.05,.09),(.9,.22,.16,1));eye.setPos(.32,y,.025)
            self.wings=[]
            for side in [-1,1]:
                pivot=self.fly.attachNewNode('wing-pivot');pivot.setPos(.03,.04*side,.08)
                wing=ellipsoid(pivot,(.17,.4,.014),(.65,.88,1,.5));wing.setY(.28*side)
                wing.setTransparency(TransparencyAttrib.MAlpha);wing.setTwoSided(True)
                self.wings.append((pivot,side))
            self.header=OnscreenText(text='FLY RL',pos=(-1.53,.9),scale=.075,fg=(.9,.96,1,1),align=TextNode.ALeft)
            self.subtitle=OnscreenText(text='FULL MALE CNS CONNECTOME / AUTONOMOUS FLIGHT',pos=(-1.53,.815),scale=.031,fg=(.35,.82,.9,1),align=TextNode.ALeft)
            self.hud=OnscreenText(text='',pos=(-1.53,.7),scale=.034,fg=(.75,.84,.92,1),align=TextNode.ALeft,mayChange=True)
            self.brain_text=OnscreenText(text='',pos=(-1.53,-.69),scale=.029,
                fg=(.7,.94,.86,1),align=TextNode.ALeft,mayChange=True)
            if self.brain_visible and not self.is_replay: self.create_brain_map()
            if not self.brain_visible: self.brain_text.hide()
            self.accept('m',self.cycle_brain)
            self.accept('b',self.toggle_brain)
            self.controls=OnscreenText(text='LMB drag orbit / RMB look / MMB pan / wheel zoom\nC camera modes / WASD + Q/E free move / SHIFT: simulation 10x / F focus fly\nSPACE pause / R reset / N new room / V sensors / ESC exit',pos=(-1.53,-.82),scale=.027,fg=(.62,.72,.82,1),align=TextNode.ALeft)
            label=('REPLAY / SAVED STATES / '+self.env.inspection['status'].upper()) if self.is_replay else ('OBSERVED MAP PLANNER / NO LEARNED MOVEMENT WEIGHTS' if self.is_planner else 'UNTRAINED POLICY / NO TRAINING RUNNING' if self.untrained_policy else 'CHECKPOINT POLICY / NO TRAINING RUNNING')
            if self.is_planner and self.policy.specification.get('experimental'):
                label='EXPERIMENTAL '+getattr(args,'planner_version','').upper()+' PLANNER / NO TRAINING RUNNING'
            self.label=OnscreenText(text=label,pos=(1.52,.89),scale=.029,fg=(1,.72,.32,1),align=TextNode.ARight)
            if self.is_replay:
                self.controls.setText('Mouse + C: camera / WASD + Q/E: free move / F: focus\nSPACE pause / R rewind / N next episode / PageUp-Down seek / V sensors / ESC exit')
                self.accept('page_up',self.seek_replay,[100]);self.accept('page_down',self.seek_replay,[-100])
            self.accept('space',self.toggle_pause);self.accept('r',self.reset_room);self.accept('n',self.new_room)
            self.accept('c',self.toggle_camera);self.accept('s',self.toggle_sensors);self.accept('escape',self.userExit)
            self.accept('arrow_left',self.orbit,[-.15]);self.accept('arrow_right',self.orbit,[.15])
            self.accept('arrow_up',self.tilt,[.1]);self.accept('arrow_down',self.tilt,[-.1])
            for key in ['w','a','s','d','q','e','shift']:
                self.accept(key,self.set_key,[key,True]);self.accept(key+'-up',self.set_key,[key,False])
                if key!='shift':
                    self.accept('shift-'+key,self.set_key,[key,True]);self.accept('shift-'+key+'-up',self.set_key,[key,False])
            # Keep S as the sensor toggle outside free-camera mode.
            self.accept('s',self.sensor_or_back)
            self.accept('v',self.toggle_sensors)
            self.accept('f',self.focus_fly)
            for button,mode in [('mouse1','orbit'),('mouse2','pan'),('mouse3','look')]:
                self.accept(button,self.start_drag,[mode]);self.accept(button+'-up',self.end_drag)
                self.accept('shift-'+button,self.start_drag,[mode]);self.accept('shift-'+button+'-up',self.end_drag)
            self.accept('wheel_up',self.zoom_view,[1]);self.accept('wheel_down',self.zoom_view,[-1])
            self.accept('shift-wheel_up',self.zoom_view,[1]);self.accept('shift-wheel_down',self.zoom_view,[-1])
            self.draw_room()
            self.controls_checked=False
            if args.offscreen:
                self.verify_controls()
            if not args.no_record and not self.is_replay:
                from fly_rl.connectome.brain import MODEL_SPEC
                self.flight_record=FlightRecorder(args.record_dir,{
                    'dataset':self.env.brain.audit,'brain_fingerprint':self.env.brain.fingerprint,
                    'brain_feature_count':self.env.feature_count,'readout_version':getattr(self.env.brain,'readout_version','random-pool-256-v1'),
                    'sensor_version':self.env.brain.sensor_version,'dt':DT,'seed':args.seed,'policy_seed':42,
                    'untrained':self.untrained_policy,'checkpoint_source':args.checkpoint,
                    'record_brain':args.record_brain,'controller':self.policy.specification if self.is_planner else {'kind':'learned_policy'},'training_updates':getattr(self.policy,'_n_updates',0),
                    'policy_timesteps':getattr(self.policy,'num_timesteps',0),'reservoir_spec':self.env.brain.model_spec,
                    'reward_version':REWARD_VERSION,
                    'anatomical_map':self.brain_map.anatomy['source'] if self.brain_map else None,
                    'neural_inspection':{'region_filter':self.brain_map.region_filter if self.brain_map else None,
                        'superclass_filter':self.brain_map.class_filter if self.brain_map else None,
                        'trace_body_id':self.brain_map.trace.body_id if self.brain_map else None,
                        'sample_interval':5,'history_capacity':240},
                    'simulation_speed':args.speed,'shift_speed_multiplier':10,
                    'neural_observation_phase':'before_action','neural_observation_interval':5,
                    'device':args.device,'flight':{'room_size':self.env.worlds[0].room.tolist(),'body_radius':.16,'max_speed':3.,
                        'acceleration_scale':3.,'drag':.6,'yaw_scale':2.1,'episode_steps':self.env.worlds[0].episode_limit,
                        'mode':self.env.worlds[0].mode,'dynamics':self.env.worlds[0].dynamics,
                        'world_version':'rooms-v4-profiled-passages' if self.env.map_profile else 'rooms-v3-dense-random-goals',
                        'map_profile':self.env.map_profile.to_dict() if self.env.map_profile else None}})
                from fly_rl.training.learning import save_model
                if self.is_planner:
                    if hasattr(self.policy,'archive_sources'):
                        self.policy.archive_sources(self.flight_record.path)
                    else:
                        from fly_rl.navigation import observed_map
                        source=Path(observed_map.__file__)
                        (self.flight_record.path/'controller.py').write_bytes(source.read_bytes())
                        (self.flight_record.path/'controller.json').write_text(json.dumps(self.policy.specification,indent=2),encoding='utf-8')
                else: save_model(self.policy,self.flight_record.path/'policy.zip',self.env.brain)
                self.record_room('initial')
                print('Recording flight to',self.flight_record.path,flush=True)
            self.write_summary('running')
            self.taskMgr.add(self.update,'flight')

        def verify_controls(self):
            original_seed=self.seed
            if self.brain_map:
                from panda3d.core import Point3,Point2
                brain_map=self.brain_map;brain_map.clear_filters()
                heading=brain_map.pivot.getH();brain_map.rotate(.1,.1)
                assert brain_map.pivot.getH()!=heading
                brain_map.pivot.setHpr(0,0,0)
                brain_map.zoom_by(1);assert brain_map.zoom!=1.;brain_map.zoom_by(-1)
                for _ in range(3): brain_map.cycle()
                assert brain_map.mode=='activity'
                point=brain_map.camera.getRelativePoint(brain_map.pivot,Point3(*brain_map.points[100]))
                projected=Point2();assert brain_map.lens.project(point,projected)
                l,r,b,t=brain_map.bounds
                mouse=[2*(l+(projected.x+1)*.5*(r-l))-1,2*(b+(projected.y+1)*.5*(t-b))-1]
                brain_map.pick(mouse);assert brain_map.selected is not None
                index=brain_map.selected
                assert brain_map.anatomy['ids'][index]==self.neural.ids[brain_map.anatomy['indices'][index]]
                brain_map.selected=None
                brain_map.region_filter='T1';brain_map.apply_filters()
                assert brain_map.mask.sum()>0 and brain_map.mask.sum()<len(brain_map.points)
                assert brain_map.geometry.getPrimitive(0).getNumVertices()==brain_map.mask.sum()
                from panda3d.core import Point3,Point2
                visible=int(np.flatnonzero(brain_map.mask)[0])
                point=brain_map.camera.getRelativePoint(brain_map.cloud,Point3(*brain_map.points[visible]))
                projected=Point2();assert brain_map.lens.project(point,projected)
                l,r,b,t=brain_map.bounds
                mouse=[2*(l+(projected.x+1)*.5*(r-l))-1,2*(b+(projected.y+1)*.5*(t-b))-1]
                brain_map.pick(mouse);assert brain_map.selected is not None and brain_map.mask[brain_map.selected]
                brain_map.clear_filters();assert brain_map.mask.all()
                self.toggle_brain();assert not self.brain_visible
                self.toggle_brain();assert self.brain_visible
                main_window=self.win
                brain_map.close();self.brain_visible=False
                assert self.win==main_window and main_window.isValid()
                assert brain_map.win not in self.winList
                self.toggle_brain();assert self.brain_visible and self.brain_map.win!=main_window
                assert len(self.winList)==2
            self.toggle_pause();assert self.paused
            self.toggle_pause();assert not self.paused
            self.toggle_camera();assert self.rig.mode=='chase'
            self.toggle_camera();assert self.rig.mode=='free'
            p=self.rig.position.copy();self.rig.move(1,0,1,.1)
            assert not np.allclose(p,self.rig.position)
            self.toggle_camera();assert self.rig.mode=='orbit'
            distance=self.rig.distance;self.rig.zoom(1);assert self.rig.distance<distance
            self.rig.zoom(-1)
            self.toggle_sensors();assert not self.sensors_visible
            self.toggle_sensors();assert self.sensors_visible
            if self.is_replay:
                self.features=self.env.next_episode();self.features=self.env.reset()
                self.room_id=self.env.current_room_id;self.draw_room();return
            position=self.env.worlds[0].position.copy()
            self.reset_room();assert np.allclose(position,self.env.worlds[0].position)
            self.new_room();assert self.seed==original_seed+1
            assert not np.allclose(position,self.env.worlds[0].position)
            self.seed=original_seed;self.reset_room()
            self.controls_checked=True

        def toggle_pause(self):
            self.paused=not self.paused
            if self.flight_record: self.flight_record.event('pause',self.steps,{'paused':self.paused})
        def toggle_camera(self):
            w=self.env.worlds[0];self.rig.cycle(w.position,w.rotation())
        def toggle_sensors(self): self.sensors_visible=not self.sensors_visible
        def sensor_or_back(self):
            if self.rig.mode=='free': self.keys['s']=True
            else: self.toggle_sensors()
        def set_key(self,key,value): self.keys[key]=value
        def start_drag(self,kind): self.drag=kind;self.last_mouse=None
        def simulation_shift(self):
            from panda3d.core import KeyboardButton
            watchers=[]
            if not args.offscreen and self.mouseWatcherNode is not None and self.win.getProperties().getForeground():
                watchers.append(self.mouseWatcherNode)
            if self.brain_map and not self.brain_map.closed and not self.brain_map.offscreen and self.brain_map.win.getProperties().getForeground():
                watchers.append(self.brain_map.watcher)
            return any(w is not None and (w.getModifierButtons().isDown(KeyboardButton.shift()) or
                any(w.isButtonDown(button) for button in [KeyboardButton.shift(),KeyboardButton.lshift(),KeyboardButton.rshift()])) for w in watchers)
        def camera_fast(self):
            watcher=self.mouseWatcherNode
            if watcher is not None:
                from panda3d.core import KeyboardButton
                return watcher.getModifierButtons().isDown(KeyboardButton.shift())
            return self.keys.get('shift',False)
        def zoom_view(self,direction): self.rig.zoom(direction,fast=self.camera_fast())
        def end_drag(self): self.drag=None;self.last_mouse=None
        def orbit(self,delta): self.rig.yaw+=delta
        def tilt(self,delta): self.rig.pitch=float(np.clip(self.rig.pitch+delta,-1.3,1.5))
        def focus_fly(self): self.rig.focus(self.env.worlds[0].position)
        def update_camera(self,elapsed):
            watcher=self.mouseWatcherNode
            if watcher is not None:
                from panda3d.core import KeyboardButton
                # Physical key state stays correct when Shift changes mid-press.
                if self.win.getProperties().getForeground():
                    for key in ['w','a','s','d','q','e']:
                        self.keys[key]=watcher.isButtonDown(KeyboardButton.asciiKey(key))
                else:
                    self.keys.clear();self.end_drag()
            fast=self.camera_fast()
            if self.drag and watcher is not None and watcher.hasMouse():
                mouse=watcher.getMouse();point=np.array([mouse.x,mouse.y])
                if self.last_mouse is not None:
                    dx,dy=point-self.last_mouse
                    if self.drag=='pan' and self.rig.mode=='orbit': self.rig.pan(dx*(4 if fast else 1),dy*(4 if fast else 1))
                    elif self.drag in ['orbit','look']: self.rig.rotate(dx,dy)
                self.last_mouse=point
            elif watcher is None or not watcher.hasMouse(): self.last_mouse=None
            self.rig.move(int(self.keys.get('w',False))-int(self.keys.get('s',False)),
                int(self.keys.get('d',False))-int(self.keys.get('a',False)),
                int(self.keys.get('e',False))-int(self.keys.get('q',False)),elapsed,fast)
            w=self.env.worlds[0];position,target=self.rig.pose(w.position,w.rotation())
            self.camera.setPos(*position);self.camera.lookAt(*target)

        def record_room(self,reason):
            if self.flight_record:
                from fly_rl.simulation.map_profiles import difficulty_metrics
                self.flight_record.event('room',self.steps,{'room_id':self.room_id,'seed':self.seed,'reason':reason,
                    'size':self.env.worlds[0].room,'initial_state':self.env.worlds[0].snapshot(),
                    'difficulty':difficulty_metrics(self.env.worlds[0])})

        def seek_replay(self,offset):
            self.features=self.env.seek(self.env.cursor+offset);self.room_id=self.env.current_room_id
            self.trail=[];self.draw_room()

        def create_brain_map(self):
            from fly_rl.visualization.brain_map import BrainMap
            self.brain_map=BrainMap(self,args.data,offscreen=args.offscreen)
            region=getattr(args,'brain_region','ALL');superclass=getattr(args,'brain_class','ALL')
            if region not in self.brain_map.region_options or superclass not in self.brain_map.class_options:
                raise ValueError('Unknown anatomical filter; use G/H to browse official labels')
            self.brain_map.region_filter=region;self.brain_map.class_filter=superclass;self.brain_map.apply_filters()
            if getattr(args,'trace_neuron',None) is not None: self.brain_map.select_body(args.trace_neuron)
        def cycle_brain(self):
            if self.brain_map: self.brain_map.cycle()
        def toggle_brain(self):
            self.brain_visible=not self.brain_visible
            if self.brain_visible:
                self.brain_text.show()
                if not self.is_replay and (self.brain_map is None or self.brain_map.closed): self.create_brain_map()
                if self.brain_map: self.brain_map.visible(True)
                if not self.is_replay and self.neural is None:
                    from fly_rl.visualization.neural_view import NeuralInspector
                    self.neural=NeuralInspector(self.env.brain,args.data)
            else:
                self.brain_text.hide()
                if self.brain_map: self.brain_map.visible(False)

        def reset_room(self):
            if self.is_planner: self.policy.reset()
            if self.neural: self.neural.reset()
            self.env.seed(self.seed);self.features=self.env.reset();self.trail=[];self.draw_room()
            if self.is_replay: self.room_id=self.env.current_room_id;self.paused=False
            else: self.room_id+=1;self.record_room('manual-reset')
        def new_room(self):
            if self.is_replay:
                self.features=self.env.next_episode();self.room_id=self.env.current_room_id
                self.trail=[];self.draw_room();self.paused=False
            else: self.seed+=1;self.reset_room()
        def draw_room(self):
            self.room.removeNode();self.room=self.render.attachNewNode('room')
            size=self.env.worlds[0].room;sx,sy,sz=size
            box(self.room,np.array([0.,0.,-.12]),np.array([sx,sy,0.]),(.085,.12,.17,1))
            lines=LineSegs();lines.setThickness(1);lines.setColor(.15,.23,.3,1)
            for i in range(int(max(sx,sy))+1):
                if i<=sx: lines.moveTo(i,0,.005);lines.drawTo(i,sy,.005)
                if i<=sy: lines.moveTo(0,i,.005);lines.drawTo(sx,i,.005)
            lines.setColor(.3,.55,.65,1)
            for x in [0,sx]:
                for y in [0,sy]: lines.moveTo(x,y,0);lines.drawTo(x,y,sz)
            for z in [0,sz]:
                lines.moveTo(0,0,z);lines.drawTo(sx,0,z);lines.drawTo(sx,sy,z);lines.drawTo(0,sy,z);lines.drawTo(0,0,z)
            self.room.attachNewNode(lines.create())
            w=self.env.worlds[0]
            partition_boxes=4*(w.map_profile.wall_count+w.map_profile.branch_count) if w.map_profile else 0
            for index,(low,high) in enumerate(w.obstacles):
                # See the fly and openings through tall partitions; collision geometry stays solid.
                box(self.room,low,high,(.2,.35,.45,.24 if index<partition_boxes else 1.))
            target=ellipsoid(self.room,(.27,.27,.27),(.2,.95,.7,1));target.setPos(*w.target)

        def update(self,task):
            elapsed=DT if args.offscreen else min(ClockObject.getGlobalClock().getDt(),.1)
            from fly_rl.visualization.playback import simulation_speed
            self.effective_speed=simulation_speed(args.speed,self.simulation_shift())
            self.phase+=elapsed*self.effective_speed;self.frames+=1
            if not self.paused:
                self.accumulator+=elapsed*self.effective_speed
                while self.accumulator>=DT:
                    if self.is_replay and self.env.finished:
                        self.paused=True;self.accumulator=0.;break
                    # Stochastic actions make an untrained policy visibly explore.
                    action,_=self.policy.predict(self.features,deterministic=bool(args.checkpoint))
                    if self.neural and (self.brain_visible or args.record_brain) and self.steps%5==0:
                        observation=self.neural.sample_activity(action[0],self.steps+1) if self.is_planner else self.neural.sample(self.policy,self.features,action[0],self.steps+1)
                        if self.flight_record: self.flight_record.event('brain-observation',self.steps+1,observation)
                        if self.brain_map and not self.brain_map.closed:
                            trace=self.brain_map.observe(self.neural)
                            if self.flight_record and trace: self.flight_record.event('selected-neuron',self.steps+1,trace)
                    if self.flight_record and args.record_brain and (self.steps+1)%20==0:
                        self.flight_record.brain_snapshot(self.steps+1,self.env.brain.state[:,0].cpu().numpy())
                    before=self.env.worlds[0].snapshot();sensors=self.env.latest_sensors[0].copy() if not self.is_replay else self.env.worlds[0].observe();features=self.env.latest_features[0].copy() if not self.is_replay else self.features[0].copy()
                    self.features,rewards,dones,infos=self.env.step(action)
                    self.steps+=1;self.accumulator-=DT
                    if self.is_replay and self.room_id!=self.env.current_room_id:
                        self.room_id=self.env.current_room_id;self.trail=[];self.draw_room()
                    if self.flight_record:
                        self.flight_record.transition(self.steps,self.room_id,sensors,features,action[0],before,infos[0],rewards[0])
                    if dones[0]:
                        self.collisions+=int(infos[0]['collision']);self.successes+=int(infos[0]['success'])
                        if self.flight_record: self.flight_record.event('episode-end',self.steps,{
                            'room_id':self.room_id,'collision':infos[0]['collision'],'success':infos[0]['success'],
                            'truncated':infos[0]['truncated'],'episode':infos[0]['episode']})
                        if not self.is_replay:
                            if self.is_planner: self.policy.reset()
                            if self.neural: self.neural.reset()
                            self.room_id+=1;self.record_room('automatic-reset')
                            self.trail=[];self.draw_room()
                    self.trail.append(self.env.worlds[0].position.copy());self.trail=self.trail[-400:]
            w=self.env.worlds[0];self.fly.setPos(*w.position);self.fly.setH(math.degrees(w.yaw))
            # The mesh faces +X; Panda pitch rotates around that forward axis.
            self.fly.setP(math.degrees(w.bank));self.fly.setR(-math.degrees(w.pitch))
            if self.brain_visible:
                if self.brain_map:
                    self.brain_map.update(self.neural)
                self.brain_text.setText('Brain activity: separate window / B hide / SPACE pause' if self.brain_map else
                    'REPLAY\nThis view has saved features only.\nFull neuron snapshots are optional.\nUse the live demo with --brain-view.')
            for wing,side in self.wings: wing.setP(math.sin(self.phase*55)*25*side)
            self.update_camera(elapsed)
            self.dynamic.removeNode();self.dynamic=self.render.attachNewNode('dynamic')
            self.dynamic.setTransparency(TransparencyAttrib.MAlpha)
            lines=LineSegs();lines.setThickness(2);lines.setColor(.2,.85,.9,1)
            if self.trail:
                lines.moveTo(*self.trail[0])
                for p in self.trail[1:]: lines.drawTo(*p)
            if self.is_replay and getattr(args,'compare',None):
                from fly_rl.recordings.archive import room_fingerprint
                from fly_rl.recordings.replay import matching_trajectory
                layout=room_fingerprint(self.env.archive.rooms[self.room_id])
                if layout not in self.comparison_cache:
                    self.comparison_cache[layout]=matching_trajectory(args.compare,layout)
                other=self.comparison_cache[layout]
                if other:
                    lines.setColor(.95,.3,.8,.8);lines.moveTo(*other[0])
                    for point in other[1:]: lines.drawTo(*point)
            if self.sensors_visible:
                if self.is_replay:
                    directions=np.asarray(self.env.archive.manifest['local_ray_directions'])@w.rotation().T
                    distances=self.env.sensor_state[:len(directions)]*self.env.archive.manifest['ray_range']
                elif hasattr(self.env,'latest_sensors'):
                    from fly_rl.simulation.sensors import DIRECTIONS,RAY_RANGE
                    directions=DIRECTIONS@w.rotation().T;distances=self.env.latest_sensors[0,:128]*RAY_RANGE
                else: directions,distances=w.rays()
                version=self.env.archive.manifest['sensor_version'] if self.is_replay else w.sensor_version
                if version in (SENSOR_V5,SENSOR_V6):
                    if self.is_replay:
                        fan=(panorama_directions() if version==SENSOR_V6 else fan_directions((w.target-w.position)@w.rotation()))@w.rotation().T
                        lengths=self.env.sensor_state[269:269+len(fan)]*FAN_RANGE
                    elif hasattr(self.env,'latest_sensors'):
                        fan=(panorama_directions() if version==SENSOR_V6 else fan_directions((w.target-w.position)@w.rotation()))@w.rotation().T
                        lengths=self.env.latest_sensors[0,269:269+len(fan)]*FAN_RANGE
                    else:fan,lengths=w.fan_rays()
                    directions=np.vstack([directions,fan]);distances=np.r_[distances,lengths]
                lines.setThickness(1);lines.setColor(.2,.43,.48,.25)
                for d,length in zip(directions,distances):
                    lines.setColor(*((1.,.35,.15,.7) if length<1. else (.2,.43,.48,.25)))
                    lines.moveTo(*(w.position+d*.4));lines.drawTo(*(w.position+d*max(length,.4)))
            self.dynamic.attachNewNode(lines.create())
            activity=float(self.env.brain.state.abs().mean().item())
            self.hud.setText(f"MaleCNS v1.0\n{self.env.brain.n:,} neurons | {self.env.brain.audit['edges']:,} directed edges\nDevice: {args.device.upper()} | room {self.seed}\nMap: {w.map_profile.name if w.map_profile else 'dense-v3' if w.mode=='dense' else w.mode} | {len(w.obstacles)} boxes\nSensors: {ray_count(getattr(w,'sensor_version',SENSOR_VERSION))} rays + approach speeds\nSimulation: {self.effective_speed:g}x / hold SHIFT: 10x boost\nCamera: {self.rig.mode.upper()} | recording: {'ON' if self.flight_record else 'OFF'}\n\nSpeed: {np.linalg.norm(w.velocity):.2f} units/s\nTarget: {w.distance:.2f} units\nMean brain activity: {activity:.3f}\nSteps: {self.steps} | collisions: {self.collisions}\nTargets reached: {self.successes}\n"+('PAUSED' if self.paused else 'RUNNING'))
            if self.is_replay:
                overlay=(' / comparison: magenta' if other else ' / no matching comparison room') if getattr(args,'compare',None) else ''
                self.hud.setText(f"SAVED FLIGHT / no brain or policy execution\nFrame: {self.env.cursor}/{self.env.total} | room {self.room_id}\nCamera: {self.rig.mode.upper()} | speed {self.effective_speed:g}x{overlay}\n\nSpeed: {np.linalg.norm(w.velocity):.2f} units/s\nTarget: {w.distance:.2f} units\nSaved feature magnitude: {activity:.3f}\nAction: {np.array2string(w.last_action,precision=2)}\nNearest sensed obstacle: {float(np.min(self.env.sensor_state[:128]))*8.:.2f}\n"+('END OF RECORDING' if self.env.finished else ('PAUSED' if self.paused else 'PLAYING')))
            if not self.preview_saved and self.frames>=2:
                self.capture_preview();self.preview_saved=True
            stop=(args.seconds>0 and (self.frames*DT if args.offscreen else time.monotonic()-self.started)>=args.seconds)
            if stop:
                self.finish();self.userExit()
            return task.cont

        def capture_preview(self):
            if self.win is None or not self.win.isValid(): return False
            self.graphicsEngine.renderFrame();self.graphicsEngine.renderFrame()
            path=Path(args.screenshot);path.parent.mkdir(parents=True,exist_ok=True)
            # Native Panda file writes can fail while stream encoding succeeds.
            # Python writes also preserve the previous preview on failure.
            from panda3d.core import PNMImage,StringStream
            picture=PNMImage();stream=StringStream()
            saved=bool(self.win.getScreenshot(picture) and picture.write(stream,path.name))
            if saved:
                temporary=path.with_name(path.stem+'.tmp'+path.suffix)
                temporary.write_bytes(stream.getData());temporary.replace(path)
            if self.brain_map and not self.brain_map.closed:
                self.brain_map.capture(path.with_name(path.stem+'-brain'+path.suffix))
            return saved

        def summary(self,status):
            result={'status':status,'frames':self.frames,'steps':self.steps,'collisions':self.collisions,
                'successes':self.successes,'screenshot':str(args.screenshot),'untrained':self.untrained_policy,
                'simulation_speed':args.speed,'shift_speed_multiplier':10,'training_invoked':False,'finite_activity':bool(np.isfinite(self.features).all()),
                'mean_activity':float(self.env.brain.state.abs().mean().item()),'controls_checked':self.controls_checked,
                'sensor_count':ray_count(self.env.worlds[0].sensor_version),'sensor_values':len(self.env.worlds[0].observe()),
                'recording':str(self.flight_record.path) if self.flight_record else None}
            result.update(dynamics=self.env.worlds[0].dynamics,brain_view=self.brain_visible,controller=self.policy.specification if self.is_planner else {'kind':'recorded_flight' if self.is_replay else 'learned_policy'})
            w=self.env.worlds[0]
            result.update(map_profile=w.map_profile.to_dict() if w.map_profile else None,room_size=w.room.tolist(),episode_limit=w.episode_limit)
            if self.brain_map:
                result['anatomical_map']=dict(self.brain_map.anatomy['source'],display='separate_window')
                result['neural_inspection']={'region_filter':self.brain_map.region_filter,
                    'superclass_filter':self.brain_map.class_filter,'trace_body_id':self.brain_map.trace.body_id,
                    'trace_samples':len(self.brain_map.trace.rows)}
            if self.is_replay:
                result.update(archive=str(self.env.archive.path),replay=True,brain_executed=False,
                    untrained=self.env.archive.manifest.get('metadata',{}).get('untrained'),
                    source_status=self.env.inspection['status'],saved_frames=self.env.total,playback_frame=self.env.cursor,
                    mean_activity=None,comparison=getattr(args,'compare',None))
            return result

        def write_summary(self,status):
            Path('reports').mkdir(exist_ok=True)
            Path('reports/replay.json' if self.is_replay else 'reports/demo.json').write_text(json.dumps(self.summary(status),indent=2),encoding='utf8')

        def finish(self,error=None,exit_reason='normal',capture=True):
            if self.finished: return
            status='failed' if error else 'closed'
            summary=self.summary(status)
            summary['exit_reason']=exit_reason
            if error:
                summary['error']=error
                if self.flight_record: self.flight_record.event('error',self.steps,{'message':error})
            from fly_rl.recordings.shutdown import finalize_session
            finalize_session(self.flight_record,summary,self.capture_preview if capture else None,
                             'reports/replay.json' if self.is_replay else 'reports/demo.json')
            self.finished=True
            if self.brain_map: self.brain_map.close()
            print(json.dumps(summary,indent=2),flush=True)

    app=Viewer()
    from fly_rl.recordings.shutdown import run_application
    run_application(app)
