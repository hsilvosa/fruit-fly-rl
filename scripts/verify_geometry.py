"""Bounded whole-connectome verification; optimizer smoke is explicitly opt-in."""
import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import time
import numpy as np
import torch
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import PROFILES, difficulty_metrics
from fly_rl.simulation.sensors import SENSOR_V3
from fly_rl.training.learning import BrainEnv, make_policy, train
from fly_rl.training.geometry_curriculum import VERSION
from fly_rl.training.suites import load_suite
from fly_rl.training.generalization import sha256
from fly_rl.training.fresh_sensor_comparison import code_hashes, initialize_pair
from fly_rl.training.test_access import require_unconsumed
from fly_rl.recordings.recording import software_info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data')
    parser.add_argument('--suite', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    parser.add_argument('--benchmark-seconds', type=float, default=12.)
    parser.add_argument('--optimizer-smoke', action='store_true', help='Exactly 128 transitions and one PPO update in a separate smoke checkpoint')
    args = parser.parse_args()
    if not np.isfinite(args.benchmark_seconds) or not 1 <= args.benchmark_seconds <= 120:
        parser.error('Whole-environment benchmark must be 1 to 120 seconds')
    torch.set_num_threads(4)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    aliases = {str(p.resolve()): sha256(p) for p in Path('runs').glob('*policy.*') if p.suffix in ['.zip', '.json']}
    suite = load_suite(args.suite)
    from fly_rl.training.mastery_curriculum import VERSION as MASTERY_VERSION,practice_partition
    mastery=suite['training_profiles'][0]['name']=='gate-near'
    training,practice=practice_partition(suite) if mastery else (suite['splits']['train']['seeds'],None)
    require_unconsumed(suite)
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'running',
              'software': software_info(), 'source_hashes': code_hashes(),
              'suite': str(Path(args.suite).resolve()), 'suite_sha256': sha256(args.suite),
              'test_policy_evaluated': False, 'aliases_before': aliases,
              'cuda_available': torch.cuda.is_available(), 'historical_suites': []}
    # This re-generates geometry only; it does not re-assess any consumed policy test.
    for path in sorted(Path('runs/suites').glob('*.json')):
        if path.resolve() == Path(args.suite).resolve():
            continue
        prior = load_suite(path)
        report['historical_suites'].append({'path': str(path), 'sha256': sha256(path),
                                             'audited_layouts': sum(len(p['seeds']) for p in prior['splits'].values())})
    report['initializations'] = [initialize_pair(args.data, args.device, suite, seed, output/f'initial-{seed}') for seed in [42, 73]]
    gc.collect()
    if args.device == 'cuda':
        torch.cuda.empty_cache()
    env = BrainEnv(args.data, 1, args.device, 42, mode='dense', dynamics='coordinated',
                   sensor_version=SENSOR_V3, map_profile='large')
    policy = make_policy(env, seed=42)
    weights = [p.detach().clone() for p in policy.policy.parameters()]
    report['graph'] = {'neurons': env.brain.n, 'edges': env.brain.audit['edges'],
                       'fingerprint': env.brain.fingerprint, 'full_graph': env.brain.n == env.brain.audit['annotated_neurons']}
    if args.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    measurements = []
    # CPU sensor work, physics, all graph updates and policy inference are included.
    for profile in PROFILES:
        env.map_profile = PROFILES[profile]
        env.worlds = [FlightWorld(10, 'dense', dynamics='coordinated', sensor_version=SENSOR_V3, map_profile=profile)]
        env.seed(10)
        features = env.reset()
        geometry = difficulty_metrics(env.worlds[0])
        if args.device == 'cuda':torch.cuda.synchronize()
        started, transitions = time.perf_counter(), 0
        deadline = started+args.benchmark_seconds/len(PROFILES)
        while time.perf_counter() < deadline:
            actions = policy.predict(features, deterministic=True)[0]
            features, rewards, dones, infos = env.step(actions)
            transitions += 1
            if not np.isfinite(features).all() or not np.isfinite(rewards).all():
                raise RuntimeError('Nonfinite whole-connectome transition')
        if args.device == 'cuda':torch.cuda.synchronize()
        elapsed = time.perf_counter()-started
        measurements.append({'profile': profile, 'transitions': transitions, 'seconds': elapsed,
                              'transitions_per_second': transitions/elapsed, 'geometry': geometry})
    if not all(torch.equal(a, b) for a, b in zip(weights, policy.policy.parameters())):
        raise RuntimeError('Inference changed policy weights')
    report.update(benchmark=measurements, benchmark_budget_seconds=args.benchmark_seconds, inference_weights_unchanged=True,
                  peak_vram_gib=torch.cuda.max_memory_allocated()/2**30 if args.device == 'cuda' else None)
    env.close()
    del policy, env, weights
    gc.collect()
    if args.device == 'cuda':torch.cuda.empty_cache()
    if args.optimizer_smoke:
        report['optimizer_smoke'] = train(args.data, args.device, 128, 1, output/'smoke/policy.zip', smoke=True,
            mode='dense', layout_seeds=training, dynamics='coordinated',
            training_seed=42, sensor_version=SENSOR_V3, curriculum=MASTERY_VERSION if mastery else VERSION, curriculum_total=128,
            map_profile=suite['map_profile'], curriculum_profiles=suite['training_profiles'],
            **({'practice_seeds':practice} if mastery else {}))
        if report['optimizer_smoke']['added_transitions'] != 128 or report['optimizer_smoke']['updates'] != 1:
            raise RuntimeError('Smoke exceeded its declared allowance')
    report['aliases_after'] = {p: sha256(p) if Path(p).exists() else None for p in aliases}
    report['aliases_unchanged'] = report['aliases_after'] == aliases
    if not report['aliases_unchanged']:raise RuntimeError('Original launcher alias changed')
    require_unconsumed(suite)
    report.update(status='passed', final_test_unconsumed=True, training_invoked=args.optimizer_smoke)
    (output/'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['status', 'graph', 'cuda_available', 'benchmark', 'peak_vram_gib', 'aliases_unchanged', 'final_test_unconsumed']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
