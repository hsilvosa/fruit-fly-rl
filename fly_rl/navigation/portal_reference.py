"""Find observable openings in broad vertical surfaces from neural range rays."""
import numpy as np
from scipy.spatial import cKDTree
from fly_rl.navigation.room_aware import RoomAwareController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp1'


class PortalReferenceController(RoomAwareController):
    """Commit to an observed approach and crossing, without a hidden gate list."""

    def __init__(self, room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.portal=None
        self.portal_started=0
        self.portal_phase='none'
        self.portal_crossings=0

    def detect_portal(self, values):
        ranges=np.clip(values[269:2069]*24,.05,24)
        directions=self.directions @ self.rotation().T
        points=directions*ranges[:,None]
        z=points[:,2]+self.position[2]
        keep=(ranges<23.4)&(z>.5)&(z<self.room_size[2]-.5)
        xy=points[keep,:2]
        if len(xy)<80:return None
        toward=(self.initial_goal-self.position)[:2]
        toward=toward/max(np.linalg.norm(toward),1e-8)
        rng=np.random.default_rng(42)
        best=None
        for i,j in rng.integers(len(xy),size=(48,2)):
            delta=xy[j]-xy[i]
            if np.linalg.norm(delta)<1:continue
            normal=np.array([delta[1],-delta[0]])/np.linalg.norm(delta)
            if normal@toward<0:normal=-normal
            alignment=float(normal@toward)
            distance=float(xy[i]@normal)
            if alignment<.35 or not .5<distance<6:continue
            inliers=np.abs(xy@normal-distance)<.12
            if inliers.sum()<80:continue
            subset=xy[inliers]
            _,vectors=np.linalg.eigh(np.cov(subset.T))
            normal=vectors[:,0]
            if normal@toward<0:normal=-normal
            distance=float(np.median(subset@normal))
            tangent=np.array([-normal[1],normal[0]])
            span=subset@tangent
            if np.ptp(span)<8 or not .5<distance<6:continue
            score=float(inliers.sum())*float(normal@toward)**2/(1+.1*distance)
            if best is None or score>best[0]:best=(score,normal,distance,span.min(),span.max())
        if best is None:return None
        _,normal,distance,low,high=best
        tangent=np.array([-normal[1],normal[0]])
        denom=directions[:,:2]@normal
        expected=np.divide(distance,denom,out=np.full(len(denom),np.inf),where=denom>.01)
        visible=(expected>0)&(expected<23)&(ranges>expected+1.)
        candidates=directions[visible]*expected[visible,None]
        if not len(candidates):return None
        horizontal=candidates[:,:2]@tangent
        heights=candidates[:,2]+self.position[2]
        usable=(horizontal>low+.5)&(horizontal<high-.5)&(heights>.6)&(heights<self.room_size[2]-.6)
        candidates=candidates[usable]
        if len(candidates)<3:return None
        coordinates=np.column_stack([candidates[:,:2]@tangent,candidates[:,2]])
        parent=list(range(len(candidates)))
        def root(i):
            while parent[i]!=i:
                parent[i]=parent[parent[i]];i=parent[i]
            return i
        for i,j in cKDTree(coordinates).query_pairs(.9):parent[root(i)]=root(j)
        groups={}
        for i in range(len(candidates)):groups.setdefault(root(i),[]).append(i)
        options=[]
        for members in groups.values():
            if len(members)<3:continue
            cluster=candidates[members]
            center=np.median(cluster,axis=0)+self.position
            center[:2]+=normal*(distance-(center-self.position)[:2]@normal)
            direction=np.r_[normal,0.]
            approach=center-direction*1.1
            score=np.linalg.norm(approach-self.position)+.3*np.linalg.norm(center-self.initial_goal)
            options.append((score,center,direction,len(members)))
        if not options:return None
        _,center,normal,count=min(options,key=lambda item:item[0])
        return dict(center=center,normal=normal,ray_support=count)

    def plan(self, goal):
        if self.portal is not None:
            delta=self.position-self.portal['center']
            passed=delta@self.portal['normal']>.9
            expired=self.tick-self.portal_started>600
            if passed or expired:
                self.portal_crossings+=int(passed)
                self.portal=None;self.reference=None;self.portal_phase='none'
        if self.portal is None:
            self.portal=self.detect_portal(self.current_values)
            if self.portal is not None:
                self.portal_started=self.tick;self.portal_phase='approach';self.reference=None
        destination=goal
        if self.portal is not None:
            center,normal=self.portal['center'],self.portal['normal']
            offset=self.position-center
            tangent=offset-normal*(offset@normal)
            if self.portal_phase=='approach' and np.linalg.norm(tangent)<.45 and -.0>offset@normal>-1.8:
                self.portal_phase='cross';self.reference=None
            destination=center+normal*(1.3 if self.portal_phase=='cross' else -1.1)
        super().plan(destination)
        self.debug.update(portal_phase=self.portal_phase,portal_crossings=self.portal_crossings,
            portal_center=self.portal['center'].tolist() if self.portal is not None else None,
            portal_normal=self.portal['normal'].tolist() if self.portal is not None else None,
            portal_ray_support=self.portal['ray_support'] if self.portal is not None else 0,
            portal_age=self.tick-self.portal_started if self.portal is not None else 0)
