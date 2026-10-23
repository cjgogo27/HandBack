"""Offline-only reconstruction of the frozen task predicate from raw body poses/contacts.
No runtime success flags are used as input. No robot environment or actions are started.
"""
from pathlib import Path
import ast,json,gzip,hashlib
import numpy as np
import mujoco
S=Path('artifact://guava_collection_pair_20261018_v1/src')
OBJECTS=('basket','tomato','can','potato','pear')

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def original_score():
    source=S/'guava/sim/tasks/red_objects_in_basket.py';tree=ast.parse(source.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='score_state'];assert len(nodes)==1
    namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
    return namespace['score_state']

def state_from_raw(names,sample):
    geoms=names['geoms'];bodies=names['bodies'];assert len(geoms)==len(set(geoms)) and len(bodies)==len(set(bodies))
    groups={n:{i for i,g in enumerate(geoms) if g and g.startswith(n+'_')} for n in OBJECTS}
    groups['table']={i for i,g in enumerate(geoms) if g and g.startswith('table')}
    left={geoms.index('gripper0_right_'+g) for g in ['link7_pad_collision','link7_tip_contact']}
    right={geoms.index('gripper0_right_'+g) for g in ['link8_pad_collision','link8_tip_contact']}
    assert all(groups.values())
    def touches(group,target,filtered=False):
        for c in sample['contacts']:
            if filtered and c['distance']>.002:continue
            if (c['g1'] in group and c['g2'] in target) or (c['g2'] in group and c['g1'] in target):return True
        return False
    pairs=[]
    for i,a in enumerate(groups):
        for b in list(groups)[i+1:]:
            if touches(groups[a],groups[b],True):pairs.append([a,b])
    objects={}
    for n in OBJECTS:
        bid=bodies.index(n+'_main');rotation=np.empty(9);mujoco.mju_quat2Mat(rotation,np.asarray(sample['body_xquat'][bid],dtype=float))
        objects[n]=dict(pos=sample['body_xpos'][bid],rotation=rotation.reshape(3,3).tolist(),held=touches(left,groups[n]) and touches(right,groups[n]))
    # Constants are the immutable RedObjectsInBasket Piper constructor values.
    # Visual-only/bbox geom names never enter raw contacts; prefix sets intersect only real contacts.
    return dict(objects=objects,contacts=pairs,table_xyz=[0.,0.,.8],table_half_xy=[.3,.3])

def audit_episode(output):
    D=Path(output);names=json.loads((D/'physical_model_names.json').read_text());res=json.loads((D/'result.json').read_text());summary=json.loads((D/'evaluation/summary.json').read_text());total=res['physics_samples']
    expected=list(range(total-38,total+1,2));wanted=set(expected+[total-40]);samples={}
    with gzip.open(D/'physical_state.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line)
            if r['step'] in wanted and r['phase'] in ['initial','control_step']:samples[r['step']]=r
    assert set(samples)==wanted and len(expected)==20
    score=original_score();scores={k:score(state_from_raw(names,v)) for k,v in samples.items()}
    before=scores[total-40];first=[scores[k] for k in expected[:10]];extra=[scores[k] for k in expected[10:]]
    assert before['success']==bool(summary['original_success'])==bool(res['original_success']), 'independent terminal predicate discrepancy'
    assert [s['success'] for s in first]==summary['hold'], 'independent first-ten hold predicate discrepancy'
    stored=json.loads((D/'post_terminal_hold.json').read_text());assert len(stored)==10
    assert all(a['checks']==b['score']['checks'] and a['success']==b['original_success'] for a,b in zip(extra,stored)), 'independent audit-hold checks discrepancy'
    return dict(output=str(D),independent_predicate_reconstructed=True,terminal=before,registered_ten_holds=first,additional_audit_holds=extra,source_sha256={str(p):digest(p) for p in [S/'guava/sim/tasks/red_objects_in_basket.py',S/'guava/sim/scoring.py',S/'piper/robosuite_piper/piper_gripper.py']},physical_log_sha256=digest(D/'physical_state.jsonl.gz'),runtime_flags_used_as_input=False,hidden_state_used_only_offline=True,geometry_collision_or_hardware_certificate=False)

def self_test():
    score=original_score()
    I=np.eye(3).tolist()
    st=dict(objects={n:dict(pos=[0.,0.,.84],rotation=I,held=False) for n in OBJECTS},contacts=[['basket','table'],['tomato','basket'],['can','basket'],['potato','table'],['pear','table']],table_xyz=[0,0,.8],table_half_xy=[.3,.3])
    st['objects']['basket']['pos']=[.1,.1,.8]
    for n in ['tomato','can']:st['objects'][n]['pos']=[.1,.1,.85]
    for n in ['potato','pear']:st['objects'][n]['pos']=[-.2,-.2,.82]
    assert score(st)['success']
    st['objects']['can']['held']=True;assert not score(st)['success'];st['objects']['can']['held']=False
    st['objects']['can']['pos']=[-.2,0,.85];assert not score(st)['success']
    return dict(correct_geometry_and_contacts_pass=True,held_object_rejected=True,outside_object_rejected=True)
