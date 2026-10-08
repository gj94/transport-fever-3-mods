import bpy,json,sys,hashlib,time
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();Q=json.load(open(P/'QA_BUILD.json'));src=P/Q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
# Measured intersection of mapped railhead centerline offsets, not an invented turnout coordinate.
point=(-7.489454351322657,624.7855446679521,.635);camera=s.objects['05_Mapped_turnout_detail'];camera.location=(point[0]+4.5,point[1]-7,5.8);camera.rotation_euler=(Vector(point)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='PERSP';camera.data.lens=43;s.camera=camera
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1280;s.render.resolution_y=854;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s,'eevee'):s.eevee.taa_render_samples=48
f=P/'renders/05_Rail_flange_detail.png';s.render.filepath=str(f);bpy.ops.render.render(write_still=True)
r={'file':str(f.relative_to(P)),'source_blend_sha256':sha,'image_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'camera':'05_Mapped_turnout_detail; read-only close-up override','camera_override':{'position':list(camera.location),'rotation':list(camera.rotation_euler),'lens_mm':43,'target_point':point},'camera_geometry_lineage':'Frozen scene geometry, materials and lighting unchanged. Only camera moved transiently for unobscured rail proof. Blend not saved.','crossing_source_ways':['602468921','640855306'],'railhead_intersection_source':'shapely offset-curve centerlines±0.868m from frozen plan; crossing point624.785545m longitudinal','engine':s.render.engine,'samples':48,'resolution':[1280,854],'denoising':False,'source_file_unchanged':sha==hashlib.sha256(src.read_bytes()).hexdigest()};f.with_suffix('.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
