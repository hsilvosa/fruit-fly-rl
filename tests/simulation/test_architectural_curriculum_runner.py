import importlib.util
from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from fly_rl.training.architectural_mastery import ArchitecturalMastery

spec=importlib.util.spec_from_file_location('curriculum_runner',Path(__file__).parents[2]/'scripts/train_architectural_curriculum.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def test_old_stage_episodes_do_not_enter_new_stage(tmp_path):
    env=SimpleNamespace(curriculum_stage=0,architectural_scene='office-floor',architectural_situation=0)
    gate=ArchitecturalMastery([('office-floor',0)],window=2,threshold=1)
    callback=runner.Telemetry(tmp_path,{},0,gate)
    callback.model=SimpleNamespace(get_env=lambda:env)
    callback.num_timesteps=1
    callback.locals={'infos':[dict(episode={'r':20,'l':10},success=True,collision=False,truncated=False)]}
    for _ in range(4): callback._on_step()
    assert gate.stage==1
    callback._on_step()
    assert gate.pending[('office-floor',0)]==[]
    env.curriculum_stage=1
    callback._on_step()
    assert gate.pending[('office-floor',0)]==[True]
    rows=[json.loads(x) for x in (tmp_path/'episodes.jsonl').read_text().splitlines()]
    assert [r['curriculum_stage'] for r in rows]==[0,0,0,0,0,1]

def test_validation_refuses_lesson_targets():
    with pytest.raises(ValueError,match='original goals'):
        runner.evaluate(None,SimpleNamespace(curriculum_stage=0),[])
