"""Representative mechanism views, without changing source model files."""
import bpy,sys
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/LHB_3A.blend'))
sc=bpy.context.scene;sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.cycles.max_bounces=5;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1280;sc.render.resolution_y=720
cam=sc.camera
cam.location=(8.7,-5.6,1.8);cam.rotation_euler=(Vector((7.45,0,.74))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.8
if '--coupling-only' not in sys.argv:
 sc.render.filepath=str(P/'renders/LHB_FIAT_bogie_detail.png');bpy.ops.render.render(write_still=True)
instance=bpy.data.objects.new('SECOND_COACH_PRESENTATION_INSTANCE',None);bpy.data.collections['PRESENTATION_ONLY'].objects.link(instance);instance.instance_type='COLLECTION';instance.instance_collection=bpy.data.collections['LHB_3A_ASSET'];instance.location=(24,0,0)
# Explicit isolated mechanism review: hide body and vestibule that conceal the contact outline.
for obj in bpy.data.objects['LHB_3A_ROOT_metres'].children_recursive:
 if obj.type in {'MESH','FONT'} and not obj.name.startswith('CBC_'):obj.hide_render=True
cam.location=(12.1,-2.3,2.8);cam.rotation_euler=(Vector((12,0,1.105))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.25
d=bpy.data.lights.new('COUPLING_INSPECTION_FILL','AREA');d.energy=20;d.size=1.0;lamp=bpy.data.objects.new(d.name,d);bpy.data.collections['PRESENTATION_ONLY'].objects.link(lamp);lamp.location=(12,-2.4,1.3);lamp.rotation_euler=(Vector((12,0,1.105))-lamp.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(P/'renders/LHB_CBC_paired_detail.png');bpy.ops.render.render(write_still=True)
