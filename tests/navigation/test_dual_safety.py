"""Map and braking ranges cannot be silently substituted for one another."""
import numpy as np
import pytest
from fly_rl.navigation.dual_safety import DualSafetyController
from fly_rl.navigation.adaptive_margin import AdaptiveMarginController
from fly_rl.navigation.registry import VersionedPlannerPolicy


def test_mapping_uses_original_contextual_coordinates_without_mutating_input():
    c=DualSafetyController();reference=AdaptiveMarginController()
    c.position[2]=reference.position[2]=6.;c.tick=1;c.tight=False
    seen=[]
    def update(values):
        seen.append(values.copy())
        return np.array([20.,0.,6.])
    c.update=update
    c.local_goal=np.array([20.,0.,0.]);c.route=[np.array([3.,0.,6.])]
    c.target=lambda:np.array([3.,0.,0.]);c.plan=lambda goal:None
    values=np.zeros((9,5669),np.float32);values[:, :128]=1
    values[:,269:2069]=.6;values[:,3869:]=.2;before=values.copy()
    c.action(values);reference.integrate(values[-1,:3869])
    np.testing.assert_equal(c.evidence,reference.evidence)
    np.testing.assert_equal(seen[0][269:2069],values[-1,3869:])
    np.testing.assert_equal(values,before)
    assert c.debug['mapping_ranges']=='context005' and c.debug['braking_ranges']=='clean-neural'


def test_policy_declares_and_checks_dual_feature_width():
    policy=VersionedPlannerPolicy('v65')
    assert policy.specification['feature_count']==5669
    policy.controller.action=lambda values:np.zeros(4,np.float32)
    policy.predict(np.zeros((1,9,5669),np.float32))
    with pytest.raises(ValueError):policy.predict(np.zeros((1,9,3869),np.float32))
    controller=DualSafetyController()
    with pytest.raises(ValueError):
        controller.action(np.zeros((9,3869)))
