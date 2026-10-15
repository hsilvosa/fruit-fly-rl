"""Frozen statistics of C1.3: real connectome against the edge-shuffled control, per-seed final-checkpoint counts.
See docs/experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C13.md.

D = mean(real) - mean(shuffled). Welch interval (unequal variances, Welch-Satterthwaite degrees of freedom), because the seeds of the two
arms are independent trainings. Verdicts, evaluated in this order:
  wiring-matters       D >= margin and the 95 percent interval of D is above 0 (the shuffled control learns less)
  shuffled-better      the 95 percent interval of D is below 0 (the real connectome learns less)
  equivalent           the 90 percent interval of D lies inside (-margin, +margin) (two one-sided tests at 5 percent)
  inconclusive         anything else
Usage as a script: connectome_control_stats.py <summary.json>... prints the table for every cell of the merged summaries.
"""
import json, sys
import numpy as np
from scipy import stats

MARGINS = {'passages': 10, 'passages-mid': 10, 'passages-wide': 10, 'medium': 10, 'levelB': 10, 'levelC': 26}
CHAIN_THRESHOLD = 28  # real mean on `passages`, the B2 threshold


def welch_difference(real, shuffled, level=0.95):
    """Return (D, standard error, degrees of freedom, lower, upper) of mean(real) - mean(shuffled)."""
    a, b = np.asarray(real, float), np.asarray(shuffled, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = float(np.sqrt(va + vb))
    if se == 0.0:
        d = float(a.mean() - b.mean())
        return d, 0.0, float('inf'), d, d
    df = float((va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1)))
    half = float(stats.t.ppf(0.5 + level / 2, df) * se)
    d = float(a.mean() - b.mean())
    return d, se, df, d - half, d + half


def verdict(real, shuffled, margin):
    d, se, df, lo95, hi95 = welch_difference(real, shuffled, 0.95)
    _, _, _, lo90, hi90 = welch_difference(real, shuffled, 0.90)
    if d >= margin and lo95 > 0:
        name = 'wiring-matters'
    elif hi95 < 0:
        name = 'shuffled-better'
    elif lo90 > -margin and hi90 < margin:
        name = 'equivalent'
    else:
        name = 'inconclusive'
    return {'difference': d, 'se': se, 'df': df, 'ci95': [lo95, hi95], 'ci90': [lo90, hi90], 'margin': margin, 'verdict': name,
            'real': list(map(float, real)), 'shuffled': list(map(float, shuffled)),
            'real_mean': float(np.mean(real)), 'shuffled_mean': float(np.mean(shuffled))}


def merge(paths):
    rows = {}
    for p in paths:
        rows.update(json.load(open(p)))
    return rows


def successes(rows, label, cell, mode='det'):
    value = rows[label][cell][mode]
    return value['successes']


def analyse(rows, mode='det'):
    real = sorted(k for k in rows if k.startswith('real'))
    shuffled = sorted(k for k in rows if k.startswith('shuffled'))
    out = {'real_runs': real, 'shuffled_runs': shuffled, 'mode': mode, 'cells': {}}
    for cell, margin in MARGINS.items():
        try:
            a = [successes(rows, k, cell, mode) for k in real]
            b = [successes(rows, k, cell, mode) for k in shuffled]
        except KeyError:
            continue
        out['cells'][cell] = verdict(a, b, margin)
    if 'passages' in out['cells']:
        out['chain_check_passes'] = out['cells']['passages']['real_mean'] >= CHAIN_THRESHOLD
    return out


if __name__ == '__main__':
    result = analyse(merge(sys.argv[1:]))
    print('real', result['real_runs'], 'shuffled', result['shuffled_runs'], 'chain check passes', result.get('chain_check_passes'))
    for cell, v in result['cells'].items():
        print(f"{cell:14s} real {v['real_mean']:6.2f} shuffled {v['shuffled_mean']:6.2f} D {v['difference']:+6.2f} "
              f"95% [{v['ci95'][0]:+.1f}, {v['ci95'][1]:+.1f}] 90% [{v['ci90'][0]:+.1f}, {v['ci90'][1]:+.1f}] margin {v['margin']} -> {v['verdict']}")
