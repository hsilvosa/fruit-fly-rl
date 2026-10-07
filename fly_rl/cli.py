"""Explicit commands; importing the package never downloads or trains."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch

def write_report(name,result):
    folder=Path('reports');folder.mkdir(exist_ok=True)
    (folder/name).write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)

def benchmark(data,device,seconds):
    from fly_rl.connectome.brain import Brain,SENSORS
    duration=min(max(seconds,1),120)
    brain=Brain(data,1,device)
    results=[];deadline=time.monotonic()+duration
    if device=='cuda': torch.cuda.reset_peak_memory_stats()
    for batch in [1,4,8,16]:
        if time.monotonic()>=deadline: break
        brain.batch=batch;brain.state=torch.zeros((brain.n,batch),device=brain.device)
        sensors=np.random.default_rng(0).uniform(-1,1,(batch,SENSORS)).astype(np.float32)
        brain.step(sensors)
        if device=='cuda': torch.cuda.synchronize()
        start=time.monotonic();steps=0;end=min(deadline,start+max(.25,duration/4))
        while time.monotonic()<end:
            features=brain.step(sensors);steps+=1
        if device=='cuda': torch.cuda.synchronize()
        assert np.isfinite(features).all() and torch.isfinite(brain.state).all()
        elapsed=time.monotonic()-start
        results.append({'batch':batch,'steps':steps,'elapsed_seconds':elapsed,'transitions_per_second':steps*batch/elapsed})
    return {'dataset':brain.audit,'device':device,'results':results,
            'peak_vram_gb':torch.cuda.max_memory_allocated()/2**30 if device=='cuda' else None,
            'full_graph':True,'budget_seconds':duration}

def main():
    parser=argparse.ArgumentParser(description='A full-connectome virtual fly. Learning runs only through explicit training commands.')
    parser.add_argument('--data',default='data');parser.add_argument('--device',choices=['cuda','cpu'],default='cuda')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('controller-versions',help='List controller revision numbers, descriptions, and historical aliases; no simulation')
    sub.add_parser('prepare-data')
    bench=sub.add_parser('benchmark');bench.add_argument('--seconds',type=float,default=20)
    demo=sub.add_parser('demo');demo.add_argument('--controller',choices=['policy','observed-map'],default='policy');demo.add_argument('--checkpoint');demo.add_argument('--seed',type=int,default=10)
    from fly_rl.navigation.versions import DEFAULT_REVISION,PUBLIC_VERSIONS,public_version
    demo.add_argument('--controller-version','--planner-version',dest='planner_version',type=public_version,choices=PUBLIC_VERSIONS,default=DEFAULT_REVISION,help='Controller revision; accepts the number or planner- prefix. Legacy aliases v55, v56, v57, v58, v59, v60, v61, v62, v63, v64, v65 remain valid. Only planner-1.0 is the default baseline; later revisions remain experimental.')
    demo.add_argument('--offscreen',action='store_true');demo.add_argument('--seconds',type=float,default=0)
    demo.add_argument('--screenshot',default='reports/demo.png')
    demo.add_argument('--speed',type=float,default=1.,help='Live simulation time multiplier; Shift boosts it 10x')
    demo.add_argument('--no-record',action='store_true',help='Disable archived flight telemetry')
    demo.add_argument('--record-dir',default='runs/demo')
    demo.add_argument('--record-brain',action='store_true',help='Save full neuron activity once per simulated second')
    demo.add_argument('--room-mode',choices=['obstacles','dense'],default='obstacles')
    demo.add_argument('--map-profile',help='dense-v3, open, passages, large, maze, or a profile JSON file')
    from fly_rl.simulation.architectural_scenes import BUILDERS
    demo.add_argument('--architecture-scene',choices=tuple(BUILDERS),help='Use a revised architectural scene and its explicit planner')
    demo.add_argument('--situation',type=int,default=0,help='Architectural situation index (zero based)')
    demo.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    from fly_rl.simulation.sensors import SENSOR_VERSIONS
    demo.add_argument('--sensor-version',choices=SENSOR_VERSIONS,help='Explicit sensory interface for untrained viewing or matching checkpoint')
    demo.add_argument('--brain-view',action='store_true');demo.add_argument('--transfer',action='store_true')
    demo.add_argument('--trace-neuron',type=int,help='Real located body ID to inspect and plot')
    demo.add_argument('--brain-region',default='ALL',help='Official somaNeuromere label')
    demo.add_argument('--brain-class',default='ALL',help='Official superclass label')
    inspect=sub.add_parser('inspect');inspect.add_argument('archive');inspect.add_argument('--output',default='reports/archive-inspection.json')
    recovery=sub.add_parser('recover');recovery.add_argument('archive');recovery.add_argument('--apply',action='store_true')
    recovery.add_argument('--output',default='reports/archive-recovery.json')
    comparison=sub.add_parser('compare');comparison.add_argument('left');comparison.add_argument('right')
    comparison.add_argument('--output',default='reports/archive-comparison.json')
    replay=sub.add_parser('replay');replay.add_argument('archive');replay.add_argument('--compare')
    replay.add_argument('--speed',type=float,default=1.);replay.add_argument('--offscreen',action='store_true')
    replay.add_argument('--seconds',type=float,default=0);replay.add_argument('--screenshot',default='reports/replay.png')
    replay.set_defaults(seed=10,checkpoint=None,no_record=True,record_dir='runs/demo',record_brain=False)
    panorama=sub.add_parser('train-panorama');panorama.add_argument('--plan',required=True)
    waypoint=sub.add_parser('train-waypoint');waypoint.add_argument('--plan',required=True)
    spatial=sub.add_parser('train-spatial');spatial.add_argument('--plan',required=True)
    guarded=sub.add_parser('train-guarded');guarded.add_argument('--plan',required=True)
    guided=sub.add_parser('train-guided');guided.add_argument('--plan',required=True,help='Explicit frozen, bounded training-only teacher protocol')
    train=sub.add_parser('train');train.add_argument('--steps',type=int,required=True);train.add_argument('--batch',type=int,default=1)
    train.add_argument('--output',default='runs/policy.zip');train.add_argument('--resume')
    train.add_argument('--mode',choices=['near','empty','obstacles','dense'],default='obstacles')
    train.add_argument('--suite',help='Frozen suite; training uses only its train split')
    train.add_argument('--map-profile',help='Named profile or a profile JSON file; implies dense mode')
    train.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    train.add_argument('--transfer',action='store_true')
    from fly_rl.simulation.sensors import SENSOR_VERSIONS
    train.add_argument('--history-frames',type=int,default=0)
    train.add_argument('--history-stride',type=int,default=8)
    train.add_argument('--transfer-history',action='store_true',help='Explicitly upgrade the movement policy with a zero-output temporal residual')
    train.add_argument('--sensor-version',choices=SENSOR_VERSIONS,help='Explicit versioned sensory contract; checkpoint resumes must match')
    train.add_argument('--gamma',type=float,default=.995,help='PPO discount per 50 ms decision; long routes may require a longer horizon')
    train.add_argument('--reward-shaping',choices=['observed-ray-risk-v1','certified-route-progress-v1'])
    train.add_argument('--timeout-as-terminal',action='store_true',help='Treat exhausted navigation attempts as failures without value bootstrap')
    smoke=sub.add_parser('smoke-test');smoke.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    evaluation=sub.add_parser('evaluate');evaluation.add_argument('--checkpoint')
    evaluation.add_argument('--episodes',type=int,default=16)
    evaluation.add_argument('--mode',choices=['near','empty','obstacles','dense'],default='obstacles')
    evaluation.add_argument('--goal-probe',action='store_true')
    evaluation.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    evaluation.add_argument('--transfer',action='store_true')
    evaluation.add_argument('--suite');evaluation.add_argument('--split',choices=['validation','test'],default='validation')
    evaluation.add_argument('--map-profile',help='Named profile or a profile JSON file; implies dense mode')
    evaluation.add_argument('--seed',type=int,default=10000)
    evaluation.add_argument('--output',default='reports/evaluation.json')
    evaluation.add_argument('--route-metrics',action='store_true')
    evaluation.add_argument('--expose-test',action='store_true',help='Explicitly consume a suite test pool; prefer final-test')
    selection=sub.add_parser('select-policy');selection.add_argument('iteration')
    selection.add_argument('--output',default='runs/navigation-policy.zip')
    plot=sub.add_parser('plot-training');plot.add_argument('iteration')
    plot.add_argument('--output',default='reports/training-progress.png');plot.add_argument('--independent')
    suite=sub.add_parser('prepare-suite');suite.add_argument('--output',required=True)
    for name,start,count in [('train',30000,256),('validation',40000,32),('test',50000,64)]:
        suite.add_argument('--'+name+'-start',type=int,default=start)
        suite.add_argument('--'+name+'-count',type=int,default=count)
    suite.add_argument('--exclude-suite',action='append',default=[])
    suite.add_argument('--map-profile',help='Target profile; omitted preserves the original dense generator')
    suite.add_argument('--training-profiles',nargs='+',default=[],help='Freeze curriculum variants using training seeds only')
    mapreport=sub.add_parser('map-report');mapreport.add_argument('--output',required=True)
    mapreport.add_argument('--profiles',nargs='+',default=['open','passages','large','maze'])
    mapreport.add_argument('--seed',type=int,default=10);mapreport.add_argument('--count',type=int,default=4);mapreport.add_argument('--figure')
    geometry=sub.add_parser('prepare-geometry-comparison');geometry.add_argument('--suite',required=True);geometry.add_argument('--output',required=True)
    geometry.add_argument('--steps-per-seed',type=int);geometry.add_argument('--batch',type=int,default=8);geometry.add_argument('--rounds',type=int,default=2);geometry.add_argument('--seeds',type=int,nargs='+',default=[42,73])
    rungeometry=sub.add_parser('run-geometry-comparison');rungeometry.add_argument('configuration');rungeometry.add_argument('--output',required=True)
    dense=sub.add_parser('train-dense');dense.add_argument('--suite',required=True)
    dense.add_argument('--output',required=True);dense.add_argument('--baseline',default='runs/navigation-policy.zip')
    dense.add_argument('--steps',type=int,default=131072);dense.add_argument('--batch',type=int,default=16)
    dense.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    dense.add_argument('--rounds',type=int,default=1)
    dense.add_argument('--training-seed',type=int,default=42)
    dense.add_argument('--no-promote',action='store_true')
    dense.add_argument('--route-metrics',action='store_true')
    dense.add_argument('--mastery',action='store_true')
    dense.add_argument('--continuous-episodes',action='store_true')
    dense.add_argument('--target-envs',type=int,default=0)
    dense.add_argument('--gamma',type=float,default=.995)
    dense.add_argument('--timeout-as-terminal',action='store_true')
    risk=sub.add_parser('prepare-risk-comparison');risk.add_argument('--suite',required=True);risk.add_argument('--output',required=True);risk.add_argument('--steps-per-seed',type=int);risk.add_argument('--batch',type=int,default=8);risk.add_argument('--rounds',type=int,default=2);risk.add_argument('--seeds',type=int,nargs='+',default=[42,73])
    runrisk=sub.add_parser('run-risk-comparison');runrisk.add_argument('configuration');runrisk.add_argument('--output',required=True)
    approach=sub.add_parser('prepare-approach-comparison');approach.add_argument('--suite',required=True);approach.add_argument('--output',required=True);approach.add_argument('--steps-per-seed',type=int);approach.add_argument('--batch',type=int,default=8);approach.add_argument('--rounds',type=int,default=2);approach.add_argument('--seeds',type=int,nargs='+',default=[42,73])
    runapproach=sub.add_parser('run-approach-comparison');runapproach.add_argument('configuration');runapproach.add_argument('--output',required=True)
    trace=sub.add_parser('trace-validation');trace.add_argument('experiment');trace.add_argument('--output',required=True);trace.add_argument('--count',type=int,default=2);trace.add_argument('--max-steps',type=int,default=1200);trace.add_argument('--kind',choices=['failure','collision','timeout'],default='failure')
    collisiondiag=sub.add_parser('diagnose-collisions');collisiondiag.add_argument('source');collisiondiag.add_argument('--output',required=True)
    traceplot=sub.add_parser('plot-validation-trace');traceplot.add_argument('source');traceplot.add_argument('--output',required=True)
    diagnose=sub.add_parser('diagnose-validation');diagnose.add_argument('source');diagnose.add_argument('--output',default='reports/validation-failures.json')
    multi=sub.add_parser('select-experiment');multi.add_argument('experiments',nargs='+');multi.add_argument('--output',required=True)
    denseplot=sub.add_parser('plot-dense');denseplot.add_argument('experiment');denseplot.add_argument('--output',default='reports/dense-flight-progress.png')
    generalplot=sub.add_parser('plot-generalization');generalplot.add_argument('experiment');generalplot.add_argument('--output',default='reports/priority12-generalization.png')
    final=sub.add_parser('final-test');final.add_argument('experiment')
    iteration=sub.add_parser('iterate');iteration.add_argument('--baseline',required=True)
    iteration.add_argument('--output',required=True);iteration.add_argument('--steps-per-round',type=int,default=65536)
    iteration.add_argument('--rounds',type=int,default=3);iteration.add_argument('--batch',type=int,default=16)
    iteration.add_argument('--dynamics',choices=['legacy','coordinated'],default='legacy')
    migrate=sub.add_parser('migrate-sensors');migrate.add_argument('source');migrate.add_argument('--output',required=True)
    migrate.add_argument('--target',choices=list(SENSOR_VERSIONS[1:]),default=SENSOR_VERSIONS[1])
    compare=sub.add_parser('compare-sensors');compare.add_argument('--suite',required=True);compare.add_argument('--baseline',required=True);compare.add_argument('--output',required=True)
    failures=sub.add_parser('plot-validation-failures');failures.add_argument('experiments',nargs='+');failures.add_argument('--output',required=True)
    fresh=sub.add_parser('prepare-fresh-comparison');fresh.add_argument('--suite',required=True);fresh.add_argument('--output',required=True);fresh.add_argument('--steps-per-seed',type=int);fresh.add_argument('--batch',type=int,default=8);fresh.add_argument('--rounds',type=int,default=2);fresh.add_argument('--seeds',nargs='+',type=int,default=[42,73])
    runfresh=sub.add_parser('run-fresh-comparison');runfresh.add_argument('configuration');runfresh.add_argument('--output',required=True)
    args=parser.parse_args()
    torch.set_num_threads(4)
    if args.command=='controller-versions':
        from fly_rl.navigation.versions import catalog
        print(json.dumps(catalog(),indent=2))
        return
    if args.command=='demo' and args.controller!='observed-map' and args.planner_version!=DEFAULT_REVISION:
        parser.error('Planner versions require --controller observed-map')
    if args.command=='demo' and args.controller=='observed-map':
        from fly_rl.simulation.sensors import SENSOR_V6
        if args.checkpoint: parser.error('Observed-map planning does not load a policy checkpoint')
        from fly_rl.navigation.registry import VersionedPlannerPolicy
        profile=args.map_profile or 'large'
        try:
            VersionedPlannerPolicy(args.planner_version,profile)
        except ValueError as error:
            parser.error(str(error))
        if args.sensor_version and args.sensor_version!=SENSOR_V6: parser.error('Observed-map planning requires the panoramic v6 sensory contract')
        args.map_profile=profile;args.room_mode='dense';args.dynamics='coordinated';args.sensor_version=SENSOR_V6
    if getattr(args,'map_profile',None):
        if args.command=='demo':args.room_mode='dense'
        elif args.command in ['train','evaluate']:args.mode='dense'
    if args.command=='map-report':
        from fly_rl.visualization.map_report import map_report
        result=map_report(args.output,args.profiles,args.seed,args.count,args.figure)
        print(json.dumps({'output':args.output,'figure':result['figure'],'layouts':len(result['rows']),'training_invoked':False,'policy_evaluated':False},indent=2))
    elif args.command=='prepare-geometry-comparison':
        from fly_rl.training.geometry_comparison import prepare_geometry_comparison
        result=prepare_geometry_comparison(args.suite,args.output,args.steps_per_seed,args.batch,args.rounds,args.seeds,args.data,mastery=True)
        print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
    elif args.command=='run-geometry-comparison':
        from fly_rl.training.geometry_comparison import run_geometry_comparison
        print(json.dumps(run_geometry_comparison(args.configuration,args.output,args.device),indent=2))
    elif args.command=='plot-validation-failures':
        from fly_rl.visualization.validation_failures import plot_validation_failures
        result=plot_validation_failures(args.experiments,args.output)
        print(json.dumps({k:v for k,v in result.items() if k!='experiments'},indent=2))
    elif args.command=='prepare-fresh-comparison':
        from fly_rl.training.fresh_sensor_comparison import prepare_fresh_comparison
        result=prepare_fresh_comparison(args.suite,args.output,args.steps_per_seed,args.batch,args.rounds,args.seeds,args.data)
        print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
    elif args.command=='run-fresh-comparison':
        from fly_rl.training.fresh_sensor_comparison import run_fresh_comparison
        print(json.dumps(run_fresh_comparison(args.configuration,args.output,args.device),indent=2))
    elif args.command=='compare-sensors':
        from fly_rl.training.sensor_comparison import run_comparison
        print(json.dumps(run_comparison(args.data,args.device,args.suite,args.baseline,args.output),indent=2),flush=True)
    elif args.command=='migrate-sensors':
        from fly_rl.training.sensor_migration import migrate_sensors
        print(json.dumps(migrate_sensors(args.source,args.output,args.target),indent=2))
    elif args.command=='prepare-data':
        from fly_rl.connectome.data import prepare
        write_report('data-audit.json',prepare(args.data))
    elif args.command=='benchmark': write_report('benchmark.json',benchmark(args.data,args.device,args.seconds))
    elif args.command=='evaluate':
        from fly_rl.training.evaluation import evaluate
        if args.suite:
            from fly_rl.training.suites import load_suite
            suite=load_suite(args.suite);seeds=suite['splits'][args.split]['seeds']
            from fly_rl.simulation.map_profiles import resolve_profile
            if args.map_profile and resolve_profile(args.map_profile)!=resolve_profile(suite.get('map_profile')):parser.error('Map profile differs from frozen suite')
            args.map_profile=suite.get('map_profile')
            if args.episodes>len(seeds): parser.error('More episodes than frozen split layouts')
            if args.split=='test':
                if not args.expose_test: parser.error('Use final-test or explicitly acknowledge --expose-test')
                from fly_rl.training.test_access import claim_test
                claim_test(suite,'generic evaluate: '+args.output)
            args.mode=suite['mode'];args.seed=seeds[0]
            if seeds[:args.episodes]!=list(range(args.seed,args.seed+args.episodes)): parser.error('Noncontiguous evaluation seeds')
        from fly_rl.simulation.sensors import SENSOR_V3
        result=evaluate(args.data,args.device,args.checkpoint,args.episodes,args.mode,args.seed,args.goal_probe,args.dynamics,args.transfer,args.route_metrics,sensor_version=SENSOR_V3 if args.map_profile and not args.checkpoint else None,map_profile=args.map_profile)
        result['suite']=args.suite;result['split']=args.split if args.suite else None
        output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
    elif args.command=='select-policy':
        from fly_rl.training.selection import select_policy
        print(json.dumps(select_policy(args.iteration,args.output),indent=2),flush=True)
    elif args.command=='plot-training':
        from fly_rl.visualization.plotting import plot_training
        print(json.dumps(plot_training(args.iteration,args.output,args.independent),indent=2),flush=True)
    elif args.command=='prepare-suite':
        from fly_rl.training.suites import prepare_suite
        print(json.dumps(prepare_suite(args.output,args.train_start,args.validation_start,args.test_start,args.train_count,args.validation_count,args.test_count,args.exclude_suite,args.map_profile,args.training_profiles),indent=2),flush=True)
    elif args.command=='train-dense':
        from fly_rl.training.dense_training import train_dense
        write_report('dense-training.json',train_dense(args.data,args.device,args.suite,args.output,args.baseline,args.steps,args.batch,args.dynamics,args.rounds,args.training_seed,not args.no_promote,args.route_metrics,curriculum='geometry-v2-practice-mastery' if args.mastery else None,mastery=args.mastery,continuous_episodes=args.continuous_episodes,gamma=args.gamma,timeout_as_terminal=args.timeout_as_terminal,target_envs=args.target_envs))
    elif args.command=='prepare-risk-comparison':
        from fly_rl.training.risk_comparison import prepare_risk_comparison
        result=prepare_risk_comparison(args.suite,args.output,args.steps_per_seed,args.batch,args.rounds,args.seeds,args.data)
        print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
    elif args.command=='run-risk-comparison':
        from fly_rl.training.risk_comparison import run_risk_comparison
        print(json.dumps(run_risk_comparison(args.configuration,args.output,args.device),indent=2))
    elif args.command=='prepare-approach-comparison':
        from fly_rl.training.approach_comparison import prepare_approach_comparison
        result=prepare_approach_comparison(args.suite,args.output,args.steps_per_seed,args.batch,args.rounds,args.seeds,args.data)
        print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
    elif args.command=='run-approach-comparison':
        from fly_rl.training.approach_comparison import run_approach_comparison
        print(json.dumps(run_approach_comparison(args.configuration,args.output,args.device),indent=2))
    elif args.command=='trace-validation':
        from fly_rl.training.validation_trace import trace_validation
        print(json.dumps(trace_validation(args.data,args.device,args.experiment,args.output,args.count,args.max_steps,args.kind),indent=2))
    elif args.command=='diagnose-collisions':
        from fly_rl.training.collision_diagnostics import diagnose_collisions
        result=diagnose_collisions(args.source,args.output)
        print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    elif args.command=='plot-validation-trace':
        from fly_rl.visualization.validation_trace import plot_validation_trace
        print(json.dumps(plot_validation_trace(args.source,args.output),indent=2))
    elif args.command=='diagnose-validation':
        from fly_rl.training.diagnostics import failure_report
        result=failure_report(args.source);output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    elif args.command=='select-experiment':
        from fly_rl.training.experiment_selection import select_experiment
        print(json.dumps(select_experiment(args.experiments,args.output),indent=2))
    elif args.command=='plot-dense':
        from fly_rl.visualization.dense_report import plot_dense
        print(json.dumps(plot_dense(args.experiment,args.output),indent=2),flush=True)
    elif args.command=='plot-generalization':
        from fly_rl.visualization.generalization_report import plot_generalization
        print(json.dumps(plot_generalization(args.experiment,args.output),indent=2))
    elif args.command=='final-test':
        from fly_rl.training.generalization import final_test
        print(json.dumps(final_test(args.data,args.device,args.experiment),indent=2),flush=True)
    elif args.command=='iterate':
        from fly_rl.training.iteration import iterate
        write_report('iteration.json',iterate(args.data,args.device,args.output,args.baseline,
            args.steps_per_round,args.rounds,args.batch,args.dynamics))
    elif args.command in ['inspect','recover','compare']:
        from fly_rl.recordings.archive import Archive,recover,compare
        if args.command=='inspect': result=Archive(args.archive).inspect()
        elif args.command=='recover': result=recover(args.archive,args.apply)
        else: result=compare(args.left,args.right)
        output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2),flush=True)
        if args.command=='inspect' and result['errors']: raise SystemExit(1)
    elif args.command=='train-panorama':
        from fly_rl.training.panorama_navigation import run
        write_report('panorama-training.json',run(args.plan,args.device))
    elif args.command=='train-waypoint':
        from fly_rl.training.waypoint_navigation import run
        write_report('last-waypoint-training.json',run(args.plan,args.device))
    elif args.command=='train-spatial':
        from fly_rl.training.spatial_navigation import run
        write_report('last-spatial-training.json',run(args.plan,args.device))
    elif args.command=='train-guarded':
        from fly_rl.training.guarded_navigation import run_guarded_navigation
        write_report('last-guarded-training.json',run_guarded_navigation(args.plan,args.device))
    elif args.command=='train-guided':
        from fly_rl.training.guided_learning import run_guided
        write_report('last-guided-training.json',run_guided(args.plan,args.device))
    elif args.command in ['demo','replay']:
        if args.command=='demo' and args.architecture_scene:
            from fly_rl.simulation.sensors import SENSOR_V6
            if args.sensor_version and args.sensor_version!=SENSOR_V6:
                parser.error('Architectural demo requires the v6 sensor contract')
            if args.checkpoint or args.map_profile:
                parser.error('Architectural demo requires its own scene contract; omit checkpoint and map-profile')
            if not 0 <= args.situation < len(BUILDERS[args.architecture_scene]().situations):
                parser.error('Unknown architectural situation index')
            args.controller='observed-map'
        if not np.isfinite(args.speed) or args.speed<=0:
            parser.error('Simulation speed must be finite and positive')
        from fly_rl.visualization.viewer import run
        run(args)
    else:
        from fly_rl.training.learning import train
        if args.command=='smoke-test':
            write_report('smoke-test.json',train(args.data,args.device,128,1,'runs/smoke/policy.zip',smoke=True,dynamics=args.dynamics))
        else:
            seeds=None
            if args.suite:
                from fly_rl.training.suites import load_suite
                suite=load_suite(args.suite);args.mode=suite['mode'];seeds=suite['splits']['train']['seeds']
                from fly_rl.simulation.map_profiles import resolve_profile
                if args.map_profile and resolve_profile(args.map_profile)!=resolve_profile(suite.get('map_profile')):parser.error('Map profile differs from frozen suite')
                args.map_profile=suite.get('map_profile')
            from fly_rl.simulation.sensors import SENSOR_V3
            result=train(args.data,args.device,args.steps,args.batch,args.output,args.resume,mode=args.mode,layout_seeds=seeds,
                dynamics=args.dynamics,allow_transfer=args.transfer,map_profile=args.map_profile,sensor_version=args.sensor_version or (SENSOR_V3 if args.map_profile and not args.resume else None),gamma=args.gamma,timeout_as_terminal=args.timeout_as_terminal,history_frames=args.history_frames,history_stride=args.history_stride,transfer_history=args.transfer_history,reward_shaping=args.reward_shaping)
            result['suite']=args.suite
            write_report('last-training.json',result)

if __name__=='__main__': main()
