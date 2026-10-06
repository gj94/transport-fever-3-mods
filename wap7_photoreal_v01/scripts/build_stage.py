"""Procedural photographic railway setting. Executed in the build_refinement namespace.
All geometry is presentation-only; no external photos/HDRIs are required.
"""
earth=material('STAGE • ochre railway earth',(.095,.075,.047),0,.94,.52,.015)
concrete=material('STAGE • weathered concrete sleepers',(.26,.245,.20),0,.86,.38,.0035)
railrust=material('STAGE • oxidised rail web',(.105,.047,.022),.60,.65,.38,.0015)
railhead=material('STAGE • burnished rail crown',(.32,.33,.32),.91,.24,.12,.00015)
ballastm=[material('STAGE • granite ballast '+str(i),c,0,.91,.2,.0015) for i,c in enumerate([(.21,.20,.17),(.30,.29,.26),(.18,.18,.17),(.26,.245,.215),(.34,.31,.26),(.15,.15,.14)])]
foliagem=[material('STAGE • dry-green foliage '+str(i),c,0,.91,.35,.001) for i,c in enumerate([(.07,.10,.025),(.11,.15,.036),(.16,.18,.04),(.06,.082,.02)])]
trunkmat=material('STAGE • bark',(.068,.055,.039),0,.95,.5,.007)
box('Ground',(0,0,-.63),(500,500,.20),earth,parent=None,coll=stage,b=0)
# Ballast shoulders have a real cross-section, extending under and beyond all sleepers.
for yc in [0,5.4]:
 v=[]
 for x in range(-100,102,2):v += [(x,yc-2.24+random.uniform(-.15,.13),-.532),(x,yc-1.50+random.uniform(-.035,.035),-.273),(x,yc+1.50+random.uniform(-.035,.035),-.273),(x,yc+2.24+random.uniform(-.13,.15),-.532)]
 fs=[(i*4+j,(i+1)*4+j,(i+1)*4+j+1,i*4+j+1) for i in range(100) for j in range(3)]
 mesh('Irregular tapered ballast bank',v,fs,ballastm[0],None,stage)
 # Rails are actual tapered I sections with a separately polished running surface.
 for sy in [-1,1]:
  yy=yc+sy*.873
  profile=[(-.075,-.181),(.075,-.181),(.075,-.16),(.016,-.144),(.014,-.052),(.032,-.036),(.036,-.018),(.031,-.002),(-.031,-.002),(-.036,-.018),(-.032,-.036),(-.014,-.052),(-.016,-.144),(-.075,-.16)]
  verts=[(x,yy+y,z) for x in [-100,100] for y,z in profile];n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  rail=mesh('Continuous profiled rail',verts,faces,railrust,None,stage,bevel=.002)
  rail.data.materials.append(railhead)
  for poly in rail.data.polygons:
   if poly.center.z>-.038:poly.material_index=1
 # Individually cast tapered prestressed-concrete sleepers.
 for i in range(-115,116):
  x=i*.60
  verts=[]
  for z,L,W in [(-.33,1.36,.14),(-.19,1.28,.105)]:verts += [(x-W,yc-L,z),(x+W,yc-L,z),(x+W,yc+L,z),(x-W,yc+L,z)]
  mesh('Prestressed concrete sleeper',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete,None,stage,bevel=.018)
  if abs(x)<30:
   for s in [-1,1]:
    yy=yc+s*.873;box('Elastic rail pad',(x,yy,-.186),(.25,.23,.012),rubber,None,stage,b=.002)
    for ss in [-1,1]:
     y=yy+ss*.09;box('Rail fastening shoulder',(x,y,-.158),(.081,.054,.043),railrust,None,stage,b=.004)
     pts=[(x-.056,y+ss*.01,-.15),(x-.054,y+ss*.053,-.136),(x+.019,y+ss*.056,-.123),(x+.070,y+ss*.025,-.145),(x+.027,y-ss*.024,-.15)]
     tube('Pandrol-style spring clip',pts,.010,edge,None,stage,N=8)
