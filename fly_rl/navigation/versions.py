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
