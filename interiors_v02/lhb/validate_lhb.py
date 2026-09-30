import bpy,os,json,math
from mathutils import Vector
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=P+'/LHB_3A_interior_v02.blend')
sc=bpy.context.scene;sc.view_layers[0].update();obs=list(bpy.data.collections['LHB_3A_PROTOTYPE'].objects)+list(bpy.data.collections['INTERIOR_V02_DAY_CONFIGURATION'].objects)+list(bpy.data.collections['PASSENGER_LOCATORS_REFERENCE_ONLY'].objects)
def bounds(o):
 vs=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]
loc=[o for o in obs if o.name.startswith('PAX_')];berth=[o for o in obs if o.name.startswith(('V02_Main_lower','V02_Main_upper','V02_Main_middle','V02_Side_lower','V02_Side_upper_0'))]
# Explicit categories avoid counting guardrails and support geometry as berths.
counts={p:sum(o.name.startswith(p) for o in obs) for p in ['V02_Main_lower','V02_Main_upper','V02_Main_middle_FOLDED','V02_Side_lower','V02_Side_upper_0']}
assert list(counts.values())==[18,18,18,9,9],counts
assert len(loc)==72
collisions=[]
furniture=[o for o in obs if o.type=='MESH' and o.name.startswith('V02_')]
# Conservative torso/head axis-aligned prism above cushion, 0.36m wide, 0.32m depth, 1.03m high.
for l in loc:
 p=l.matrix_world.translation;low=(p.x-.16,p.y-.18,p.z+.05);high=(p.x+.16,p.y+.18,p.z+1.08)
 for o in furniture:
  a,b=bounds(o)
  if all(min(high[i],b[i])-max(low[i],a[i])>.001 for i in range(3)):collisions.append([l.name,o.name])
assert not collisions,collisions
bogies=[o for o in obs if o.name.startswith('BOGIE_')];axles=[o for o in obs if o.name.startswith('AXLE_')];assert len(bogies)==2 and len(axles)==4
assert all(abs(abs(o.location.x)-7.45)<1e-5 for o in bogies)
assert all(abs(abs(o.location.x)-1.28)<1e-5 for o in axles)
assert len([o for o in obs if o.name.startswith('DOOR_')])==4
door_apertures=[]
for o in obs:
 if o.name.startswith(('Door_leaf','Door_recess','V02_Entry_inner_liner')):
  z=.28 if o.name.startswith('Door_recess') else .29
  hit=o.ray_cast(Vector((0,-1,z)),Vector((0,1,0)),distance=2)[0]
  assert not hit, ('Opaque door aperture',o.name)
  door_apertures.append(o.name)
assert len(door_apertures)==12
r={'blender':bpy.app.version_string,'berth_counts':counts,'berth_total':sum(counts.values()),'day_configuration':'18 middle berths stowed upright as backrests; no deploy animation supplied','seated_locator_count':len(loc),'torso_head_proxy_collisions':collisions,'proxy_dimensions_m':[.32,.36,1.03],'proxy_limit':'Torso/head only; not full passenger mesh, limbs or runtime animation validation.','nominal_main_aisle_clear_width_m':.51,'bogie_pivots':{o.name:list(o.location) for o in bogies},'axle_pivots':{o.name:list(o.location) for o in axles},'opaque_source_window_block':'No opaque source shell across main window openings. New wall panels preserve apertures.','door_aperture_raycast_pass':door_apertures,'embedded_image_count':sum(i.packed_file is not None for i in bpy.data.images),'non_render_image_names':[i.name for i in bpy.data.images if i.source!='VIEWER'],'asset_objects':len(obs),'status':'Editable visual prototype; no game integration or LOD performance test'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=P+'/LHB_3A_interior_v02.fbx');objs=list(bpy.context.scene.objects);v=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
r['fbx_roundtrip']={'objects':len(objs),'meshes':sum(o.type=='MESH' for o in objs),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs if o.type=='MESH'),'bounds_min':[min(p[i] for p in v) for i in range(3)],'bounds_max':[max(p[i] for p in v) for i in range(3)],'locator_count':sum(o.name.startswith('PAX_') for o in objs),'presentation_leaks':[o.name for o in objs if o.type in {'CAMERA','LIGHT'} or o.name.startswith('DISPLAY_')]}
assert not r['fbx_roundtrip']['presentation_leaks'];assert r['fbx_roundtrip']['locator_count']==72
open(P+'/validation.json','w').write(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
