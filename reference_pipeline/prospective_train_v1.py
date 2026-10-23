"""Actual pooled update. Same six-parent order, replay, optimizer and mask; selected prefixes only.
No future evaluation observations or labels are read. Absent handoff retains all four targets.
"""
from pathlib import Path
import os,json,time,hashlib,pickle,random,base64,io,traceback,subprocess
P=Path('artifact://piper_handoff_learning_20261021_v1')
N=Path(__file__).resolve().parents[1];spec=json.loads(os.environ['PROSPECTIVE_TRAIN_SPEC']);T=N/'prospective_v1'/'training'/('seed'+str(spec['training_seed'])+'_'+spec['method'])
process_started=time.time();T.mkdir(exist_ok=False)
def dump(n,v):
 q=T/(n+'.tmp');q.write_text(json.dumps(v,indent=2));q.replace(T/n)
try:
 import torch
 from PIL import Image
 from transformers import AutoProcessor,AutoModelForImageTextToText
 from peft import LoraConfig,get_peft_model
 status=json.loads((P/'training_collection_v3_status.json').read_text())
 assert status['state']=='completed_training_collection' and len(status['rows'])==24
 candidates={1:[],2:[],4:[]};files={};parents=[]
 for row in status['rows']:
  D=Path(row['output'])/'handoff'
  if not all((D/f'prefix_{k}.pkl').exists() for k in [1,2,4]):continue
  states={k:pickle.loads((D/f'prefix_{k}.pkl').read_bytes()) for k in [1,2,4]}
  if any(s['offline_task_already_complete'] for s in states.values()):continue
  parents.append(row['seed'])
  for k,s in states.items():
   p=D/f'prefix_{k}.pkl';files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
   j=0
   for i,m in enumerate(s['messages']):
    if m['role']=='assistant' and '<tool_call>' in str(m['content']):
     action=s['accepted'][j];j+=1
     if action['owner']=='teacher':
      candidates[k].append({'parent_seed':row['seed'],'teacher_ordinal':sum(a['owner']=='teacher' for a in s['accepted'][:j]),'messages':s['messages'][:i+1],
       'target_sha256':hashlib.sha256(m['content'].encode()).hexdigest(),'tool_ok':action['ok']})
   assert j==len(s['accepted'])
 assert len(parents)==6
 selection=json.loads((N/'prospective_v1/selection.json').read_text());assert selection['state']=='completed_causal_prefix_selection'
 assert parents==selection['parent_order']
 method=spec['method'];assert method in ['B','F4','Fbest','S1','S2','V']
 assert spec['training_seed'] in [42,43]
 selected={r['parent']:r['retained_k'] for r in selection['methods'][method]} if method!='B' else {p:0 for p in parents}
 assert set(selected)==set(parents) and all(v in ([0] if method=='B' else [1,2,4]) for v in selected.values())
 candidates[0]=[]
 replay_source=Path('artifact://piper_sft_20261018_v1/dataset/train_swift.jsonl')
 replay=[];replay_rng=random.Random(2718)
 with replay_source.open() as f:
  for line in f:
   r=json.loads(line)
   if 'red_objects_in_basket' not in json.dumps(r):continue
   indices=[i for i,m in enumerate(r['messages']) if m['role']=='assistant' and '<tool_call>' in str(m['content'])]
   if indices:
    i=replay_rng.choice(indices)
    replay.append({'parent_id':r['id'],'target_index':i,'messages':r['messages'][:i+1]})
   if len(replay)>=12:break
 assert len(replay)==12
 base=Path('artifact://guava_collection_pair_20261018_v1')
 config=json.loads((base/'protocol.json').read_text())
 processor=AutoProcessor.from_pretrained(config['same_processor_for_both'],local_files_only=True)
 def conversation(source):
  converted=[]
  for m in source:
   c=m['content']
   if isinstance(c,list):
    parts=[]
    for p in c:
     if p['type']=='text':parts.append({'type':'text','text':p['text']})
     elif p['type'] in ['image_url','image']:
      u=p['image_url']['url'] if p['type']=='image_url' else p['image']
      im=Image.open(io.BytesIO(base64.b64decode(u.split(',',1)[1]))) if u.startswith('data:') else Image.open(u)
      parts.append({'type':'image','image':im.convert('RGB')})
     else:raise ValueError('Unsupported public content')
    c=parts
   converted.append({'role':m['role'],'content':c})
  return converted
 def encode(sample):
  c=conversation(sample['messages']);assert c[-1]['role']=='assistant'
  x=processor.apply_chat_template(c,tokenize=True,add_generation_prompt=False,return_dict=True,return_tensors='pt')
  a=processor.apply_chat_template(c[:-1],tokenize=True,add_generation_prompt=False,return_dict=True,return_tensors='pt')
  n=a['input_ids'].shape[-1]
  assert torch.equal(x['input_ids'][:,:n],a['input_ids'])
  assert x['input_ids'].shape[-1]<32768,'No truncation or deletion to favor an arm'
  header=processor.tokenizer.encode('<|im_start|>assistant\n',add_special_tokens=False)
  assert x['input_ids'][0,n:n+len(header)].tolist()==header
  y=x['input_ids'].clone();y[:,:n+len(header)]=-100;assert (y!=-100).any()
  return x,y,{'total_tokens':int(x['input_ids'].shape[-1]),'supervised_tokens':int((y!=-100).sum()),'context_and_header_masked':True}
 manifest={'task':'red_objects_in_basket','stage':'exploratory teaching-length mechanism, NOT a validated new exit policy',
  'parents':parents,'prefix_files_sha256':files,'base_checkpoint':config['groups']['sft']['model'],
  'replay_source_sha256':hashlib.sha256(replay_source.read_bytes()).hexdigest(),'replay_targets':[{'parent_id':r['parent_id'],'target_index':r['target_index']} for r in replay],
  'training_seed':42,'steps_per_arm':4*len(parents),'old_new_examples_per_step':[2,1],'lr':1e-4,
  'lora':{'r':8,'alpha':16,'target_modules':['q_proj','v_proj','o_proj']},
  'candidate_examples':{str(k):len(v) for k,v in candidates.items()},
  'same_update_steps_not_equal_acquisition_cost':True,'test_results_not_used_for_selection':True,
  'historical_replay_is_not_claimed_fully_quality_approved':True,
  'new_teacher_tool_failures':{str(k):sum(not r['tool_ok'] for r in v) for k,v in candidates.items()}}
 manifest.update(stage='prospective pooled actual update from causal prefix choices; downstream gains untested',spec=spec,parents=parents,steps_per_arm=24,selected_k_by_parent=selected,selection_sha256=hashlib.sha256((N/'prospective_v1/selection.json').read_bytes()).hexdigest(),abstention_preserves_four_targets=True,training_seed=spec['training_seed'])
 dump('manifest.json',manifest)
 torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.cuda.set_per_process_memory_fraction(.70,0)
 cached_replay=[encode(r) for r in replay]
 all_results={}
 for k in [0 if method=='B' else 4]:
  torch.manual_seed(spec['training_seed']);random.seed(spec['training_seed']);torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
  loading_started=time.time()
  model=AutoModelForImageTextToText.from_pretrained(config['groups']['sft']['model'],local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda:0')
  loading_seconds=time.time()-loading_started
  model=get_peft_model(model,LoraConfig(r=8,lora_alpha=16,lora_dropout=0.,target_modules=['q_proj','v_proj','o_proj'],task_type='CAUSAL_LM'))
  model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.enable_input_require_grads()
  for name,p in model.named_parameters():
   if 'visual' in name or 'vision' in name:p.requires_grad=False
  params={n:p for n,p in model.named_parameters() if p.requires_grad};before={n:p.detach().cpu().float().clone() for n,p in params.items()}
  opt=torch.optim.AdamW(params.values(),lr=1e-4,weight_decay=.01);model.train();rng=random.Random(spec['training_seed'])
  newrows=[r for r in candidates[k] if r['parent_seed'] in parents and r['teacher_ordinal']<=selected[r['parent_seed']]]
  cache=[encode(r) for r in newrows];history=[];begin=time.time()
  dump('new_target_manifest.json',[{q:v for q,v in r.items() if q!='messages'} for r in newrows])
  initial_nll=[];model.eval()
  with torch.inference_mode():
   for (x,y,audit),row in zip(cache,newrows):
    loss=model(**x.to('cuda:0'),labels=y.to('cuda:0'),use_cache=False).loss
    initial_nll.append({'parent':row['parent_seed'],'ordinal':row['teacher_ordinal'],'nll':float(loss),'target_sha256':row['target_sha256']});x.to('cpu');del loss
  dump('initial_public_target_nll.json',initial_nll);model.train()
  steps=4*len(parents)
  for step in range(steps):
   parent=parents[step%len(parents)];ordinal=1+(step//len(parents))%max(selected[parent],1)
   new_idx=next((i for i,r in enumerate(newrows) if r['parent_seed']==parent and r['teacher_ordinal']==ordinal),None)
   opt.zero_grad();old_idxs=[(2*step)%12,(2*step+1)%12]
   samples=([('new',cache[new_idx])] if k else [('old_control',cached_replay[(2*step+2)%12])])+[('old',cached_replay[i]) for i in old_idxs]
   record={'step':step+1,'parent':parent,'teacher_ordinal':ordinal if k else None,'new_index':new_idx,'selected_k':selected[parent],'old_indices':old_idxs,'examples':[]}
   for source,(x,y,audit) in samples:
    batch=x.to('cuda:0');labels=y.to('cuda:0')
    loss=model(**batch,labels=labels,use_cache=False).loss;assert torch.isfinite(loss)
    (loss/3).backward();record['examples'].append({'source':source,'loss':float(loss.detach()),**audit})
    # BatchFeature.to mutates its values: explicitly return cached data to CPU.
    x.to('cpu');del batch,labels,loss
   norm=torch.nn.utils.clip_grad_norm_(params.values(),1.0);assert torch.isfinite(norm);opt.step()
   record['grad_norm']=float(norm);record['elapsed_seconds']=time.time()-begin;history.append(record)
   dump(f'arm_{k}_history.json',history)
  delta=max(float((p.detach().cpu().float()-before[n]).abs().max()) for n,p in params.items());assert delta>0
  target=T/'adapter';model.save_pretrained(target,safe_serialization=True)
  all_results[str(k)]={'status':'trained','steps':steps,'seconds':time.time()-begin,
   'max_parameter_delta':delta,'loading_seconds':loading_seconds,'process_seconds_including_loading':time.time()-process_started,'adapter_sha256':hashlib.sha256((target/'adapter_model.safetensors').read_bytes()).hexdigest(),'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20,
   'adapter':str(target),'new_supervised_tokens':sum(e['supervised_tokens'] for r in history for e in r['examples'] if e['source']=='new')}
  dump('status.json',{'state':'training','arms':all_results,'at':time.time()})
  del model,opt,params,before,cache;import gc;gc.collect();torch.cuda.empty_cache()
 dump('status.json',{'state':'completed','arms':all_results,'at':time.time(),
      'downstream_autonomous_learning_gain_still_untested':True})
except BaseException:
 dump('status.json',{'state':'failed','at':time.time(),'traceback':traceback.format_exc()});raise
