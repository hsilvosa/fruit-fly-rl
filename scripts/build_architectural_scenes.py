"""Build CPU-only architectural drafts, meshes, collision records and previews."""
import argparse
import hashlib
import json
from pathlib import Path

from fly_rl.simulation.architectural_scenes import BUILDERS, SCENE_VERSION, export_scene
from fly_rl.visualization.architecture_preview import write_gallery, write_plans, write_preview


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    scenes = [builder() for builder in BUILDERS.values()]
    reports = [export_scene(scene, output) for scene in scenes]
    write_preview(scenes, output / 'index.html', reports)
    write_gallery(scenes, output / 'gallery.png')
    write_plans(scenes, output / 'plans.png')
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())
             if p.is_file() and p.name != 'manifest.json'}
    manifest = {'schema': SCENE_VERSION, 'brain_loaded': False, 'training_invoked': False,
                'policy_evaluated': False, 'gpu_required': False, 'scenes': reports, 'files': files}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('assets/architecture/draft-0.2'))
    args = parser.parse_args()
    result = build(args.output)
    print(json.dumps({'output': str(args.output), 'scenes': result['scenes'], 'gpu_required': False}, indent=2))
