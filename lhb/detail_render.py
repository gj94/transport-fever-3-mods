import bpy,os
from mathutils import Vector
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=P+'/LHB_3A_prototype.blend')
s=bpy.context.scene;c=s.camera;c.location=(11,-8,3.2);c.rotation_euler=(Vector((8.2,0,1.55))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=7.9
s.render.resolution_x=1100;s.render.resolution_y=700;s.cycles.samples=32;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=P+'/LHB_3A_detail.png';bpy.ops.render.render(write_still=True)
