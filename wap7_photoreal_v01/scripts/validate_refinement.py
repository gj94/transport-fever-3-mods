"""Geometry/rig verification, not a TF3 runtime test. Blender 4.3.2.
Run from the package: blender -b -t 2 --python scripts/validate_refinement.py -- ../pantograph_v04/WAP7_pantograph_v04.blend
"""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else OUT.parent/'pantograph_v04/WAP7_pantograph_v04.blend'
def meshhash(o):
 return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest() if o.type=='MESH' else None
def stamp(o):
 return {'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[[float(v) for v in row] for row in o.matrix_world],'geometry':meshhash(o),'drivers':[(d.data_path,d.array_index,d.driver.expression,[(v.name,v.type,[(t.id.name if t.id else None,t.data_path) for t in v.targets]) for v in d.driver.variables]) for d in o.animation_data.drivers] if o.animation_data else []}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.view_layer.update()
protected={o.name:stamp(o) for o in bpy.data.objects if o.type=='EMPTY' or o.name in bpy.data.collections['CAB_INTERIORS_V02'].objects};interiors=list(bpy.data.collections['CAB_INTERIORS_V02'].objects.keys())
bpy.ops.wm.open_mainfile(filepath=str(OUT/'WAP7_photoreal_v01.blend'));bpy.context.view_layer.update();s=bpy.context.scene
missing=[];changed=[]
for name,old in protected.items():
 if name not in bpy.data.objects:missing.append(name);continue
 new=stamp(bpy.data.objects[name]);delta=max(abs(a-b) for ar,br in zip(old['matrix'],new['matrix']) for a,b in zip(ar,br))
 if delta>1e-6 or old['parent']!=new['parent'] or old['geometry']!=new['geometry'] or old['drivers']!=new['drivers']:changed.append({'name':name,'matrix_delta':delta,'geometry_changed':old['geometry']!=new['geometry'],'hierarchy_changed':old['parent']!=new['parent'],'drivers_changed':old['drivers']!=new['drivers']})
asset=[o for o in bpy.data.objects['WAP7_ROOT'].children_recursive if o.type=='MESH' and not o.hide_render]
dg=bpy.context.evaluated_depsgraph_get();mins=[1e8]*3;maxs=[-1e8]*3;tris=0;nan=[]
for o in asset:
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles)
 for v in me.vertices:
  p=o.matrix_world@v.co
  if not all(math.isfinite(q) for q in p):nan.append(o.name)
  for i in range(3):mins[i]=min(mins[i],p[i]);maxs[i]=max(maxs[i],p[i])
 ev.to_mesh_clear()
# 11 poses for both rigs, measured actual strip top and levelness.
poses={}
for key in ['FRONT','REAR']:
 ctrl=bpy.data.objects['PANTO_'+key+'_CTRL'];rows=[]
 for v in [i/10 for i in range(11)]:
  ctrl['extension']=v;ctrl.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
  strip=bpy.data.objects['PANTO_'+key+'_CONTACT_STRIP_1'];coords=[strip.matrix_world@vv.co for vv in strip.data.vertices];zz=sorted(set(round(p.z,6) for p in coords));pivot=bpy.data.objects['PANTO_'+key+'_HEAD_LEVEL_PIVOT'];up=pivot.matrix_world.to_quaternion()@Vector((0,0,1));rows.append({'extension':v,'contact_top_z_m':max(p.z for p in coords),'head_level_error_degrees':math.degrees(math.acos(max(-1,min(1,up.z))))})
 ctrl['extension']=0;ctrl.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update();poses[key]=rows
# Presentation contact-height proof in a live pose, then restore source authoring state.
ctrl=bpy.data.objects['PANTO_REAR_CTRL'];ctrl['extension']=(math.degrees(math.asin((5.53-4.212)/2.45))-1)/35;ctrl.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update();st=bpy.data.objects['PANTO_REAR_CONTACT_STRIP_1'];contact=max((st.matrix_world@v.co).z for v in st.data.vertices)
report={'blender':bpy.app.version_string,'master_sha256':hashlib.sha256((OUT/'WAP7_photoreal_v01.blend').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_objects_checked':len(protected),'interior_objects_preserved':len(interiors),'missing_protected':missing,'changed_protected':changed,'units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length},'coupling_anchors_m':{n:list(bpy.data.objects[n].matrix_world.translation) for n in ['COUPLING_FRONT','COUPLING_REAR']},'asset_visible_evaluated_bounds_m':{'min':mins,'max':maxs,'extent':[b-a for a,b in zip(mins,maxs)]},'asset_evaluated_triangles':tris,'asset_visible_mesh_objects':len(asset),'nonfinite_geometry_objects':sorted(set(nan)),'images':[{'name':i.name,'packed':bool(i.packed_file),'path':i.filepath} for i in bpy.data.images if i.source=='FILE'],'pantograph_pose_samples':poses,'hero_contact_proof':{'contact_wire_m':5.53,'actual_strip_top_m':contact,'error_m':contact-5.53},'scope_limits':['No TF3 conversion or runtime test','No finite-element/manufacturer geometry validation','No swept collision certification for added cosmetic hardware','Hidden-side fitting placement remains representative'],'pass':not missing and not changed and not nan and abs(contact-5.53)<1e-5}
(OUT/'qa/geometry_and_rig_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['pass']
