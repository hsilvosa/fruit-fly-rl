"""Irreversible local record of exposure to a versioned test pool."""
from pathlib import Path
import json
from datetime import datetime, timezone


def claim_test(suite, purpose, directory='runs/suites/consumed'):
    if 'test_fingerprint' not in suite:
        return None  # Legacy records keep their original per-experiment guard.
    fingerprint=suite['test_fingerprint']
    if len(fingerprint)!=64 or any(c not in '0123456789abcdef' for c in fingerprint): raise ValueError('Invalid test fingerprint')
    root = Path(directory)
    if (root/(fingerprint+'.json')).exists(): raise FileExistsError('Test pool already claimed')
    require_unconsumed(suite,directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root/(suite['test_fingerprint']+'.json')
    with path.open('x', encoding='utf-8') as handle:
        json.dump({'purpose': purpose, 'test_fingerprint': suite['test_fingerprint'],
                   'claimed_utc': datetime.now(timezone.utc).isoformat(),
                   'test_geometries':suite.get('splits',{}).get('test',{}).get('geometry_sha256',[]),
                   'note': 'Consumed even if evaluation fails; do not tune and retry as an untouched test.'}, handle, indent=2)
    return str(path)


def require_unconsumed(suite, directory='runs/suites/consumed'):
    geometries=set(suite.get('splits',{}).get('test',{}).get('geometry_sha256',[]))
    for path in Path(directory).glob('*.json'):
        exposed=json.loads(path.read_text(encoding='utf-8'))
        if geometries.intersection(exposed.get('test_geometries',[])):
            raise ValueError('Test geometry already exposed, including overlapping subsets')
    if 'test_fingerprint' in suite and (Path(directory)/(suite['test_fingerprint']+'.json')).exists():
        raise ValueError('Test pool already exposed; create a genuinely independent suite')
