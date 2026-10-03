"""Versioned sensor ordering shared by the world, reservoir, and recordings."""
import itertools
import numpy as np

base=np.array([v for v in itertools.product([-1,0,1],repeat=3) if v!=(0,0,0)],dtype=float)
base/=np.linalg.norm(base,axis=1,keepdims=True)
i=np.arange(102,dtype=float)
z=1-2*(i+.5)/102
phi=i*np.pi*(3-np.sqrt(5))
extra=np.column_stack([np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z])
DIRECTIONS=np.vstack([base,extra])
RAY_COUNT=128
RAY_RANGE=8.
SENSORS=2*RAY_COUNT+13
SENSOR_VERSION='sensors-v2-128-distance-128-approach-13-state'
SENSOR_NAMES=([f'distance_{i:03d}' for i in range(RAY_COUNT)] +
              [f'approach_speed_{i:03d}' for i in range(RAY_COUNT)] +
              ['target_x','target_y','target_z','target_distance','velocity_x','velocity_y','velocity_z',
               'previous_forward','previous_lateral','previous_vertical','previous_yaw','altitude','yaw_rate'])

SENSOR_V3='sensors-v3-128-distance-128-approach-13-state-room-scales-yaw-rate'
SENSOR_VERSIONS=(SENSOR_VERSION,SENSOR_V3)

def validate_sensor_version(value):
    if value not in SENSOR_VERSIONS: raise ValueError('Unknown sensor version')
    return value
