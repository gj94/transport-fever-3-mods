"""Editable roof manufacture and AM92-form pantograph visual hardware.
Accepted level-head animation datums are preserved; kinematic mechanism remains representative."""
import bpy,math
from mathutils import Vector,Matrix
from math import pi,sin,cos
import common as C

def apply(context=None):
 M=context['materials'];B=bpy.data.objects['BODY'];F=float(context.get('body_width_factor',1.0));col=C.collection('V02_ROOF_AND_PANTOGRAPH_DETAILS');pre='V02_RF_';C.remove_prefix(pre)
 def mesh(n,v,f,m='roof',p=B,b=0,s=False,local=False):return C.mesh(pre+n,v,f,M[m],p,col,b,s,local)
 def box(n,c,d,m='roof',p=B,b=.003,local=False):return C.box(pre+n,c,d,M[m],p,col,b,local)
 def cyl(n,c,r,d,m='iron',p=B,axis='Z',N=40,b=0,local=False):return C.cyl(pre+n,c,r,d,M[m],p,col,axis,N,b,local)
 def rod(n,a,b,r,m='iron',p=B,N=12,local=False):return C.rod(pre+n,a,b,r,M[m],p,col,N,local)
 def tube(n,pts,r,m='iron',p=B,N=14,local=False):return C.tube(pre+n,pts,r,M[m],p,col,N,local)
 def ring(n,c,ro,ri,d,m='steel',p=B,axis='Z',N=48,local=False):return C.ring(pre+n,c,ro,ri,d,M[m],p,col,axis,N,local)
 def bolt(n,c,r=.009,d=.009,m='steel',p=B,axis='Z',local=False):return C.bolt(pre+n,c,r,d,M[m],p,col,axis,local=local)
 def beam(n,a,b,w,h,m='iron',p=B,local=False):return C.beam(pre+n,a,b,w,h,M[m],p,col,local)
 C.hide_prefix(['Insulator ceramic skirt','Insulator stem','HV porcelain','Porcelain top terminal','Busbar terminal stud','Ceramic base mounting','Ceramic flange fixing','High voltage copper bus','Roof high voltage bus','Formed high-voltage busbar','Vacuum circuit breaker','Open pantograph mounting','Pantograph fixed spring','Pantograph base pivot','Pantograph frame fixing','Pantograph pneumatic air feed','Pantograph pneumatic cylinder','Roof-module','Roof ventilation module','Cab roof cooling hose','Roof hose convolution','Roof panel bolt','Roof panel washer bolt','Roof-panel lifting eye'])
 # Replace the underlying flat/chamfered cab roof instead of layering a curved cap above it.
 # Boolean cut is confined above windscreen/header apertures and leaves every rig transform untouched.
 C.hide_prefix(['Formed curved cab roof crown','Continuous eaves rain gutter'])
 shell=bpy.data.objects['Chamfered welded body shell'];crowns={}
 for e in [-1,1]:
  cutter=box('temporary obsolete roof cutter',(e*8.72,0,4.17),(3.24,3.4,1.234),'roof',p=None,b=0)
  mod=shell.modifiers.new('Remove obsolete planar cab crown','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=shell;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
  profile=[(7.10,1.454,3.836),(7.42,1.454,3.885),(7.86,1.454,3.955),(8.30,1.454,3.960),(8.63,1.454,3.885),(8.85,1.420,3.780),(9.04,1.305,3.650),(9.170,1.196,3.553)]
  pts=[]
  for k in range(len(profile)-1):
   a=Vector(profile[max(0,k-1)]);b0=Vector(profile[k]);c=Vector(profile[k+1]);d=Vector(profile[min(len(profile)-1,k+2)])
   for j in range(10):
    t=j/10;pts.append(.5*((2*b0)+(-a+c)*t+(2*a-5*b0+4*c-d)*t*t+(-a+3*b0-3*c+d)*t*t*t))
  pts.append(Vector(profile[-1]));vs=[]
  for xx,w,top in pts:
   w*=F
   for j in range(65):
    yn=-1+j/32;yy=w*yn;zz=3.553+(top-3.553)*max(0,cos(yn*pi/2))**.52
    # First row matches the actual main-body roof section, avoiding a triangular open transition.
    t=max(0,min(1,(xx-7.10)/.55));blend=t*t*(3-2*t);rear=3.78 if abs(yy)<=1.36 else 3.55+.23*max(0,(1.576-abs(yy))/.216)
    zz=rear*(1-blend)+zz*blend;vs.append((e*xx,yy,zz))
  fs=[(k*65+j,k*65+j+1,(k+1)*65+j+1,(k+1)*65+j) for k in range(len(pts)-1) for j in range(64)]
  if e==1:fs=[tuple(reversed(f)) for f in fs]
  o=mesh('continuous formed cab roof skin',vs,fs,'roof',s=True);crowns[e]=o;mod=o.modifiers.new('Steel roof skin thickness','SOLIDIFY');mod.thickness=.003
  # Seam at the removable cab crown joint, not faceted broad patches.
  for sy in [-1,1]:
   tube('cab eave folded drip edge',[(e*7.10,sy*1.587,3.553),(e*8.78,sy*1.587,3.553),(e*9.170,sy*1.302,3.553)],.008,'roof',N=12)
 for sy in [-1,1]:
  box('main body eave channel',(0,sy*1.587,3.551),(14.20,.022,.024),'roof',b=.003)
 # Roof hatch gaskets, panel lips, restrained bolt circles and proper lifting eyes.
 for x in [-6,-3,0,3,6]:
  for y in [-1.08,1.08]:
   rod('roof hatch continuous gasket',(x-1.417,y,3.83),(x+1.417,y,3.83),.008,'rubber')
   for dx in [-1.22,-.61,0,.61,1.22]:
    bolt('roof hatch washer fixing',(x+dx,y,3.879),.009,.009,'steel')
  for xx in [x-1.42,x+1.42]:
   rod('roof hatch transverse gasket',(xx,-1.078,3.83),(xx,1.078,3.83),.008,'rubber')
  for y in [-.90,.90]:
   for dx in [-1.12,1.12]:
    box('roof lifting eye foot',(x+dx,y,3.881),(.126,.058,.012),'roof',b=.003)
    # Closed steel lifting loops, not a squared pipe handle.
    ring('roof hoist lifting eye',(x+dx,y,3.930),.037,.024,.014,'iron',axis='Y',N=40)
    for dd in [-.046,.046]:bolt('hoist bracket bolt',(x+dx+dd,y,3.894),.006,.006,'steel')
 # Porcelain supports have sloped sheds with undercuts and filleted roots, not stacked flat disks.
 def porcelain(n,x,y,z,h=.27,r=.10,sheds=6):
  box(n+' mounting base',(x,y,z+.010),(.255,.245,.021),'roof',b=.005)
  for dx in [-.087,.087]:
   for dy in [-.082,.082]:bolt(n+' base fixing',(x+dx,y+dy,z+.026),.009,.009,'steel')
  profile=[(.022,.073),(.029,.083),(.038,.083),(.042,.053)]
  sh=(h-.065)/sheds
  for j in range(sheds):
   zz=.043+j*sh
   profile += [(zz,.052),(zz+sh*.26,r*.93),(zz+sh*.38,r),(zz+sh*.47,r*.98),(zz+sh*.57,.070),(zz+sh*.73,.053),(zz+sh,.052)]
  profile += [(h-.017,.055),(h-.013,.077),(h,.077)]
  C.lathe(pre+n+' glazed shed stack',(x,y,z),profile,M['ceramic'],B,col,'Z',64)
  ring(n+' upper steel flange',(x,y,z+h+.008),.079,.023,.016,'iron')
  cyl(n+' conductor stud',(x,y,z+h+.018),.019,.038,'steel',N=24)
  return z+h+.037
 # Mounting geometry follows preserved controller roots; AM92-like I base rather than giant rectangle.
 for name in ['FRONT','REAR']:
  pre0='PANTO_'+name;ctrl=bpy.data.objects[pre0+'_CTRL'];lo=bpy.data.objects[pre0+'_LOWER_PIVOT'];up=bpy.data.objects[pre0+'_ELBOW_PIVOT'];head=bpy.data.objects[pre0+'_HEAD_LEVEL_PIVOT'];x=ctrl.matrix_world.translation.x
  # Retain hidden visual proxies for downstream metadata compatibility, replace visual mesh only.
  for o in bpy.data.objects:
   if o.type=='MESH' and o.name.startswith(pre0+'_'):o.hide_render=True;o.hide_viewport=True;o['v02_replaced']=True
  for dx in [-.05,1.42]:
   for sy in [-1,1]:porcelain(name+' mounting porcelain',x+dx,sy*.49,3.865,.228,.103,5)
  box(name+' I-base central web',(x+.68,0,4.103),(1.74,.188,.053),'ochre',b=.005)
  for dx in [-.05,1.42]:
   box(name+' I-base support crossmember',(x+dx,0,4.105),(.094,1.14,.062),'ochre',b=.006)
   for sy in [-1,1]:bolt(name+' base mount stud',(x+dx,sy*.49,4.144),.012,.014,'steel')
  # Fixed transverse pivot housing with independent spring cans and retained fasteners.
  cyl(name+' base main pivot shaft',(0,0,-.012),.035,1.02,'steel',ctrl,'Y',64,local=True)
  for sy in [-1,1]:
   box(name+' base pillow block',(0,sy*.40,-.017),(.128,.078,.080),'ochre',ctrl,b=.008,local=True)
   ring(name+' base bearing gland',(0,sy*.457,-.011),.048,.027,.018,'iron',ctrl,'Y',48,True)
   bolt(name+' main bearing nut',(0,sy*.477,-.011),.025,.017,'steel',ctrl,'Y',True)
   # Spring can axis is longitudinal, with a domed end, seam and strap clamps.
   C.lathe(pre+name+' cylindrical raising spring can',(.43,sy*.263,-.021),[(-.23,0),(-.23,.055),(-.216,.066),(-.18,.069),(.18,.069),(.218,.063),(.23,.050),(.23,0)],M['ochre'],ctrl,col,'X',64,True)
   for dx in [-.155,.155]:ring(name+' spring can clamp',(dx+.43,sy*.263,-.021),.074,.066,.027,'iron',ctrl,'X',48,True)
   cyl(name+' spring can end cap',(.668,sy*.263,-.021),.049,.011,'iron',ctrl,'X',48,local=True)
   for j in range(4):
    a=j*pi/2;bolt(name+' spring cover screw',(.676,sy*.263+.037*cos(a),-.021+.037*sin(a)),.0055,.006,'steel',ctrl,'X',True)
   cyl(name+' spring tension rod',(.116,sy*.263,-.021),.012,.265,'steel',ctrl,'X',32,local=True)
   box(name+' spring rod clevis',(.013,sy*.263,-.021),(.064,.061,.045),'iron',ctrl,b=.008,local=True)
   cyl(name+' spring clevis pin',(.013,sy*.263,-.021),.012,.085,'steel',ctrl,'Y',32,local=True)
   cyl(name+' tension adjuster nut',(.152,sy*.263,-.021),.019,.021,'iron',ctrl,'X',6,local=True)
   # No generic loose service-feed tails are invented on the photographed spring housings.
  # Substantial tapered lower member is a formed structural section below hinge centre.
  vs=[]
  for xx,w,h in [(.04,.107,.104),(.17,.10,.100),(1.20,.071,.069),(1.37,.067,.065)]:
   for yy,zz in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:vs.append((xx,yy,zz-.042))
  fs=[(3,2,1,0),(12,13,14,15)]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(3) for j in range(4)]
  mesh(name+' tapered lower structural arm',vs,fs,'ochre',lo,b=.005,local=True)
  # End clevis cheeks grip the bearing shaft; closed all poses with old datum mechanism.
  for xx in [0,1.4]:
   for sy in [-1,1]:
    box(name+' lower arm clevis cheek',(xx,sy*.064,-.019),(.134,.022,.071),'ochre',lo,b=.008,local=True)
    ring(name+' lower arm bearing eye',(xx,sy*.079,-.004),.041,.022,.019,'iron',lo,'Y',48,True)
   cyl(name+' lower clevis bearing shaft',(xx,0,-.004),.023,.203,'steel',lo,'Y',48,local=True)
  # Slim parallel control rod, forked ends and actual adjustment collar.
  rod(name+' lower parallel control link',(.10,-.18,-.025),(1.31,-.18,-.025),.0105,'ochre',lo,20,True)
  for xx in [.13,1.28]:
   cyl(name+' control rod adjuster',(xx,-.18,-.025),.016,.070,'iron',lo,'X',6,local=True)
  for xx in [.072,1.350]:
   ring(name+' control link pin eye',(xx,-.18,-.026),.027,.013,.020,'ochre',lo,'Y',32,True)
   cyl(name+' control link cross pin',(xx,-.075,-.026),.011,.276,'steel',lo,'Y',32,local=True)
  # Upper arm is a thin twin tube frame with triangular diagonals, separate at elbow/head bearings.
  for sy in [-1,1]:
   rod(name+' upper tube arm',(0,sy*.28,-.007),(-1.05,sy*.245,-.007),.015,'ochre',up,24,True)
   rod(name+' upper diagonal tie',(-.035,sy*.28,-.010),(-.88,-sy*.22,-.010),.007,'ochre',up,14,True)
  rod(name+' upper frame crossbrace',(-.80,-.245,-.007),(-.80,.245,-.007),.010,'ochre',up,18,True)
  cyl(name+' elbow hollow transverse shaft',(0,0,0),.029,.718,'iron',up,'Y',56,local=True)
  for sy in [-1,1]:
   ring(name+' elbow bronze bush',(0,sy*.346,0),.035,.023,.026,'brass',up,'Y',48,True)
   bolt(name+' elbow retaining nut',(0,sy*.370,0),.024,.014,'steel',up,'Y',True)
  # Copper shunts bridge articulations in separate flexible arcs below the collector plane.
  for sy in [-1,1]:
   # Both terminals intersect real shaft/frame metal and remain attached in every pose.
   tube(name+' elbow flexible copper braid',C.bezier_points([(.018,sy*.260,-.021),(.008,sy*.324,-.054),(-.022,sy*.326,-.068),(-.070,sy*.277,-.018)],10),.005,'copper',up,12,True)
   box(name+' shunt shaft terminal',(.020,sy*.260,-.018),(.025,.028,.020),'copper',up,b=.002,local=True)
   box(name+' shunt upper tube terminal',(-.070,sy*.277,-.018),(.031,.028,.017),'copper',up,b=.002,local=True)
  # Collector head: retained carbon contact top at local z.032, metal cage/plunger hardware below it.
  for xx in [-.065,.065]:
   box(name+' collector contact carbon',(xx,0,.025),(.045,1.64,.014),'carbon',head,b=.0015,local=True)
   box(name+' collector steel carrier',(xx,0,.008),(.039,1.62,.018),'iron',head,b=.002,local=True)
   for y in [-.76,-.50,-.25,0,.25,.50,.76]:
    bolt(name+' contact strip retaining screw',(xx,y,-.006),.0045,.005,'steel',head,'Z',True)
  for y in [-.72,-.36,0,.36,.72]:box(name+' collector transverse lattice',(0,y,-.017),(.164,.021,.019),'ochre',head,b=.002,local=True)
  for sy in [-1,1]:
   # Smooth swept guide horns stay below the nominal folded contact plane.
   for xx in [-.065,.065]:
    pts=[(xx,sy*.81,.020),(xx,sy*.86,.018),(xx,sy*.93,.001),(xx,sy*.99,-.031),(xx,sy*1.024,-.070)]
    tube(name+' curved collector guide horn',C.bezier_points(pts,8),.007,'ochre',head,16,True)
   cyl(name+' head suspension plunger',(0,sy*.225,-.018),.016,.060,'steel',head,'Z',32,local=True)
   ring(name+' plunger sliding bush',(0,sy*.225,-.042),.026,.016,.016,'iron',head,'Z',32,True)
   # Correctly scaled short spring coils under the contact carrier.
   pts=[]
   for j in range(97):
    a=j/96*4*pi;pts.append((.028*cos(a),sy*.225+.028*sin(a),-.051+j/96*.039))
   tube(name+' head suspension spring',pts,.003,'steel',head,8,True)
  cyl(name+' collector rocking shaft',(0,0,-.044),.016,.63,'iron',head,'Y',40,local=True)
  # Short secured flexible bonding braid following moving head frame.
  tube(name+' collector bonding braid',C.bezier_points([(0,-.280,-.060),(-.020,-.295,-.082),(-.090,-.300,-.071),(-.065,-.280,-.004)],10),.0045,'copper',head,12,True)
  ring(name+' collector bonding shaft clip',(0,-.280,-.044),.020,.016,.026,'copper',head,'Y',40,True)
  box(name+' collector bonding carrier terminal',(-.065,-.280,-.005),(.031,.025,.009),'copper',head,b=.002,local=True)
 # Roof HV line: supported conduits and bolted saddles, clearances below4.255.
 linepts=[]
 for x in [-2.65,-1.4,.35,2.65]:
  z=porcelain('roof line porcelain',x,.572,3.861,.252,.100,6)
  box('HV copper terminal saddle',(x,.572,z-.007),(.120,.066,.020),'copper',b=.004)
  for dx in [-.038,.038]:bolt('terminal clamping nut',(x+dx,.572,z+.010),.007,.009,'steel')
 linepts=[(-4.07,.572,4.172),(-2.65,.572,4.172),(-1.4,.572,4.172),(.35,.572,4.172),(2.65,.572,4.172),(4.12,.572,4.172)]
 tube('roof longitudinal HV conductor',linepts,.015,'copper',N=20)
 tube('rear panto base electrical strap',C.bezier_points([(-4.07,.572,4.172),(-4.18,.58,4.19),(-4.32,.49,4.152)],10),.010,'copper',N=16)
 tube('front panto base electrical strap',C.bezier_points([(4.12,.572,4.172),(4.18,.56,4.192),(4.25,.43,4.178)],10),.010,'copper',N=16)
 # Two separate poles around compact vacuum breaker assembly, ceramic born profile.
 for x in [-.48,.48]:porcelain('breaker ceramic pole',x,-.23,3.861,.277,.104,7)
 box('breaker grounded mechanism base',(0,-.23,3.925),(.76,.44,.105),'roof',b=.015)
 box('breaker aluminium access cover',(0,-.468,3.929),(.67,.020,.079),'iron',b=.007)
 for x in [-.28,.28]:
  for z in [3.904,3.950]:bolt('breaker cover screw',(x,-.483,z),.005,.005,'steel',axis='Y')
 cyl('breaker main horizontal interrupter',(0,-.23,4.172),.062,.83,'ceramic',axis='X',N=64)
 for x in [-.43,.43]:
  ring('breaker terminal collar',(x,-.23,4.172),.068,.051,.035,'copper',axis='X')
  for a in [0,pi/2,pi,3*pi/2]:bolt('breaker terminal clamp',(x,-.23+.053*cos(a),4.172+.053*sin(a)),.005,.005,'steel',axis='X')
 tube('breaker return HV conductor',[(-.48,-.23,4.214),(-.60,-.23,4.224),(-1.10,.572,4.172)],.013,'copper',N=18)
 # Output goes to a separate roof-through transformer bushing, never back onto the common roofline.
 porcelain('transformer roof-through bushing',1.29,-.57,3.861,.271,.112,7)
 ring('transformer bushing waterproof skirt',(1.29,-.57,3.885),.179,.115,.018,'blackpaint',N=64)
 tube('breaker output transformer lead',[(.48,-.23,4.214),(.67,-.30,4.224),(1.29,-.57,4.169)],.013,'copper',N=18)
 # Line-side surge arrestor is a separate capped shunt to the grounded roof, with drain lead.
 porcelain('roof surge arrestor',-2.05,-.57,3.861,.288,.087,8)
 tube('surge arrestor line tap',[(-2.05,-.57,4.191),(-2.08,-.17,4.223),(-2.15,.572,4.172)],.012,'copper',N=18)
 tube('surge arrestor earth tail',[(-2.05,-.57,3.89),(-2.19,-.65,3.875),(-2.32,-.65,3.865)],.006,'copper',N=10)
 bolt('surge earth bonding stud',(-2.32,-.65,3.882),.011,.013,'steel')
 # Compact potential-transformer body with flanged porcelain entry, on the line side.
 box('roof potential transformer case',(2.38,-.52,3.959),(.37,.29,.181),'roof',b=.021)
 porcelain('potential transformer bushing',2.38,-.52,4.024,.147,.075,4)
 tube('voltage transformer line sense lead',[(2.38,-.52,4.208),(2.44,-.10,4.224),(2.49,.572,4.172)],.010,'copper',N=16)
 for dx in [-.13,.13]:
  for dy in [-.098,.098]:bolt('voltage transformer base fixing',(2.38+dx,-.52+dy,3.886),.007,.008,'steel')
 # Bus anti-vibration clamps and threaded mounting studs.
 for x in [-3.6,-2.65,-1.4,.35,2.65,3.6]:
  ring('HV line split clamp',(x,.572,4.172),.020,.015,.025,'copper',axis='X',N=32)
 # Roof cab ventilation hoods with folded flanges, true louvre depth, control-box seams.
 for e in [-1,1]:
  x=e*7.69
  box('cab roof ventilation base gasket',(x,0,3.846),(.96,1.25,.018),'rubber',b=.015)
  box('cab roof ventilation folded case',(x,0,3.974),(.91,1.18,.242),'cream',b=.018)
  box('ventilation hood removable top',(x,0,4.098),(.943,1.211,.021),'cream',b=.009)
  for sy in [-1,1]:
   box('ventilation louvre dark cavity',(x,sy*.599,3.975),(.80,.014,.175),'blackpaint',b=.006)
   # Eight horizontal slats, sloped down/outward like pressed galvanised fins.
   for j in range(7):
    z=3.907+j*.023
    vs=[(x-.386,sy*.600,z+.008),(x+.386,sy*.600,z+.008),(x+.386,sy*.622,z-.002),(x-.386,sy*.622,z-.002)]
    o=mesh('ventilation pressed louvre blade',vs,[(0,1,2,3)],'cream');mod=o.modifiers.new('Sheet metal thickness','SOLIDIFY');mod.thickness=.0015
   for dx in [-.416,.416]:box('ventilation side jamb',(x+dx,sy*.612,3.975),(.017,.029,.198),'cream',b=.003)
   for dx in [-.408,0,.408]:bolt('ventilation case screw',(x+dx,sy*.628,3.875),.0045,.005,'steel',axis='Y')
  for dx in [-.407,.407]:
   for y in [-.54,.54]:bolt('ventilation top fixing',(x+dx,y,4.116),.006,.007,'steel')
  # Exact vent service-conduit routing is not established; no unsupported free-ended hose is invented.
 # Seat the existing exterior horn hardware on the actual curved roof, not its old datum plane.
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update()
 trees={e:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],all_triangles=False) for e,o in crowns.items()}
 def roof_height(x,y):
  hit=trees[1 if x>0 else -1].ray_cast(Vector((x,y,4.8)),Vector((0,0,-1)),2)[0]
  if hit is None:raise RuntimeError('No formed roof below fitting at '+str((x,y)))
  return hit.z
 seated=[]
 for o in list(bpy.data.objects):
  if o.name.startswith('V02_EXT_horn pneumatic air line'):
   bpy.data.objects.remove(o,do_unlink=True);continue
  if not o.name.startswith(('V02_EXT_horn support foot','V02_EXT_horn mounting strap')):continue
  iw=o.matrix_world.inverted();isfoot='support foot' in o.name
  for v in o.data.vertices:
   w=o.matrix_world@v.co
   if isfoot:w.z=roof_height(w.x,w.y)+(.014 if w.z>3.979 else .001)
   elif w.z<4.022:w.z=roof_height(w.x,w.y)+.012
   v.co=iw@w
  o.data.update();o['roof_seated']=True;o['attachment_method']='Base vertices conformed to actual crown; support reaches base plate';seated.append(o.name)
 for e in [-1,1]:
  for y,L in [(-.56,.355),(.56,.310)]:
   for dx in [-.030,.030]:
    x=e*(8.40+dx);bolt('horn base seated fixing',(x,y,roof_height(x,y)+.0176),.006,.006,'steel')
   xx=e*8.20;yy=y*.80;zz=roof_height(xx,yy)
   ring('horn pneumatic roof gland gasket',(xx,yy,zz+.004),.018,.008,.006,'rubber')
   cyl('horn pneumatic roof bulkhead union',(xx,yy,zz+.018),.012,.025,'brass',N=6,b=.001)
   start=(e*(8.47-L/2-.050),y,4.091)
   cyl('horn rear air inlet union',start,.009,.017,'brass',axis='X',N=6,b=.0007)
   pts=[start,(start[0]-e*.036,y,4.083),(e*8.215,y*.90,zz+.073),(xx,yy,zz+.024)]
   tube('connected horn pneumatic air feed',C.bezier_points(pts,10),.0045,'copper',N=12)
 return {'collection':col.name,'objects':len(col.objects),'panto_transform_preservation':True,'horn_foot_and_strap_seating':seated,'description':'AM92 form visual mechanisms with preserved representative level-head authoring rig; nominal folded height within4.255m'}
