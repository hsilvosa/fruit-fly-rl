"""Edge-shuffled connectome: a no-connectome control that keeps everything except the biological wiring.

Rows of the sparse matrix are targets and columns are sources (update = tanh(matrix @ state + input)). The control reassigns the
target of every edge by one global permutation of the edge list. For each source neuron the out-degree and the weights (and so the
sign, Dale's law) are unchanged. Each target keeps its in-degree. Neuron count, edge count, weight distribution, input mapping and
output pooling are the same as in the real brain, so only who connects to whom changes. Duplicate (target, source) pairs created by
the shuffle are summed (about 0.3 percent of the edges, concentrated on high-degree neurons). The result is deterministic for a given seed and is never stored.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import sparse

from fly_rl.connectome.brain import Brain


def shuffle_targets(matrix, seed):
    """Return a CSR matrix with the same shape and edge set per source, but permuted targets."""
    coo = sparse.coo_matrix(matrix)
    permutation = np.random.default_rng(seed).permutation(coo.nnz)
    shuffled = sparse.coo_matrix((coo.data, (coo.row[permutation], coo.col)), shape=coo.shape)
    return shuffled.tocsr()  # sums duplicate (target, source) pairs


class ShuffledBrain(Brain):
    """Fixed reservoir with the connectome's edge targets shuffled. Same interface and readout as `Brain`."""

    def __init__(self, seed=1, data='data', batch=1, device='cuda', sensor_version=None, source_matrix=None):
        if source_matrix is None:
            source_matrix = sparse.load_npz(Path(data) / 'processed' / 'brain.npz')
            real = json.loads((Path(data) / 'processed' / 'audit.json').read_text())
            dataset, real_fingerprint = real.get('dataset', 'MaleCNS v1.0'), real['fingerprint']
        else:
            dataset, real_fingerprint = 'test-only', 'test-only'
        shuffled = shuffle_targets(source_matrix, seed)
        super().__init__(data, batch, device, matrix=shuffled, sensor_version=sensor_version)
        digest = hashlib.sha256(shuffled.indices.tobytes() + shuffled.indptr.tobytes()).hexdigest()[:16]
        self.shuffle_seed = seed
        self.audit = {'dataset': dataset, 'annotated_neurons': shuffled.shape[0], 'edges': int(shuffled.nnz),
                      'fingerprint': f'shuffled-targets-seed{seed}-{digest}-from-{real_fingerprint[:12]}'}
