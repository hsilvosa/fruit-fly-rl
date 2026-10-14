"""Fresh-pool confirmation of run 601 and stochastic-versus-deterministic check (pool 880000, 64 episodes). Evaluation only."""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

MID = 'scripts/profiles/passages-mid.json'
OUT = 'runs/verification/committee-evals'
os.makedirs(OUT, exist_ok=True)
R601 = 'runs/training/random-run/seed601/stage-3.zip'
PILOT = 'runs/training/phase1-pilot/seed442/stage-3.zip'
S505 = 'runs/training/variance-study/seed505/stage-3.zip'
jobs = []
for name, prof in (('passages-wide', 'passages-wide'), ('passages-mid', MID), ('passages', 'passages'), ('medium', 'none')):
    out = f'{OUT}/seed601-{name}.json'
    if not os.path.exists(out):
        jobs.append(([sys.executable, '-s', 'scripts/eval_cell.py', R601, prof, '880000', '64', out], {}))
for label, ck in (('pilot', PILOT), ('seed505', S505)):
    for name, prof in (('passages-wide', 'passages-wide'), ('passages', 'passages')):
        out = f'{OUT}/stochastic-{label}-{name}.json'
        if not os.path.exists(out):
            jobs.append(([sys.executable, '-s', 'scripts/eval_cell.py', ck, prof, '880000', '64', out], {'STOCHASTIC': '1'}))
# the guard runs a list of commands; environment is passed through the command via env wrapper
cmds = []
for cmd, env in jobs:
    if env:
        cmds.append([sys.executable, '-s', '-c', "import os,sys,runpy; os.environ['STOCHASTIC']='1'; sys.argv=%r; runpy.run_path('scripts/eval_cell.py', run_name='__main__')" % (cmd[2:],)])
    else:
        cmds.append(cmd)
run_limited(cmds)
print('done')
