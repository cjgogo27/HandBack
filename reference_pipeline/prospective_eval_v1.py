"""Frozen new-scene autonomous evaluation. Same limits/control as development; no teacher or gate labels."""
from pathlib import Path
from copy import deepcopy
import json,hashlib

def install(spec,out):
 from guava.collection import rollout
 D=Path(out)/'evaluation';D.mkdir(exist_ok=False)
 original=rollout.continue_rollout;execute=rollout.execute_observe;actions=[]
 def executed(ctx,registry,name,args):
  value=execute(ctx,registry,name,args)
  actions.append({'owner':'student','name':name,'arguments':deepcopy(args),'result':value[0],'ok':bool(value[1])})
  (D/'accepted_actions.json').write_text(json.dumps(actions,indent=2))
  return value
 def continued(ctx,registry,provider,cfg,trial_id,messages,runtime,**kwargs):
  kwargs['save_checkpoints']=False
  assert cfg.turn_budget==25 and spec['phase']=='prospective_stage_A'
  old_step=ctx.env.step;contact={'maximum_external_robot_penetration_m':0.}
  def step(action):
   value=old_step(action);m=ctx.env.rob.sim.model._model;d=ctx.env.rob.sim.data
   for c in d.contact[:d.ncon]:
    names=[m.geom(int(c.geom1)).name or '',m.geom(int(c.geom2)).name or '']
    if sum(n.startswith(('gripper0','robot0')) for n in names)==1:
     contact['maximum_external_robot_penetration_m']=max(contact['maximum_external_robot_penetration_m'],-float(c.dist))
   return value
  ctx.env.step=step
  try:
   traj=original(ctx,registry,provider,cfg,trial_id,messages,runtime,**kwargs)
   hold=[]
   for _ in range(10):ctx.env._settle(2);hold.append(bool(ctx.env.rob._check_success()))
  finally:ctx.env.step=old_step
  traj.loss_by_message={i:False for i,m in enumerate(traj.messages) if m['role']=='assistant'}
  summary={'arm':spec['learning_arm'],'seed':spec['seed'],'original_success':bool(traj.success),
   'terminal':traj.quality.get('terminal'),'end_reason':traj.quality.get('end_reason'),
   'action_count':traj.quality.get('action_count'),'hold':hold,**contact,
   'teacher_calls':0,'full_task_from_new_initial_state':True,'student_only_loss_labels':False,
   'all_assistant_loss_mask_false':True,'not_an_independent_training_seed_replication':True,'protocol_phase':'prospective_stage_A','selection_results_or_teacher_not_available_to_policy':True}
  summary['raw_complete_and_held']=summary['original_success'] and summary['terminal']=='Task complete.' and all(hold)
  summary['exploratory_contact_thresholds_m']={str(t):summary['raw_complete_and_held'] and contact['maximum_external_robot_penetration_m']<=t for t in [.001,.002,.005]}
  (D/'summary.json').write_text(json.dumps(summary,indent=2))
  (D/'literal_messages.json').write_text(json.dumps(traj.messages))
  traj.runtime_metadata.update(learning_arm=spec['learning_arm'],unassisted_evaluation_only=True,
      no_teacher_no_lookup=True,not_for_supervised_training=True)
  return traj
 rollout.execute_observe=executed;rollout.continue_rollout=continued
