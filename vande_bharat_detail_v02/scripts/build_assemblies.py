"""Linked compact-rake authoring assemblies. Original per-car sources remain independent."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];PITCH=24.0
SPEC={8:['DTC','MC','TC_EC','MC2','MC2','TC_CC','MC','DTC'],16:['DTC','MC','TC_CC','MC2','MC','TC_CC','MC2','NDTC_EC','NDTC_EC2','MC2','TC_CC','MC','MC2','TC_CC','MC','DTC']}
for count,kinds in SPEC.items():
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;cache={};rows=[]
 for i,kind in enumerate(kinds):
  if kind not in cache:
   with bpy.data.libraries.load(str(OUT/'cars'/f'VB_{kind}.blend'),link=True) as(src,dst):dst.collections=[f'VB_{kind}_ASSET']
   cache[kind]=dst.collections[0]
  o=bpy.data.objects.new(f'CAR_{i+1:02d}_{kind}',None);sc.collection.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=cache[kind];x=(i-(count-1)/2)*PITCH;sign=-1 if i<count/2 else 1;o.location=(x,0,0);o.rotation_euler.z=math.pi if sign<0 else 0
  qa=json.loads((OUT/'qa'/f'VB_{kind}.json').read_text());lo,hi=qa['bounds_lowered_m']['min'][0],qa['bounds_lowered_m']['max'][0]
  rows.append({'index':i+1,'type':kind,'source_blend':f'../cars/VB_{kind}.blend','origin_m':[x,0,0],'rotation_z_deg':180 if sign<0 else 0,'left_spacing_datum_m':x-PITCH/2,'right_spacing_datum_m':x+PITCH/2,'visible_x_min_m':x+(lo if sign>0 else -hi),'visible_x_max_m':x+(hi if sign>0 else -lo),'passenger_seats_prototype':qa['passenger_seats'],'has_pantograph':kind.startswith('TC')})
 bpy.context.view_layer.update();mins=[1e9]*3;maxs=[-1e9]*3
 for inst in bpy.context.evaluated_depsgraph_get().object_instances:
  if inst.object.type=='MESH' and not inst.object.hide_render:
   for corner in inst.object.bound_box:
    v=inst.matrix_world@Vector(corner)
    for k in range(3):mins[k]=min(mins[k],v[k]);maxs[k]=max(maxs[k],v[k])
 length=maxs[0]-mins[0];span=rows[-1]['right_spacing_datum_m']-rows[0]['left_spacing_datum_m'];assert abs(span-count*PITCH)<1e-9
 joins=[{'cars':[i+1,i+2],'anchor_error_m':abs(rows[i]['right_spacing_datum_m']-rows[i+1]['left_spacing_datum_m'])} for i in range(count-1)];assert all(x['anchor_error_m']<1e-9 for x in joins)
 report={'formation_cars':count,'coupling_pitch_m':PITCH,'outer_anchor_span_m':span,'evaluated_bounds_m':{'min':mins,'max':maxs},'visible_length_m':length,'nominal_prototype_span_m':count*24.0,'passenger_seats_prototype_total':sum(r['passenger_seats_prototype'] for r in rows),'cars':rows,'joins':joins,'status':'Full-size VB2 authoring assembly using24m nominal coupling pitch; exact fine equipment remains representative; TF3 runtime conversion not included','linked_control_scope':'Each type is linked once; repeated type instances share authored controls. Converter must make controls independent per car.','formation_note':'16-car order based on official system layout; 8-car inventory confirmed, TC_EC placement/handing remains selected interpretation.'}
 for lib in bpy.data.libraries:lib.filepath='//../cars/'+Path(lib.filepath).name
 sc.name=f'VB_{count}_CAR_DETAIL_V02';sc['coupling_span_m']=span;sc['visual_length_m']=length;sc['asset_status']=report['status'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'assemblies'/f'VB_{count}_car.blend'),compress=True)
 (OUT/'assemblies'/f'VB_{count}_formation.json').write_text(json.dumps(report,indent=2));print('ASSEMBLY',count,length,span,flush=True)
