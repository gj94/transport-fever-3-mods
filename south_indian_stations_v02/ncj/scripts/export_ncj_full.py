import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','FONT','CURVE'} and not o.name.startswith('Review'))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/NCJ_full_station_v02.glb'),export_format='GLB',use_selection=True,export_apply=True)

import zipfile
with zipfile.ZipFile(R/'exports/NCJ_full_station_v02_GLTF.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:z.write(R/'exports/NCJ_full_station_v02.glb','NCJ_full_station_v02.glb')
