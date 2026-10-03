import numpy as np
import pytest
from fly_rl.connectome.anatomy import join_positions,display_positions

def test_join_respects_brain_order_and_omits_missing_coordinates():
    ids=np.array([90,12,44,21])
    result=join_positions(ids,[
        {'bodyId':21,'somaLocation':[3,5,8],'type':'motor','somaNeuromere':'T1','superclass':'motor'},
        {'bodyId':44,'somaLocation':None},
        {'bodyId':999,'somaLocation':[0,0,0]},
        {'bodyId':90,'somaLocation':[1,2,4],'superclass':'central'},
        {'bodyId':12,'somaLocation':[np.nan,2,3]}])
    np.testing.assert_array_equal(result['indices'],[0,3])
    np.testing.assert_array_equal(result['raw_positions'],[[1,2,4],[3,5,8]])
    assert result['types']==['central','motor']
    assert result['total_neurons']==4
    assert result['regions'].tolist()==['Unassigned neuromere','T1']
    assert result['classes'].tolist()==['central','motor']

def test_display_preserves_relative_anatomical_distances():
    raw=np.array([[10,20,30],[10,23,34],[16,20,30]],dtype=float)
    shown=display_positions(raw)
    original=np.linalg.norm(raw[:,None]-raw[None,:],axis=-1)
    transformed=np.linalg.norm(shown[:,None]-shown[None,:],axis=-1)
    np.testing.assert_allclose(transformed,original/3,rtol=1e-6)
    assert np.isfinite(shown).all()
    with pytest.raises(ValueError,match='Degenerate'): display_positions(np.ones((2,3)))
