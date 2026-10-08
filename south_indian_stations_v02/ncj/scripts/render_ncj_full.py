import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
quick='quick' in args;s.cycles.samples=12 if quick else 96;s.render.resolution_x=1000 if quick else 1400;s.render.resolution_y=650 if quick else 900
names=[a for a in args if a!='quick']
for c in sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:x.name):
 if names and not any(c.name.startswith(a) for a in names):continue
 
 label=bpy.data.collections.get('91_REVIEW_LABELS_NOT_PHYSICAL')
 if label:label.hide_render=not c.name.startswith('10_');label.hide_viewport=False
 s.cycles.samples=12 if quick else (128 if c.name[:2] in ['02','03','04','12','14'] else 48)
 s.camera=c;s.render.filepath=str(R/'renders'/f'{c.name}.png');bpy.ops.render.render(write_still=True)
