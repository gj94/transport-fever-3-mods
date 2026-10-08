import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
# Connect dropper tops to the actual sampled messenger curve in the final packed scene.
import math
G={}
for ob in bpy.context.scene.objects:
 if ob.name.startswith('Sagged messenger'):
  pts=[ob.matrix_world@p.co.xyz for p in ob.data.splines[0].points]
  for a,b in zip(pts,pts[1:]):
   for gx in range(math.floor(min(a.x,b.x)/5),math.floor(max(a.x,b.x)/5)+1):
    for gy in range(math.floor(min(a.y,b.y)/5),math.floor(max(a.y,b.y)/5)+1):G.setdefault((gx,gy),[]).append((a,b))
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('Catenary dropper'):continue
 pp=ob.data.splines[0].points;p=ob.matrix_world@pp[0].co.xyz;best=(1e9,None)
 for a,b in G.get((math.floor(p.x/5),math.floor(p.y/5)),[]):
  dx=b.x-a.x;dy=b.y-a.y;ll=dx*dx+dy*dy
  if ll<1e-12:continue
  t=max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/ll));d=(p.x-a.x-dx*t)**2+(p.y-a.y-dy*t)**2
  if d<best[0]:best=(d,a.z+(b.z-a.z)*t)
 if best[0]<.0025:pp[-1].co.z=best[1]
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'exports'/'ERS_full_station_v02.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_v02.blend'),compress=True)
