import os
"""Rich, efficient railway environments, source-specific configuration and metric geometry.
Run only through the shared serialized Blender launcher. No rolling stock.
"""
import bpy,math,json,sys,random,hashlib,time
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];code=sys.argv[sys.argv.index('--')+1].upper();R=Path(os.environ.get('SOUTH_STATION_OUTPUT_DIR',str(BASE/code.lower())));D=json.loads((R/'source/layout.json').read_text());C=D['config'];random.seed(sum(map(ord,code)));Z=.95
sys.path.insert(0,str(BASE/'scripts'));from access_geometry import approach_end,link_clearance
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
collections={};active=None;batches={};counts={}
def group(n):
 global active
 if n not in collections:collections[n]=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(collections[n])
 active=collections[n];return active
def mesh(n,vs,fs,m):
 if not vs or not fs:return
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);active.objects.link(o)
 if m:d.materials.append(m)
 return o
def mat(n,col,rough=.72,metal=0,noise=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  nd=m.node_tree.nodes;lk=m.node_tree.links;t=nd.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=3.5;t.inputs['Detail'].default_value=3;coord=nd.new('ShaderNodeNewGeometry');lk.new(coord.outputs['Position'],t.inputs['Vector']);r=nd.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*[v*(1-noise) for v in col],1);r.color_ramp.elements[1].color=(*col,1);lk.new(t.outputs['Fac'],r.inputs[0]);lk.new(r.outputs[0],p.inputs['Base Color']);b=nd.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=.015;lk.new(t.outputs['Fac'],b.inputs['Height']);lk.new(b.outputs[0],p.inputs['Normal'])
 return m
M={}
for key,args in {
 'cream':(C['color'],.78,0,.13),'ivory':((.82,.81,.69),.65,0,.08),'red':((.39,.075,.045),.63,0,.13),'tile':((.51,.46,.35),.73,0,.2),'tile2':((.43,.40,.31),.75,0,.23),'concrete':((.42,.44,.40),.76,0,.22),'dark':((.027,.034,.035),.73,0,0),'steel':((.45,.49,.49),.34,.8,0),'blue':((.025,.20,.31),.53,.35,.10),'teal':((.03,.29,.24),.65,.15,.08),'rust':((.24,.10,.045),.65,.7,.13),'head':((.43,.48,.5),.24,.94,0),'ballast':((.28,.28,.24),.88,0,.6),'wood':((.25,.12,.045),.66,0,.3),'roof':((.47,.51,.48),.62,.6,.15),'roofblue':((.035,.29,.41),.53,.45,.12),'terracotta':((.42,.16,.07),.8,0,.27),'glass':((.11,.23,.25),.22,.55,0),'yellow':((.96,.68,.025),.54,.04,.10),'white':((.84,.85,.76),.47,0,.05),'green':((.11,.27,.055),.84,0,.25),'trunk':((.29,.22,.15),.91,0,.36),'soil':((.34,.31,.20),.97,0,.7),'asphalt':((.14,.16,.15),.89,0,.35),'water':((.12,.24,.25),.2,.35,0)}.items():M[key]=mat(key,*args)
M['light']=mat('Fluorescent diffuser',(.93,.90,.72),.4);p=M['light'].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.93,.9,.72,1);p.inputs['Emission Strength'].default_value=2
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def box(n,p,s,m,ang=0):
 key=(active.name,n,m);v,f=batches.setdefault(key,([],[]));k=len(v);co,si=math.cos(ang),math.sin(ang)
 for xx,yy,zz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
  x,y=xx*s[0]/2,yy*s[1]/2;v.append((p[0]+x*co-y*si,p[1]+x*si+y*co,p[2]+zz*s[2]/2))
 f.extend(tuple(k+j for j in a) for a in F);counts[n]=counts.get(n,0)+1

def cyl(n,p,r,h,m,verts=12):
 v=[(p[0]+r*math.cos(i*math.tau/verts),p[1]+r*math.sin(i*math.tau/verts),p[2]+z) for z in [-h/2,h/2] for i in range(verts)];f=[tuple(range(verts-1,-1,-1)),tuple(range(verts,verts*2))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)];return mesh(n,v,f,M[m])
def beam(n,a,b,r,m):
 a,b=Vector(a),Vector(b);d=b-a
 if d.length<.001:return
 u=d.normalized();v=u.cross(Vector((0,0,1)))
 if v.length<.01:v=u.cross(Vector((0,1,0)))
 v.normalize();w=u.cross(v);vs=[]
 for p in [a,b]:
  for i in range(8):q=p+r*(v*math.cos(i*math.tau/8)+w*math.sin(i*math.tau/8));vs.append(tuple(q))
 fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 key=(active.name,n,m);bv,bf=batches.setdefault(key,([],[]));k=len(bv);bv.extend(vs);bf.extend(tuple(k+j for j in a) for a in fs)
def wire(n,pts,r,m):
 for a,b in zip(pts,pts[1:]):beam(n,a,b,r,m)
def flush():
 global active
 old=active
 for (cn,n,m),(v,f) in batches.items():active=collections[cn];mesh(n,v,f,M[m])
 batches.clear();active=old
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf')
def text(n,body,p,size,m='dark',width=None,rot=(math.pi/2,0,0)):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.004;d.resolution_u=4;d.font=font;o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=p;o.rotation_euler=rot;d.materials.append(M[m]);expected=max(len(s) for s in body.split('\n'))*size*.58
 if width and expected>width:o.scale.x=width/expected
 return o
def plaque(label,p,w=2.2,h=.42):
 box('Wayfinding enamel board',p,(w,.065,h),'blue');text('Wayfinding '+label,label,(p[0],p[1]-.037,p[2]),h*.42,'white',w-.12)
def area(n,p,power,size):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=p
 return o
def sample(pts,x):
 for a,b in zip(pts,pts[1:]):
  if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>.001:return a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1])
 return min(pts,key=lambda p:abs(p[0]-x))[1]
def distance(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(.00001,dx*dx+dy*dy)));return math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t)
def railclear(x,y):return min(distance((x,y),a,b) for w in D['ways'] for a,b in zip(w['xy'],w['xy'][1:]))
def pfsect(p,x):
 ys=[];ps=p['xy']
 for a,b in zip(ps,ps[1:]):
  if min(a[0],b[0])<=x<max(a[0],b[0]):ys.append(a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1]))
 return (min(ys),max(ys)) if len(ys)>1 else None
def pfmid(p,x):
 sec=pfsect(p,x)
 return sum(sec)/2 if sec else sum(q[1] for q in p['xy'])/len(p['xy'])
def pfbounds(p):return[min(q[0] for q in p['xy']),min(q[1] for q in p['xy']),max(q[0] for q in p['xy']),max(q[1] for q in p['xy'])]
def bench(x,y,z=Z,angle=0):
 def xy(dx,dy):return(x+dx*math.cos(angle)-dy*math.sin(angle),y+dx*math.sin(angle)+dy*math.cos(angle))
 for dx in [-.95,.95]:
  for dy in [-.25,.25]:a,b=xy(dx,dy);box('Bench cast legs',(a,b,z+.24),(.08,.09,.48),'blue',angle)
 for j in range(4):a,b=xy(0,-.25+j*.17);box('Bench timber seat',(a,b,z+.47),(2.3,.13,.07),'wood',angle)
 for j in range(3):a,b=xy(0,.32);box('Bench timber back',(a,b,z+.69+j*.15),(2.3,.065,.13),'wood',angle)
 for dx in [-1.08,1.08]:
  a,b=xy(dx,-.25);c,d=xy(dx,.34);beam('Bench armrests',(a,b,z+.76),(c,d,z+.76),.025,'steel')
