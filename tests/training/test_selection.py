import json
import pytest
from fly_rl.training.selection import select_policy

def test_promotion_uses_success_not_last_round_and_preserves_source(tmp_path):
    results=[]
    for i,success in enumerate([.875,.5]):
        checkpoint=tmp_path/f'round-{i}.zip';checkpoint.write_bytes(b'checkpoint-'+bytes([i]))
        checkpoint.with_suffix('.json').write_text(json.dumps({'fingerprint':'same'}))
        results.append({'checkpoint':str(checkpoint),'obstacles':{'success_rate':success,
            'collision_rate':1-success,'mean_distance_end':1.}})
    source=tmp_path/'iteration.json';source.write_text(json.dumps({'results':results}))
    destination=tmp_path/'selected.zip'
    before=(tmp_path/'round-0.zip').read_bytes()
    report=select_policy(source,destination)
    assert report['success_rate']==.875 and destination.read_bytes()==before
    assert (tmp_path/'round-0.zip').read_bytes()==before
    assert json.loads(destination.with_suffix('.json').read_text())['fingerprint']=='same'
    source.write_text(json.dumps({'results':[]}))
    with pytest.raises(ValueError): select_policy(source,destination)
