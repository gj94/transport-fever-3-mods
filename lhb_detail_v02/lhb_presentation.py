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
 phi=(1+math.sqrt(5))/2;norm=math.sqrt(1+phi*phi)*1.65
 outline=[tuple(v/norm for v in q) for q in [(-1,phi,0),(1,phi,0),(-1,-phi,0),(1,-phi,0),(0,-1,phi),(0,1,phi),(0,-1,-phi),(0,1,-phi),(phi,0,-1),(phi,0,1),(-phi,0,-1),(-phi,0,1)]]
 topology=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
 for i in range(13500):
  x=rng.uniform(-20,20);y=rng.uniform(-1.82,1.82);z=-.193+rng.uniform(-.01,.014)
  # Sleepers and rail pads remain visible; stones do not cover their upper faces.
  if abs((x+.31)%.62-.31)<.145 and abs(y)<1.38:continue
  a=rng.random()*math.tau;cs,sn=math.cos(a),math.sin(a);sx=rng.uniform(.025,.078);sy=rng.uniform(.023,.070);sz=rng.uniform(.026,.066);base=len(vertices)
  for xx,yy,zz in outline:
   jitter=rng.uniform(.72,1.24);vertices.append((x+(xx*sx*cs-yy*sy*sn)*jitter,y+(xx*sx*sn+yy*sy*cs)*jitter,z+zz*sz*jitter))
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