# Batched angular ballast chips. Close geometry, low distant density; fixed seed.
# Every stone is an irregular triangulated octahedron, not a sphere or shader illusion.
verts=[];faces=[];midx=[]
for k in range(145000):
 x=random.uniform(-30,30);yc=random.choice([0,5.4]);y=yc+random.uniform(-2.19,2.19)
 if abs(x)>27 and random.random()<.48:continue
 z=-.265 if abs(y-yc)<1.52 else -.265-(abs(y-yc)-1.52)*.40
 if random.random()<.15:y=yc+random.choice([-1,1])*random.uniform(2.12,2.85);z=-.522
 z+=random.uniform(-.012,.034)
 r=random.uniform(.019,.042);rx=r*random.uniform(.7,1.6);ry=r*random.uniform(.7,1.4);rz=r*random.uniform(.50,.96);a=random.uniform(0,2*pi)
 base=len(verts);shape=[(-rx,0,0),(0,-ry,0),(rx,0,0),(0,ry,0),(random.uniform(-.3,.3)*rx,random.uniform(-.3,.3)*ry,rz),(0,0,-rz*.7)]
 for xx,yy,zz in shape:verts.append((x+xx*cos(a)-yy*sin(a),y+xx*sin(a)+yy*cos(a),z+zz))
 ff=[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)];faces += [tuple(base+i for i in f) for f in ff];midx += [random.randrange(len(ballastm))]*8
stones=mesh('Angular granite ballast • individual chips',verts,faces,ballastm[0],None,stage)
for m in ballastm[1:]:stones.data.materials.append(m)
for p,mi in zip(stones.data.polygons,midx):p.material_index=mi
# Occasional weeds at ballast edge, asymmetrically clumped.
vs=[];fs=[]
for k in range(1450):
 x=random.uniform(-70,70);y=random.choice([-1,1])*random.uniform(2.3,3.6);z=-.5
 if random.random()<.25:y+=5.4
 for j in range(random.randint(3,6)):
  a=random.random()*2*pi;h=random.uniform(.05,.25);w=random.uniform(.006,.012);dx=random.uniform(-.08,.08);dy=random.uniform(-.08,.08);b=len(vs)
  vs += [(x+dx-w*cos(a),y+dy-w*sin(a),z),(x+dx+w*cos(a),y+dy+w*sin(a),z),(x+dx+cos(a)*h*.4,y+dy+sin(a)*h*.4,z+h)];fs.append((b,b+1,b+2))
mesh('Scattered ballast-edge grasses',vs,fs,foliagem[2],None,stage)
# Dense, irregular distant canopy. A full layered leaf silhouette avoids floating leafcards.
leafv=[];leaff=[];leafm=[]
for k in range(43):
 x=-106+k*5.3+random.uniform(-2,2);y=random.uniform(58,72);h=random.uniform(2.5,5.8);r=random.uniform(3.1,5.1)
 rod('Distant tree trunk',(x,y,-.5),(x+.15,y,h*.72),.15,trunkmat,None,stage,N=8)
 for cl in range(11):
  cx=x+random.uniform(-r*.65,r*.65);cy=y+random.uniform(-r*.6,r*.6);cz=h*.66+random.uniform(-r*.3,r*.5);rr=random.uniform(.8,1.7)
  # Dense faceted canopy core, hidden behind peripheral leaflets, shaded as leaves.
  N=12;R=7;bv=len(leafv)
  for row in range(R+1):
   ph=pi*row/R
   for q in range(N):
    th=2*pi*q/N;rad=rr*random.uniform(.92,1.10);leafv.append((cx+rad*sin(ph)*cos(th),cy+rad*sin(ph)*sin(th),cz+rad*.8*cos(ph)))
  for row in range(R):
   for q in range(N):
    leaff.append((bv+row*N+q,bv+row*N+(q+1)%N,bv+(row+1)*N+(q+1)%N,bv+(row+1)*N+q));leafm.append(random.randrange(4))
  for j in range(90):
   theta=random.random()*2*pi;u=random.uniform(-1,1);rrr=rr*random.uniform(.85,1.2);xx=rrr*math.sqrt(1-u*u)*cos(theta);yy=rrr*math.sqrt(1-u*u)*sin(theta);zz=rrr*u*.8
   sz=random.uniform(.06,.16);b=len(leafv);leafv += [(cx+xx-sz,cy+yy,cz+zz),(cx+xx+sz,cy+yy,cz+zz),(cx+xx,cy+yy-sz*.7,cz+zz+.07),(cx+xx,cy+yy+sz*.6,cz+zz+sz*.45)];leaff += [(b,b+1,b+2),(b,b+3,b+1),(b,b+2,b+3)];leafm += [random.randrange(4)]*3
