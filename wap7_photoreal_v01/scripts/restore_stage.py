"""Recreate the exact presentation setting around the compact vehicle-only master.
Executed by render_previews.py after opening the master. Helper function definitions
are read without executing the model-building statements in build_refinement.py.
"""
import bpy,math,random,ast
from pathlib import Path
from mathutils import Vector,Matrix
from math import pi,sin,cos
OUT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;root=bpy.data.objects['WAP7_ROOT'];body=bpy.data.objects['BODY'];asset=bpy.data.collections['PHOTOREAL_REFINEMENT'];created=[]
if 'PRESENTATION_ONLY' in bpy.data.collections:
 for o in list(bpy.data.collections['PRESENTATION_ONLY'].all_objects):bpy.data.objects.remove(o,do_unlink=True)
 stage=bpy.data.collections['PRESENTATION_ONLY']
else:
 stage=bpy.data.collections.new('PRESENTATION_ONLY');scene.collection.children.link(stage)
for name,key in [('rubber','PBR • weathered EPDM'),('edge','PBR • rubbed black metal'),('ceramic','PBR • glazed brown porcelain'),('steel','PBR • polished steel contact edges')]:globals()[name]=bpy.data.materials[key]
tree=ast.parse((OUT/'scripts/build_refinement.py').read_text())
helpers=ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))],type_ignores=[])
exec(compile(helpers,'geometry_helpers_from_build_refinement','exec'),globals())
random.seed(19002)
exec(compile((OUT/'scripts/build_stage.py').read_text(),'build_stage.py','exec'),globals())
print('REBUILT_PRESENTATION_GEOMETRY',len(stage.all_objects),flush=True)
