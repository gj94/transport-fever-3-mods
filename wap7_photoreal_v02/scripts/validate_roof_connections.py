"""Check visible bonding terminals against real metal seats at representative poses.
This is a geometric attachment check, not electrical-design certification.
"""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
master=Path(a[0]) if a else P/'WAP7_detail_v02.blend'
bpy.ops.wm.open_mainfile(filepath=str(master));scene=bpy.context.scene
rows=[]
def point_box_gap(world,ob):
 p=ob.matrix_world.inverted()@world
 lo=[min(v.co[k] for v in ob.data.vertices) for k in range(3)]
 hi=[max(v.co[k] for v in ob.data.vertices) for k in range(3)]
 return sum(max(lo[k]-p[k],0,p[k]-hi[k])**2 for k in range(3))**.5
for extension in [0,.62,1]:
 for name in ['FRONT','REAR']:
  ctrl=bpy.data.objects['PANTO_'+name+'_CTRL'];ctrl['extension']=extension;ctrl.update_tag()
 scene.frame_set(1);bpy.context.view_layer.update()
 for name in ['FRONT','REAR']:
  up=bpy.data.objects['PANTO_'+name+'_ELBOW_PIVOT'];head=bpy.data.objects['PANTO_'+name+'_HEAD_LEVEL_PIVOT']
  specs=[]
  for side in [-1,1]:
   specs += [('elbow shaft '+str(side),up,(.018,side*.260,-.021),'shunt shaft terminal',.005),('elbow upper tube '+str(side),up,(-.070,side*.277,-.018),'shunt upper tube terminal',.005)]
  specs += [('collector carrier',head,(-.065,-.280,-.004),'collector bonding carrier terminal',.0045),('collector shaft',head,(0,-.280,-.060),'collector bonding shaft clip',.0045)]
  for label,parent,co,suffix,radius in specs:
   point=parent.matrix_world@Vector(co)
   targets=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V02_RF_'+name+' '+suffix)]
   assert targets,(name,suffix)
   gap=min(point_box_gap(point,o) for o in targets)
   rows.append({'extension':extension,'pantograph':name,'connection':label,'endpoint_to_terminal_bounds_gap_m':gap,'cable_radius_m':radius,'pass':gap<=radius+.0005})
# Fixed roof bus straps terminate on actual panto mounting fittings.
for label,co,needle in [('rear bus strap',(-4.32,.49,4.152),'V02_RF_REAR base mount stud'),('front bus strap',(4.25,.43,4.178),'V02_RF_FRONT base pillow block')]:
 targets=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(needle)]
 gap=min(point_box_gap(Vector(co),o) for o in targets)
 rows.append({'connection':label,'endpoint_to_terminal_bounds_gap_m':gap,'cable_radius_m':.010,'pass':gap<=.0105})
loose=[o.name for o in bpy.data.objects if not o.hide_render and o.name.startswith('V02_RF_') and 'air supply tube' in o.name]
assert not loose,loose
crowns={}
for o in bpy.data.objects:
 if o.name.startswith('V02_RF_continuous formed cab roof skin'):
  vs=[o.matrix_world@v.co for v in o.data.vertices];sign=1 if sum(v.x for v in vs)>0 else -1
  crowns[sign]=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in o.data.polygons])
for o in bpy.data.objects:
 if not o.name.startswith('V02_EXT_horn support foot'):continue
 gaps=[]
 for v in list(o.data.vertices)[:4]:
  p=o.matrix_world@v.co;hit=crowns[1 if p.x>0 else -1].ray_cast(Vector((p.x,p.y,4.8)),Vector((0,0,-1)),2)[0]
  assert hit is not None;gaps.append(p.z-hit.z)
 rows.append({'connection':o.name,'base_to_actual_crown_gaps_m':gaps,'pass':all(.0005<g<.0015 for g in gaps)})
assert not [o.name for o in bpy.data.objects if not o.hide_render and 'cab cooling service conduit' in o.name]
report={'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'checks':rows,'unsupported_loose_service_tails':loose,'all_pass':all(r['pass'] for r in rows),'limit':'Endpoint-to-terminal geometry checks only; electrical routing and exact AM92 manufacture remain representative'}
(P/'qa/roof_connection_validation.json').write_text(json.dumps(report,indent=2))
print('ROOF_CONNECTIONS',report['all_pass'],len(rows),flush=True)
assert report['all_pass'],report
