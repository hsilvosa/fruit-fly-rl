"""Coordinated simplified flight; no wing aerodynamics are claimed."""
import numpy as np
VERSION='coordinated-v1'

def advance(world,action,dt):
    desired_rate=1.8*action[3]+.8*action[1]
    world.yaw_rate+=min(1.,dt*5.)*(desired_rate-world.yaw_rate)
    world.yaw=(world.yaw+world.yaw_rate*dt+np.pi)%(2*np.pi)-np.pi
    rotation=world.rotation();local=world.velocity@rotation
    thrust=np.array([(3. if action[0]>=0 else 1.2)*action[0],.35*action[1],2.5*action[2]])
    local+=(thrust-np.array([.6,2.8,.8])*local)*dt
    world.velocity=rotation@local
    world.bank+=min(1.,dt*6.)*(np.clip(-.3*action[1]-.12*world.yaw_rate,-.55,.55)-world.bank)
    horizontal=max(np.linalg.norm(world.velocity[:2]),.2)
    world.pitch+=min(1.,dt*6.)*(np.clip(np.arctan2(world.velocity[2],horizontal),-.6,.6)-world.pitch)
