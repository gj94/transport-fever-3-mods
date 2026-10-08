"""Original bilingual class markings, using shaped Noto Devanagari raster decals.
The PNGs contain text only and are packed into each Blender master. No railway
photo or proprietary logo texture is used. Exact numbered-stock fonts vary.
"""
from pathlib import Path
import bpy
ENGLISH={'1A':'AC FIRST CLASS','2A':'AC TWO TIER','3A':'AC THREE TIER','2S':'SECOND SITTING','CC':'AC CHAIR CAR','SL':'SLEEPER','GS':'GENERAL SECOND'}
HINDI={'1A':'वातानुकूलित प्रथम श्रेणी','2A':'वातानुकूलित 2 टियर','3A':'वातानुकूलित 3 टियर','2S':'द्वितीय श्रेणी','CC':'वातानुकूलित कुर्सी यान','SL':'शयनयान','GS':'द्वितीय श्रेणी'}

def hindi(g,side,parent,x):
 path=Path(__file__).resolve().parents[1]/'textures'/f'class_hi_{g.V}.png'
 img=bpy.data.images.load(str(path),check_existing=True);img.pack();img.alpha_mode='STRAIGHT'
 name='Painted Hindi class '+g.V;m=bpy.data.materials.get(name)
 if not m:
  m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;nt.links.new(tex.outputs['Color'],p.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.62
  m.diffuse_color=(.34,.56,.54,1)
 h=.16;w=h*img.size[0]/img.size[1];y=side*1.626;z=3.21
 # Mirrored X mapping lets both sides read left-to-right from outside.
 xx=[x-w/2,x+w/2] if side<0 else [x+w/2,x-w/2]
 verts=[(xx[0],y,z-h/2),(xx[1],y,z-h/2),(xx[1],y,z+h/2),(xx[0],y,z+h/2)]
 ob=g.mesh('Hindi class painted marking',verts,[(0,1,2,3)],m,parent)
 uv=ob.data.uv_layers.new(name='Marking UV')
 for poly in ob.data.polygons:
  for li,co in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
 ob['text_hi']=HINDI[g.V];ob['font']='Noto Sans Devanagari Regular; Raqm shaped';ob['authoring']='Original text-only decal, not a photograph'
 return ob
