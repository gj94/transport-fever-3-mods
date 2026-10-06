"""Neutral inspection stage initial iteration; presentation excluded from vehicle export."""
import bpy, math
from mathutils import Vector
import common as C

def apply(context=None):
 col=C.collection('V02_PRESENTATION_ONLY')
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
 sc=bpy.context.scene
 ground=bpy.data.materials.get('V02_STAGE neutral ballast ground') or bpy.data.materials.new('V02_STAGE neutral ballast ground');ground.use_nodes=True;p=ground.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.15,.165,.17,1);p.inputs['Roughness'].default_value=.88
 C.box('V02_STAGE ground',(0,0,-.20),(200,200,.3),ground,None,col,b=0)
 # Simple rails for contact datum during inspection. Real scenic stage is added after geometry review.
 for y in [-.873,.873]:C.box('V02_STAGE inspection rail',(0,y,-.066),(100,.070,.128),context['materials']['steel'],None,col,b=.004)
 w=bpy.data.worlds.new('V02_STAGE neutral world');sc.world=w;w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[0].default_value=(.42,.48,.53,1);w.node_tree.nodes.get('Background').inputs[1].default_value=.55
 def area(n,loc,target,energy,size):
  d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 area('V02_STAGE neutral key',(9,-9,10),(3,0,2),1800,7)
 area('V02_STAGE broad sky fill',(-7,6,9),(-2,0,2),1600,10)
 area('V02_STAGE frontal fill',(14,-6,7),(8,0,2),700,5)
 def camera(n,loc,target,lens=55):
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.02;d.clip_end=300;d.dof.use_dof=False;return o
 camera('V02_CAM_HERO',(29,-15,3.5),(1.0,0,2.2),72)
 camera('V02_CAM_FRONT',(19,-.8,2.8),(9.0,0,2.25),85)
 camera('V02_CAM_CAB',(15,-8,3.5),(8.4,-.25,2.6),67)
 camera('V02_CAM_COUPLER',(13.0,-2.6,1.5),(9.9,-.08,1.10),66)
 camera('V02_CAM_COUPLER_TOP',(12.7,-2.2,2.9),(10.02,0,1.12),73)
 camera('V02_CAM_WINDOW',(12.5,-3.4,3.6),(9.28,-.45,3.0),76)
 camera('V02_CAM_BOGIE',(7.7,-8.5,1.25),(6,-.20,.90),65)
 camera('V02_CAM_ROOF',(-.5,-8.5,7.4),(-4.6,0,4.45),67)
 camera('V02_CAM_PANTOGRAPH',(-1.7,-5.5,5.8),(-4.8,0,4.7),64)
 camera('V02_CAM_SIDE',(0,-31,2.3),(0,0,2.3),55)
 sc.camera=bpy.data.objects['V02_CAM_CAB']
 return {'mode':'neutral inspection','collection':col.name}
