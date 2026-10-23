"""Global visual/native-tool support baseline, explicit adaptation, not original robot reproduction."""
import numpy as np,re,json
TOOLS=['move','grasp','align','get_position','get_position_and_size','close_gripper','release','rotate','home_pose']
CATS={'target_name':['can','tomato','basket','potato','pear','other'],'position':['top','bottom','left','right','front','behind','other'],'clearance':['small','large','medium','other'],'motion_mode':['default','preserve_tcp','grasp_center_radial','other'],'axis':['x','y','z','other']}
KEYS={'move':{'target_position','motion_mode'},'grasp':{'target_name'},'align':{'target_name','position','clearance'},'get_position':{'target_name'},'get_position_and_size':{'target_name'},'close_gripper':set(),'release':set(),'rotate':{'angle_deg','axis'},'home_pose':set()}
def encode_action(act):
 name=act['name'];args=act['arguments'];assert name in TOOLS and not (set(args)-KEYS[name]),'unknown tool/parameter: reject instead of drop'
 x=[float(name==t) for t in TOOLS]
 for key,levels in CATS.items():
  value=str(args.get(key,'preserve_tcp' if key=='motion_mode' and name=='move' else 'missing')).lower()
  if key=='target_name':value=next((s for s in levels[:-1] if re.search(r'\b'+s+r'\b',value)),'other') if key in args else 'missing'
  if value not in levels and value!='missing':value='other'
  x.extend(float(value==s) for s in levels+['missing'])
 pos=args.get('target_position',[0.,0.,0.]);assert len(pos)==3
 x.extend([float(v) for v in pos]);x.append(float(args.get('angle_deg',0.)))
 x.extend([float('target_position' in args),float('angle_deg' in args)])
 assert np.isfinite(x).all();return np.asarray(x)
def build(vectors,actions):
 X=np.stack([encode_action(a) for a in actions]);scale=X.std(0);scale[:-6]=np.maximum(scale[:-6],.1);scale[-6:-3]=np.maximum(scale[-6:-3],.01);scale[-3]=max(scale[-3],1.);scale[-2:]=np.maximum(scale[-2:],.1)
 E=np.asarray(vectors);E=E/np.linalg.norm(E,axis=1,keepdims=True);return {'embeddings':E,'actions':X,'scale':scale}
def score(memory,embedding,action):
 q=encode_action(action);e=np.asarray(embedding);e=e/np.linalg.norm(e);s=memory['embeddings']@e;neighbors=np.argsort(-s,kind='stable')[:10];dist=np.linalg.norm((memory['actions'][neighbors]-q)/memory['scale'],axis=1);idx=np.argsort(dist,kind='stable')[:3];chosen=neighbors[idx]
 return {'visual':float(np.mean(s[chosen])),'risk':float(np.mean(dist[idx])),'memory_indices':chosen.tolist()}
def select(score_at,thresholds):
 accepted=0;trace=[]
 for k in [1,2,4]:
  z=score_at(k);yes=z.get('supported_format',True) and z['visual']>=thresholds['visual_lower'] and z['risk']<=thresholds['risk_upper'];accepted=accepted+1 if yes else 0
  trace.append({'k':k,**z,'accept':bool(yes),'consecutive':accepted})
  if accepted>=2:return {'selected':k,'trace':trace,'abstained':False}
 return {'selected':None,'trace':trace,'abstained':True}
def self_test():
 a={'name':'move','arguments':{'target_position':[.2,.1,.15],'motion_mode':'preserve_tcp'}};b={'name':'release','arguments':{}};m=build([[1,0],[0,1],[.99,.01]],[a,b,a]);s=score(m,[1,0],a);assert s['risk']>=0 and np.isfinite(s['risk'])
 try:encode_action({'name':'move','arguments':{'target_position':[.2,.1,.15],'hidden_object_id':1}})
 except AssertionError:pass
 else:raise AssertionError('unknown field accepted')
 reads=[]
 def z(k):
  reads.append(k)
  if k==4:raise AssertionError('future score accessed after two accepted queries')
  return {'visual':1.,'risk':0.}
 assert select(z,{'visual_lower':.5,'risk_upper':1.})['selected']==2 and reads==[1,2]
 return {'unknown_field_rejected':True,'future_score_not_read':True,'finite_distance':True}
if __name__=='__main__':print(json.dumps(self_test()))
