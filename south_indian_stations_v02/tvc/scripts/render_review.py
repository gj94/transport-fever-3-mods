import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=4;S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
names=args or sorted(o.name for o in S.objects if o.type=='CAMERA')
for name in names:
 S.camera=bpy.data.objects[name]
 if name.startswith('12_'):S.render.resolution_x=2400;S.render.resolution_y=700
 else:S.render.resolution_x=1440;S.render.resolution_y=900
 S.render.filepath=str(R/'renders'/f'{name}.png');print('RENDER',name,flush=True);bpy.ops.render.render(write_still=True)
