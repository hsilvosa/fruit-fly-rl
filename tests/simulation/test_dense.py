import numpy as np
from fly_rl.simulation.world import FlightWorld,segment_box,ray_box,RADIUS

def test_dense_layout_has_clear_route_and_varied_endpoints():
    signs=[]
    for seed in range(16):
        w=FlightWorld(seed,'dense');other=FlightWorld(seed,'dense')
        assert np.array_equal(w.room,[32,32,12]) and len(w.obstacles)==48
        assert np.array_equal(w.position,other.position) and np.array_equal(w.target,other.target)
        assert w.distance>=14 and w.episode_limit==1200
        assert w.observation_space.contains(w.observe())
        for low,high in w.obstacles:
            assert (low>=0).all() and (high<=w.room).all()
            for a,b in zip(w.reference_route,w.reference_route[1:]):
                assert not segment_box(a,b,low-RADIUS,high+RADIUS)
        signs.append(w.target[0]>w.position[0])
    assert any(signs) and not all(signs)

def test_vectorized_rays_match_scalar_geometry():
    for mode in ['obstacles','dense']:
        w=FlightWorld(5,mode)
        directions,distances=w.rays()
        for d,value in zip(directions,distances):
            exits=[((w.room[k] if d[k]>0 else 0)-w.position[k])/d[k] for k in range(3) if abs(d[k])>1e-9]
            expected=min([8.]+[v for v in exits if v>=0]+[ray_box(w.position,d,l,h) for l,h in w.obstacles])
            assert np.isclose(value,expected)

def test_training_layout_pool_excludes_validation():
    w=FlightWorld(42,'dense',layout_seeds=[0,1,2])
    seen=set()
    for _ in range(20):
        _,info=w.reset();seen.add(info['room_seed'])
    assert seen=={0,1,2}

def test_frozen_suite_rejects_overlapping_seeds(tmp_path):
    import json,hashlib
    from pathlib import Path
    from fly_rl.training.suites import load_suite
    from fly_rl.simulation.world import WORLD_VERSION
    import fly_rl.simulation.world
    import pytest
    source=Path(fly_rl.simulation.world.__file__)
    suite={'world_version':WORLD_VERSION,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'splits':{'train':{'seeds':[1,2]},'validation':{'seeds':[2,3]},'test':{'seeds':[4]}}}
    path=tmp_path/'suite.json';path.write_text(json.dumps(suite))
    with pytest.raises(ValueError,match='Overlapping'): load_suite(path)
    suite['splits']['validation']['seeds']=[3]
    suite['mode']='dense'
    from fly_rl.training.suites import layout_hash
    for pool in suite['splits'].values(): pool['layout_sha256']=[layout_hash(FlightWorld(s,'dense')) for s in pool['seeds']]
    path.write_text(json.dumps(suite))
    assert load_suite(path)['splits']['test']['seeds']==[4]
    suite['source_sha256']='changed';path.write_text(json.dumps(suite))
    with pytest.raises(ValueError,match='changed'): load_suite(path)
