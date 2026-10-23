"""Frozen 07+08 causal-prefix selector. No file I/O or simulator truth at decision time."""
import copy
import numpy as np
from .features import fit_linear,predict,FEATURE_NAMES
KS=(1,2,4)

def select(current_at,kind,models=None,fixed_k=None):
    assert kind in ('V','S1','S2','F')
    if kind=='F':
        assert fixed_k in KS
        return dict(retained_k=fixed_k,handoff=True,trace=[],read_prefixes=[])
    consecutive=0;trace=[]
    for k in KS:
        # Caller may obtain only the current public prefix and its actual background proposal.
        current=current_at(k)
        assert set(current)=={'feature','supported'}
        x=np.asarray(current['feature'],float)
        assert x.shape==(len(FEATURE_NAMES),) and np.isfinite(x).all()
        supported=bool(current['supported']);consecutive=consecutive+1 if supported else 0
        qs=qc=None
        if kind=='V':
            assert models is not None
            qs=predict(models['stop'],x)
            qc=predict(models['continue'],x) if k<4 else None
            early=supported and (k==4 or qs>=qc)
        elif kind=='S1':early=supported
        else:early=consecutive>=2
        trace.append(dict(k=k,supported=supported,consecutive_scheduled_checkpoints=consecutive,stop_value=qs,continue_value=qc,return_now=bool(early)))
        if early:return dict(retained_k=k,handoff=True,trace=trace,read_prefixes=[r['k'] for r in trace])
    # No early return must NOT discard the teacher sequence or replace it with replay.
    return dict(retained_k=4,handoff=False,trace=trace,read_prefixes=[r['k'] for r in trace])

def continue_target(values,supported,k):
    assert k in (1,2)
    if k==2:return float(values[4])
    return float(max(values[4],values[2])) if supported[2] else float(values[4])

def fit_models(records):
    """records are TRAINING labels only; decision select() cannot access this table."""
    assert records
    pairs=[(r,k) for r in records for k in KS]
    stop=fit_linear([r['features'][k] for r,k in pairs],[r['values'][k] for r,k in pairs])
    pairs=[(r,k) for r in records for k in (1,2)]
    cont=fit_linear([r['features'][k] for r,k in pairs],[continue_target(r['values'],r['supported'],k) for r,k in pairs])
    return dict(stop=stop,**{'continue':cont})

def crossfit(records):
    ids=[r['parent'] for r in records];assert len(ids)==len(set(ids)) and len(ids)==6
    folds=[]
    for held in records:
        train=[r for r in records if r['parent']!=held['parent']]
        models=fit_models(train)
        calls=[]
        def at(k):
            calls.append(k)
            return dict(feature=held['features'][k],supported=held['supported'][k])
        d=select(at,'V',models)
        assert calls==d['read_prefixes']
        folds.append(dict(parent=held['parent'],training_parents=[r['parent'] for r in train],models=models,decision=d))
    return dict(folds=folds,deployment_models=fit_models(records),feature_names=FEATURE_NAMES,L2=1.,labels_use_only_other_parents_for_OOF=True,proxy_cost_subtracted=False)

def self_test():
    def constant(v):return dict(mean=[0]*10,scale=[1]*10,coef=[v]+[0]*10,logistic=False)
    models={'stop':constant(1),'continue':constant(0)}
    def now(k):
        assert k==1,'future public features were read despite early handoff'
        return dict(feature=np.zeros(10),supported=True)
    assert select(now,'V',models)['read_prefixes']==[1]
    no=select(lambda k:dict(feature=np.zeros(10),supported=False),'V',models)
    assert no['retained_k']==4 and no['handoff'] is False
    assert continue_target({1:0,2:100,4:2},{1:False,2:False,4:False},1)==2
    assert continue_target({1:0,2:100,4:2},{1:False,2:True,4:False},1)==100
    assert continue_target({1:0,2:100,4:2},{1:False,2:True,4:False},2)==2
    assert select(lambda k:dict(feature=np.zeros(10),supported=k!=2),'S2')['handoff'] is False
    assert select(lambda k:dict(feature=np.zeros(10),supported=True),'S2')['retained_k']==2
    records=[dict(parent=i,features={k:[i*.1+k*.01]*10 for k in KS},values={k:i*.1+k*.01 for k in KS},supported={k:True for k in KS}) for i in range(6)]
    a=crossfit(records);modified=copy.deepcopy(records);modified[0]['values']={k:1000 for k in KS};b=crossfit(modified)
    assert a['folds'][0]['models']==b['folds'][0]['models']
    assert a['folds'][0]['decision']==b['folds'][0]['decision']
    # IDs can only choose the fold: relabeling does not affect coefficients or choices.
    renamed=copy.deepcopy(records)
    for r in renamed:r['parent']+=9900
    c=crossfit(renamed)
    assert a['deployment_models']==c['deployment_models']
    assert [x['decision'] for x in a['folds']]==[x['decision'] for x in c['folds']]
    return dict(early_stop_does_not_read_future=True,no_support_retains_all_four=True,unsupported_future_early_return_excluded=True,held_out_value_mutation_invariant=True,parent_ID_not_feature=True,S2_requires_two_scheduled_checks=True)

if __name__=='__main__':
    import json
    print(json.dumps(self_test()))
