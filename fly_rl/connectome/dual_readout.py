"""Separate contextual map features from literal distances used for braking."""
import torch
from fly_rl.connectome.innovation import MotionStableActivityBrain, MOTION_STABLE_READOUT

DUAL_READOUT = 'neural-projection-dual-map005-distance-clean-v1'
DUAL_FEATURES = 5669


class DualActivityBrain(MotionStableActivityBrain):
    """Advance the same graph once; emit v60 features plus 1,800 clean ranges.

    Both outputs reconstruct previous/current neuron activity through the known
    projection. Extra coordinates are not raw world observations. The original
    3,869-coordinate prefix preserves its exact contextual decoder semantics.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature_count = DUAL_FEATURES
        self.readout_version = DUAL_READOUT
        self.model_spec = self.model_spec.replace(MOTION_STABLE_READOUT, DUAL_READOUT)

    @torch.no_grad()
    def reconstruct_activity(self, previous, current):
        if previous.shape != self.state.shape or current.shape != self.state.shape:
            raise ValueError('Full previous and current neuron states are required')
        drive = torch.atanh((2*current-previous).clamp(-1+1e-6, 1-1e-6))
        drive += self.centering_drive[:, None]
        recurrent = torch.sparse.mm(self.matrix, previous)
        rhs = torch.sparse.mm(self.projection_transpose, torch.cat([drive-recurrent, recurrent], dim=1))
        decoded = torch.cholesky_solve(rhs, self.factor)/self.norm[:, None]
        clean, context = decoded.chunk(2, dim=1)
        mapping = clean+self.recurrent_gain*context
        return torch.cat([mapping, clean[269:2069]], dim=0).T.contiguous().cpu().numpy()
