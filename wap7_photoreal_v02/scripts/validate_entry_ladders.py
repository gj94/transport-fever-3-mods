"""Read-only representative yaw clearance check; not a certified curve-clearance analysis."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];src=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else P/'WAP7_detail_v02.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));sc=bpy.context.scene
prefixes=('V02_EXT_lower entry ladder','V02_EXT_ladder upper bracket','V02_EXT_ladder tray','V02_EXT_thin chequered ladder','V02_EXT_raised steel chequer','V02_EXT_ladder rung')
ladders=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes) and not o.hide_render]
body=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name=='Chamfered welded body shell' or o.name.startswith(('V02_CBC_underframe','V02_CBC_body floor','V02_EXT_sill tread','V02_EXT_thin chequered sill','V02_EXT_raised sill','V02_CBC_sill recess')))]
wheels=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('V02_RG_')) and any(k in o.name.lower() for k in ['wheel','tyre','tread','axlebox','damper'])]

def under(obj,root):
 p=obj.parent
 while p:
  if p==root:return True
  p=p.parent
 return False

def combined(obs,dg):
 vs=[];fs=[]
 for o in obs:
  ob=o.evaluated_get(dg);me=ob.to_mesh();base=len(vs);vs.extend(tuple(ob.matrix_world@v.co) for v in me.vertices);fs.extend(tuple(base+j for j in p.vertices) for p in me.polygons);ob.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=.00002),vs
report={'source':src.name,'scope':'Gross body/wheel collision check at representative bogie yaw±8deg; mounting and elevation are photo-fit assumptions, not curve certification','ladders':len(ladders),'poses':{}}
for n in ['BOGIE_A_YAW_Z','BOGIE_B_YAW_Z']:
 o=bpy.data.objects[n];saved=o.rotation_euler.z
 for deg in [-8,0,8]:
  o.rotation_euler.z=math.radians(deg);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  ls=[x for x in ladders if x.parent==o];lt,vs=combined(ls,dg);bt,_=combined(body,dg);wt,_=combined([x for x in wheels if under(x,o)],dg)
  report['poses'][n+'_'+str(deg)]={'body_triangle_overlaps':len(lt.overlap(bt)),'wheel_or_axlebox_triangle_overlaps':len(lt.overlap(wt)),'ladder_world_min':[min(p[k] for p in vs) for k in range(3)],'ladder_world_max':[max(p[k] for p in vs) for k in range(3)]}
 o.rotation_euler.z=saved;bpy.context.view_layer.update()
report['no_gross_intersections']=all(x['body_triangle_overlaps']==0 and x['wheel_or_axlebox_triangle_overlaps']==0 for x in report['poses'].values())
(P/'qa/entry_ladder_yaw_clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
