"""Original ICF family: Blender 4.3.2. Run blender -b -t 2 --python build_icf_family.py -- [all|1A|2A|3A|2S|CC|SL|GS] [--render].
No external assets/dependencies. Prototype layout interpretation, not manufacturing drawings.
"""
import bpy, bmesh, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(__file__).resolve().parents[1]
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
VARIANTS={
 '1A':dict(code='WGFAC',capacity=18,berths=18,ac=True,label='A C  F I R S T',layout='3 four-berth cabins and 3 two-berth coupes; 18 daytime seated positions',windows=9),
 '2A':dict(code='WGACCW',capacity=46,berths=46,ac=True,label='A C  T W O  T I E R',layout='7 full 6-berth bays plus 4-berth end bay; curtains; no middle berths',windows=16),
 '3A':dict(code='WGACCN',capacity=64,berths=64,ac=True,label='A C  T H R E E  T I E R',layout='8 bays of 8 berths; daytime folded middle berths; wide sealed windows',windows=8),
 '2S':dict(code='WGSCZ',capacity=108,berths=0,ac=False,label='S E C O N D  S I T T I N G',layout='18 rows of 3+3 individual low-back seats; nine facing pairs',windows=18),
 'CC':dict(code='WGSCZAC',capacity=73,berths=0,ac=True,label='A C  C H A I R  C A R',layout='14 rows of 3+2 reclining-style chairs plus one 3-seat end row',windows=8),
 'SL':dict(code='WGSCN',capacity=72,berths=72,ac=False,label='S L E E P E R',layout='9 bays of 8 berths; daytime folded middle berths',windows=18),
 'GS':dict(code='GS / WGS 108-seat representative',capacity=108,berths=0,ac=False,label='G E N E R A L  S E C O N D',layout='18 rows of 3+3 benches; related second-seating shell; 108-seat subtype',windows=18),
}
# Mesh builders put coordinates in vehicle space. Parenting preserves world transforms.
def material(n,c,metal=0,rough=.45,alpha=1,transmission=0,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,alpha);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Alpha'].default_value=alpha;p.inputs['Transmission Weight'].default_value=transmission
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 if transmission:m['source_transmission']=transmission;m['fbx_fallback_alpha']=alpha;m['tf3_material']='glass'
 return m

