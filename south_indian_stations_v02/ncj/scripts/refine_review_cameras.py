"""Final review viewpoints; geometry unchanged. Show kiosk working face and actual excavated pit."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'))
for name,loc,target,lens in [
 ('05_PLATFORM_DETAIL',(64,12.4,2.9),(-90,15.4,2.8),37),
 ('04_TOILETS',(-68,5.7,2.3),(-72,10.5,1.6),23),
 ('08_DEPOT_PITS',(-132,112,4.6),(-220,103.7,-.05),42)]:
 o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True)
