"""Explicit experimental planner selection and complete source provenance."""
import hashlib
import importlib
import inspect
import json
import numpy as np
from pathlib import Path
from fly_rl.navigation.observed_map import ObservedMapPolicy
from fly_rl.navigation.versions import revision

CONTROLLERS = dict(v55=('observed_map', 'ObservedMapController'),
    v56=('goal_margin', 'GoalMarginController'), v57=('cruise', 'CruiseController'),
    v58=('free_margin', 'FreeMarginController'), v59=('speed_margin', 'SpeedMarginController'),
    v60=('adaptive_margin', 'AdaptiveMarginController'),
    v61=('distance_stable', 'DistanceStableController'),
    v62=('persistent_route', 'PersistentRouteController'),
    v63=('ray_consistent', 'RayConsistentController'),
    v64=('momentum_guard', 'MomentumGuardController'),
    v65=('dual_safety', 'DualSafetyController'),
    **{'room-aware-exp1': ('room_aware', 'RoomAwareController'),
       'frontier-cost-exp1': ('frontier_cost', 'FrontierCostController'),
       'portal-reference-exp1': ('portal_reference', 'PortalReferenceController'),
       'portal-reference-exp2': ('portal_reference_refined', 'RefinedPortalController'),
       'portal-reference-exp3': ('portal_multi_plane', 'MultiPlanePortalController'),
       'portal-reference-exp4': ('portal_axis', 'AxisPortalController'),
       'portal-reference-exp5': ('portal_near_wall', 'NearWallPortalController'),
       'portal-reference-exp6': ('portal_clean_map', 'CleanMapPortalController'),
       'portal-reference-exp7': ('portal_fast', 'FastPortalController'),
       'portal-reference-exp8': ('portal_recovery', 'RecoveryPortalController'),
       'portal-reference-exp9': ('portal_center_refinement', 'RefiningPortalController'),
       'portal-reference-exp10': ('portal_goal_priority', 'GoalPriorityPortalController'),
       'portal-reference-exp11': ('portal_fine_grid', 'FineGridPortalController')})


class VersionedPlannerPolicy(ObservedMapPolicy):
    """Viewer adapter; selecting a version does not train or promote it."""

    def __init__(self, version, map_profile='large'):
        self.revision = revision(version)
        self.version = self.revision.legacy
        self.map_profile = map_profile
        self.reset()

    def reset(self):
        module, name = CONTROLLERS[self.version]
        implementation = importlib.import_module(f'fly_rl.navigation.{module}')
        supported = getattr(implementation, 'SUPPORTED_PROFILES', ('large',))
        if self.map_profile not in supported:
            raise ValueError('Controller does not support the selected room profile')
        constructor = getattr(implementation, name)
        if hasattr(implementation, 'SUPPORTED_PROFILES'):
            from fly_rl.simulation.map_profiles import resolve_profile
            self.controller = constructor(resolve_profile(self.map_profile).room_size)
        else:
            self.controller = constructor()

    def predict(self, features, deterministic=True):
        features = np.asarray(features)
        module = inspect.getmodule(type(self.controller))
        width = getattr(module, 'FEATURE_COUNT', 3869)
        if features.shape != (1, 9, width) or not np.isfinite(features).all():
            raise ValueError('Planner requires its declared finite nine-frame neural observation')
        return self.controller.action(features[0])[None], None

    def source_files(self):
        paths = {Path(__file__), Path(inspect.getfile(revision))}
        for kind in type(self.controller).__mro__:
            if kind is not object:
                paths.add(Path(inspect.getfile(kind)))
        module=inspect.getmodule(type(self.controller))
        if hasattr(module, 'READOUT_MODULE'):
            paths.add(Path(inspect.getfile(importlib.import_module(module.READOUT_MODULE))))
        if hasattr(module, 'READOUT_CLASS'):
            for kind in module.READOUT_CLASS.__mro__:
                if kind is not object:
                    paths.add(Path(inspect.getfile(kind)))
        return sorted(paths)

    @property
    def specification(self):
        primary = Path(inspect.getfile(type(self.controller)))
        module = inspect.getmodule(type(self.controller))
        spec = dict(super().specification)
        root = Path(__file__).resolve().parents[2]
        spec.update(version=module.CONTROLLER_VERSION,
            controller_version=self.revision.name,
            controller_label=self.revision.label,
            legacy_alias=self.revision.legacy,
            readout=getattr(module, 'READOUT_VERSION', spec['readout']),
            experimental=self.version != 'v55',
            feature_count=getattr(module, 'FEATURE_COUNT', 3869),
            room_size=list(getattr(self.controller, 'room_size', [48,48,16])),
            map_profile=self.map_profile,
            source_sha256=hashlib.sha256(primary.read_bytes()).hexdigest(),
            sources=[dict(module='.'.join(p.resolve().relative_to(root).with_suffix('').parts),
                archive_file=f'controller-{p.stem}.py',
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in self.source_files()])
        return spec

    def archive_sources(self, directory):
        directory = Path(directory)
        primary = Path(inspect.getfile(type(self.controller)))
        (directory/'controller.py').write_bytes(primary.read_bytes())
        for path in self.source_files():
            (directory/f'controller-{path.stem}.py').write_bytes(path.read_bytes())
        (directory/'controller.json').write_text(json.dumps(self.specification, indent=2)+'\n', encoding='utf-8')
