from fly_rl.training.generalization import summarize


def test_route_quality_counts_successes_and_discloses_missing_references():
    measured = {'route_metrics': True, 'collision_rate': .25, 'timeout_rate': .25, 'episodes': [
        dict(success=True, steps=20, distance_start=10, path_length=14, path_over_feasible_reference=1.2),
        dict(success=True, steps=30, distance_start=10, path_length=18, path_over_feasible_reference=None),
        dict(success=False, steps=10, distance_start=10, path_length=1, path_over_feasible_reference=.1),
        dict(success=False, steps=40, distance_start=10, path_length=2, path_over_feasible_reference=None)]}
    result = summarize(measured)
    assert result['successes'] == 2 and result['mean_success_path_length'] == 16
    assert result['mean_success_arrival_seconds'] == 1.25
    assert result['mean_success_path_over_feasible_reference'] == 1.2
    assert result['successful_reference_count'] == 1 and result['reference_missing_successes'] == 1
    assert 'approximate' in result['route_reference']
