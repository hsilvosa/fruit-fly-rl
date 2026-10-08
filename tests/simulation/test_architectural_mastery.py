import pytest
from fly_rl.training.architectural_mastery import ArchitecturalMastery


def round_(mastery, first=True, second=True):
    changes=[]
    for case,success in [('office',first),('street',second)]:
        for _ in range(mastery.window):changes.append(mastery.record(case,success))
    return any(changes)


def test_requires_complete_disjoint_rounds_for_every_task():
    mastery=ArchitecturalMastery(['office','street'],window=2)
    for _ in range(20):assert not mastery.record('office',True)
    assert mastery.stage==0
    for _ in range(2):assert not mastery.record('street',True)
    assert mastery.consecutive_rounds==1 and mastery.stage==0
    assert round_(mastery)
    assert mastery.stage==1 and mastery.consecutive_rounds==0


def test_failed_round_resets_gate_and_original_stage_is_terminal():
    mastery=ArchitecturalMastery(['office','street'],window=2)
    assert not round_(mastery)
    assert not round_(mastery,second=False)
    assert mastery.consecutive_rounds==0
    for stage in (1,2,4):
        assert not round_(mastery)
        assert round_(mastery)
        assert mastery.stage==stage
    assert not round_(mastery)
    assert not round_(mastery)
    assert mastery.stage==4
    assert 'not independent validation' in mastery.snapshot()['kind']


def test_unknown_case_and_invalid_success_are_rejected():
    mastery=ArchitecturalMastery(['office'])
    with pytest.raises(ValueError):mastery.record('unknown',True)
    with pytest.raises(ValueError):mastery.record('office',1)
