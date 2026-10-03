import pytest
from fly_rl.training.test_access import claim_test, require_unconsumed
from fly_rl.training.suites import load_suite
from fly_rl.training.experiment_selection import select_experiment
from test_seed_selection import experiment


def test_partial_overlap_consumes_geometry_even_with_different_pool_id(tmp_path):
    ledger=tmp_path/'ledger'
    first={'test_fingerprint':'a'*64,'splits':{'test':{'geometry_sha256':['g1','g2']}}}
    overlap={'test_fingerprint':'b'*64,'splits':{'test':{'geometry_sha256':['g2','g3']}}}
    distinct={'test_fingerprint':'c'*64,'splits':{'test':{'geometry_sha256':['g4']}}}
    claim_test(first,'test',ledger)
    with pytest.raises(ValueError,match='geometry already exposed'):
        require_unconsumed(overlap,ledger)
    with pytest.raises(ValueError,match='geometry already exposed'):
        claim_test(overlap,'test',ledger)
    assert claim_test(distinct,'test',ledger)
    assert not (ledger/('b'*64+'.json')).exists()


def test_global_exposure_prevents_selection_from_individually_unmarked_runs(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    a=experiment(tmp_path/'a',42,.9);b=experiment(tmp_path/'b',73,.8)
    claim_test(load_suite(a/'suite.json'),'generic evaluation')
    with pytest.raises(ValueError,match='already exposed'):
        select_experiment([a,b],tmp_path/'selected')
    assert not (tmp_path/'selected').exists()