def fan(x,y,z):
 beam('Fan pendant stem',(x,y,z+.30),(x,y,z),.016,'white');cyl('Fan motor',(x,y,z),.115,.12,'ivory')
 for ang in [0,2.094,4.188]:box('Fan paddle',(x+.31*math.cos(ang),y+.31*math.sin(ang),z-.08),(.62,.13,.019),'white',ang)
def light(x,y,z):box('Tube fixture',(x,y,z),(1.3,.22,.12),'white');box('Tube diffuser',(x,y,z-.074),(1.18,.14,.028),'light')
def tap(x,y,z):
 wire('Chrome tap',[(x,y,z),(x,y-.2,z),(x,y-.2,z-.075)],.019,'steel');beam('Tap handle',(x-.06,y,z+.05),(x+.06,y,z+.05),.013,'steel')
def waterpoint(x,y):
 box('Water tile backsplash',(x,y,Z+.90),(2.4,.17,1.45),'white');box('Water trough',(x,y-.35,Z+.54),(2.5,.70,.14),'concrete')
 for dx in [-.8,-.4,0,.4,.8]:tap(x+dx,y-.11,Z+.95);box('Water trough grate',(x+dx,y-.40,Z+.615),(.025,.47,.012),'dark')
 plaque('DRINKING WATER',(x,y-.12,Z+1.53),2.4,.30)
native_shapes={}
def native_letters(lang,p,width,height=.36):
 if lang not in native_shapes:
  f=R/'source'/('name_'+lang+'_outlined.svg')
  if not f.exists():return
  before=set(bpy.data.objects);bpy.ops.import_curve.svg(filepath=str(f));obs=list(set(bpy.data.objects)-before)
  if not obs:return
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;vv=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector((min(v.x for v in vv),min(v.y for v in vv),0));hi=Vector((max(v.x for v in vv),max(v.y for v in vv),0));ce=(lo+hi)/2;vs=[tuple(v-ce) for v in vv];fs=[list(p.vertices) for p in o.data.polygons];native_shapes[lang]=(vs,fs,hi-lo)
  bpy.data.objects.remove(o,do_unlink=True)
 vs,fs,size=native_shapes[lang];scale=min(width/max(.001,size.x),height/max(.001,size.y));verts=[(p[0]+v[0]*scale,p[1]-v[2]*scale,p[2]+v[1]*scale) for v in vs];return mesh('Shaped regional station name '+lang,verts,fs,M['dark'])
native_names=json.loads((R/'source/native_names.json').read_text()) if (R/'source/native_names.json').exists() else []
def stationboard(x,y,width=5):
 for dx in [-width/2+.15,width/2-.15]:box('Nameboard uprights',(x+dx,y,Z+1.24),(.14,.14,2.48),'dark')
 box('Station identification yellow board',(x,y,Z+2.10),(width,.13,1.48),'yellow');text('Station name',D['name'].upper(),(x,y-.074,Z+2.04),.31,'dark',width-.28);text('Station code',code+'  •  SOUTHERN RAILWAY',(x,y-.076,Z+1.62),.19,'dark',width-.4)
 if native_names:native_letters(native_names[0][0],(x,y-.081,Z+2.57),width-.30,.37)
 text('Station name back',D['name'].upper(),(x,y+.076,Z+2.04),.31,'dark',width-.28,rot=(math.pi/2,0,math.pi))
 text('Station code back',code+'  SOUTHERN RAILWAY',(x,y+.077,Z+1.62),.19,'dark',width-.40,rot=(math.pi/2,0,math.pi))
 # Native spelling comes directly from OSM station tags, shaped by Inkscape/Pango; no invented transliteration.

print('BUILD',code,'RAIL',flush=True)
group('10_RAIL_NETWORK_MAP_DERIVED');rail=json.loads((R/'source/rail_mesh.json').read_text())
for key,mt in [('head','head'),('web','rust'),('foot','rust'),('guard','rust'),('blade','head')]:
 if key in rail:mesh('Unioned running rail '+key,rail[key]['vertices'],rail[key]['faces'],M[mt])
group('11_TRACK_FORMATION_AND_FASTENERS');mesh('Full continuous ballast formation',rail['ballast']['vertices'],rail['ballast']['faces'],M['ballast'])
# Sleepers use metric pitch. De-duplicate connected-way endpoints and reserve turnout zones for long bearers.
seen=set();sleeper_count=0
def in_bearer_patch(x,y):
 for site in rail.get('bearer_sites',[]):
  dx,dy=x-site['center'][0],y-site['center'][1];u=site['u'];uu=dx*u[0]+dy*u[1];vv=-dx*u[1]+dy*u[0]
  if abs(uu)<site['half_length'] and abs(vv)<site['half_width']:return True
 return False

