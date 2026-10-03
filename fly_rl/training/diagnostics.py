"""Classify retained validation outcomes without running policy evaluation."""
import json
from pathlib import Path
from collections import Counter


def failure_report(source):
    data = json.loads(Path(source).read_text(encoding='utf-8'))
    measured = data.get('validation', data)
    if data.get('split') == 'test' or 'selected_summary' in data:
        raise ValueError('Failure diagnostics for tuning must use validation, not final-test records')
    rows = measured['episodes']; categories = Counter()
    for row in rows: categories[outcome_label(row)] += 1
    return {'source': str(source), 'episodes': len(rows), 'categories': dict(categories),
            'training_invoked': False, 'evaluation_invoked': False,
            'limits': 'Outcome heuristics. Old summaries lack collision positions/altitude histories; do not infer their causes.'}


def outcome_label(row):
    if row['success']: return 'success'
    if row.get('collision'): return 'collision_location_unknown'
    if row.get('idle_fraction',0)>=.25: return 'timeout_with_frequent_stopping'
    if row.get('distance_end',float('inf'))<2: return 'timeout_near_goal'
    return 'timeout_without_arrival'
