"""Fresh Blender/FBX import, pivot/anchor/motion and live highreach swept QA."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent

def worldverts(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(p.vertices) for p in m.polygons];ev.to_mesh_clear();return v,f

def bvh(o):
 v,f=worldverts(o);return BVHTree.FromPolygons(v,f,all_triangles=False)

def stripinfo():
 o=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Panto_contact_strips');v,f=worldverts(o);zs=[w.z for w in v];top=[w.z for w in v if abs(w.z-max(zs))<.0001]
 # Check local strip top row transformed: must be identical horizontal plane.
 upper=[o.matrix_world@v.co for v in o.data.vertices if abs(v.co.z-.032)<1e-5]
 return {'top_z_m':max(zs),'top_level_spread_m':max(w.z for w in upper)-min(w.z for w in upper)}

def basecheck():
 roots=[o for o in bpy.data.objects if not o.parent and o.type=='EMPTY'];assert len(roots)==1,[(o.name,o.type) for o in roots];r=roots[0]
 assert r.name.startswith('WAG12B_') and r.name.endswith('_ROOT')
 assert max(abs(r.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
 anchors={}
 for n,x in [('COUPLING_FRONT',9.6),('COUPLING_REAR',-9.6)]:
  o=bpy.data.objects[n];assert o.parent==r;assert (o.matrix_world.translation-Vector((x,0,1.105))).length<2e-5
  normal=(o.matrix_world.to_3x3()@Vector((1,0,0))).normalized();assert (normal-Vector((1 if x>0 else -1,0,0))).length<1e-5;anchors[n]={'xyz_m':list(o.matrix_world.translation),'normal':list(normal)}
 axles=[]
 for label,x in [('A',5.1),('B',-5.1)]:
  bo=bpy.data.objects['BOGIE_'+label+'_YAW_Z'];assert bo.parent==r;assert abs(bo.matrix_world.translation.x-x)<1e-5
  for i,xx in enumerate((1.3,-1.3),1):
   a=bpy.data.objects[f'AXLE_{label}_{i}_ROLL_Y'];assert a.parent==bo;assert (a.matrix_world.translation-Vector((x+xx,0,.625))).length<2e-5;axles.append(list(a.matrix_world.translation))
 drivers=[o for o in bpy.data.objects if o.name.startswith('DRIVER_')];assert len(drivers)==2;assert all(o.parent.name=='CAB_INTERIOR' for o in drivers)
 mesh=[o for o in bpy.data.objects if o.type=='MESH'];tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in mesh);assert all(math.isfinite(c) for o in mesh for v in o.data.vertices for c in v.co)
 # All vertices reachable below single root, no presentation props.
 assert all(o==r or o in r.children_recursive for o in bpy.data.objects)
 assert not any(o.type in ('LIGHT','CAMERA') for o in bpy.data.objects)
 return {'root':r.name,'anchors':anchors,'axles_world_m':axles,'crew_markers':len(drivers),'mesh_objects':len(mesh),'triangles':tris,'all_finite':True,'all_asset_objects_under_root':True,'no_presentation_objects':True}

def fresh_imports():
 reports=[]
 for f in sorted((P/'sections').glob('*.fbx')):
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(f),use_anim=True,anim_offset=0);bpy.context.view_layer.update();report=basecheck();report['file']=f.name;report['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
  glass=next(m for m in bpy.data.materials if m.name=='Clear_glass');node=glass.node_tree.nodes.get('Principled BSDF');alpha=node.inputs['Alpha'].default_value;assert abs(alpha-.18)<.001,alpha;report['fbx_glass_alpha']=alpha;report['fbx_transmission_portability']='Transmission is not represented by FBX; alpha=.18 fallback verified'
  if '_motion' in f.name:
   frames=[]
   for frame,height in [(1,4.245),(41,7.52),(81,4.245)]:
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();s=stripinfo();assert abs(s['top_z_m']-height)<.0001,(f,frame,s);assert s['top_level_spread_m']<.0001;frames.append({'frame':frame,**s})
   report['motion_samples']=frames
  else:
   target=7.52 if '_highreach' in f.name else 5.917 if '_standard_raised' in f.name else 4.245
   s=stripinfo();assert abs(s['top_z_m']-target)<.0001,(f,s,target);assert s['top_level_spread_m']<.0001;report['contact_strip']=s
  report['passed']=True;reports.append(report)
 (P/'qa'/'fbx_roundtrip.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'anim_offset':0,'fresh_import_count':len(reports),'all_passed':True,'files':reports},indent=2))

def live_checks():
 reports=[]
 for sec in ('A','B'):
  bpy.ops.wm.open_mainfile(filepath=str(P/'sections'/('WAG12B_'+sec+'.blend')));bpy.context.view_layer.update();base=basecheck();ctrl=bpy.data.objects['PANTO_CTRL'];low=bpy.data.objects['PANTO_LOWER_PIVOT'];elb=bpy.data.objects['PANTO_ELBOW_PIVOT'];head=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT'];moving=[o for p in (low,elb,head) for o in p.children if o.type=='MESH']
  # All non-panto geometry above shoulder is considered roof obstacle. Own bearing/insulator seats exempt by design.
  obstacles=[]
  for o in bpy.data.objects:
   if o.type!='MESH' or o.name.startswith('Panto_'):continue
   vs,fs=worldverts(o)
   if max(v.z for v in vs)>3.78 and min(v.x for v in vs)<-1.0:obstacles.append((o.name,bvh(o)))
  collisions=[];rows=[]
  for i in range(101):
   ctrl['extension']=i/100;ctrl.update_tag();bpy.context.view_layer.update();s=stripinfo();assert s['top_level_spread_m']<.00005
   len1=(elb.matrix_world.translation-low.matrix_world.translation).length;len2=(head.matrix_world.translation-elb.matrix_world.translation).length;assert abs(len1-2.4)<1e-5 and abs(len2-2)<1e-5
   normal=(head.matrix_world.to_3x3()@Vector((0,0,1))).normalized();assert (normal-Vector((0,0,1))).length<.00001
   for o in moving:
    bv=bvh(o)
    for name,obv in obstacles:
     if bv.overlap(obv):collisions.append({'extension':i/100,'moving':o.name,'static':name})
   if i in (0,25,50,75,100):rows.append({'extension':i/100,**s,'rigid_lengths_m':[len1,len2]})
  # Opaque wall aperture probes independent of glass and fine protective guard bars.
  ctrl['extension']=0;ctrl.update_tag();bpy.context.view_layer.update();opaque=[]
  for o in bpy.data.objects:
   if o.type=='MESH' and any(k in o.name for k in ('shell','panels','pillars','cheek','fascia','bulkhead')):opaque.append((o.name,bvh(o)))
  probes=[]
  for y,z in [(-.7,2.92),(.7,2.92),(-.5,3.31),(.5,3.31)]:
   hits=[]
   for n,bv in opaque:
    pos,norm,idx,dist=bv.ray_cast(Vector((8.1,y,z)),Vector((1,0,0)),3)
    if pos is not None:hits.append(n)
   probes.append({'origin':[8.1,y,z],'opaque_shell_hits':hits});assert not hits,probes[-1]
  # Main side window sightlines.
  for sy in (-1,1):
   hits=[]
   for n,bv in opaque:
    if bv.ray_cast(Vector((7.8,0,3.10)),Vector((0,sy,0)),2)[0] is not None:hits.append(n)
   probes.append({'origin':[7.8,0,3.10],'direction':[0,sy,0],'opaque_shell_hits':hits});assert not hits
  reports.append({'section':sec,'base':base,'poses_checked':101,'head_level_pass':True,'rigid_lengths_pass':True,'samples':rows,'roof_collision_pairs':collisions,'aperture_probes':probes,'runtime_character_fit':'not tested; markers provisional','passed':not collisions})
 (P/'qa'/'rig_and_aperture_checks.json').write_text(json.dumps({'all_passed':all(x['passed'] for x in reports),'sections':reports},indent=2));assert all(x['passed'] for x in reports),[(x['section'],x['roof_collision_pairs'][:8]) for x in reports]

fresh_imports();live_checks();print('ALL WAG12B CHECKS PASS')
