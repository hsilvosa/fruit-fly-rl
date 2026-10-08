"""Official soma positions joined to the complete audited neuron ordering."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pyarrow.feather as feather

def join_positions(ids,rows):
    lookup={int(body):i for i,body in enumerate(ids)}
    indices=[];positions=[];types=[];regions=[];classes=[]
    for row in rows:
        point=row.get('somaLocation');index=lookup.get(int(row['bodyId']))
        if index is None or point is None or len(point)!=3: continue
        if not np.isfinite(point).all(): continue
        indices.append(index);positions.append(point);types.append(row.get('type') or row.get('superclass') or 'unassigned')
        regions.append(row.get('somaNeuromere') or 'Unassigned neuromere')
        classes.append(row.get('superclass') or 'Unassigned superclass')
    order=np.argsort(indices)
    return {'indices':np.asarray(indices,dtype=np.int64)[order],
        'raw_positions':np.asarray(positions,dtype=np.float64).reshape(-1,3)[order],
        'types':[types[i] for i in order],'regions':np.asarray(regions)[order],'classes':np.asarray(classes)[order],'total_neurons':len(ids)}

def load_anatomy(data):
    data=Path(data);ids=np.load(data/'processed'/'neuron_ids.npy',allow_pickle=False)
    audit=json.loads((data/'processed'/'audit.json').read_text())
    name=next(name for name in audit['raw_files'] if name.startswith('body-annotations'))
    source=data/'raw'/name;checksum=hashlib.sha256(source.read_bytes()).hexdigest()
    if checksum!=audit['raw_files'][name]['sha256']: raise ValueError('Anatomical annotation checksum mismatch')
    table=feather.read_table(source,columns=['bodyId','somaLocation','type','superclass','somaNeuromere'])
    anatomy=join_positions(ids,table.to_pylist())
    if not len(anatomy['indices']): raise ValueError('No official soma positions are available')
    anatomy['ids']=ids[anatomy['indices']]
    anatomy['source']={'file':str(source),'sha256':checksum,'coordinate_field':'somaLocation',
        'located_neurons':len(anatomy['indices']),'unlocated_neurons':len(ids)-len(anatomy['indices']),
        'coordinate_units':'native annotation volume coordinates','geometry':'somata only; no neurite morphology'}
    return anatomy

def display_positions(raw):
    center=(raw.min(axis=0)+raw.max(axis=0))*.5
    scale=max(np.ptp(raw,axis=0))*.5
    if scale<=0: raise ValueError('Degenerate anatomical positions')
    result=(raw-center)/scale
    result[:,2]*=-1 # Reflect the displayed vertical axis, preserving anatomical distances.
    return result.astype(np.float32)
