"""Re-render existing saved source without rebuilding geometry."""
import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_2017_station.blend'))
s=bpy.context.scene;s.cycles.samples=64;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
cams=sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda o:o.name)
q=json.loads((P/'qa_build.json').read_text());q['render_samples']=64;q['denoiser']='Disabled: this Blender build has no OpenImageDenoise';(P/'qa_build.json').write_text(json.dumps(q,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_2017_station.blend'))
for cam in cams:
 s.render.resolution_y=400 if cam.name.startswith('02_') else 1000
 s.camera=cam;s.render.filepath=str(P/'renders'/(cam.name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=cams[0];s.render.resolution_y=1000;bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_2017_station.blend'))
