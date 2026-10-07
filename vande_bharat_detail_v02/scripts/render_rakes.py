"""Actual linked-rake renders, with neutral procedural railway presentation only."""
import os,bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
SCRIPT_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'));from common import box,collection
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];view=args[0] if args else 'rake8';samples=int(args[1]) if len(args)>1 else 128;width=int(args[2]) if len(args)>2 else 1600
count=16 if view=='rake16' else 8;source=OUT/'assemblies'/f'VB_{count}_car.blend';bpy.ops.wm.open_mainfile(filepath=str(source));sha=hashlib.sha256(source.read_bytes()).hexdigest();sc=bpy.context.scene;C=collection('PRESENTATION_NOT_EXPORTED')
INPUT_LIBRARIES={str(Path(bpy.path.abspath(lib.filepath)).resolve().relative_to(OUT)):hashlib.sha256(Path(bpy.path.abspath(lib.filepath)).read_bytes()).hexdigest() for lib in bpy.data.libraries}
# Reuse the WAP7 v02's proven CC0 lighting and real railway meshes, extended for full rakes.
import railway_presentation
stage=railway_presentation.apply();stagecol=bpy.data.collections[stage['collection']];offset=90 if count==8 else 186
for obj in stagecol.objects:obj.location.x+=offset
# Raise the presentation contact system to the preserved VB authoring contact height.
for obj in stagecol.objects:
 if obj.type=='MESH' and any(k in obj.name for k in ['OHE','contact copper','messenger catenary','catenary droppers']):
  for v in obj.data.vertices:
   if v.co.z>4.5:v.co.z+=.387
front=count*24/2-.222;loc=(front+13.2,-12,2.35);target=(front-11.8,0,2.2);lens=50
cam=bpy.data.cameras.new('Rake review camera');o=bpy.data.objects.new('Rake review camera',cam);C.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_end=1500;sc.camera=o
sc.render.engine='CYCLES';sc.cycles.samples=samples;sc.cycles.use_denoising=False;sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.015;sc.cycles.max_bounces=8;sc.cycles.transmission_bounces=6;sc.cycles.sample_clamp_indirect=3;sc.render.threads_mode='FIXED';sc.render.threads=int(os.environ.get("VB_RENDER_THREADS","6"));sc.render.resolution_x=width;sc.render.resolution_y=round(width*.56);sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.filepath=str(OUT/'previews'/f'{view}.png');sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0
bpy.ops.render.render(write_still=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
assert all(hashlib.sha256((OUT/name).read_bytes()).hexdigest()==value for name,value in INPUT_LIBRARIES.items())
(OUT/'qa'/f'render_{view}.json').write_text(json.dumps({'view':view,'source':str(source.relative_to(OUT)),'source_sha256':sha,'library_source_sha256':INPUT_LIBRARIES,'render_script_sha256':SCRIPT_SHA,'samples':samples,'image_sha256':hashlib.sha256((OUT/'previews'/f'{view}.png').read_bytes()).hexdigest(),'camera':{'location':loc,'target':target,'lens':lens},'presentation':stage,'presentation_offset_m':offset,'location_claim':'Generic rail depot, not a depicted real station. Actual linked source cars.'},indent=2))
