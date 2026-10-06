"""39002 photo-led exterior hardware. All meshes separate editable components.
Small unresolvable hardware is representative class-level construction, not claimed drawings."""
import bpy, math, random
from mathutils import Vector, Matrix
from math import pi, sin, cos
import common as C

def apply(context=None):
 context=context or {};M=context['materials'];B=bpy.data.objects['BODY'];col=C.collection('V02_EXTERIOR_DETAILS');pre='V02_EXT_'
 C.remove_prefix(pre)
 F=float(context.get('body_width_factor',1.0));mode='front'
 def mapped(n,c):
  x,y,z=c
  if mode!='front' or n.startswith(('roof ','horn ','pneumatic horn')):return (x,y,z)
  if 'headlight' in n and not any(k in n for k in ['mount gasket','service plate','headlight plate']):anchor=math.copysign(.139,y) if abs(y)>1e-8 else 0
  elif 'marker' in n:anchor=math.copysign(1.019,y)
  elif any(k in n for k in ['jumper','power receptacle','receptacle flange']):anchor=math.copysign(.535,y)
  else:anchor=y
  return (x,y+anchor*(F-1),z)
 def mesh(n,v,f,m='iron',parent=B,b=0,smooth=False):
  vv=[(x,y*F,z) for x,y,z in v] if mode=='front' else v
  return C.mesh(pre+n,vv,f,M[m],parent,col,b,smooth)
 def box(n,c,d,m='iron',parent=B,b=.003):
  if mode=='front' and abs(c[1])<1e-6 and d[1]>.3 and not n.startswith(('roof ','horn ')):d=(d[0],d[1]*F,d[2])
  return C.box(pre+n,mapped(n,c),d,M[m],parent,col,b)
 def cyl(n,c,r,d,m='iron',parent=B,axis='Z',N=40,b=0):return C.cyl(pre+n,mapped(n,c),r,d,M[m],parent,col,axis,N,b)
 def rod(n,a,b,r,m='iron',parent=B,N=12):return C.rod(pre+n,mapped(n,a),mapped(n,b),r,M[m],parent,col,N)
 def tube(n,p,r,m='iron',parent=B,N=12):return C.tube(pre+n,[mapped(n,q) for q in p],r,M[m],parent,col,N)
 def ring(n,c,ro,ri,d,m='steel',parent=B,axis='X',N=48):return C.ring(pre+n,mapped(n,c),ro,ri,d,M[m],parent,col,axis,N)
 def bolt(n,c,r=.009,d=.009,m='steel',parent=B,axis='X'):return C.bolt(pre+n,mapped(n,c),r,d,M[m],parent,col,axis)
 def beam(n,a,b,w,h,m='iron',parent=B):return C.beam(pre+n,mapped(n,a),mapped(n,b),w,h,M[m],parent,col)
 def lathe(n,c,p,m='iron',parent=B,axis='X',N=64):return C.lathe(pre+n,mapped(n,c),p,M[m],parent,col,axis,N)
 def screw(n,c,r=.006,axis='X'):return C.slotted_screw(pre+n,mapped(n,c),r,M['steel'],M['blackpaint'],B,col,axis)
 def fx(z):return 9.52-max(z-2.35,0)*.35/1.2
 def faceband(n,e,y,z,w,h,r,band,offset,depth,mat):
  # Hollow compound sealing extrusion follows the sloped front; never opaque aperture filler.
  loops=[]
  for ww,hh,rr,dd in [(w,h,r,0),(w,h,r,depth),(w-2*band,h-2*band,max(.008,r-band),depth),(w-2*band,h-2*band,max(.008,r-band),0)]:
   pts=C.rounded_rect(ww,hh,rr);loops.append([(e*(fx(z+zz)+offset+dd),y+yy,z+zz) for yy,zz in pts])
  N=len(loops[0]);vs=sum(loops,[]);fs=[]
  for k in range(4):
   for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
  return mesh(n,vs,fs,mat,b=.0012)
 C.hide_prefix(['Rounded windshield protection cage','Fine windshield guard bar','Guard horizontal frame','Cage mounting hinge','Cage mounting bolt','Wiper swept arm','Wiper rubber blade','Wiper spindle','Windscreen rubber seal','Front windscreen glass','Headlight bezel','Headlight glass','Twin headlight recess','Headlight polished inner ring','Headlight reflector','Halogen bulb cap','Headlight lens refractive rib','Marker lamps','Marker lamp circular bezel','Marker lens','HOG flexible jumper','Jumper socket','Jumper corrugated sleeve','Nose bent grab rail','Front grabrail bracket','Horn flared bell','Horn mouth','Horn trumpet stem','Cab central roof lamp','Cab roof lamp'])
 for e in [-1,1]:
  # Glazing: 6 mm laminated panel, deep black gasket, metal retainer and fine external lock strip.
  for s in [-1,1]:
   y=s*.618;z=3.015
   faceband('windscreen EPDM channel',e,y,z,1.013,.942,.049,.031,.024,.014,'rubber')
   faceband('windscreen gasket locking bead',e,y,z,1.001,.930,.046,.006,.040,.005,'blackpaint')
   pts=C.rounded_rect(.953,.877,.027,N=10);N=len(pts);vs=[]
   for dx in [.015,.021]:vs += [(e*(fx(z+zz)+dx),y+yy,z+zz) for yy,zz in pts]
   fs=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
   pane=mesh('laminated windscreen pane',vs,fs,'glass',smooth=False)
   import materials
   materials.assign_windscreen_service(pane,M['windscreen'])
   # One bent tube perimeter plus real fine welded rod screen, spaced from glass.
   pts=[(e*(fx(z+zz)+.087),y+yy,z+zz) for yy,zz in C.rounded_rect(1.080,.937,.078,N=12)];pts.append(pts[0]);tube('windscreen guard perimeter',pts,.0105,'blackpaint',N=16)
   for j in range(16):
    yy=y-.461+j*.06147
    rod('windscreen welded vertical wire',(e*(fx(2.620)+.086),yy,2.620),(e*(fx(3.410)+.086),yy,3.410),.0042,'blackpaint',N=10)
   for zz in [2.624,2.674,3.355,3.408]:
    rod('windscreen horizontal wire',(e*(fx(zz)+.089),y-.500,zz),(e*(fx(zz)+.089),y+.500,zz),.0055,'blackpaint')
   # Returns show the cage is a welded steel screen rather than flat bars pasted on glass.
   for yy in [y-.489,y+.489]:
    for zz in [2.676,3.35]:
     rod('guard standoff',(e*(fx(zz)+.028),yy,zz),(e*(fx(zz)+.089),yy,zz),.010,'blackpaint')
   for yy in [y-.545,y+.545]:
    for zz in [2.70,3.33]:
     box('guard mounting lug',(e*(fx(zz)+.048),yy,zz),(.022,.037,.065),'iron',b=.004)
     bolt('guard hinge rivet',(e*(fx(zz)+.063),yy,zz),.010,.007,'steel')
   # Pantograph-type wiper joint detail, rubber blade and separate spring-loaded arm.
   yy=y+s*.18;z0=2.540;xx=e*(fx(z0)+.039)
   ring('wiper spindle gasket',(xx,yy,z0),.028,.012,.009,'rubber')
   cyl('wiper spindle stem',(xx+e*.014,yy,z0),.012,.032,'steel',axis='X')
   bolt('wiper spindle retaining nut',(xx+e*.033,yy,z0),.018,.012,'blackpaint')
   p0=(e*(fx(2.57)+.052),yy,2.57);p1=(e*(fx(2.90)+.052),y-s*.03,2.90)
   beam('wiper pressed steel arm',p0,p1,.018,.008,'blackpaint')
   rod('wiper tension return spring',(e*(fx(2.65)+.055),y+s*.11,2.65),(e*(fx(2.81)+.055),y+s*.003,2.81),.006,'steel')
   bl0=(e*(fx(2.78)+.057),y-s*.035,2.78);bl1=(e*(fx(3.25)+.057),y-s*.12,3.25)
   beam('wiper blade rubber edge',bl0,bl1,.015,.006,'rubber')
   beam('wiper blade articulated metal spine',tuple(Vector(bl0)+Vector((e*.004,0,0))),tuple(Vector(bl1)+Vector((e*.004,0,0))),.009,.006,'blackpaint')
   for zz in [2.86,3.00,3.16]:
    cyl('wiper blade pivot',(e*(fx(zz)+.064),y-s*(.035+(.12-.035)*(zz-2.78)/.47),zz),.006,.013,'steel',axis='X',N=16)
   C.sphere(pre+'washer jet body',mapped('washer jet body',(e*9.506,y+s*.30,2.49)),.013,M['blackpaint'],B,col,N=20,R=10,scale=(.7,1,.7))
   rod('washer jet feed',(e*9.491,y+s*.3,2.49),(e*9.479,y+s*.30,2.53),.003,'rubber',N=8)
  # Cream twin-headlight service plate, edge lip, screws, deep actual reflector cups.
  box('headlight mount gasket',(e*9.539,0,1.99),(.019,.575,.365),'rubber',b=.011)
  box('headlight pressed service plate',(e*9.554,0,1.99),(.014,.565,.355),'cream',b=.009)
  for yy in [-.25,.25]:
   for zz in [1.846,2.134]:screw('headlight plate', (e*9.565,yy,zz),.009)
  for y in [-.139,.139]:
   # reflector bowls are nested concave shells with real chrome interior and filament.
   prof=[(-.015,.045),(-.012,.068),(.000,.089),(.018,.110),(.048,.119),(.055,.121),(.060,.116),(.047,.112),(.020,.101),(.001,.080),(-.008,.046),(-.015,.045)]
   lathe('headlight spun metal housing',(e*9.61,y,1.99),[(e*a,r) for a,r in prof],'blackpaint')
   lathe('headlight silver reflector',(e*9.607,y,1.99),[(e*a,r) for a,r in [(-.038,.009),(-.034,.021),(-.024,.045),(-.010,.068),(.015,.097),(.038,.109)]],'bright')
   ring('headlight clear lens gasket',(e*9.657,y,1.99),.116,.109,.012,'rubber')
   ring('headlight polished retaining bezel',(e*9.670,y,1.99),.124,.113,.014,'steel')
   # slightly convex glass prism. Outer path returns through thin rear plane for real refraction.
   prof=[(-.003,0),(-.003,.110),(.001,.110),(.004,.09),(.006,.045),(.007,0)]
   lathe('headlight convex glass cover',(e*9.672,y,1.99),[(e*a,r) for a,r in prof],'lens')
   cyl('headlight bulb base',(e*9.585,y,1.99),.013,.018,'steel',axis='X',N=24)
   C.sphere(pre+'headlight quartz bulb',mapped('headlight quartz bulb',(e*9.603,y,1.99)),.014,M['lens'],B,col,24,12,scale=(1.5,.65,.65))
   rod('headlight filament',(e*9.608,y-.003,1.99),(e*9.608,y+.003,1.99),.0006,'bright',N=8)
   for j in range(-8,9):
    a=j*.0115;h=math.sqrt(max(0,.105**2-a*a));rod('headlight moulded lens prism',(e*9.679,y+a,1.99-h),(e*9.679,y+a,1.99+h),.0006,'lens',N=8)
   for k in range(4):
    a=pi/4+k*pi/2;yy=y+.127*cos(a);zz=1.99+.127*sin(a)
    box('headlight bezel toggle clip',(e*9.667,yy,zz),(.025,.026,.015),'blackpaint',b=.002)
    screw('headlight clip',(e*9.682,yy,zz),.006)
  # Stacked white/ruby marker lamps on individually bolted metal plates.
  for y in [-1.019,1.019]:
   box('marker backing gasket',(e*9.540,y,2.007),(.017,.234,.376),'rubber',b=.012)
   box('marker stamped cover plate',(e*9.552,y,2.007),(.016,.222,.365),'cream',b=.009)
   for yy in [y-.087,y+.087]:
    for zz in [1.845,2.166]:screw('marker plate',(e*9.564,yy,zz),.006)
   for z,mat in [(2.088,'lens'),(1.925,'redlens')]:
    ring('marker EPDM seal',(e*9.564,y,z),.078,.063,.009,'rubber')
    lathe('marker reflector cup',(e*9.566,y,z),[(e*a,r) for a,r in [(-.008,.015),(.001,.04),(.014,.064)]],'bright')
    ring('marker chrome lock ring',(e*9.586,y,z),.075,.065,.014,'steel')
    lathe('marker convex lens',(e*9.59,y,z),[(e*a,r) for a,r in [(-.003,0),(-.003,.062),(.001,.064),(.005,.058),(.009,.037),(.010,0)]],mat)
    for j in range(-5,6):
     yy=j*.010;h=math.sqrt(max(0,.058**2-yy*yy));rod('marker lens prism',(e*9.598,y+yy,z-h),(e*9.598,y+yy,z+h),.00065,mat,N=8)
  # Continuous front handrail with proper rounded elbows and mounting feet.
  pts=C.bezier_points([(e*9.585,-1.137,1.425),(e*9.594,-1.137,2.30),(e*9.596,-1.10,2.338),(e*9.596,1.10,2.338),(e*9.594,1.137,2.30),(e*9.585,1.137,1.425)],steps=8)
  # Keep long horizontal straight rather than Catmull bulge.
  pts=[(e*9.595,-1.137,1.43),(e*9.595,-1.137,2.29)]+[(e*9.595,-1.09-.047*cos(a),2.29+.047*sin(a)) for a in [i*pi/16 for i in range(9)]]+[(e*9.595,1.09,2.337)]+[(e*9.595,1.09+.047*sin(a),2.29+.047*cos(a)) for a in [i*pi/16 for i in range(9)]]+[(e*9.595,1.137,1.43)]
  tube('front safety handrail',pts,.0125,'blackpaint',N=16)
  for yy in [-1.137,1.137]:
   for z in [1.46,2.28]:
    box('front handrail mounting tab',(e*9.551,yy,z),(.012,.044,.061),'cream',b=.002)
    rod('front handrail stand-off',(e*9.558,yy,z),(e*9.596,yy,z),.009,'blackpaint')
    bolt('front handrail mount',(e*9.566,yy,z+.021),.006,.006,'steel')
  # Front low-voltage MU/HOG sockets under lamp plate, separate coloured hinged caps.
  for yy,mat in [(-.052,'green'),(.052,'cream')]:
   box('MU control socket mounting',(e*9.556,yy,1.730),(.022,.081,.121),'blackpaint',b=.009)
   box('MU sprung protective cap',(e*9.578,yy,1.737),(.019,.073,.112),mat,b=.009)
   cyl('MU cap hinge barrel',(e*9.58,yy,1.795),.012,.085,'steel',axis='Y',N=24)
   box('MU cap finger lip',(e*9.591,yy,1.683),(.012,.034,.012),'iron',b=.002)
  # Main two heavy jumper receptacles tilted down on robust plate brackets.
  for s in [-1,1]:
   y=s*.535
   box('power receptacle rear flange',(e*9.556,y,1.515),(.036,.272,.228),'iron',b=.010)
   for yy in [y-.108,y+.108]:
    for z in [1.426,1.602]:bolt('receptacle flange fixing',(e*9.581,yy,z),.011,.010,'steel')
   # The casting is a sloping octagonal housing, not a generic cube.
   p0=Vector((e*9.600,y,1.527));p1=Vector((e*9.732,y,1.425));axis=(p1-p0).normalized()
   for rr,ll,mm,cc in [(.090,.17,'iron',(p0+p1)/2),(.097,.020,'blackpaint',p1),(.079,.022,'iron',p1+axis*.014)]:
    # General cylinder along vector constructed through lathe and quaternion.
    pr=[(-ll/2,0),(-ll/2,rr),(ll/2,rr),(ll/2,0)];o=C.lathe(pre+'jumper cast receptacle', (0,0,0),pr,M[mm],None,col,'Z',40);q=axis.to_track_quat('Z','Y');o.matrix_world=Matrix.Translation(Vector(mapped('jumper cast receptacle',cc)))@q.to_matrix().to_4x4();o.parent=B;o.matrix_parent_inverse=B.matrix_world.inverted()
   # Curved plug cover hood, retaining hinge and hooked latch.
   box('jumper top hinge block',(e*9.654,y,1.614),(.058,.18,.035),'iron',b=.008)
   cyl('jumper hinge pin',(e*9.655,y,1.625),.012,.216,'steel',axis='Y',N=24)
   for yy in [y-.093,y+.093]:ring('jumper hinge bearing',(e*9.655,yy,1.625),.023,.014,.027,'iron',axis='Y',N=32)
   tube('jumper locking bail',C.bezier_points([(e*9.63,y-.072,1.57),(e*9.76,y-.072,1.46),(e*9.773,y+.072,1.445),(e*9.63,y+.072,1.57)],8),.008,'steel')
   # Photo-visible rectangular ladder support directly below socket.
   for yy in [y-.115,y+.115]:beam('jumper bracket vertical',(e*9.597,yy,1.477),(e*9.716,yy,1.214),.025,.028,'iron')
   for z in [1.235,1.317,1.40]:
    xx=9.70-(z-1.235)*.38;box('jumper bracket crosspiece',(e*xx,y,z),(.045,.262,.028),'iron',b=.004)
   # Heavy electrical cable curved all the way to the pilot return, with rigid collar at plug.
   points=[tuple(p1+axis*.04),(e*9.80,y*1.03,1.18),(e*9.84,y*.98,.84),(e*9.73,y*.83,.52),(e*9.49,y*.60,.49),(e*9.40,y*.53,.73)]
   tube('jumper cable flexible rubber',C.bezier_points(points,12),.030,'rubber',N=18)
   for k in range(7):
    cc=p1+axis*(.04+k*.010);o=ring('jumper plug strain relief',cc,.036,.027,.006,'blackpaint',axis='Z',N=28);# rings aligned to actual tilted plug
    # World mesh generated at cc; rotate about own center from Z to hose axis.
    q=axis.to_track_quat('Z','Y');T=Matrix.Translation(cc)@q.to_matrix().to_4x4()@Matrix.Translation(-cc)
    for v in o.data.vertices:v.co=T@v.co
  # Small nose hose tap, backnut and tether beside right-hand marker.
  y=.756
  cyl('nose fitting backnut',(e*9.548,y,1.875),.017,.021,'brass',axis='X',N=6)
  rod('nose vent pipe',(e*9.566,y,1.875),(e*9.60,y,1.914),.010,'brass')
  box('nose vent stop handle',(e*9.605,y,1.917),(.039,.015,.009),'blackpaint',b=.002)
  # Central roof searchlight: painted mounting pedestal, narrow housing, optics inside.
  box('roof searchlight upright pedestal',(e*8.575,0,3.994),(.18,.22,.25),'cream',b=.009)
  box('roof searchlight body',(e*8.60,0,4.157),(.22,.241,.187),'roof',b=.013)
  box('roof searchlight face recess',(e*8.716,0,4.157),(.010,.207,.152),'rubber',b=.010)
  lathe('roof searchlight reflector',(e*8.717,0,4.157),[(e*a,r) for a,r in [(-.03,.005),(-.025,.025),(-.011,.049),(.003,.061)]],'bright')
  ring('roof searchlight bezel',(e*8.724,0,4.157),.072,.063,.009,'blackpaint')
  lathe('roof searchlight glass',(e*8.730,0,4.157),[(e*a,r) for a,r in [(-.003,0),(-.003,.061),(.001,.061),(.005,.03),(.005,0)]],'lens')
  for y in [-.093,.093]:
   for z in [4.10,4.215]:screw('roof light case',(e*8.720,y,z),.0045)
  # Two different-sized trumpet horns with actual hollow bell interiors and end plates.
  for y,r,L in [(-.56,.087,.355),(.56,.079,.310)]:
   z=4.091;x=8.47
   profile=[(-L/2,.040),(-L/2+.025,.047),(-.07,.047),(.01,.050),(.07,r*.72),(L/2,r),(L/2+.004,r),(L/2+.005,r-.006),(.075,r*.65),(.015,.042),(-.04,.020),(-.08,.008)]
   lathe('pneumatic horn hollow bell',(e*x,y,z),[(e*a,rr) for a,rr in profile],'blackpaint')
   cyl('horn diaphragm housing',(e*(x-L/2-.028),y,z),.051,.043,'roof',axis='X',N=40)
   for k in range(6):
    a=k*pi/3;bolt('horn diaphragm screw',(e*(x-L/2-.052),y+.038*cos(a),z+.038*sin(a)),.0045,.004,'steel')
   box('horn support foot',(e*(x-.07),y,3.979),(.098,.091,.02),'roof',b=.003)
   box('horn mounting strap',(e*(x-.07),y,4.022),(.047,.030,.09),'blackpaint',b=.004)
   tube('horn pneumatic air line',C.bezier_points([(e*(x-.18),y,z-.015),(e*(x-.25),y,4.045),(e*(x-.31),y*.7,4.018)],8),.005,'copper',N=10)
 mode='side'
 # Continuous livery is a micron-offset surface coating, never thick coloured boxes.
 C.hide_prefix(['Continuous red bodyside band','Continuous red stripe across cab bevel','Front red band'])
 z0,z1=1.8924,2.1876
 def stripe_quad(n,a,b):
  o=mesh(n,[(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],[(0,1,2,3)],'red');o['coating']='Conformal paint layer, not a raised panel';return o
 for side in [-1,1]:
  for a,b in [(-9.16024,-8.122),(-7.478,7.478),(8.122,9.16024)]:stripe_quad('continuous painted side belt',(a,side*1.5767),(b,side*1.5767))
  for e in [-1,1]:
   stripe_quad('painted door belt',(e*7.8-.318,side*1.5887),(e*7.8+.318,side*1.5887))
   stripe_quad('painted corner belt',(e*9.16024,side*1.5767),(e*9.5207,side*1.296343))
 for e in [-1,1]:stripe_quad('painted front belt',(e*9.5207,-1.296343),(e*9.5207,1.296343))
 # Indian flag is flush paint on the nose, including the part below the red belt.
 for o in bpy.data.objects:
  if o.type=='MESH' and o.name.startswith('National tricolour'):
   iw=o.matrix_world.inverted()
   for v in o.data.vertices:
    p=o.matrix_world@v.co;p.x=math.copysign(9.5215,p.x);v.co=iw@p
 # Photo-led crest artwork remains an original drawn approximation, now with authentic content cues.
 from pathlib import Path
 im=bpy.data.images.load(str(Path(__file__).resolve().parents[1]/'textures/v02_royapuram_crest.png'),check_existing=True);im.pack();im.filepath='//textures/v02_royapuram_crest.png'
 for mat in bpy.data.materials:
  if mat.name=='DECAL • shed_emblem.png':
   for node in mat.node_tree.nodes:
    if node.type=='TEX_IMAGE':node.image=im
 for o in list(bpy.data.objects):
  if o.name.startswith('Shed crest'):
   e=1 if sum((o.matrix_world@v.co).x for v in o.data.vertices)>0 else -1;mat=o.data.materials[0]
   verts=[];faces=[];N=24
   for j in range(N+1):
    z=2.390-.175+j*.35/N
    for i in range(N+1):verts.append((e*(fx(z)+.0008),-.175+i*.35/N,z))
   for j in range(N):
    for i in range(N):faces.append((j*(N+1)+i,j*(N+1)+i+1,(j+1)*(N+1)+i+1,(j+1)*(N+1)+i))
   if e<0:faces=[tuple(reversed(ff)) for ff in faces]
   me=bpy.data.meshes.new('Conformal painted Royapuram crest');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();o.data=me;o.matrix_parent_inverse=B.matrix_world.inverted();o.matrix_basis=Matrix.Identity(4)
   uv=me.uv_layers.new(name='Crest paint UV')
   for poly in me.polygons:
    for li in poly.loop_indices:
     v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(((v.y+.175)/.35 if e>0 else 1-(v.y+.175)/.35),(v.z-(2.390-.175))/.35)
 # Cab-side sliding frames and door glass are purpose-made seal extrusions with rounded corners.
 C.hide_prefix(['Cab side window surround','Cab side glazing','Sliding window divider','Door window seal','Door glazing','Cab door perimeter gasket'])
 def sideband(n,s,x,z,w,h,r,band,y,depth,mat):
  loops=[]
  for ww,hh,rr,dd in [(w,h,r,0),(w,h,r,depth),(w-2*band,h-2*band,max(.006,r-band),depth),(w-2*band,h-2*band,max(.006,r-band),0)]:
   loops.append([(x+xx,s*(y+dd),z+zz) for xx,zz in C.rounded_rect(ww,hh,rr,N=8)])
  N=len(loops[0]);vs=sum(loops,[]);fs=[]
  for k in range(4):
   for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
  return mesh(n,vs,fs,mat,b=.001)
 for e in [-1,1]:
  for side in [-1,1]:
   # Side window clear aperture and small independent sliding pane tracks.
   x=e*8.55;z=3.03
   sideband('side window outer fastening frame',side,x,z,.594,.842,.039,.032,1.578,.014,'blackpaint')
   sideband('side window soft glazing gasket',side,x,z,.536,.784,.028,.015,1.590,.010,'rubber')
   for xx,ww in [(x-e*.130,.247),(x+e*.128,.247)]:
    pts=C.rounded_rect(ww,.746,.014,N=8);N=len(pts);v=[]
    for yy in [1.584,1.590]:v += [(xx+dx,side*yy,z+dz) for dx,dz in pts]
    f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
    if side==1:f=[tuple(reversed(ff)) for ff in f]
    mesh('side laminated sliding glass',v,f,'glass')
   for zz in [2.656,3.404]:
    box('sliding window rail',(x,side*1.601,zz),(.514,.014,.012),'steel',b=.002)
    rod('slider weather strip',(x-.252,side*1.605,zz+.008),(x+.252,side*1.605,zz+.008),.003,'rubber',N=8)
   box('sliding pane meeting stile',(x,side*1.606,z),(.025,.025,.756),'blackpaint',b=.002)
   box('side window latch',(x-e*.017,side*1.615,2.989),(.039,.017,.051),'steel',b=.004)
   box('side window finger lip',(x-e*.03,side*1.626,3.008),(.015,.014,.028),'blackpaint',b=.002)
   for xx in [x-.276,x+.276]:
    for zz in [2.666,3.03,3.393]:screw('cab side window frame',(xx,side*1.596,zz),.005,'Y')
   # Door perimeter: a compressed seal at the leaf gap, not a wide black picture frame.
   x=e*7.80
   sideband('door compressed perimeter seal',side,x,2.570,.671,1.960,.027,.012,1.577,.015,'rubber')
   sideband('door glazing exterior seal',side,x,3.020,.433,.811,.028,.016,1.592,.016,'rubber')
   sideband('door glazing lock bead',side,x,3.020,.418,.794,.023,.004,1.609,.004,'blackpaint')
   pts=C.rounded_rect(.397,.757,.016,N=8);N=len(pts);vs=[]
   for yy in [1.588,1.594]:vs += [(x+xx,side*yy,3.020+zz) for xx,zz in pts]
   fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
   if side==1:fs=[tuple(reversed(ff)) for ff in fs]
   mesh('door laminated vision pane',vs,fs,'glass')
   # Water runs out at bottom frame drain slots, with a recessed sill lip and small rubber plugs.
   for xx in [x-.148,x+.148]:
    box('door window drainage slot',(xx,side*1.611,2.623),(.021,.003,.005),'blackpaint',b=.001)
 # Door hinge and latch manufacture: replace shapeless blocks with pin knuckles/fasteners.
 C.hide_prefix(['Door hinges','Door latch','Latch base'])
 for e in [-1,1]:
  for s in [-1,1]:
   x=e*7.80;y=s*1.593
   for z in [1.77,2.46,3.37]:
    xx=x+e*.299
    box('door hinge fixed leaf',(xx+e*.026,y,z),(.044,.009,.090),'cream',b=.002)
    box('door hinge moving leaf',(xx-e*.025,y,z),(.041,.010,.092),'cream',b=.002)
    for dz in [-.032,0,.032]:cyl('door hinge knuckle',(xx,y+s*.008,z+dz),.010,.029,'steel',axis='Z',N=24)
    cyl('door hinge vertical pin',(xx,y+s*.008,z),.004,.114,'steel',N=20)
    for dx in [-.032,.037]:
     for dz in [-.026,.026]:screw('door hinge leaf',(xx+dx,y+s*.012,z+dz),.0045,'Y')
   xx=x-e*.21;z=2.485
   box('door latch escutcheon',(xx,y,z),(.057,.015,.110),'blackpaint',b=.010)
   ring('door handle collar',(xx,y+s*.014,z+.015),.019,.009,.010,'steel',axis='Y',N=32)
   tube('door cast handle',C.bezier_points([(xx,y+s*.018,z+.014),(xx,y+s*.052,z+.014),(xx-e*.077,y+s*.057,z+.014),(xx-e*.088,y+s*.042,z+.014)],8),.008,'steel',N=14)
   cyl('door key cylinder',(xx,y+s*.010,z-.029),.010,.012,'steel',axis='Y',N=24)
   box('door key slot',(xx,y+s*.019,z-.029),(.002,.001,.009),'blackpaint',b=0)
 # Recessed entry grab rails stay inside the GA width, mounted on bolted offset feet.
 for e in [-1,1]:
  for side in [-1,1]:
   for x in [e*7.8-.377,e*7.8+.377]:
    pts=C.bezier_points([(x,side*1.588,1.59),(x,side*1.631,1.66),(x,side*1.631,3.40),(x,side*1.588,3.48)],8)
    tube('cab access bent grab rail',pts,.011,'cream',N=16)
    for z in [1.59,2.50,3.48]:
     box('entry rail foot',(x,side*1.588,z),(.045,.012,.065),'cream',b=.004)
     for dz in [-.021,.021]:bolt('entry rail fixing',(x,side*1.601,z+dz),.0055,.006,'steel',axis='Y')
 # Photo-fit narrow lower ladder starts near axle height, with a separate recessed sill tread.
 # Heights/projections are photographic estimates, not certified manufacturing dimensions.
 C.hide_prefix(['Cab access tread','Anti slip tread','Cab tread serration'])
 for e in [-1,1]:
  for side in [-1,1]:
   x=e*7.8;bogie=bpy.data.objects['BOGIE_B_YAW_Z' if e>0 else 'BOGIE_A_YAW_Z']
   for xx in [x-.221,x+.221]:
    box('lower entry ladder stile',(xx,side*1.548,.790),(.030,.018,.760),'iron',parent=bogie,b=.003)
    beam('ladder upper bracket',(xx,side*1.548,1.145),(xx,side*1.229,1.155),.031,.019,'iron',parent=bogie)
   for z in [.450,.900]:
    for xx in [x-.235,x+.235]:box('ladder tray folded end',(xx,side*1.535,z),(.003,.170,.021),'iron',parent=bogie,b=.0007)
    for yy in [1.451,1.619]:box('ladder tray folded lip',(x,side*yy,z),(.473,.003,.021),'iron',parent=bogie,b=.0007)
    box('thin chequered ladder plate',(x,side*1.535,z+.006),(.456,.164,.005),'iron',parent=bogie,b=.0007)
    verts=[];faces=[]
    for i in range(13):
     for j in range(4):
      xx=x-.210+i*.035;yy=side*(1.468+j*.044);ang=pi/4 if (i+j)%2 else -pi/4;ba=len(verts)
      for zz in [z+.0085,z+.0102]:
       for u,v in [(-.012,0),(0,-.0028),(.012,0),(0,.0028)]:verts.append((xx+u*cos(ang)-v*sin(ang),yy+u*sin(ang)+v*cos(ang),zz))
      faces.extend([tuple(ba+k for k in q) for q in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
    mesh('raised steel chequer pattern',verts,faces,'steel',parent=bogie)
    for xx in [x-.218,x+.218]:bolt('ladder rung fastening',(xx,side*1.558,z+.024),.006,.006,'steel',parent=bogie,axis='Z')
   # Upper footboard is inset into the real sill notch, with useful inboard depth.
   z=1.435
   for xx in [x-.282,x+.282]:box('sill tread folded end',(xx,side*1.466,z),(.003,.253,.022),'iron',b=.0007)
   for yy in [1.340,1.592]:box('sill tread folded lip',(x,side*yy,z),(.568,.003,.022),'iron',b=.0007)
   box('thin chequered sill footboard',(x,side*1.466,z+.006),(.550,.242,.005),'iron',b=.0007)
   verts=[];faces=[]
   for i in range(15):
    for j in range(6):
     xx=x-.248+i*.0355;yy=side*(1.359+j*.043);ang=pi/4 if (i+j)%2 else -pi/4;ba=len(verts)
     for zz in [z+.0085,z+.0102]:
      for u,v in [(-.012,0),(0,-.0028),(.012,0),(0,.0028)]:verts.append((xx+u*cos(ang)-v*sin(ang),yy+u*sin(ang)+v*cos(ang),zz))
     faces.extend([tuple(ba+k for k in q) for q in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
   mesh('raised sill chequer pattern',verts,faces,'steel')
 return {'collection':col.name,'objects':len(col.objects),'source':'RPM WAP-7 39002 photograph, photo-led representative fine hardware'}
