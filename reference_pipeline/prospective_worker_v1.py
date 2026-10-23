"""One real Piper teacher rollout. Raw collection, no success-rate gate."""
import sys, os, json, pathlib, time, datetime, gzip, traceback, hashlib, copy

spec=json.load(sys.stdin)
assert spec['task']=='red_objects_in_basket' and spec['phase']=='prospective_stage_A' and spec['seed'] in range(4062104001,4062104013)
assert spec['task'] in ['pick_up_carrot', 'tomato_near_potato', 'lemon_in_bin', 'push_pot', 'cube_stack_reverse', 'apple_juice_reverse_order', 'bin_and_tray_simple', 'set_table', 'can_in_bin', 'apple_juice_order', 'remove_cube_from_tray', 'push_basket', 'close_drawer', 'shell_game', 'red_objects_in_basket']
kind=spec.get('kind','base')
out=pathlib.Path(spec['output']); out.mkdir(parents=True,exist_ok=False)
def atomic(name,data):
 p=out/name; tmp=p.with_suffix(p.suffix+'.tmp')
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)); tmp.replace(p)
started=time.time(); task=spec['task']; index=spec['index']; seed=spec['seed']
atomic('started.json',{'task':task,'index':index,'seed':seed,'pid':os.getpid(),'process_start':pathlib.Path('/proc/self/stat').read_text().split()[21],'kind':kind,'started_at_unix':started,'teacher_input':'simulation RGB, instruction, proprioception, tool feedback only'})
env=ik=None; physics=None; original_step=original_execute=original_configure=None
result={'replacement_of':spec.get('replacement_of'),'replacement_source':spec.get('replacement_source'),'parent_only':bool(spec.get('parent_only',False)),'kind':kind,'output':str(out),'task':task,'index':index,'seed':seed,'raw_collection':True,'training_eligible':False,'physical_review':'pending','status':'error'}
actions=[]; step_count=0; call_count=0; audit_enabled=False
try:
 import numpy as np
 import yaml
 from robosuite.utils import camera_utils as _depth_utils
 _original_depth_conversion=_depth_utils.get_real_depth_map
 def _record_invalid_depth(sim,depth):
  if not (np.isfinite(depth).all() and np.all(depth>=0.) and np.all(depth<=1.)):
   np.save(out/('invalid_depth_'+str(time.time_ns())+'.npy'),depth)
   atomic('invalid_depth_range.json',{'minimum':float(np.nanmin(depth)),'maximum':float(np.nanmax(depth)),'nan_count':int(np.isnan(depth).sum()),'outside_count':int(((depth<0)|(depth>1)).sum()),'dtype':str(depth.dtype),'shape':list(depth.shape),'no_clipping_or_retry':True})
  return _original_depth_conversion(sim,depth)
 _depth_utils.get_real_depth_map=_record_invalid_depth
 from guava.config import CollectionConfig
 from guava.scripts.collect import _apply_yaml
 from guava.sim.tasks import make_env
 from guava.robot.arm import RobotArm
 from guava.robot.ik.ik_pose import IKPoseSolver
 from guava.perception.sam3 import SAM3Solver
 from guava.llm.providers.openai_compat import OpenAICompatProvider
 from guava.collection.trial import run_trial
 from guava.collection.trajectory import save_trajectory, save_branch_trajectory
 from runtime_support import install_protocol, run_recovery, audit_record, list_branches
 install_protocol(out)
 from quality_runtime import install as install_quality
 install_quality(out)
 from three_task_runtime import install as install_three
 install_three(out)
 from single_view_runtime import install as install_single
 from canonical_tools_runtime import install as install_canonical
 install_single();install_canonical()
 from production_adapters import install as install_adapters, verify_mass
 profile=install_adapters(spec,out)
 from feedback_contract import install as install_feedback_contract
 install_feedback_contract()
 from sensor import install as install_sensor
 install_sensor()
 from prospective_eval_v1 import install as install_evaluation
 install_evaluation(spec,out)
 from guava.collection import rollout
 from guava.task_catalog import TRAINING_TASKS
 assert task in ['pick_up_carrot', 'tomato_near_potato', 'lemon_in_bin', 'push_pot', 'cube_stack_reverse', 'apple_juice_reverse_order', 'bin_and_tray_simple', 'set_table', 'can_in_bin', 'apple_juice_order', 'remove_cube_from_tray', 'push_basket', 'close_drawer', 'shell_game', 'red_objects_in_basket'] and os.environ['GUAVA_ROBOT']=='Piper'
 from official_config import OFFICIAL
 if task not in OFFICIAL['configs']:
  extra=(pathlib.Path('configs')/(task+'.yaml')).read_text()
  OFFICIAL['configs'][task]={'yaml':extra,'sha256':hashlib.sha256(extra.encode()).hexdigest(),'source':'frozen task YAML; collection pipeline extended to benchmark'}
 cfg=CollectionConfig(); raw=yaml.safe_load(OFFICIAL['configs'][task]['yaml']); _apply_yaml(cfg,raw)
 cfg.sim.task=task; cfg.sim.perception='sam3'; cfg.sim.grasp='pca'
 cfg.sim.visualize=False; cfg.sim.use_mjviewer=False; cfg.sim.motion_speed=raw['sim']['motion_speed']
 cfg.sim.camera.name='robot0_real_top'; cfg.sim.camera.width=640; cfg.sim.camera.height=480; cfg.sim.camera_views=['robot0_real_top']
 cfg.sim.randomize.seed=seed-index; cfg.output_dir=str(out/'native')
 cfg.robot.sam3_url=spec['sam3_url']; cfg.record_video=False; cfg.video_fps=20
 cfg.llm.base_url=spec['api_base_url']; cfg.llm.model=spec['model_id']; cfg.llm.max_tokens=raw['llm']['max_tokens']
 atomic('configuration.json',{'task':task,'seed':seed,'yaml_sha256':OFFICIAL['configs'][task]['sha256'],'turn_budget':cfg.turn_budget,'max_retries':cfg.max_retries,'official_commit':OFFICIAL['commit'],'model_profile':profile,'task_yaml':raw,'overrides':{'motion_speed':cfg.sim.motion_speed,'perception':'sam3','camera':'robot0_real_top','width':640,'height':480,'video_fps':20,'api_base_url':cfg.llm.base_url,'transport':'local nonstreaming; full reply before tool execution','model':cfg.llm.model,'reasoning_effort':None,'decoding':'greedy BF16, native Qwen assistant prefill restored','max_completion_tokens':cfg.llm.max_tokens,'stop_on_reward':cfg.stop_on_reward},'native_training_export_held_until_review':True})
 class Provider(OpenAICompatProvider):
  def complete(self,messages,tools=None,**kwargs):
   global call_count
   call_count+=1; kwargs.pop('reasoning_effort',None); kwargs['temperature']=0
   atomic('inflight_messages.json',messages)
   if call_count==1:atomic('first_model_input_contract.json',{'messages_sha256':hashlib.sha256(json.dumps(messages,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
   if spec.get('preflight_only'):raise ValueError('Preflight only: no model request and no action')
   begin=time.time(); atomic('activity.json',{'state':'api_request','call':call_count,'at_unix':begin,'task':task})
   telemetry={'call':call_count,'start_unix':begin,'task':task,'index':index}; response=None
   try:
    response=super().complete(messages,tools,**kwargs)
    public=response.get('choices',[{}])[0].get('message',{})
    with (out/'public_completions.jsonl').open('a') as f:f.write(json.dumps({'call':call_count,'content':public.get('content'),'tool_calls':public.get('tool_calls'),'finish_reason':response.get('choices',[{}])[0].get('finish_reason')},ensure_ascii=False)+'\n')
    telemetry.update(ok=True,model=response.get('model'),usage=response.get('usage'),finish_reason=response.get('choices',[{}])[0].get('finish_reason'))
    return response
   except BaseException as exc:
    telemetry.update(ok=False,error_type=type(exc).__name__); raise
   finally:
    telemetry.update(end_unix=time.time(),seconds=time.time()-begin)
    with (out/'api_usage.jsonl').open('a') as f:f.write(json.dumps(telemetry)+'\n')
    atomic('activity.json',{'state':'api_returned','call':call_count,'at_unix':time.time(),'ok':telemetry.get('ok')})
 import requests
 from urllib.parse import urlparse
 from stream_transport import complete_stream_post
 original_post=requests.post
 def measured_post(url,*args,**kwargs):
  if urlparse(str(url)).hostname!=urlparse(spec['api_base_url']).hostname:return original_post(url,*args,**kwargs)
  begin=time.time(); entry={'start_unix':begin,'provider_call':call_count,'phase':spec['phase'],'concurrency_limit':spec['concurrency_limit']}
  try:
   response=original_post(url,*args,**kwargs);entry['status']=response.status_code;entry['stream_first_event_unix']=getattr(response,'_piper_stream_first_event_unix',None);return response
  except BaseException as exc:
   entry['error_type']=type(exc).__name__;raise
  finally:
   entry.update(end_unix=time.time(),seconds=time.time()-begin)
   with (out/'http_attempts.jsonl').open('a') as f:f.write(json.dumps(entry)+'\n')
 requests.post=measured_post
 provider=Provider(cfg.llm.base_url,spec.pop('api_key'),cfg.llm.model)
 env=make_env(cfg.sim); env.reset(seed=seed)
 ik=IKPoseSolver(env,joint_lower=cfg.robot.joint_lower,joint_upper=cfg.robot.joint_upper,joint_rest=cfg.robot.joint_rest)
 verify_mass(env,profile,out)
 arm=RobotArm(env,ik,cfg.robot); sam=SAM3Solver(cfg.robot.sam3_url)
 physics=gzip.open(out/'physical_state.jsonl.gz','wt')
 def sample(phase):
  global step_count
  d=env.rob.sim.data; m=env.rob.sim.model._model
  contacts=[{'g1':int(c.geom1),'g2':int(c.geom2),'distance':float(c.dist)} for c in d.contact[:d.ncon]]
  item={'phase':phase,'step':step_count,'sim_time':float(d.time),'qpos':np.asarray(d.qpos).tolist(),'qvel':np.asarray(d.qvel).tolist(),'body_xpos':np.asarray(d.body_xpos).tolist(),'body_xquat':np.asarray(d.body_xquat).tolist(),'contacts':contacts}
  physics.write(json.dumps(item,separators=(',',':'))+'\n')
  return item
 original_step=env.step; original_execute=rollout.execute_observe; original_configure=rollout.configure_context
 def audited_step(action):
  global step_count
  value=original_step(action)
  if audit_enabled:step_count+=1; sample('control_step')
  return value
 def configure(*args,**kwargs):
  global audit_enabled
  public=original_configure(*args,**kwargs); audit_enabled=True
  for name,observable in public[0].env.rob._observables.items():
   if name.endswith(("_image","_depth")):observable.set_enabled(False)
  atomic('effective_contract.json',{'system_sha256':hashlib.sha256(public[2].encode()).hexdigest(),'tools_text_sha256':hashlib.sha256(public[3].encode()).hexdigest(),'schema_sha256':hashlib.sha256(json.dumps(public[4],sort_keys=True).encode()).hexdigest(),'tool_names':list(public[1]),'system':public[2],'tools':public[3]})
  assert cfg.turn_budget==raw['turn_budget'] and cfg.max_retries==raw['max_retries'], 'Official collection limit overridden'
  public[5].update(official_commit=OFFICIAL['commit'],effective_turn_budget=cfg.turn_budget,model_profile=profile)
  atomic('effective_limits.json',{'turn_budget':cfg.turn_budget,'max_retries':cfg.max_retries,'max_tokens':cfg.llm.max_tokens,'motion_speed':cfg.sim.motion_speed,'stop_on_reward':cfg.stop_on_reward})
  m=env.rob.sim.model._model
  import mujoco
  mujoco.mj_saveModel(m,str(out/'initial_compiled_model.mjb'),None)
  atomic('compiled_model_contract.json',{'mjb_sha256':hashlib.sha256((out/'initial_compiled_model.mjb').read_bytes()).hexdigest(),'mujoco_version':mujoco.__version__,'for_independent_offline_kinematics_and_collision_only':True,'not_provided_to_model':True})
  atomic('physical_model_names.json',{'bodies':[m.body(i).name for i in range(m.nbody)],'geoms':[m.geom(i).name for i in range(m.ngeom)],'joints':[m.joint(i).name for i in range(m.njnt)],'offline_review_only':True})
  atomic('initial_physical_state.json',{'state':sample('initial'),'original_success':bool(env.rob._check_success())})
  return public
 def execute(ctx,registry,name,args):
  atomic('activity.json',{'state':'tool_execution','tool':name,'action':len(actions),'at_unix':time.time()})
  args=copy.deepcopy(args)
  begin=time.time(); value=original_execute(ctx,registry,name,args)
  actions.append({'tool':name,'arguments':args,'result':value[0],'ok':value[1],'seconds':time.time()-begin})
  atomic('actions.json',actions); sample('after_tool'); physics.flush()
  return value
 env.step=audited_step; rollout.execute_observe=execute; rollout.configure_context=configure
 if kind=='base':
  traj=run_trial(env,arm,sam,provider,cfg,index)
 else:
  traj=run_recovery(env,arm,sam,provider,cfg,index,spec,out,sample)
 # Additional physical hold is audit only, after the teacher has terminated.
 physical_hold=[]
 for _ in range(10):
  env._settle(2)
  physical_hold.append({'time':float(env.rob.sim.data.time),'original_success':bool(env.rob._check_success()),'score':env.rob.score() if hasattr(env.rob,'score') else None})
 atomic('post_terminal_hold.json',physical_hold)
 teacher_quality=dict(traj.quality)
 atomic('final_physical_state.json',{'state':sample('final'),'original_success':bool(env.rob._check_success()),'reward':float(env.rob.reward(action=None))})
 traj.quality.update({'eligible':False,'raw_collection':True,'diagnostic_only':False,'review_status':'pending_physical_and_native_filter','teacher_reported_quality':teacher_quality})
 traj.runtime_metadata.update({'replacement_of':spec.get('replacement_of'),'replacement_wave':spec['campaign'],'parent_only':bool(spec.get('parent_only',False)),'collection_campaign':spec['campaign'],'api_base_url':cfg.llm.base_url,'episode_output':str(out),'offline_physics':'physical_state.jsonl.gz','task_split':'evaluation','evaluation_only':True,'worker_slot':spec['slot'],'scaling_phase':spec['phase'],'concurrency_limit':spec['concurrency_limit']})
 if kind=='base':save_trajectory(traj,cfg.output_dir)
 else:save_branch_trajectory(traj,cfg.output_dir)
 result.update(status='recorded',original_success=bool(traj.success),teacher_quality=teacher_quality,terminal_complete=teacher_quality.get('terminal')=='Task complete.',action_count=len(actions),native_path=str(next((out/('native/trajectories' if kind=='base' else 'native/trajectories_branch')).glob('*.json'))),video_path=str(out/'native/videos'/f'trial_{index:04d}.mp4') if kind=='base' else str(out/'native/videos_branch'/f"trial_{spec['parent_index']:04d}_branch_{index:04d}.mp4"))
 result['automated_audit']=audit_record(pathlib.Path(result['native_path']),out,actions,teacher_quality,physical_hold,kind)
 if kind=='base' and result['automated_audit']['collection_precheck_passed']:
  result['branch_candidates']=list_branches(out,index,cfg,result['automated_audit']['branch_parent_path'])
except BaseException as exc:
 result.update(error_type=type(exc).__name__,traceback=traceback.format_exc(),action_count=len(actions),incomplete=True)
finally:
 if env is not None:
  if original_step is not None:env.step=original_step
  if original_execute is not None:rollout.execute_observe=original_execute
  if original_configure is not None:rollout.configure_context=original_configure
  try:env.rob.close()
  except Exception:pass
 if ik is not None:
  try:ik._p.disconnect(physicsClientId=ik._client_id)
  except Exception:pass
 if physics is not None:physics.close()
 result.update(finished_at_unix=time.time(),elapsed_seconds=time.time()-started,api_calls=call_count,physics_samples=step_count)
 from collection_integrity import inspect
 result['collection_quota_passed'],result['collection_integrity_errors']=inspect(result,out)
 atomic('result.json',result)
 atomic('activity.json',{'state':'finished','at_unix':time.time(),'status':result['status']})
 print(json.dumps({k:result.get(k) for k in ['task','index','status','original_success','terminal_complete','error_type','api_calls','elapsed_seconds']}),flush=True)
