"""Raw contact recomputation, extracted from the executed auditor. Units: metres."""
import math

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
