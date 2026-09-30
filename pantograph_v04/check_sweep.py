import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'WAP7_pantograph_v04.blend'));sc=bpy.context.scene
new=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('PANTO_')]
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [(min(v[i] for v in p),max(v[i] for v in p)) for i in range(3)]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=1e-7)
def overlaps(a,b):return all(a[i][0]<=b[i][1] and b[i][0]<=a[i][1] for i in range(3))
obstacles=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o in new:continue
 bb=bounds(o)
 if bb[2][1]>3.85 and bb[2][0]<5 and (bb[0][0]<7 and bb[0][1]>-7):obstacles.append((o,bounds(o),tree(o)))
collisions=[];intentional=[];maxangle=0;minimum_z=100;moving_min_z=100
for k in range(101):
 e=k/100
 for end in ['FRONT','REAR']:
  r=bpy.data.objects['PANTO_'+end+'_CTRL'];r['extension']=e;r.update_tag()
 bpy.context.view_layer.update()
 for end in ['FRONT','REAR']:
  he=bpy.data.objects['PANTO_'+end+'_HEAD_LEVEL_PIVOT'];maxangle=max(maxangle,max(abs(math.degrees(x)) for x in he.matrix_world.to_euler()))
 for o in new:
  bb=bounds(o);minimum_z=min(minimum_z,bb[2][0]);moving=not any(s in o.name for s in ['BASE_BEARING','BASE_HINGE'])
  if moving:moving_min_z=min(moving_min_z,bb[2][0])
  candidates=[(p,b,t) for p,b,t in obstacles if overlaps(bb,b)]
  if not candidates:continue
  t=tree(o)
  for p,b,pt in candidates:
   if t.overlap(pt):
    row={'extension':e,'part':o.name,'source_part':p.name}
    if 'BASE_BEARING' in o.name and p.name.startswith('Pantograph base'):intentional.append(row)
    else:collisions.append(row)
report={'samples_per_pantograph':101,'max_head_tilt_deg':maxangle,'minimum_moving_mesh_z_m':moving_min_z,'minimum_roof_panel_clearance_m':moving_min_z-3.872499942779541,'unintended_source_geometry_surface_intersections':collisions,'intentional_bearing_base_contacts_count':len(intentional),'method':'World-space BVH triangle surface intersections against preserved nearby roof/equipment; intentional bearing/base contact excluded. Joint self-contact is intentional; this does not claim manufacturing tolerances or actuator simulation.'}
(P/'sweep_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not collisions
