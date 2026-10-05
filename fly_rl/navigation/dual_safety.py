"""Experimental v65: retain v60 mapping and use clean ranges for flight safety."""
import numpy as np
from fly_rl.navigation.momentum_guard import MomentumGuardController
from fly_rl.connectome.dual_readout import DualActivityBrain, DUAL_READOUT, DUAL_FEATURES

CONTROLLER_VERSION = 'observed-neuronal-map-v65-dual-safety'
READOUT_VERSION = DUAL_READOUT
READOUT_MODULE = 'fly_rl.connectome.dual_readout'
READOUT_CLASS = DualActivityBrain
FEATURE_COUNT = DUAL_FEATURES


class DualSafetyController(MomentumGuardController):
    """Mapping and safety have declared, separate neural feature coordinates."""

    def action(self, features):
        features = np.asarray(features)
        if features.ndim != 2 or features.shape[-1] != DUAL_FEATURES or not np.isfinite(features).all():
            raise ValueError('Dual safety requires finite 5,669-coordinate neural history')
        self.mapping_values = features[-1, :3869].copy()
        braking = features[:, :3869].copy()
        braking[:, 269:2069] = features[:, 3869:5669]
        result = super().action(braking)
        self.debug.update(mapping_ranges='context005', braking_ranges='clean-neural',
                          feature_count=DUAL_FEATURES)
        return result

    def integrate(self, values):
        super().integrate(self.mapping_values)
