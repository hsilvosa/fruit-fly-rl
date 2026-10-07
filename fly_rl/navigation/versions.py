"""Public controller revisions and permanent aliases for recorded experiments."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ControllerRevision:
    number: str
    legacy: str
    label: str
    experimental: bool = True

    @property
    def name(self):
        return f'planner-{self.number}'


REVISIONS = (
    ControllerRevision('1.0', 'v55', 'baseline', False),
    ControllerRevision('1.0.1-exp.1', 'v56', 'goal-margin correction'),
    ControllerRevision('1.1-exp.1', 'v57', 'higher cruise speed'),
    ControllerRevision('1.1-exp.2', 'v58', 'known-free margin traversal'),
    ControllerRevision('1.1-exp.3', 'v59', 'combined speed and clearance'),
    ControllerRevision('1.1', 'v60', 'adaptive clearance'),
    ControllerRevision('1.2-exp.1', 'v61', 'clean ranges'),
    ControllerRevision('1.2-exp.2', 'v62', 'persistent route'),
    ControllerRevision('1.2-exp.3', 'v63', 'ray-consistent mapping'),
    ControllerRevision('1.2-exp.4', 'v64', 'momentum braking'),
    ControllerRevision('1.2', 'v65', 'dual readout'),
    ControllerRevision('1.3-exp.1', 'room-aware-exp1', 'room-aware committed references'),
    ControllerRevision('1.3-exp.2', 'frontier-cost-exp1', 'observed-free route preference'),
    ControllerRevision('1.3-exp.3', 'portal-reference-exp1', 'observed opening approach and crossing'),
    ControllerRevision('1.3-exp.4', 'portal-reference-exp2', 'sample-aware opening commitment'),
    ControllerRevision('1.3-exp.5', 'portal-reference-exp3', 'multiple observed wall candidates'),
    ControllerRevision('1.3-exp.6', 'portal-reference-exp4', 'beacon-aligned observed surfaces'),
    ControllerRevision('1.3-exp.7', 'portal-reference-exp5', 'distance-aware wall span'),
    ControllerRevision('1.3-exp.8', 'portal-reference-exp6', 'clean-range opening map'),
    ControllerRevision('1.3-exp.9', 'portal-reference-exp7', 'bounded faster opening flight'),
    ControllerRevision('1.3-exp.10', 'portal-reference-exp8', 'stalled-reference recovery'),
    ControllerRevision('1.3-exp.11', 'portal-reference-exp9', 'opening-center refinement'),
    ControllerRevision('1.3-exp.12', 'portal-reference-exp10', 'goal-priority opening planning'),
    ControllerRevision('1.3-exp.13', 'portal-reference-exp11', 'finer occupancy grid'),
    ControllerRevision('1.3-exp.14', 'portal-reference-exp12', 'supported surface fallback and close goal handover'),
    ControllerRevision('1.3-exp.15', 'portal-reference-exp13', 'bounded confined cruise and close goal handover'),
    ControllerRevision('1.3-exp.16', 'portal-reference-exp14', 'nonprogress visit pressure and close goal handover'),
    ControllerRevision('1.3-exp.17', 'portal-reference-exp15', 'clean initial-beacon surface alignment'),
    ControllerRevision('1.3-exp.18', 'portal-reference-exp16', 'observed opening clearance reference'),
    ControllerRevision('1.3-exp.19', 'portal-reference-exp17', 'neural ray visible-goal handover'),
    ControllerRevision('1.3-exp.20', 'portal-reference-exp18', 'stable neural visible-goal handover'),
    ControllerRevision('1.3-exp.21', 'portal-reference-exp19', 'committed neural visible-goal handover'),
    ControllerRevision('1.3-exp.22', 'repeatable-goal-exp1', 'repeatable full-graph visible-goal execution'),
    ControllerRevision('1.3-exp.23', 'segmented-goal-exp1', 'repeatable segmented full-graph visible-goal execution'),
    ControllerRevision('1.3-exp.24', 'wall-survey-exp1', 'observed blocking-wall opening survey'),
    ControllerRevision('1.3-exp.25', 'clearance-goal-exp1', 'near-body clearance and crossing-aware goal handover'),
    ControllerRevision('1.3-exp.26', 'distant-opening-exp1', 'extended observable opening range with near-choice preservation'),
    ControllerRevision('1.3-exp.27', 'progress-wall-scan-exp1', 'bounded observed-wall scan after longitudinal nonprogress'),
)
DEFAULT_REVISION = 'planner-1.0'
PUBLIC_VERSIONS = tuple(revision.name for revision in REVISIONS)
ALIASES = {alias: revision for revision in REVISIONS
           for alias in (revision.name, revision.number, revision.legacy)}


def revision(value):
    try:
        return ALIASES[value]
    except (KeyError, TypeError):
        raise ValueError(f'Unknown controller revision: {value}') from None


def public_version(value):
    return revision(value).name


def legacy_version(value):
    return revision(value).legacy


def catalog():
    return [dict(name=entry.name, **asdict(entry)) for entry in REVISIONS]
