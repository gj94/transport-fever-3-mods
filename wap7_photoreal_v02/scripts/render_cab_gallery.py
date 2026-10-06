"""Render cab proofs from an explicit, already-integrated delivery master.

This script NEVER calls the cab builder, imports a component authoring module,
or saves a .blend. It changes only in-memory presentation settings, new proof
cameras/lights and a new world. Source geometry, materials and vehicle poses
are checked before/after staging and rendering. Existing source lights are
muted only in memory. Use --stage-only to inspect the setup without rendering.

Example (only run when a render slot is available):
 blender -b --python-exit-code 1 --python render_cab_gallery.py -- \
   --master /path/to/final.blend --view panel_A --samples 96 --width 1600 \
   --threads 2 --output /path/to/panel_A.png --expected-sha256 <sha256>
"""
import argparse, array, hashlib, json, math, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

VIEWS={
 'panel_A':{'position':(8.015,.568,2.980),'target':(8.787,.568,2.656),'lens_mm':24.0,'aspect':1.6},
 'overview_A':{'position':(7.470,0,3.130),'target':(8.960,0,2.680),'lens_mm':17.5,'aspect':4/3},
 'seats_rear':{'position':(8.940,.030,3.065),'target':(7.770,-.010,2.340),'lens_mm':17.5,'aspect':4/3},
}
# Canonical cab coordinates. The same setup follows each existing cab root.
LIGHTS=[
 ('front_daylight',(10.60,-.80,5.20),(8.30,0,2.80),180.0,3.20,(.96,.98,1.00)),
 ('ceiling_practical',(8.10,0,3.53),(8.40,0,2.20),32.0,1.25,(1.00,.97,.91)),
 ('soft_bounce_fill',(7.41,0,3.12),(8.86,0,2.65),50.0,1.40,(.97,.99,1.00)),
 ('footwell_inspection_fill',(8.10,.20,1.93),(8.73,.78,1.83),12.0,.55,(.97,.99,1.00)),
 ('seat_inspection_fill',(8.24,-.18,2.12),(7.98,.78,1.93),14.0,.50,(.97,.99,1.00)),
 ('side_daylight',(8.55,-3.30,4.60),(8.50,0,2.70),160.0,2.30,(.87,.93,1.00)),
]
WORLD_COLOR=(.65,.71,.77,1.0)
WORLD_STRENGTH=.60


