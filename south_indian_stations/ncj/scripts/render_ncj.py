import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_2010_station.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
names=['01_HERO_FORECOURT','02_FRONT_ELEVATION','03_ENTRANCE_DETAIL','04_PLATFORM_CONTEXT']
if '--' in sys.argv:
 opts=sys.argv[sys.argv.index('--')+1:]
 if opts:names=opts
for n in names:
 s.camera=bpy.data.objects[n];s.render.filepath=str(R/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
