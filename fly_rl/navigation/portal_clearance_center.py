"""Select visible opening points with clearance from observed surface endpoints."""
import numpy as np
from scipy.spatial import cKDTree
from fly_rl.navigation.portal_center_refinement import RefiningPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp16'

class ClearancePortalController(RefiningPortalController):
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
            if np.ptp(span)<8 or np.ptp(points[keep][inliers,2])<min(self.room_size[2]*.65, distance*3.) or not .5<distance<6:continue
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
        if len(candidates)<1:return None
        coordinates=np.column_stack([candidates[:,:2]@tangent,candidates[:,2]])
        parent=list(range(len(candidates)))
        def root(i):
            while parent[i]!=i:
                parent[i]=parent[parent[i]];i=parent[i]
            return i
        spacing=min(3.2,max(.9,.35+.17*float(np.median(expected[visible][usable]))))
        for i,j in cKDTree(coordinates).query_pairs(spacing):parent[root(i)]=root(j)
        groups={}
        for i in range(len(candidates)):groups.setdefault(root(i),[]).append(i)
        surface=points[keep][np.abs(xy@normal-distance)<.12]
        surface_coordinates=np.column_stack([surface[:,:2]@tangent,surface[:,2]])
        wall_tree=cKDTree(surface_coordinates)
        options=[]
        for members in groups.values():
            if len(members)<1:continue
            cluster=candidates[members]
            coordinates=np.column_stack([cluster[:,:2]@tangent,cluster[:,2]])
            clearance=wall_tree.query(coordinates)[0]
            center=cluster[int(np.argmax(clearance))]+self.position
            center[:2]+=normal*(distance-(center-self.position)[:2]@normal)
            direction=np.r_[normal,0.]
            if any(direction@old_normal>.95 and abs((center-old_center)@direction)<1.5 for old_center,old_normal in self.completed_planes):continue
            approach=center-direction*1.1
            score=np.linalg.norm(approach-self.position)+.3*np.linalg.norm(center-self.initial_goal)
            options.append((score,center,direction,len(members)))
        if not options:return None
        _,center,normal,count=min(options,key=lambda item:item[0])
        return dict(center=center,normal=normal,ray_support=count)
