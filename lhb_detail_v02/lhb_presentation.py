"""Transient original trackside ground geometry with credited CC0 ground shaders.
This is presentation only and must never be exported with the vehicle.
"""
import bpy,math,random
from pathlib import Path

def refine_ground(studio,ground_object,asset_root):
 env=Path(asset_root).parent/'wap7_photoreal_v02/environment'
 mat=ground_object.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
 uv=ground_object.data.uv_layers.new(name='Ground_2m_repeat')
 for poly in ground_object.data.polygons:
  for li in poly.loop_indices:
   v=ground_object.data.vertices[ground_object.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.5,v.y*.5)
 for file,socket,noncolor in [('dirt_diff_2k.jpg','Base Color',False),('dirt_rough_2k.jpg','Roughness',True)]:
  path=env/file
  if path.exists():
   tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path));tex.image.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';links.new(tex.outputs['Color'],p.inputs[socket])
 path=env/'dirt_disp_2k.exr'
 if path.exists():
  tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path));tex.image.colorspace_settings.name='Non-Color';b=nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.022;b.inputs['Strength'].default_value=.6;links.new(tex.outputs['Color'],b.inputs['Height']);links.new(b.outputs['Normal'],p.inputs['Normal'])
 rng=random.Random(34324)
 def newmat(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;pp=m.node_tree.nodes.get('Principled BSDF');pp.inputs['Base Color'].default_value=(*color,1);pp.inputs['Roughness'].default_value=.88;return m
 stone_materials=[newmat('PRESENTATION natural ballast '+str(i),c) for i,c in enumerate([(.13,.125,.11),(.22,.21,.18),(.30,.28,.235),(.10,.11,.105),(.36,.34,.29)])]
 # Angular original stone meshes, scattered deterministically over the ballast bed.
 vertices=[];faces=[];mi=[]
 outline=[(-.65,-.45,-.55),(.45,-.65,-.42),(.75,.32,-.46),(-.4,.7,-.5),(-.7,-.4,.35),(.43,-.53,.65),(.64,.34,.4),(-.33,.68,.55)]
 topology=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 for i in range(13500):
  x=rng.uniform(-20,20);y=rng.uniform(-1.82,1.82);z=-.193+rng.uniform(-.01,.014)
  # Sleepers and rail pads remain visible; stones do not cover their upper faces.
  if abs((x+.31)%.62-.31)<.145 and abs(y)<1.38:continue
  a=rng.random()*math.tau;cs,sn=math.cos(a),math.sin(a);sx=rng.uniform(.025,.078);sy=rng.uniform(.023,.070);sz=rng.uniform(.026,.066);base=len(vertices)
  for xx,yy,zz in outline:vertices.append((x+xx*sx*cs-yy*sy*sn,y+xx*sx*sn+yy*sy*cs,z+zz*sz))
  color=rng.randrange(len(stone_materials))
  for f in topology:faces.append(tuple(base+j for j in f));mi.append(color)
 mesh=bpy.data.meshes.new('PRESENTATION angular stone scatter');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);studio.objects.link(o)
 for m in stone_materials:mesh.materials.append(m)
 for i,p in enumerate(mesh.polygons):p.material_index=mi[i]
 grass_materials=[newmat('PRESENTATION dry grass '+str(i),c) for i,c in enumerate([(.085,.12,.038),(.18,.21,.068),(.25,.23,.10)])]
 vertices=[];faces=[];mi=[]
 for i in range(2500):
  x=rng.uniform(-58,58);y=rng.choice([-1,1])*rng.uniform(2.1,22);h=rng.uniform(.07,.27);z=-.362
  for j in range(3):
   a=rng.random()*math.tau;w=.008;dx,dy=math.cos(a),math.sin(a);base=len(vertices)
   vertices.extend([(x-w*dy,y+w*dx,z),(x+w*dy,y-w*dx,z),(x+.06*dx,y+.06*dy,z+h)])
   faces.append((base,base+1,base+2));mi.append(rng.randrange(3))
 mesh=bpy.data.meshes.new('PRESENTATION sparse trackside grass');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);studio.objects.link(o)
 for m in grass_materials:mesh.materials.append(m)
 for i,p in enumerate(mesh.polygons):p.material_index=mi[i]
 return {'ground_material':'Poly Haven Dirt, CC0','sky':'Poly Haven Kloofendal 48d Partly Cloudy Pure Sky, CC0','track_and_vegetation':'Original deterministic mesh geometry','location_claim':None}
