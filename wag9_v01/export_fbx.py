"""Re-export interchange assets from masters, with FBX-only glass alpha fallback.
Blender: blender -b -t 4 --python export_fbx.py
Creates static FBXs and a losslessly zipped motion FBX. Live masters stay unchanged.
"""
import bpy,zipfile,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent

def export(name,anim=False):
 root=bpy.data.objects['WAG9_ROOT'];bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root
 m=bpy.data.materials['12_Clear_cab_laminated_glass'];p=m.node_tree.nodes['Principled BSDF'];old=(tuple(m.diffuse_color),tuple(p.inputs['Base Color'].default_value),p.inputs['Alpha'].default_value)
 m.diffuse_color=(*old[0][:3],.25);p.inputs['Base Color'].default_value=(*old[1][:3],.25);p.inputs['Alpha'].default_value=.25
 bpy.ops.export_scene.fbx(filepath=str(P/name),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_space_transform=False,add_leaf_bones=False,bake_anim=anim,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,path_mode='AUTO',use_custom_props=True)
 m.diffuse_color=old[0];p.inputs['Base Color'].default_value=old[1];p.inputs['Alpha'].default_value=old[2]
bpy.ops.wm.open_mainfile(filepath=str(P/'WAG9_master.blend'))
for e,name in [(0,'WAG9_lowered.fbx'),(1,'WAG9_raised.fbx')]:
 for side in ('FRONT','REAR'):
  c=bpy.data.objects['PANTO_'+side+'_CTRL'];c['extension']=e;c.update_tag()
 bpy.context.view_layer.update();export(name)
bpy.ops.wm.open_mainfile(filepath=str(P/'WAG9_baked_motion.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();export('WAG9_motion.fbx',True)
raw=P/'WAG9_motion.fbx';archive=P/'WAG9_motion.fbx.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.write(raw,raw.name)
with zipfile.ZipFile(archive) as z:unpacked=z.read(raw.name)
a=hashlib.sha256(raw.read_bytes()).hexdigest();b=hashlib.sha256(unpacked).hexdigest();assert a==b
(P/'qa/motion_archive_validation.json').write_text(json.dumps({'archive':archive.name,'member':raw.name,'uncompressed_bytes':raw.stat().st_size,'archive_bytes':archive.stat().st_size,'uncompressed_sha256':a,'extracted_sha256':b,'passed':a==b},indent=2))
print('EXPORT_AND_ZIP_COMPLETE',archive.stat().st_size,flush=True)
