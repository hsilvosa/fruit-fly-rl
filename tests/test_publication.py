"""Security regressions for a source-only publication, without training."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest


@pytest.fixture
def publication(tmp_path):
    if not shutil.which('git'):
        pytest.skip('Publication checks require Git')
    # This staged path becomes scripts/verify_publication.py when installed.
    tool = Path(__file__).with_name('publication_audit_staged.py')
    if not tool.is_file():
        tool = Path(__file__).resolve().parents[1]/'scripts/verify_publication.py'
    spec = importlib.util.spec_from_file_location('publication_verifier', tool)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path/'project'
    root.mkdir()
    def git(*args):
        return subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', *args],
                              cwd=root, capture_output=True, check=True)
    git('init', '-q')
    (root/'README.md').write_text('[Guide](docs/guide.md)\n', encoding='utf-8')
    (root/'docs').mkdir()
    (root/'docs/guide.md').write_bytes(b'Public technical documentation.\r\n')
    git('add', 'README.md', 'docs/guide.md')
    return module, root, git


def test_public_links_cannot_depend_on_ignored_local_files(publication):
    module, root, git = publication
    assert module.audit(root)['status'] == 'passed'
    (root/'private').mkdir()
    (root/'private/notes.md').write_text('Local notes', encoding='utf-8')
    (root/'README.md').write_text('[Notes](private/notes.md)\n', encoding='utf-8')
    errors = module.audit(root)['errors']
    assert any(error['reason'] == 'link unavailable in tracked publication tree' for error in errors)


@pytest.mark.parametrize('name', ['private/notes.md', 'docs/JOURNAL.md', 'runs/checkpoint.json',
                                '.env', '.env.local', 'debug.log', 'weights.pt', 'credential.pem',
                                '.venv/config.txt', 'dist/local.txt', 'module/__pycache__/cached.pyc'])
def test_tracking_private_records_fails_publication(publication, name):
    module, root, git = publication
    path = root/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('Private local record', encoding='utf-8')
    git('add', name)
    assert any(error['file'] == name and error['reason'] == 'private or generated artifact is tracked'
               for error in module.audit(root)['errors'])


@pytest.mark.parametrize('content, reason', [
    ('C:\\Users\\Example\\local', 'personal absolute filesystem path'),
    ('token='+'ghp_'+'X'*36, 'possible credential or private key; inspect locally'),
    ('FINAL_RESULTS_PENDING', 'unfinished verification or result placeholder'),
])
def test_sensitive_document_content_fails_publication(publication, content, reason):
    module, root, git = publication
    (root/'docs/guide.md').write_text(content, encoding='utf-8')
    assert any(error['reason'] == reason for error in module.audit(root)['errors'])


def test_machine_evidence_stays_private_even_without_personal_paths(publication):
    module, root, git = publication
    path = root/'docs/evidence/experiment-launch.json'
    path.parent.mkdir(parents=True)
    path.write_text('{"pid": 1234, "status": "running"}', encoding='utf-8')
    git('add', 'docs/evidence/experiment-launch.json')
    assert any(error['reason'] == 'detailed evidence is not approved for public tree'
               for error in module.audit(root)['errors'])


def test_documentation_images_must_be_in_the_public_tree(publication):
    module, root, git = publication
    image = root/'docs/map.png'
    image.write_bytes(b'figure fixture')
    (root/'README.md').write_text('![Map](docs/map.png)\n', encoding='utf-8')
    assert module.audit(root)['status'] == 'failed'
    git('add', 'docs/map.png')
    assert module.audit(root)['status'] == 'passed'


def test_public_example_environment_is_allowed(publication):
    module, root, git = publication
    (root/'.env.example').write_text('EXAMPLE_SETTING=demo\n', encoding='utf-8')
    git('add', '.env.example')
    assert module.audit(root)['status'] == 'passed'


@pytest.mark.parametrize('content', ['95% interval 0.0â€“5.7%', 'An invalid character: \ufffd'])
def test_damaged_document_encoding_fails_publication(publication, content):
    module, root, git = publication
    (root/'docs/guide.md').write_text(content, encoding='utf-8')
    assert any(error['reason'] == 'text encoding artifact; inspect and repair documentation'
               for error in module.audit(root)['errors'])


def test_release_archive_checks_committed_bytes_and_private_extras(publication):
    module, root, git = publication
    git('-c', 'user.name=QA', '-c', 'user.email=qa@example.invalid', 'commit', '-qm', 'QA fixture')
    archive = root/'release.zip'
    git('-c', 'core.autocrlf=false', 'archive', '--format=zip', f'--output={archive}', 'HEAD')
    assert module.audit_archive(root, archive)['status'] == 'passed'
    with zipfile.ZipFile(archive, 'a') as output:
        output.writestr('private/notes.md', 'Private note')
    assert module.audit_archive(root, archive)['status'] == 'failed'


def test_release_archive_accepts_declared_crlf_but_rejects_changed_commands(publication):
    module, root, git = publication
    (root/'.gitattributes').write_text('*.cmd text eol=crlf\n', encoding='utf-8')
    (root/'launch.cmd').write_bytes(b'@echo off\necho original\n')
    git('add', '.gitattributes', 'launch.cmd')
    git('-c', 'user.name=QA', '-c', 'user.email=qa@example.invalid', 'commit', '-qm', 'Line ending fixture')
    archive = root/'release.zip'
    git('-c', 'core.autocrlf=false', 'archive', '--format=zip', f'--output={archive}', 'HEAD')
    with zipfile.ZipFile(archive) as source:
        contents = {name: source.read(name) for name in source.namelist() if not name.endswith('/')}
    assert b'\r\n' in contents['launch.cmd']
    assert module.audit_archive(root, archive)['status'] == 'passed'
    contents['launch.cmd'] = b'@echo off\r\necho changed\r\n'
    with zipfile.ZipFile(archive, 'w') as changed:
        for name, data in contents.items():
            changed.writestr(name, data)
    assert module.audit_archive(root, archive)['status'] == 'failed'
