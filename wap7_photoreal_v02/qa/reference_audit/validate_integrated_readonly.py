"""Portable independent geometry/rig audit. Never saves an opened model.

blender -b -t 1 --python-exit-code 1 --python validate_integrated_readonly.py -- \
  --master WAP7_detail.blend --baseline functional_interface_baseline.json \
  --report independent_validation.json

For the first reference capture, replace --baseline with --source v01.blend
and add --export-baseline functional_interface_baseline.json. Subsequent runs
need only the captured JSON and the master, with no work-folder dependency.
Legacy source.blend master.blend report.json positional arguments still work.
"""
import bpy, sys, json, hashlib, math, argparse
from pathlib import Path
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(argv)==3 and not argv[0].startswith('--'):
 argv=['--source',argv[0],'--master',argv[1],'--report',argv[2]]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--master',type=Path)
ref=parser.add_mutually_exclusive_group()
ref.add_argument('--source',type=Path)
ref.add_argument('--baseline',type=Path)
parser.add_argument('--export-baseline',type=Path)
parser.add_argument('--capture-only',action='store_true',help='Capture the source interface JSON without opening a master')
parser.add_argument('--report',type=Path)
options=parser.parse_args(argv)
source=options.source;target=options.master;out=options.report
baseline_path=options.baseline or Path(__file__).with_name('functional_interface_baseline.json')
if options.export_baseline and not source:parser.error('--export-baseline requires --source')
if options.capture_only and not(source and options.export_baseline):parser.error('--capture-only requires --source and --export-baseline')
if not options.capture_only and not(target and out):parser.error('--master and --report are required for validation')
inputs=[path for path in [target,source or baseline_path] if path]
for path in inputs:
 if not path.is_file():parser.error('Input file does not exist: '+str(path))
for path in [out,options.export_baseline]:
 if path and path.resolve() in {item.resolve() for item in inputs}:
  parser.error('A report or baseline export must not overwrite an input file')
def file_hash(path):
 digest=hashlib.sha256()
 with path.open('rb') as handle:
  for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block)
 return digest.hexdigest()
def drivers(o):
 return [(d.data_path,d.array_index,d.driver.expression,[(v.name,v.type,[(t.id.name if t.id else None,t.data_path) for t in v.targets]) for v in d.driver.variables]) for d in o.animation_data.drivers] if o.animation_data else []
