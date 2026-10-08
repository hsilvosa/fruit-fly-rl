import copy
import pytest
from fly_rl.training.architectural_mastery import ArchitecturalMastery
from fly_rl.training.architectural_mixed_schedule import MixedTaskScheduler, restore_mastery


def test_restore_preserves_progress_and_disjoint_pending_windows():
    cases=(('office',0),('street',0))
    gate=ArchitecturalMastery(cases,window=2)
    for _ in range(2):
        for case in cases:
            for _ in range(2):gate.record(case,True)
    gate.record(cases[0],False)
    restored=restore_mastery(cases,gate.snapshot())
    assert restored.snapshot()==gate.snapshot()
    assert restored.stage==1
    bad=copy.deepcopy(gate.snapshot());bad['stage']=2
    with pytest.raises(ValueError):restore_mastery(cases,bad)


def test_original_tasks_alternate_without_consuming_lesson_windows():
    cases=(('office',0),('street',0))
    gate=ArchitecturalMastery(cases,window=2)
    scheduler=MixedTaskScheduler(cases)
    before=gate.snapshot()
    selected=[scheduler.select(gate) for _ in range(4)]
    assert selected==[(0,cases[0]),(4,cases[0]),(0,cases[1]),(4,cases[1])]
    assert gate.snapshot()==before


def test_original_stage_keeps_all_tasks_and_never_shortens_goals():
    cases=('a','b');gate=ArchitecturalMastery(cases,window=2)
    for _ in range(6):
        for case in cases:
            for _ in range(2):gate.record(case,True)
    assert gate.stage==4
    scheduler=MixedTaskScheduler(cases)
    assert [scheduler.select(gate) for _ in range(4)]==[(4,'a'),(4,'b'),(4,'a'),(4,'b')]
