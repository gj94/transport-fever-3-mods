import bpy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; sc=bpy.context.scene
exec(compile((R/'scripts/add_return_detail.py').read_text(),str(R/'scripts/add_return_detail.py'),'exec'))
for n in ['Platform name English','Platform code','Module provenance label','Trilingual TVC nameboard lettering']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
# Replace placeholder foliage volumes with explicit individual leaf silhouettes.
import random, math
from mathutils import Vector
random.seed(23)
for old in [o for o in list(sc.objects) if o.name.startswith('Foliage cluster')]:
 vs=[];fs=[];center=old.location.copy()
 for j in range(110):
  az=random.uniform(0,math.tau);el=random.uniform(-.8,.8);rr=random.random()**.5
  p=center+Vector((math.cos(az)*rr*1.25,math.sin(az)*rr,.65*el))
  a=random.uniform(0,math.tau);u=Vector((math.cos(a),math.sin(a),random.uniform(-.4,.4)))*random.uniform(.12,.25)
  v=Vector((-math.sin(a),math.cos(a),.1))*.065;n=len(vs)
  vs.extend([p-u,p+v,p+u,p-v,p+Vector((0,0,.025))]);fs.extend([(n,n+1,n+4),(n+1,n+2,n+4),(n+2,n+3,n+4),(n+3,n,n+4)])
 me=bpy.data.meshes.new('Tropical leaflet cloud');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Individual tropical leaf clusters',me);bpy.data.collections['03_FORECOURT_CONTEXT_GAME_ADJUSTED'].objects.link(o);me.materials.append(bpy.data.materials['Tropical foliage']);bpy.data.objects.remove(old,do_unlink=True)

# Original, correctly shaped Malayalam/Hindi/English graphic.
m=bpy.data.materials.new('Original trilingual board graphic');m.use_nodes=True
im=bpy.data.images.load(str(R/'textures/TVC_trilingual_board.png'));im.pack()
t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;p=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.75
vs=[(11.89,20.69,2.56),(17.61,20.69,2.56),(17.61,20.69,4.45),(11.89,20.69,4.45)]
me=bpy.data.meshes.new('Trilingual sign plate');me.from_pydata(vs,[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new(name='UVMap')
for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=co
o=bpy.data.objects.new('Trilingual TVC nameboard lettering',me);bpy.data.collections['04_MODULAR_PLATFORM_CANOPY_DEMONSTRATOR'].objects.link(o);me.materials.append(m)
# Use 1.676 m clear inner rail-head distance, head width .068.
for o in sc.objects:
 if o.name.startswith(('Rail foot','Rail web','Rail head')):o.location.y=13.8 + (.872 if o.location.y>13.8 else -.872)
# Pack fonts too; source is portable.
bpy.ops.file.pack_all()
bpy.data.objects['CAM_Hero'].data.lens=39
sc.camera=bpy.data.objects['CAM_Hero'];sc.render.resolution_percentage=75;sc.cycles.samples=64;sc.cycles.use_denoising=False;sc.render.threads=4
for c in bpy.data.collections:
 if c.name.startswith(('01_','02_','03_','04_')):c.asset_mark();c['dimension_basis']='photo-inferred / game-adjusted; no station-specific survey dimensions'
bpy.data.collections['04_MODULAR_PLATFORM_CANOPY_DEMONSTRATOR'].instance_offset=(0,19,0)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'TVC_heritage_2022_v1.blend'))
qa={'objects':len(sc.objects),'meshes':sum(o.type=='MESH' for o in sc.objects),'vertices':sum(len(o.data.vertices) for o in sc.objects if o.type=='MESH'),'scale_length':sc.unit_settings.scale_length,'packed_images':[i.name for i in bpy.data.images if i.packed_file],'missing_external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()],'central_upper_front_bays':3,'station_specific_measured_dimensions':0,'rail_inner_gauge_m':1.676,'render_engine':sc.render.engine,'render_samples':sc.cycles.samples,'render_threads':sc.render.threads}
(R/'qa_geometry.json').write_text(json.dumps(qa,indent=2))
for cam,name in [('CAM_Hero','hero'),('CAM_Elevation','elevation'),('CAM_Heritage_detail','heritage_detail'),('CAM_Canopy_detail','canopy_detail')]:
 sc.camera=bpy.data.objects[cam];sc.render.resolution_percentage=100 if name in ['hero','elevation'] else 75;sc.render.resolution_y=650 if name=='elevation' else 1000;sc.render.filepath=str(R/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
