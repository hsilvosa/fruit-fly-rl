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
SENSOR_V4='sensors-v4-128-distance-128-approach-14-state-deadline'
SENSOR_V5='sensors-v5-v3-plus-589-goal-fan-rays-range24'
FAN_RANGE=24.
FAN_AZIMUTH=np.deg2rad(np.linspace(-75,75,31))
FAN_ELEVATION=np.deg2rad(np.linspace(-45,45,19))
FAN_COUNT=len(FAN_AZIMUTH)*len(FAN_ELEVATION)
FAN_SPEC={'rays':FAN_COUNT,'range':FAN_RANGE,'azimuth_degrees':[-75,75,31],
          'elevation_degrees':[-45,45,19],'center':'observed target bearing; not route or aperture',
          'ordering':'elevation rows, azimuth columns'}
SENSOR_VERSIONS=(SENSOR_VERSION,SENSOR_V3,SENSOR_V4,SENSOR_V5)

def validate_sensor_version(value):
    if value not in SENSOR_VERSIONS: raise ValueError('Unknown sensor version')
    return value


def sensor_names(version):
    validate_sensor_version(version)
    names=SENSOR_NAMES.copy()+(['remaining_time_fraction'] if version==SENSOR_V4 else [])
    if version==SENSOR_V5:
        names+=[f'fan_distance_{i:03d}' for i in range(FAN_COUNT)]+[f'fan_approach_speed_{i:03d}' for i in range(FAN_COUNT)]
    return names

def sensor_count(version):
    return len(sensor_names(version))


def fan_directions(local_target):
    """Synthetic visual scan centered on the already observed target bearing."""
    delta=np.asarray(local_target,dtype=float)
    if delta.shape!=(3,) or not np.isfinite(delta).all():raise ValueError('Finite target bearing required')
    theta=np.arctan2(delta[1],delta[0]);phi=np.arctan2(delta[2],np.linalg.norm(delta[:2]))
    azimuth,elevation=np.meshgrid(theta+FAN_AZIMUTH,np.clip(phi+FAN_ELEVATION,-np.pi/2+.01,np.pi/2-.01))
    return np.column_stack([(np.cos(elevation)*np.cos(azimuth)).ravel(),
                            (np.cos(elevation)*np.sin(azimuth)).ravel(),np.sin(elevation).ravel()])


def ray_count(version):
    validate_sensor_version(version)
    return RAY_COUNT+(FAN_COUNT if version==SENSOR_V5 else 0)