def snap(o):
 return {'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[[float(v) for v in row] for row in o.matrix_world],'drivers':json.loads(json.dumps(drivers(o))),'custom':{k:o[k] for k in ['extension'] if k in o}}
def read(path):bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
if source:
 read(source)
 old={o.name:snap(o) for o in bpy.data.objects if o.type=='EMPTY'}
 old_units={'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length}
 baseline={'schema':'wap7-functional-interface-baseline-v1','source_name':source.name,'source_sha256':file_hash(source),'blender':bpy.app.version_string,'units':old_units,'objects':old,'scope':'Reference model interface contract, not manufacturer certification','approved_geometry_changes':{'BODY':'Restore local Y scale to 1.0 only','CAB_A_INTERIOR':'Refit cab geometry frame','CAB_B_INTERIOR':'Refit cab geometry frame'}}
 if options.export_baseline:
  options.export_baseline.parent.mkdir(parents=True,exist_ok=True)
  options.export_baseline.write_text(json.dumps(baseline,indent=2),encoding='utf-8')
 if options.capture_only:
  print(json.dumps({'baseline_written':str(options.export_baseline),'source_sha256':baseline['source_sha256'],'protected_objects':len(old),'units':old_units},indent=2))
  raise SystemExit(0)
else:
 baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
 if baseline.get('schema')!='wap7-functional-interface-baseline-v1':raise ValueError('Unsupported baseline schema')
 old=baseline['objects'];old_units=baseline['units']
 if not old or 'WAP7_ROOT' not in old:raise ValueError('Missing WAP7 baseline interface')
read(target);scene=bpy.context.scene
r={'schema':'wap7-independent-validation-v2','source':baseline['source_name'],'source_sha256':baseline['source_sha256'],'target':target.name,'target_sha256':file_hash(target),'blender':bpy.app.version_string,'units':{'system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length},'baseline_units':old_units,'protected_empties_count':len(old),'missing_protected':[],'changed_protected':[],'intentional_geometry_changes':[]}
# The documented geometric corrections restore BODY Y scale and renew the cab frames.
# Functional interface worlds are still compared strictly; old cab meshes are not a pass criterion.
allowed_geometry_frames={'BODY','CAB_A_INTERIOR','CAB_B_INTERIOR'}
for n,a in old.items():
 if n not in bpy.data.objects:r['missing_protected'].append(n);continue
 b=snap(bpy.data.objects[n]);d=max(abs(x-y) for ar,br in zip(a['matrix'],b['matrix']) for x,y in zip(ar,br))
 if d>1e-6 or a['type']!=b['type'] or a['parent']!=b['parent'] or a['drivers']!=b['drivers'] or a['custom']!=b['custom']:
  entry={'name':n,'type_before':a['type'],'type_after':b['type'],'matrix_max_delta':d,'parent_before':a['parent'],'parent_after':b['parent'],'driver_changed':a['drivers']!=b['drivers'],'custom_changed':a['custom']!=b['custom'],'matrix_before':a['matrix'],'matrix_after':b['matrix']}
  geometry_allowed=n in allowed_geometry_frames
  if n=='BODY':
   geometry_allowed=abs(bpy.data.objects[n].scale.y-1.0)<1e-6 and max(abs(a['matrix'][i][j]-b['matrix'][i][j]) for i in range(4) for j in range(4) if (i,j)!=(1,1))<1e-6
   entry['approved_change']='BODY local scale Y restored to1.0; baseline main skin width2.9084027m, nominal restored width3.152m'
  elif n in allowed_geometry_frames:entry['approved_change']='Cab geometry frame may be refitted to corrected body width'
  if geometry_allowed and a['type']==b['type'] and a['parent']==b['parent'] and a['drivers']==b['drivers'] and a['custom']==b['custom']:r['intentional_geometry_changes'].append(entry)
  else:r['changed_protected'].append(entry)
# Compare saved frames above; measure envelope in a folded pose only in memory.
saved_poses={}
for side in ['FRONT','REAR']:
 c=bpy.data.objects.get('PANTO_'+side+'_CTRL')
 if c:
  saved_poses[c.name]=c.get('extension',0);c['extension']=0.0;c.update_tag()
scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
r['saved_pantograph_extensions']=saved_poses;r['bounds_pose']='Both pantographs folded in memory'
root=bpy.data.objects.get('WAP7_ROOT')
if not root:raise RuntimeError('WAP7_ROOT is missing')
def render_members(layer_collection):
 if layer_collection.exclude or layer_collection.collection.hide_render:return set()
 members=set(layer_collection.collection.objects)
 for child in layer_collection.children:members|=render_members(child)
 return members
render_objects=render_members(bpy.context.view_layer.layer_collection)
asset=set(root.children_recursive)|{root};dg=bpy.context.evaluated_depsgraph_get();rows=[];nonfinite=[];tris=0
for o in sorted(asset,key=lambda o:o.name):
 if o.type not in {'MESH','CURVE','FONT'} or o.hide_render or o not in render_objects:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh()
 if me and me.vertices:
  lo=[float('inf')]*3;hi=[float('-inf')]*3
  for v in me.vertices:
   p=ev.matrix_world@v.co
   if not all(math.isfinite(c) for c in p):nonfinite.append(o.name)
   for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
  me.calc_loop_triangles();tris+=len(me.loop_triangles);rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'min':lo,'max':hi,'vertices':len(me.vertices),'triangles':len(me.loop_triangles)})
 ev.to_mesh_clear()
mins=[min(o['min'][k] for o in rows) for k in range(3)];maxs=[max(o['max'][k] for o in rows) for k in range(3)]
r.update({'visible_asset_objects':len(rows),'evaluated_triangles':tris,'bounds_m':{'min':mins,'max':maxs,'extent':[b-a for a,b in zip(mins,maxs)],'height_above_rail':maxs[2]},'over_nominal_width':[o for o in rows if o['min'][1]<-1.576001 or o['max'][1]>1.576001],'over_nominal_height':[o for o in rows if o['max'][2]>4.255001],'nonfinite':sorted(set(nonfinite)),'images':[{'name':i.name,'packed':bool(i.packed_file),'source':i.source,'path':i.filepath,'size':list(i.size)} for i in bpy.data.images if i.source=='FILE'],'asset_bounds_by_object':rows})
r['nominal_reference_m']={'length_over_couplers':20.562,'main_body_width':3.152,'pantograph_locked_height_above_rail':4.255}
r['nominal_deviation_m']={'visible_length':maxs[0]-mins[0]-20.562,'folded_height_above_rail':maxs[2]-4.255}
def datum(name):
 o=bpy.data.objects.get(name)
 return [float(x) for x in o.matrix_world.translation] if o else None
coupling_datums={end:datum('COUPLING_'+end) for end in ['FRONT','REAR']}
axle_datums={o.name:datum(o.name) for o in bpy.data.objects if o.name in old and o.name.startswith('AXLE_')}
bogie_datums={end:datum('BOGIE_'+end+'_YAW_Z') for end in ['A','B']}
r['interface_datums_m']={'coupling_anchor_world_positions':coupling_datums,'coupling_anchor_separation':(Vector(coupling_datums['FRONT'])-Vector(coupling_datums['REAR'])).length if all(coupling_datums.values()) else None,'bogie_world_positions':bogie_datums,'axle_world_positions':axle_datums,'total_axle_longitudinal_span':max(p[0] for p in axle_datums.values())-min(p[0] for p in axle_datums.values()) if axle_datums else None,'bogie_wheelbases':{end:max(p[0] for n,p in axle_datums.items() if n.startswith('AXLE_'+end+'_'))-min(p[0] for n,p in axle_datums.items() if n.startswith('AXLE_'+end+'_')) for end in ['A','B'] if any(n.startswith('AXLE_'+end+'_') for n in axle_datums)},'interpretation':'Coupling attachment anchors are preserved interface datums; their separation is not the visible length over couplers'}
body=bpy.data.objects.get('BODY');body_names={o.name for o in body.children_recursive} if body else set()
excluded=set()
for control in ['PANTO_FRONT_CTRL','PANTO_REAR_CTRL','CAB_A_INTERIOR','CAB_B_INTERIOR']:
 o=bpy.data.objects.get(control)
 if o:excluded|={c.name for c in o.children_recursive}|{o.name}
def envelope(items):
 if not items:return None
 lo=[min(o['min'][k] for o in items) for k in range(3)];hi=[max(o['max'][k] for o in items) for k in range(3)]
 return {'min':lo,'max':hi,'extent':[b-a for a,b in zip(lo,hi)],'object_count':len(items),'width_extrema_objects':[o['name'] for o in items if abs(o['min'][1]-lo[1])<1e-6 or abs(o['max'][1]-hi[1])<1e-6]}
r['separate_envelopes_m']={'main_body_skin':envelope([o for o in rows if o['name']=='Chamfered welded body shell']),'body_fixed_visual_branch_excluding_cabs_machinery_pantographs':envelope([o for o in rows if o['name'] in body_names and o['name'] not in excluded and not o['name'].startswith(('MACHV02_','CABV02_'))]),'complete_visible_asset':envelope(rows)}
r['width_interpretation']='Main-body 3152 mm is supported by WAP7 GA SKEL4490; generic tables also give3100. NWR max width3152 does not establish precise accessory stand-off allowances. Projections are reported, not silently flattened or treated as certification failures.'
# Sample mechanism in memory. Restored before exiting, never saved.
r['pantograph_samples']={}
for side in ['FRONT','REAR']:
 c=bpy.data.objects.get('PANTO_'+side+'_CTRL');head=bpy.data.objects.get('PANTO_'+side+'_HEAD_LEVEL_PIVOT')
 if not c or not head:continue
 orig=c.get('extension',0);samples=[]
 for t in [i/10 for i in range(11)]:
  c['extension']=t;c.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();up=head.matrix_world.to_quaternion()@Vector((0,0,1));up.normalize()
  # Measure the actual visible rebuilt collector, not the hidden legacy rig proxy.
  strips=[o for o in head.children_recursive if not o.hide_render and o in render_objects and o.type=='MESH' and 'collector contact carbon' in o.name]
  zz=[];contact_faces=[];dg=bpy.context.evaluated_depsgraph_get()
  for strip in strips:
   ev=strip.evaluated_get(dg);me=ev.to_mesh();zz.extend((ev.matrix_world@v.co).z for v in me.vertices)
   # The broad local +Z face is the actual manufactured carbon contact surface.
   faces=[f for f in me.polygons if f.normal.z>.999]
   if faces:
    face=max(faces,key=lambda f:f.center.z);normal=(ev.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized();face_z=[(ev.matrix_world@me.vertices[i].co).z for i in face.vertices]
    contact_faces.append({'object':strip.name,'level_error_degrees':math.degrees(math.acos(max(-1,min(1,normal.z)))),'contact_face_z_range':max(face_z)-min(face_z),'contact_face_top_z':max(face_z)})
   ev.to_mesh_clear()
  samples.append({'extension':t,'head_level_error_degrees':math.degrees(math.acos(max(-1,min(1,up.z)))),'visible_strip_objects':[s.name for s in strips],'strip_top_z':max(zz) if zz else None,'actual_contact_faces':contact_faces,'paired_contact_top_delta':max(f['contact_face_top_z'] for f in contact_faces)-min(f['contact_face_top_z'] for f in contact_faces) if len(contact_faces)==2 else None})
 c['extension']=orig;c.update_tag();scene.frame_set(scene.frame_current);bpy.context.view_layer.update();r['pantograph_samples'][side]=samples
r['pantograph_validation_pass']=set(r['pantograph_samples'])=={'FRONT','REAR'} and all(len(samples)==11 and all(s['head_level_error_degrees']<1e-4 and s['strip_top_z'] is not None and len(s['visible_strip_objects'])==2 and len(s['actual_contact_faces'])==2 and s['paired_contact_top_delta']<1e-5 and all(f['level_error_degrees']<.01 and f['contact_face_z_range']<1e-5 for f in s['actual_contact_faces']) for s in samples) for samples in r['pantograph_samples'].values())
r['mechanism_integrity_pass']=not(r['missing_protected'] or r['changed_protected'] or r['nonfinite']) and r['units']==old_units and r['pantograph_validation_pass']
r['pass']=r['mechanism_integrity_pass']
for name,value in saved_poses.items():
 c=bpy.data.objects[name];c['extension']=value;c.update_tag()
scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
r['limits']=['Pass refers to functional interface, metre units, finite geometry and collector-level checks','Dimension agreement is nominal class-scale evidence, not as-built certification','Raw vertical extent includes flanges below rail and is not height above rail','No operational or swept-collision certification','In-memory pose sampling does not modify saved model','Visible geometry uses current view-layer collection exclusion and render visibility','Old cab mesh count/placement is not a preservation criterion']
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:r[k] for k in ['target','target_sha256','pass','missing_protected','changed_protected','bounds_m','nominal_deviation_m']},indent=2))
if not r['pass']:raise RuntimeError('Independent interface validation failed; inspect the JSON report')
