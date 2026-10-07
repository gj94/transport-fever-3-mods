"""Actual CPU Cycles renders and per-image source provenance.
Usage: blender -b -t 2 --python render_lhb_detail.py -- 3A exterior interior
Environment LHB_SAMPLES=64 LHB_RESOLUTION=1600. No source geometry edits saved.
"""
import bpy,sys,os,math,json,hashlib,time,random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['3A','exterior','interior']
k=args[0];views=args[1:] or ['exterior','interior'];source=P/'models'/('LHB_'+k+'.blend')
source_sha=hashlib.sha256(source.read_bytes()).hexdigest();script_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
print('LOADING',source,flush=True);bpy.ops.wm.open_mainfile(filepath=str(source));print('LOADED',flush=True);sc=bpy.context.scene;studio=bpy.data.collections['PRESENTATION_ONLY'];root=bpy.data.objects['LHB_'+k+'_ROOT_metres'];objs=[root]+list(root.children_recursive)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=int(os.environ.get('LHB_SAMPLES','48'));sc.cycles.use_denoising=False;sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.02;sc.cycles.adaptive_min_samples=32;sc.cycles.sample_clamp_indirect=3;sc.cycles.max_bounces=12;sc.cycles.diffuse_bounces=4;sc.cycles.glossy_bounces=4;sc.cycles.transmission_bounces=12;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=int(os.environ.get('LHB_RESOLUTION','1400'));sc.render.resolution_y=int(sc.render.resolution_x*.60);sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.76,.89,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.48
hdri=P.parent/'wap7_photoreal_v02/environment/kloofendal_48d_partly_cloudy_puresky_2k.hdr'
if hdri.exists():
 tex=sc.world.node_tree.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(hdri));sc.world.node_tree.links.new(tex.outputs['Color'],sc.world.node_tree.nodes['Background'].inputs[0])

