"""Minimal factual marking correction on existing approved source masters.
Only four Technical maintenance stencil mesh datablocks per class are replaced.
All other mesh geometry, transforms, materials and hierarchy are fingerprinted.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,struct,datetime
p=Path(__file__).resolve().parents[1]
variants=['1A','2A','3A','2S','CC','SL','GS']

def fingerprint(root):
 h=hashlib.sha256();count=0
 for o in sorted(root.children_recursive,key=lambda o:o.name):
  if o.name.startswith('Technical maintenance stencil'):continue
  h.update(o.name.encode());h.update((o.parent.name if o.parent else '').encode());h.update(str([list(row) for row in o.matrix_world]).encode())
  if o.type=='MESH':
   count+=1
   for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
   for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
   for m in o.data.materials:h.update(m.name.encode())
 return h.hexdigest(),count

for v in variants:
 folder=p/v;source=folder/f'ICF_{v}_master.blend';previous_sha=hashlib.sha256(source.read_bytes()).hexdigest();manifest=json.loads((folder/'manifest.json').read_text())
 if manifest.get('build_pass')=='r12-stencil' and (folder/'qa/capacity_stencil_patch.json').exists():
  prior=json.loads((folder/'qa/capacity_stencil_patch.json').read_text())
  if prior.get('after_source_sha256')==previous_sha and prior.get('non_text_geometry_unchanged'):
   print('STENCIL_ALREADY_PATCHED',v,flush=True);continue
 bpy.ops.wm.open_mainfile(filepath=str(source));root=bpy.data.objects[f'ICF_{v}_ROOT'];before,count=fingerprint(root)
 obs=[o for o in root.children_recursive if o.name.startswith('Technical maintenance stencil')];assert len(obs)==4,(v,len(obs))
 label=f'{manifest["subtype"].split()[0]}  {manifest["physical_capacity"]}  '+('BERTHS' if manifest['physical_berths'] else 'SEATS')
 for o in obs:
  cu=bpy.data.curves.new('Capacity stencil replacement','FONT');cu.body=label;cu.size=.039;cu.align_x='CENTER';cu.resolution_u=10;cu.extrude=.0002;cu.space_character=1.04
  tmp=bpy.data.objects.new('TEMP capacity stencil',cu);bpy.context.scene.collection.objects.link(tmp)
  for m in o.data.materials:cu.materials.append(m)
  bpy.ops.object.select_all(action='DESELECT');tmp.select_set(True);bpy.context.view_layer.objects.active=tmp;bpy.ops.object.convert(target='MESH')
  bm=bmesh.new();bm.from_mesh(tmp.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
  tiny=[f for f in bm.faces if f.calc_area()<1e-12]
  if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
  wire=[e for e in bm.edges if not e.link_faces]
  if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
  loose=[x for x in bm.verts if not x.link_edges]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  if bm.edges and all(e.is_manifold for e in bm.edges):bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  bm.to_mesh(tmp.data);bm.free();o.data=tmp.data;o['capacity_stencil_text']=label;bpy.data.objects.remove(tmp,do_unlink=True)
 after,count_after=fingerprint(root);assert before==after and count==count_after,'Non-text geometry changed'
 previous_pass=root['build_pass'];root['build_pass']='r12-stencil';root['geometry_base_pass']=previous_pass
 meshes=[o for o in root.children_recursive if o.type=='MESH'];tri=sum(len(f.vertices)-2 for o in meshes for f in o.data.polygons)
 manifest['previous_build_pass']=manifest['build_pass'];manifest['build_pass']='r12-stencil';manifest['triangles']=tri
 manifest['build_source_sha256']['icf_shell.py']=hashlib.sha256((p/'scripts/icf_shell.py').read_bytes()).hexdigest();manifest['build_source_sha256'][Path(__file__).name]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 manifest['capacity_stencil']=label;manifest['build_time_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest['source_before_stencil_sha256']=previous_sha
 manifest['rebuild_command']='Base build.py all, then build_1a_r11.py, then patch_capacity_stencils_r12.py'
 bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):
  if not o.name.startswith('BERTH_'):o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=root
 glass=next(m for m in bpy.data.materials if m.name.startswith('GLASS'));bs=glass.node_tree.nodes.get('Principled BSDF');alpha=bs.inputs['Alpha'].default_value;bs.inputs['Alpha'].default_value=glass.get('fbx_fallback_alpha',.24)
 bpy.ops.export_scene.fbx(filepath=str(folder/f'ICF_{v}.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='X',axis_up='Z',apply_unit_scale=True,use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,use_custom_props=True,path_mode='COPY',embed_textures=False);bs.inputs['Alpha'].default_value=alpha
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2))
 report={'variant':v,'before_source_sha256':previous_sha,'after_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'non_text_geometry_sha256_before':before,'non_text_geometry_sha256_after':after,'non_text_meshes_checked':count,'non_text_geometry_unchanged':before==after,'replaced_stencils':len(obs),'text':label,'no_tare_mass_claim':True,'source_geometry_base_pass':previous_pass}
 (folder/'qa/capacity_stencil_patch.json').write_text(json.dumps(report,indent=2));print('STENCIL_PATCHED',v,label,count,flush=True)
