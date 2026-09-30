"""Fresh-import QA, Blender4.3: blender -b -t 4 --python validate_fbx.py"""
import bpy,math,json,bmesh,zipfile,tempfile
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
out={}
for name in ('WAG9_lowered.fbx','WAG9_raised.fbx','WAG9_motion.fbx'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 temporary=None;source=P/name
 if not source.exists() and (P/(name+'.zip')).exists():
  temporary=tempfile.TemporaryDirectory(prefix='wag9_fbx_qa_');source=Path(temporary.name)/name
  with zipfile.ZipFile(P/(name+'.zip')) as archive:source.write_bytes(archive.read(name))
 bpy.ops.import_scene.fbx(filepath=str(source),anim_offset=0,use_custom_normals=True)
 if temporary:temporary.cleanup()
 sc=bpy.context.scene;root=bpy.data.objects['WAG9_ROOT'];sc.frame_set(1);bpy.context.view_layer.update()
 r={'asset_file':name,'root_matrix':[[float(x) for x in row] for row in root.matrix_world],'meshes':sum(o.type=='MESH' for o in sc.objects),'parentless':[o.name for o in sc.objects if o.parent is None],'couplings':{},'rig_frames':[],'errors':[]}
 if max(abs(root.matrix_world[i][j]-float(i==j)) for i in range(4) for j in range(4))>1e-4:r['errors'].append('root matrix changed')
 if r['parentless']!=['WAG9_ROOT']:r['errors'].append('additional export roots')
 for n in ('COUPLING_FRONT','COUPLING_REAR'):
  o=bpy.data.objects[n];r['couplings'][n]={'pos':list(o.matrix_world.translation),'normal':list(o.matrix_world.to_3x3()@Vector((1,0,0))),'parent':o.parent.name}
  expected=Vector((10.281 if n.endswith('FRONT') else -10.281,0,1.105))
  if (o.matrix_world.translation-expected).length>1e-4:r['errors'].append('coupling scale/location '+n)
 r['coupling_span_m']=(bpy.data.objects['COUPLING_FRONT'].matrix_world.translation-bpy.data.objects['COUPLING_REAR'].matrix_world.translation).length
 r['bogies']=[o.name for o in sc.objects if '_YAW_Z' in o.name];r['axles']=[o.name for o in sc.objects if '_ROLL_Y' in o.name]
 if len(r['bogies'])!=2 or len(r['axles'])!=6:r['errors'].append('running gear hierarchy')
 for n in r['axles']:
  ax=bpy.data.objects[n]
  if not ax.parent or '_YAW_Z' not in ax.parent.name:r['errors'].append('axle parenting '+n)
 frames=[1,21,41,61,81,101,121,141,161] if name.endswith('motion.fbx') else [1]
 for f in frames:
  sc.frame_set(f);bpy.context.view_layer.update();fr={'frame':f,'rigs':{}}
  for side in ('FRONT','REAR'):
   pre='PANTO_'+side;lo=bpy.data.objects[pre+'_LOWER_PIVOT'];up=bpy.data.objects[pre+'_ELBOW_PIVOT'];he=bpy.data.objects[pre+'_HEAD_LEVEL_PIVOT']
   points=[ob.matrix_world@v.co for ob in sc.objects if ob.name.startswith(pre+'_CONTACT_STRIP_') for v in ob.data.vertices]
   top=max(v.z for v in points);u=he.matrix_world.to_3x3()@Vector((0,0,1));ll=(lo.matrix_world.translation-up.matrix_world.translation).length;ul=(up.matrix_world.translation-he.matrix_world.translation).length
   fr['rigs'][side]={'contact_top_m':top,'head_up':list(u),'lower_length_m':ll,'upper_length_m':ul}
   if abs(ll-1.38)>1e-4 or abs(ul-1.15)>1e-4:r['errors'].append('arm length '+side+' '+str(f))
   if (u-Vector((0,0,1))).length>1e-4:r['errors'].append('head level '+side+' '+str(f))
   if name.endswith('lowered.fbx') and abs(top-4.255)>1e-4:r['errors'].append('lowered endpoint')
   if name.endswith('raised.fbx') and abs(top-5.917)>1e-4:r['errors'].append('raised endpoint')
   if name.endswith('motion.fbx'):
    e=(min(1,max(0,(f-1)/40)) if f<=81 else max(0,1-(f-81)/40)) if side=='FRONT' else (max(0,min(1,(f-41)/40)) if f<=121 else max(0,1-(f-121)/40))
    a0=math.asin((4.255-4.105-.044)/2.53);a1=math.asin((5.917-4.105-.044)/2.53);expect=4.149+2.53*math.sin(a0+(a1-a0)*e)
    if abs(top-expect)>1e-4:r['errors'].append('baked animation offset/value '+side+' '+str(f))
  r['rig_frames'].append(fr)
 sc.frame_set(1);bpy.context.view_layer.update()
 pts=[o.matrix_world@v.co for o in sc.objects if o.type=='MESH' for v in o.data.vertices]
 r['bounds_m']={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
 r['triangles']=sum(len(p.vertices)-2 for o in sc.objects if o.type=='MESH' for p in o.data.polygons)
 r['closed_glazing']=[]
 for o in sc.objects:
  if o.name.startswith('GLASS_'):
   bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free();r['closed_glazing'].append({'name':o.name,'bad_edges':bad})
   if bad:r['errors'].append('glass nonmanifold '+o.name)
 gm=bpy.data.materials.get('12_Clear_cab_laminated_glass');gp=gm.node_tree.nodes['Principled BSDF'];r['glazing_material']={'alpha':gp.inputs['Alpha'].default_value,'transmission':gp.inputs['Transmission Weight'].default_value,'fbx_alpha_fallback':True}
 if abs(gp.inputs['Alpha'].default_value-.25)>1e-4:r['errors'].append('FBX glass alpha fallback lost')
 r['passed']=not r['errors'];out[name]=r
 print('FRESH_IMPORT',name,r['passed'],r['errors'],flush=True)
(P/'qa/fbx_fresh_import_validation.json').write_text(json.dumps(out,indent=2))
assert all(x['passed'] for x in out.values()),'FBX QA failed'
