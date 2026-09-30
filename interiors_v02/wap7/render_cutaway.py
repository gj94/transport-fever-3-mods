import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'WAP7_interiors_v02.blend'))
s=bpy.context.scene;s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
asset=bpy.data.collections['WAP7_ASSET'];inter=bpy.data.collections['CAB_INTERIORS_V02']
hidden=[]
for o in list(asset.objects)+list(inter.objects):
 if o in asset.objects.values() or (o.parent and o.parent.name.startswith('CAB_A') and any(t in o.name for t in ['ceiling','center roof','bulkhead','gangway','side interior','door','blind','lamp','fluorescent','overhead'])):
  if not o.hide_render:hidden.append(o);o.hide_render=True
cam=bpy.data.objects['CAB_A_CAB_REVIEW'];oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldtype=cam.data.type
cam.location=(6.9,-3.1,4.65);cam.rotation_euler=(Vector((8.35,0,2.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.5;
for o in bpy.data.collections['PRESENTATION_ONLY'].objects:
 if o.type=='MESH' and o.name!='Studio floor':o.hide_render=True
s.camera=cam;s.cycles.samples=32;s.render.filepath=str(P/'WAP7_cab_cutaway.png');bpy.ops.render.render(write_still=True)
