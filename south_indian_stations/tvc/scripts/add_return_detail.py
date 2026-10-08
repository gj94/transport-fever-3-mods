# Called by finalizer after base build. Extends 2010 visible pavilion return evidence.
import math, random, bpy
from mathutils import Vector, Matrix
random.seed(1931)
scene=bpy.context.scene
current=bpy.data.collections['01_HERITAGE_CENTRAL_3_BAY']
stone=[bpy.data.materials['Granite variation %02d'%i] for i in range(7)]
for n,label in [('mortar','Recessed grey mortar'),('cream','Weathered ivory limework'),('shutter','Aged painted timber'),('dark','Unlit aperture'),('black','Iron and rubber')]:globals()[n]=bpy.data.materials[label]
source=(R/'scripts/build_tvc.py').read_text();exec(source[source.index('def cube('):source.index("collection('01_HERITAGE")])
if not bpy.data.objects.get('RETURN_DETAIL_DONE'):
 for o in list(current.objects):
  if o.name.startswith('Pavilion side wall') and abs(o.location.x)<8:bpy.data.objects.remove(o,do_unlink=True)
 for sg in (-1,1):
  before=set(current.objects)
  ops=[(x,6.05,10.85,.62) for x in (-2.6,0,2.6)]
  facade('Central return dressed stone',0,8,14.9,0,ops)
  for x,b,s,r in ops:window(x,0,b,s,r)
  for x in (-3.55,-1.3,1.3,3.55):
   cube('Return ivory pilaster',(x,-.15,6.75),(.7,.4,13.5),cream,.025)
   cube('Return pilaster capital',(x,-.2,13.6),(1.05,.5,.23),cream,.025)
  rot=Matrix.Rotation(sg*math.pi/2,4,'Z');trans=Matrix.Translation((sg*7.2,4,0))
  for o in set(current.objects)-before:o.matrix_world=trans@rot@Matrix.LocRotScale(o.location,o.rotation_euler.to_quaternion(),o.scale)
 marker=bpy.data.objects.new('RETURN_DETAIL_DONE',None);current.objects.link(marker);marker.hide_render=True
