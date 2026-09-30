"""Measured coupled pair clearances and closed glazing topology."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
reports=[]
for sec in 'AB':
 bpy.ops.wm.open_mainfile(filepath=str(P/'sections'/('WAG12B_'+sec+'.blend')));glass=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH' or not ob.data.materials or ob.data.materials[0].name!='Clear_glass':continue
  bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);nonman=sum(not e.is_manifold for e in bm.edges);bm.free();assert boundary==0 and nonman==0
  glass.append({'object':ob.name,'boundary_edges':boundary,'nonmanifold_edges':nonman,'closed':True})
 eye=bpy.data.objects['CAB_EYE_CAMERA_REFERENCE'].matrix_world.translation.copy();eye_hits=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH' or (ob.data.materials and ob.data.materials[0].name=='Clear_glass'):continue
  verts=[ob.matrix_world@v.co for v in ob.data.vertices];faces=[tuple(p.vertices) for p in ob.data.polygons];tree=BVHTree.FromPolygons(verts,faces)
  hit=tree.ray_cast(eye,Vector((1,0,0)),3.0)
  if hit[0] is not None:eye_hits.append({'object':ob.name,'distance_m':hit[3]})
 assert not eye_hits,eye_hits
 reports.append({'section':sec,'closed_glass_meshes':glass,'actual_eye_forward_ray_origin_m':list(eye),'actual_eye_forward_ray_opaque_hits':eye_hits,'passed':bool(glass)})
bpy.ops.wm.open_mainfile(filepath=str(P/'assemblies'/'WAG12B_pair.blend'));bpy.context.view_layer.update();parts={}
for sec in 'AB':
 root=bpy.data.objects['WAG12B_'+sec+'_ROOT'];allobs=list(root.children_recursive);rear=next(o for o in allobs if o.name.startswith('COUPLING_REAR'));front=next(o for o in allobs if o.name.startswith('COUPLING_FRONT'))
 data={'rear':rear,'front':front}
 for prefix in ('Rear_end_wall','Gangway_bellows','Gangway_bridge_half','Internal_drawbar_half'):
  obs=[o for o in allobs if o.name.startswith(prefix) and o.type=='MESH'];xs=[(o.matrix_world@v.co).x for o in obs for v in o.data.vertices];data[prefix]=(min(xs),max(xs))
 parts[sec]=data
A,B=parts['A'],parts['B'];distance=(A['rear'].matrix_world.translation-B['rear'].matrix_world.translation).length
an=(A['rear'].matrix_world.to_3x3()@Vector((1,0,0))).normalized();bn=(B['rear'].matrix_world.to_3x3()@Vector((1,0,0))).normalized();dot=an.dot(bn)
gaps={name:A[name][0]-B[name][1] for name in ('Rear_end_wall','Gangway_bellows','Gangway_bridge_half','Internal_drawbar_half')}
span=(A['front'].matrix_world.translation-B['front'].matrix_world.translation).length
assert distance<1e-5 and abs(dot+1)<1e-6 and abs(span-38.4)<1e-5
assert abs(gaps['Internal_drawbar_half'])<1e-5 and all(gaps[n]>0 for n in ('Rear_end_wall','Gangway_bellows','Gangway_bridge_half'))
assert len([o for o in bpy.data.objects if o.name.startswith('BOGIE_') and o.type=='EMPTY'])==4
assert len([o for o in bpy.data.objects if o.name.startswith('AXLE_') and o.type=='EMPTY'])==8
report={'pair_internal_anchor_error_m':distance,'outward_normal_dot':dot,'outer_coupling_span_m':span,'gaps_m':gaps,'interpretation':{'Rear_end_wall':'minimum gap between fixed rear body wall faces','Gangway_bellows':'expansion space between authored rubber bellows lips','Gangway_bridge_half':'gap between metal bridge half tips','Internal_drawbar_half':'zero denotes touching half-drawbar endpoints at the shared mating plane'},'bogies':4,'axles':8,'outer_driving_cabs':2,'internal_driving_cabs':0,'glazing':reports,'passed':True,'limitations':'straight authored pose only; dynamic coupler yaw/compression and curve/slope collisions are not simulated'}
(P/'qa'/'assembly_and_glazing.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
