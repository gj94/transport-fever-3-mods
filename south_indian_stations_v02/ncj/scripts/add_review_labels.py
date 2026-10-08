import bpy,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
c=bpy.data.collections.new('91_REVIEW_LABELS_NOT_PHYSICAL');s.collection.children.link(c)
m=bpy.data.materials.new('Review ink');m.diffuse_color=(.035,.045,.06,1)
def txt(body,p,size):
 d=bpy.data.curves.new('Review: '+body,'FONT');d.body=body;d.size=size;d.align_x='CENTER';o=bpy.data.objects.new('Review: '+body,d);c.objects.link(o);o.location=p;d.materials.append(m)
for body,p,size in [('NAGERCOIL JUNCTION · FULL-SIZE YARD',(-50,-140,20),30),('METRES  |  BG 1676 mm  |  NO ROLLING STOCK',(-50,-188,20),18),('MAP-DERIVED WITH RECONSTRUCTED DETAIL · MIXED-DATE EVIDENCE',(-50,-222,20),14),('TVC / NAGERCOIL TOWN',(-1070,-95,20),17),('TIRUNELVELI',(-1075,565,20),17),('KANNIYAKUMARI',(1000,470,20),17),('1A TERMINAL BAY',(-530,-40,20),19),('PF1 · BOOKING / WAITING',(-15,-65,20),18),('PF2 / PF3 ISLAND',(-20,160,20),18),('PIT / MAINTENANCE ROADS',(-360,220,20),18),('GOODS SHED',(-570,-90,20),17),('SOUTH THROAT / SIDINGS',(390,195,20),18)]:txt(body,p,size)
# Label-only leader lines make the top-down view reviewable without altering physical asset geometry.
for a,b in [((-530,-17,19),(-520,5,19)),((-20,150,19),(-30,35,19)),((-355,210,19),(-330,92,19)),((385,180,19),(300,65,19))]:
 d=bpy.data.curves.new('Review leader','CURVE');d.dimensions='3D';d.bevel_depth=.7;sp=d.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1);o=bpy.data.objects.new('Review leader',d);c.objects.link(o);d.materials.append(m)
c.hide_render=True;c.hide_viewport=True;c['scope']='Review-only graphic annotation; disabled by default and excluded from physical export.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True)
