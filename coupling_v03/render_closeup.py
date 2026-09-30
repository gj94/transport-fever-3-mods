import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'paired_straight_QA.blend'));s=bpy.context.scene;c=s.camera;c.location=(10.20,-3.3,2.75);c.rotation_euler=(Vector((10.20,0,1.105))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=58;s.render.resolution_x=1100;s.render.resolution_y=740;s.render.filepath=str(P/'paired_connection_closeup.png');bpy.ops.render.render(write_still=True)
