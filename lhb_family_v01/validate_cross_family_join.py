"""Exact evaluated-solid LHB3A / ICF3A straight contact test.
Requires the sibling icf_family_v01 source package. Override with -- /path/to/ICF_3A_master.blend.
"""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
icf=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else P.parent/'icf_family_v01/3A/ICF_3A_master.blend'
source=P/'models/LHB_3A.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));lhbroot=bpy.data.objects['LHB_3A_ROOT_metres']
with bpy.data.libraries.load(str(icf),link=False) as (frm,to):to.objects=list(frm.objects)
icfroot=next(o for o in to.objects if o and o.name.startswith('ICF_3A_ROOT'))
coll=bpy.data.collections.new('QA_ICF_REFERENCE');bpy.context.scene.collection.children.link(coll)
for o in [icfroot]+list(icfroot.children_recursive):
 if not o.users_collection:coll.objects.link(o)
 else:
  if o.name not in bpy.context.scene.objects:coll.objects.link(o)
a=next(o for o in lhbroot.children_recursive if o.name.startswith('COUPLING_FRONT'));b=next(o for o in icfroot.children_recursive if o.name.startswith('COUPLING_REAR'))
bpy.context.view_layer.update();shift=a.matrix_world.translation-b.matrix_world.translation;icfroot.location+=shift;bpy.context.view_layer.update()
anchorerror=(a.matrix_world.translation-b.matrix_world.translation).length;axisdot=(a.matrix_world.to_3x3()@Vector((1,0,0))).dot(b.matrix_world.to_3x3()@Vector((1,0,0)))
dg=bpy.context.evaluated_depsgraph_get()
def evaluate(root,side):
 result=[]
 for o in root.children_recursive:
  if o.type not in {'MESH','FONT'}:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();pts=[o.matrix_world@v.co for v in m.vertices]
  if not pts:ev.to_mesh_clear();continue
  bounds=[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
  if (side=='left' and bounds[0][1]>11) or (side=='right' and bounds[0][0]<13):
   d=m.copy();tmp=bpy.data.objects.new('QA_EVALUATED_'+o.name,d);bpy.context.scene.collection.objects.link(tmp);tmp.matrix_world=o.matrix_world.copy();result.append((o.name,tmp,bounds))
  ev.to_mesh_clear()
 return result
left=evaluate(lhbroot,'left');right=evaluate(icfroot,'right');tests=[];errors=[]
for namea,oa,ba in left:
 for nameb,ob,bb in right:
  ov=[min(ba[i][1],bb[i][1])-max(ba[i][0],bb[i][0]) for i in range(3)]
  if min(ov)<=1e-7:continue
  mod=oa.modifiers.new('EXACT_INTERSECTION','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=ob
  ev=oa.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);volume=abs(bm.calc_volume(signed=True));bm.free();ev.to_mesh_clear();oa.modifiers.remove(mod)
  t={'LHB_mesh':namea,'ICF_mesh':nameb,'aabb_overlap_m':ov,'exact_positive_intersection_m3':volume};tests.append(t)
  if volume>1e-8:errors.append(t)
result={'passed':anchorerror<1e-5 and abs(axisdot+1)<1e-5 and not errors,'models':['LHB_3A','ICF_3A'],'source_sha256':{'LHB_3A':hashlib.sha256(source.read_bytes()).hexdigest(),'ICF_3A':hashlib.sha256(icf.read_bytes()).hexdigest()},'ICF_world_translation_m':list(icfroot.location),'mating_plane_xyz_m':list(a.matrix_world.translation),'anchor_position_error_m':anchorerror,'outward_axis_dot_product':axisdot,'near_join_evaluated_mesh_counts':[len(left),len(right)],'positive_aabb_candidates_exact_boolean_tested':tests,'unexpected_positive_volume_intersections':errors,'tolerance_m3':1e-8,'scope':'Representative full evaluated LHB3A + ICF3A straight join. LHB variants separately verify identical shared CBC outline. No curves, compression, yaw or runtime physics tested.'}
(P/'qa/LHB_ICF_straight_join.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['passed']
