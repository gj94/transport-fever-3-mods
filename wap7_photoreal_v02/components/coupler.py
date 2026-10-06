"""Photo-led locomotive tightlock transition coupler and front chassis detail.
Frontier manufacturer H-loco morphology; preserved artistic coupling planes, not certified mating CAD."""
import bpy, math, random
from mathutils import Vector, Matrix
from math import pi,sin,cos
import common as C

def apply(context=None):
 M=context['materials'];B=bpy.data.objects['BODY'];col=C.collection('V02_COUPLER_AND_BUFFER_DETAILS');pre='V02_CBC_';C.remove_prefix(pre)
 C.hide_prefix(['CBC knuckle boss','CBC knuckle cast','CBC mechanical','CBC pin washer','CBC throat','CBC top','Buffer plate','Buffer shank','Buffer central','Buffer polished','Buffer beam','Brake air hose','Hose connector','Pilot perimeter','Pilot horizontal','Pilot vertical','Pilot lower','Main load bearing underframe'])
 for o in bpy.data.objects:
  if o.type=='MESH' and o.name.startswith(('CBC_FRONT_','CBC_REAR_')):o.hide_render=True;o.hide_viewport=True;o['v02_replaced']=True
 def mesh(n,v,f,m='iron',p=B,b=0,s=False):return C.mesh(pre+n,v,f,M[m],p,col,b,s)
 def box(n,c,d,m='iron',p=B,b=.004):return C.box(pre+n,c,d,M[m],p,col,b)
 def cyl(n,c,r,d,m='iron',p=B,axis='Z',N=40,b=0):return C.cyl(pre+n,c,r,d,M[m],p,col,axis,N,b)
 def rod(n,a,b,r,m='iron',p=B,N=12):return C.rod(pre+n,a,b,r,M[m],p,col,N)
 def tube(n,pts,r,m='iron',p=B,N=14):return C.tube(pre+n,pts,r,M[m],p,col,N)
 def ring(n,c,ro,ri,d,m='steel',p=B,axis='X',N=64):return C.ring(pre+n,c,ro,ri,d,M[m],p,col,axis,N)
 def bolt(n,c,r=.014,d=.014,m='steel',p=B,axis='X'):return C.bolt(pre+n,c,r,d,M[m],p,col,axis)
 def extr(n,poly,z0,z1,m='cast',p=B,b=.008):return C.extrude_xy(pre+n,poly,z0,z1,M[m],p,col,b)
 def beam(n,a,b,w,h,m='iron',p=B):return C.beam(pre+n,a,b,w,h,M[m],p,col)
 # Actual perimeter structure opens the top of each bogie to spring pockets.
 for s in [-1,1]:
  box('underframe longitudinal outer web',(0,s*1.508,1.405),(19.03,.070,.190),'blackpaint',b=.007)
  box('underframe channel lower flange',(0,s*1.487,1.315),(19.03,.160,.024),'iron',b=.004)
  box('underframe channel upper flange',(0,s*1.487,1.492),(19.03,.180,.020),'blackpaint',b=.003)
  # Continuous weld toe under body sill, manufactured radius only a few mm.
  rod('underframe flange weld',(-9.45,s*1.414,1.478),(9.45,s*1.414,1.478),.003,'iron')
 floorpan=box('body floor structural pan',(0,0,1.505),(18.97,3.03,.036),'blackpaint',b=.003)
 # Proper recesses receive the documented long secondary coils inside the body.
 shell=bpy.data.objects['Chamfered welded body shell']
 for mod in list(floorpan.modifiers):floorpan.modifiers.remove(mod)
 for bx in [-6,6]:
  for dx in [-.255,.255]:
   for sy in [-1,1]:
    cutter=box('temporary spring pocket cutter',(bx+dx,sy*1.12,1.535),(.338,.342,.760),'blackpaint',p=None,b=0)
    for target in [floorpan,shell]:
     mod=target.modifiers.new('Secondary spring service pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
     bpy.context.view_layer.objects.active=target
     bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
 mod=floorpan.modifiers.new('Floorpan manufactured cut edges','BEVEL');mod.width=.002;mod.segments=2
 floorpan.modifiers.new('Floorpan face normals','WEIGHTED_NORMAL')
 for x in [-8.95,-3.1,-2.15,0,2.15,3.1,8.95]:
  box('underframe transverse diaphragm',(x,0,1.404),(.085,3.00,.18),'blackpaint',b=.006)
  for s in [-1,1]:
   for z in [1.35,1.455]:bolt('diaphragm attachment',(x,s*1.551,z),.009,.009,'steel',axis='Y')
 # Local sill pockets keep the photo-fit top tread within the body section rather than a projecting wing.
 targets=[o for o in col.objects if o.name.startswith(('V02_CBC_underframe longitudinal','V02_CBC_underframe channel','V02_CBC_body floor structural'))]
 for o in targets:
  for mod in list(o.modifiers):
   if mod.type in {'BEVEL','WEIGHTED_NORMAL'}:o.modifiers.remove(mod)
 for e in [-1,1]:
  for side in [-1,1]:
   cutter=box('temporary cab sill pocket',(e*7.8,side*1.535,1.454),(.630,.49,.275),'blackpaint',p=None,b=0)
   for target in targets:
    mod=target.modifiers.new('Entry sill recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
   bpy.data.objects.remove(cutter,do_unlink=True)
   for xx in [e*7.8-.329,e*7.8+.329]:box('sill recess reinforcement cheek',(xx,side*1.496,1.406),(.024,.105,.182),'iron',b=.004)
 for o in targets:
  mod=o.modifiers.new('Machined step pocket edges','BEVEL');mod.width=.0025;mod.segments=2;o.modifiers.new('Underframe normals','WEIGHTED_NORMAL')
 for e,label in [(1,'FRONT'),(-1,'REAR')]:
  P=bpy.data.objects['CBC_'+label+'_PIVOT']
  # Helpers reflect full outward coordinate set, but preserve coupler pivot and inheritance.
  def Q(x,y,z):return(e*x,e*y,z)
  def shape(n,poly,z0,z1,m='cast',b=.010):return extr(n,[Q(x,y,0)[:2] for x,y in poly],z0,z1,m,P,b)
  def cast_loft(n,poly,z0,z1,m='cast',tip=None,taper=.90):
   # Each contour corner is a physical cast radius; z sections carry the shoulder transitions.
   pts=[]
   for k,c in enumerate(poly):
    c=Vector(c);a=Vector(poly[k-1]);d=Vector(poly[(k+1)%len(poly)])
    f=min(.28,.017/max(.0001,min((a-c).length,(d-c).length)))
    a=c+(a-c)*f;d=c+(d-c)*f
    for j in range(7):
     t=j/6;pts.append((1-t)**2*a+2*(1-t)*t*c+t*t*d)
   if tip:
    shift=tip-max(v.x for v in pts)
    pts=[Vector((v.x+shift,v.y)) for v in pts]
   center=sum(pts,Vector((0,0)))/len(pts);h=z1-z0;vs=[]
   edge=min(.024,h*.18);levels=[(z0,taper),(z0+edge,1),(z0+h*.26,1.005),(z1-h*.26,1.005),(z1-edge,1),(z1,taper)]
   for zz,scale in levels:
    for v in pts:
     q=center+(v-center)*scale;vs.append(Q(q.x,q.y,zz))
   if tip:
    delta=tip-max(e*v[0] for v in vs);vs=[(v[0]+e*delta,v[1],v[2]) for v in vs]
   N=len(pts);fs=[tuple(reversed(range(N))),tuple(range((len(levels)-1)*N,len(levels)*N))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(levels)-1) for i in range(N)]
   o=mesh(n,vs,fs,m,P,s=True)
   o.data.polygons[0].use_smooth=False;o.data.polygons[1].use_smooth=False
   return o
  # Head shape: concave guard-arm throat, separate curved pivoting knuckle, top/bottom wings.
  # Existing 10.200 m datum remains an artistic contact plane. Extreme tip reaches10.281.
  shank=[(9.43,-.10),(9.90,-.102),(10.02,-.172),(10.11,-.190),(10.151,-.141),(10.145,-.088),(10.01,-.048),(9.86,.103),(9.43,.102)]
  shape('forged shank and hollow head transition',shank,.991,1.219,'cast',.014)
  # Deep throat left clear; guard arm wraps outside it with tapered cast thickness.
  guard=[(9.94,-.14),(10.03,-.224),(10.19,-.237),(10.256,-.207),(10.271,-.162),(10.252,-.127),(10.190,-.143),(10.096,-.158),(10.029,-.107)]
  guardobj=cast_loft('curved guard arm',guard,.980,1.233,'cast',taper=.87)
  # Tightlock wings extend vertically at the back of the mouth; open slots are genuine gaps.
  wings=[]
  for za,zb in [(.922,.993),(1.224,1.293)]:
   wing=[(10.018,-.19),(10.094,-.266),(10.220,-.264),(10.27,-.209),(10.252,-.183),(10.130,-.197),(10.075,-.125)]
   wings.append(cast_loft('anti-climber wing',wing,za,zb,'cast',taper=.83))
  # Visible vertically curved knuckle on opposite side of throat.
  knuckle=[(10.047,.108),(10.035,.156),(10.047,.202),(10.089,.229),(10.180,.224),(10.248,.174),(10.281,.121),(10.276,.045),(10.255,-.042),(10.229,-.079),(10.198,-.070),(10.181,-.031),(10.186,.053),(10.161,.108),(10.103,.071),(10.058,.067)]
  knuckleobj=cast_loft('closed curved knuckle',knuckle,.942,1.267,'cast',tip=10.281,taper=.92)
  # Contact burnishing is assigned to the actual bearing surface, not a floating silver sticker.
  import materials
  contactmat=materials.basic('V02_CBC_rubbed_knuckle_steel',(.19,.185,.168),.40,1,.055,.000035,1100,.022)
  knuckleobj.data.materials.append(contactmat)
  for f in knuckleobj.data.polygons:
   if .990<f.center.z<1.225 and e*f.center.x>10.215 and abs(f.center.y)<.178 and e*f.normal.x>.35:f.material_index=1
  # Interrupted guard-wing web gives the casting its visible deep side relief.
  # Tapered through-relief gives splayed cast ribs rather than a machined rectangular window.
  section=[(10.088,1.063),(10.174,1.066),(10.208,1.095),(10.194,1.151),(10.073,1.158),(10.071,1.101)]
  cv=[]
  for yy,scale in [(-.315,1.10),(-.107,.80)]:
   for xx,zz in section:cv.append(Q(10.14+(xx-10.14)*scale,yy,1.110+(zz-1.110)*scale))
  nn=len(section);cf=[tuple(reversed(range(nn))),tuple(range(nn,2*nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
  cutter=mesh('temporary guard relief cutter',cv,cf,'cast',p=None,b=.010)
  bpy.context.view_layer.objects.active=cutter
  for mm in list(cutter.modifiers):bpy.ops.object.modifier_apply(modifier=mm.name)
  mod=guardobj.modifiers.new('Cast guard-arm web relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=guardobj;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
  # Knuckle pin has bored cast bosses and a separate turned retaining shaft.
  for z in [.958,1.263]:
   ring('knuckle cast pin boss',Q(10.066,.153,z),.055,.030,.042,'cast',P,'Z',56)
  cyl('knuckle retained pivot pin',Q(10.066,.153,1.123),.026,.355,'steel',P,'Z',48,b=.002)
  cyl('knuckle pin cap',Q(10.066,.153,1.309),.035,.014,'iron',P,'Z',48,b=.003)
  ring('knuckle pin cap witness',Q(10.066,.153,1.318),.014,.005,.003,'blackpaint',P,'Z',32)
  # Rear locking mechanism, thrower linkage and top-operated release toggle.
  box('lock lifter foot',Q(9.981,-.034,1.260),(.120,.105,.030),'cast',P,b=.009)
  for y in [-.080,.027]:box('lock lifter bearing cheek',Q(9.992,y,1.288),(.100,.018,.060),'cast',P,b=.008)
  cyl('lock lifter horizontal shaft',Q(9.992,-.026,1.303),.018,.140,'steel',P,'Y',40)
  box('lock lifter saddle',Q(10.003,-.026,1.314),(.079,.059,.038),'iron',P,b=.010)
  tube('lock operating link',[Q(9.991,-.026,1.316),Q(9.975,-.047,1.362),Q(9.898,-.089,1.381)],.012,'iron',P)
  # Open top pin drilling and visible internal receiver floor under the mouth.
  # The visible upper wing drilling is actually open through the casting, not a dark disk.
  drill=cyl('temporary casting bore cutter',Q(10.164,-.202,1.266),.019,.126,'iron',p=None,axis='Z',N=48)
  for target in [wings[1],guardobj]:
   mm=target.modifiers.new('Upper casting through bore','BOOLEAN');mm.operation='DIFFERENCE';mm.solver='EXACT';mm.object=drill;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mm.name)
  bpy.data.objects.remove(drill,do_unlink=True)
  ring('casting drainage bore rim',Q(10.164,-.202,1.294),.024,.019,.004,'iron',P,'Z',48)
  mod=guardobj.modifiers.new('Casting relief edge radius','BEVEL');mod.width=.0025;mod.segments=3
  box('coupler throat bottom wear plate',Q(10.107,-.038,.983),(.133,.142,.013),'grease',P,b=.004)
  # Lower transition screw-coupling suspension eye, cast lug and pivoted sling.
  for y in [-.064,.064]:box('transition coupling suspension cheek',Q(10.052,y,.914),(.104,.039,.084),'cast',P,b=.012)
  cyl('transition suspension pin',Q(10.052,0,.910),.024,.205,'steel',P,'Y',40)
  tube('transition hanging sling',C.bezier_points([Q(10.08,-.061,.905),Q(10.11,-.065,.772),Q(10.113,0,.741),Q(10.11,.065,.772),Q(10.08,.061,.905)],12),.018,'iron',P,N=16)
  # Raised casting parting ridge is narrow, restrained, mechanically plausible.
  tube('casting parting seam',[Q(9.69,.104,1.209),Q(9.91,.109,1.209),Q(10.023,.186,1.226),Q(10.18,.226,1.247)],.0018,'iron',P,N=8)
  # Draft pocket, striker and support saddle surround the extending shank.
  for y in [-.145,.145]:box('draft pocket side cheek',Q(9.53,y,1.105),(.39,.030,.315),'iron',P,b=.009)
  for z in [.955,1.255]:box('draft pocket upper lower cheek',Q(9.53,0,z),(.39,.308,.028),'iron',P,b=.007)
  cyl('draft pin top retained',Q(9.53,0,1.273),.048,.020,'steel',P,N=40,b=.005)
  for y in [-.124,.124]:bolt('draft pocket fastening',Q(9.68,y,1.27),.016,.016,'steel',P,'Z')
  box('coupler support leaf carrier',Q(9.81,0,.926),(.245,.330,.035),'iron',P,b=.007)
  for y in [-.14,.14]:box('support saddle side runner',Q(9.81,y,.966),(.255,.031,.082),'iron',P,b=.008)
  # Body-fixed uncoupling bar, operating bracket and articulated link (link follows coupler).
  tube('uncoupling handle rod',[Q(9.60,-1.08,1.29),Q(9.64,-.88,1.31),Q(9.69,-.55,1.31),Q(9.73,-.20,1.345),Q(9.86,-.10,1.375)],.012,'blackpaint')
  for y in [-.94,-.56]:
   box('uncoupling rod bracket',Q(9.60,y,1.32),(.045,.050,.074),'iron',b=.005)
   bolt('uncoupling rod pivot',Q(9.641,y,1.324),.013,.014,'steel')
  # Bufferbeam box flanges and web; central draft opening remains clear.
  for y in [-.85,.85]:
   box('bufferbeam outboard web',Q(9.615,y,1.155),(.215,1.02,.285),'blackpaint',b=.006)
   for z in [1.017,1.287]:box('bufferbeam horizontal flange',Q(9.615,y,z),(.245,1.04,.022),'iron',b=.003)
  for s in [-1,1]:
   y=s*.978
   # Disc and buffer shank are machined lathe geometry with shoulder and mounting flange.
   box('buffer mounting plate',Q(9.737,y,1.105),(.030,.337,.368),'iron',b=.013)
   for yy in [y-.126,y+.126]:
    for zz in [.967,1.243]:bolt('buffer base bolt',Q(9.760,yy,zz),.018,.018,'steel')
   prof=[(9.746,.133),(9.775,.139),(9.793,.111),(9.923,.111),(9.944,.097),(10.045,.097)]
   C.lathe(pre+'buffer cylindrical housing',Q(0,y,1.105),[(e*x,r) for x,r in prof],M['iron'],B,col,'X',72)
   C.lathe(pre+'buffer polished sliding ram',Q(0,y,1.105),[(e*9.927,.093),(e*10.052,.093)],M['bright'],B,col,'X',64)
   # Buffer face has a subtle convex dish, flange edge and a full face wear map.
   prof=[(10.021,0),(10.021,.206),(10.032,.235),(10.049,.244),(10.083,.244),(10.103,.216),(10.113,.145),(10.118,0)]
   bf=C.lathe(pre+'buffer convex contact disc',Q(0,y,1.105),[(e*x,r) for x,r in prof],M['iron'],B,col,'X',96)
   # Separate contacted face shader and local UVs from the calibrated physical material library.
   import materials
   materials.assign_buffer_uv(bf,axis='X')
   bf.data.materials.append(M['buffer'])
   for f in bf.data.polygons:
    if abs(f.center.x)>10.069:f.material_index=1
   # Grease nipple and dust boot witness rings at the housing shoulder.
   ring('buffer seal dust ring',Q(9.933,y,1.105),.116,.096,.019,'rubber',axis='X',N=64)
   cyl('buffer grease nipple',Q(9.834,y,1.230),.009,.019,'brass',N=16)
  # Air system isolating taps and uncoupled hoses, connected with hanging dummy heads.
  for s,y in [(-1,-.36),(1,.80)]:
   z=1.02
   cyl('air cock mounting boss',Q(9.76,y,z),.031,.055,'iron',axis='X',N=32)
   cyl('air cock valve body',Q(9.805,y,z),.032,.071,'brass',axis='X',N=32)
   cyl('air cock spindle',Q(9.807,y,z+.039),.012,.041,'steel',N=24)
   box('air cock lever',Q(9.813,y+s*.038,z+.063),(.020,.109,.012),'red' if s==-1 else 'cream',b=.004)
   for xx in [9.770,9.828]:cyl('air hose hex union',Q(xx,y,z),.033,.020,'iron',axis='X',N=6)
   pts=[Q(9.848,y,z),Q(9.93,y+s*.045,.80),Q(9.90,y+s*.045,.56),Q(9.80,y-s*.13,.51),Q(9.73,y-s*.27,.58)]
   tube('air brake hose',C.bezier_points(pts,14),.021,'rubber',N=16)
   cc=Q(9.73,y-s*.27,.58)
   cyl('air hose dummy coupling body',cc,.041,.051,'iron',axis='X',N=40)
   ring('air hose dummy face seal',Q(9.762,y-s*.27,.58),.030,.018,.009,'rubber',axis='X',N=32)
   for dz in [-.029,.029]:box('air gladhand cast lug',Q(9.743,y-s*.27,.58+dz),(.04,.071,.018),'iron',b=.006)
   # Small suspension tether uses discrete chain links, not solid black rope.
   for k in range(7):
    cc=Q(9.73,y-s*.27,.625+k*.026);ring('hose retaining chain link',cc,.016,.010,.004,'iron',axis='X' if k%2 else 'Y',N=20)
  # Substantial open lattice pilot. Welded rectangular perimeter, fine bars, attachment plates.
  pts=[Q(9.498,-1.285,.390),Q(9.556,-1.410,.527),Q(9.57,-1.365,.924),Q(9.57,1.365,.924),Q(9.556,1.410,.527),Q(9.498,1.285,.390),Q(9.498,-1.285,.390)]
  for a,b in zip(pts[:-1],pts[1:]):beam('pilot perimeter welded angle',a,b,.039,.036,'iron')
  for y in [-1.20,-.98,-.76,-.54,-.32,-.10,.12,.34,.56,.78,1.,1.20]:
   beam('pilot vertical flat bar',Q(9.531,y,.410),Q(9.575,y,.915),.014,.011,'iron')
  for z in [.468,.60,.733,.865]:
   beam('pilot horizontal flat bar',Q(9.544,-1.344,z),Q(9.544,1.344,z),.013,.013,'iron')
  box('pilot replaceable bottom wear strip',Q(9.515,0,.393),(.055,2.575,.060),'iron',b=.006)
  for y in [-1.26,-.90,-.55,.55,.90,1.26]:bolt('pilot wear strip rivet',Q(9.548,y,.402),.012,.010,'iron')
  for y in [-1.17,1.17]:
   beam('pilot rear mounting strut',Q(9.53,y,.78),Q(9.40,y,1.19),.062,.045,'iron')
   box('pilot mounting plate',Q(9.59,y,.821),(.018,.138,.108),'iron',b=.007)
   for yy in [y-.046,y+.046]:bolt('pilot attachment bolt',Q(9.612,yy,.821),.011,.011,'steel')
 return {'objects':len(col.objects),'collection':col.name,'length_extrema_m':[-10.281,10.281],'anchor_preservation':True,'note':'Manufacturer/photo-led H-type morphology, representative small hardware; no mating CAD certification'}
