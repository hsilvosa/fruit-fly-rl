"""Training task selection and validated restoration; never flight actions."""
from fly_rl.training.architectural_mastery import ArchitecturalMastery
from fly_rl.training.architectural_schedule import MasteryTaskScheduler


def restore_mastery(cases, snapshot):
    """Reconstruct the gate by replaying complete rounds and pending outcomes."""
    gate = ArchitecturalMastery(cases, window=snapshot['window'], threshold=snapshot['threshold'])
    if snapshot['stage_order'] != list(gate.stage_order):
        raise ValueError('Curriculum stage order mismatch')
    keys = {str(case) for case in gate.cases}
    for recorded in snapshot['rounds']:
        if recorded['stage'] != gate.stage or set(recorded['goals']) != keys:
            raise ValueError('Invalid saved mastery round')
        for case in gate.cases:
            count = recorded['goals'][str(case)]
            if type(count) is not int or not 0 <= count <= gate.window:
                raise ValueError('Invalid saved success count')
            for index in range(gate.window):
                gate.record(case, index < count)
        if gate.rounds[-1] != recorded:
            raise ValueError('Saved round disagrees with criterion')
    if gate.stage != snapshot['stage'] or gate.consecutive_rounds != snapshot['consecutive_rounds']:
        raise ValueError('Saved curriculum progress is inconsistent')
    pending = snapshot['pending']
    if set(pending) != keys:
        raise ValueError('Saved training tasks disagree')
    if all(len(values) == gate.window for values in pending.values()):
        raise ValueError('Completed pending round was not finalized')
    for case in gate.cases:
        values = pending[str(case)]
        if len(values) > gate.window or any(type(value) is not bool for value in values):
            raise ValueError('Invalid pending outcomes')
        gate.pending[case] = list(values)
    return gate


class MixedTaskScheduler:
    """Alternate lesson chunks and original-goal chunks over training cases only."""
    def __init__(self, cases):
        self.cases = tuple(cases)
        self.lessons = MasteryTaskScheduler(self.cases)
        self.original_cursor = 0
        self.chunk = 0

    def select(self, mastery):
        if tuple(mastery.cases) != self.cases:
            raise ValueError('Training task contract mismatch')
        original = mastery.stage == 4 or self.chunk % 2 == 1
        self.chunk += 1
        if original:
            case = self.cases[self.original_cursor]
            self.original_cursor = (self.original_cursor + 1) % len(self.cases)
            return 4, case
        return mastery.stage, self.lessons.select(mastery)
