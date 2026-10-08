"""Restrict architectural escapes to blocked, planned portal crossings."""
from pathlib import Path
import hashlib
from fly_rl.navigation.architectural_recovery import EscapeArchitecturalController, EscapeArchitecturalPolicy


class PortalEscapeArchitecturalController(EscapeArchitecturalController):
    def choose_escape(self):
        if not self.debug.get('found') or self.portal_phase != 'cross':
            return None
        return super().choose_escape()


class PortalEscapeArchitecturalPolicy(EscapeArchitecturalPolicy):
    def reset(self):
        self.controller = PortalEscapeArchitecturalController(self.room_size)

    @property
    def specification(self):
        result = dict(super().specification)
        result.update(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      controller_version='planner-1.4-exp.3',
                      version='observed-neuronal-map-architecture-portal-escape-exp1')
        return result

    def source_files(self):
        return sorted(set(super().source_files()) | {Path(__file__)})
