"""EC fabric-only curvature refinement. Fixed bounds and all hardware stay unchanged."""
import bpy, hashlib, struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def _hardware_stamp(me,target):
 h=hashlib.sha256()
 for p in me.polygons:
  if p.material_index==target:continue
  h.update(struct.pack('<ii?',p.material_index,len(p.vertices),p.use_smooth))
  for vi in p.vertices:h.update(struct.pack('<3f',*me.vertices[vi].co))
 return h.hexdigest()

def apply_to_mesh(me):
 if me.get('ec_fabric_refinement')=='bounded_catmull_clark_2':return {'already_refined':True}
 target=next(i for i,m in enumerate(me.materials) if m.name=='VB02_INT_Charcoal_jacquard_EC')
 before=_hardware_stamp(me,target)
 oldv=[v.co.copy() for v in me.vertices];oldp=[(tuple(p.vertices),p.material_index,p.use_smooth) for p in me.polygons]
 chosen=[f for f,mi,sm in oldp if mi==target];adj={v:set() for f in chosen for v in f}
 for f in chosen:
  for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
 islands=[];unseen=set(adj)
 while unseen:
  start=min(unseen);stack=[start];ids=set()
  while stack:
   a=stack.pop()
   if a in ids:continue
   ids.add(a);stack.extend(adj[a]-ids)
  unseen-=ids;islands.append(sorted(ids))
 verts=[];faces=[];mats=[];smooth=[];mapping={}
 for f,mi,sm in oldp:
  if mi==target:continue
  ff=[]
  for vi in f:
   if vi not in mapping:mapping[vi]=len(verts);verts.append(tuple(oldv[vi]))
   ff.append(mapping[vi])
  faces.append(tuple(ff));mats.append(mi);smooth.append(sm)
 reports=[]
 for ids in islands:
  lookup={a:i for i,a in enumerate(ids)};vv=[oldv[a] for a in ids];ff=[tuple(lookup[a] for a in f) for f in chosen if f[0] in lookup]
  lo=Vector(tuple(min(v[k] for v in vv) for k in range(3)));hi=Vector(tuple(max(v[k] for v in vv) for k in range(3)))
  tm=bpy.data.meshes.new('EC_fabric_refinement_temporary');tm.from_pydata(vv,[],ff);tm.update()
  ob=bpy.data.objects.new('EC_fabric_refinement_temporary',tm);bpy.context.scene.collection.objects.link(ob)
  sub=ob.modifiers.new('Fabric curvature only','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=2;sub.render_levels=2
  bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();nv=[v.co.copy() for v in em.vertices];nf=[tuple(p.vertices) for p in em.polygons]
  nlo=Vector(tuple(min(v[k] for v in nv) for k in range(3)));nhi=Vector(tuple(max(v[k] for v in nv) for k in range(3)))
  nv=[Vector(tuple(lo[k]+(v[k]-nlo[k])*(hi[k]-lo[k])/(nhi[k]-nlo[k]) for k in range(3))) for v in nv]
  bounds_error=max(abs(min(v[k] for v in nv)-lo[k]) for k in range(3));bounds_error=max(bounds_error,max(abs(max(v[k] for v in nv)-hi[k]) for k in range(3)))
  old_tree=BVHTree.FromPolygons(vv,ff,all_triangles=False)
  offset=max(old_tree.find_nearest(v)[3] for v in nv)
  base=len(verts);verts.extend(tuple(v) for v in nv);faces.extend(tuple(base+i for i in f) for f in nf);mats.extend([target]*len(nf));smooth.extend([True]*len(nf))
  reports.append({'old_vertices':len(vv),'new_vertices':len(nv),'old_polygons':len(ff),'new_polygons':len(nf),'minimum':list(lo),'maximum':list(hi),'envelope_error_m':bounds_error,'maximum_new_vertex_distance_from_old_surface_m':offset})
  ev.to_mesh_clear();bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(tm)
 me.clear_geometry();me.from_pydata(verts,[],faces)
 for p,mi,sm in zip(me.polygons,mats,smooth):p.material_index=mi;p.use_smooth=sm
 me.update();after=_hardware_stamp(me,target);assert before==after,'Non-fabric hardware changed'
 assert len(islands)==4 and max(r['envelope_error_m'] for r in reports)<1e-6
 me['ec_fabric_refinement']='bounded_catmull_clark_2'
 return {'cloth_islands':len(islands),'hardware_before_sha256':before,'hardware_after_sha256':after,'hardware_identical':before==after,'islands':reports,'geometry_scope':'Only EC cushion/back/wing cloth surfaces. Each original axis-aligned envelope restored; no marker/object transform or hardware changes.'}
