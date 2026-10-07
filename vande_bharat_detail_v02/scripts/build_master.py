"""Build seven full-size VB2 source cars, preserving the new explicit prototype scaffold controls."""
import bpy,sys,json,hashlib,time,importlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
kinds=a[0].split(',') if a else ['DTC','MC','MC2','TC_CC','TC_EC','NDTC_EC','NDTC_EC2']
modules=a[1].split(',') if len(a)>1 else ['exterior','endcap_detail','running_gear','roof_equipment','vcb_detail','panto_micro','interiors','cab']
for kind in kinds:
 source=OUT.parent/'vande_bharat_v01/cars'/f'VB_{kind}.blend'
 import prototype_base;ctx=prototype_base.build(kind);sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
 protected={o.name:{'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world]} for o in bpy.data.objects if o.type=='EMPTY' and not o.name.startswith('LIGHT_')}
 import materials;M=materials.apply();root=bpy.data.objects[f'VB_{kind}_ROOT'];body=bpy.data.objects['BODY'];col=bpy.data.collections[f'VB_{kind}_ASSET']
 ctx.update({'root':root,'body':body,'collection':col,'materials':M,'out':OUT});report={'kind':kind,'prior_compact_reference_sha256':hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None,'primitive_helpers_sha256':hashlib.sha256(prototype_base.LEGACY.read_bytes()).hexdigest(),'build_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'prototype_layout':ctx['layout'],'components':{}}
 for name in modules:
  p=OUT/'components'/f'{name}.py'
  if p.exists():
   t=time.time();mod=importlib.import_module(name);report['components'][name]=mod.apply(ctx);print('COMPONENT',kind,name,round(time.time()-t,2),flush=True)
 bpy.context.view_layer.update()
 for name,old in protected.items():
  obj=bpy.data.objects.get(name);assert obj is not None,name
  assert (obj.parent.name if obj.parent else None)==old['parent'],name
  assert max(abs(v-old['matrix'][i][j]) for i,row in enumerate(obj.matrix_world) for j,v in enumerate(row))<1e-6,name
 for o in col.objects:
  if o.type=='MESH':
   assert o.parent is not None,o.name
   if o.name.startswith('VB02_'):o['visual_revision']='v02 reference-informed detail; exact unseen hardware representative'
 # Visual geometry and controls stay in the same collection for linked-car assemblies.
 points=[]
 deps=bpy.context.evaluated_depsgraph_get()
 for obj in col.objects:
  if obj.type=='MESH' and not obj.hide_render:
   ev=obj.evaluated_get(deps);points.extend(ev.matrix_world@v.co for v in ev.data.vertices)
 bounds={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
 report.update({'bounds_lowered_m':bounds,'passenger_seats':sum(o.name.startswith('PAX_') and o.type=='EMPTY' for o in col.objects),'driver_seats':sum(o.name.startswith('DRIVER_') and o.type=='EMPTY' for o in col.objects),'objects':len(col.objects),'mesh_objects':sum(o.type=='MESH' for o in col.objects),'protected_transform_count':len(protected),'protected_controls_unchanged':True,'protected_transforms':protected,'component_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'components').glob('*.py')}})
 root['visual_revision']='Vande Bharat full-size exquisite-detail v02';root['status']='Editable full-size Blender source; prototype nominal dimensions; TF3 conversion excluded';root['prior_compact_reference_sha256']=report['prior_compact_reference_sha256'] or 'not present'
 sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.engine='CYCLES';sc.cycles.samples=128;sc.cycles.use_denoising=False;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:
   if not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cars'/f'VB_{kind}.blend'),compress=True)
 (OUT/'qa'/f'VB_{kind}.json').write_text(json.dumps(report,indent=2));print('BUILT',kind,report['objects'],bounds,flush=True)
