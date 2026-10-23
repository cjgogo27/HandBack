"""Separate raw-log recomputation. Reads completed artifacts only; changes no rollout."""
from pathlib import Path
import json,gzip,hashlib,math

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def raw_peaks(records,geoms,cutoff):
    peak=extra=initial=0.;steps=[];top=None
    for r in records:
        for c in r['contacts']:
            i,j=int(c['g1']),int(c['g2']);assert 0<=i<len(geoms) and 0<=j<len(geoms)
            names=[geoms[i] or '',geoms[j] or ''];distance=float(c['distance']);assert math.isfinite(distance)
            if sum(n.startswith(('gripper0','robot0')) for n in names)!=1:continue
            depth=max(0.,-distance)
            if r['phase']=='initial':initial=max(initial,depth)
            if r['phase']=='control_step':
                if r['step']<=cutoff:
                    if depth>peak:peak=depth;top=dict(step=r['step'],sim_time=r['sim_time'],geoms=names,depth_m=depth)
                else:extra=max(extra,depth)
        if r['phase']=='control_step':steps.append(r['step'])
    assert steps==list(range(1,len(steps)+1)), 'missing or duplicated control samples'
    return peak,extra,initial,top,len(steps)

def audit(row):
    D=Path(row['output']);res=json.loads((D/'result.json').read_text());s=json.loads((D/'evaluation/summary.json').read_text())
    assert res['status']=='recorded'
    exit_proof='explicit_worker_returncode'
    if 'returncode' in row:assert row['returncode']==0
    else:
        # This old four-step controller appended each immutable row ONLY after assert wait()==0.
        # Do not invent a missing return code; verify that exact controller and its completed row.
        root=D.parents[1];controller=root/'job/control4_controller_v1.py';c=json.loads((root/'control4_status.json').read_text())
        assert row['name']=='replay4' and c['state']=='completed_matched_control' and row in c['rows']
        assert sha(controller)=='e578587894a820ccc9f788bb18779a89dad3a43019abc7b0e438a96a047b437e'
        exit_proof='completed_frozen_control4_controller_asserted_worker_wait_equals_zero'
    native=Path(res['native_path']);n=json.loads(native.read_text());m=json.loads(n['metadata']) if isinstance(n['metadata'],str) else n['metadata']
    assert bool(m['success'])==bool(res['original_success'])==bool(s['original_success'])
    assistants=[r for r in n['conversations'] if r['from']=='gpt'];assert assistants and all(r['loss'] is False for r in assistants)
    terminal=assistants[-1]['value'].rstrip().endswith('Task complete.')
    assert terminal==bool(res['terminal_complete'])==(s['terminal']=='Task complete.')
    assert len(s['hold'])==10
    raw=bool(m['success'] and terminal and all(s['hold']))
    assert raw==bool(s['raw_complete_and_held'])
    extra_hold=json.loads((D/'post_terminal_hold.json').read_text());assert len(extra_hold)==10
    assert all(bool(h['score']['success'])==bool(h['original_success']) for h in extra_hold)
    names=json.loads((D/'physical_model_names.json').read_text())['geoms'];total=int(res['physics_samples']);assert total>=40
    final=json.loads((D/'final_physical_state.json').read_text())['state'];assert final['step']==total
    # The immutable worker executes protocol ten holds (2 steps each), then ten additional audit-only holds.
    # Reproduce the registered first-ten-hold metric; additional observations are retained and separately reported.
    with gzip.open(D/'physical_state.jsonl.gz','rt') as f:records=[json.loads(l) for l in f]
    peak,extra,initial,top,observed=raw_peaks(records,names,total-20)
    assert observed==total
    assert abs(peak-s['maximum_external_robot_penetration_m'])<1e-10, 'raw contact discrepancy'
    imgs=[]
    for im in n['images']:
        p=Path(im);assert p.is_file() and p.stat().st_size>0
        imgs.append(dict(path=str(p),sha256=sha(p)))
    assert imgs
    return dict(name=row['name'],seed=row['seed'],output=str(D),raw_complete_and_held=raw,maximum_external_robot_penetration_m=peak,extra_audit_hold_peak_m=extra,initial_peak_m=initial,peak_state=top,control_samples=total,protocol_cutoff_step=total-20,extra_hold_checks=[h['original_success'] for h in extra_hold],joint_2mm=raw and peak<=.002,native_loss_false=True,images_verified=len(imgs),source_sha256={f:sha(D/f) for f in ['physical_state.jsonl.gz','physical_model_names.json','evaluation/summary.json','post_terminal_hold.json','result.json']},native_sha256=sha(native),image_manifest=imgs,independent_contact_recomputation=True,exit_proof=exit_proof,semantic_predicate_replayed_from_model=False,hardware_safety_certified=False)

def self_test():
    rows=[dict(phase='control_step',step=i,sim_time=i,contacts=[dict(g1=0,g2=1,distance=-.001 if i<=20 else -.009)]) for i in range(1,41)]
    a=raw_peaks(rows,['robot0_finger','box'],20);assert a[:2]==(.001,.009)
    try:raw_peaks(rows[1:],['robot0_finger','box'],20)
    except AssertionError:pass
    else:raise AssertionError('missing sample accepted')
    return dict(extra_hold_separated=True,missing_control_sample_rejected=True)
