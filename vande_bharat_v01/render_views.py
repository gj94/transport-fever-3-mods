import bpy,sys,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'nose'
source='VB_DTC.blend' if mode in ['nose','cab'] else 'VB_TC_EC.blend'
bpy.ops.wm.open_mainfile(filepath=str(P/'cars'/source));sc=bpy.context.scene
presentation=bpy.data.collections.new('PRESENTATION_NOT_EXPORTED');sc.collection.children.link(presentation)
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 presentation.objects.link(o)
def cube(n,c,d,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);move(o);m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);o.data.materials.append(m)
def light(n,loc,power,size):
 da=bpy.data.lights.new(n,'AREA');da.energy=power;da.shape='DISK';da.size=size;o=bpy.data.objects.new(n,da);presentation.objects.link(o);o.location=loc;o.rotation_euler=(Vector((3,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
if mode=='nose':
 cube('Ground',(0,0,-.35),(60,60,.5),(.08,.10,.13))
 for y in [-.838,.838]:cube('Rail',(0,y,-.08),(28,.075,.16),(.28,.30,.34))
 for j in range(-19,20):cube('Sleeper',(j*.65,0,-.18),(.22,2.65,.16),(.22,.23,.22))
 light('Key',(10,-9,14),2300,9);light('Fill',(3,8,10),1700,8);light('Rim',(-8,-1,9),1200,7)
 loc=(17,-23,11);target=(1.5,0,2);lens=46
elif mode=='cab':
 light('Cab_key',(6.4,0,3.1),75,2);light('Cab_fill',(8,0,3.4),50,1.5)
 loc=(6.43,-.73,2.48);target=(16,-.73,2.48);lens=20
else:
 for x in [-5,-2,2,5]:light('Saloon_light'+str(x),(x,0,3.45),70,2)
 loc=(-5.9,0,2.7);target=(4.5,0,2.32);lens=20
cam=bpy.data.cameras.new('Camera');o=bpy.data.objects.new('Camera',cam);presentation.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;sc.camera=o
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=1400;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'renders'/(mode+'.png'));sc.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'renders'/(mode+'_review.blend')),compress=True);bpy.ops.render.render(write_still=True)
