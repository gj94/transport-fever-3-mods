"""Actual Blender scene previews. Usage: blender -b MASTER -t 2 --python render_detail.py -- exterior cutaway aisle bogie entrance."""
from pathlib import Path
import bpy,sys,os,json,hashlib,datetime,time
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import preview_track
renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
presentation_source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('preview_track.py'),Path(__file__).with_name('icf_presentation.py')]}
scene=bpy.context.scene;cam=scene.camera
preview_track.build(scene,length=120 if 'hero' in sys.argv else 32)
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.33,.35,.37,1)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['exterior']
environment_report=None
if 'hero' in args:
 import icf_presentation
 environment_report=icf_presentation.build_outdoor(scene,Path(__file__).resolve().parents[1])
variant=Path(bpy.data.filepath).parent.name
source_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
asset_root=bpy.data.objects.get('ICF_'+variant+'_ROOT');build_pass=asset_root.get('build_pass','early WIP') if asset_root else 'unknown'
out=Path(bpy.data.filepath).parent/'renders';out.mkdir(exist_ok=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=int(os.environ.get('ICF_RENDER_SAMPLES','24'));scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=int(os.environ.get('ICF_RENDER_THREADS','4'))
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=float(os.environ.get('ICF_ADAPTIVE_THRESHOLD','0.02'))
scene.cycles.adaptive_min_samples=int(os.environ.get('ICF_ADAPTIVE_MIN_SAMPLES','64'))
scene.render.resolution_x=int(os.environ.get('ICF_RENDER_WIDTH','1000'));scene.render.resolution_y=int(os.environ.get('ICF_RENDER_HEIGHT','650'));scene.render.resolution_percentage=100
views={'exterior':((22,-24,12),(0,0,1.8),'ORTHO',26.7),'cutaway':((16,-20,21),(0,0,1.9),'ORTHO',25.6),'aisle':((-7.2,1.06 if variant=='1A' else (.60 if variant in ['SL','2A','3A'] else 0),2.5),(4,1.06 if variant=='1A' else (.60 if variant in ['SL','2A','3A'] else 0),2.49),'PERSP',21),'bogie':((-7.8,-5.2,1.38),(-7.3915,0,.82),'PERSP',38),'coupling':((13.3,-2.8,1.65),(10.8,0,1.0),'PERSP',55),'entrance':((13,-7,4.8),(9.25,-.3,2.15),'PERSP',48),'cabin_diagonal':((-5.18,.35,2.73),(-6.35,-.82,2.58),'PERSP',24),'cabin_cutaway':((-6,1.47,2.68),(-6,-.46,2.60),'PERSP',17),'markings':((-2.7,-4.4,3.12),(-2.7,-1.62,3.1),'PERSP',45),'cabin':((-6,.44,2.65),(-6,-1.20,2.40),'PERSP',21),'window':((0,-4.5,2.50),(0,-1.60,2.40),'PERSP',38),'bay':((.95 if variant in ['2A','3A'] else .05,1.20,2.73),(.95 if variant in ['2A','3A'] else 0,-.85,2.35),'PERSP',21),'toilet':((9.75,-.20,3.50),(10.12,1.01,1.95),'PERSP',28),'side':((0,-28,2.3),(0,0,2.3),'ORTHO',23.7)}
views['hero']=((24,-28,5.4),(0,0,1.9),'PERSP',68)
views['side_berth']=((.95 if variant in ['2A','3A'] else .05,-.1,2.33),(.95 if variant in ['2A','3A'] else .05,1.45,2.32),'PERSP',18)
views['headrest']=((6.95,-.45,2.62),(5.35,-.45,2.25),'PERSP',40)
if variant=='CC':views['aisle']=((7.65,.06,2.66),(-3,.06,2.42),'PERSP',23)
for key in args:
 started=time.monotonic();hidden=[];lights=[]
 if key=='cutaway':
  for n in ['ROOF_ASSEMBLY','SHELL_SIDE_L']:
   p=bpy.data.objects.get(n)
   if p:
    for o in p.children_recursive:
     if o.type=='MESH' and not o.hide_render:hidden.append(o);o.hide_render=True
 if key=='cabin_cutaway':
  for n in ['First AC compartment call plate','Compartment call pushbutton']:
   ob=bpy.data.objects.get(n)
   if ob and not ob.hide_render:hidden.append(ob);ob.hide_render=True
  for ob in bpy.data.objects:
   if ob.name.startswith(('Cabin_A_corridor_wall','Cabin_A_sliding_door_parked','Cabin_A_door_header','Cabin_A_door_pull','Cabin_A_nameplate','Cabin_A_door_lock_plate','Cabin_A_door_privacy_latch')) and not ob.hide_render:hidden.append(ob);ob.hide_render=True
 if key in ['bogie','coupling']:
  ld=bpy.data.lights.new('STUDIO close inspection softbox','AREA');ld.energy=250;ld.size=3.5
  ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=(-7.4,-3.8,2.4) if key=='bogie' else (12.5,-3.0,2.5);target=Vector((-7.4,0,.8) if key=='bogie' else (10.8,0,1.0));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();lights.append(ob)
 if key=='toilet':
  for ob in bpy.data.objects:
   if ob.name.startswith(('Lavatory door leaf','Lavatory door head')) and not ob.hide_render:hidden.append(ob);ob.hide_render=True
 if key in ['aisle','bay','toilet','cabin','cabin_cutaway','cabin_diagonal','side_berth','headrest']:
  for x in [-7,-5,-3,-1,1,3,5,7]:
   ld=bpy.data.lights.new('STUDIO preview aisle fill','AREA');ld.energy=45;ld.shape='RECTANGLE';ld.size=.65;ld.size_y=1.8
   ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=(x,.6,3.34);lights.append(ob)
  if variant=='1A':
   for x in [-6,-3,-.5,1.5,3.5,6]:
    ld=bpy.data.lights.new('STUDIO cabin ceiling soft fill','AREA');ld.energy=30;ld.size=.80;ld.color=(1,.97,.92)
    ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=(x,-.43,3.57);lights.append(ob)
  elif key=='bay':
   ld=bpy.data.lights.new('STUDIO bay ceiling soft fill','AREA');ld.energy=35;ld.size=1.0
   ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=(.95 if variant in ['2A','3A'] else 0,-.45,3.56);lights.append(ob)
  scene.cycles.samples=int(os.environ.get('ICF_INTERIOR_SAMPLES','64'))
 loc,target,kind,scale=views[key];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=kind
 if kind=='ORTHO':cam.data.ortho_scale=scale
 else:cam.data.lens=scale
 scene.render.filepath=str(out/(key+'_'+os.environ.get('ICF_RENDER_SUFFIX','proof')+'.png'));bpy.ops.render.render(write_still=True)
 assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==source_sha256,'Source changed during rendering'
 metadata={'variant':variant,'view':key,'presentation_environment':environment_report,'source_build_pass':build_pass,'source_blend_sha256':source_sha256,'renderer_script_sha256':renderer_sha256,'presentation_source_sha256':presentation_source_sha256,'samples':scene.cycles.samples,'adaptive_sampling':scene.cycles.use_adaptive_sampling,'adaptive_threshold':scene.cycles.adaptive_threshold,'adaptive_min_samples':scene.cycles.adaptive_min_samples,'render_threads':scene.render.threads,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'engine':'Blender Cycles CPU, no denoising','camera_position_m':list(cam.location),'camera_lens_mm':cam.data.lens if cam.data.type=='PERSP' else None,'orthographic_scale_m':cam.data.ortho_scale if cam.data.type=='ORTHO' else None,'hidden_mesh_count':len(hidden),'cutaway':key in ['cutaway','cabin_cutaway','toilet'],'cutaway_scope':'Roof and near bodyside' if key=='cutaway' else ('First-AC cabin A corridor partition, parked leaf and attached call controls only' if key=='cabin_cutaway' else ('Lavatory door leaves and headers only' if key=='toilet' else None)),'preview_track_gauge_m':1.676,'duration_seconds':round(time.monotonic()-started,2),'rendered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'image_sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()}
 Path(scene.render.filepath).with_suffix('.json').write_text(json.dumps(metadata,indent=2))
 for ob in hidden:ob.hide_render=False
 for ob in lights:bpy.data.objects.remove(ob,do_unlink=True)
 print('RENDER_COMPLETE',variant,key,flush=True)
