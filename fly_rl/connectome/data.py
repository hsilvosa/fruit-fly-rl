"""Public MaleCNS data download, auditing, and sparse graph preparation."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.feather as feather
from scipy import sparse
import requests

BASE = 'https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'
FILES = {
    'annotations': 'body-annotations-male-cns-v1.0-minconf-0.5.feather',
    'neurotransmitters': 'body-neurotransmitters-male-cns-v1.0.feather',
    'weights': 'connectome-weights-male-cns-v1.0-minconf-0.5.feather',
}

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def download(root):
    raw = Path(root) / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    previous = json.loads((raw/'manifest.json').read_text()) if (raw/'manifest.json').exists() else {}
    manifest = {}
    for name in FILES.values():
        path = raw / name
        if not path.exists():
            tmp = path.with_suffix('.part')
            print('Downloading', name, flush=True)
            with requests.get(BASE+name, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                size = int(r.headers.get('content-length', 0))
                count = 0; last = time.monotonic()
                with tmp.open('wb') as out:
                    for block in r.iter_content(4*1024*1024):
                        out.write(block); count += len(block)
                        if time.monotonic()-last > 20:
                            print(f'{count/1e6:.0f}/{size/1e6:.0f} MB', flush=True)
                            last = time.monotonic()
                if size and count != size:
                    raise RuntimeError('Incomplete download: '+name)
            tmp.replace(path)
        digest = sha256(path)
        if name in previous and digest != previous[name]['sha256']:
            raise RuntimeError('Cached data checksum mismatch: '+name)
        manifest[name] = {'url': BASE+name, 'bytes': path.stat().st_size, 'sha256': digest}
    (raw/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    return manifest

def prepare(root):
    root = Path(root)
    manifest = download(root)
    annotations = feather.read_table(root/'raw'/FILES['annotations']).to_pandas()
    nt = feather.read_table(root/'raw'/FILES['neurotransmitters']).to_pandas()
    print('Annotation columns:', list(annotations.columns), flush=True)
    print('NT columns:', list(nt.columns), flush=True)
    # Feather stores dataframe indices as explicit columns; schemas are validated below.
    id_col = next((x for x in ['body', 'bodyId', 'body_id', 'segment', '__index_level_0__'] if x in annotations), None)
    if id_col is None:
        raise ValueError('Unknown neuron-ID schema: '+str(annotations.columns))
    # The annotation file also lists glia, orphans, and out-of-scope segments.
    # Retain every traced neuron and every superclass-annotated neuronal body,
    # excluding explicitly non-neuronal/orphan/unimportant segments.
    neuronal=(annotations['status'].eq('Traced') | annotations['superclass'].notna())
    neuronal &= ~annotations['status'].isin(['Glia','Orphan','Unimportant'])
    ids = np.unique(annotations.loc[neuronal,id_col].to_numpy(dtype=np.int64))
    if len(ids) < 100000:
        raise ValueError('Unexpectedly small annotated neuron universe')
    n = len(ids)
    signs = np.ones(n, dtype=np.float32)
    ntid = next((x for x in [id_col, 'body', 'bodyId', '__index_level_0__'] if x in nt), None)
    ntcol = next((x for x in ['predicted_nt', 'nt_type', 'neurotransmitter', 'consensus_nt', 'nt'] if x in nt), None)
    if ntid is None or ntcol is None:
        raise ValueError('Unknown neurotransmitter schema')
    gaba_ids = nt.loc[nt[ntcol].astype(str).str.lower().eq('gaba'), ntid].to_numpy(dtype=np.int64)
    signs[np.isin(ids, gaba_ids)] = -1
    graph_path = root/'raw'/FILES['weights']
    rows=[]; cols=[]; values=[]; all_edges=0; excluded=0; synapses=0
    with pa.memory_map(str(graph_path), 'r') as source:
        reader=ipc.open_file(source)
        print('Connection schema:', reader.schema, flush=True)
        names=reader.schema.names
        pre=next((x for x in ['body_pre','bodyId_pre','pre'] if x in names), None)
        post=next((x for x in ['body_post','bodyId_post','post'] if x in names), None)
        strength=next((x for x in ['weight','syn_count','count'] if x in names), None)
        if None in (pre,post,strength): raise ValueError('Unknown connection schema')
        for batch_index in range(reader.num_record_batches):
            b=reader.get_batch(batch_index)
            p=b.column(names.index(pre)).to_numpy().astype(np.int64)
            q=b.column(names.index(post)).to_numpy().astype(np.int64)
            w=b.column(names.index(strength)).to_numpy().astype(np.float32)
            i=np.searchsorted(ids,p); j=np.searchsorted(ids,q)
            valid=(i<n)&(j<n)
            valid &= (ids[np.minimum(i,n-1)]==p)&(ids[np.minimum(j,n-1)]==q)
            if not np.isfinite(w).all() or (w<=0).any(): raise ValueError('Invalid source weights')
            all_edges+=len(w); excluded+=int((~valid).sum())
            rows.append(j[valid].astype(np.int32)); cols.append(i[valid].astype(np.int32)); values.append(w[valid])
            synapses+=int(w[valid].sum(dtype=np.float64))
    row=np.concatenate(rows); col=np.concatenate(cols); count=np.concatenate(values)
    counts=sparse.coo_matrix((count,(row,col)),shape=(n,n)).tocsr()
    counts.sum_duplicates()
    incoming=np.asarray(counts.sum(axis=1)).ravel()
    graph=counts.copy()
    graph.data *= signs[graph.indices]
    graph.data *= np.repeat(0.9/np.maximum(incoming,1),np.diff(graph.indptr))
    out=root/'processed'; out.mkdir(parents=True,exist_ok=True)
    sparse.save_npz(out/'synapse_counts.npz',counts)
    sparse.save_npz(out/'brain.npz',graph)
    np.save(out/'neuron_ids.npy',ids)
    np.save(out/'neuron_signs.npy',signs)
    processed_hashes={p.name:sha256(p) for p in out.glob('*.np*')}
    fingerprint=hashlib.sha256(json.dumps({'raw':manifest,'processed':processed_hashes},sort_keys=True).encode()).hexdigest()
    audit={'dataset':'MaleCNS v1.0','fingerprint':fingerprint,'annotated_neurons':n,
           'edges':int(graph.nnz),'source_edges':all_edges,'excluded_fragment_edges':excluded,
           'annotation_rows':len(annotations),'excluded_annotation_rows':int((~neuronal).sum()),
           'neuron_selection':'(status=Traced OR superclass assigned) AND status not in Glia,Orphan,Unimportant',
           'synapses':synapses,'isolated_neurons':int(((counts.getnnz(axis=0)+counts.getnnz(axis=1))==0).sum()),
           'gaba_neurons':int((signs<0).sum()),'all_annotated_neurons_retained':True,
           'orientation':'matrix[postsynaptic, presynaptic]',
           'source':'https://male-cns.janelia.org/download/',
           'license':'CC-BY 4.0','attribution':'HHMI Janelia FlyEM, University of Cambridge, MRC LMB, Google Research',
           'assumptions':'GABA negative; other or unknown NT positive. Synthetic sensory projection. Tanh leaky dynamics.',
           'raw_files':manifest,
           'processed_files':processed_hashes}
    (out/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['raw_files','processed_files']},indent=2),flush=True)
    return audit
