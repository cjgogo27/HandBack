"""Build display crops and clearly labelled discrete-observation replays from archived sources.

Input layout is documented in docs/media.md. No simulator or interpolation is used.
"""
from pathlib import Path
import argparse, csv, hashlib, json, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(source):
    source=Path(source)
    dest=ROOT/'docs/assets/media';dest.mkdir(parents=True,exist_ok=True)
    visual=json.loads((source/'visual_manifest.json').read_text(encoding='utf8'))
    mapping=json.loads((source/'display_codes.json').read_text(encoding='utf8'))['mapping']
    ordered=sorted(mapping,key=lambda m:int(mapping[m][1:]))
    rows=list(csv.DictReader((ROOT/'data/stage_a.csv').open(encoding='utf8')))
    gallery=[]
    for row in rows:
        method,seed=row['method'],int(row['seed']);scene=seed-4062104001
        gi=ordered.index(method)//3;ci=ordered.index(method)%3;ri=scene%4;start=(scene//4)*4+1
        panel=source/f'final_native_scenes_{start}_{start+3}_group{gi+1}.png'
        name=f'{method}_{seed}_final.webp'
        # The archived panel embeds each native image at 480x360, below a 40px label.
        with Image.open(panel) as img:
            crop=img.crop((ci*480,ri*405+40,ci*480+480,ri*405+400))
            crop.save(dest/name,format='WEBP',lossless=True,method=6)
        raw=next(r for r in visual['source_images'] if r['method']==method and r['seed']==seed)
        gallery.append(dict(method=method,seed=seed,file=name,sha256=sha(dest/name),
            source_panel=panel.name,source_panel_sha256=sha(panel),native_source_sha256=raw['source_sha256'],
            native_sha256=raw['native_sha256'],transformation='Lossless crop of the 480x360 native-image region of the archived review panel; no reconstruction or retouching',
            is_last_native_observation_not_post_hold_camera=True))
    replays=[]
    font=ImageFont.load_default(size=18)
    labels={4062104002:'Joint success',4062104006:'Task not completed',4062104008:'Completed, contact screen failed'}
    for seed,title in labels.items():
        ep=source/f'V_{seed}';spec=json.loads((ep/'source_manifest.json').read_text(encoding='utf8'));records=spec['records']
        fname=f'V_{seed}_observations.mp4';path=dest/fname
        writer=imageio_ffmpeg.write_frames(str(path),(640,560),fps=1,codec='libx264',pix_fmt_in='rgb24',
            pix_fmt_out='yuv420p',output_params=['-crf','20','-preset','medium','-movflags','+faststart'],macro_block_size=1)
        writer.send(None)
        try:
            for rec in records:
                p=ep/rec['file'];assert sha(p)==rec['source_sha256']
                with Image.open(p) as img:
                    assert img.size==(640,480)
                    canvas=Image.new('RGB',(640,560),'#102938');canvas.paste(img.convert('RGB'),(0,80))
                    d=ImageDraw.Draw(canvas)
                    d.text((12,8),f'V / {seed} | observation {rec["index"]+1}/{len(records)}',font=font,fill='white')
                    d.text((12,33),'Discrete observations: 1 image/second. NOT continuous video.',font=font,fill='#bfe3f0')
                    d.text((12,56),title,font=font,fill='white')
                    writer.send(np.asarray(canvas))
        finally:writer.close()
        replays.append(dict(method='V',seed=seed,title=title,file=fname,sha256=sha(path),frames=len(records),fps=1,
            observation_source_sha256=[r['source_sha256'] for r in records],
            source_frames_manifest_sha256=sha(ep/'source_manifest.json'),
            transformation='Original RGB camera observations in saved order, no interpolation; added label band above uncropped 640x480 image; H.264 encoded',
            not_continuous_motion_video=True,playback_time_not_simulation_or_wall_time=True,
            selection='Post hoc illustrative success, task failure and contact-screen failure; not independent tests'))
    peaks=[]
    for method in ('U','V'):
        rec=next(r for r in visual['derived_peak_diagnostics'] if r['method']==method)
        name=rec['picture'];shutil.copyfile(source/name,dest/name)
        peaks.append(dict(method=method,seed=rec['seed'],file=name,sha256=sha(dest/name),
            derived_from_logged_body_poses=True,not_native_camera_frame=True,
            initial_native_alignment_mean_absolute_rgb_error=rec['initial_native_alignment_mean_absolute_rgb_error'],
            note='Derived diagnostic; not pixel-exact evidence, physical zero-overlap proof or hardware safety certificate'))
    paired={}
    for method in ('V','S1'):
        spec=json.loads((source/f'{method}_4062104002/source_manifest.json').read_text(encoding='utf8'))
        paired[method]=[r['source_sha256'] for r in spec['records']]
    manifest=dict(gallery=gallery,replays=replays,derived_peaks=peaks,
        paired_scene_4002_native_observation_hashes_identical=paired['V']==paired['S1'],
        raw_sources_distribution='GitHub release asset handback-media-sources-v0.1.0.zip',
        no_new_robot_actions_or_simulation_integration=True)
    (ROOT/'data/media_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'gallery':len(gallery),'replays':len(replays),'derived_peaks':len(peaks),
                      'media_bytes':sum(p.stat().st_size for p in dest.iterdir())}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=Path,required=True)
    build(p.parse_args().source_root)