def mat(name,color,rough=0.8,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
ballast=mat('Presentation_ballast',(.13,.12,.10));m=ballast.node_tree;n=m.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=180;b=m.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.5;b.inputs['Distance'].default_value=.027;m.links.new(n.outputs['Fac'],b.inputs['Height']);m.links.new(b.outputs['Normal'],m.nodes['Principled BSDF'].inputs['Normal'])
rail=mat('Presentation_rail_head',(.28,.31,.33),.23,.8);rust=mat('Presentation_rail_web',(.13,.08,.045),.88,.18);sleeper=mat('Presentation_concrete',(.25,.25,.23));groundmat=mat('Presentation_surround',(.16,.18,.16))
def box(name,loc,dim,material,bevel=0):
 x,y,z=[q/2 for q in dim]
 vertices=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
 faces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
 o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=loc;data.materials.append(material)
 if bevel:md=o.modifiers.new('Edge radius','BEVEL');md.width=bevel;md.segments=2
 return o
ground_object=box('PRESENTATION_ground',(0,0,-.47),(260,260,.2),groundmat);box('PRESENTATION_ballast',(0,0,-.30),(40,3.65,.18),ballast,.06)
for y in [-.869,.869]:
 box('PRESENTATION_rail_head',(0,y,-.018),(39,.065,.036),rail,.009)
 box('PRESENTATION_rail_web',(0,y,-.083),(39,.017,.095),rust,.003)
 box('PRESENTATION_rail_foot',(0,y,-.144),(39,.14,.023),rust,.003)
for i in range(62):
 x=(i-30.5)*.62;box('PRESENTATION_sleeper',(x,0,-.22),(.25,2.66,.13),sleeper,.025)
 for y in [-.869,.869]:
  box('PRESENTATION_rail_chair',(x,y,-.161),(.30,.22,.018),rust,.003)
  for s in [-1,1]:box('PRESENTATION_clip',(x,y+s*.080,-.135),(.055,.05,.025),rust,.01)
from lhb_presentation import refine_ground
environment_report=refine_ground(studio,ground_object,P)
if 'hero' in views:
 sys.path.insert(0,str(P.parent/'vande_bharat_detail_v02/components'))
 import environment_depot
 def depot_mat(name,color,rough=.7,metal=0,*unused):return mat(name,color,rough,metal)
 environment_report['depot']=environment_depot.apply(studio,depot_mat)
# Exterior key uses broad sunlight in addition to the existing soft reflectors.
d=bpy.data.lights.new('PRESENTATION_sun','SUN');d.energy=2;d.angle=.20;o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.rotation_euler=(.45,-.50,-.55)
d=bpy.data.lights.new('CAMERA_inspection_fill','AREA');d.energy=0;d.shape='DISK';d.size=1.7;fill=bpy.data.objects.new(d.name,d);studio.objects.link(fill)
for apparatus in studio.objects:
 if apparatus.type=='LIGHT':apparatus.visible_glossy=False
def camera(loc,target,lens=48,ortho=None):
 o=sc.camera;o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO' if ortho else 'PERSP';o.data.ortho_scale=ortho or 26;o.data.lens=lens;o.data.clip_start=.015;o.data.clip_end=300;fill.location=loc;fill.rotation_euler=o.rotation_euler
for view in views:
 for o in objs:o.hide_render=False
 fill.data.energy=0
 for l in studio.objects:
  if l.type=='LIGHT' and l.name.startswith('Interior_fill'):l.data.energy=25
 hidden=[]
 if view=='exterior':camera((20,-30,8.5),(0,0,2.05),ortho=26.1)
 elif view=='hero':camera((24,-38,5.2),(0,0,2.05),lens=60)
 elif view=='side':camera((0,-34,2.0),(0,0,2.0),ortho=25.7)
 elif view=='window':camera((2.65,-4.55,2.75),(1.85,-1.58,2.50),lens=58)
 elif view=='door':camera((14,-7,3.30),(10.20,-1.1,2.0),lens=45)
 elif view=='hvac':camera((12,-4.8,6.7),(9.8,0,3.78),lens=54)
 elif view=='end':camera((16,-6,3.4),(9.5,0,2.0),lens=52)
 elif view=='roof':camera((9,-12,13),(6,0,3.1),ortho=13)
 elif view=='bogie':
  camera((10.7,-5.5,1.7),(7.45,0,.65),lens=46);fill.data.energy=30
 elif view=='coupler':camera((14,-2.7,1.7),(11.65,0,1.31),lens=58)
 elif view=='layout':
  for o in objs:
   hide=any(c.name=='ROOF_REMOVABLE' for c in o.users_collection)
   if o.type in {'MESH','FONT'} and sum((o.matrix_world@Vector(corner)).y for corner in o.bound_box)/8<-1.47 and o.name.startswith(('BODYSIDE','WINDOW','GLASS','CURTAIN','INTERIOR_','CLASS','RAILWAY','COACH','ENTRY','DOOR')):hide=True
   if o.name.startswith(('MAIN_UPPER','SIDE_UPPER','FIRST_UPPER','FIRST_upper_guard','BERTH_upper_guard','UPPER_folded_cotton_sheet','LINEN_hem','UPPER_berth_support_stay')):hide=True
   if o.name.startswith('UPHOLSTERY_edge_piping') and o.type=='MESH' and max((o.matrix_world@Vector(corner)).z for corner in o.bound_box)>2.80:hide=True
   if hide:o.hide_render=True;hidden.append(o.name)
  camera((7,-22,28),(0,0,1.95),ortho=26.4)
 elif view=='interior':
  if k=='1A':camera((-7.18,.25,2.55),(-7.23,-1.42,2.49),lens=17)
  elif k in ['2A','3A','SL','GS']:camera((-7.94,.70,2.64),(5,.70,2.56),lens=22)
  else:camera((-8.75,-.23 if k=='CC' else 0,2.63),(5,-.23 if k=='CC' else 0,2.47),lens=22)
  fill.data.energy=14 if k=='1A' else 24
  for l in studio.objects:
   if l.type=='LIGHT' and l.name.startswith('Interior_fill'):l.data.energy=36 if k=='1A' else 54
 elif view=='chair_detail':
  camera((-8.72,-.05,2.35),(-7.95,-.78,2.12),lens=25);fill.data.energy=20
  for l in studio.objects:
   if l.type=='LIGHT' and l.name.startswith('Interior_fill'):l.data.energy=45
 elif view=='cabin_entry':
  camera((-7.15,-1.30,2.59),(-7.21,.52,2.43),lens=19);fill.data.energy=22
  for l in studio.objects:
   if l.type=='LIGHT' and l.name.startswith('Interior_fill'):l.data.energy=36
 elif view=='bay':
  camera((-.15,1.45,2.57),(-.1,-1.2,2.50),lens=19)
  fill.data.energy=28
 elif view=='vestibule':
  camera((9.10,.37,2.55),(11.15,.4,2.28),lens=18);fill.data.energy=95
 elif view=='toilet':
  for o in objs:
   if o.name.startswith('WC_door') and o.matrix_world.translation.x>10:o.hide_render=True;hidden.append(o.name)
  camera((10.0,.73,2.76),(11.25,1.08,1.97),lens=18);fill.data.energy=80
 else:raise ValueError(view)
 sc.render.filepath=str(P/'previews'/f'LHB_{k}_{view}.png');start=time.time();bpy.ops.render.render(write_still=True)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha,'Source changed during rendering'
 output=Path(sc.render.filepath);report={'variant':k,'view':view,'source':str(source.relative_to(P)),'source_sha256':source_sha,'render_script_sha256':script_sha,'image':str(output.relative_to(P)),'image_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'renderer':'Blender CPU Cycles','samples':sc.cycles.samples,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'seconds':time.time()-start,'camera_xyz':list(sc.camera.location),'camera_lens_mm':sc.camera.data.lens,'camera_type':sc.camera.data.type,'hidden_for_review':hidden,'presentation_environment':environment_report,'environment_dependency':'../wap7_photoreal_v02/environment (Poly Haven CC0; existing repository assets)','actual_geometry_render':True,'image_generation_used':False}
 (P/'qa'/f'render_{k}_{view}.json').write_text(json.dumps(report,indent=2));print('RENDERED',k,view,round(time.time()-start,2),flush=True)
