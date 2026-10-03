"""Viewer time scaling changes presentation, never the physics timestep."""
import math

def simulation_speed(base=1.,shift=False):
    if not math.isfinite(base) or base<=0: raise ValueError('Simulation speed must be finite and positive')
    return base*(10. if shift else 1.)
