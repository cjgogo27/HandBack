"""Small causal-prefix prototype. No simulator, snapshot, future labels, or file access."""
import json,math
import numpy as np
FEATURE_NAMES=['teacher_fraction','remaining_fraction','last_tool_ok','public_failure_fraction','mean_past_teacher_nll','last_past_teacher_nll','last_move','last_grasp','last_release','last_perception']

def public_features(*,teacher_count,prior_decisions,past_actions,past_target_nll):
 assert teacher_count in [1,2,4] and 0<=prior_decisions<25
 teachers=[a for a in past_actions if a['owner']=='teacher'];assert len(teachers)==teacher_count
 assert len(past_target_nll)==teacher_count and all(math.isfinite(float(v)) for v in past_target_nll)
 def failure(a):
  if not a['ok']:return True
  try:d=json.loads(a['result']) if isinstance(a['result'],str) else a['result']
  except (TypeError,ValueError):return False
  return isinstance(d,dict) and (d.get('landed') is False or d.get('motion') in ['failed','failure','move_short'] or d.get('execution') in ['partial','failed'])
 last=teachers[-1];name=last['name']
 return np.array([teacher_count/4,(25-prior_decisions)/25,float(last['ok']),sum(failure(a) for a in teachers)/4,float(np.mean(past_target_nll)),float(past_target_nll[-1]),float(name=='move'),float(name=='grasp'),float(name=='release'),float(name in ['get_position','get_position_and_size'])])

def fit_linear(X,y,logistic=False):
 X=np.asarray(X,float);y=np.asarray(y,float);mu=X.mean(0);sd=X.std(0);sd[sd<1e-8]=1
 Z=np.column_stack([np.ones(len(X)),(X-mu)/sd]);penalty=np.diag([0.]+[1.]*X.shape[1]);b=np.zeros(Z.shape[1])
 if logistic:
  # Fixed L2=1; no threshold tuning on held-out parent.
  for _ in range(50):
   p=1/(1+np.exp(-np.clip(Z@b,-30,30)));g=Z.T@(p-y)+penalty@b;H=Z.T@((p*(1-p))[:,None]*Z)+penalty+np.eye(len(b))*1e-8
   delta=np.linalg.solve(H,g);b-=delta
   if np.max(np.abs(delta))<1e-9:break
 else:b=np.linalg.solve(Z.T@Z+penalty+np.eye(len(b))*1e-8,Z.T@y)
 return {'mean':mu.tolist(),'scale':sd.tolist(),'coef':b.tolist(),'logistic':logistic,'feature_names':FEATURE_NAMES}

def predict(model,x):
 z=np.r_[1,(np.asarray(x)-model['mean'])/model['scale']];v=float(z@model['coef'])
 return 1/(1+math.exp(-max(-30,min(30,v)))) if model['logistic'] else v

def choose(feature_at,models,kind):
 assert kind in ['learning_value','returnability','fixed4']
 if kind=='fixed4':return {'selected':4,'trace':[],'abstained':False}
 trace=[]
 for k in [1,2,4]:
  x=feature_at(k);p=predict(models['support'],x)
  if kind=='returnability':stop=p>=.5;qs=qc=None
  else:
   qs=predict(models['stop'],x);qc=predict(models['continue'],x) if k<4 else None
   stop=p>=.5 and (k==4 or qs>=qc)
  trace.append({'k':k,'support_probability':p,'stop_value':qs,'continue_value':qc,'return_now':bool(stop)})
  if stop:return {'selected':k,'trace':trace,'abstained':False}
 return {'selected':None,'trace':trace,'abstained':True}

def self_test():
 const=lambda value,logistic=False:{'mean':[0]*10,'scale':[1]*10,'coef':[value]+[0]*10,'logistic':logistic}
 models={'support':const(10,True),'stop':const(1),'continue':const(0)}
 reads=[]
 def current(k):
  reads.append(k)
  if k>1:raise AssertionError('future feature was accessed despite returning at first step')
  return np.zeros(10)
 r=choose(current,models,'learning_value');assert r['selected']==1 and reads==[1]
 # Future hidden data has no argument in the feature extractor.
 try:public_features(teacher_count=1,prior_decisions=1,past_actions=[],past_target_nll=[],snapshot={})
 except TypeError:pass
 else:raise AssertionError('hidden snapshot unexpectedly accepted')
 try:public_features(teacher_count=1,prior_decisions=1,past_actions=[{'owner':'teacher'}]*4,past_target_nll=[1])
 except AssertionError:pass
 else:raise AssertionError('future action tail accepted')
 return {'future_accessor_not_read':True,'hidden_input_rejected':True,'future_action_tail_rejected':True}
if __name__=='__main__':print(json.dumps(self_test()))
