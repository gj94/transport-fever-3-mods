import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
s=bpy.context.scene
# Idempotent final QA fix also present in the builder: east yard fence clears mapped tracks.
for o in s.objects:
 if o.name.startswith(('Boundary concrete post','Boundary wire')) and abs(o.location.y-121)<.1:o.location.y=160
from mathutils import Vector
if '13_Turnout_frog_detail' not in bpy.data.objects:
 cd=bpy.data.cameras.new('13_Turnout_frog_detail');o=bpy.data.objects.new('13_Turnout_frog_detail',cd);s.collection.objects.link(o);o.location=(557,33,3.6);o.rotation_euler=(Vector((549.85,39.75,.62))-o.location).to_track_quat('-Z','Y').to_euler();cd.lens=46;cd.clip_end=4000
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_v02.blend'),compress=True)
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=96;s.render.resolution_x=1200;s.render.resolution_y=750
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if '05' in args and '13' not in args:args.append('13')
order={'13':0,'05':1,'02':2} if args else {}
for c in sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:(order.get(x.name[:2],9),x.name)):
 if args and not any(c.name.startswith(a) for a in args):continue
 s.cycles.samples=128 if c.name[:2] in ['02','03','08','09','11'] else 64
 s.camera=c;s.render.filepath=str(P/'renders'/(c.name+'.png'));bpy.ops.render.render(write_still=True)
