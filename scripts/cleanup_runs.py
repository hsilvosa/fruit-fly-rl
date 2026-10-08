"""Record and delete regenerable raw imitation datasets under runs/training/*/training-data.

Writes a manifest (directory, file names, byte sizes) to private/runs-cleanup-manifest.json before deleting.
Keeps every JSON, ZIP and log of each experiment. Usage: cleanup_runs.py [--apply]
"""
import json, os, shutil, sys, glob
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
apply = '--apply' in sys.argv
rows = []
total = 0
for d in sorted(glob.glob('runs/training/*/training-data')):
    files = []
    for root, _, names in os.walk(d):
        for n in names:
            p = os.path.join(root, n)
            files.append({'file': os.path.relpath(p, d).replace(chr(92), '/'), 'bytes': os.path.getsize(p)})
    size = sum(f['bytes'] for f in files)
    total += size
    rows.append({'directory': d.replace(chr(92), '/'), 'bytes': size, 'files': files})
manifest = {'reason': 'Raw teacher-collected imitation datasets of completed, superseded experiments; regenerable by the experiment code.',
            'total_bytes': total, 'directories': rows}
os.makedirs('private', exist_ok=True)
json.dump(manifest, open('private/runs-cleanup-manifest.json', 'w'), indent=1)
print('directories', len(rows), 'total GiB', round(total / 2 ** 30, 1))
if apply:
    for r in rows:
        shutil.rmtree(r['directory'])
    for d in glob.glob('SB3-*'):
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    print('deleted')
