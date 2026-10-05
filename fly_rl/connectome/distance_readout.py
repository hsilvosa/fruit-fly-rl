"""Keep recurrent context out of channels interpreted as physical distances."""
from fly_rl.connectome.innovation import MotionStableActivityBrain, MOTION_STABLE_READOUT

DISTANCE_STABLE_READOUT = 'neural-projection-distance-stable-speed005-v1'


class DistanceStableActivityBrain(MotionStableActivityBrain):
    """Decode ranges from full neural states; retain context in panoramic speeds.

    All neurons and edges still advance. Known projection and recurrent-drive
    subtraction make this an engineered information bound, not biological vision.
    Reconstruction reads previous/current activity, never raw sensor values.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recurrent_gain[269:2069] = 0
        self.readout_version = DISTANCE_STABLE_READOUT
        self.model_spec = self.model_spec.replace(MOTION_STABLE_READOUT, DISTANCE_STABLE_READOUT)
