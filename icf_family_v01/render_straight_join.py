import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'1A'/'ICF_1A_master.blend'));root=bpy.data.objects['ICF_1A_ROOT'];obs=[root]+list(root.children_recursive);coll=bpy.data.collections.new('TRAILING_COACH_same_meshes');bpy.context.scene.collection.children.link(coll);mapping={}
for o in obs:
 n=o.copy();coll.objects.link(n);n.name='TRAILING_'+o.name;mapping[o]=n
for o,n in mapping.items():
 n.parent=mapping.get(o.parent);n.matrix_parent_inverse=o.matrix_parent_inverse.copy();n.matrix_basis=o.matrix_basis.copy()
mapping[root].matrix_world=Matrix.Translation((22.297,0,0));bpy.context.view_layer.update()
scene=bpy.context.scene;cam=scene.camera;cam.data.type='PERSP';cam.data.lens=53;cam.location=(11.1485,-2.5,4.0);cam.rotation_euler=(Vector((11.1485,0,1.14))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1100;scene.render.resolution_y=760
for loc,energy in [((11.15,-2.3,2.9),400),((11.15,1.7,2.4),200)]:
 ld=bpy.data.lights.new('STUDIO coupling detail fill','AREA');ld.energy=energy;ld.size=1.8;o=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((11.1485,0,1.10))-o.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(P/'renders'/'two_coach_CBC_connection.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'qa'/'two_coach_straight_fixture.blend'),compress=True);bpy.ops.render.render(write_still=True)
