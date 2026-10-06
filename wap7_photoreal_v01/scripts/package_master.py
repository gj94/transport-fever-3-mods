"""Save a compact self-contained vehicle master, with packed textures and no scenery.
Checks all vehicle mesh coordinates, topology, transforms, materials and image bytes
before/after packaging. The procedural setting is restored at render time.
"""
import bpy,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];MASTER=OUT/'WAP7_photoreal_v01.blend'
original_sha=hashlib.sha256(MASTER.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
def stamp():
 root=bpy.data.objects['WAP7_ROOT'];items=[];materials=set()
 for o in sorted(root.children_recursive+[root],key=lambda o:o.name):
  if o.type=='MESH':
   for m in o.data.materials:
    if m:materials.add(m)
   geom=hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[p.material_index for p in o.data.polygons])).encode()).hexdigest()
  else:geom=None
  items.append((o.name,o.parent.name if o.parent else None,[[float(x) for x in row] for row in o.matrix_world],geom,[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []))
 node_data=[]
 for m in sorted(materials,key=lambda m:m.name):
  if not m.use_nodes:continue
  ns=[]
  for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
   sockets=[]
   for a in n.inputs:
    if hasattr(a,'default_value'):
     v=a.default_value
     try:v=list(v)
     except TypeError:pass
     sockets.append((a.name,v))
   ns.append((n.name,n.bl_idname,sockets,n.image.name if n.type=='TEX_IMAGE' and n.image else None))
  links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
  node_data.append((m.name,ns,links))
 return {'vehicle_geometry_sha256':hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest(),'vehicle_material_graph_sha256':hashlib.sha256(json.dumps(node_data,sort_keys=True).encode()).hexdigest(),'packed_images':{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file},'vehicle_objects':len(items)}
before=stamp();removed=0
if 'PRESENTATION_ONLY' in bpy.data.collections:
 c=bpy.data.collections['PRESENTATION_ONLY']
 for o in list(c.all_objects):bpy.data.objects.remove(o,do_unlink=True);removed+=1
 bpy.data.collections.remove(c)
# Remove now-unused mesh data, preventing packed scene geometry from bloating the file.
for me in list(bpy.data.meshes):
 if me.users==0:bpy.data.meshes.remove(me)
for im in bpy.data.images:
 if im.source=='FILE':
  if not im.packed_file:im.pack()
  im.filepath='//textures/'+Path(im.filepath).name
scene=bpy.context.scene;scene.camera=None;scene.render.filepath='//previews/01_hero_trackside.png';scene['presentation_rebuild']='scripts/render_previews.py reconstructs scripts/build_stage.py around this self-contained vehicle master'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER),compress=True,relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(MASTER));after=stamp();assert before==after,'Vehicle content changed during packaging'
report={'source_render_master_sha256':original_sha,'packaged_master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'vehicle_content_identical':before==after,'vehicle_geometry_sha256':after['vehicle_geometry_sha256'],'vehicle_material_graph_sha256':after['vehicle_material_graph_sha256'],'packed_images_sha256':after['packed_images'],'vehicle_objects':after['vehicle_objects'],'removed_presentation_objects':removed,'packaged_bytes':MASTER.stat().st_size,'packed_texture_paths_relative':all(i.filepath.startswith('//textures/') for i in bpy.data.images if i.source=='FILE'),'presentation_reproduction':'render_previews.py executes restore_stage.py and deterministic build_stage.py; no linked external libraries'}
(OUT/'qa/packaging_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
