"""Budget, data separation, and source freezing before any GPU initialization."""
import hashlib
from datetime import datetime, timezone, timedelta
import pytest
from scripts.check_planner_failures import validate_request
from scripts.check_planner_development import validate


def protocol(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / 'source.py'
    source.write_text('frozen')
    return dict(schema=1, kind='frozen-prospective-development', task='large',
        arms=['v55', 'v60'], seeds=list(range(9500000, 9500016)),
        physical_cap_per_arm=81920, training_transitions=0, reserved_test_access=False,
        deadline_utc=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
        sources={'source.py': hashlib.sha256(source.read_bytes()).hexdigest()}, aliases={})


def test_frozen_protocol_passes_before_source_change(tmp_path, monkeypatch):
    p = protocol(tmp_path, monkeypatch)
    validate(p)
    (tmp_path / 'source.py').write_text('changed')
    with pytest.raises(ValueError, match='mismatch'):
        validate(p)


@pytest.mark.parametrize('field,value', [('training_transitions', 1),
    ('reserved_test_access', True), ('physical_cap_per_arm', 81936),
    ('arms', ['v55', 'v59']), ('deadline_utc', '2000-01-01T00:00:00+00:00')])
def test_invalid_protocol_cannot_start_check(tmp_path, monkeypatch, field, value):
    p = protocol(tmp_path, monkeypatch)
    p[field] = value
    with pytest.raises(ValueError):
        validate(p)


@pytest.mark.parametrize('seeds,cap', [([1, 1], 100), ([1, 3], 100),
    ([True], 3), ([1, 2], 3), ([1], 12001)])
def test_known_failure_budget_and_seed_contract(seeds, cap):
    with pytest.raises(ValueError):
        validate_request(seeds, cap, 'reused-failure-diagnostic')
