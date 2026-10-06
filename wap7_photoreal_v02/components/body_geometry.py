"""Correct the inherited transverse fit hack using WAP7 GA SKEL-4490.
Main body width3152mm is a representative GA dimension; generic3100 tables conflict.
Panto/bogie/axle/coupling functional datums remain fixed; fittings are relocated/recessed."""
import bpy, math
from mathutils import Vector,Matrix
import common as C
OLD_BODY_HALF=1.576*.9227166175842285
BODY_HALF=1.576
WIDTH_FACTOR=BODY_HALF/OLD_BODY_HALF

def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [(min(v[k] for v in p),max(v[k] for v in p)) for k in range(3)]

def move_side_to(o,target):
 bb=bounds(o);yc=sum(bb[1])/2;s=1 if yc>=0 else -1;mw=o.matrix_world.copy();mw.translation.y+=s*target-yc;o.matrix_world=mw

def apply(context=None):
 B=bpy.data.objects['BODY'];sc=bpy.context.scene;old=list(B.scale)
 # Perform all structural cuts before final edge treatment, avoiding repeated non-first Boolean application.
 for mod in list(bpy.data.objects['Chamfered welded body shell'].modifiers):
  if mod.type in {'BEVEL','WEIGHTED_NORMAL'}:bpy.data.objects['Chamfered welded body shell'].modifiers.remove(mod)
 keep={n:bpy.data.objects[n].matrix_world.copy() for n in ['PANTO_FRONT_CTRL','PANTO_REAR_CTRL']}
 B.scale.y=1.0;bpy.context.view_layer.update()
 for n,mw in keep.items():
  o=bpy.data.objects[n];o.matrix_parent_inverse=B.matrix_world.inverted();o.matrix_world=mw
 bpy.context.view_layer.update()
 # Unscaled source door leaves are deliberately moved into realistic recesses.
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.name.startswith('Cab door leaf'):
   move_side_to(o,1.5705)
   # Door header remains under the formed roof edge, not above it.
   iw=o.matrix_world.inverted()
   for v in o.data.vertices:
    w=o.matrix_world@v.co
    if w.z>3.545:w.z=3.545;v.co=iw@w
  elif o.name.startswith('Brushed cab door kickplate'):move_side_to(o,1.593)
  elif o.name.startswith('Kickplate fastener'):move_side_to(o,1.601)
  elif o.name.startswith('Cab identification stencil'):move_side_to(o,1.5887)
  elif o.name.startswith(('Cab entry grab rail','Cab rain downpipe')):o.hide_render=True;o.hide_viewport=True;o['v02_replaced']=True
 # A recessed filter assembly retains its real depth and a modest outer lip beyond the main skin.
 filters=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Filter ','Intake vertical screen wire','Intake horizontal screen wire'))]
 for side in [-1,1]:
  obs=[o for o in filters if sum(bounds(o)[1])*side>0]
  mx=max((max(abs(v) for v in bounds(o)[1]) for o in obs),default=BODY_HALF)
  delta=side*(1.620-mx)
  for o in obs:
   mw=o.matrix_world.copy();mw.translation.y+=delta;o.matrix_world=mw
 # Shallow outer-panel rebates receive filter rims and recessed cab hardware.
 col=C.collection('V02_BODY_RECONSTRUCTION');shell=bpy.data.objects['Chamfered welded body shell']
 def cut(n,c,d):
  cutter=C.box('V02_BODY_TEMP_'+n,c,d,None,None,col,b=0)
  mod=shell.modifiers.new(n,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 for side in [-1,1]:
  layouts=[(4.78,.78,1.43,2.91),(-3.92,.52,1.20,3.02),(-6.2,.40,.47,3.10),(-6.72,.40,.47,3.10)] if side==-1 else [(-4.8,1.43,1.30,2.94),(3.85,.52,1.30,2.96),(6.22,.38,.47,3.1),(6.70,.38,.47,3.1)]
  for x,w,h,z in layouts:cut('Recessed inertial filter aperture',(x,side*1.556,z),(w+.117,.19,h+.112))

 for side in [-1,1]:
  for e in [-1,1]:cut('Recessed cab sill access opening',(e*7.8,side*1.535,1.45),(.618,.47,.270))
 # Hollow machinery compartment follows the sloping structural roof shoulder, not an oversize box.
 # Inner clearances are inferred manufacture allowances; main external body profile stays unchanged.
 profile=[(-1.46,1.520),(1.46,1.520),(1.46,3.610),(1.315,3.735),(-1.315,3.735),(-1.46,3.610)]
 N=len(profile);vs=[(x,y,z) for x in [-7.145,7.145] for y,z in profile];fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 cutter=C.mesh('V02_BODY_TEMP_machinery_cavity',vs,fs,None,None,col)
 mod=shell.modifiers.new('True machinery compartment cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 for e in [-1,1]:cut('Cab machinery doorway connection',(e*7.245,0,2.557),(.34,.762,1.914))
 # Flush paint follows actual white or stripe surfaces, never floating centimetres off the nose.
 front_prefix=('Front railway zone','Front shed code','Front class','Front running number','Front shed name','Front HOG equipment designation')
 side_prefix=('Railway painted lettering','Large running number','Locomotive technical stencil','Jacking stencil')
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.name.startswith(front_prefix):
   iw=o.matrix_world.inverted()
   for v in o.data.vertices:
    w=o.matrix_world@v.co;e=1 if w.x>0 else -1;w.x=e*(9.52-max(w.z-2.35,0)*.35/1.2+.0007);v.co=iw@w
  elif o.name.startswith(side_prefix):
   move_side_to(o,1.5767)
  elif o.name.startswith('National tricolour'):
   # Flag has a small opaque white painted field and crosses the stripe boundary; use thin surface panel.
   iw=o.matrix_world.inverted()
   for v in o.data.vertices:
    w=o.matrix_world@v.co;w.x=math.copysign(9.5527,w.x);v.co=iw@w
 return {'old_body_scale':old,'new_body_scale':list(B.scale),'main_shell_width_m':3.152,'side_hardware':'Physically seated/offset; accessory envelope reported separately','preserved_panto_ctrl_worlds':True,'reference':'ACTM VolIII WAP7 GA SKEL4490 PDF24,3152 overall width of body','source_conflict':'Generic handbook tables list3100; selected representative WAP7-specific GA, not certified as-built39002 crosssection'}
