"""Offline rigid-scene rendering from logged body poses. Never used for control/teacher input.
Derived diagnostic images are not native observations or a physics/safety certificate.
"""
import numpy as np
import mujoco

def rotation(q):
    out=np.empty(9);mujoco.mju_quat2Mat(out,np.asarray(q,dtype=float));return out.reshape(3,3)

def apply_logged_body_poses(model,data,sample,camera='robot0_real_top'):
    assert len(sample['body_xpos'])==model.nbody and len(sample['body_xquat'])==model.nbody
    assert getattr(model,'nskin',0)==0,'rigid-only audit, unsupported skinned model'
    cam=model.camera(camera).id;assert int(model.cam_mode[cam])==int(mujoco.mjtCamLight.mjCAMLIGHT_FIXED),'camera tracking mode not supported'
    rotations=np.array([rotation(q) for q in sample['body_xquat']]);positions=np.asarray(sample['body_xpos'],float)
    assert positions.shape==(model.nbody,3) and np.isfinite(positions).all()
    data.xpos[:]=positions;data.xquat[:]=sample['body_xquat'];data.xmat[:]=rotations.reshape(model.nbody,9)
    for gid,bid in enumerate(model.geom_bodyid):
        data.geom_xpos[gid]=positions[bid]+rotations[bid]@model.geom_pos[gid]
        data.geom_xmat[gid]=(rotations[bid]@rotation(model.geom_quat[gid])).reshape(9)
    for cid,bid in enumerate(model.cam_bodyid):
        if int(model.cam_mode[cid])!=int(mujoco.mjtCamLight.mjCAMLIGHT_FIXED):continue
        data.cam_xpos[cid]=positions[bid]+rotations[bid]@model.cam_pos[cid]
        data.cam_xmat[cid]=(rotations[bid]@rotation(model.cam_quat[cid])).reshape(9)
    for lid,bid in enumerate(model.light_bodyid):
        data.light_xpos[lid]=positions[bid]+rotations[bid]@model.light_pos[lid]
        data.light_xdir[lid]=rotations[bid]@model.light_dir[lid]
    return data

def render(model,data,width=640,height=480,camera='robot0_real_top'):
    option=mujoco.MjvOption();option.geomgroup[0]=0;option.geomgroup[1]=1
    with mujoco.Renderer(model,height=height,width=width) as renderer:
        renderer.update_scene(data,camera=camera,scene_option=option)
        return renderer.render().copy()

def self_test():
    xml='<mujoco><visual><global offwidth="256" offheight="256"/></visual><worldbody><light pos="0 0 2"/><camera name="robot0_real_top" pos="0 -1 .7" xyaxes="1 0 0 0 .57 .82"/><geom type="plane" size="1 1 .01" group="1"/><body pos="0 0 .15"><freejoint/><geom type="sphere" size=".04" mass=".1" group="1" rgba="0 0 1 1"/></body></worldbody></mujoco>'
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    a=render(m,d,128,128);sample=dict(body_xpos=d.xpos.copy().tolist(),body_xquat=d.xquat.copy().tolist())
    d.qpos[0]+=.2;mujoco.mj_forward(m,d);apply_logged_body_poses(m,d,sample);b=render(m,d,128,128)
    assert np.array_equal(a,b),'raw logged-body pose reconstruction did not reproduce initial pixels'
    return dict(rigid_pose_reconstruction_pixel_exact=True,isolated_synthetic_fixture=True,real_task_scene_consumed=False,simulator_steps=0)

if __name__=='__main__':
    import json
    print(json.dumps(self_test()))