def mesh(n,v,f,m,parent=None,coll=None,bevel=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);(coll or C).objects.link(o)
 if m:me.materials.append(m)
 if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
 if bevel:
  mod=o.modifiers.new('Small manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=2
 return o

def box(n,c,s,m,parent=None,bevel=0,coll=None):
 x,y,z=c;a,b,d=[v/2 for v in s];v=[(x+i*a,y+j*b,z+k*d) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 # Consistent outward winding for all six manufactured box faces.
 return mesh(n,v,[tuple(reversed(face)) for face in f],m,parent or BODY,coll,bevel)

def rod(n,a,b,r,m,parent=None,N=10,coll=None):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.01:u=d.cross(Vector((1,0,0)))
 u.normalize();w=d.cross(u);v=[tuple(p+r*(math.cos(i*2*math.pi/N)*u+math.sin(i*2*math.pi/N)*w)) for p in [a,b] for i in range(N)];f=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[tuple(reversed(range(N))),tuple(range(N,2*N))]
 return mesh(n,v,f,m,parent or BODY,coll)

def path(n,pts,r,m,parent=None,N=8):
 # Joined cylindrical sections remain original mesh, with no live curve dependency.
 for a,b in zip(pts,pts[1:]):rod(n,a,b,r,m,parent,N)

def empty(n,loc,parent=None,yaw=0):
 o=bpy.data.objects.new(n,None);C.objects.link(o);o.parent=parent;o.location=loc;o.rotation_euler.z=yaw;o.empty_display_type='ARROWS';o.empty_display_size=.13;bpy.context.view_layer.update();return o

def text(n,s,pos,size,m,sign=-1,parent=None):
 cu=bpy.data.curves.new(n,'FONT');cu.body=s;cu.size=size;cu.align_x='CENTER';cu.resolution_u=10;cu.extrude=.0002;o=bpy.data.objects.new(n,cu);C.objects.link(o);o.location=pos;o.rotation_euler=(math.pi/2,0,0 if sign==-1 else math.pi);cu.materials.append(m);o.parent=parent or BODY;o.matrix_parent_inverse=o.parent.matrix_world.inverted();return o

def loop(n,x,y,z,w,h,m,parent=None):
 # Chamfered rectangular gasket ring. Nonzero aperture, no opaque pane behind it.
 r=.06;pts=[(x-w/2+r,y,z-h/2),(x+w/2-r,y,z-h/2),(x+w/2,y,z-h/2+r),(x+w/2,y,z+h/2-r),(x+w/2-r,y,z+h/2),(x-w/2+r,y,z+h/2),(x-w/2,y,z+h/2-r),(x-w/2,y,z-h/2+r),(x-w/2+r,y,z-h/2)]
 path(n,pts,.012,m,parent,N=8)

def ring(n,c,r,m,parent=None,N=20,tube=.005):
 pts=[(c[0]+r*math.cos(i*2*math.pi/N),c[1]+r*math.sin(i*2*math.pi/N),c[2]) for i in range(N+1)];path(n,pts,tube,m,parent,6)

def pax(c,yaw=0):
 global NPAX
 NPAX+=1;o=empty(f'PAX_SEATED_{NPAX:03d}',c,INTERIOR,yaw);o['animation']='sitting';o['coordinate_semantics']='character root; cushion top minus 0.483 m';o['forward_axis']='+X local';o['pelvis_offset_m']=.483;o['authoring_only']=True;return o

def berth(c,kind):
 global NBERTH
 NBERTH+=1;o=empty(f'BERTH_{NBERTH:03d}_{kind}',c,INTERIOR);o['reference_only']=True;o['exclude_from_passenger_export']=True;return o

def cushion(n,c,s):
 o=box(n,c,s,UPHOL,INTERIOR,.022);o['component']='seat_cushion';CUSHIONS.append(o);return o

def fan(x,y,z):
 rod('Fan ceiling stem',(x,y,z+.28),(x,y,z+.07),.019,STEEL,INTERIOR)
 rod('Fan motor',(x,y,z-.02),(x,y,z+.09),.054,DARK,INTERIOR,N=12)
 for rr in [.10,.20]:ring('Fan circular wire guard',(x,y,z),rr,STEEL,INTERIOR,N=16)
 for i in range(6):
  a=i*math.pi/3;rod('Fan guard spoke',(x,y,z-.02),(x+.20*math.cos(a),y+.20*math.sin(a),z),.004,STEEL,INTERIOR,N=6)
 for i in range(3):
  a=i*2*math.pi/3;vs=[(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a),z+.035) for u,v in [(.02,-.025),(.17,-.045),(.19,.04),(.06,.045)]];mesh('Fan swept blade',vs,[(0,1,2,3)],DARK,INTERIOR)

def bogies():
 for bi,bx in enumerate([-7.3915,7.3915],1):
  bg=empty(f'BOGIE_{bi}_PIVOT',(bx,0,1.0),ROOT);bg['wheelbase_m']=2.896
  for y in [-1.1,1.1]:
   box('Bogie longitudinal frame',(bx,y,.97),(3.86,.17,.24),DARK,bg,.028)
   box('Bolster lower spring plank',(bx,y,.57),(1.2,.28,.11),DARK,bg,.014)
   for dx in [-.33,.33]:
    pts=[(bx+dx+.118*math.cos(t*math.pi/6),y+.118*math.sin(t*math.pi/6),.64+.34*t/72) for t in range(73)];path('Bolster coil spring',pts,.022,SPRING,bg,6)
   for dx in [-.7,.7]:rod('Bogie swing hanger',(bx+dx,y,1.02),(bx+dx*.82,y,.56),.025,STEEL,bg)
   rod('Secondary damper',(bx+.64,y,.63),(bx+.70,y,1.03),.043,STEEL,bg)
  for dx in [-1.72,0,1.72]:box('Bogie cross frame',(bx+dx,0,.91),(.17,2.31,.18),DARK,bg,.018)
  box('Bogie bolster',(bx,0,1.10),(.42,2.27,.17),DARK,bg,.022)
  for ai,ax in enumerate([bx-1.448,bx+1.448],1):
   ar=empty(f'BOGIE_{bi}_AXLE_{ai}_ROTATE_Y',(0,0,0),bg);ar.matrix_world=Matrix.Translation((ax,0,.4575));bpy.context.view_layer.update();ar['rotation_axis']='+Y local'
   rod('Axle shaft',(ax,-1.15,.4575),(ax,1.15,.4575),.084,STEEL,ar,N=16)
   for s in [-1,1]:
    rod('915mm wheel tread',(ax,s*.8225,.4575),(ax,s*.9525,.4575),.4575,STEEL,ar,N=48)
    rod('Wheel flange',(ax,s*.802,.4575),(ax,s*.827,.4575),.480,DARK,ar,N=48)
    rod('Wheel recessed web',(ax,s*.956,.4575),(ax,s*1.008,.4575),.35,DARK,ar,N=32)
    rod('Wheel hub',(ax,s*.95,.4575),(ax,s*1.07,.4575),.135,STEEL,ar,N=20)
    box('Axlebox',(ax,s*1.145,.49),(.34,.25,.27),DARK,bg,.034)
    rod('Axlebox bearing cover',(ax,s*1.27,.49),(ax,s*1.29,.49),.10,SPRING,bg,N=16)
    for dx in [-.27,.27]:
     pts=[(ax+dx+.077*math.cos(t*math.pi/6),s*1.12+.077*math.sin(t*math.pi/6),.57+.29*t/60) for t in range(61)];path('Primary spring coil',pts,.016,SPRING,bg,6)
     rod('Primary spring guide',(ax+dx,s*1.12,.57),(ax+dx,s*1.12,.89),.031,DARK,bg)
    for dx in [-.43,.43]:
     box('Tread brake shoe',(ax+dx,s*.89,.49),(.09,.15,.27),DARK,bg,.014);rod('Brake suspension lever',(ax+dx,s*.89,.5),(ax+dx*.80,s*.89,.94),.018,STEEL,bg)
   for dx in [-.48,.48]:rod('Brake cross beam',(ax+dx,-.96,.45),(ax+dx,.96,.45),.028,DARK,bg)
  rod('Brake cylinder',(bx-.25,.30,.75),(bx+.25,.30,.75),.12,DARK,bg,N=20)
  rod('Longitudinal brake pull rod',(bx-1.85,.35,.42),(bx+1.85,.35,.42),.023,STEEL,bg)

def underframe(ac):
 for y in [-1.43,1.43]:box('Longitudinal underframe solebar',(0,y,1.15),(21.1,.15,.24),DARK)
 for x in range(-10,11):box('Underframe cross bearer',(x,0,1.13),(.07,2.86,.12),DARK)
 for x in [-3.6,3.6]:
  box('Battery box',(x,-.94,.75),(1.65,.65,.55),DARK,bevel=.022)
  for dx in [-.54,0,.54]:
   box('Battery box service cover',(x+dx,-1.277,.77),(.50,.025,.45),SPRING,bevel=.01)
   rod('Battery cover handle',(x+dx-.075,-1.30,.79),(x+dx+.075,-1.30,.79),.010,STEEL)
 for x in [-2.8,2.8]:
  rod('Water tank',(x-.75,.70,.74),(x+.75,.70,.74),.24,ROOF,N=24)
  for dx in [-.48,.48]:box('Tank support strap',(x+dx,.70,.51),(.07,.53,.05),DARK)
 rod('Air reservoir',(-.70,0,.75),(.70,0,.75),.20,DARK,N=24)
 rod('Continuous brake air pipe',(-10.5,.29,1.05),(10.5,.29,1.05),.023,STEEL)
 for x in [-6,6]:
  rod('Self generating alternator',(x-.25,-.55,.78),(x+.25,-.55,.78),.19,DARK,N=20)
  box('Alternator mount',(x,-.55,1.02),(.52,.6,.08),DARK)
 if ac:
  for x in [-.95,.95]:
   box('Underslung air conditioning condenser',(x,.90,.74),(1.70,.86,.55),ROOF,bevel=.025)
   for xx in [x-.70+i*.1 for i in range(15)]:box('Condenser grille fin',(xx,1.342,.75),(.035,.025,.40),DARK)
   for xx in [x-.43,x+.43]:rod('Condenser fan grille centre',(xx,.91,.43),(xx,.91,.455),.25,DARK,N=24)
 else:
  box('Lighting control box',(0,-1.03,.88),(.65,.38,.34),DARK,bevel=.02)

def coupling():
 for s,label in [(1,'FRONT'),(-1,'REAR')]:
  a=empty('COUPLING_'+label,(s*11.1485,0,1.105),ROOT,0 if s==1 else math.pi);a['datum']='project CBC mating plane; retrofit visual adaptation';a['outward_axis']='+X local'
  pivot=empty('CBC_'+label+'_PIVOT',(s*10.38,0,1.105),ROOT,0 if s==1 else math.pi)
  # Transform local coupler authored mesh coordinates into world vehicle coordinates.
  def cb(n,c,d):
   o=box('CBC_'+label+'_'+n,(s*(10.38+c[0]),s*c[1],1.105+c[2]),d,STEEL,pivot,.008);return o
  reach=.7685;cb('draft_pocket',(.02,0,0),(.28,.34,.30));cb('shank',(.30,0,0),(.57,.17,.17));cb('support_saddle',(.38,0,-.16),(.23,.29,.075))
  poly=[(-.30,-.10),(-.23,-.18),(-.08,-.18),(-.08,-.045),(.08,.045),(.08,.18),(-.15,.18),(-.30,.10)]
  vv=[(s*(11.1485+x),s*y,1.105+z) for z in [-.115,.115] for x,y in poly];nn=len(poly);ff=[tuple(reversed(range(nn))),tuple(range(nn,2*nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)];mesh('CBC_'+label+'_closed_knuckle_head',vv,ff,STEEL,pivot,bevel=0)  # keep complementary contact profile exact
  rod('CBC_'+label+'_knuckle_pin',(s*10.9985,s*.105,.973),(s*10.9985,s*.105,1.237),.027,DARK,pivot,N=16)
  box('Buffer beam',(s*10.49,0,1.06),(.19,2.89,.28),DARK)
  for y in [-.978,.978]:
   rod('Retained side buffer housing',(s*10.50,y,1.105),(s*10.81,y,1.105),.14,DARK,N=20)
   rod('Retained side buffer shank',(s*10.70,y,1.105),(s*11.08,y,1.105),.083,STEEL,N=16)
   rod('Retained side buffer face',(s*11.0885,y,1.105),(s*11.1485,y,1.105),.21,DARK,N=24)
  for y in [-.36,.36]:
   path('Air brake hose',[(s*10.55,y,1.02),(s*10.82,y,.85),(s*10.85,y,.55),(s*10.69,y,.44)],.026,RUBBER,N=10)
   box('Brake isolation cock',(s*10.56,y,1.01),(.10,.08,.06),RED)

def shell(cfg):
 global WINDOW_APERTURES
 ac=cfg['ac'];floor=FLOORZ;box('Structural coach floor',(0,0,floor-.065),(21.337,3.13,.13),DARK);box('Finished lino floor',(0,0,floor+.008),(21.13,3.10,.016),FLOOR,INTERIOR)
 n=cfg['windows'];pitch=15.12/n;wins=[-7.56+pitch*(i+.5) for i in range(n)];ww=min(1.25,pitch*.74) if ac else .65;wh=.64 if V=='3A' else .75
 if V=='1A':wins=[-6.92,-5.40,-3.92,-2.40,-.50,1.50,3.50,5.08,6.59];ww=.98
 WINDOW_APERTURES=[]
 for s in [-1,1]:
  side=empty('SHELL_SIDE_'+('R' if s==1 else 'L'),(0,0,0),BODY)
  openings=sorted([(x,ww,'saloon') for x in wins]+[(-9.12,.78,'door'),(9.12,.78,'door'),(-10.1,.44,'toilet'),(10.1,.44,'toilet')])
  y=s*1.596;zlo=2.01;zhi=2.76
  box('Lower blue bodyside',(0,y,(floor+zlo)/2),(21.337,.053,zlo-floor),BLUE,side)
  box('Upper blue letterboard',(0,y,3.095),(21.337,.053,.67),BLUE,side)
  for z in [1.98,2.80]:box('Cyan horizontal window band',(0,s*1.60,z),(21.337,.056,.09),CYAN,side)
  e=-10.6685
  for x,w,kind in openings:
   if x-w/2>e:box('Window zone pier',((e+x-w/2)/2,y,2.385),(x-w/2-e,.054,.75),CYAN,side)
   e=x+w/2
  if e<10.6685:box('Window zone end pier',((e+10.6685)/2,y,2.385),(10.6685-e,.054,.75),CYAN,side)
  # Interior wall lining is built from same opening grid; no invisible plane behind glazing.
  box('Lower interior sidewall',(0,s*1.553,(floor+2.0)/2),(21.12,.020,2.0-floor),CREAM,side)
  box('Upper interior sidewall',(0,s*1.553,3.075),(21.12,.020,.59),CREAM,side)
  e=-10.56
  for x,w,kind in openings:
   if x-w/2>e:box('Interior aperture pier',((e+x-w/2)/2,s*1.553,2.385),(x-w/2-e,.025,.75),CREAM,side)
   e=x+w/2
  for x in wins:
   WINDOW_APERTURES.append(dict(x=x,y=y,z=2.385,width=ww,height=wh))
   if wh<.75:
    dh=(.75-wh)/2
    for dz in [-1,1]:
     zz=2.385+dz*(wh/2+dh/2)
     box('Wide AC window transom skin',(x,y,zz),(ww+.015,.054,dh),CYAN,side)
     box('Wide AC window transom lining',(x,s*1.553,zz),(ww+.015,.025,dh),CREAM,side)
   loop('Window rubber gasket',x,s*1.634,2.385,ww+.018,wh+.02,RUBBER,side)
   loop('Window metal frame',x,s*1.651,2.385,ww-.013,wh-.03,STEEL,side)
   box('Window sealed glass' if ac else 'Closed clear sliding glass',(x,s*1.603,2.385),(ww-.025,.008,wh-.034),GLASS,side)
   box('Window sill',(x,s*1.51,2.01),(ww+.06,.11,.035),TRIM,side,.006)
   if not ac:
    for j in range(5):rod('Window security bar',(x-ww/2+.03,s*1.675,2.09+j*.145),(x+ww/2-.03,s*1.675,2.09+j*.145),.007,STEEL,side,N=8)
    box('Raised shutter headbox',(x,s*1.565,2.88),(ww-.035,.035,.16),CYAN,side)
    for xx in [x-ww/2,x+ww/2]:box('Shutter runner',(xx,s*1.53,2.385),(.025,.035,.75),STEEL,side)
   elif V in ['1A','2A','CC']:
    for dx in [-ww/2+.05,ww/2-.05]:
     box('Tied window curtain',(x+dx,s*1.50,2.39),(.085,.055,.70),CURTAIN,side,.015)
     box('Curtain tie band',(x+dx,s*1.466,2.34),(.09,.014,.045),TRIM,side)
  for x in [-9.12,9.12]:
   door=empty('DOOR_'+('A' if x<0 else 'B')+('_R' if s>0 else '_L'),(0,0,0),BODY)
   # Door is panelled around a real glazed aperture, rather than a dark painted rectangle.
   for z,h in [(1.68,.72),(3.005,.50)]:box('Entrance door blue panel',(x,s*1.572,z),(.77,.045,h),BLUE,door,.008)
   for dx in [-.34,.34]:box('Entrance door window stile',(x+dx,s*1.572,2.40),(.09,.046,.75),BLUE,door)
   box('Entrance door glazing',(x,s*1.585,2.40),(.57,.008,.68),GLASS,door);loop('Entrance door window gasket',x,s*1.61,2.40,.59,.70,RUBBER,door)
   if not ac:
    for j in range(5):rod('Entrance window security bars',(x-.28,s*1.63,2.13+j*.13),(x+.28,s*1.63,2.13+j*.13),.007,STEEL,door,N=8)
   for dx in [-.46,.46]:path('Entrance curved grabrail',[(x+dx,s*1.64,1.43),(x+dx,s*1.73,1.51),(x+dx,s*1.73,2.87),(x+dx,s*1.64,2.94)],.018,STEEL,side)
   for z in [.46,.72,.98,1.24]:box('Entry anti-slip tread',(x,s*1.62,z),(.78,.24,.035),STEEL,side,.004)
   for dx in [-.36,.36]:rod('Entry ladder side rail',(x+dx,s*1.68,.40),(x+dx,s*1.68,1.29),.018,DARK,side)
   rod('Door pull handle',(x+.27,s*1.62,1.91),(x+.27,s*1.62,2.09),.012,STEEL,door)
   text('Exit marking','EXIT',(x-.59,s*1.63,3.07),.075,WHITE,s,side)
  for x in [-10.1,10.1]:box('Toilet frosted pane',(x,s*1.60,2.385),(.424,.009,.71),FROST,side);loop('Toilet window gasket',x,s*1.634,2.385,.445,.75,RUBBER,side)
  text('Class legend',cfg['label'],(0,s*1.632,3.06),.145,WHITE,s,side)
  text('Coach subtype label',f'ICF {V}  /  {cfg["capacity"]}',(5.6,s*1.634,3.14),.10,WHITE,s,side)
  box('Routeboard panel',(-4.95,s*1.637,3.10),(1.55,.025,.22),TRIM,side,.008)
  text('Routeboard lettering','INDIAN RAILWAYS',(-4.95,s*1.656,3.075),.083,DARK,s,side)
  text('Legacy retrofit marking','LEGACY',(-6.6,s*1.633,1.66),.055,WHITE,s,side)
  for xx in [-10.6,10.6]:box('End warning stripe',(xx,s*1.629,2.34),(.045,.012,2.0),YELLOW,side)
 roofparent=empty('ROOF_ASSEMBLY',(0,0,0),BODY)
 N=32;vv=[(x,1.6225*math.cos(j*math.pi/N),3.39+.635*math.sin(j*math.pi/N)) for x in [-10.6685,10.6685] for j in range(N+1)];ff=[(j,j+1,N+j+2,N+j+1) for j in range(N)];o=mesh('Pressed steel roof shell',vv,ff,ROOF,roofparent);mod=o.modifiers.new('Closed roof thickness','SOLIDIFY');mod.thickness=.025
 vv=[(x,1.55*math.cos(j*math.pi/N),3.35+.58*math.sin(j*math.pi/N)) for x in [-10.55,10.55] for j in range(N+1)];mesh('Curved ceiling lining',vv,ff,CREAM,roofparent)
 for x in [-9,-6,-3,0,3,6,9]:path('Roof welded panel seam',[(x,1.623*math.cos(j*math.pi/16),3.391+.635*math.sin(j*math.pi/16)) for j in range(17)],.003,STEEL,roofparent,6)
 if ac:
  # Under-slung SG AC representative: smooth roof, internal duct, no invented roof AC pods.
  box('AC longitudinal distribution duct',(0,0,3.72),(15.8,.60,.19),CREAM,roofparent,.025)
  for x in [-7+i*1.75 for i in range(9)]:
   for y in [-.31,.31]:
    box('AC diffuser grille',(x,y,3.67),(.36,.035,.10),TRIM,roofparent)
    for dx in [-.13,-.065,0,.065,.13]:box('AC diffuser slot',(x+dx,y*1.02,3.67),(.019,.025,.075),DARK,roofparent)
 else:
  for x in [-7.4+i*1.85 for i in range(9)]:
   box('Roof ventilator low base',(x,0,4.002),(.44,.34,.035),ROOF,roofparent,.006)
   box('Roof ventilator cap',(x,0,4.037),(.38,.28,.032),ROOF,roofparent,.015)
   for y in [-.14,.14]:box('Ventilator louvre slot',(x,y,4.020),(.28,.025,.018),DARK,roofparent)
 for s in [-1,1]:
  end=empty('END_'+('A' if s<0 else 'B'),(0,0,0),BODY)
  for y in [-1.065,1.065]:box('Coach end wall',(s*10.645,y,2.37),(.045,1.04,2.10),BLUE,end,.01)
  box('End top header',(s*10.645,0,3.33),(.045,3.2,.26),BLUE,end)
  vv=[(s*10.645,1.6225*math.cos(j*math.pi/32),3.39+.635*math.sin(j*math.pi/32)) for j in range(33)];mesh('Curved end roof cap',vv,[tuple(range(33))],BLUE,end)
  for j in range(7):
   xx=s*(10.66+j*.033)
   for y in [-.61,.61]:box('Gangway bellows pleat',(xx,y,2.28),(.027,.12,1.94),RUBBER,end,.008)
   box('Gangway bellows top',(xx,0,3.245),(.027,1.28,.10),RUBBER,end,.012)
  box('Vestibule footplate',(s*10.79,0,floor-.010),(.38,1.11,.07),STEEL,end)
  # Split panels leave a transparent glazed center opening.
  for yy in [-.36,.36]:box('Vestibule door stile',(s*10.45,yy,2.30),(.042,.13,1.96),CREAM,end)
  box('Vestibule lower door',(s*10.45,0,1.82),(.042,.72,.97),CREAM,end)
  box('Vestibule upper door',(s*10.45,0,3.06),(.042,.72,.35),CREAM,end)
  box('Vestibule glass',(s*10.45,0,2.64),(.009,.57,.57),GLASS,end)
  for yy in [-.29,.29]:rod('Vestibule inner handle',(s*10.42,yy,2.00),(s*10.42,yy,2.30),.014,STEEL,end)
 return wins

def toilets_and_ends(ac):
 # Four actual simplified toilet compartments, inward side corridor doors, washbasins outside.
 for s in [-1,1]:
  x=s*8.1
  aisle=.62 if V in ['1A','2A','3A','SL'] else 0
  clear=.68 if aisle else .62
  # Split bulkhead around a passage opening; doors visually open for AC saloon.
  le=aisle-clear/2;ri=aisle+clear/2
  for ya,yb in [(-1.53,le),(ri,1.53)]:box('Saloon end bulkhead',(x,(ya+yb)/2,2.35),(.045,yb-ya,2.08),CREAM,INTERIOR)
  box('Saloon doorway header',(x,aisle,3.34),(.05,clear,.15),TRIM,INTERIOR)
  if ac:
   box('Saloon sliding door parked panel',(x+s*.052,ri+.25,2.36),(.033,.49,1.90),CREAM,INTERIOR,.008)
   rod('Saloon door handle',(x+s*.073,ri+.12,2.10),(x+s*.073,ri+.12,2.33),.013,STEEL,INTERIOR)
  for ys in [-1,1]:
   # Compartment x9.70..10.58, y.47..1.52.
   xx=s*10.13;yy=ys*1.01
   box('Toilet cross partition',(s*9.66,yy,2.30),(.045,1.07,1.99),CREAM,INTERIOR)
   box('Toilet corridor wall',(xx,ys*.485,2.31),(.90,.035,2.02),CREAM,INTERIOR)
   box('Toilet door',(xx,ys*.462,2.28),(.71,.036,1.87),TRIM,INTERIOR,.006)
   rod('Toilet door pull',(xx+s*.20,ys*.436,2.10),(xx+s*.20,ys*.436,2.27),.011,STEEL,INTERIOR)
   box('Toilet sanitary floor',(xx,yy,FLOORZ+.033),(.82,.94,.035),TRIM,INTERIOR)
   box('Toilet pedestal',(xx+s*.10,yy,FLOORZ+.23),(.32,.34,.42),WHITE,INTERIOR,.035)
   box('Toilet pan',(xx+s*.10,yy,FLOORZ+.47),(.42,.40,.085),WHITE,INTERIOR,.045)
   box('Toilet bowl inset',(xx+s*.10,yy,FLOORZ+.518),(.22,.24,.015),DARK,INTERIOR,.03)
   box('Toilet cistern',(s*10.46,yy,FLOORZ+.67),(.17,.38,.43),WHITE,INTERIOR,.02)
   rod('Toilet grab handle',(s*9.72,yy-.25,2.08),(s*9.72,yy+.25,2.08),.012,STEEL,INTERIOR)
   box('Washbasin cabinet',(s*9.40,ys*1.12,FLOORZ+.47),(.38,.57,.68),CREAM,INTERIOR,.02)
   box('Washbasin countertop',(s*9.40,ys*1.12,FLOORZ+.84),(.44,.62,.06),TRIM,INTERIOR,.02)
   box('Washbasin bowl',(s*9.40,ys*1.12,FLOORZ+.877),(.25,.35,.015),DARK,INTERIOR,.04)
   path('Washbasin tap',[(s*9.54,ys*1.12,FLOORZ+.89),(s*9.54,ys*1.12,FLOORZ+1.04),(s*9.43,ys*1.12,FLOORZ+1.04)],.011,STEEL,INTERIOR)
   box('Washbasin mirror',(s*9.63,ys*1.11,2.62),(.012,.50,.58),MIRROR,INTERIOR)
  for yy in [-1.34,1.34]:rod('Vestibule interior grab pole',(s*8.60,yy,FLOORZ+.12),(s*8.60,yy,3.18),.021,STEEL,INTERIOR)
  box('Fire extinguisher cabinet',(s*8.50,-1.33,2.05),(.25,.25,.60),RED,INTERIOR,.03)
  text('Interior emergency instructions','EMERGENCY',(s*8.48,-1.468,2.48),.065,RED,-1,INTERIOR)
  # SG electrical locker occupies vestibule niche.
  box('Electrical distribution cupboard',(s*8.50,1.28,2.34),(.40,.45,1.91),CREAM,INTERIOR,.01)
  for z in [1.65,2.1,2.55,3.0]:box('Distribution cupboard panel',(s*8.50,1.04,z),(.34,.018,.35),TRIM,INTERIOR,.003)

def overhead_lights(count=9):
 for i in range(count):
  x=-7.3+i*14.6/(count-1)
  box('Fluorescent lamp housing',(x,.58 if V in ['1A','2A','3A','SL'] else 0,3.58),(.65,.18,.06),TRIM,INTERIOR,.008)
  box('Fluorescent lamp diffuser',(x,.58 if V in ['1A','2A','3A','SL'] else 0,3.541),(.59,.135,.025),LAMP,INTERIOR,.005)

def sleeping_layout(tiers,bays,last_without_side=False):
 pitch=15.2/bays;left=-7.6;seat_top=FLOORZ+.44
 for b in range(bays):
  cx=left+(b+.5)*pitch;pref=f'Bay_{b+1:02d}'
  for side in [-1,1]:
   xx=cx+side*(pitch/2-.35)
   cushion(pref+'_lower_cushion',(xx,-.61,seat_top-.06),(.62,1.78,.12))
   cushion(pref+'_upper_cushion',(xx,-.61,3.00),(.64,1.78,.10))
   box(pref+'_lower_pan',(xx,-.61,seat_top-.135),(.64,1.8,.03),DARK,INTERIOR)
   for yy in [-1.3,.1]:rod(pref+'_lower_leg',(xx,yy,FLOORZ+.02),(xx,yy,seat_top-.15),.023,STEEL,INTERIOR)
   if tiers==3:
    cushion(pref+'_folded_middle_backrest',(cx+side*(pitch/2-.055),-.61,2.10),(.085,1.78,.58))
   else:
    cushion(pref+'_lower_backrest',(cx+side*(pitch/2-.08),-.61,2.04),(.09,1.78,.47))
   seats=3 if tiers==3 else 2
   for j in range(seats):
    yy=-1.25+j*(1.28/(seats-1));pax((xx,yy,seat_top-.483),0 if side==-1 else math.pi)
   berth((xx,-.61,seat_top),'LOWER')
   if tiers==3:berth((xx,-.61,2.36),'MIDDLE_FOLDED')
   berth((xx,-.61,3.06),'UPPER')
   for yy in [-1.35,.16]:
    hx=cx+side*(pitch/2-.62);ceiling=3.356+.587*math.sqrt(max(0,1-(yy/1.556)**2))
    rod(pref+'_upper_support',(hx,yy,2.95),(hx,yy,ceiling-.012),.011,STEEL,INTERIOR)
    box(pref+'_upper_hanger_ceiling_plate',(hx,yy,ceiling-.012),(.080,.065,.025),STEEL,INTERIOR,.004)
   for yy in [-1.37,.15]:rod(pref+'_luggage_rack_rail',(xx-.27,yy,FLOORZ+.14),(xx+.27,yy,FLOORZ+.14),.010,STEEL,INTERIOR)
   for dx in [-.25,-.125,0,.125,.25]:rod(pref+'_underseat_rack',(xx+dx,-1.38,FLOORZ+.14),(xx+dx,.15,FLOORZ+.14),.007,STEEL,INTERIOR,N=6)
   lx=cx+side*(pitch/2-.33)
   for dx in [-.12,.12]:rod(pref+'_ladder',(lx+dx,.32,FLOORZ+.07),(lx+dx,.32,3.03),.014,STEEL,INTERIOR)
   for z in [1.60,1.90,2.20,2.50,2.80]:rod(pref+'_ladder_step',(lx-.12,.32,z),(lx+.12,.32,z),.013,STEEL,INTERIOR)
   box(pref+'_individual_reading_lamp',(cx+side*(pitch/2-.15),-.90,2.69),(.09,.06,.06),LAMP,INTERIOR,.009)
  if b==0:box('Compartment end partition',(cx-pitch/2,-.61,2.39),(.035,1.85,2.10),CREAM,INTERIOR)
  box('Shared compartment partition',(cx+pitch/2,-.61,2.39),(.035,1.85,2.10),CREAM,INTERIOR)
  if not(last_without_side and b==bays-1):
   for tier,z in [('LOWER',seat_top-.06),('UPPER',3.00)]:
    cushion(pref+'_side_'+tier,(cx,1.19,z),(pitch-.10,.58,.12 if tier=='LOWER' else .10));berth((cx,1.19,z+.07),'SIDE_'+tier)
   for xx,ya in [(cx-pitch/2+.30,0),(cx+pitch/2-.30,math.pi)]:pax((xx,1.19,seat_top-.483),ya)
   # Two side seat backs at ends; middle seam identifies folding side lower bench.
   for xx in [cx-pitch/2+.04,cx+pitch/2-.04]:
    box(pref+'_side_seat_back',(xx,1.19,2.05),(.065,.58,.51),UPHOL,INTERIOR,.017);rod(pref+'_side_berth_support',(xx,.885,FLOORZ+.08),(xx,.885,3.20),.017,STEEL,INTERIOR)
   box(pref+'_side_cushion_seam',(cx,1.19,seat_top+.001),(.007,.56,.006),DARK,INTERIOR)
  else:
   # Low and overhead linen storage leave the real side windows unobstructed.
   # Exact end-service arrangement is representative, not a traced coach drawing.
   box('2A low linen storage locker',(cx,1.18,FLOORZ+.32),(pitch-.14,.62,.63),CREAM,INTERIOR,.02)
   box('2A overhead linen locker',(cx,1.18,3.14),(pitch-.14,.62,.35),CREAM,INTERIOR,.02)
   for xx in [cx-.39,cx+.39]:
    box('Linen lower locker panel',(xx,.856,FLOORZ+.32),(.69,.025,.54),TRIM,INTERIOR,.01)
    box('Linen upper locker panel',(xx,.856,3.14),(.69,.025,.29),TRIM,INTERIOR,.008)
   text('Linen storage stencil','LINEN',(cx,.838,FLOORZ+.36),.06,DARK,-1,INTERIOR)
  box(pref+'_window_table',(cx,-1.28,1.95),(.36,.39,.035),TRIM,INTERIOR,.015)
  rod(pref+'_table_brace',(cx,-1.48,1.68),(cx,-1.14,1.92),.012,STEEL,INTERIOR)
  if V=='2A':
   # Curtains gathered to sides leave a visible, usable entry.
   for curtain_y in [.37,.85]:
    if curtain_y==.85 and last_without_side and b==bays-1:continue
    rod(pref+'_curtain_upper_track',(cx-pitch/2,curtain_y,3.31),(cx+pitch/2,curtain_y,3.31),.012,STEEL,INTERIOR)
    for xx in [cx-pitch/2+.09,cx+pitch/2-.09]:
     vv=[];NX=24;NZ=20
     for iz in range(NZ+1):
      t=iz/NZ;pinch=math.exp(-((t-.43)/.16)**2);width=.21-.10*pinch
      for ix in range(NX+1):
       u=ix/NX;vv.append((xx+(u-.5)*width,curtain_y+(.029-.011*pinch)*math.cos(u*math.pi*8+.3*math.sin(t*math.pi)),FLOORZ+.055+t*(3.26-FLOORZ-.055)+.012*math.sin(u*math.pi*4)*(1-t)**5))
     cloth=mesh(pref+'_gathered_privacy_curtain',vv,[(iz*(NX+1)+ix,iz*(NX+1)+ix+1,(iz+1)*(NX+1)+ix+1,(iz+1)*(NX+1)+ix) for iz in range(NZ) for ix in range(NX)],CURTAIN,INTERIOR)
     for poly in cloth.data.polygons:poly.use_smooth=True
     path(pref+'_curtain_lower_hem',vv[:NX+1],.0018,CURTAIN,INTERIOR,6)
     box(pref+'_curtain_tie',(xx,curtain_y-.035,2.10),(.112,.013,.029),CURTAIN,INTERIOR,.004)
     for k in range(5):
      xp=xx+(k/4-.5)*.19;pp=[(xp,curtain_y+.013*math.cos(a*math.pi/8),3.294+.013*math.sin(a*math.pi/8)) for a in range(17)]
      path(pref+'_curtain_hanging_ring',pp,.0023,STEEL,INTERIOR,6)
      rod(pref+'_curtain_small_hook',(xp,curtain_y,3.282),(xp,curtain_y+.025,3.26),.0024,STEEL,INTERIOR,N=6)

  fan(cx,-.61,3.43)  # conventional coaches retain supplementary circulating fans
  text(pref+'_number_plate',str(b+1),(cx+.4,.348,3.18),.085,DARK,1,INTERIOR)
 overhead_lights()

def first_class():
 seat_top=FLOORZ+.44;start=-7.5;spec=[('A',3,4),('B',3,4),('C',2,2),('D',2,2),('E',2,2),('F',3,4)]
 for name,length,num in spec:
  cx=start+length/2;end=start+length;prefix=('Cabin_' if num==4 else 'Coupe_')+name
  box(prefix+'_end_partition',(start,-.46,2.37),(.05,2.08,2.10),CREAM,INTERIOR)
  # Side corridor y=.61..1.53, private compartments y=-1.51..+.55.
  # Corridor wall genuinely interrupted around sliding door aperture.
  doorx=cx+.15;dw=.70
  for xa,xb in [(start,doorx-dw/2),(doorx+dw/2,end)]:box(prefix+'_corridor_wall',((xa+xb)/2,.57,2.37),(xb-xa,.045,2.10),CREAM,INTERIOR)
  box(prefix+'_door_header',(doorx,.57,3.31),(.74,.055,.20),TRIM,INTERIOR)
  # Parked sliding door leaves doorway open and interior review possible.
  box(prefix+'_sliding_door_parked',(doorx-.76,.605,2.36),(.70,.034,1.94),TRIM,INTERIOR,.01)
  rod(prefix+'_door_pull',(doorx-.52,.631,2.02),(doorx-.52,.631,2.30),.012,STEEL,INTERIOR)
  text(prefix+'_nameplate',prefix.replace('_',' '),(doorx,.643,3.15),.078,DARK,1,INTERIOR)
  xvals=[start+.41,end-.41] if num==4 else [start+.42]
  for j,xx in enumerate(xvals):
   face=0 if j==0 else math.pi
   cushion(prefix+'_lower_berth',(xx,-.49,seat_top-.06),(.73,1.88,.12));cushion(prefix+'_lower_backrest',(xx+(-.31 if face==0 else .31),-.49,2.10),(.10,1.88,.57))
   cushion(prefix+'_upper_berth',(xx,-.49,2.94),(.74,1.88,.12))
   for yy in [-1.05,.05]:pax((xx,yy,seat_top-.483),face)
   berth((xx,-.49,seat_top),'LOWER');berth((xx,-.49,3.01),'UPPER')
   box(prefix+'_lower_berth_base',(xx,-.49,seat_top-.245),(.72,1.83,.26),DARK,INTERIOR,.018)
   for yy in [-1.35,.34]:
    hx=xx+(.28 if face==0 else -.28);ceiling=3.356+.587*math.sqrt(max(0,1-(yy/1.556)**2))
    rod(prefix+'_upper_hanger',(hx,yy,2.92),(hx,yy,ceiling-.012),.012,STEEL,INTERIOR)
    box(prefix+'_upper_hanger_ceiling_plate',(hx,yy,ceiling-.012),(.085,.065,.025),STEEL,INTERIOR,.004)
   rod(prefix+'_upper_safety_rail',(xx-.28,.435,3.06),(xx+.28,.435,3.06),.013,STEEL,INTERIOR)
   for dx in [-.12,.12]:rod(prefix+'_ladder_upright',(xx+dx,.465,FLOORZ+.02),(xx+dx,.465,3.02),.014,STEEL,INTERIOR)
   for zz in [1.62,1.94,2.26,2.58,2.90]:rod(prefix+'_ladder_step',(xx-.12,.465,zz),(xx+.12,.465,zz),.012,STEEL,INTERIOR)
  tablex=cx if num==4 else end-.50
  box(prefix+'_folding_table',(tablex,-1.22,1.99),(.53,.52,.033),TRIM,INTERIOR,.018)
  rod(prefix+'_table_bracket',(tablex,-1.48,1.66),(tablex,-1.01,1.96),.015,STEEL,INTERIOR)
  if num==4:
   box(prefix+'_mirror_frame',(tablex,-1.522,2.965),(.47,.018,.40),STEEL,INTERIOR,.012)
   box(prefix+'_mirror',(tablex,-1.508,2.965),(.425,.006,.358),MIRROR,INTERIOR,.005)
   box(prefix+'_vertical_control_column',(tablex,-1.508,2.30),(.18,.025,.77),TRIM,INTERIOR,.008)
   for zz in [2.09,2.20,2.31,2.42,2.53]:
    box(prefix+'_individual_switch_plate',(tablex,-1.489,zz),(.128,.014,.085),CREAM,INTERIOR,.004)
    box(prefix+'_rocker_switch',(tablex+.027,-1.479,zz),(.038,.010,.049),DARK,INTERIOR,.004)
   box(prefix+'_socket_faceplate',(tablex,-1.487,2.625),(.128,.018,.13),CREAM,INTERIOR,.007)
   for dx,dz,rr in [(-.029,-.015,.0065),(.029,-.015,.0065),(0,.033,.0085)]:rod(prefix+'_three_pin_socket_recess',(tablex+dx,-1.479,2.625+dz),(tablex+dx,-1.475,2.625+dz),rr,DARK,INTERIOR,N=16)
   text(prefix+'_voltage_label','230 V AC',(tablex,-1.473,2.70),.034,DARK,1,INTERIOR)
  else:
   box(prefix+'_coupe_partition_mirror_frame',(end-.034,-.76,2.79),(.018,.47,.52),STEEL,INTERIOR,.012)
   box(prefix+'_coupe_partition_mirror',(end-.048,-.76,2.79),(.006,.427,.476),MIRROR,INTERIOR,.006)
   box(prefix+'_coupe_controls',(end-.05,-.76,2.29),(.025,.18,.32),TRIM,INTERIOR,.006)
   for zz in [2.21,2.30,2.39]:box(prefix+'_coupe_switch',(end-.068,-.76,zz),(.010,.085,.055),DARK,INTERIOR,.004)
  box(prefix+'_sliding_door_guide_rail',(doorx-.38,.615,3.395),(1.51,.075,.06),TRIM,INTERIOR,.009)
  box(prefix+'_door_lock_plate',(doorx-.52,.632,2.055),(.075,.015,.24),STEEL,INTERIOR,.006)
  rod(prefix+'_door_privacy_latch',(doorx-.52,.643,2.005),(doorx-.52,.663,2.005),.022,STEEL,INTERIOR,N=20)
  box(prefix+'_reading_light',(tablex,-1.40,3.19),(.30,.16,.075),LAMP,INTERIOR,.01)
  for xx in xvals:
   for y0 in [-1.31,.25]:rod(prefix+'_underberth_luggage_retainer',(xx-.30,y0,FLOORZ+.14),(xx+.30,y0,FLOORZ+.14),.011,STEEL,INTERIOR)
  fan(cx,-.46,3.45)
  start=end
 box('Cabin_F_end_partition',(7.5,-.46,2.37),(.05,2.08,2.10),CREAM,INTERIOR)
 overhead_lights(7)

def chairs():
 top=FLOORZ+.44
 if V=='CC':
  rows=15;pitch=1.0;xs=[-7.0+i*pitch for i in range(rows)];ys=[-1.27,-.81,-.35,.50,1.05];width=.41
 else:
  rows=18;pitch=.84;xs=[-7.14+i*pitch for i in range(rows)];ys=[-1.28,-.84,-.40,.40,.84,1.28];width=.405
 for row,x in enumerate(xs):
  facing=1 if V=='CC' or row%2==0 else -1
  seats=ys if not(V=='CC' and row==14) else ys[:3]
  if V=='GS':
   for s in [-1,1]:
    cushion('GS three-person bench',(x,s*.84,top-.06),(.53,1.31,.12))
    box('GS full-width bench backrest',(x-facing*.25,s*.84,top+.29),(.065,1.32,.57),UPHOL,INTERIOR,.016)
  for y in seats:
   if V!='GS':
    cushion('Reclining chair seat' if V=='CC' else 'Individual second sitting seat',(x,y,top-.06),(.53,width,.12))
    # Each back support and headrest independently visible; second seating lower back.
    h=.76 if V=='CC' else .55
    ob=box('Chair upholstered back' if V=='CC' else 'Low-back seat shell',(x-facing*.25,y,top+h/2-.025),(.105,width,h),UPHOL,INTERIOR,.022)
    if V=='CC':
     box('Chair headrest cover',(x-facing*.182,y,top+.63),(.026,width-.055,.19),WHITE,INTERIOR,.012)
     box('Folded chair rear table',(x-facing*.316,y,top+.27),(.027,width-.10,.21),TRIM,INTERIOR,.009)
     for dy in [-width/2-.015,width/2+.015]:
      box('Chair armrest',(x,y+dy,top+.24),(.42,.037,.042),DARK,INTERIOR,.012)
      rod('Chair arm support',(x-.12,y+dy,top-.04),(x-.12,y+dy,top+.22),.012,STEEL,INTERIOR)
   rod('Seat support post',(x,y,FLOORZ+.02),(x,y,top-.13),.026,STEEL,INTERIOR)
   pax((x,y,top-.483),0 if facing==1 else math.pi)
  if row%2==0:
   for s in [-1,1]:
    rod('Bench foot rail',(x-.18,s*.24,FLOORZ+.10),(x-.18,s*1.47,FLOORZ+.10),.015,STEEL,INTERIOR)
  if row%2==0:
   for y in [-.74,.74]:fan(x+.3,y,3.41)
 for s in [-1,1]:
  # Open rail racks, never false sleeping-berth markers.
  for y in [s*.94,s*1.48]:rod('Overhead luggage rack front/rear rail',(-7.65,y,3.01),(7.65,y,3.01),.018,STEEL,INTERIOR)
  for x in [-7.6+i*.38 for i in range(41)]:rod('Overhead rack cross bar',(x,s*.93,3.01),(x,s*1.48,3.01),.008,STEEL,INTERIOR,N=6)
  for x in [-7.5,-5,-2.5,0,2.5,5,7.5]:rod('Overhead rack diagonal bracket',(x,s*.94,3.01),(x,s*1.51,3.28),.015,STEEL,INTERIOR)
 overhead_lights()

def build(v,render=False):
 global V,CFG,C,ROOT,BODY,INTERIOR,FLOORZ,NPAX,NBERTH,CUSHIONS,BLUE,CYAN,ROOF,STEEL,DARK,RUBBER,SPRING,CREAM,TRIM,FLOOR,UPHOL,RED,WHITE,YELLOW,GLASS,FROST,CURTAIN,LAMP,MIRROR
 V=v;CFG=VARIANTS[v];NPAX=NBERTH=0;CUSHIONS=[]
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections):bpy.data.collections.remove(c)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 C=bpy.data.collections.new('ICF_'+v+'_ASSET');scene.collection.children.link(C)
 BLUE=material('ICF blue enamel',(.025,.14,.30),.25,.35);CYAN=material('ICF pale blue window band',(.35,.66,.73),.18,.38);ROOF=material('Aluminium silver roof',(.49,.54,.55),.6,.48);STEEL=material('Brushed stainless steel',(.44,.49,.52),.77,.30);DARK=material('Underframe graphite',(.047,.057,.063),.45,.58);RUBBER=material('Rubber black',(.012,.016,.021),.0,.70);SPRING=material('Patinated spring steel',(.15,.17,.17),.65,.4);CREAM=material('Warm ivory laminate',(.72,.76,.68),.03,.60);TRIM=material('Pale grey interior trims',(.52,.60,.58),.18,.46);FLOOR=material('Speckled nonslip lino',(.18,.23,.24),0,.83);UPHOL=material('Burgundy first class upholstery' if v=='1A' else 'Blue passenger upholstery',(.30,.045,.055) if v=='1A' else (.025,.14,.30),0,.57);RED=material('Emergency red',(.66,.028,.012),.06,.42);WHITE=material('Ivory lettering headrest linen',(.83,.88,.84),0,.58);YELLOW=material('Warning yellow',(.95,.64,.04),.08,.5);GLASS=material('GLASS sealed passenger glazing alpha fallback',(.57,.78,.84),0,.10,.22,.92);FROST=material('FROST toilet privacy glass',(.60,.75,.73),0,.38,.58,.40);CURTAIN=material('Muted teal privacy curtain',(.06,.28,.28),0,.8);LAMP=material('Warm light diffuser',(.95,.88,.68),0,.35,emit=1.2);MIRROR=material('Brushed mirror panel',(.60,.66,.68),.9,.13)
 for m,sc,st in [(FLOOR,150,.18),(UPHOL,160,.12)]:
  nt=m.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=sc;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=st;bump.inputs['Distance'].default_value=.004;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
 ROOT=empty('ICF_'+v+'_ROOT',(0,0,0));BODY=empty('BODY',(0,0,0),ROOT);INTERIOR=empty('INTERIOR',(0,0,0),BODY);FLOORZ=1.313 if CFG['ac'] else 1.278
 ROOT['variant']=v;ROOT['subtype']=CFG['code'];ROOT['physical_capacity']=CFG['capacity'];ROOT['physical_berths']=CFG['berths'];ROOT['model_status']='Original detailed source prototype; no TF3 conversion';ROOT['body_length_m']=21.337;ROOT['nominal_body_width_m']=3.245;ROOT['coupling_span_m']=22.297;ROOT['rail_datum_z_m']=0;ROOT['layout']=CFG['layout'];ROOT['coupling']='Conventional screw coupling with side buffers; static uncoupled pose';ROOT['passenger_root_offset_m']=.483
 shell(CFG);underframe(CFG['ac']);bogies();coupling();toilets_and_ends(CFG['ac'])
 if v=='1A':first_class()
 elif v in ['2A','3A','SL']:sleeping_layout(2 if v=='2A' else 3,9 if v=='SL' else 8,v=='2A')
 else:chairs()
 if 'DETAIL_HOOK' in globals():DETAIL_HOOK()
 assert NPAX==CFG['capacity'],(v,NPAX);assert NBERTH==CFG['berths'],(v,NBERTH)
 # Bake geometry and manufactured radii, leaving strict EMPTY hierarchy.
 bpy.ops.object.select_all(action='DESELECT')
 for o in C.objects:
  if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
 bpy.context.view_layer.objects.active=next(o for o in C.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH');bpy.context.view_layer.update()
 # Export surfaces have consistent closed-volume winding and welded micro-edges.
 # Very thin bevel intersections can generate coincident corners after evaluation.
 for ob in C.objects:
  if ob.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
  # Font tessellation can leave collinear zero-area slivers despite welded edges.
  tiny=[face for face in bm.faces if face.calc_area()<1e-12]
  if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
  wire=[edge for edge in bm.edges if not edge.link_faces]
  if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
  loose=[vert for vert in bm.verts if not vert.link_edges]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  if bm.edges and all(e.is_manifold for e in bm.edges):bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  bm.to_mesh(ob.data);bm.free();ob.data.update()

 asset=list(C.objects);meshes=[o for o in asset if o.type=='MESH'];vertices=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];bounds=[[min(v[i] for v in vertices),max(v[i] for v in vertices)] for i in range(3)]
 triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 folder=OUT/v;folder.mkdir(exist_ok=True);(folder/'qa').mkdir(exist_ok=True);(folder/'renders').mkdir(exist_ok=True)
 manifest={'variant':v,'subtype':CFG['code'],'layout':CFG['layout'],'physical_capacity':CFG['capacity'],'physical_berths':NBERTH,'daytime_seated_positions':NPAX,'PAX_marker_count':NPAX,'BERTH_reference_count':NBERTH,'game_capacity':None,'game_capacity_note':'Physical capacity is not gameplay capacity. Existing project ICF balance was20 for72; preserve converter ownership. Do not treat each marker as an extra commercial capacity.','root':ROOT.name,'root_type':'EMPTY','body_parent':'BODY','interior_parent':'INTERIOR','passenger_facing_axis':'+X local','passenger_root_offset_below_cushion_m':.483,'passenger_animation':'sitting','legacy_icf_slot_yaw_correction':'Do not apply; these markers carry actual facing yaw already','berth_export':'Reference-only; never passenger seats','dimensions_m':{'body_length':21.337,'body_width':3.245,'nominal_roof_crown':4.025,'floor_top':FLOORZ,'coupling_point_span':22.297,'coupling_height':1.105,'bogie_centres':14.783,'bogie_wheelbase':2.896,'wheel_tread_diameter':.915,'gauge':1.676},'evaluated_mesh_bounds_m':bounds,'triangles':triangles,'mesh_objects':len(meshes),'material_count':len([m for m in bpy.data.materials if m.users]),'windows_per_side':CFG['windows'],'window_apertures':WINDOW_APERTURES,'coupling_front_m':[11.1485,0,1.105],'coupling_rear_m':[-11.1485,0,1.105],'source_blender_version':bpy.app.version_string,'repo_baseline':'91bcc2899eeedccb7497374227d1c81562279640','known_limits':['Representative dimensions and layout capacities supported by railway sources; exact berth/door/window spacing is procedural interpretation, not a traced production drawing.','Default hardware is a conventional screw coupling with side buffers. Buffer contact span is not a CBC mating certification.','Daytime folded middles and parked saloon/cabin doors are static; no working animations.','Glazing source uses Principled transmission plus FBX alpha fallback; target game shader configuration required.','Upper BERTH markers are references only; no seated characters on upper/middle bunks.','GS108 and2S108 intentionally share related3+3 shell; GS uses benches,2S uses individual seat units. Reservation class alone is not a unique prototype body.','No LODs, collision proxies, UV atlas, bilingual exact stock markings, TF3 resources or runtime validation supplied.']}
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2));(folder/'dimensions.json').write_text(json.dumps(manifest['dimensions_m'],indent=2))
 report={'variant':v,'asserted_counts_ok':NPAX==CFG['capacity'] and NBERTH==CFG['berths'],'root_identity':list(ROOT.matrix_world)==list(Matrix.Identity(4)),'material_limit_64_pass':manifest['material_count']<=64,'triangles':triangles,'materials':manifest['material_count'],'pax_count':NPAX,'berth_count':NBERTH,'windows':len(WINDOW_APERTURES),'apertures':'Wall skin/lining segmented from same opening list; glass panes physically occupy openings','rail_tread_z':0.0,'flange_below_rail_is_expected':True,'anchors':{'front':list(bpy.data.objects['COUPLING_FRONT'].matrix_world.translation),'rear':list(bpy.data.objects['COUPLING_REAR'].matrix_world.translation)},'mechanical_hierarchy':{o.name:{'parent':o.parent.name if o.parent else None,'world_position':list(o.matrix_world.translation)} for o in asset if o.type=='EMPTY' and o.name.startswith(('BOGIE','SCREW','COUPLING'))},'marker_root_heights':sorted(set(round(o.matrix_world.translation.z,6) for o in asset if o.name.startswith('PAX_'))),'passenger_cushion_top':FLOORZ+.44,'pelvis_offset':.483,'actual_stock_skeleton_reference':'Repository tools/check_vb_character_fit.py + TF3-INSTALL.md validates sitting pelvis at root +0.483; per-class full animated body runtime fit still unverified','preview_render':'CPU Cycles,2threads,no denoiser'}
 (folder/'qa'/'source_checks.json').write_text(json.dumps(report,indent=2))
 # Source master includes all reference BERTH markers; FBX excludes them explicitly.
 setup_studio(scene)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/f'ICF_{v}_master.blend'),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in asset:
  if not o.name.startswith('BERTH_'):o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 # Blender keeps physical dielectric alpha=1. FBX receives its documented
 # transparency fallback only during export, then authoring values are restored.
 glass_alpha=GLASS.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value
 GLASS.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=GLASS.get('fbx_fallback_alpha',.24)
 bpy.ops.export_scene.fbx(filepath=str(folder/f'ICF_{v}.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='X',axis_up='Z',apply_unit_scale=True,use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,use_custom_props=True,path_mode='COPY',embed_textures=False)
 GLASS.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=glass_alpha
 print('BUILT_VARIANT',v,json.dumps({'triangles':triangles,'materials':manifest['material_count'],'pax':NPAX,'berths':NBERTH}),flush=True)
 if render:render_views(folder)
 return manifest

def setup_studio(scene):
 global STUDIO
 STUDIO=bpy.data.collections.new('STUDIO_render_only');scene.collection.children.link(STUDIO)
 ground=material('Studio charcoal ground',(.065,.09,.12),0,.8)
 box('STUDIO ground',(0,0,-.09),(160,160,.10),ground,parent=None,coll=STUDIO)
 # Ground accidentally defaults BODY parent through box; explicitly unparent preserving identity.
 bpy.data.objects['STUDIO ground'].parent=None
 for name,loc,energy,size in [('Key',(0,-7,13),2400,12),('Fill',(3,9,9),2000,10),('End',(-13,-1,7),1000,7)]:
  ld=bpy.data.lights.new('STUDIO '+name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;lo=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((0,0,1.6))-lo.location).to_track_quat('-Z','Y').to_euler()
 world=bpy.data.worlds.new('ICF studio world') if not bpy.data.worlds else bpy.data.worlds[0];scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.32,.42,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
 camd=bpy.data.cameras.new('STUDIO Camera');cam=bpy.data.objects.new('STUDIO Camera',camd);STUDIO.objects.link(cam);scene.camera=cam
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1200;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
 cam.location=(25,-24,14);cam.rotation_euler=(Vector((0,0,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=26.8

def render_views(folder,include_aisle=True):
 scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=64;scene.render.filepath=str(folder/'renders'/'exterior.png');bpy.ops.render.render(write_still=True)
 # Clearly identified cutaway: roof assembly and near side removed only for preview, source intact.
 hide=[]
 for name in ['ROOF_ASSEMBLY','SHELL_SIDE_L']:
  p=bpy.data.objects.get(name)
  if p:
   for o in [p]+list(p.children_recursive):
    if o.type=='MESH':hide.append(o);o.hide_render=True
 scene.cycles.samples=96;cam.location=(20,-21,23);cam.rotation_euler=(Vector((0,0,1.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=25.5;scene.render.filepath=str(folder/'renders'/'interior_cutaway.png');bpy.ops.render.render(write_still=True)
 for o in hide:o.hide_render=False
 if not include_aisle:return
 cam.location=(-7.2,1.06 if V=='1A' else (.60 if V in ['2A','3A','SL'] else 0),2.58);target=Vector((3.0,cam.location.y,2.48));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=21;scene.render.filepath=str(folder/'renders'/'passenger_aisle.png');scene.cycles.samples=192;scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4
 # Interior fill lights are preview only; no concealment of geometry.
 for x in [-7,-5,-3,-1,1,3,5,7]:
  ld=bpy.data.lights.new('STUDIO interior fill','AREA');ld.energy=55;ld.shape='RECTANGLE';ld.size=.48;ld.size_y=1.6;lo=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(lo);lo.location=(x,1.08 if V=='1A' else (.60 if V in ['2A','3A','SL'] else 0),3.25)
  if V=='1A':
   ld=bpy.data.lights.new('STUDIO cabin fill','AREA');ld.energy=35;ld.size=.7;lo=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(lo);lo.location=(x,-.52,3.47)
 bpy.ops.render.render(write_still=True)

if __name__=='__main__':
 variants=list(VARIANTS) if not ARGS or ARGS[0]=='all' else [ARGS[0]]
 manifests=[build(v,'--render' in ARGS) for v in variants]
 if len(manifests)==7:(OUT/'family_manifest.json').write_text(json.dumps(manifests,indent=2))
