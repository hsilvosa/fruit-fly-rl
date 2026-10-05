"""Transient readers cannot erase the last valid recording/status file."""
import pytest
from fly_rl import atomic_io


def windows_error(code):
    error = PermissionError('simulated Windows rename conflict')
    error.winerror = code
    return error


@pytest.mark.parametrize('code', [5, 32, 33])
def test_transient_conflict_retries_without_losing_old_file(tmp_path, monkeypatch, code):
    source, destination = tmp_path/'pending', tmp_path/'status'
    source.write_text('new'); destination.write_text('old')
    original = atomic_io.os.replace
    attempts, waits = [], []
    def replace(left, right):
        attempts.append(1)
        if len(attempts) <= 2:
            assert destination.read_text() == 'old' and source.read_text() == 'new'
            raise windows_error(code)
        original(left, right)
    monkeypatch.setattr(atomic_io.os, 'replace', replace)
    monkeypatch.setattr(atomic_io.time, 'sleep', waits.append)
    atomic_io.replace_file(source, destination)
    assert destination.read_text() == 'new' and not source.exists()
    assert len(attempts) == 3 and waits == [.02, .05]


def test_persistent_error_keeps_both_files_and_propagates(tmp_path, monkeypatch):
    source, destination = tmp_path/'pending', tmp_path/'status'
    source.write_text('new'); destination.write_text('old')
    waits = []
    monkeypatch.setattr(atomic_io.os, 'replace', lambda *args: (_ for _ in ()).throw(windows_error(5)))
    monkeypatch.setattr(atomic_io.time, 'sleep', waits.append)
    with pytest.raises(PermissionError):
        atomic_io.replace_file(source, destination)
    assert destination.read_text() == 'old' and source.read_text() == 'new'
    assert waits == [.02, .05, .10]


def test_other_os_errors_are_not_retried(monkeypatch):
    waits = []
    monkeypatch.setattr(atomic_io.os, 'replace', lambda *args: (_ for _ in ()).throw(FileNotFoundError()))
    monkeypatch.setattr(atomic_io.time, 'sleep', waits.append)
    with pytest.raises(FileNotFoundError):
        atomic_io.replace_file('missing', 'target')
    assert not waits
