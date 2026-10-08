# Executed in final build. Tests the whole stair width against real evaluated
# shelter/bridge/ceiling geometry, rather than only entry openings.
from mathutils.bvhtree import BVHTree
flush();bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();checks=[];hits=[]
colls=[c for c in bpy.data.collections if c.name.startswith(('13_','14_','80_'))]
obstacles=[]
for c in colls:
 for ob in c.objects:
  if ob.type=='MESH':
   tree=BVHTree.FromObject(ob,deps)
   if tree:obstacles.append((ob.name,tree,ob.matrix_world.inverted()))
for bx in(-105,178):
 direction=1 if bx<0 else -1
 for yy in(18.6,40.4,60):
  for k in range(38):
   xx=bx+direction*(2.1+(38-k)*.30);zz=.85+(k+1)*6.64/38
   for off in(-.9,0,.9):
    p=Vector((xx,yy+off,zz+.03));checks.append(tuple(p))
    for name,tree,inv in obstacles:
     q=inv@p;up=(inv.to_3x3()@Vector((0,0,1))).normalized();loc,normal,index,dist=tree.ray_cast(q,up,1.97)
     if loc is not None:hits.append({'bridge_x':bx,'platform_y':yy,'step':k,'across_width':off,'obstacle':name,'distance_m':dist});break
report={'sampled_vertical_clearance_m':2.0,'lateral_samples_m':[-.9,0,.9],'stair_flights':6,'sample_count':len(checks),'evaluated_obstacle_meshes':len(obstacles),'hits':hits,'result':'PASS' if not hits else 'FAIL','scope':'Full flight tread centres at three lateral positions, evaluated shelter/bridge/room-ceiling meshes. This supplements entrance/landing circulation review; not building-code certification.'}
(R/'STAIR_CLEARANCE_QA.json').write_text(json.dumps(report,indent=2));print('STAIR_CLEARANCE',report['result'],len(hits),flush=True)
