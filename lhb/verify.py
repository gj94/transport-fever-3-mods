import bpy,json,os
from mathutils import Vector
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=P+'/LHB_3A_prototype.blend')
asset=bpy.data.collections['LHB_3A_PROTOTYPE'];obs=list(asset.objects)
report={'blender':bpy.app.version_string,'asset_objects':len(obs),'mesh_objects':sum(o.type=='MESH' for o in obs),'curve_objects':sum(o.type=='CURVE' for o in obs),'font_objects':sum(o.type=='FONT' for o in obs),'bogie_pivots':{o.name:list(o.location) for o in obs if o.name.startswith('BOGIE_')},'axle_pivots':{o.name:list(o.location) for o in obs if o.name.startswith('AXLE_')},'mesh_vertices_before_modifiers':sum(len(o.data.vertices) for o in obs if o.type=='MESH'),'main_berths':sum(o.name.startswith('Main_berth') for o in obs),'side_berths':sum(o.name.startswith('Side_berth') for o in obs),'status':'Visual prototype; not engine validated'}
assert len(report['bogie_pivots'])==2
assert len(report['axle_pivots'])==4
assert report['main_berths']==54 and report['side_berths']==18
assert all(abs(abs(v[0])-7.45)<1e-5 for v in report['bogie_pivots'].values())
assert all(abs(abs(v[0])-1.28)<1e-5 for v in report['axle_pivots'].values())
open(P+'/verification.json','w').write(json.dumps(report,indent=2));print(json.dumps(report))
