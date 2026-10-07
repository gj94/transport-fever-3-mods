"""Fresh FBX import and relocated texture validation, with authoring marker checks.
No runtime/native conversion is performed. Blender --python validate_fbx.py -- all|CC
"""
from pathlib import Path
import bpy,json,sys,math,shutil,hashlib
P=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
variants=['1A','2A','3A','2S','CC','SL','GS'] if args[0]=='all' else args
TOL=3e-5;reports=[]
def bounds(obs):
 pts=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
for v in variants:
 folder=P/v;m=json.loads((folder/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(folder/f'ICF_{v}_master.blend'))
 root=bpy.data.objects[m['root']];asset=[root]+list(root.children_recursive);bpy.context.view_layer.update();source_bounds=bounds(asset)
 rig={o.name:{'parent':o.parent.name if o.parent else None,'matrix':[list(row) for row in o.matrix_world]} for o in asset if o.type=='EMPTY' and not o.name.startswith('BERTH_')}
 cushion_bounds=[(o.name,bounds([o])) for o in asset if o.type=='MESH' and o.get('component')=='seat_cushion']
 fits=[];source_errors=[]
 for o in asset:
  if not o.name.startswith('PAX_SEATED_'):continue
  p=o.matrix_world.translation;found=[n for n,b in cushion_bounds if b[0][0]<=p.x<=b[0][1] and b[1][0]<=p.y<=b[1][1] and abs(b[2][1]-p.z-.483)<.012]
  fits.append({'name':o.name,'cushion_candidates':found,'nominal_root_z_m':p.z})
  if not found:source_errors.append('No lower cushion at seated pelvis: '+o.name)
  if abs(p.z-m['dimensions_m']['floor_top']-.44+.483)>.002:source_errors.append('Nominal root height changed: '+o.name)
 image_pack=[{'name':im.name,'packed':im.packed_file is not None} for im in bpy.data.images if im.name.startswith('class_hi_')]
 if not image_pack or not all(x['packed'] for x in image_pack):source_errors.append('Source marking image is not packed')
 scratch=Path('/tmp')/('icf-fbx-portable-'+v);scratch.mkdir(exist_ok=True);fbx=folder/f'ICF_{v}.fbx';dest=scratch/fbx.name
 # Invalidate absolute exporter paths in a disposable equal-length binary copy.
 # Relative .fbm paths remain untouched, so success requires relocated textures.
 payload=fbx.read_bytes();prefix=str(P).encode();invalid=(b'/unavailable_icf_source'+b'_'*len(prefix))[:len(prefix)];count=payload.count(prefix);dest.write_bytes(payload.replace(prefix,invalid))
 fbmdir=folder/f'ICF_{v}.fbm'
 if fbmdir.exists():shutil.copytree(fbmdir,scratch/fbmdir.name,dirs_exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(dest));bpy.context.view_layer.update();obs=list(bpy.data.objects);errors=[]
 if any(o.type in {'LIGHT','CAMERA'} or o.name.startswith('STUDIO') for o in obs):errors.append('Studio object leaked into FBX')
 if any(o.name.startswith('BERTH_') for o in obs):errors.append('Reference berths leaked into FBX')
 for name,spec in rig.items():
  ob=bpy.data.objects.get(name)
  if not ob:errors.append('Missing hierarchy node '+name);continue
  if (ob.parent.name if ob.parent else None)!=spec['parent']:errors.append('Changed parent '+name)
  if max(abs(ob.matrix_world[i][j]-spec['matrix'][i][j]) for i in range(4) for j in range(4))>TOL:errors.append('Changed transform '+name)
 new_bounds=bounds(obs)
 if max(abs(new_bounds[i][j]-source_bounds[i][j]) for i in range(3) for j in range(2))>TOL:errors.append('Mesh bounds changed in roundtrip')
 if any(any(abs(s-1)>TOL for s in ob.scale) for ob in obs):errors.append('Nonunit imported object scale')
 glass=[]
 for mat in bpy.data.materials:
  if mat.name.startswith(('GLASS','FROST')):
   alpha=mat.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value;glass.append({'name':mat.name,'alpha':alpha})
   if not 0<alpha<1:errors.append('Missing transparent fallback '+mat.name)
 if len(glass)!=2:errors.append('Expected two glass materials')
 images=[]
 for im in bpy.data.images:
  if not im.name.startswith('class_hi_'):continue
  path=Path(bpy.path.abspath(im.filepath)).resolve();valid=path.is_relative_to(scratch) and path.is_file() and im.size[0]>0
  images.append({'name':im.name,'path':str(path),'relocated_and_loaded':valid})
  if not valid:errors.append('Marking texture did not resolve within relocated copy')
 if not images:errors.append('Marking texture absent from FBX')
 result={'variant':v,'source_passed':not source_errors,'source_errors':source_errors,'seated_marker_fit':fits,'nominal_pelvis_offset_m':.483,'soft_cushion_compression_allowance_m':.012,'source_images':image_pack,'fbx_passed':not errors,'fbx_errors':errors,'fresh_import':True,'absolute_path_references_invalidated':count,'relocated_images':images,'source_bounds_m':source_bounds,'fbx_bounds_m':new_bounds,'checked_hierarchy_nodes':len(rig),'PAX_count':sum(o.name.startswith('PAX_') for o in obs),'BERTH_export_count':sum(o.name.startswith('BERTH_') for o in obs),'glass_fallback':glass,'note':'Authoring-space seated-root fit only; full animated anatomy, game boarding and native materials remain unvalidated.'}
 (folder/'qa'/'fbx_fresh_import.json').write_text(json.dumps(result,indent=2));reports.append({'variant':v,'source_passed':not source_errors,'fbx_passed':not errors,'source_errors':source_errors,'fbx_errors':errors});print('FBX_QA',v,json.dumps(reports[-1]),flush=True)
(P/'qa'/'fbx_summary.json').write_text(json.dumps(reports,indent=2))
