"""Keep velocity for motor control, exclude its panorama plane from perception."""
from fly_rl.training.sparse_directional_panorama_policy import SparseDirectionalPanoramicBrainHistory
from fly_rl.simulation.sensors import SENSORS,PANORAMA_COUNT

class DistanceOnlyPanoramicBrainHistory(SparseDirectionalPanoramicBrainHistory):
    def forward_with_attention(self,observations):
        visual=observations.clone()
        visual[...,SENSORS+PANORAMA_COUNT:]=0
        return super().forward_with_attention(visual)
