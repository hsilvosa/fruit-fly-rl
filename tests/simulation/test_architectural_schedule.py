import pytest
from fly_rl.training.architectural_mastery import ArchitecturalMastery
from fly_rl.training.architectural_schedule import MasteryTaskScheduler

def test_full_windows_are_skipped_without_dropping_tasks():
    cases=('a','b','c'); gate=ArchitecturalMastery(cases,window=2)
    scheduler=MasteryTaskScheduler(cases)
    gate.record('a',True);gate.record('a',True)
    assert scheduler.select(gate)=='b'
    assert scheduler.select(gate)=='c'
    assert scheduler.select(gate)=='b'
    for case in ('b','c'):
        gate.record(case,True);gate.record(case,True)
    assert len(gate.rounds)==1
    assert {scheduler.select(gate) for _ in cases}==set(cases)

def test_missing_task_contract_is_rejected():
    with pytest.raises(ValueError,match='disagree'):
        MasteryTaskScheduler(('a',)).select(ArchitecturalMastery(('b',)))
