"""Audit the working copies of Git-tracked publication files without running a policy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
from urllib.parse import unquote, urlsplit


def audit(root):
    root = Path(root).resolve()
    result = subprocess.run(
        ['git', '-c', f'safe.directory={root.as_posix()}', 'ls-files', '-z'],
        cwd=root, capture_output=True, check=True,
    )
    tracked = {item.decode('utf-8') for item in result.stdout.split(b'\0') if item}
    errors = []
    links = 0
    private_names = {'docs/JOURNAL.md', 'docs/journal-entry-template.md'}
    public_evidence = {'docs/evidence/geometry-v1-results.json'}
    personal_path = re.compile(r'(?i)(?:[a-z]:[\\/]+Users[\\/]+|/home/|/Users/)')
    credential = re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    text_extensions = {'.md', '.json', '.toml', '.yaml', '.yml', '.txt', '.bib', '.ps1', '.cmd', '.py'}
    for name in sorted(tracked):
        path = root / name
        generated_prefixes = ('private/', 'runs/', 'data/', 'reports/', '.conda/', '.venv/', 'venv/',
                              'build/', 'dist/', '__pycache__/', '.pytest_cache/')
        secret_file = (path.name == '.env' or path.name.startswith('.env.')) and path.name != '.env.example'
        local_binary = path.suffix.lower() in {'.pt', '.pth', '.ckpt', '.onnx', '.pkl', '.pem', '.key', '.log', '.pyc', '.pyo', '.whl'}
        cached = any(part in {'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
                     or part.endswith('.egg-info') for part in Path(name).parts)
        if name in private_names or name.startswith(generated_prefixes) or cached or secret_file or local_binary:
            errors.append({'file': name, 'reason': 'private or generated artifact is tracked'})
        if name.startswith('docs/evidence/') and path.suffix == '.json' and name not in public_evidence:
            errors.append({'file': name, 'reason': 'detailed evidence is not approved for public tree'})
        if not path.is_file():
            errors.append({'file': name, 'reason': 'tracked file missing; update index before publication audit'})
            continue
        if path.suffix.lower() not in text_extensions:
            continue
        content = path.read_text(encoding='utf-8-sig')
        # The guard's own regex is a rule, rather than a personal filesystem path.
        if path.suffix.lower() in {'.md', '.json', '.toml', '.yaml', '.yml', '.txt', '.bib'} and personal_path.search(content):
            errors.append({'file': name, 'reason': 'personal absolute filesystem path'})
        if credential.search(content):
            errors.append({'file': name, 'reason': 'possible credential or private key; inspect locally'})
        if path.suffix.lower() != '.md':
            continue
        if any(marker in content for marker in ('\ufffd', 'Ã', 'Â', 'â€')):
            errors.append({'file': name, 'reason': 'text encoding artifact; inspect and repair documentation'})
        if re.search(r'\bFINAL_[A-Z_]+_PENDING\b', content):
            errors.append({'file': name, 'reason': 'unfinished verification or result placeholder'})
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            target = target.strip().strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            links += 1
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root):
                errors.append({'file': name, 'reason': 'link leaves repository', 'target': target})
                continue
            relative = destination.relative_to(root).as_posix()
            if relative not in tracked and not any(item.startswith(relative.rstrip('/') + '/') for item in tracked):
                errors.append({'file': name, 'reason': 'link unavailable in tracked publication tree', 'target': target})
    return {'status': 'failed' if errors else 'passed', 'tracked_files': len(tracked),
            'local_links': links, 'training_invoked': False, 'evaluation_invoked': False, 'errors': errors}


def audit_archive(root, archive):
    """Compare an archive with committed blobs, respecting Git newline normalization."""
    root = Path(root).resolve()
    report = audit(root)
    result = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'ls-files', '-z'],
                            cwd=root, capture_output=True, check=True)
    expected = {name.decode('utf-8') for name in result.stdout.split(b'\0') if name}
    clean = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'diff', '--quiet', 'HEAD', '--'], cwd=root)
    if clean.returncode:
        report['errors'].append({'reason': 'commit tracked changes before auditing a release archive'})
    tree = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'ls-tree', '-rz', '--full-tree', 'HEAD'],
                          cwd=root, capture_output=True, check=True)
    blobs = {}
    for record in tree.stdout.split(b'\0'):
        if record:
            metadata, name = record.split(b'\t', 1)
            blobs[name.decode('utf-8')] = metadata.split()[2].decode('ascii')
    algorithm = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'rev-parse', '--show-object-format'],
                               cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    with zipfile.ZipFile(archive) as source:
        files = {entry.filename for entry in source.infolist() if not entry.is_dir()}
        if files != expected:
            report['errors'].append({'reason': 'archive files differ from tracked publication tree',
                                     'missing': sorted(expected-files), 'unexpected': sorted(files-expected)})
        for name in sorted(files & expected):
            content = source.read(name)
            actual = hashlib.new(algorithm, b'blob '+str(len(content)).encode('ascii')+b'\0'+content).hexdigest()
            if actual != blobs.get(name):
                report['errors'].append({'file': name, 'reason': 'archive bytes differ from committed source blob'})
    report['archive_files'] = len(files)
    report['archive_contains_git_history'] = any(name.startswith('.git/') for name in files)
    if report['archive_contains_git_history']:
        report['errors'].append({'reason': 'archive includes Git history'})
    report['status'] = 'failed' if report['errors'] else 'passed'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    report = audit_archive(args.root, args.archive) if args.archive else audit(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(report['status'] != 'passed')
