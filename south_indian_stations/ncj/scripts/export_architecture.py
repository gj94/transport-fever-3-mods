import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_2010_station.blend'))
bpy.ops.object.select_all(action='DESELECT')
for name in ['01_MAIN_2010_PHOTO','02_LEFT_VERANDA_2010_PHOTO','03_ANNEX_PHOTO_INFERRED','04_SIGNAGE']:
 for o in bpy.data.collections[name].objects:
  if o.type in {'MESH','FONT','CURVE'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/NCJ_2010_architecture.glb'),export_format='GLB',use_selection=True,export_apply=True)