def sha256_file(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()


def numbers(v):return [float(x) for x in v]
def matrix_rows(m):return [numbers(row) for row in m]


def geometry_digest(names):
 """Hash source meshes/topology and object poses without evaluated-mesh copies.

 One compact float buffer at a time keeps the extra memory bounded. Text and
 other curve settings are included; no source geometry is changed or evaluated
 into a duplicate mesh. Modifier identity/enabled state and material slots are
 recorded as part of the source object description.
 """
 h=hashlib.sha256();seen=set();mesh_count=0;vertex_count=0;object_count=0
 def emit(value):h.update(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
 for name in sorted(names):
  o=bpy.data.objects.get(name)
  if o is None:raise RuntimeError('Source object disappeared: '+name)
  if o.type in {'LIGHT','CAMERA'}:continue
  object_count+=1
  emit({'object':name,'type':o.type,'parent':o.parent.name if o.parent else None,
        'world':matrix_rows(o.matrix_world),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,
        'materials':[s.material.name if s.material else None for s in o.material_slots],
        'modifiers':[(m.name,m.type,m.show_render,m.show_viewport) for m in o.modifiers]})
  data=o.data
  if not data or data.as_pointer() in seen:continue
  seen.add(data.as_pointer())
  if o.type=='MESH':
   mesh_count+=1;vertex_count+=len(data.vertices)
   emit({'mesh':data.name,'vertices':len(data.vertices),'loops':len(data.loops),'polygons':len(data.polygons)})
   a=array.array('f',[0.0])*(len(data.vertices)*3);data.vertices.foreach_get('co',a);h.update(a.tobytes());del a
   a=array.array('i',[0])*len(data.loops);data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());del a
   a=array.array('i',[0])*len(data.polygons);data.polygons.foreach_get('loop_total',a);h.update(a.tobytes());del a
   a=array.array('i',[0])*len(data.polygons);data.polygons.foreach_get('material_index',a);h.update(a.tobytes());del a
  elif o.type in {'CURVE','SURFACE','FONT'}:
   emit({'curve':data.name,'body':getattr(data,'body',None),'dimensions':data.dimensions,
         'extrude':data.extrude,'bevel_depth':data.bevel_depth,'bevel_resolution':data.bevel_resolution,
         'resolution_u':data.resolution_u})
   for spline in data.splines:
    emit({'spline_type':spline.type,'cyclic':spline.use_cyclic_u,
          'points':[numbers(p.co) for p in spline.points],
          'bezier':[(numbers(p.co),numbers(p.handle_left),numbers(p.handle_right)) for p in spline.bezier_points]})
 return {'sha256':h.hexdigest(),'source_geometry_objects':object_count,'unique_meshes':mesh_count,'base_vertices':vertex_count}


def pose_snapshot():
 prefixes=('WAP7_ROOT','BODY','CAB_A_INTERIOR','CAB_B_INTERIOR','CABV02_1_Rear_door_hinge','CABV02_2_Rear_door_hinge','COUPLING','DRIVER','BOGIE','AXLE','PANTO')
 result={}
 for o in bpy.data.objects:
  if o.type=='EMPTY' and o.name.startswith(prefixes):
   result[o.name]={'world':matrix_rows(o.matrix_world),'parent':o.parent.name if o.parent else None,
                   'open_angle_deg':o.get('open_angle_deg'),'extension':o.get('extension')}
 return {'frame':bpy.context.scene.frame_current,'unit_system':bpy.context.scene.unit_settings.system,
         'scale_length':bpy.context.scene.unit_settings.scale_length,'roots_and_controls':result}


def source_readiness(stage_only):
 required=['WAP7_ROOT','BODY','CAB_A_INTERIOR','CAB_B_INTERIOR','CABV02_1_Panel_A_removable_face']
 missing=[n for n in required if n not in bpy.data.objects]
 if missing:raise RuntimeError('The input is not an integrated cab master; missing '+', '.join(missing))
 result={'body_scale':numbers(bpy.data.objects['BODY'].scale),'paint_recipes':{},'warnings':[]}
 if abs(bpy.data.objects['BODY'].scale.y-1.0)>1e-5:
  result['warnings'].append('The source still has a legacy BODY Y scale; this is not the corrected full-width master')
 for suffix in ['Warm grey interior enamel','Folded desk light grey satin','Charcoal removable instrument panel']:
  ma=bpy.data.materials.get('CABV02_'+suffix)
  result['paint_recipes'][suffix]=ma.get('cab_paint_recipe') if ma else None
  if not ma or ma.get('cab_paint_recipe')!='dielectric_metric_v1':result['warnings'].append('Stale or missing cab paint: '+suffix)
 cord=bpy.data.objects.get('CABV02_1_Panel_A_BL_key_tether')
 result['lanyard_base_vertices']=len(cord.data.vertices) if cord and cord.type=='MESH' else 0
 if result['lanyard_base_vertices']<500:result['warnings'].append('The master predates the final smooth lanyard polish')
 if result['warnings'] and not stage_only:raise RuntimeError('Final gallery input failed readiness: '+'; '.join(result['warnings']))
 return result


def add_presentation(args,master_sha):
 scene=bpy.context.scene;before_lights=[]
 for o in list(bpy.data.objects):
  if o.type=='LIGHT':
   before_lights.append({'name':o.name,'previous_hide_render':bool(o.hide_render)})
   o.hide_render=True
 coll=bpy.data.collections.new('CABFINAL_PROOF_STAGE_'+master_sha[:8]);scene.collection.children.link(coll)
 lights=[]
 for index,root_name in [(1,'CAB_A_INTERIOR'),(2,'CAB_B_INTERIOR')]:
  root=bpy.data.objects[root_name]
  for label,loc,target,power,size,color in LIGHTS:
   name=f'CABFINAL_{index}_{label}';d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
   o=bpy.data.objects.new(name,d);coll.objects.link(o);o.location=root.matrix_world @ Vector(loc);target_world=root.matrix_world @ Vector(target)
   o.rotation_euler=(target_world-o.location).to_track_quat('-Z','Y').to_euler();o.visible_camera=False;o.visible_transmission=False
   lights.append({'name':o.name,'type':'AREA','shape':'DISK','energy_watts':power,'size_m':size,'color_linear':list(color),
                  'world_location':numbers(o.location),'world_target':numbers(target_world),'visible_camera':False,'visible_transmission':False})
 view=VIEWS[args.view];root=bpy.data.objects['CAB_A_INTERIOR' if args.cab==1 else 'CAB_B_INTERIOR']
 d=bpy.data.cameras.new('CABFINAL_'+args.view);camera=bpy.data.objects.new(d.name,d);coll.objects.link(camera)
 camera.location=root.matrix_world @ Vector(view['position']);target=root.matrix_world @ Vector(view['target'])
 camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();d.lens=view['lens_mm'];d.sensor_width=36;d.sensor_fit='AUTO';d.clip_start=.02;d.clip_end=500;scene.camera=camera
 world=bpy.data.worlds.new('CABFINAL_NeutralDaylight_'+master_sha[:8]);world.use_nodes=True
 world.node_tree.nodes['Background'].inputs['Color'].default_value=WORLD_COLOR;world.node_tree.nodes['Background'].inputs['Strength'].default_value=WORLD_STRENGTH;scene.world=world
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=False
 scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=12
 if args.view=='overview_A':
  scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.02;scene.cycles.adaptive_min_samples=32
 scene.render.threads_mode='FIXED';scene.render.threads=args.threads;scene.render.resolution_x=args.width;scene.render.resolution_y=round(args.width/view['aspect']);scene.render.resolution_percentage=100
 scene.render.film_transparent=False;scene.render.use_compositing=False;scene.render.use_sequencer=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0.0
 scene.render.filepath=str(args.output)
 bpy.context.view_layer.update()
 return {'collection':coll.name,'source_lights_muted_in_memory':before_lights,'lights':lights,
         'world':{'color_linear':list(WORLD_COLOR),'strength':WORLD_STRENGTH},
         'camera':{'object':camera.name,'view':args.view,'cab':args.cab,'world_location':numbers(camera.location),
                   'world_target':numbers(target),'world_matrix':matrix_rows(camera.matrix_world),'lens_mm':d.lens,'sensor_width_mm':d.sensor_width,
                   'clip_start_m':d.clip_start,'clip_end_m':d.clip_end},
         'render':{'engine':'Cycles CPU','maximum_samples':args.samples,'denoising':False,'threads':args.threads,
                   'adaptive_sampling':scene.cycles.use_adaptive_sampling,'adaptive_min_samples':scene.cycles.adaptive_min_samples,'adaptive_threshold':scene.cycles.adaptive_threshold,
                   'width':scene.render.resolution_x,'height':scene.render.resolution_y,'view_transform':scene.view_settings.view_transform,
                   'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'film_transparent':False,'compositing':False,'sequencer':False}}


def write_json(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp')
 tmp.write_text(json.dumps(data,indent=2,allow_nan=False));tmp.replace(path)


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--master',type=Path,required=True,help='Explicit already-integrated delivery .blend; never overwritten')
 parser.add_argument('--view',choices=tuple(VIEWS),required=True)
 parser.add_argument('--cab',type=int,choices=(1,2),default=1,help='Use the selected framing in this existing cab')
 parser.add_argument('--samples',type=int,default=96)
 parser.add_argument('--width',type=int,default=1600)
 parser.add_argument('--threads',type=int,default=2)
 parser.add_argument('--output',type=Path,required=True,help='Output PNG; provenance is written beside it')
 parser.add_argument('--provenance',type=Path,help='Optional explicit provenance JSON path')
 parser.add_argument('--expected-sha256',help='Refuse a master whose bytes differ from this exact SHA256')
 parser.add_argument('--stage-only',action='store_true',help='Open/check/stage and emit JSON only; do not render or save a .blend')
 argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 args=parser.parse_args(argv)
 if args.samples<1 or args.width<64 or not 1<=args.threads<=9:parser.error('samples must be positive, width>=64 and threads between1 and9')
 args.master=args.master.expanduser().resolve(strict=True);args.output=args.output.expanduser().resolve()
 if args.master.suffix.lower()!='.blend':parser.error('--master must be a .blend file')
 if args.output.suffix.lower()!='.png' or args.output==args.master:parser.error('--output must be a separate .png path')
 provenance=args.provenance.expanduser().resolve() if args.provenance else args.output.with_suffix('.provenance.json')
 if provenance in {args.master,args.output}:parser.error('Provenance must be a separate JSON path')
 start_sha=sha256_file(args.master)
 if args.expected_sha256 and args.expected_sha256.lower()!=start_sha:raise RuntimeError('Master SHA mismatch: '+start_sha)
 report={'status':'opening','master_path':str(args.master),'master_sha256':start_sha,'blender_version':bpy.app.version_string,
         'script_sha256':sha256_file(Path(__file__)),'output_png':str(args.output),'stage_only':args.stage_only,
         'pipeline':'Open exact integrated master; stage presentation only; no cab rebuild and no blend save'}
 try:
  bpy.ops.wm.open_mainfile(filepath=str(args.master),load_ui=False)
  bpy.context.view_layer.update();source_names={o.name for o in bpy.data.objects}
  report['source_readiness']=source_readiness(args.stage_only)
  report['source_geometry_before']=geometry_digest(source_names);report['vehicle_pose_before']=pose_snapshot()
  report['presentation']=add_presentation(args,start_sha)
  report['source_geometry_after_staging']=geometry_digest(source_names);report['vehicle_pose_after_staging']=pose_snapshot()
  if report['source_geometry_after_staging']!=report['source_geometry_before'] or report['vehicle_pose_after_staging']!=report['vehicle_pose_before']:
   raise RuntimeError('Presentation setup altered source geometry or vehicle pose')
  report['status']='staged';report['source_geometry_unchanged']=True;write_json(provenance,report)
  if not args.stage_only:
   args.output.parent.mkdir(parents=True,exist_ok=True);t0=time.monotonic();bpy.ops.render.render(write_still=True);report['render_seconds']=time.monotonic()-t0
   if not args.output.is_file():raise RuntimeError('Renderer did not produce the requested PNG')
   report['source_geometry_after_render']=geometry_digest(source_names);report['vehicle_pose_after_render']=pose_snapshot()
   if report['source_geometry_after_render']!=report['source_geometry_before'] or report['vehicle_pose_after_render']!=report['vehicle_pose_before']:
    raise RuntimeError('Source geometry or vehicle pose changed during render')
   report['png_sha256']=sha256_file(args.output);report['png_bytes']=args.output.stat().st_size;report['status']='rendered'
  report['master_sha256_after']=sha256_file(args.master);report['master_file_unchanged']=report['master_sha256_after']==start_sha
  if not report['master_file_unchanged']:raise RuntimeError('The input path changed during this run; the image is not proof of the newest master')
  write_json(provenance,report);print(json.dumps({'status':report['status'],'master_sha256':start_sha,'provenance':str(provenance),'source_geometry_unchanged':True,'master_file_unchanged':True}),flush=True)
 except Exception as error:
  report['status']='failed';report['error']=str(error);write_json(provenance,report);raise

if __name__=='__main__':main()
