import json
import pytest
from fly_rl.training.suites import prepare_suite, load_suite
from fly_rl.training.test_access import claim_test, require_unconsumed
from fly_rl.training.diagnostics import failure_report


def test_fresh_pools_exclude_historical_and_detect_tampering(tmp_path):
    old = tmp_path/'old.json'; fresh = tmp_path/'fresh.json'
    prepare_suite(old, 0, 10000, 20000, 2, 2, 2)
    prepare_suite(fresh, 30000, 40000, 50000, 2, 2, 2, [old])
    suite = load_suite(fresh)
    assert suite['splits']['test']['seeds'] == [50000, 50001]
    assert suite['excluded_suites'] and len(suite['test_fingerprint']) == 64
    with pytest.raises(ValueError, match='reuse'):
        prepare_suite(tmp_path/'bad.json', 0, 40000, 50000, 2, 2, 2, [old])
    suite['splits']['test']['layout_sha256'][0] = '0'*64
    fresh.write_text(json.dumps(suite))
    with pytest.raises(ValueError, match='fingerprint'):
        load_suite(fresh)


def test_new_suite_ranges_and_pool_fingerprints_are_checked(tmp_path):
    with pytest.raises(ValueError, match='Overlapping'):
        prepare_suite(tmp_path/'bad.json', 0, 1, 10, 2, 2, 2)
    path = tmp_path/'suite.json'; prepare_suite(path, train_count=1, validation_count=1, test_count=1)
    suite = load_suite(path); suite['test_fingerprint'] = '0'*64; path.write_text(json.dumps(suite))
    with pytest.raises(ValueError, match='Test pool'):
        load_suite(path)


def test_test_exposure_survives_failed_or_different_experiment(tmp_path):
    suite = {'test_fingerprint': 'a'*64}
    require_unconsumed(suite, tmp_path)
    record = claim_test(suite, 'experiment-one', tmp_path)
    assert json.loads(open(record).read())['purpose'] == 'experiment-one'
    with pytest.raises(FileExistsError):
        claim_test(suite, 'experiment-two', tmp_path)
    with pytest.raises(ValueError, match='exposed'):
        require_unconsumed(suite, tmp_path)


def test_diagnostics_do_not_invent_collision_causes_or_read_test(tmp_path):
    path = tmp_path/'validation.json'
    path.write_text(json.dumps({'episodes': [dict(success=False, collision=True, idle_fraction=0),
        dict(success=False, collision=False, idle_fraction=.5, distance_end=10)]}))
    result = failure_report(path)
    assert result['categories'] == {'collision_location_unknown': 1, 'timeout_with_frequent_stopping': 1}
    path.write_text('{"split":"test","episodes":[]}')
    with pytest.raises(ValueError, match='validation'):
        failure_report(path)
