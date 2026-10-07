"""Actual Blender scene previews. Usage: blender -b MASTER -t 2 --python render_detail.py -- exterior cutaway aisle bogie entrance."""
from pathlib import Path
import bpy,sys,os
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import preview_track
scene=bpy.context.scene;cam=scene.camera
preview_track.build(scene)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['exterior']
variant=Path(bpy.data.filepath).parent.name
out=Path(bpy.data.filepath).parent/'renders';out.mkdir(exist_ok=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=int(os.environ.get('ICF_RENDER_SAMPLES','24'));scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=int(os.environ.get('ICF_RENDER_WIDTH','1000'));scene.render.resolution_y=int(os.environ.get('ICF_RENDER_HEIGHT','650'));scene.render.resolution_percentage=100
views={'exterior':((22,-24,12),(0,0,1.8),'ORTHO',26.7),'cutaway':((16,-20,21),(0,0,1.9),'ORTHO',25.6),'aisle':((-7.2,1.06 if variant=='1A' else (.60 if variant in ['SL','2A','3A'] else 0),2.5),(4,1.06 if variant=='1A' else (.60 if variant in ['SL','2A','3A'] else 0),2.49),'PERSP',21),'bogie':((-10.5,-5,2.6),(-7.3915,0,.8),'PERSP',48),'entrance':((13,-7,4.8),(9.25,-.3,2.15),'PERSP',48),'cabin':((-6,.44,2.65),(-6,-1.20,2.40),'PERSP',21),'window':((0,-4.5,2.50),(0,-1.60,2.40),'PERSP',38),'bay':((.95 if variant in ['2A','3A'] else .05,1.20,2.73),(.95 if variant in ['2A','3A'] else 0,-.85,2.35),'PERSP',21),'toilet':((9.75,-.20,3.50),(10.12,1.01,1.95),'PERSP',28),'side':((0,-28,2.3),(0,0,2.3),'ORTHO',23.7)}
for key in args:
 hidden=[];lights=[]
 if key=='cutaway':
  for n in ['ROOF_ASSEMBLY','SHELL_SIDE_L']:
   p=bpy.data.objects.get(n)
   if p:
    for o in p.children_recursive:
     if o.type=='MESH' and not o.hide_render:hidden.append(o);o.hide_render=True
 if key=='toilet':
  for ob in bpy.data.objects:
   if ob.name.startswith(('Lavatory door leaf','Lavatory door head')) and not ob.hide_render:hidden.append(ob);ob.hide_render=True
 if key in ['aisle','bay','toilet','cabin']:
  for x in [-7,-5,-3,-1,1,3,5,7]:
   ld=bpy.data.lights.new('STUDIO preview aisle fill','AREA');ld.energy=45;ld.shape='RECTANGLE';ld.size=.65;ld.size_y=1.8
   ob=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(ob);ob.location=(x,.6,3.34);lights.append(ob)
  scene.cycles.samples=int(os.environ.get('ICF_INTERIOR_SAMPLES','64'))
 loc,target,kind,scale=views[key];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=kind
 if kind=='ORTHO':cam.data.ortho_scale=scale
 else:cam.data.lens=scale
 scene.render.filepath=str(out/(key+'_'+os.environ.get('ICF_RENDER_SUFFIX','proof')+'.png'));bpy.ops.render.render(write_still=True)
 for ob in hidden:ob.hide_render=False
 for ob in lights:bpy.data.objects.remove(ob,do_unlink=True)
 print('RENDER_COMPLETE',variant,key,flush=True)
