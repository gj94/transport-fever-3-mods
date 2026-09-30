"""Actual evaluated-geometry two-coach join test; positive-volume contacts use exact mesh Boolean."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
variants=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['1A','2A','3A','2S','CC','SL','GS']
def bb(o,shift=0):
 pts=[o.matrix_world@v.co+Vector((shift,0,0)) for v in o.data.vertices]
 return [(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)]
def intersect_volume(a,b,shift):
 # Meshes are already modifier-baked by source builder. Copy mesh data and transforms
 # into a temporary scene pair; the second car is translated by actual anchor pitch.
 oa=bpy.data.objects.new('QA_A',a.data.copy());ob=bpy.data.objects.new('QA_B',b.data.copy());bpy.context.scene.collection.objects.link(oa);bpy.context.scene.collection.objects.link(ob);oa.matrix_world=a.matrix_world.copy();ob.matrix_world=Matrix.Translation((shift,0,0))@b.matrix_world;bpy.context.view_layer.update()
 mod=oa.modifiers.new('EXACT evaluated solid intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=ob
 deps=bpy.context.evaluated_depsgraph_get();ev=oa.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);volume=abs(bm.calc_volume(signed=True));verts=len(me.vertices);faces=len(me.polygons);bm.free();ev.to_mesh_clear();bpy.data.objects.remove(oa,do_unlink=True);bpy.data.objects.remove(ob,do_unlink=True)
 return {'intersection_volume_m3':volume,'boolean_result_vertices':verts,'boolean_result_faces':faces}
reports=[]
for v in variants:
 folder=P/v;bpy.ops.wm.open_mainfile(filepath=str(folder/f'ICF_{v}_master.blend'));root=bpy.data.objects[f'ICF_{v}_ROOT'];bpy.context.view_layer.update();meshes=[o for o in root.children_recursive if o.type=='MESH'];pitch=22.297
 # Retain all objects that could physically approach the join; this includes body,
 # end wall, gangway, tread plates, buffers, coupling, hoses and signs.
 left=[(o,bb(o)) for o in meshes if bb(o)[0][1]>9.5];right=[(o,bb(o,pitch)) for o in meshes if bb(o,pitch)[0][0]<12.8]
 positive=[];touch=[];errors=[]
 for a,aa in left:
  for b,bbx in right:
   overlap=[min(aa[k][1],bbx[k][1])-max(aa[k][0],bbx[k][0]) for k in range(3)]
   if all(d>1e-7 for d in overlap):
    test=intersect_volume(a,b,pitch);test.update(first_mesh=a.name,second_mesh=b.name,aabb_overlap_m=overlap);positive.append(test)
    if test['intersection_volume_m3']>1e-8:errors.append(test)
   elif all(d>=-1e-6 for d in overlap):
    touch.append({'first_mesh':a.name,'second_mesh':b.name,'aabb_overlap_m':overlap,'interpretation':'Zero-thickness nominal mating surface, not positive solid overlap'})
 anchora=bpy.data.objects['COUPLING_FRONT'].matrix_world.copy();anchorb=Matrix.Translation((pitch,0,0))@bpy.data.objects['COUPLING_REAR'].matrix_world
 anchor_error=(anchora.translation-anchorb.translation).length
 forwarddot=(anchora.to_3x3()@Vector((1,0,0))).dot(anchorb.to_3x3()@Vector((1,0,0)))
 if anchor_error>1e-6 or abs(forwarddot+1)>1e-6:errors.append('Anchor mating frame mismatch')
 report={'variant':v,'passed':not errors,'test':'Two identical full coaches; second car translated +22.297m along X; actual baked evaluated meshes, not only anchor coordinates','all_meshes_per_coach':len(meshes),'near_join_meshes_left':len(left),'near_join_meshes_right':len(right),'anchor_position_error_m':anchor_error,'outward_axis_dot_product':forwarddot,'body_end_clearance_m':pitch-21.337,'positive_aabb_candidates_exact_boolean_tested':positive,'zero_thickness_mating_contacts':touch,'unexpected_positive_volume_intersections':errors,'tolerances':{'aabb_positive_m':1e-7,'positive_volume_failure_m3':1e-8},'cbc_profile_relative_to_plane_m':[[-.30,-.10],[-.23,-.18],[-.08,-.18],[-.08,-.045],[.08,.045],[.08,.18],[-.15,.18],[-.30,.10]],'scope':'Straight static join only; yaw/compression and coupled curves remain runtime work'}
 (folder/'qa'/'two_coach_straight_join.json').write_text(json.dumps(report,indent=2));reports.append(report);print('STRAIGHT_JOIN',v,'PASS' if not errors else 'FAIL',len(positive),'positive AABB candidates',len(touch),'surface contacts',flush=True);assert not errors,(v,errors)
(P/'qa'/'two_coach_straight_joins.json').write_text(json.dumps(reports,indent=2))
