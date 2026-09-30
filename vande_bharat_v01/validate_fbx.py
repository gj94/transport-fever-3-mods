"""Fresh Blender FBX import validation; doesn't claim target game importer equivalence."""
import bpy,json,math,re,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;results={}
for path in sorted((P/'cars').glob('*.fbx')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));sc=bpy.context.scene;bpy.context.view_layer.update();obs=list(sc.objects);roots=[o for o in obs if o.type=='EMPTY' and 'ROOT' in o.name and not o.parent];assert len(roots)==1,(path,roots);root=roots[0]
 kind=path.stem.removeprefix('VB_').removesuffix('_raised').removesuffix('_motion');qa=json.loads((P/'qa'/f'VB_{kind}.json').read_text());positions={n:list(bpy.data.objects[n].matrix_world.translation) for n in ['COUPLING_FRONT','COUPLING_REAR','BOGIE_A_YAW_Z','BOGIE_B_YAW_Z']}
 for n,expected in [('COUPLING_FRONT',[9.6875,0,1.02]),('COUPLING_REAR',[-9.6875,0,1.02]),('BOGIE_A_YAW_Z',[5.85,0,.71]),('BOGIE_B_YAW_Z',[-5.85,0,.71])]:assert (Vector(positions[n])-Vector(expected)).length<1e-5,(path,n,positions[n])
 axles=[o for o in obs if o.type=='EMPTY' and o.name.startswith('AXLE_')];assert len(axles)==4
 for o in axles:assert o.parent and o.parent.name.startswith('BOGIE_') and abs(o.matrix_world.translation.z-.476)<1e-5
 paxes=[o for o in obs if o.type=='EMPTY' and o.name.startswith('PAX_')];drivers=[o for o in obs if o.type=='EMPTY' and re.fullmatch(r'DRIVER_\d+',o.name)];doors=[o for o in obs if o.type=='EMPTY' and o.name.startswith('DOOR_')];assert len(paxes)==qa['passenger_seats'];assert len(drivers)==qa['driver_seats'];assert len(doors)==4
 assert all(o==root or o in list(root.children_recursive) for o in obs)
 norms=[re.sub('[^a-z0-9_]','_',o.name.lower()) for o in obs];assert len(norms)==len(set(norms))
 report={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'root_count':1,'root_identity_error':max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4)),'coordinates':positions,'axle_count':4,'door_pivots':len(doors),'passenger_anchors':len(paxes),'driver_anchors':len(drivers),'all_parented':True,'normalized_name_collisions':False,'bounds':None}
 pts=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices];report['bounds']={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
 if kind.startswith('TC'):
  for n,pa in [('PANTO_CTRL','PANTO_BASE'),('PANTO_LOWER_PIVOT','PANTO_CTRL'),('PANTO_ELBOW_PIVOT','PANTO_LOWER_PIVOT'),('PANTO_HEAD_LEVEL_PIVOT','PANTO_ELBOW_PIVOT')]:assert bpy.data.objects[n].parent.name==pa
  report['panto_hierarchy_retained']=True
  if '_motion' in path.stem:
   poses=[]
   # Default Blender FBX importer adds one frame offset.
   for frame in [2,22,42,62,82]:
    sc.frame_set(frame);bpy.context.view_layer.update();he=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT'];poses.append({'import_frame':frame,'head_top_z_m':he.matrix_world.translation.z+.032,'head_level_error':max(abs(v) for v in he.matrix_world.to_euler())})
   assert abs(poses[0]['head_top_z_m']-4.0791215)<1e-4;assert abs(poses[2]['head_top_z_m']-5.917)<1e-4;assert max(p['head_level_error'] for p in poses)<1e-4;report['baked_sample_poses']=poses
  else:
   he=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT'];target=5.917 if '_raised' in path.stem else 4.0791215;assert abs(he.matrix_world.translation.z+.032-target)<1e-4;report['panto_contact_top_m']=he.matrix_world.translation.z+.032
 results[path.name]=report
(P/'qa'/'fbx_roundtrip.json').write_text(json.dumps(results,indent=2));print('FBX_VALIDATION_PASS',len(results))
