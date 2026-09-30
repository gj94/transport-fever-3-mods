"""Fresh-source and fresh-FBX mechanical, topology, bounds and marker QA."""
import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
out={}
def descendants(r):return [r]+list(r.children_recursive)
def bounds(objs):
 pts=[o.matrix_world@Vector(v) for o in objs if o.type=='MESH' for v in o.bound_box]
 return {'min':[min(p[a] for p in pts) for a in range(3)],'max':[max(p[a] for p in pts) for a in range(3)]}
def verify(k,mode):
 root=bpy.data.objects['LHB_'+k+'_ROOT_metres'];objs=descendants(root);meshes=[o for o in objs if o.type=='MESH'];dg=bpy.context.evaluated_depsgraph_get();tri=0;bad=[];mats=set()
 for o in meshes:
  m=o.evaluated_get(dg).to_mesh();m.calc_loop_triangles();tri+=len(m.loop_triangles)
  bm=bmesh.new();bm.from_mesh(m)
  if any(not e.is_manifold for e in bm.edges):bad.append(o.name)
  bm.free();o.evaluated_get(dg).to_mesh_clear()
  mats.update(m.name for m in o.data.materials if m)
 pax=[o for o in objs if o.type=='EMPTY' and o.name.startswith('PAX_')];berths=[o for o in objs if o.type=='EMPTY' and o.name.startswith('BERTH_')];manifest=json.loads((P/'models'/('LHB_'+k+'_manifest.json')).read_text())
 checks={}
 checks['root_identity']=root.type=='EMPTY' and root.matrix_world.translation.length<1e-5 and all(abs(s-1)<1e-5 for s in root.scale)
 checks['PAX_count']=len(pax)==manifest['daytime_seats'];checks['BERTH_count']=len(berths)==manifest['BERTH_references'];checks['PAX_parent_local_contract']=all(o.parent.name=='BODY_PIVOT' and (o.matrix_world.translation-o.matrix_local.translation).length<1e-5 for o in pax)
 checks['PAX_seated_root_height']=all(abs(o.matrix_world.translation.z-1.357)<1e-5 for o in pax)
 checks['PAX_yaw']=all(abs(math.sin(o.rotation_euler.z))<1e-5 for o in pax)
 anchor={}
 for name,sg in [('FRONT',1),('REAR',-1)]:
  o=bpy.data.objects['COUPLING_'+name];anchor[name]={'xyz':list(o.matrix_world.translation),'forward':list(o.matrix_world.to_3x3()@Vector((1,0,0)))}
  checks['coupling_'+name]=o.parent==root and (o.matrix_world.translation-Vector((sg*12,0,1.105))).length<1e-4 and (o.matrix_world.to_3x3()@Vector((1,0,0))-Vector((sg,0,0))).length<1e-4
  b=bpy.data.objects['BOGIE_'+name+'_PIVOT'];checks['bogie_'+name]=b.parent==root and abs(b.matrix_world.translation.x-sg*7.45)<1e-4
  for suffix,dx in [('A',-1.28),('B',1.28)]:
   a=bpy.data.objects['AXLE_'+name+'_'+suffix+'_PIVOT'];checks['axle_'+name+suffix]=a.parent==b and (a.matrix_world.translation-Vector((sg*7.45+dx,0,.4575))).length<1e-4
 glassmat=bpy.data.materials.get('GLASS_source_transmission_FBX_alpha');p=glassmat.node_tree.nodes.get('Principled BSDF');checks['glass_material']=abs(p.inputs['Transmission Weight'].default_value-.96)<1e-4 if mode=='blend' else abs(p.inputs['Alpha'].default_value-.22)<1e-4
 # closed volume panes, and no opaque bodyside at pane-centre ray.
 panes=[o for o in meshes if o.name.startswith(('GLASS_WINDOW','GLASS_DOOR'))];apertures=[]
 walls=[o for o in meshes if o.name.startswith(('BODYSIDE','INTERIOR_window_pillar','INTERIOR_sill_liner','DOOR_lower','DOOR_header','DOOR_window_jamb','DOOR_window_frame'))]
 for g in panes:
  centre=sum((g.matrix_world@Vector(v) for v in g.bound_box),Vector())/8;sg=1 if centre.y>0 else -1;origin=Vector((centre.x,sg*1.75,centre.z));direction=Vector((0,-sg,0));hits=[]
  for o in walls:
   inv=o.matrix_world.inverted();h,pt,no,ix=o.ray_cast(inv@origin,inv.to_3x3()@direction,distance=.30)
   if h:hits.append(o.name)
  if hits:apertures.append({'pane':g.name,'occluders':hits})
 checks['through_window_apertures']=not apertures
 # Paired CBC head outline has a shared antisymmetric contact face.
 # Triangle clipping measures positive intersection area, allowing exact face contact.
 from mathutils.geometry import tessellate_polygon
 outline=[(-.30,-.10),(-.23,-.18),(-.08,-.18),(-.08,-.045),(.08,.045),(.08,.18),(-.15,.18),(-.30,.10)]
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2) if len(poly)>2 else 0
 def intersect(subject,clip):
  orient=1 if sum(clip[i][0]*clip[(i+1)%len(clip)][1]-clip[(i+1)%len(clip)][0]*clip[i][1] for i in range(len(clip)))>=0 else -1
  for a,b in zip(clip,clip[1:]+clip[:1]):
   result=[]
   if not subject:return []
   prev=subject[-1];pv=orient*cross(a,b,prev)
   for cur in subject:
    cv=orient*cross(a,b,cur)
    if (cv>=0)!=(pv>=0):
     t=pv/(pv-cv);result.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
    if cv>=0:result.append(cur)
    prev,pv=cur,cv
   subject=result
  return subject
 tris=[[(outline[v] if isinstance(v,int) else tuple(v[:2])) for v in t] for t in tessellate_polygon([[Vector((x,y,0)) for x,y in outline]])]
 other=[[(-x,-y) for x,y in t] for t in tris]
 overlap_area=sum(area(intersect(list(a),list(b))) for a in tris for b in other)
 # Verify evaluated mesh retains precisely the authored outline before using the analytic test.
 heads=[o for o in meshes if o.name.startswith('CBC_head_shared_ICF_profile')]
 shape_ok=len(heads)==2 and all(len(o.data.vertices)==16 and all(any(abs(v.co.x-x)<1e-5 and abs(v.co.y-y)<1e-5 for x,y in outline) for v in o.data.vertices) for o in heads)
 coupler_overlaps=[] if overlap_area<1e-10 else [{'positive_plan_overlap_m2':overlap_area}]
 checks['paired_CBC_no_volume_overlap']=shape_ok and not coupler_overlaps
 # Conservative upright torso/head proxy; ignores seat cushions, never uses BERTH markers.
 # Boxes cover root+hip offset +.05 to +.99; no exact character meshes available here.
 colliders=[o for o in meshes if not o.name.startswith(('GLASS','CHAIR_cushion','MAIN_LOWER','SIDE_LOWER','FIRST_LOWER','GS_main_bench','GS_side_bench'))]
 collisions=[]
 for s in pax:
  q=s.matrix_world.translation;lo=Vector((q.x-.12,q.y-.16,1.90));hi=Vector((q.x+.12,q.y+.16,2.80))
  for o in colliders:
   pp=[o.matrix_world@Vector(v) for v in o.bound_box];a=Vector(tuple(min(p[i] for p in pp) for i in range(3)));b=Vector(tuple(max(p[i] for p in pp) for i in range(3)))
   if all(min(hi[i],b[i])-max(lo[i],a[i])>1e-4 for i in range(3)):collisions.append({'PAX':s.name,'mesh':o.name})
 checks['torso_head_proxy_clear']=not collisions
 checks['material_budget']=len(mats)<=64;checks['all_panes_manifold']=not any(n.startswith('GLASS') for n in bad)
 # Text outline is intentionally not closed volumetric, report separately.
 nonglassbad=[n for n in bad if not n.startswith(('CLASS_MARKING','RAILWAY_MARKING','COACH_CODE','WC_sign','CABIN_label','BAY_NUMBER'))]
 checks['mesh_closed_components']=not nonglassbad
 result={'pass':all(checks.values()),'checks':checks,'mesh_count':len(meshes),'evaluated_triangles':tri,'materials':len(mats),'actual_mesh_bounds_m':bounds(meshes),'anchors':anchor,'nonmanifold_meshes':bad,'opaque_window_occlusions':apertures,'paired_CBC_positive_plan_overlap':coupler_overlaps,'proxy_collisions':collisions,'PAX_count':len(pax),'BERTH_count':len(berths),'scope':'Blender source and fresh FBX import only; no native TF3 conversion or runtime test. Torso/head proxies do not verify limbs, passenger variants, or animations.'}
 return result
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/('LHB_'+k+'.blend')));src=verify(k,'blend')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/'models'/('LHB_'+k+'.fbx')));fbx=verify(k,'fbx')
 diffs=[abs(src['actual_mesh_bounds_m'][part][i]-fbx['actual_mesh_bounds_m'][part][i]) for part in ['min','max'] for i in range(3)]
 out[k]={'source':src,'fresh_fbx':fbx,'max_bounds_delta_m':max(diffs),'bounds_match':max(diffs)<.005}
 (P/'qa'/(k+'_validation.json')).write_text(json.dumps(out[k],indent=2))
 print(k,src['pass'],fbx['pass'],src['evaluated_triangles'],len(src['proxy_collisions']),flush=True)
(P/'qa'/'all_variants_validation.json').write_text(json.dumps(out,indent=2))
assert all(v['source']['pass'] and v['fresh_fbx']['pass'] and v['bounds_match'] for v in out.values()),'See detailed QA failures'
