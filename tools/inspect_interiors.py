import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for key,rel in [('wap7','wap7/WAP7_interiors_v02.blend'),('lhb_3a','lhb/LHB_3A_interior_v02.blend'),('icf_sleeper','icf/icf_sleeper_interior_v02.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(root/'interiors_v02'/rel))
 print('MODEL',key)
 print('COLLECTIONS',[(c.name,len(c.objects),len(c.all_objects)) for c in bpy.data.collections])
 print('ROOTS',[(o.name,o.type) for o in bpy.data.objects if not o.parent])
 print('MARKERS',[(o.name,o.parent.name if o.parent else None,list(o.matrix_world.translation)) for o in bpy.data.objects if o.type in {'EMPTY','CAMERA'} and any(s in o.name.upper() for s in ['CAB','PAX_B01','SEATED_01','DRIVER'])])
 print('GLASS',[(m.name,[(n.type,n.image.name if n.type=='TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes] if m.use_nodes else []) for m in bpy.data.materials if any(s in m.name.lower() for s in ['glass','glaz','gauge','display'])])
