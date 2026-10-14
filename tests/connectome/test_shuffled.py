import numpy as np
from scipy import sparse

from fly_rl.connectome.shuffled import ShuffledBrain, shuffle_targets


def example_matrix(n=1500, density=0.004, seed=0):
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], n)  # one sign per source neuron, as in the real graph
    matrix = sparse.random(n, n, density=density, random_state=seed, format='csr')
    matrix.data = np.abs(matrix.data).astype(np.float32) * 0.9
    return (matrix @ sparse.diags(signs)).tocsr().astype(np.float32)


def test_shuffle_keeps_degrees_and_source_weights():
    matrix = example_matrix()
    shuffled = shuffle_targets(matrix, 3)
    assert shuffled.shape == matrix.shape
    original_in = np.diff(matrix.indptr)
    # In-degree can only shrink where the shuffle created duplicate pairs (summed).
    assert (np.diff(shuffled.indptr) <= original_in).all()
    assert abs(shuffled.nnz - matrix.nnz) <= 0.01 * matrix.nnz
    out_original = np.asarray(abs(matrix).sum(axis=0)).ravel()
    out_shuffled = np.asarray(abs(shuffled).sum(axis=0)).ravel()
    np.testing.assert_allclose(out_original, out_shuffled, rtol=1e-5, atol=1e-6)
    # Dale's law: the sign of every source neuron is unchanged.
    sign_original = np.sign(np.asarray(matrix.sum(axis=0)).ravel())
    sign_shuffled = np.sign(np.asarray(shuffled.sum(axis=0)).ravel())
    np.testing.assert_array_equal(sign_original, sign_shuffled)


def test_shuffle_changes_the_wiring_and_is_deterministic():
    matrix = example_matrix()
    a, b, c = shuffle_targets(matrix, 3), shuffle_targets(matrix, 3), shuffle_targets(matrix, 4)
    assert (a != b).nnz == 0
    assert (a != c).nnz > 0
    assert (a != matrix).nnz > 0.5 * matrix.nnz


def test_shuffled_brain_has_distinct_fingerprint_and_runs():
    matrix = example_matrix(n=300, density=0.02)
    brain = ShuffledBrain(seed=1, batch=2, device='cpu', source_matrix=matrix)
    other = ShuffledBrain(seed=2, batch=2, device='cpu', source_matrix=matrix)
    assert brain.fingerprint.startswith('shuffled-targets-seed1-')
    assert brain.fingerprint != other.fingerprint
    assert brain.fingerprint.endswith(f':{brain.model_spec}')
    features = brain.step(np.zeros((2, brain.sensor_count), dtype=np.float32) + 0.3)
    assert features.shape == (2, 256) and np.isfinite(features).all()
