import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'paired_straight_QA.blend'));s=bpy.context.scene;c=s.camera;c.location=(32,-40,25);c.rotation_euler=(Vector((11.1,0,1.9))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=47;s.render.resolution_x=1100;s.render.resolution_y=580;s.render.filepath=str(P/'paired_straight_overview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'paired_straight_QA.blend'),compress=True)