leaves=mesh('Distant dense geometric broadleaf canopy',leafv,leaff,foliagem[0],None,stage,smooth=True)
for m in foliagem[1:]:leaves.data.materials.append(m)
for p,mi in zip(leaves.data.polygons,leafm):p.material_index=mi
# Electrification at a visual 5.53 m contact plane. Pantograph pose computed by render script.
wire=material('STAGE • overhead conductor',(.095,.067,.036),.78,.46,.10)
mastmat=material('STAGE • galvanized catenary structure',(.31,.32,.29),.68,.49,.22,.0006)
for x in [-56,-20,24,66]:
 y=3.17
 box('Catenary concrete foundation',(x,y,-.18),(.65,.65,.65),concrete,None,stage,b=.02)
 # Open H-section mast, to keep silhouette convincing.
 for dx in [-.095,.095]:box('Catenary mast flange',(x+dx,y,3.6),(.020,.25,7.55),mastmat,None,stage,b=.003)
 box('Catenary mast web',(x,y,3.6),(.18,.020,7.55),mastmat,None,stage,b=.003)
 rod('Catenary cantilever boom',(x,y,6.7),(x,-.17,6.28),.031,mastmat,None,stage,N=12)
 rod('Catenary cantilever brace',(x,y,5.43),(x,.33,6.36),.024,mastmat,None,stage,N=12)
 rod('Catenary registration arm',(x,.85,5.64),(x,0,5.53),.020,mastmat,None,stage,N=10)
 for yy,zz in [(2.75,6.64),(2.58,5.65)]:
  for j in range(7):cyl('Catenary brown insulator',(x,yy-j*.047,zz),.083,.022,ceramic,None,axis='Y',N=18,coll=stage)
rod('Contact wire',(-110,0,5.53),(110,0,5.53),.0058,wire,None,stage,N=8)
# Messenger has a shallow repeating catenary sag; vertical droppers are visible silhouettes.
pts=[]
for i in range(111):
 x=-110+2*i;phase=((x+20)%44)/44;z=6.28-.28*sin(pi*phase);pts.append((x,0,z))
tube('Sagging messenger cable',pts,.006,wire,None,stage,N=8)
for x in range(-100,101,6):
 phase=((x+20)%44)/44;zz=6.28-.28*sin(pi*phase);rod('Catenary dropper',(x,0,5.535),(x,0,zz),.0025,wire,None,stage,N=6)
