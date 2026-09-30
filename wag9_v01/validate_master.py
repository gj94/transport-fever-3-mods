"""Independent source checks: all cab glazing apertures, mesh hierarchy and markers."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'WAG9_master.blend'))
sc=bpy.context.scene;objs=list(bpy.data.collections['WAG9_ASSET'].objects);bpy.context.view_layer.update()
report={'aperture_samples':[],'scale_checks':[],'failures':[]}
opaque=[o for o in objs if o.type=='MESH' and not any(m and m.node_tree and m.node_tree.nodes.get('Principled BSDF') and m.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value>.5 for m in o.data.materials)]
# A local slab ray through each pane centre must not hit any opaque backing mesh.
for g in [o for o in objs if o.name.startswith('GLASS_')]:
 face=max(g.data.polygons,key=lambda p:p.area);centre=g.matrix_world@face.center;normal=(g.matrix_world.to_3x3()@face.normal).normalized()
 if 'side_lookout' in g.name:centre += g.matrix_world.to_3x3()@Vector((.18,0,0))
 blockers=[]
 for ob in opaque:
  inv=ob.matrix_world.inverted();origin=inv@(centre-normal*.06);direction=(inv.to_3x3()@normal).normalized();ok,p,n,i=ob.ray_cast(origin,direction,distance=.12)
  if ok:blockers.append(ob.name)
 report['aperture_samples'].append({'pane':g.name,'sample_centre_m':list(centre),'opaque_blockers':blockers,'pass':not blockers})
 if blockers:report['failures'].append(g.name+': '+','.join(blockers))
report['cab_forward_sightlines']=[]
for idx,end in [(1,1),(2,-1)]:
 eye=bpy.data.objects['CAB_EYE_CAMERA_REFERENCE_'+str(idx)].matrix_world.translation
 for yy in (-.80,-.70,-.60):
  for zz in (3.10,3.20,3.30):
   target=Vector((end*10.5,end*yy,zz));direction=(target-eye).normalized();distance=(target-eye).length;hits=[]
   for ob in opaque:
    inv=ob.matrix_world.inverted();ok,p,n,i=ob.ray_cast(inv@eye,(inv.to_3x3()@direction).normalized(),distance=distance)
    if ok:hits.append(ob.name)
   structural=[n for n in hits if not n.startswith(('Windscreen guard','Windscreen wiper','Wiper spindle'))]
   report['cab_forward_sightlines'].append({'cab':idx,'target_world':list(target),'opaque_hits':hits,'structural_blockers':structural,'pass':not structural})
   if structural:report['failures'].append('cab sightline '+str(idx)+': '+','.join(structural))
for o in objs:
 if any(abs(x-1)>1e-6 for x in o.scale):report['scale_checks'].append({'object':o.name,'scale':list(o.scale)})
report['non_identity_object_scales']=len(report['scale_checks'])
if report['scale_checks']:report['failures'].append('nonidentity scales')
# Track-related geometry and actual marker positions.
report['bogie_centres']=[list(bpy.data.objects['BOGIE_'+x+'_YAW_Z'].matrix_world.translation) for x in ('A','B')]
report['axle_centres']=[{'name':o.name,'world_m':list(o.matrix_world.translation)} for o in objs if '_ROLL_Y' in o.name]
# Full independent extension sweep (101 configurations, 202 panto measurements).
report['pantograph_101_pose_sweep']=[]
roof_prefix=('Central roof crown','Removable roof panel','Roof walkway plate','Walkway raised grip','Cab roof','Long roof shoulder')
roof=[o for o in objs if o.type=='MESH' and o.name.startswith(roof_prefix)]
roof_max=max((o.matrix_world@v.co).z for o in roof for v in o.data.vertices)
for i in range(101):
 for side,e in [('FRONT',i/100),('REAR',1-i/100)]:
  c=bpy.data.objects['PANTO_'+side+'_CTRL'];c['extension']=e;c.update_tag()
 bpy.context.view_layer.update()
 row={'extensions':[i/100,1-i/100],'pantographs':{}}
 for side in ('FRONT','REAR'):
  pre='PANTO_'+side;lo=bpy.data.objects[pre+'_LOWER_PIVOT'];up=bpy.data.objects[pre+'_ELBOW_PIVOT'];head=bpy.data.objects[pre+'_HEAD_LEVEL_PIVOT']
  lower=(up.matrix_world.translation-lo.matrix_world.translation).length;upper=(head.matrix_world.translation-up.matrix_world.translation).length;u=head.matrix_world.to_3x3()@Vector((0,0,1))
  moving=[o for o in lo.children_recursive if o.type=='MESH'];minz=min((o.matrix_world@v.co).z for o in moving for v in o.data.vertices)
  strip=[o for o in moving if '_CONTACT_STRIP_' in o.name];top=max((o.matrix_world@v.co).z for o in strip for v in o.data.vertices)
  clearance=minz-roof_max
  row['pantographs'][side]={'lower_length_m':lower,'upper_length_m':upper,'head_up':list(u),'strip_top_m':top,'moving_min_z_m':minz,'roof_max_z_m':roof_max,'conservative_roof_vertical_clearance_m':clearance}
  if abs(lower-1.38)>1e-5 or abs(upper-1.15)>1e-5 or (u-Vector((0,0,1))).length>1e-5 or clearance<0:report['failures'].append('panto sweep '+str(i)+' '+side)
 report['pantograph_101_pose_sweep'].append(row)
# Refresh exact final asset counters and lowered bounds after small geometry refinements.
for side in ('FRONT','REAR'):
 c=bpy.data.objects['PANTO_'+side+'_CTRL'];c['extension']=0.;c.update_tag()
bpy.context.view_layer.update();meshes=[o for o in objs if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
q=json.loads((P/'qa/mesh_rig_validation.json').read_text());q['mesh_objects']=len(meshes);q['triangles']=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons);q['asset_materials']=len({m.name for o in meshes for m in o.data.materials});q['evaluated_bounds_lowered']={'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]};q['final_refinements_checked']=True;(P/'qa/mesh_rig_validation.json').write_text(json.dumps(q,indent=2))
report['final_mesh_stats']={k:q[k] for k in ('mesh_objects','triangles','asset_materials','evaluated_bounds_lowered')}
report['glass_count']=len(report['aperture_samples']);report['passed']=not report['failures'];(P/'qa/master_aperture_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
