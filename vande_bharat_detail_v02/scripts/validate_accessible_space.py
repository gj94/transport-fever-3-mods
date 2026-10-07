import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
import interiors,materials
from prototype_dimensions import layout_for
src=OUT/'cars/VB_DTC.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
ctx={'collection':bpy.data.collections['VB_DTC_ASSET']}
# Distance in the horizontal plane from each physical triangle crossing the
# clear occupied-height band, using all integrated car meshes as obstacles.
c=Vector((-10.62,.70));radius=.75;zmin=1.35;zmax=2.67

def segment(a,b):
 d=b-a
 if d.length_squared<1e-14:return (a-c).length
 t=max(0,min(1,(c-a).dot(d)/d.length_squared));return (a+t*d-c).length

def triangle(a,b,d):
 cross=lambda x,y:x.x*y.y-x.y*y.x
 area=cross(b-a,d-a)
 if abs(area)>1e-12:
  aa=cross(b-c,d-c)/area;bb=cross(d-c,a-c)/area;cc=cross(a-c,b-c)/area
  if min(aa,bb,cc)>=-1e-8:return 0.
 return min(segment(a,b),segment(b,d),segment(d,a))
checks=[];hits=[]
for o in ctx['collection'].objects:
 if o.type!='MESH' or o.hide_render:continue
 if 'wheelchair_turning_zone_floor' in o.name:continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if not pts:continue
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if hi[2]<=zmin or lo[2]>=zmax or hi[0]<c.x-radius-.15 or lo[0]>c.x+radius+.15 or hi[1]<c.y-radius-.15 or lo[1]>c.y+radius+.15:continue
 o.data.calc_loop_triangles();distance=999
 for t in o.data.loop_triangles:
  pp=[pts[i] for i in t.vertices]
  if max(p.z for p in pp)<=zmin or min(p.z for p in pp)>=zmax:continue
  if max(p.x for p in pp)<c.x-radius-.15 or min(p.x for p in pp)>c.x+radius+.15:continue
  distance=min(distance,triangle(*(Vector((p.x,p.y)) for p in pp)))
 if distance<999:
  checks.append(dict(object=o.name,minimum_horizontal_distance_to_center_m=distance,margin_to_1_5m_circle_m=distance-radius))
  if distance<radius-.0001:hits.append(checks[-1])
checks.sort(key=lambda x:x['margin_to_1_5m_circle_m'])
# Clear jamb opening measured from actual mesh coordinate groups: these jambs
# each have one closed cuboid/rounded-rect island at the doorway edges.
j=bpy.data.objects['VB02_INT_service_accessible_clear_opening_jamb'];xs=sorted(set(round((j.matrix_world@v.co).x,7) for v in j.data.vertices));mid=-9.0425
left=max(x for x in xs if x<mid);right=min(x for x in xs if x>mid)
opening=right-left
# Local WC side obstruction includes its physical handle; shell outside face
# and the vehicle's actual sidewall inner face define the remaining corridor.
selected=[o for o in ctx['collection'].objects if o.type=='MESH' and any(k in o.name for k in ['service_accessible_curved_wall','service_accessible_door_handle','service_accessible_clear_opening_jamb','service_removable_closed_door'])]
wcmax=max((o.matrix_world@v.co).y for o in selected for v in o.data.vertices)
wall=bpy.data.objects.get('Open_sidewall');walls=[wall] if wall else []
wall_inner=min((o.matrix_world@v.co).y for o in walls for v in o.data.vertices if (o.matrix_world@v.co).y>1.4) if walls else 1.524
report=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_car=str(src.relative_to(OUT)) if src.exists() else 'prototype_base scaffold',updated_interior_in_memory=False,saved_over_source=False,occupied_height_band_z_m=[zmin,zmax],turning_circle_center_xy=list(c),turning_circle_diameter_m=1.50,minimum_obstacle_clearance_m=min(x['margin_to_1_5m_circle_m'] for x in checks),clearance_hits=hits,nearest_obstacles=checks[:15],door_clear_opening_between_jambs_m=opening,door_state='Static closed leaf; opening measurement applies with the leaf removed/slid out of the doorway',wc_maximum_lateral_projection_m=wcmax,actual_sidewall_inner_y_m=wall_inner,corridor_clear_including_WC_handle_m=wall_inner-wcmax,certification='Visual-layout geometric check only; no accessibility certification')
Path(str(OUT/'qa/DTC_accessibility_mesh_clearance.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
assert not hits,hits
assert opening>1.10
assert wall_inner-wcmax>1.15

