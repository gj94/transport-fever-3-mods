"""Build source-only WAP7 realism v02 from the accepted v01 master.
No TF3 game resources are modified. Components are isolated/idempotent authoring modules."""
import bpy, sys, json, time, hashlib, importlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
BASE=Path(a[0]) if a else OUT.parent/'wap7_photoreal_v01/WAP7_photoreal_v01.blend'
if not BASE.exists() and not a:BASE=OUT.parent/'wap7_repo/wap7_photoreal_v01/WAP7_photoreal_v01.blend'
bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene
# Repack legacy bytes from a verified local path; stale packed-file source paths are not retained.
for im in bpy.data.images:
 if im.source=='FILE' and im.packed_file:
  candidate=OUT/'textures'/Path(im.filepath).name;data=bytes(im.packed_file.data)
  if not candidate.exists() or candidate.read_bytes()!=data:candidate.write_bytes(data)
  im.unpack(method='REMOVE');im.filepath=str(candidate);im.reload();im.pack()
# Preserve every non-visual transform used by root, coupling, bogie, axle and panto mechanism.
protected={o.name:[list(r) for r in o.matrix_world] for o in bpy.data.objects if o.type=='EMPTY' and (o.name.startswith(('WAP7_ROOT','BODY','BOGIE_','AXLE_','COUPLING_','CBC_','PANTO_')))}
import body_geometry
width_report=body_geometry.apply();
import materials
M=materials.apply({'body_width_factor':body_geometry.WIDTH_FACTOR});context={'body_width_factor':body_geometry.WIDTH_FACTOR,'root':bpy.data.objects['WAP7_ROOT'],'body':bpy.data.objects['BODY'],'materials':M,'out':OUT};report={'body_geometry':width_report}
# Explicit surface-role overrides approved in neutral and in-context gear tests.
if (OUT/'components/surface_running_gear.py').exists():
 import surface_running_gear
 gm=surface_running_gear.setup();context['material_overrides']={'frame':gm['gear_frame'],'plate':gm['gear_frame'],'weld':gm['gear_frame'],'sandbox':gm['gear_frame'],'equipment':gm['gear_frame'],'axlebox':gm['gear_cast'],'motor':gm['gear_cast'],'cylinder':gm['gear_cast'],'wheelweb':gm['gear_wheelweb'],'tread':M['tread'],'rubber':M['rubber'],'grease':M['grease']}
for name in (a[1].split(',') if len(a)>1 else ['exterior','coupler','roof','running_gear','cab_interiors','machinery_room']):
 p=OUT/'components'/(name+'.py')
 if p.exists():
  mod=importlib.import_module(name);t=time.time();report[name]=mod.apply(context);print('COMPONENT',name,'seconds',round(time.time()-t,2),flush=True)
shell=bpy.data.objects['Chamfered welded body shell'];mod=shell.modifiers.new('Finished formed sheet edges','BEVEL');mod.width=.0035;mod.segments=3;shell.modifiers.new('Stable shell face normals','WEIGHTED_NORMAL')
if (OUT/'components/stage.py').exists():
 import stage;report['stage']=stage.apply(context)
for o in bpy.data.objects:
 if o.type=='EMPTY' and o.name in protected and o.name!='BODY':
  assert max(abs(v-protected[o.name][i][j]) for i,r in enumerate(o.matrix_world) for j,v in enumerate(r))<1e-5,o.name
for im in bpy.data.images:
 if im.source=='FILE' and im.packed_file:
  name=Path(im.filepath).name;dest=OUT/'textures'/name
  if not dest.exists() or dest.read_bytes()!=im.packed_file.data:dest.write_bytes(im.packed_file.data)
  im.filepath='//textures/'+name
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.01;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8;scene.cycles.sample_clamp_indirect=4.0
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene['render_provenance']='True Cycles vehicle geometry. Render-only presentation uses separately credited environment dependencies; no generated vehicle image or projected vehicle photograph.'
root=bpy.data.objects['WAP7_ROOT'];root['visual_revision']='Minute-detail v02; 39002 Royapuram photo-led representative hardware';root['source_baseline_sha256']=hashlib.sha256(BASE.read_bytes()).hexdigest()
root['asset_status']='Source-only; exact small hardware is representative; not converted or tested in TF3'
bpy.context.preferences.filepaths.save_version=0
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAP7_detail_v02.blend'),compress=True,relative_remap=False)
report.update({'component_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((OUT/'components').glob('*.py')) if p.stem in {'body_geometry','common','materials','surface_materials','surface_running_gear','exterior','coupler','roof','running_gear','cab_interiors','machinery_room','stage'}},'baseline':BASE.name,'baseline_sha256':root['source_baseline_sha256'],'objects':len(bpy.data.objects),'protected_transforms':protected,'packed_images':[im.name for im in bpy.data.images if im.packed_file]})
(OUT/'qa/build_report.json').write_text(json.dumps(report,indent=2,default=str));print('BUILD_COMPLETE',len(bpy.data.objects),flush=True)