for w in D['ways']:
 carry=0;pts=w['xy']
 for a,b in zip(pts,pts[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
  if L<.001:continue
  ux,uy=dx/L,dy/L;ang=math.atan2(dy,dx)
  while carry<L:
   x,y=a[0]+ux*carry,a[1]+uy*carry;key=(round(x,1),round(y,1))
   if key not in seen and not in_bearer_patch(x,y):
    seen.add(key);sleeper_count+=1
    if code=='TVCN' and w['tags'].get('layer')=='-1':
     for sg in [-1,1]:box('Inspection pit separate rail support',(x-uy*sg*.872,y+ux*sg*.872,-.061),(.30,.50,.16),'concrete',ang)
    else:box('Concrete sleeper',(x,y,-.061),(.245,2.75,.16),'concrete',ang)
    for sg in [-1,1]:
     xx,yy=x-uy*sg*.872,y+ux*sg*.872;box('Resilient rail pad',(xx,yy,.030),(.21,.22,.025),'dark',ang)
     for off in [-.09,.09]:box('Elastic rail fastener',(xx-uy*off,yy+ux*off,.047),(.10,.040,.032),'rust',ang)
   carry+=.60
  carry-=L
for site in rail.get('bearer_sites',[]):
 x,y=site['center'];u=site['u'];ang=math.atan2(u[1],u[0])
 for j in range(-5,6):box('Extended crossing bearer',(x+u[0]*j*.60,y+u[1]*j*.60,-.061),(.27,4.8,.16),'concrete',ang)
# Actual angular granite stones along both shoulders, with a seeded repeatable distribution.
rockv=[];rockf=[]
for w in D['ways']:
 for a,b in zip(w['xy'],w['xy'][1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
  if L<.01:continue
  nx,ny=-dy/L,dx/L
  for j in range(int(L*1.1)):
   t=random.random();off=random.choice([-1,1])*random.uniform(1.32,1.70);x=a[0]+dx*t+nx*off;y=a[1]+dy*t+ny*off;r=random.uniform(.026,.065);z=-.102;k=len(rockv);rockv.extend([(x-r,y-r,z),(x+r,y-r,z),(x+r,y+r,z),(x-r,y+r,z),(x+r*.22,y-r*.2,z+r)]);rockf.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
mesh('Individual angular granite shoulder stones',rockv,rockf,M['ballast'])
# Crossing furniture is fitted to actual mapped intersection; unioned rails give genuine flange channels.
group('12_POINTWORK_VISUAL_RECONSTRUCTION');unique=[]
for frog in rail['crossings']:
 x,y=frog['xy']
 if any(math.hypot(x-a,y-b)<5 for a,b in unique):continue
 unique.append((x,y));w=min(D['ways'],key=lambda w:min(distance((x,y),a,b) for a,b in zip(w['xy'],w['xy'][1:])));a,b=min(zip(w['xy'],w['xy'][1:]),key=lambda ab:distance((x,y),*ab));ang=math.atan2(b[1]-a[1],b[0]-a[0]);u=(math.cos(ang),math.sin(ang));n=(-u[1],u[0])
 # Real channel-subtracted guard rail mesh is loaded with the running rails; no crossing overlays.
 px,py=x+n[0]*2.5-u[0]*6,y+n[1]*2.5-u[1]*6
 if railclear(px,py)>2.0:
  box('Point motor enclosure',(px,py,.25),(.82,.49,.35),'concrete',ang);beam('Recessed point linkage',(px,py,-.04),(px-n[0]*2.0,py-n[1]*2.0,-.04),.024,'steel')
# End treatment only for real source dead ends, never cropped main ends.
group('13_BUFFERS_AND_SIGNALS');buffer_count=0
for w in D['ways']:
 if w['tags'].get('service') not in ['yard','spur','siding']:continue
 for ix in [0,-1]:
  p=w['xy'][ix]
  if abs(p[0])>C['envelope']-2 or abs(p[1])>395:continue
  if any(min(distance(p,a,b) for a,b in zip(ow['xy'],ow['xy'][1:]))<.15 for ow in D['ways'] if ow is not w):continue
  q=w['xy'][1 if ix==0 else -2];d=Vector((q[0]-p[0],q[1]-p[1],0)).normalized();n=Vector((-d.y,d.x,0));buffer_count+=1
  for sg in [-1,1]:
   a=Vector((*p,.10))+n*sg*.85;beam('Buffer A frame',a+Vector((d.x*1.5,d.y*1.5,.05)),a+Vector((0,0,1.1)),.07,'rust')
  box('Buffer stop beam',(p[0],p[1],1.08),(2.5,.22,.30),'white',math.atan2(d.y,d.x)+math.pi/2)
# Metric station platform meshes, separately editable and fully extended.
group('20_PLATFORMS_SOURCE_AND_INFERRED');pmeshes=json.loads((R/'source/platform_mesh.json').read_text())
for p0 in pmeshes:mesh('Platform body '+p0['id'],p0['vertices'],p0['faces'],M['concrete'])
for pf in D['platforms']:
 ps=pf['xy'];mesh('Platform top '+pf['id'],[(x,y,Z+.014) for x,y in ps[:-1]],[tuple(range(len(ps)-1))],M['tile']);b=pfbounds(pf)
 # Narrow coping and safety line follow the true edge, including source curves.
 for a,bb in zip(ps,ps[1:]):
  dx,dy=bb[0]-a[0],bb[1]-a[1];L=math.hypot(dx,dy)
  if L<3:continue
  ang=math.atan2(dy,dx)
  for j in range(max(1,int(L/1.5))):
   t=(j+.5)/max(1,int(L/1.5));x,y=a[0]+dx*t,a[1]+dy*t;box('Platform white coping fascia',(x,y,Z-.12),(L/max(1,int(L/1.5))-.02,.12,.24),'white' if j%5 else 'red',ang)
  beam('Yellow platform safety edge',(a[0],a[1],Z+.035),(bb[0],bb[1],Z+.035),.043,'yellow')
 # Narrow joint strips create scale without fragile render noise.
 for xx in range(math.ceil(b[0]+2),math.floor(b[2]-2),2):
  sec=pfsect(pf,xx)
  if sec:box('Platform transverse paving joint',(xx,sum(sec)/2,Z+.019),(.012,sec[1]-sec[0]-.20,.009),'tile2')
print('BUILD',code,'PLATFORM_DETAILS',flush=True)
# Canopies curve by source platform centerline; repeated roof bays have trusses, purlins and downpipes.
def shelter(pf,x0,x1,width):
 group('21_PLATFORM_SHELTERS')
 for x in [x0+i*6 for i in range(int((x1-x0)/6)+1)]:
  sec=pfsect(pf,x)
  if not sec:continue
  y=sum(sec)/2;w=min(width,sec[1]-sec[0]-.8)
  for sg in [-1,1]:
   yy=y+sg*w*.29
   if railclear(x,yy)>2:
    box('Canopy footing',(x,yy,Z+.22),(.37,.42,.44),'concrete');box('Canopy steel column',(x,yy,Z+1.86),(.14,.16,3.40),'blue')
  beam('Canopy roof tie',(x,y-w/2,Z+3.50),(x,y+w/2,Z+3.50),.045,'blue')
  for sg in [-1,1]:
   beam('Canopy roof top chord',(x,y,Z+4.12),(x,y+sg*w/2,Z+3.50),.04,'blue');beam('Canopy truss web',(x,y,Z+3.50),(x,y+sg*w*.27,Z+3.81),.027,'blue')
  light(x,y,Z+3.34)
 for x in [x0+i*1.6 for i in range(int((x1-x0)/1.6))]:
  a,b=x,min(x+1.60,x1);ya,yb=pfmid(pf,a),pfmid(pf,b);sec=pfsect(pf,(a+b)/2)
  if not sec:continue
  w=min(width,sec[1]-sec[0]-.65);vs=[];fs=[]
  for i in range(11):
   t=i/10;xx=a+(b-a)*t;yy=ya+(yb-ya)*t;zz=.028 if i%2 else -.028;vs.extend([(xx,yy-w/2,Z+3.54+zz),(xx,yy,Z+4.14+zz),(xx,yy+w/2,Z+3.54+zz)])
  for i in range(10):
   for j in range(2):fs.append((i*3+j,i*3+j+1,(i+1)*3+j+1,(i+1)*3+j))
  # Batch corrugated mesh rather than creating thousands of objects.
  key=(active.name,'Corrugated canopy roof',C.get('canopy_material','roof'));vv,ff=batches.setdefault(key,([],[]));k=len(vv);vv.extend(vs);ff.extend(tuple(k+j for j in f) for f in fs)
  for off in [-.4,0,.4]:beam('Longitudinal canopy purlin',(a,ya+off*w,Z+4.02-abs(off)*1.2),(b,yb+off*w,Z+4.02-abs(off)*1.2),.045,'steel')
 for x in [x0+6+i*18 for i in range(max(1,int((x1-x0-6)/18)))]:
  if x>=x1:continue
  y=pfmid(pf,x);wire('Canopy rainwater downpipe',[(x,y+width*.48,Z+3.5),(x,y+width*.48,Z+.15)],.043,'concrete')
# Config supports photo-specific dispersed shelters and continuous terminal canopy zones.
canopy_coverage=[]
bridge_x=None
if C['bridge'] and (len(D['platforms'])>1 or C.get('bridge_extra_landing')):
 common0=max(pfbounds(p)[0] for p in D['platforms']);common1=min(pfbounds(p)[2] for p in D['platforms']);bridge_x=max(common0+30,min(common1-30,C.get('bridge_x',-70)))
for ix,pf in enumerate(D['platforms']):
 b=pfbounds(pf);available=b[2]-b[0];center=max(b[0]+20,min(b[2]-20,0));is_halt=C['halt'];width=min(C['pfwidth']-.5,7)
 if code=='TVCN':zones=[(b[0]+30,b[2]-45)]
 elif is_halt:zones=[(center-7,center+7),(min(b[2]-25,center+70),min(b[2]-11,center+84))]
 else:
  L=min(120,available*.32);zones=[(center-L*.62,center+L*.38),(b[0]+available*.74,b[0]+available*.74+22)]
 if C.get('no_platform_shelters'):zones=[]
 if C.get('shelter_zones'):zones=C['shelter_zones'][min(ix,len(C['shelter_zones'])-1)]
 if bridge_x is not None:
  zones=[q for a,b0 in zones for q in [(a,min(b0,bridge_x-4)),(max(a,bridge_x+17),b0)] if q[1]-q[0]>4]
 for a,b0 in zones:
  if b0>a and b0-a>4:shelter(pf,max(a,b[0]+5),min(b0,b[2]-5),width);canopy_coverage.append([ix,a,b0])
 group('22_PASSENGER_FURNITURE')
 for x in range(math.ceil(b[0]+16),math.floor(b[2]-12),24 if not is_halt else 40):
  y=pfmid(pf,x);sec=pfsect(pf,x)
  if sec and sec[1]-sec[0]>3.3 and railclear(x,y)>2.6 and (bridge_x is None or not bridge_x-5<x<bridge_x+18):bench(x,y)
 for x in [b[0]+22,center,b[2]-22]:
  if abs(x-C.get('building_x',0))<C['building'][0]/2+7:continue
  y=pfmid(pf,x)
  if bridge_x is not None and bridge_x-5<x<bridge_x+18:continue
  stationboard(x,y,5 if len(D['name'])<20 else 6.5)
 for x in [center-27,center+33] if not is_halt else [center+20]:
  y=pfmid(pf,x);sec=pfsect(pf,x)
  if sec and railclear(x,y)>2.6 and (bridge_x is None or not bridge_x-5<x<bridge_x+18):waterpoint(x,y+.5)
 for x in range(math.ceil(b[0]+28),math.floor(b[2]-18),48):
  y=pfmid(pf,x)
  if bridge_x is not None and bridge_x-5<x<bridge_x+18:continue
  cyl('Platform light mast',(x,y,Z+2.8),.048,5.6,'concrete');beam('Lamp crossarm',(x,y-.6,Z+5.55),(x,y+.6,Z+5.55),.03,'steel')
  for sg in [-1,1]:box('LED platform light',(x,y+sg*.58,Z+5.54),(.45,.27,.11),'white')
  for sg,mt in [(-1,'blue'),(1,'teal')]:cyl('Segregated litter bin',(x+sg*.31,y+.8,Z+.35),.22,.7,mt);cyl('Litter bin rim',(x+sg*.31,y+.8,Z+.715),.23,.04,'steel')
 for x in [center-12,center+15]:
  y=pfmid(pf,x)
  beam('Platform number sign post',(x,y,Z),(x,y,Z+2.90),.033,'blue');plaque('PLATFORM '+pf['tags'].get('ref',str(ix+1)),(x,y,Z+2.75),2.0,.4)
# Footbridge spans with stair opening intervals and physically clear platform landings.
bridge_data=[]
if C['bridge'] and (len(D['platforms'])>1 or C.get('bridge_extra_landing')):
 group('23_FOOTBRIDGE_RECONSTRUCTED');common0=max(pfbounds(p)[0] for p in D['platforms']);common1=min(pfbounds(p)[2] for p in D['platforms']);fx=max(common0+30,min(common1-30,C.get('bridge_x',-70)));pys=[pfmid(p,fx) for p in D['platforms']]
 if C.get('bridge_extra_landing'):
  road_y=sum(D['cross_section_y'])/len(D['cross_section_y']);pys.append(road_y+(11 if pys[0]<road_y else -11))
 ya,yb=min(pys)-1,max(pys)+1;deckz=7.90
 box('Footbridge deck',(fx,(ya+yb)/2,deckz),(2.6,yb-ya,.22),'concrete');box('Footbridge covering',(fx,(ya+yb)/2,deckz+2.46),(3.1,yb-ya+1,.12),'roofblue')
 for xx in [fx-1.3,fx+1.3]:
  gaps=[(y-1.1,y+1.1) for y in pys] if xx>fx else []
  def valid(y):return not any(a-.05<y<b+.05 for a,b in gaps)
  for j in range(int((yb-ya)/2)+1):
   y=ya+j*2
   if valid(y):beam('Bridge steel post',(xx,y,deckz+.13),(xx,y,deckz+2.3),.045,'blue')
   if y+2<yb and valid(y) and valid(y+2):beam('Bridge truss web',(xx,y,deckz+.20),(xx,y+2,deckz+2.2),.035,'blue')
  for j in range(int((yb-ya)/.3)+1):
   y=ya+j*.3
   if valid(y):beam('Bridge safety infill',(xx,y,deckz+.2),(xx,y,deckz+1.18),.014,'steel')
  for z in [deckz+.18,deckz+1.23,deckz+2.3]:
   intervals=[(ya,yb)]
   if z<deckz+2:
    for a,b in gaps:intervals=[q for lo,hi in intervals for q in [(lo,min(hi,a)),(max(lo,b),hi)] if q[1]>q[0]]
   for a,b in intervals:beam('Bridge longitudinal rail',(xx,a,z),(xx,b,z),.04,'blue')
 for i,y in enumerate(pys):
  # 42 treads at165mm rise,300mm going; top landing begins clear of bridge railing.
  for x in [fx-.82,fx+.82]:box('Footbridge support column',(x,y,(Z+deckz)/2),(.28,.28,deckz-Z),'concrete')
  steps=42;deck_top=deckz+.11;platform_top=Z+.014;rise=(deck_top-platform_top)/steps;run=.30;landing_edge=fx+2.275;start=landing_edge+.15
  box('Stair upper landing',(fx+1.75,y,deckz),(1.05,2.2,.22),'concrete')
  for j in range(steps):
   x=start+j*run;top=deck_top-(j+1)*rise;box('Stair non-slip tread',(x,y,top-.065),(.30,2.1,.13),'concrete');box('Stair yellow nosing',(x+.137,y,top+.002),(.023,2.1,.004),'yellow')
  for sg in [-1,1]:
   yy=y+sg*1.06;beam('Stair structural stringer',(start-.2,yy,deckz-.2),(start+steps*run,yy,Z-.1),.065,'steel');beam('Stair handrail',(start-.2,yy,deckz+1.0),(start+steps*run,yy,Z+1.0),.03,'blue')
   for j in range(0,steps,3):x=start+j*run;z=deck_top-(j+1)*rise;beam('Stair baluster',(x,yy,z),(x,yy,z+1),.018,'blue')
  bridge_data.append(dict(x=fx,y=y,landing_start_x=start,landing_end_x=landing_edge+steps*run,deck_height=deckz,landing_top_z=deck_top,first_tread_top_z=deck_top-rise,nominal_rise_m=rise,stair_transition_version=2))
# Building position outside the nearest platform, with true hall-to-platform connection.
p0=next((p for p in D['platforms'] if p['id']==C.get('primary_platform_id')),min(D['platforms'],key=lambda p:abs(pfmid(p,0))));bb=pfbounds(p0);bx=max(bb[0]+C['building'][0]/2+15,min(bb[2]-C['building'][0]/2-15,C.get('building_x',0)));sec=pfsect(p0,bx);track_y=sum(D['cross_section_y'])/max(1,len(D['cross_section_y']));side=C.get('building_side',1 if sum(sec)/2>track_y else -1);W,H=C['building'];edge=sec[1] if side>0 else sec[0];by=edge+side*(H/2+.3)
# Local frontage coordinates: Y increases from street toward railway regardless of platform side.
build_front=by+side*H/2;build_back=by-side*H/2
building_info={'center':[bx,by],'width':W,'depth':H,'side':side,'front_y':build_front,'platform_y':build_back,'footprint':[bx-W/2,by-H/2,bx+W/2,by+H/2],'basis':'Photograph-informed exterior envelope; metric size and hidden room partitions reconstructed unless documented'}
def bp(x,y,z):return(bx+x,build_front-side*y,z)
def b_box(n,p,s,m):box(n,bp(*p),s,m)
def b_text(n,body,p,size,m='dark',width=None):return text(n,body,bp(*p),size,m,width,rot=(math.pi/2,0,math.pi) if side>0 else (math.pi/2,0,0))
def b_beam(n,a,b,r,m):beam(n,bp(*a),bp(*b),r,m)
def b_window(x,y,z,w=1.35,h=1.5):
 b_box('Window recessed reveal',(x,y,z),(w+.17,.12,h+.18),'dark');b_box('Window glazing',(x,y-side*.02,z),(w,.035,h),'glass')
 for dx in [-w/2,0,w/2]:b_box('Window painted frame',(x+dx,y-.085,z),(.06,.075,h+.1),'red')
 for dz in [-h/2,0,h/2]:b_box('Window horizontal mullion',(x,y-.09,z+dz),(w,.07,.045),'red')
 for j in range(7):b_box('Window security grille',(x-w*.42+j*w*.14,y-.15,z),(.018,.022,h),'steel')
 b_box('Window concrete sill',(x,y-.2,z-h/2-.08),(w+.3,.4,.12),'ivory')
print('BUILD',code,'ARCHITECTURE',flush=True)
group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');height=C.get('wall_height',3.7 if not C['halt'] else 3.05);doorw=2.5 if W>20 else 1.55
b_box('Station building plinth',(0,H/2,Z-.20),(W+.4,H+.3,.4),'concrete');b_box('Station habitable floor',(0,H/2,Z+.035),(W,H,.08),'tile');b_box('Covered verandah floor',(0,-1.8,Z-.015),(W+1,3.6,.14),'tile')
# Main frontage and rear have real portals, not black proxy openings.
for yy in [0,H]:
 for a,b in [(-W/2,-doorw/2),(doorw/2,W/2)]:b_box('Masonry portal flank',((a+b)/2,yy,Z+height/2),(b-a,.23,height),'cream')
 b_box('Masonry portal lintel',(0,yy,Z+(height+2.35)/2),(doorw,.24,height-2.35),'cream')
for x in [-W/2,W/2]:b_box('Station building endwall',(x,H/2,Z+height/2),(.24,H,height),'cream')
for yy in [0,H]:b_box('Red oxide skirting',(0,yy-.14,Z+.15),(W,.035,.30),'red')
# Door opening in skirting stays physically clear.
# Trim skirting from portal with component replacement below by rendering flank-only components.
# Security door leaves are visibly open beside the public opening.
for sg in [-1,1]:b_box('Folded entrance gate',(sg*(doorw/2+.14),.12,Z+1.12),(.18,.12,2.24),'blue')
for x in [-W*.33,W*.33]:b_window(x,-.16,Z+1.65)
# Verandah columns, beam and roof; scale/roof type comes from individual source configuration.
for j in range(max(3,int(W/4)+1)):
 x=-W/2+j*W/max(2,int(W/4));b_box('Verandah column',(x,-2.8,Z+height/2),(.22,.25,height),'ivory');b_box('Verandah column plinth',(x,-2.8,Z+.2),(.31,.34,.4),'red')
b_box('Verandah fascia',(0,-2.8,Z+height),(W+.6,.26,.30),'ivory')
group('31_ROOFS_REMOVABLE')
if C['roof'] in ['tile','terminal']:
 roofz=Z+height+.18;ridge=roofz+H*.25;v=[bp(-W/2-.6,-3.15,roofz),bp(W/2+.6,-3.15,roofz),bp(-W/2-.6,H/2,ridge),bp(W/2+.6,H/2,ridge),bp(-W/2-.6,H+.65,roofz),bp(W/2+.6,H+.65,roofz)];mesh('Pitched traditional station roof',v,[(0,1,3,2),(2,3,5,4)],M['terracotta'] if C['roof']=='tile' else M['roofblue'])
 for x in [(-W/2-.55)+j*.33 for j in range(int((W+1.1)/.33)+1)]:
  b_beam('Terracotta tile course relief',(x,-3.12,roofz+.018),(x,H/2,ridge+.018),.032,'terracotta' if C['roof']=='tile' else 'blue');b_beam('Terracotta tile course relief',(x,H/2,ridge+.018),(x,H+.62,roofz+.018),.032,'terracotta' if C['roof']=='tile' else 'blue')
 for x in [-W/2,W/2]:mesh('Gable infill',[bp(x,0,roofz),bp(x,H,roofz),bp(x,H/2,ridge)],[(0,1,2)],M['cream'])
else:
 b_box('Flat concrete main roof',(0,H/2,Z+height+.16),(W+.65,H+.6,.27),'ivory');b_box('Flat verandah canopy',(0,-1.65,Z+height+.05),(W+1,3.45,.18),'ivory')
 for yy in [-.18,H+.18]:b_box('Flat roof parapet',(0,yy,Z+height+.53),(W+.4,.17,.62),'cream')
 for x in [-W/2-.18,W/2+.18]:b_box('End parapet',(x,H/2,Z+height+.53),(.17,H+.35,.62),'cream')
 if W>25:
  b_box('Raised entrance sign crown',(0,-.18,Z+height+.84),(W*.42,.25,.72),'ivory')
# Roof water goods, telecommunication fixtures, removable ceiling.
for x in [-W/2+.35,W/2-.35]:b_beam('Roof rainwater downpipe',(x,-.24,Z+height),(x,-.24,Z+.13),.05,'concrete')
b_box('Interior ceiling removable',(0,H/2,Z+height-.12),(W-.25,H-.25,.12),'ivory')
# Entrance sign intentionally English; local script source goes into data, no invented transliterations.
group('32_ARCHITECTURAL_SIGNS');b_box('Front station sign backing',(0,-2.97,Z+height+.03),(min(W,26),.13,.58),'yellow');b_text('Front station identity',D['name'].upper(),(0,-3.05,Z+height+.03),.36,'dark',min(W,25))
if D['metadata'].get('legacy_name_code'):b_text('Legacy station identity',D['metadata']['legacy_name_code'],(0,-.17,Z+2.85),.23,'blue',W*.6)
print('BUILD',code,'INTERIOR',flush=True)
group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED')
# Interior partitions leave a2.5m center aisle; realistic modest hut interiors for halts.
roomz=Z;counter_x=-W*.29;counter_w=min(6,W*.35);counter_y=H*.58
b_box('Ticket office counter lower',(counter_x,counter_y,Z+.53),(counter_w,.2,1.06),'cream');b_box('Ticket counter granite top',(counter_x,counter_y-.13,Z+1.12),(counter_w+.2,.55,.12),'concrete')
for j in range(max(1,int(counter_w/1.8))):
 x=counter_x+(j-(max(1,int(counter_w/1.8))-1)/2)*1.8
 b_box('Ticket counter grille header',(x,counter_y,Z+2.32),(1.55,.10,.15),'blue')
 for dx in [-.77,.77]:b_box('Ticket counter grille jamb',(x+dx,counter_y,Z+1.72),(.045,.09,1.20),'blue')
 for k in range(9):b_box('Ticket security grille',(x-.70+k*.175,counter_y,Z+1.79),(.022,.024,1.0),'blue')
 b_box('Ticket pass opening',(x,counter_y-.03,Z+1.25),(.40,.13,.25),'dark');b_box('Ticket window label backing',(x,counter_y-.08,Z+2.58),(1.65,.08,.34),'blue');b_text('Ticket window label','TICKETS',(x,counter_y-.15,Z+2.58),.18,'white',1.6)
 b_box('Booking clerk desk',(x,counter_y+1.0,Z+.76),(1.5,.70,.09),'wood');b_box('Booking computer display',(x,counter_y+.90,Z+1.06),(.46,.12,.34),'dark');b_box('Booking keyboard',(x,counter_y+.61,Z+.83),(.39,.16,.026),'dark')
 for dx in [-.60,.60]:b_box('Office desk leg',(x+dx,counter_y+1,Z+.38),(.045,.045,.76),'steel')
 b_box('Clerk chair seat',(x,counter_y+1.60,Z+.47),(.44,.44,.085),'blue');b_box('Clerk chair back',(x,counter_y+1.8,Z+.78),(.44,.05,.50),'blue')
 for dx in [-.17,.17]:
  for dy in [-.17,.17]:b_box('Chair leg',(x+dx,counter_y+1.60+dy,Z+.24),(.03,.03,.48),'steel')
for x in [W*.22,W*.36] if W>25 else [W*.28]:
 for y in [H*.20] if W>20 else [H*.26]:xx,yy,zz=bp(x,y,Z);bench(xx,yy,Z,0 if side>0 else math.pi)
for j in range(max(1,int(W/9))):
 x=-W/2+W*(j+.5)/max(1,int(W/9));xx,yy,_=bp(x,H*.32,0);fan(xx,yy,Z+height-.53);light(xx,yy,Z+height-.23);area('Interior soft ceiling light',(xx,yy,Z+height-.3),180 if C['halt'] else 350,3)
# Continuous jointed floor, timetables, clock, switch plates, extinguishers and luggage shelf.
for x in range(math.ceil(-W/2+1),math.floor(W/2)):
 for y in range(1,math.floor(H)):b_box('Individual floor terrazzo tile',(x,y,Z+.085),(.985,.985,.035),'tile' if (x+y)%6 else 'tile2')
b_box('Public timetable case',(W*.28,H-.18,Z+1.65),(min(3,W*.3),.08,1.1),'wood');b_box('Timetable paper',(W*.28,H-.23,Z+1.65),(min(2.85,W*.28),.015,.95),'ivory')
for j in range(9):b_box('Timetable printed row',(W*.28,H-.25,Z+1.99-j*.085),(min(2.6,W*.25),.01,.012),'dark')
for x in [-W*.40,W*.4]:
 b_box('Electrical switch plate',(x,.17,Z+1.32),(.15,.045,.21),'white');b_beam('Surface electrical conduit',(x,.17,Z+1.5),(x,.17,Z+height-.2),.012,'concrete')
xx,yy,_=bp(W*.37,H-.50,0);cyl('Fire extinguisher',(xx,yy,Z+.93),.10,.57,'red');b_beam('Fire extinguisher hose',(W*.37,H-.48,Z+1.2),(W*.37+.18,H-.48,Z+.80),.016,'dark')
if not C['halt']:
 # A small enclosed staff/records room with an open real doorway occupies far wing.
 group('34_STAFF_TOILET_SERVICE_RECONSTRUCTED');rx=W*.34;rw=max(4,W*.24);ry=H*.62
 for x in [rx-rw/2,rx+rw/2]:b_box('Staff partition wall',(x,ry,Z+1.5),(.12,H*.55,3),'cream')
 b_box('Staff partition lintel',(rx,H*.35,Z+2.7),(rw,.13,.6),'cream')
 for a,b in [(-rw/2,-.6),(.6,rw/2)]:b_box('Staff doorway flank',(rx+(a+b)/2,H*.35,Z+1.5),(b-a,.13,3),'cream')
 b_text('Station office label','STATION OFFICE',(rx,H*.35-.10,Z+2.50),.18,'blue',rw-.2)
 b_box('Office working desk',(rx,H*.70,Z+.78),(2,.85,.10),'wood');b_box('Office telephone',(rx+.60,H*.65,Z+.91),(.25,.20,.10),'dark');b_box('Staff record cabinet',(rx+rw*.29,H-.44,Z+1.02),(.9,.65,2.04),'concrete')
 for z in [Z+.65,Z+1.3,Z+1.75]:b_box('Cabinet handle',(rx+rw*.29,H-.78,z),(.17,.04,.025),'steel')
 b_box('Operating diagram board',(rx,H-.17,Z+2.2),(2.1,.08,1.0),'blue');b_box('Operating diagram paper',(rx,H-.23,Z+2.2),(1.96,.01,.86),'white')
 for j in range(4):b_box('Diagram railway lines',(rx,H-.25,Z+1.94+j*.16),(1.80,.01,.014),'dark')
 # Separate small sanitary annex, not an invented station concourse.
 tx=bx+W/2+5;ty=by;tw=5;td=4;top=Z+3.05
 box('Toilet annex floor',(tx,ty,Z-.025),(tw,td,.16),'concrete')
 for x in [tx-tw/2,tx+tw/2]:box('Toilet annex sidewall',(x,ty,Z+1.5),(.17,td,3),'cream')
 box('Toilet annex backwall',(tx,ty+side*td/2,Z+1.5),(tw,.17,3),'cream');box('Toilet annex door header',(tx,ty-side*td/2,Z+2.7),(tw,.17,.6),'cream')
 for xx in [tx-1.65,tx+1.65]:box('Toilet front door flank',(xx,ty-side*td/2,Z+1.5),(1.65,.17,3),'cream')
 box('Toilet annex flat roof',(tx,ty,top),(tw+.35,td+.35,.17),'ivory');box('WC partition',(tx,ty+.2,Z+1.25),(.10,3.2,2.5),'white')
 for xx in [tx-1.15,tx+1.15]:
  cyl('WC pedestal',(xx,ty+.6,Z+.25),.18,.45,'white');o=cyl('WC bowl rim',(xx,ty+.5,Z+.49),.30,.10,'white',20);o.scale.y=1.25;cyl('WC bowl inset',(xx,ty+.5,Z+.547),.20,.012,'dark');box('WC cistern',(xx,ty+1.22,Z+.88),(.48,.19,.56),'white')
 box('Washbasin',(tx-1.15,ty-.65,Z+.77),(.70,.53,.16),'white');tap(tx-1.15,ty-.42,Z+1.04);area('Toilet light',(tx,ty,top-.15),150,2)
 # Reconstructed sanitary-annex access joins its raised floor to the platform, avoiding an isolated cubicle.
 group('35_BUILDING_ACCESS');px=tx;ya=ty-side*1.95;yb=approach_end(D,px,by,side)[0];ww=1.60;access_clearance=link_clearance(D,px,ya,yb,ww);vv=[(px-ww/2,ya,-.20),(px+ww/2,ya,-.20),(px+ww/2,yb,-.20),(px-ww/2,yb,-.20),(px-ww/2,ya,1.005),(px+ww/2,ya,1.005),(px+ww/2,yb,.964),(px-ww/2,yb,.964)];mesh('Reconstructed sanitary annex approach',vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],M['concrete']);building_info['sanitary_annex_approach']={'center_x':px,'width_m':ww,'endpoints':[[px,ya,1.005],[px,yb,.964]],'basis':'Explicitly reconstructed continuous connection to sanitary annex','clearance':access_clearance}
# Covered platform access and front step/ramp with a clear central route.
group('35_BUILDING_ACCESS');xx,yy,_=bp(0,H+.15,0);box('Hall platform link',(xx,yy,Z-.015),(doorw,1.0,.14),'tile')
stair_rise=(Z+.055+.14)/7
for i in range(7):xx,yy,_=bp(0,-3.755-i*.31,0);box('Station entrance stair',(xx,yy,Z+.055-(i+1)*stair_rise-.07),(doorw+1.4,.31,.14),'concrete')
# Sloped accessible path to one verandah side, no vertical step proxy.
x=bx-W*.35;front_outer=build_front+side*3.6;length=12.0;vs=[(x-1,front_outer,-.12),(x+1,front_outer,-.12),(x-1,front_outer+side*length,-.12),(x+1,front_outer+side*length,-.12),(x-1,front_outer,Z+.055),(x+1,front_outer,Z+.055),(x-1,front_outer+side*length,-.14),(x+1,front_outer+side*length,-.14)];mesh('Accessible sloping entrance path',vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],M['concrete'])
# Forecourt is external station-specific extent, no parked train or road vehicle proxies.
group('40_FORECOURT_AND_LANDSCAPE');fy=build_front+side*16;box('Station forecourt',(bx,fy,-.21),(max(W+18,36),27,.14),'asphalt')
for x in [bx-W/2-7,bx+W/2+10]:
 box('Forecourt curb',(x,fy,-.02),(.3,27,.28),'white')
 for j in range(7):box('Kerb red band',(x,fy-12+j*4,.0),(.31,1.5,.22),'red')
# Site ground and tropical planting, kept clear of mapped railway envelopes.
allpts=[p for w in D['ways'] for p in w['xy']];bounds=[min(p[0] for p in allpts),min(p[1] for p in allpts),max(p[0] for p in allpts),max(p[1] for p in allpts)];gx=(bounds[0]+bounds[2])/2;gy=(bounds[1]+bounds[3])/2;gw=bounds[2]-bounds[0]+90;gh=max(140,bounds[3]-bounds[1]+140)
mesh('Terrain with real inspection-pit openings',rail['terrain']['vertices'],rail['terrain']['faces'],M['soil']) if 'terrain' in rail else box('Terrain base',(gx,gy,-.44),(gw,gh,.20),'soil')
def palm(x,y,h=9):
 bend=random.uniform(-.7,.7);beam('Coconut palm trunk',(x,y,-.32),(x+bend,y+.15,h),.13,'trunk')
 for j in range(9):
  a=j*math.tau/9;L=random.uniform(2.5,3.8);dx,dy=math.cos(a),math.sin(a);root=Vector((x+bend,y+.15,h));tip=root+Vector((dx*L,dy*L,-1.0));mid=root+Vector((dx*L*.48,dy*L*.48,.55));wire('Palm frond rachis',[root,mid,tip],.025,'green');v=[];f=[]
  for k in range(1,10):
   t=k/10;p=root.lerp(mid,t*2) if t<.5 else mid.lerp(tip,(t-.5)*2);w=.52*math.sin(t*math.pi);off=Vector((-dy*w,dx*w,-.25));j0=len(v);v.extend([tuple(p),tuple(p+off+Vector((-dx*.35,-dy*.35,0))),tuple(p+Vector((dx*.26,dy*.26,-.15))),tuple(p-off+Vector((-dx*.35,-dy*.35,0)))]);f.extend([(j0,j0+1,j0+2),(j0,j0+2,j0+3)])
  mesh('Coconut frond leaflets',v,f,M['green'])
for j in range(34 if code=='TVCN' else 19):
 x=random.uniform(max(bounds[0],-650),min(bounds[2],650));y=random.choice([bounds[1]-random.uniform(15,42),bounds[3]+random.uniform(18,45)])
 if railclear(x,y)>9 and not (bx-W/2-15<x<bx+W/2+15 and abs(y-fy)<23):palm(x,y,random.uniform(7,12))
# Electrification at source lines. All support feet filtered against EVERY rail road, not only nearest main.
print('BUILD',code,'OHE',flush=True);group('50_OHE_VISUAL_RECONSTRUCTION');ohe_positions=[]
for x in range(math.ceil(bounds[0]/54)*54,math.floor(bounds[2]/54)*54,54):
 if bridge_x is not None and abs(x-bridge_x)<4:continue
 ys=[]
 for w in D['ways']:
  if min(p[0] for p in w['xy'])<=x<=max(p[0] for p in w['xy']):ys.append(sample(w['xy'],x))
 if not ys:continue
 portal_supports=[]
 for outer_sg,yy in [(-1,min(ys)-3.5),(1,max(ys)+3.5)]:
  # Set foundations OUTSIDE physical platform bodies rather than omit every station mast.
  for pf in D['platforms']:
   sec0=pfsect(pf,x)
   if sec0 and sec0[0]-.7<yy<sec0[1]+.7:yy=sec0[0]-.85 if outer_sg<0 else sec0[1]+.85
  if railclear(x,yy)<2.9:continue
  if bx-W/2-1<x<bx+W/2+1 and abs(yy-by)<H/2+2:continue
  box('OHE mast foundation',(x,yy,-.02),(.65,.70,.60),'concrete');box('OHE mast',(x,yy,4.05),(.14,.18,8.20),'steel');ohe_positions.append([x,yy]);portal_supports.append(yy);nearest=min(ys,key=lambda y:abs(y-yy));beam('OHE cantilever',(x,yy,7.10),(x,nearest,6.65),.032,'steel');beam('OHE steady arm',(x,yy,6.15),(x,nearest,5.95),.025,'steel')
  for j in range(6):cyl('OHE porcelain insulator',(x,yy,6.35+j*.065),.075,.032,'ivory',10)
 # Separate spanning boom above all roofs with supports outside platforms.
 if max(ys)-min(ys)>18 and len(portal_supports)==2:beam('OHE gantry crossbeam',(x,min(portal_supports),8.30),(x,max(portal_supports),8.30),.07,'steel')
for w in D['ways']:
 if w['tags'].get('electrified')=='no':continue
 pp=w['xy'];wire('Contact wire '+w['id'],[(x,y,5.90) for x,y in pp],.009,'rust');wire('Catenary messenger '+w['id'],[(x,y,6.75) for x,y in pp],.010,'rust')
 for a,b in zip(pp,pp[1:]):
  L=math.dist(a,b)
  for j in range(int(L/9)):
   t=(j+.5)*9/L;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;beam('Catenary dropper',(x,y,5.90),(x,y,6.75),.006,'steel')
# Small station equipment at clear lateral offsets only.
group('51_TRACKSIDE_SERVICES');signal_positions=[]
for pf in D['platforms']:
 b=pfbounds(pf)
 for x in [b[0]-20,b[2]+20]:
  y=pfmid(pf,x);nearest=min(D['cross_section_y'],key=lambda yy:abs(y-yy));yy=nearest+(3.2 if y>nearest else -3.2)
  if railclear(x,yy)<2.6:continue
  box('Signal base',(x,yy,-.02),(.58,.60,.55),'concrete');cyl('Signal post',(x,yy,2.03),.06,4.1,'steel');box('Signal head',(x,yy,4.03),(.32,.19,1.18),'dark')
  for z,mt in [(3.70,'red'),(4.03,'yellow'),(4.36,'green')]:
   o=cyl('Signal lens',(x,yy-.12,z),.105,.025,mt,14);o.rotation_euler.x=math.pi/2
  signal_positions.append([x,yy]);box('Relay cabinet',(x+3,yy,0.62),(.8,.5,1.35),'concrete')
# Continuous side drainage and cable lids follow platform outer side, not across running rails.
for pf in D['platforms']:
 b=pfbounds(pf)
 for x in range(math.ceil(b[0]),math.floor(b[2]),4):
  sec=pfsect(pf,x)
  if not sec:continue
  py=sum(sec)/2;out=sec[1]+.65 if py>track_y else sec[0]-.65
  if railclear(x,out)>2.3:box('Cable trough cover',(x,out,-.15),(3.94,.42,.13),'concrete')
# Entire inspection pits only where source layer=-1 explicitly marks recessed maintenance roads.
if code=='TVCN':
 group('52_MAINTENANCE_ROADS_RECONSTRUCTED')
 for w in D['ways']:
  if w['tags'].get('layer')!='-1':continue
  for a,b in zip(w['xy'],w['xy'][1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);ang=math.atan2(dy,dx);x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
   box('Inspection pit deep invert',(x,y,-.99),(L,1.12,.10),'dark',ang)
   for sg in [-1,1]:box('Inspection pit concrete retaining wall',(x-math.sin(ang)*sg*.69,y+math.cos(ang)*sg*.69,-.48),(L,.18,.98),'concrete',ang)
   for sg in [-1,1]:box('Pit edge service walkway',(x-math.sin(ang)*sg*1.95,y+math.cos(ang)*sg*1.95,-.04),(L,.56,.18),'concrete',ang)
exec(compile((BASE/'scripts/architectural_variants.py').read_text(),str(BASE/'scripts/architectural_variants.py'),'exec'))
flush();print('BUILD',code,'SAVE',flush=True)
# Presentation cameras and flat deliverable collection hierarchy.
group('90_LIGHTS_AND_CAMERAS');scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
world=bpy.data.worlds.new('Tropical daylight') if not bpy.data.worlds else bpy.data.worlds[0];scene.world=world;world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.76,.88,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.6
ld=bpy.data.lights.new('Afternoon sun','SUN');lo=bpy.data.objects.new('Afternoon sun',ld);active.objects.link(lo);ld.energy=2.6;ld.angle=.18;lo.rotation_euler=(.48,-.45,-.50);fill=area('Broad sky fill',(bx,by,80),18000,100)
def camera(name,pos,target,lens=45,ortho=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);active.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.10;d.clip_end=10000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
cam=[];pmin=min(pfbounds(p)[0] for p in D['platforms']);pmax=max(pfbounds(p)[2] for p in D['platforms']);pc=(pmin+pmax)/2;pcy=sum(pfmid(p,pc) for p in D['platforms'])/len(D['platforms']);fullw=bounds[2]-bounds[0]
cam.append(camera('01_FULL_STATION_NETWORK',(gx+fullw*.28,gy-fullw*.28,fullw*.50),(gx,gy,0),ortho=fullw*1.03))
arch_side=-side if C.get('architecture') in ['pgz_hut','amva_corrugated','erl_two_level'] else side
cam.append(camera('02_STATION_ARCHITECTURE',(bx-W*.85,by+arch_side*max(28,W*.67),max(7,W*.20)),(bx,by,Z+1.7),lens=43))
px=min(pmax-35,max(pmin+20,bx-65));py=pfmid(p0,px);cam.append(camera('03_PLATFORM_AND_TRACKS',(px,py,3.0),(min(pmax-15,px+150),pfmid(p0,min(pmax-15,px+150))-side*3,2.1),lens=27))
ip=bp(W*.05,H*.18,Z+1.65);it=bp(-W*.20,H*.7,Z+1.4);cam.append(camera('04_FURNISHED_INTERIOR',ip,it,lens=22 if not C['halt'] else 18))
if unique:
 x,y=unique[len(unique)//2];cam.append(camera('05_PHYSICAL_POINTWORK',(x-10,y-8,7),(x,y,.10),lens=47))
else:
 x=max(pmin+20,min(pmax-20,bx+35));yy=min(D['cross_section_y'],key=lambda y:abs(y-pfmid(p0,x)));cam.append(camera('05_TRACK_AND_PLATFORM_DETAIL',(x-6,yy-5,3.5),(x+9,yy,.35),lens=42))
if C.get('open_halt'):
 pcx=30;pcy=pfmid(p0,pcx);cam[1].name='02_OPEN_SHELTER_ARCHITECTURE';cam[1].location=(pcx-21,pcy-24,7);cam[1].rotation_euler=(Vector((pcx,pcy,Z+1.5))-cam[1].location).to_track_quat('\x2dZ','Y').to_euler();cam[3].name='04_COVERED_WAITING_DETAIL';cam[3].location=(pcx-8,pcy-4,2.5);cam[3].rotation_euler=(Vector((pcx,pcy,Z+1.3))-cam[3].location).to_track_quat('\x2dZ','Y').to_euler()
if C.get('architecture')=='njt_barrel_entry':
 cam[1].location=(bx-43,build_front+side*64,18);cam[1].rotation_euler=(Vector((bx-13,by,Z+3))-cam[1].location).to_track_quat('\x2dZ','Y').to_euler();cam[1].data.lens=42
scene.camera=cam[1];scene.render.engine='CYCLES' if '--cycles' in sys.argv else 'CYCLES'
# Use bounded clean Eevee, avoiding unavailable OpenImageDenoise.
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.threads_mode='FIXED';scene.render.threads=4
scene['station_code']=code;scene['source_scope']='Google/photo-informed + OSM mixed-date source geometry + disclosed reconstructed architecture and hidden interiors; not surveyed';scene['no_rolling_stock']=True;scene['nominal_gauge_m']=1.676
for o in bpy.data.objects:
 if o.type=='MESH':o['geometry_units']='metres'
# Remove actual central skirting segments obstructing doors; batches need no portal-floor obstacles.
for o in list(bpy.data.objects):
 if o.name.startswith('Red oxide skirting'):bpy.data.objects.remove(o,do_unlink=True)
group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
for yy in ([] if C.get('open_halt') or C.get('architecture')=='davm_ticket_shelter' else [0,H]):
 for a,b in [(-W/2,-doorw/2),(doorw/2,W/2)]:b_box('Portal-clear red skirting',((a+b)/2,yy-.14,Z+.15),(b-a,.035,.3),'red')
flush();scene.render.filepath=str(R/'renders/02_STATION_ARCHITECTURE.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/f'{code}_station_v01.blend'),compress=True)
qa=dict(station=code,name=D['name'],units='metres',nominal_gauge_m=1.676,railhead_flange_channel_qa=rail['qa'],reported_platform_faces=D['metadata']['iri_reported_platforms'],model_platform_bodies=len(D['platforms']),platform_ids=[p['id'] for p in D['platforms']],platform_bounds={p['id']:pfbounds(p) for p in D['platforms']},source_road_pieces=len(D['ways']),road_piece_ids=[w['id'] for w in D['ways']],source_track_centres_at_station=D['cross_section_y'],no_trains=True,sleepers=sleeper_count,buffers=buffer_count,pointwork_sites=len(unique),objects=len(scene.objects),meshes=sum(o.type=='MESH' for o in scene.objects),vertices=sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),polygons=sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),rail_bounds_xy=bounds,building=building_info,footbridges=bridge_data,canopies=canopy_coverage,ohe_mast_count=len(ohe_positions),ohe_minimum_rail_center_distance=min([railclear(*p) for p in ohe_positions] or [None]),ohe_positions=ohe_positions,signal_positions=signal_positions,packed_images=[dict(name=i.name,packed=bool(i.packed_file)) for i in bpy.data.images if i.source=='FILE'],cameras=[dict(name=c.name,location=list(c.location),target_rotation=list(c.rotation_euler)) for c in cam],stair_transition_version=2,status='Built; independent visual/geometry QA pending',render_engine=scene.render.engine)
(R/'QA_BUILD.json').write_text(json.dumps(qa,indent=2));(R/'source/build_config.json').write_text(json.dumps(C,indent=2))
print('SAVED',code,qa['objects'],qa['vertices'],flush=True)
