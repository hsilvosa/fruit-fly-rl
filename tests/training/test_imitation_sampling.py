import numpy as np
from fly_rl.training.guided_learning import imitation_indices

def test_balancing_preserves_turn_vertical_and_startup_examples():
    rng=np.random.default_rng(42)
    turns=np.arange(10);vertical=np.arange(10,20);starts=np.arange(20,30)
    selected=imitation_indices(40,32,rng,turns,vertical,starts)
    assert np.isin(selected[:8],turns).all()
    assert np.isin(selected[8:16],vertical).all()
    assert np.isin(selected[16:24],starts).all()
    assert ((selected>=0)&(selected<40)).all()

def test_empty_strata_keep_uniform_finite_indices():
    empty=np.array([],dtype=int)
    indices=imitation_indices(7,32,np.random.default_rng(3),empty,empty,empty)
    expected=np.random.default_rng(3).integers(7,size=32)
    assert np.array_equal(indices,expected)

def test_legacy_turn_sampling_remains_identical():
    turns=np.arange(5)
    expected_rng=np.random.default_rng(42)
    expected=expected_rng.integers(20,size=32)
    expected[:16]=expected_rng.choice(turns,16)
    actual=imitation_indices(20,32,np.random.default_rng(42),turns)
    assert np.array_equal(actual,expected)
