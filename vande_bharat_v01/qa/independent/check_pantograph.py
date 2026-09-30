"""Read-only independent VB pantograph rigid-motion and roof intersection sweep."""
import bpy,json,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
path=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else str(Path(__file__).resolve().parents[2]/'cars/VB_TC_CC.blend');bpy.ops.wm.open_mainfile(filepath=path)
r=bpy.data.objects['PANTO_CTRL'];lo=bpy.data.objects['PANTO_LOWER_PIVOT'];up=bpy.data.objects['PANTO_ELBOW_PIVOT'];he=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT']
moving=[o for o in lo.children_recursive if o.type=='MESH']
def pts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o):return BVHTree.FromPolygons(pts(o),[tuple(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=1e-7)
def bb(ps):return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def overlap(a,b):return all(a[0][i]<=b[1][i] and b[0][i]<=a[1][i] for i in range(3))
fixed=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o in moving or o.name.lower().startswith('panto_'):continue
 ps=pts(o);b=bb(ps)
 if b[1][2]<3.70 or b[0][0]>.7 or b[1][0]<-2:continue
 fixed.append((o,tree(o),b))
poses=[];hits=[]
for i in range(101):
 r['extension']=i/100;r.update_tag();bpy.context.view_layer.update()
 lengths=[(up.matrix_world.translation-lo.matrix_world.translation).length,(he.matrix_world.translation-up.matrix_world.translation).length]
 strip=[o for o in he.children if o.type=='MESH' and 'contact_strips' in o.name.lower()]
 tops=[p.z for o in strip for p in pts(o)]
 poses.append({'extension':i/100,'lengths':lengths,'head_tilt_rad':max(abs(x) for x in he.matrix_world.to_euler()),'contact_top_z':max(tops)})
 for o in moving:
  ps=pts(o);b=bb(ps);tr=None
  for other,ot,ob in fixed:
   if not overlap(b,ob):continue
   if tr is None:tr=tree(o)
   intersections=tr.overlap(ot)
   if intersections:hits.append({'extension':i/100,'moving':o.name,'fixed':other.name,'triangle_pairs':len(intersections)})
report={'file':path,'poses':poses,'roof_intersections':hits,'fixed_meshes_checked':[o.name for o,t,b in fixed],'method':'101 independent extension poses; world-space triangle BVH overlap against nearby non-pantograph roof/body meshes; excludes base assembly contacts and joint self-contact. No manufacturing or runtime-wire certification.'}
out=(Path(__file__).resolve().parent/'independent_pantograph_sweep.json');out.write_text(json.dumps(report,indent=2));print('PANTO_REVIEW',len(hits),'intersection records',poses[0],poses[-1])
