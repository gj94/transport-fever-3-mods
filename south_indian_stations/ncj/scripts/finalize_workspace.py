import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_2010_station.blend'))
bpy.ops.object.select_all(action='DESELECT')
bpy.context.scene.camera=bpy.data.objects['01_HERO_FORECOURT']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_2010_station.blend'))
