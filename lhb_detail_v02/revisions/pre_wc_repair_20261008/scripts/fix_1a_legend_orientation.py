"""Apply the approved 1A-only label correction to a locked master.
Run this after rebuilding 1A; the eight original build modules remain unchanged.
Only CABIN_control_legend FONT rotations change. A non-text evaluated geometry
fingerprint proves all other geometry and transforms remain untouched.
"""
import bpy, hashlib, json, math
from pathlib import Path
P=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=P/'models/LHB_1A.blend'
others={p.name:sha(p) for p in (P/'models').glob('LHB_*.blend') if p!=source}
oldsha=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
def fingerprint():
 h=hashlib.sha256();dg=bpy.context.evaluated_depsgraph_get()
 for ob in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if ob.type=='FONT':continue
  h.update(json.dumps([ob.name,ob.type,ob.parent.name if ob.parent else None,[list(r) for r in ob.matrix_world]],sort_keys=True).encode())
  if ob.type=='MESH':
   ev=ob.evaluated_get(dg);me=ev.to_mesh()
   h.update(json.dumps([[list(v.co) for v in me.vertices],[[list(p.vertices),p.material_index,p.use_smooth] for p in me.polygons],[m.name if m else None for m in me.materials]],separators=(',',':')).encode());ev.to_mesh_clear()
 return h.hexdigest()
before=fingerprint();labels=[o for o in bpy.data.objects if o.name.startswith('CABIN_control_legend')]
assert len(labels)==8 and all(o.type=='FONT' and o.data.body=='LIGHT  /  SOCKET' for o in labels)
changes=[]
for ob in labels:
 previous=list(ob.rotation_euler);ob.rotation_euler=(math.pi/2,0,math.pi)
 changes.append({'object':ob.name,'before':previous,'after':list(ob.rotation_euler),'front_normal':'+Y','text':'LIGHT  /  SOCKET'})
bpy.context.view_layer.update();after=fingerprint();assert before==after
root=bpy.data.objects['LHB_1A_ROOT_metres'];patch={'script':'scripts/fix_1a_legend_orientation.py','sha256':sha(Path(__file__)),'purpose':'Orient eight cabin legends toward the interior (+Y); no non-text changes'}
root['post_build_patch']=json.dumps(patch,sort_keys=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
glass=bpy.data.materials['GLASS_source_transmission_FBX_alpha'];p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=0;p.inputs['Alpha'].default_value=.22;glass.diffuse_color=(*glass.diffuse_color[:3],.22)
bpy.ops.object.select_all(action='DESELECT')
for o in [root]+list(root.children_recursive):o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=str(source.with_suffix('.fbx')),use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
for suffix in ['manifest','markers']:
 p=P/'models'/f'LHB_1A_{suffix}.json';data=json.loads(p.read_text());data['post_build_patch']=patch;p.write_text(json.dumps(data,indent=2))
assert all(sha(P/'models'/name)==digest for name,digest in others.items())
report={'status':'pass','source_sha256_before':oldsha,'source_sha256_after':sha(source),'patch':patch,'non_text_fingerprint_before':before,'non_text_fingerprint_after':after,'other_six_source_sha256_unchanged':others,'changes':changes,'fbx_sha256':sha(source.with_suffix('.fbx'))}
(P/'qa/1A_legend_orientation_patch.json').write_text(json.dumps(report,indent=2))
print('LEGEND_PATCH_PASS',before,sha(source),flush=True)
