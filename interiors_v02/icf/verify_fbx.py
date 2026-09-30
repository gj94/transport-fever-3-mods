import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(p/'icf_sleeper_interior_v02.fbx'))
obs=list(bpy.context.scene.objects)
meshes=[o for o in obs if o.type=='MESH']
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
checks={'imported_objects':len(obs),'mesh_objects':len(meshes),'triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),'berth_locators':sum(o.name.startswith('BERTH_') for o in obs),'passenger_locators':sum(o.name.startswith('PASSENGER_SEATED_') for o in obs),'bogie_and_axle_parents':{o.name:o.parent.name if o.parent else None for o in obs if o.name.startswith('BOGIE_')},'world_bounds_m':[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)],'lights':sum(o.type=='LIGHT' for o in obs),'cameras':sum(o.type=='CAMERA' for o in obs)}
bpy.context.view_layer.update()
hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((-7.8,.60,2.46)),Vector((1,0,0)),distance=15.6)
checks['eye_height_aisle_ray_unobstructed']=not hit[0]
checks['ceiling_has_downward_facing_surface']=any(f.normal.z<-.9 for o in meshes if o.name.startswith('Interior curved ceiling') for f in o.data.polygons)
checks['floor_has_upward_facing_surface']=any(f.normal.z>.9 for o in meshes if o.name.startswith('Interior finished floor') for f in o.data.polygons)
assert checks['eye_height_aisle_ray_unobstructed']
(p/'fbx_validation.json').write_text(json.dumps(checks,indent=2));assert checks['berth_locators']==72 and checks['passenger_locators']==72;assert checks['lights']==checks['cameras']==0
print(checks)
bpy.ops.wm.open_mainfile(filepath=str(p/'icf_sleeper_interior_v02.blend'))
asset=[o for c in bpy.data.collections if c.name.startswith('ICF') for o in c.objects]
checks_blend={'hidden_asset_meshes':[o.name for o in asset if o.type=='MESH' and o.hide_render],'render_filepath':bpy.context.scene.render.filepath,'render_samples':bpy.context.scene.cycles.samples,'denoising':bpy.context.scene.cycles.use_denoising,'render_threads':bpy.context.scene.render.threads,'active_camera':bpy.context.scene.camera.name,'source_copy_sha256':__import__('hashlib').sha256((p/'source'/'icf_sleeper_prototype.blend').read_bytes()).hexdigest()}
(p/'blend_validation.json').write_text(json.dumps(checks_blend,indent=2));assert not checks_blend['hidden_asset_meshes'];assert checks_blend['render_filepath'].startswith('//');assert not checks_blend['denoising']
