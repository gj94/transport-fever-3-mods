"""Render review images without altering stored geometry. CPU, two threads, no denoise."""
import bpy,sys,math,os
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['1A','2A','3A','2S','CC','SL','GS']
for k in args:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/('LHB_'+k+'.blend')))
 sc=bpy.context.scene;studio=bpy.data.collections['PRESENTATION_ONLY'];root=bpy.data.objects['LHB_'+k+'_ROOT_metres'];objs=[root]+list(root.children_recursive)
 sc.cycles.samples=24;sc.cycles.max_bounces=5;sc.cycles.diffuse_bounces=2;sc.cycles.glossy_bounces=2;sc.cycles.transmission_bounces=4;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1280;sc.render.resolution_y=720
 # Purely presentational ground and broad-gauge track, excluded from all assets/FBX.
 def cube(n,loc,dim,mat):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;o.data.materials.append(mat)
  for c in list(o.users_collection):c.objects.unlink(o)
  studio.objects.link(o);return o
 g=bpy.data.materials.new('Presentation_ground');g.diffuse_color=(.12,.145,.18,1);g.use_nodes=True;g.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.12,.145,.18,1);g.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
 ground=cube('STUDIO_GROUND',(0,0,-.32),(200,200,.2),g)
 steel=bpy.data.materials['Satin_stainless'];rub=bpy.data.materials['Rubber_and_equipment']
 track=[]
 for y in [-.869,.869]:track.append(cube('PRESENTATION_RAIL',(0,y,-.065),(31,.062,.13),steel))
 for i in range(49):track.append(cube('PRESENTATION_SLEEPER',((i-24)*.62,0,-.17),(.24,2.65,.14),rub))
 def camera(loc,target,lens=24,ortho=None):
  o=sc.camera;o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO' if ortho else 'PERSP';o.data.ortho_scale=ortho or 25;o.data.lens=lens;o.data.clip_start=.015
 def render(name):
  path=P/'renders'/('LHB_'+k+'_'+name+'.png')
  if os.environ.get('LHB_SKIP_EXISTING')=='1' and path.exists() and not (name=='interior' and os.environ.get('LHB_REFRESH_INTERIORS')=='1'):return
  sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 camera((20,-29,13),(0,0,1.9),ortho=27);render('exterior')
 hidden=[]
 for o in objs:
  n=o.name
  hide=o.name in bpy.data.collections['ROOF_REMOVABLE'].objects or (o.users_collection and any(c.name=='ROOF_REMOVABLE' for c in o.users_collection))
  if o.type in {'MESH','FONT'}:
   co=o.matrix_world.translation
   if co.y< -1.47 and n.startswith(('BODYSIDE','WINDOW','GLASS','CURTAIN','INTERIOR_','CLASS_','RAILWAY_','COACH_','ENTRY_','DOOR_')):hide=True
  if n.startswith(('MAIN_UPPER','SIDE_UPPER','FIRST_UPPER','BERTH_upper_guard')):hide=True
  if hide and not o.hide_render:o.hide_render=True;hidden.append(o)
 camera((11,-21,27),(0,0,1.8),ortho=27);render('layout_cutaway')
 for o in hidden:o.hide_render=False
 # Real in-model view, no walls or roofs removed.
 if k=='1A':camera((-7.18,.27,2.59),(-7.23,-1.4,2.48),lens=15)
 elif k in ['2A','3A','SL','GS']:camera((-7.94,.70,2.68),(5,.70,2.55),lens=20)
 else:camera((-8.98,-.22 if k=='CC' else 0,2.65),(5,-.22 if k=='CC' else 0,2.48),lens=20)
 # Brighter inspection lighting is presentation-only, never vehicle emissive geometry.
 for light in studio.objects:
  if light.type=='LIGHT' and light.name.startswith('Interior_fill'):light.data.energy=110
 d=bpy.data.lights.new('CAMERA_INSPECTION_FILL','AREA');d.energy=100;d.shape='DISK';d.size=1.2
 lamp=bpy.data.objects.new(d.name,d);studio.objects.link(lamp);lamp.location=sc.camera.location.copy();lamp.rotation_euler=sc.camera.rotation_euler.copy()
 sc.cycles.samples=24;render('interior')
 print('RENDERED',k,flush=True)
