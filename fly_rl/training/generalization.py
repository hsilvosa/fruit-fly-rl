"""Evaluate a frozen selection once; test outcomes never select or change weights."""
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime,timezone
from fly_rl.training.suites import load_suite
from fly_rl.training.evaluation import evaluate
from fly_rl.simulation.world import DT

def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''): digest.update(chunk)
    return digest.hexdigest()

def summarize(result):
    rows=result['episodes'];n=len(rows);k=sum(r['success'] for r in rows);p=k/n;z=1.959963984540054
    denominator=1+z*z/n;center=(p+z*z/(2*n))/denominator
    margin=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    successful=[r for r in rows if r['success']]
    ratios=[r['path_over_feasible_reference'] for r in successful if r.get('path_over_feasible_reference') is not None]
    return {'episodes':n,'successes':k,'success_rate':p,'success_wilson_95':[center-margin,center+margin],
        'collision_rate':result['collision_rate'],'timeout_rate':result['timeout_rate'],
        'mean_success_arrival_seconds':sum(r['steps']*DT for r in successful)/len(successful) if successful else None,
        'mean_success_path_length':sum(r['path_length'] for r in successful)/len(successful) if successful else None,
        'mean_success_path_over_straight_line':sum(r['path_length']/r['distance_start'] for r in successful)/len(successful) if successful else None,
        'mean_success_path_over_feasible_reference':sum(ratios)/len(ratios) if ratios else None,
        'successful_reference_count':len(ratios),'reference_missing_successes':len(successful)-len(ratios),
        'route_reference':'clearance-aware sampled visibility roadmap; approximate geometric path to goal center, not a global/dynamic optimum' if result.get('route_metrics') else 'straight-line lower bound; not an obstacle-aware optimal route'}

def final_test(data,device,experiment):
    folder=Path(experiment);state=json.loads((folder/'experiment.json').read_text())
    if state['status']!='completed': raise ValueError('Training must finish before the final test')
    frozen=json.loads((folder/'selection.json').read_text());checkpoint=Path(frozen['checkpoint']);suite_path=Path(frozen['suite'])
    for path,expected in [(checkpoint,frozen['checkpoint_sha256']),(checkpoint.with_suffix('.json'),frozen['metadata_sha256']),
                          (suite_path,frozen['suite_sha256'])]:
        if sha256(path)!=expected: raise ValueError('Frozen selection integrity mismatch')
    configuration=frozen.get('evaluation_configuration',{})
    if configuration.get('evaluator_sha256'):
        from fly_rl.training import evaluation as evaluator_module
        from fly_rl.simulation import planner as planner_module
        if sha256(evaluator_module.__file__)!=configuration['evaluator_sha256'] or sha256(planner_module.__file__)!=configuration['planner_sha256']:
            raise ValueError('Frozen evaluation configuration source changed')
    suite=load_suite(suite_path);seeds=suite['splits']['test']['seeds']
    if suite.get('map_profile'):
        from fly_rl.simulation import world as world_module,map_profiles as profiles_module
        if configuration.get('map_profile')!=suite['map_profile'] or configuration.get('world_sha256')!=sha256(world_module.__file__) or configuration.get('map_profiles_sha256')!=sha256(profiles_module.__file__):
            raise ValueError('Frozen profiled evaluation geometry changed')
    if seeds!=list(range(seeds[0],seeds[0]+len(seeds))): raise ValueError('Noncontiguous test suite')
    from fly_rl.training.test_access import claim_test,require_unconsumed
    require_unconsumed(suite)
    report=folder/'final-test.json'
    result={'status':'running','selection':frozen,'split':'test','episodes':len(seeds),
        'started_utc':datetime.now(timezone.utc).isoformat(),'training_invoked':False}
    with report.open('x',encoding='utf8') as handle: json.dump(result,handle,indent=2)
    result['test_access_record']=claim_test(suite,str(folder.resolve()))
    state.update(final_test_evaluated=True,test_report=str(report.resolve()))
    tmp=folder/'experiment.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(folder/'experiment.json')
    def save():
        tmp=report.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2));tmp.replace(report)
    try:
        kwargs={'map_profile':suite['map_profile']} if suite.get('map_profile') else {}
        result['selected']=evaluate(data,device,checkpoint,len(seeds),frozen['mode'],seeds[0],dynamics=frozen['dynamics'],route_metrics=frozen.get('evaluation_configuration',{}).get('route_metrics',False),**kwargs)
        result['selected_summary']=summarize(result['selected']);save()
        result['untrained']=evaluate(data,device,None,len(seeds),frozen['mode'],seeds[0],dynamics=frozen['dynamics'],route_metrics=frozen.get('evaluation_configuration',{}).get('route_metrics',False),sensor_version=frozen.get('evaluation_configuration',{}).get('sensor_version'),**kwargs)
        result['untrained_summary']=summarize(result['untrained'])
        result['success_improvement']=result['selected_summary']['success_rate']-result['untrained_summary']['success_rate']
        if sha256(checkpoint)!=frozen['checkpoint_sha256'] or sha256(checkpoint.with_suffix('.json'))!=frozen['metadata_sha256']:
            raise ValueError('Evaluation modified the frozen checkpoint')
        result.update(status='completed',test_used_for_selection=False)
    except BaseException as exc: result.update(status='failed',error=repr(exc));raise
    finally: result['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return result
