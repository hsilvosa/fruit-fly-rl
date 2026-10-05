"""Explicit experimental planner selection and complete source provenance."""
import hashlib
import importlib
import inspect
import json
from pathlib import Path
from fly_rl.navigation.observed_map import ObservedMapPolicy

CONTROLLERS = dict(v55=('observed_map', 'ObservedMapController'),
    v56=('goal_margin', 'GoalMarginController'), v57=('cruise', 'CruiseController'),
    v58=('free_margin', 'FreeMarginController'), v59=('speed_margin', 'SpeedMarginController'),
    v60=('adaptive_margin', 'AdaptiveMarginController'))


class VersionedPlannerPolicy(ObservedMapPolicy):
    """Viewer adapter; selecting a version does not train or promote it."""

    def __init__(self, version):
        if version not in CONTROLLERS:
            raise ValueError('Unknown planner version')
        self.version = version
        self.reset()

    def reset(self):
        module, name = CONTROLLERS[self.version]
        self.controller = getattr(importlib.import_module(f'fly_rl.navigation.{module}'), name)()

    def source_files(self):
        paths = {Path(__file__)}
        for kind in type(self.controller).__mro__:
            if kind is not object:
                paths.add(Path(inspect.getfile(kind)))
        return sorted(paths)

    @property
    def specification(self):
        primary = Path(inspect.getfile(type(self.controller)))
        spec = dict(super().specification)
        spec.update(version=inspect.getmodule(type(self.controller)).CONTROLLER_VERSION,
            experimental=self.version != 'v55',
            source_sha256=hashlib.sha256(primary.read_bytes()).hexdigest(),
            sources=[dict(module=f'fly_rl.navigation.{p.stem}',
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
