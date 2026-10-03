import json
import pytest
from fly_rl.training.sensor_comparison import freeze_sensor_winner
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.simulation.sensors import SENSOR_VERSION,SENSOR_V3
from test_seed_selection import experiment


def groups(tmp_path):
    result=[]
    for label,version,score in [('v2',SENSOR_VERSION,.7),('v3',SENSOR_V3,.8)]:
        members=[]
        for seed in [42,73]:
            p=experiment(tmp_path/f'{label}-{seed}',seed,score)
            file=p/'selection.json';frozen=json.loads(file.read_text());frozen['evaluation_configuration']={'sensor_version':version,'route_metrics':True};file.write_text(json.dumps(frozen));members.append(p)
        group=tmp_path/f'{label}-selected';select_experiment(members,group);result.append(group)
    return result


def test_sensor_winner_uses_only_validation_and_balanced_declared_budgets(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path);members=groups(tmp_path)
    winner=freeze_sensor_winner(members,tmp_path/'winner')
    assert winner['selected_sensor_version']==SENSOR_V3
    assert winner['training']['added_transitions']==262144 and not winner['final_test_evaluated']
    assert len(winner['sensor_comparison'])==2


def test_comparison_rejects_unequal_budgets_and_different_evaluation(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path);members=groups(tmp_path)
    file=members[0]/'experiment.json';state=json.loads(file.read_text());state['seed_experiments'][0]['added_transitions']=1;file.write_text(json.dumps(state))
    with pytest.raises(ValueError,match='equal seed budgets'):freeze_sensor_winner(members,tmp_path/'wrong')
    assert not (tmp_path/'wrong').exists()


def test_declared_fresh_budget_is_used_for_selection(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path);members=groups(tmp_path)
    for group in members:
        file=group/'experiment.json';state=json.loads(file.read_text())
        for member in state['seed_experiments']:member['added_transitions']=131072
        file.write_text(json.dumps(state))
    winner=freeze_sensor_winner(members,tmp_path/'winner',{42:131072,73:131072})
    assert winner['training']['added_transitions']==524288
