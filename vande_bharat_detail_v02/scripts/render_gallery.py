"""Render supplied source geometry only; presentation is transient, never saved over master."""
import os,bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
SCRIPT_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'));from common import box,mesh,collection,cyl
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];view=args[0] if args else 'hero';samples=int(args[1]) if len(args)>1 else 64;width=int(args[2]) if len(args)>2 else 1200
kind='TC_EC' if view in ['ec','ec_front','roof','pantograph','panhead','vcb'] else 'MC' if view in ['cc','bogie','underframe','vestibule','toilet','pantry'] else 'DTC';source=OUT/'cars'/f'VB_{kind}.blend';bpy.ops.wm.open_mainfile(filepath=str(source));sha=hashlib.sha256(source.read_bytes()).hexdigest();sc=bpy.context.scene;C=collection('PRESENTATION_NOT_EXPORTED')
def mat(n,c,metal=0,rough=.6):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
rail=mat('Stage rail steel',(.25,.29,.32),.86,.28);sleep=mat('Stage concrete',(.26,.28,.27));ground=mat('Stage neutral ground',(.19,.23,.26));dark=mat('Stage rail fastening',(.055,.058,.061),.5)
# Sky HDRI is a credited dependency already supplied by prior repository source.
world=bpy.data.worlds.new('Review world');sc.world=world;world.use_nodes=True;nodes=world.node_tree.nodes;bg=nodes.get('Background');bg.inputs[1].default_value=.48
hdri=OUT.parent/'wap7_photoreal_v02/environment/kloofendal_48d_partly_cloudy_puresky_2k.hdr'
if hdri.exists():
 tex=nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(hdri));world.node_tree.links.new(tex.outputs['Color'],bg.inputs['Color'])
else:bg.inputs[0].default_value=(.65,.73,.85,1)
def light(n,pos,target,energy,size,color=(1,1,1)):
 d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);C.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
interior=view in ['cc','ec','ec_front','cab','cab_controls','cab_seats','vestibule','toilet','pantry']
if not interior:
 box('Inspection ground',(0,0,-.29),(70,70,.30),ground,coll=C,b=.02)
 for y in [-.838,.838]:
  box('Rail foot',(0,y,-.139),(35,.15,.025),rail,coll=C,b=.004);box('Rail web',(0,y,-.076),(35,.024,.102),rail,coll=C,b=.002);box('Rail crown',(0,y,-.012),(35,.072,.024),rail,coll=C,b=.008)
 for i in range(-28,29):
  x=i*.62;box('Concrete sleeper',(x,0,-.205),(.23,2.64,.115),sleep,coll=C,b=.026)
  for y in [-.838,.838]:
   box('Rail pad',(x,y,-.151),(.22,.19,.025),dark,coll=C,b=.004)
 light('Large front key',(12,-10,13),(2,0,1.8),2200,10);light('Soft side fill',(-2,8,10),(0,0,1.8),1300,9);light('Bogie fill',(4,-5,2),(3,0,.65),90,5)
else:
 bg.inputs[1].default_value=.30
 for x in [-6,-3,0,3,6]:light('Saloon bounce '+str(x),(x,0,3.42),(x,0,1.3),42,2.0)
 if view.startswith('cab'):
  light('Cab roof bounce',(9.0,0,3.35),(10.2,0,1.9),90,1.9);light('Cab windscreen daylight',(10.5,0,3.05),(9.3,0,1.6),60,1.6)
poses={'hero':((17,-23,8.0),(1.5,0,1.90),48),'front':((21,-.8,4.7),(7.9,0,2.2),60),'nose':((17,-10,5.1),(9.52,0,2.1),55),'side':((0,-29,6),(0,0,2),50),'bogie':((10.2,-5.7,1.9),(7.45,0,.7),57),'underframe':((1,-7,1.5),(0,0,.72),49),'roof':((8,-6,8.0),(7.0,0,4.1),48),'pantograph':((12.5,-7.3,6.5),(9.0,0,4.8),42),'panhead':((11,-3.2,6.75),(9.2,0,5.68),48),'vcb':((9.2,-3.8,5.2),(7.55,-1.05,4.02),56),'cc':((-7.9,.18,2.73),(6.8,.18,2.41),20),'ec':((-7.7,0,2.75),(6.8,0,2.44),20),'cab':((5.90,-.92,2.80),(7.6,.12,2.00),23),'cab_controls':((6.44,-.12,2.67),(7.40,0,2.13),26),'cab_seats':((7.43,-.96,2.89),(6.25,.05,1.98),21),'ec_front':((-.20,0,2.76),(-5.1,0,2.42),22),'vestibule':((-8.16,-.12,2.58),(-8.84,1.01,2.1),23),'toilet':((-9.265,.14,2.60),(-9.45,1.16,1.98),18),'pantry':((10.6,0,2.64),(8.8,1.0,2.30),24)}
report=json.loads((OUT/'qa'/f'VB_{kind}.json').read_text())
if view in ['cab','cab_controls','cab_seats']:
 info=report['components']['cab']['cameras'][{'cab':'overview','cab_controls':'instruments','cab_seats':'seat_detail'}[view]]
 poses[view]=(info['location'],info['target'],info['lens_mm'])
loc,target,lens=poses[view]
cutaway=[]
if view=='toilet':
 for ob in bpy.data.objects:
  if ob.type=='MESH' and any(v in ob.name for v in ['VB02_INT_service_removable_closed_door','VB02_INT_service_cabin_roof','VB02_INT_service_door_','VB02_INT_service_WC_']):ob.hide_render=True;cutaway.append(ob.name)
 light('Washroom soft fill',(-8.85,.45,2.85),(-8.88,1.1,1.8),20,.65)
if view=='pantry':light('Galley soft fill',(8.15,.2,3.0),(8.85,1.0,2.1),24,.8)
if view in ['pantograph','panhead','vcb']:
 o=bpy.data.objects.get('PANTO_CTRL');o['extension']=1;o.update_tag();bpy.context.view_layer.update()
d=bpy.data.cameras.new('Review '+view);o=bpy.data.objects.new('Review '+view,d);C.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
if view=='side':d.type='ORTHO';d.ortho_scale=26.8
d.clip_start=.04;d.clip_end=800;sc.camera=o
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=samples;sc.cycles.use_denoising=False;sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.025 if samples<100 else .01;sc.cycles.max_bounces=10;sc.cycles.transmission_bounces=8;sc.cycles.transparent_max_bounces=8;sc.cycles.sample_clamp_indirect=3
sc.render.threads_mode='FIXED';sc.render.threads=int(os.environ.get("VB_RENDER_THREADS","6"));sc.render.resolution_x=width;sc.render.resolution_y=round(width*(.27 if view=='side' else .625));sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.filepath=str(OUT/'previews'/f'{view}.png');sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.35 if interior else .2
bpy.ops.render.render(write_still=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(OUT/'qa'/f'render_{view}.json').write_text(json.dumps({'view':view,'source':str(source.relative_to(OUT)),'source_sha256':sha,'render_script_sha256':SCRIPT_SHA,'samples':samples,'resolution':[sc.render.resolution_x,sc.render.resolution_y],'camera':{'position':loc,'target':target,'lens':lens},'image_sha256':hashlib.sha256((OUT/'previews'/f'{view}.png').read_bytes()).hexdigest(),'presentation_saved_into_source':False,'transient_cutaway_hidden_objects':cutaway,'geometry_source':'Actual Blender source geometry; no composited vehicle artwork'},indent=2))