# Photographic, physically lit sky: warm low sun, cool large sky fill.
world=scene.world;world.use_nodes=True;nt=world.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputWorld');bg=nt.nodes.new('ShaderNodeBackground');sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(20);sky.sun_rotation=math.radians(133);sky.air_density=1.05;sky.dust_density=1.6;sky.ozone_density=1;sky.sun_disc=False;sky.sun_intensity=.85;bg.inputs[1].default_value=.08;nt.links.new(sky.outputs[0],bg.inputs[0]);nt.links.new(bg.outputs[0],out.inputs[0])
d=bpy.data.lights.new('Late afternoon daylight','SUN');d.energy=2.3;d.angle=math.radians(2.0);d.color=(1.0,.90,.76);o=bpy.data.objects.new(d.name,d);stage.objects.link(o);o.rotation_euler=(-Vector((8,-12,16))).to_track_quat('-Z','Y').to_euler()
# Large bounce card simulates warm platform/ground reflection, all lights remain presentation only.
d=bpy.data.lights.new('Sky-side soft bounce','AREA');d.energy=600;d.shape='DISK';d.size=12;o=bpy.data.objects.new(d.name,d);stage.objects.link(o);o.location=(8,-11,7);o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,lens=55,ortho=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=700
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 d.dof.use_dof=False;return o
camera('CAM_HERO',(33,-14,3.05),(1.0,0,2.25),90)
camera('CAM_SIDE',(0,-35,2.75),(0,0,2.75),50,22.3)
camera('CAM_CAB',(16.7,-10.5,3.6),(8.0,-.18,2.65),66)
camera('CAM_BOGIE',(8.0,-10.5,1.25),(6,-.24,1.12),65)
camera('CAM_ROOF',(1.8,-10.0,9.0),(-2.7,0,4.2),54)
camera('CAM_FRONT',(24,-.20,2.55),(9.45,0,2.52),105)

hero=bpy.data.objects['CAM_HERO'];hero.data.dof.use_dof=True;hero.data.dof.focus_distance=31;hero.data.dof.aperture_fstop=4.0

for m in [earth,ballastm[0]]:
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');no=nt.nodes.new('ShaderNodeTexVoronoi');no.inputs['Scale'].default_value=42 if m==earth else 30;no.distance='EUCLIDEAN';nt.links.new(tc.outputs['Object'],no.inputs['Vector']);bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.75;bn.inputs['Distance'].default_value=.045;nt.links.new(no.outputs['Distance'],bn.inputs['Height']);nt.links.new(bn.outputs['Normal'],p.inputs['Normal'])

# The final photographic composition uses a subdued railway-boundary wall, not conspicuous toy trees.
for o in list(stage.objects):
 if o.name.startswith(('Distant tree trunk','Distant dense')):o.hide_render=True;o.hide_viewport=True
wallmat=material('STAGE • aged railway boundary concrete',(.17,.175,.16),0,.93,.48,.009)
box('Distant railway boundary wall',(-8,17,.38),(230,.22,1.75),wallmat,None,stage,b=.03)
for i in range(-30,31):
 x=i*3.5;box('Boundary wall post',(x,16.88,.44),(.18,.35,1.90),wallmat,None,stage,b=.01)
 for z in [-.12,.32,.76]:rod('Boundary concrete joint',(x-1.65,16.873,z),(x+1.65,16.873,z),.006,edge,None,stage,N=6)
# Additional coarse ground variation, including dark disturbed ground beside ballast.
nt=earth.node_tree;p=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=.9;no.inputs['Detail'].default_value=5;no.inputs['Roughness'].default_value=.75;nt.links.new(tc.outputs['Object'],no.inputs[0]);ra=nt.nodes.new('ShaderNodeValToRGB');ra.color_ramp.elements[0].color=(.05,.045,.035,1);ra.color_ramp.elements[1].color=(.16,.139,.102,1);nt.links.new(no.outputs['Fac'],ra.inputs[0]);nt.links.new(ra.outputs[0],p.inputs['Base Color'])

for x in [-6,6]:
 d=bpy.data.lights.new('Low reflected daylight fill','AREA');d.energy=80;d.shape='DISK';d.size=4;o=bpy.data.objects.new(d.name,d);stage.objects.link(o);o.location=(x,-4,2.0);o.rotation_euler=(Vector((x,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
