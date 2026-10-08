"""Full-graph dual reconstruction with repeatable segmented CSR sums."""
import torch
from fly_rl.connectome.repeatable_readout import RepeatableDualActivityBrain, REPEATABLE_DUAL_READOUT

SEGMENTED_DUAL_READOUT = 'neural-projection-dual-repeatable-segmented-v1'

class SegmentedDualActivityBrain(RepeatableDualActivityBrain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readout_version = SEGMENTED_DUAL_READOUT
        self.model_spec = self.model_spec.replace(REPEATABLE_DUAL_READOUT, SEGMENTED_DUAL_READOUT)

    def multiply(self, matrix, dense):
        key = id(matrix)
        if key not in self._csr_cache:
            lengths = matrix.crow_indices()[1:] - matrix.crow_indices()[:-1]
            self._csr_cache[key] = (lengths, matrix.col_indices(), matrix.values())
        lengths, columns, weights = self._csr_cache[key]
        contributions = weights[:, None] * dense[columns]
        return torch.segment_reduce(contributions, reduce='sum', lengths=lengths, axis=0)
