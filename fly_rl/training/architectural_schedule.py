"""Select training tasks with incomplete mastery windows; no action control."""

class MasteryTaskScheduler:
    def __init__(self, cases):
        self.cases=tuple(cases)
        if not self.cases or len(set(self.cases))!=len(self.cases):
            raise ValueError('Tasks must be nonempty and unique')
        self.cursor=0

    def select(self, mastery):
        if tuple(mastery.cases)!=self.cases:
            raise ValueError('Scheduler and mastery tasks disagree')
        # Do not spend a whole cycle on tasks whose windows are already full.
        for offset in range(len(self.cases)):
            index=(self.cursor+offset)%len(self.cases)
            case=self.cases[index]
            if len(mastery.pending[case])<mastery.window:
                self.cursor=(index+1)%len(self.cases)
                return case
        raise RuntimeError('All windows full without mastery round completion')
