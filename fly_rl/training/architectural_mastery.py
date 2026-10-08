"""Training-only curriculum progression from repeated per-task outcomes."""
import math


class ArchitecturalMastery:
    """Require two disjoint successful rounds covering every training task."""
    def __init__(self, cases, window=8, threshold=.75):
        self.cases=tuple(cases)
        if not self.cases or len(set(self.cases)) != len(self.cases):
            raise ValueError('Training tasks must be nonempty and unique')
        if type(window) is not int or window < 2 or not 0 < threshold <= 1:
            raise ValueError('Invalid mastery criterion')
        self.window=window;self.threshold=threshold
        self.stage_order=(0,1,2,4)
        self.stage_index=0;self.consecutive_rounds=0;self.rounds=[]
        self.pending={case:[] for case in self.cases}

    @property
    def stage(self):return self.stage_order[self.stage_index]

    def record(self, case, success):
        if case not in self.pending or type(success) is not bool:
            raise ValueError('Unknown task or invalid success outcome')
        # Full tasks wait for the slower tasks; extra episodes are not used
        # again to turn overlapping evidence into two successful rounds.
        if len(self.pending[case]) < self.window:
            self.pending[case].append(success)
        if any(len(values)<self.window for values in self.pending.values()):return False
        counts={str(case):sum(values) for case,values in self.pending.items()}
        required=math.ceil(self.window*self.threshold)
        passed=all(count>=required for count in counts.values())
        self.rounds.append(dict(stage=self.stage,goals=counts,episodes_per_task=self.window,
                                required_goals=required,passed=passed))
        self.consecutive_rounds=self.consecutive_rounds+1 if passed else 0
        self.pending={case:[] for case in self.cases}
        advanced=self.consecutive_rounds>=2 and self.stage_index<len(self.stage_order)-1
        if advanced:
            self.stage_index+=1;self.consecutive_rounds=0
        return advanced

    def snapshot(self):
        return dict(kind='adaptive training evidence, not independent validation',
                    stage=self.stage,stage_order=list(self.stage_order),window=self.window,
                    threshold=self.threshold,consecutive_rounds=self.consecutive_rounds,
                    pending={str(case):list(values) for case,values in self.pending.items()},
                    rounds=list(self.rounds))
