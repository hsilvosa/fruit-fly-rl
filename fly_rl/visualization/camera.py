"""Independent orbit and free-flight spectator camera geometry."""
import numpy as np

class CameraRig:
    def __init__(self):
        self.mode='orbit';self.target=np.array([6.,6.,2.]);self.distance=19.
        self.yaw=-2.4;self.pitch=.55;self.position=np.array([0.,-4.,7.])
        self.chase_distance=3.
        self.free_yaw=.75;self.free_pitch=-.25

    def pose(self,fly_position=None,fly_rotation=None):
        if self.mode=='chase':
            p=fly_position-fly_rotation@np.array([self.chase_distance,0.,0.])+np.array([0,0,1.5])
            return p,fly_position
        if self.mode=='free':
            direction=np.array([np.cos(self.free_pitch)*np.cos(self.free_yaw),
                np.cos(self.free_pitch)*np.sin(self.free_yaw),np.sin(self.free_pitch)])
            return self.position.copy(),self.position+direction
        offset=self.distance*np.array([np.cos(self.pitch)*np.cos(self.yaw),
            np.cos(self.pitch)*np.sin(self.yaw),np.sin(self.pitch)])
        return self.target+offset,self.target.copy()

    def cycle(self,fly_position,fly_rotation):
        old_position,old_target=self.pose(fly_position,fly_rotation)
        self.mode={'orbit':'chase','chase':'free','free':'orbit'}[self.mode]
        if self.mode=='free':
            self.position=old_position.copy();d=old_target-old_position
            self.free_yaw=float(np.arctan2(d[1],d[0]))
            self.free_pitch=float(np.arctan2(d[2],np.linalg.norm(d[:2])))

    def rotate(self,dx,dy):
        if self.mode=='free':
            self.free_yaw-=dx*2.5;self.free_pitch=float(np.clip(self.free_pitch+dy*2.5,-1.5,1.5))
        elif self.mode=='orbit':
            self.yaw-=dx*2.5;self.pitch=float(np.clip(self.pitch+dy*2.5,-1.3,1.5))

    def pan(self,dx,dy):
        right=np.array([-np.sin(self.yaw),np.cos(self.yaw),0.])
        self.target+=(-dx*right+np.array([0.,0.,-dy]))*self.distance*.7

    def zoom(self,direction,fast=False):
        if self.mode=='free': self.move(direction,0,0,.15,fast)
        elif self.mode=='chase': self.chase_distance=float(np.clip(self.chase_distance*np.exp(-direction*.12*(4 if fast else 1)),.5,15.))
        else: self.distance=float(np.clip(self.distance*np.exp(-direction*.12*(4 if fast else 1)),1.,65.))

    def move(self,forward,right,up,dt,fast=False):
        if self.mode!='free': return
        direction=np.array([np.cos(self.free_pitch)*np.cos(self.free_yaw),
            np.cos(self.free_pitch)*np.sin(self.free_yaw),np.sin(self.free_pitch)])
        lateral=np.array([-np.sin(self.free_yaw),np.cos(self.free_yaw),0.])
        self.position+=(direction*forward+lateral*right+np.array([0,0,up]))*dt*(40 if fast else 4)

    def focus(self,position):
        self.mode='orbit';self.target=np.asarray(position).copy();self.distance=4.
