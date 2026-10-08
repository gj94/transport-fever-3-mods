"""Evidence-led coastal station visual reconstruction. All Blender runs use shared locked runner.
Assets are full scale metres; OSM centerlines, original art, photographed massing, reconstructed rooms.
"""
import bpy,sys,json,math,random,time,hashlib,resource
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'KUMM';P=Path(next((a.split('=',1)[1] for a in sys.argv if a.startswith('--output=')),str(BASE/CODE))).resolve();VERSION=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--version=')),'v01')
D=json.load(open(P/'references/plan.json'));BO=D.get('bridge_offset_m',65);S=D['station'];random.seed(sum(map(ord,CODE)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection':bpy.data.collections.remove(c)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.render.engine='CYCLES' if '--cycles' in sys.argv else 'BLENDER_EEVEE_NEXT';sc.cycles.samples=24;sc.cycles.use_denoising=False
# CPU Cycles remains dependable on this headless host; no OIDN build.
sc.render.resolution_x=1440;sc.render.resolution_y=960;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.render.threads_mode='FIXED';sc.render.threads=4
sc.world.color=(.45,.57,.70);sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.52,.66,.82,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sc.view_settings.view_transform='Standard';sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=0;sc.view_settings.gamma=1
COL=None;BATCH={};CAT=None;metrics={'station_code':CODE,'created_utc':'2026-10-08','units':'metres','gauge_m':1.676,'stock_objects':0,'platform_faces_iri':int(S['reported_platform_count'] or 0),'platform_bodies_modeled':len(D['platforms']),'road_cross_section_count':len(D['transect_road_centers_x']),'source_route_segments':len(D['routes']),'mapped_turnout_nodes':len(D['turnout_nodes']),'furnished_interiors':None if CODE=='TNU' else 'reconstructed; hidden room partitions, fittings, fixtures and room use are not surveyed','geometry_method':'OSM source-plan projected to local metres; three-part unioned broad-gauge rail solids with45mm visual flange channels; source-map resolution is not engineering turnout certification','closure':'Closed 2017-07-10' if CODE=='TNU' else None}
def coll(name):
 global COL,CAT
 CAT=name;COL=bpy.data.collections.new(name);sc.collection.children.link(COL);return COL

def mat(name,col,rough=.75,metal=0,noise=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=noise;t.inputs['Detail'].default_value=2
  co=n.new('ShaderNodeTexCoord');m.node_tree.links.new(co.outputs['Object'],t.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*.76 for v in col),1);r.color_ramp.elements[1].color=(*(min(1,v*1.12) for v in col),1);m.node_tree.links.new(t.outputs['Fac'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.015;m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs[0],p.inputs['Normal'])
 return m
M={}
for name,color,rough,metal,noise in [('ivory',(.80,.77,.65),.82,0,5),('peach',(.76,.39,.25),.8,0,5),('cream',(.85,.77,.52),.8,0,5),('white',(.85,.87,.83),.7,0,5),('red',(.46,.105,.065),.8,0,6),('blue',(.06,.23,.35),.7,.15,5),('roof',(.37,.40,.37),.7,.2,24),('basalt',(.13,.16,.17),.9,0,16),('aqua',(.20,.62,.59),.82,0,4),('roofgreen',(.065,.29,.18),.55,.15,20),('orange',(.85,.32,.055),.8,0,5),('roofblue',(.035,.24,.57),.50,.25,24),('tile',(.42,.16,.08),.85,0,20),('stone',(.51,.51,.43),.85,0,35),('pavers',(.50,.26,.19),.85,0,32),('yellow',(.93,.64,.06),.75,0,5),('steel',(.37,.42,.40),.42,.72,14),('dark',(.033,.036,.032),.76,0,0),('glass',(.075,.17,.20),.2,.6,0),('wood',(.27,.13,.05),.7,0,8),('railhead',(.40,.43,.41),.24,.88,0),('railweb',(.25,.14,.075),.7,.4,10),('ballast',(.28,.25,.21),.95,0,75),('sleeper',(.43,.43,.38),.9,0,20),('ground',(.28,.34,.17),.95,0,1.5),('leaf',(.10,.24,.055),.9,0,5),('leaflight',(.18,.32,.075),.85,0,5),('road',(.13,.14,.13),.85,0,44),('water',(.09,.25,.22),.18,.25,4)]:M[name]=mat(name,color,rough,metal,noise)

def mesh(name,v,f,m):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);COL.objects.link(ob)
 if m:me.materials.append(m)
 return ob

def batchgeom(v,f,m):
 key=(CAT,m.name);d=BATCH.setdefault(key,{'v':[],'f':[],'m':m,'col':COL});n=len(d['v']);d['v'].extend(v);d['f'].extend([tuple(n+i for i in ff) for ff in f])

def box(name,loc,dim,m,batch=True):
 x,y,z=loc;a,b,c=[v/2 for v in dim];v=[(x+u*a,y+w*b,z+t*c) for u,w,t in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];f=[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)]
 if batch:batchgeom(v,f,m)
 else:return mesh(name,v,f,m)

def beam(name,a,b,w,m,dep=None):
 a,b=Vector(a),Vector(b);length=(b-a).length
 if length<.0001:return
 q=(b-a).to_track_quat('Z','Y');x,y,z=(a+b)/2;ww=w/2;dd=(dep or w)/2;ll=length/2;v=[tuple(q@Vector((u*ww,v*dd,t*ll))+Vector((x,y,z))) for u,v,t in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];batchgeom(v,[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)],m)

def cyl(name,loc,r,h,m,n=12):
 x,y,z=loc;v=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z+t*h/2) for t in [-1,1] for i in range(n)];f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];batchgeom(v,f,m)

def tube(name,points,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=0;cu.resolution_u=1;s=cu.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);COL.objects.link(ob);ob.data.materials.append(m);return ob

def txt(name,body,loc,size,m,rot=(math.pi/2,0,0)):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0015;ob=bpy.data.objects.new(name,cu);COL.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;cu.materials.append(m);return ob

def texmat(name,filename):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(P/'textures'/filename),check_existing=True);im.image.pack();m.node_tree.links.new(im.outputs['Color'],n['Principled BSDF'].inputs['Base Color']);n['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
SIGN=texmat('Original trilingual nameboard art','board.png');FASC=texmat('Original station fascia art','fascia.png');NOTICE=texmat('Original reconstruction informational poster','notice.png')
def plane(name,loc,w,h,m,axis='Y',sg=1):
 x,y,z=loc
 if axis=='Y':v=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
 else:v=[(x,y-sg*w/2,z-h/2),(x,y+sg*w/2,z-h/2),(x,y+sg*w/2,z+h/2),(x,y-sg*w/2,z+h/2)]
 ob=mesh(name,v,[(0,1,2,3)],m);uv=ob.data.uv_layers.new()
 for i,c in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=c
 return ob

def sample(points,step):
 out=[];dd=0
 for a,b in zip(points,points[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy)
  if not le:continue
  while dd<=le:
   t=dd/le;out.append((a[0]+dx*t,a[1]+dy*t,dx/le,dy/le));dd+=step
  dd-=le
 return out

def polyplate(name,pts,z0,z1,m):
 # Blender concave ngon is tessellated for export; wall faces remain true perimeter.
 ps=pts[:-1] if pts[0]==pts[-1] else pts;n=len(ps);v=[(x,y,z) for z in [z0,z1] for x,y in ps];f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,v,f,m)

def at_y(points,y):
 for a,b in zip(points,points[1:]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(a[1]-b[1])>.001:
   t=(y-a[1])/(b[1]-a[1]);return a[0]+(b[0]-a[0])*t
 return min(points,key=lambda p:abs(p[1]-y))[0]

def inside(pt,poly):
 x,y=pt;yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def platform_span(poly,y):
 xx=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-5:xx.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return (min(xx),max(xx)) if len(xx)>1 else None

coll('01 | Mapped railway infrastructure')
R=json.load(open(P/'references/rail_meshes.json'))
for k,m in [('ballast',M['ballast']),('foot',M['railweb']),('web',M['railweb']),('head',M['railhead'])]:o=mesh('Mapped rail '+k,R[k]['v'],R[k]['f'],m);o['basis']='OSM mapped centerlines; visual broad gauge, not engineering geometry'
seen=set();sleepers=0
for r in D['routes']:
 for x,y,dx,dy in sample(r['xy'],.65):
  ky=(round(x*2),round(y*2))
  if ky in seen:continue
  seen.add(ky);nx,ny=-dy,dx;a=(x+nx*1.375,y+ny*1.375,.40);b=(x-nx*1.375,y-ny*1.375,.40);beam('Prestressed concrete sleeper',a,b,.22,M['sleeper'],.22);sleepers+=1
  for sg in [-1,1]:
   cx,cy=x+nx*sg*.868,y+ny*sg*.868
   box('Fastening plate',(cx,cy,.469),(.24,.24,.028),M['dark'])
   for j in [-1,1]:cyl('Railclip anchor',(cx+nx*j*.095,cy+ny*j*.095,.505),.029,.07,M['steel'],6)
metrics['sleeper_count']=sleepers
metrics['switch_hardware']=[]
for t in D['turnout_nodes']:
 x,y=t['xy'];candidates=[]
 for off in [2.35,-2.35,3.05,-3.05]:
  xx=x+off;pp=(xx,y)
  if any(inside(pp,p['xy']) for p in D['platforms']):continue
  near=min(abs(at_y(r['xy'],y)-xx) for r in D['routes'] if min(p[1] for p in r['xy'])-2<=y<=max(p[1] for p in r['xy'])+2)
  if near>1.35:candidates.append((near,off))
 off=max(candidates)[1] if candidates else -2.35
 mx=x+off;metrics['switch_hardware'].append({'node_xy':[x,y],'motor_xy':[mx,y],'placement':'Reconstructed visible outside platform and rail envelope','candidate_clearance':max(candidates)[0] if candidates else None})
 box('Mapped switch visual motor',(mx,y,.56),(.65,1,.38),M['dark']);box('Switch motor cover',(mx,y,.775),(.71,1.05,.07),M['steel']);beam('Throw linkage',(x-.9,y,.50),(mx,y,.50),.055,M['steel']);box('Switch inspection slab',(mx,y,.29),(1.1,1.4,.14),M['stone'])
 for i in [-1,0,1]:box('Switch rodding clips',(x+i*.68,y,.52),(.12,.15,.12),M['steel'])
# Mapped dead-end spurs get visible bufferstops; clipped through-route endpoints do not.
endpoint_map={}
for r in D['routes']:
 for ix in [0,-1]:
  p=r['xy'][ix];q=r['xy'][1 if ix==0 else -2];key=tuple(round(v,4) for v in p);endpoint_map.setdefault(key,[]).append((r,p,q))
for key,ends in endpoint_map.items():
 if len(ends)!=1:continue
 r,p,q=ends[0]
 if r['tags'].get('service') not in ['siding','yard','spur']:continue
 if abs(p[1])>D['bounds_xy'][3]-3 or abs(p[0])>abs(D['bounds_xy'][0])-3:continue
 if any(math.dist(p,n['xy'])<.15 for n in D['turnout_nodes']):continue
 dx,dy=p[0]-q[0],p[1]-q[1];le=math.hypot(dx,dy);dx/=le;dy/=le;nx,ny=-dy,dx
 for sg in [-1,1]:
  a=(p[0]+nx*sg*.85-dx*1.3,p[1]+ny*sg*.85-dy*1.3,.50);b=(p[0]+nx*sg*.85,p[1]+ny*sg*.85,1.5);beam('Mapped siding buffer diagonal',a,b,.15,M['railweb'])
 beam('Bufferstop crossbeam',(p[0]+nx*1.2,p[1]+ny*1.2,1.4),(p[0]-nx*1.2,p[1]-ny*1.2,1.4),.22,M['red']);box('Bufferstop white panel',(p[0],p[1],1.8),(.5,.16,.5),M['white'])
# Source-aligned catenary, 6.3 m contact height (5.665m above rail), harmless unmapped portal locations.
coll('02 | Electrification and rail services')
for r in D['routes']:
 if r['tags'].get('electrified')=='no':continue
 pts=r['xy'];tube('Contact wire OSM route '+r['id'],[(x,y,6.30) for x,y in pts],.013,M['dark']);tube('Messenger OSM route '+r['id'],[(x,y,7.02) for x,y in pts],.014,M['dark'])
 for x,y,dx,dy in sample(pts,12):beam('Catenary dropper',(x,y,6.30),(x,y,7.02),.014,M['steel'])
ys=range(-1000,1001,54)
for y in ys:
 xs=[at_y(r['xy'],y) for r in D['routes'] if min(p[1] for p in r['xy'])<=y<=max(p[1] for p in r['xy'])]
 if not xs:continue
 lo,hi=min(xs),max(xs)
 if hi-lo<2:
  sgn=-D['main_building']['public_side'];xx=lo+sgn*3.5;beam('Single line OHE mast',(xx,y,.0),(xx,y,8.1),.20,M['steel']);beam('Cantilever arm',(xx,y,7.0),(lo-sgn*.6,y,7.0),.075,M['steel']);beam('Cantilever stay',(xx,y,8),(lo,y,7),.055,M['steel'])
 else:
  xx0,xx1=lo-11.5,hi+11.5
  for xx in [xx0,xx1]:
   box('Portal foundation',(xx,y,.25),(.9,.9,.5),M['stone']);beam('OHE portal upright',(xx,y,.4),(xx,y,8.0),.19,M['steel'])
  beam('OHE portal top',(xx0,y,8.0),(xx1,y,8.0),.17,M['steel']);beam('OHE portal lower chord',(xx0,y,7.5),(xx1,y,7.5),.14,M['steel'])
  for i in range(int((xx1-xx0)/2)):
   x=xx0+i*2;beam('Portal truss diagonal',(x,y,7.5),(min(x+2,xx1),y,8),.045,M['steel'])
  for xx in xs:beam('Registration drop',(xx,y,7.5),(xx,y,6.35),.045,M['steel']);cyl('OHE insulator',(xx,y,7.15),.13,.30,M['dark'])
 for xx in [lo-3.4,hi+3.4]:
  if y%108==0:box('Trackside relay cabinet',(xx,y+4,.95),(.7,.6,1.4),M['ivory']);box('Cabinet foundation',(xx,y+4,.16),(.95,.85,.3),M['stone'])
# Signal visual positions beyond platform, not current certified signalling scheme.
for i,r in enumerate(D['routes'][:len(D['transect_road_centers_x'])]):
 for yy in [-390,390]:
  x=at_y(r['xy'],yy)+3.1;beam('Visual signal mast',(x,yy,0),(x,yy,4.2),.11,M['steel']);box('Signal black housing',(x,yy,3.85),(.45,.3,1.3),M['dark'])
  for zz in [3.42,3.85,4.28]:cyl('Signal lens',(x,yy-.18,zz),.10,.035,M['red'],12)

coll('03 | Platforms and hardscape')
platform_info=[]
for i,p in enumerate(D['platforms']):
 pp=p['xy'];mesh('Platform body '+str(i+1)+' | '+p['basis'],p['body_mesh']['v'],p['body_mesh']['f'],M['red']);mesh('Platform paving '+str(i+1),p['paving_mesh']['v'],p['paving_mesh']['f'],M['stone']);bounds=[min(a[0] for a in pp),min(a[1] for a in pp),max(a[0] for a in pp),max(a[1] for a in pp)];midy=(bounds[1]+bounds[3])/2
 # safety strips conform exactly to source perimeter; stop at every end.
 for a,b in zip(pp,pp[1:]):
  le=math.dist(a,b)
  if le<4:continue
  dx,dy=(b[0]-a[0])/le,(b[1]-a[1])/le
  beam('Platform coping',[a[0],a[1],1.43],[b[0],b[1],1.43],.22,M['white'],.10)
  nx,ny=-dy,dx;mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
  if not inside((mx+nx*.4,my+ny*.4),pp):nx,ny=-nx,-ny
  beam('Safety line',[a[0]+nx*.48,a[1]+ny*.48,1.459],[b[0]+nx*.48,b[1]+ny*.48,1.459],.16,M['yellow'],.012)
 # Visible checker red/grey tile band using original tiled geometry, center-zone only.
 for yy in range(int(max(bounds[1],-300)),int(min(bounds[3],400)),2):
  sp=platform_span(pp,yy)
  if not sp:continue
  for xx in [sp[0]+1.1,sp[1]-1.1]:
   if inside((xx,yy),pp):box('Red platform edge paving',(xx,yy,1.462),(.8,1.94,.018),M['stone'] if CODE=='EZP' else M['pavers'])
 sp=platform_span(pp,midy) or (bounds[0],bounds[2]);cx=(sp[0]+sp[1])/2
 platform_info.append({'x':cx,'y':midy,'bounds':bounds,'poly':pp,'width':sp[1]-sp[0],'ref':p['ref'] or str(i+1)})
 # platform signage at both ends, benches and lights along route
 for yy in [bounds[1]+15,bounds[3]-15]:
  sp=platform_span(pp,yy)
  if not sp:continue
  x=(sp[0]+sp[1])/2;ww=min(4.8,sp[1]-sp[0]-1)
  box('Yellow nameboard',(x,yy,3.22),(ww,.12,1.72),M['yellow']);plane('Trilingual nameboard',(x,yy-.067,3.22),ww*.95,1.60,SIGN)
  for sg in [-1,1]:box('Nameboard upright',(x+sg*(ww/2-.14),yy,2.48),(.13,.16,2.10),M['white']);box('Nameboard black foot',(x+sg*(ww/2-.14),yy,1.64),(.15,.18,.45),M['dark'])
 for yy in range(int(bounds[1]+35),int(bounds[3]-20),35):
  if abs(yy-D['main_building']['center'][1])<6:continue
  if len(D['platforms'])>1 and D['main_building']['center'][1]+BO-19<yy<D['main_building']['center'][1]+BO+7:continue
  sp=platform_span(pp,yy)
  if not sp:continue
  x=(sp[0]+sp[1])/2
  # Benches lie lengthwise along the platform, leaving broad walking aisle.
  box('Bench stone seat',(x,yy,1.98),(.58,2.5,.14),M['dark'] if CODE=='VAY' else M['red'])
  if CODE!='VAY':box('Bench back slab',(x+.25,yy,2.32),(.10,2.5,.6),M['red'])
  for sy in [-.9,.9]:box('Bench sculpted concrete leg',(x,yy+sy,1.73),(.48,.25,.45),M['stone'])
  if yy%70<35 and abs(yy+8-D['main_building']['center'][1])>6 and not(len(D['platforms'])>1 and D['main_building']['center'][1]+BO-19<yy+8<D['main_building']['center'][1]+BO+7):
   beam('Platform LED pole',(x,yy+8,1.45),(x,yy+8,6.0),.07,M['steel']);beam('LED cantilever',(x,yy+8,6),(x+.9,yy+8,6),.06,M['steel']);box('LED luminaire',(x+.7,yy+8,5.97),(1.0,.22,.09),M['white'])
 # Continuous boundary fence on outer side for side platforms only.
 nearest=[r for r in D['routes'] if abs(at_y(r['xy'],midy)-cx)<18]
 tracks_left=any(at_y(r['xy'],midy)<cx for r in nearest);tracks_right=any(at_y(r['xy'],midy)>cx for r in nearest)
 if not (tracks_left and tracks_right):
  outer=1 if tracks_left else -1
  for yy in range(int(bounds[1]+5),int(bounds[3]-5),2):
   # Leave entry and maintenance gaps.
   if abs(yy-D['main_building']['center'][1])<D['main_building']['length']/2+5:continue
   sp=platform_span(pp,yy)
   if not sp:continue
   xx=(sp[1]-.25) if outer>0 else (sp[0]+.25);box('Boundary fence pier',(xx,yy,2.03),(.20,.20,1.16),M['white'] if CODE=='VAY' else M['aqua'] if CODE=='EZP' else M['red'])
   if CODE=='VAY':
    box('Vayalar solid white boundary wall',(xx,yy+1,1.98),(.18,2,1.05),M['white']);continue
   for z in [1.71,2.21]:box('Fence horizontal rails',(xx,yy+1,z),(.09,1.8,.09),M['white'])
   for sy in [.3,.6,.9,1.2,1.5]:box('Fence concrete picket',(xx,yy+sy,2),(.08,.08,.88),M['white'])

# Architectural profiles derived from inspected photographs, with dimensions and unseen rooms reconstructed.
STYLE={'KUMM':('peach','peach','flat',6.2),'AROR':('white','red','flat',3.6),'EZP':('ivory','red','flat',3.4),'TUVR':('ivory','red','flat',4.9),'VAY':('aqua','dark','flat',3.4),'SRTL':('cream','dark','twin_gable',5.8),'TRVZ':('ivory','red','flat',3.4),'MAKM':('cream','red','flat',3.9),'KAVR':('ivory','red','flat',3.4),'TMPY':('cream','red','flat',3.4),'ALLP':('ivory','peach','two_storey',7.8),'PNPR':('cream','blue','flat',3.5),'AMPA':('cream','dark','clerestory',5.7),'TZH':('cream','orange','flat',3.5),'KVTA':('cream','orange','flat',3.9),'HAD':('cream','red','gable',6.0),'CHPD':('cream','peach','flat',3.7),'KYJ':('ivory','red','broad_portal',5.5)}
bx,by=D['main_building']['center'];DEP=D['main_building']['width'];LEN=D['main_building']['length'];SIDE=D['main_building']['public_side'];H=3.8

def loc(u,v,z):return(bx+SIDE*v,by+u,z)
def b0(n,u,v,z,du,dv,dz,m):box(n,loc(u,v,z),(dv,du,dz),m)
def be0(n,a,b,w,m):beam(n,loc(*a),loc(*b),w,m)
def tex0(n,u,v,z,w,h,m):return plane(n,loc(u,v,z),w,h,m,'X',SIDE if v>=0 else -SIDE)
def text0(n,t,u,v,z,size,m):return txt(n,t,loc(u,v,z),size,m,(math.pi/2,0,math.pi/2 if SIDE>0 else -math.pi/2))

def window(u,v,width=1.7,height=1.35,z=3):
 b0('Recessed glazing',u,v,z,width,.05,height,M['wood'] if CODE=='AROR' else M['glass'])
 if CODE=='AROR':
  for side in [-1,1]:
   u0=u+side*width*.27;leaf=box('Aroor hinged wooden shutter',loc(u0,v+.25,z),(.09,width*.49,height),M['wood'],False);leaf.rotation_euler[2]=side*.35
   for zz in [z-height*.38,z+height*.38]:b0('Wood shutter raised panel rail',u0,v+.33,zz,width*.42,.08,.075,M['red'])
 for uu in [u-width/2,u,u+width/2]:b0('Window frame',uu,v+SIDE*.045,z,.055,.08,height+.1,M['wood'])
 for zz in [z-height/2,z,z+height/2]:b0('Window horizontal rail',u,v+.065,zz,width,.07,.05,M['wood'])
 for uu in [u-width*.35,u-width*.18,u+width*.18,u+width*.35]:b0('Window security grille',uu,v+.10,z,.025,.025,height,M['dark'])

def rooflocal(u,v,w,d,eave,rise,m):
 p=[loc(u-w/2,v-d/2,eave),loc(u+w/2,v-d/2,eave),loc(u+w/2,v,eave+rise),loc(u-w/2,v,eave+rise),loc(u-w/2,v+d/2,eave),loc(u+w/2,v+d/2,eave)]
 o=mesh('Pitched roof shell',p,[(0,1,2,3),(3,2,5,4)],m);sol=o.modifiers.new('Roof thickness','SOLIDIFY');sol.thickness=.08
 for vv in [-d/2,d/2]:be0('Roof eaves',(u-w/2,v+vv,eave),(u+w/2,v+vv,eave),.16,M['white'])
 for uu in [u-w/2,u+w/2]:
  be0('Roof rake',(uu,v-d/2,eave),(uu,v,eave+rise),.12,M['red']);be0('Roof rake',(uu,v,eave+rise),(uu,v+d/2,eave),.12,M['red'])
 for ii in range(int(w/.22)):
  uu=u-w/2+ii*.22
  for sg in [-1,1]:be0('Visible roof tile rib',(uu,v,eave+rise+.025),(uu,v+sg*d/2,eave+.025),.033,m)

def chair(u,v,z=1.45):
 b0('Waiting seat',u,v,z+.46,.58,.58,.09,M['blue']);b0('Waiting seat back',u,v+.23,z+.84,.58,.08,.66,M['blue'])
 for a in [-.22,.22]:
  for b in [-.20,.20]:be0('Chair tubular leg',(u+a,v+b,z),(u+a,v+b,z+.43),.028,M['steel'])

def fan(u,v,z):
 be0('Ceiling fan stem',(u,v,z),(u,v,z-.42),.03,M['dark']);cyl('Fan hub',loc(u,v,z-.43),.11,.12,M['ivory'])
 for ang in [0,math.tau/3,math.tau*2/3]:
  a=loc(u+.15*math.cos(ang),v+.15*math.sin(ang),z-.46);b=loc(u+.68*math.cos(ang),v+.68*math.sin(ang),z-.46);beam('Fan blade',a,b,.12,M['ivory'],.035)

if CODE!='TNU':
 wallcol,trimcol,style,toph=STYLE[CODE];wall=M[wallcol];trim=M[trimcol];LEN=max(LEN,12);DEP=max(DEP,7);H=4.05 if LEN>25 else 3.65;z0=1.45;eave=z0+H
 coll('04 | '+S['station_name']+' photographed architecture')
 b0('Main hall terrazzo floor',0,0,1.42,LEN,DEP,.16,M['stone']);b0('Foundation plinth',0,0,.71,LEN+.3,DEP+.3,1.4,M['dark'] if CODE=='VAY' else M['basalt'] if CODE=='TMPY' else M['red'])
 # Two side walls and open central entrances; no facade texture hiding inaccessible solid box.
 for u in [-LEN/2,LEN/2]:b0('End masonry wall',u,0,z0+H/2,.24,DEP,H,wall)
 EH=1.0 if CODE in ['AROR','EZP','VAY','KAVR','TMPY','PNPR','TRVZ'] else 1.7
 for v in [-DEP/2,DEP/2]:
  for sg in [-1,1]:
   le=LEN/2-EH;u=sg*(EH+le/2);b0('Facade lower wall beneath windows',u,v,z0+.64,le,.26,1.28,wall);b0('Facade lintel strip',u,v,eave-.34,le,.26,.68,wall)
   # Window openings remain as physically thin glass framed within masonry bays.
   n=max(1,int(le/3.1));pw=le/n
   for j in range(n+1):b0('Facade structural pier',sg*(EH+j*pw),v,z0+H/2,.24,.28,H,wall)
   for j in range(n):
    uc=sg*(EH+(j+.5)*pw);ww=pw-.33
    if CODE in ['AROR','EZP','VAY','KAVR','TMPY','PNPR','TRVZ']:
     ww=min(1.65,ww);blank=(pw-.33-ww)/2
     if blank>.05:
      for ss in [-1,1]:b0('Small halt masonry window surround',uc+ss*(ww/2+blank/2),v,z0+2.04,blank,.26,1.6,wall)
    window(uc,v+.01,ww,1.45,z0+2.0)
  b0('Entrance lintel',0,v,eave-.25,2*EH+.25,.3,.50,wall)
  for u in [-EH-.05,EH+.05]:b0('Entrance reveal pilaster',u,v+.05,z0+H/2,.24,.42,H,trim)
  # Folding gate parked open in side recess.
  for sg in [-1,1]:
   for j in range(7):
    u=sg*(EH-.14+j*.026);be0('Collapsible gate vertical',(u,v+.17,z0),(u,v+.17,z0+2.85),.022,M['white'] if CODE=='CHPD' else M['dark'])
   for zz in [1.7,2.45,3.20,3.9]:be0('Gate folded diamond',(sg*(EH-.2),v+.17,zz),(sg*(EH+.03),v+.17,zz+.5),.018,M['dark'])
 b0('Hall ceiling',0,0,eave+.08,LEN+.50,DEP+.50,.18,wall)
 # Front portico: trim, observed piers and weather shade.
 porchwidth=min(LEN+1,16 if LEN<30 else 25);porchdepth=3.0 if CODE!='KUMM' else 3.5
 if CODE=='TMPY':porchwidth=3.2;porchdepth=1.2
 if CODE=='TUVR':porchwidth=12.0
 b0('Portico flat canopy',0,DEP/2+porchdepth/2,eave-.35,porchwidth,porchdepth+.3,.28,trim)
 for u in ([] if CODE=='TMPY' else [-porchwidth/2+.4,porchwidth/2-.4]):
  b0('Portico square column',u,DEP/2+porchdepth-.2,z0+(H-.45)/2,.10 if CODE in ['VAY','PNPR'] else .40,.10 if CODE in ['VAY','PNPR'] else .42,H-.45,trim)
  b0('Portico base block',u,DEP/2+porchdepth-.2,z0+.22,.6,.62,.44,M['dark'])
 if CODE not in ['ALLP','TZH','VAY','PNPR']:tex0('Trilingual entrance fascia',0,DEP/2+porchdepth+.17,eave-.35,porchwidth-.3,.72,FASC)
 if CODE=='TZH':tex0('Thakazhi compact white station-name panel',LEN*.23,DEP/2+.21,eave-.62,5.8,.68,FASC)
 # Continuous raised portico floor and platform threshold bridge: no unsupported entrance/drop.
 b0('Portico raised floor landing',0,DEP/2+porchdepth/2,1.37,porchwidth,porchdepth,.16,M['stone'])
 if platform_info:
  nearest_p=min(platform_info,key=lambda p:abs(p['x']-bx));sp=platform_span(nearest_p['poly'],by)
  if sp:
   rearx=bx-SIDE*DEP/2;edge=sp[1] if SIDE>0 else sp[0]
   bridge_width=abs(rearx-edge)+.20
   box('Platform entrance threshold bridge',((rearx+edge)/2,by,1.37),(bridge_width,3.35,.16),M['stone'])
 # Approach steps plus accessible side ramp. Reconstructed practical circulation.
 for j in range(6):b0('Entrance step',0,DEP/2+porchdepth+(.5*j),1.45-(j+.5)*(1.45/6),porchwidth*.6,.52,1.45/6,M['stone'])
 ru=porchwidth/2+1.1
 b0('Accessible ramp top landing connector',porchwidth/2+.45,DEP/2+1.2,1.37,2.0,1.6,.16,M['stone'])
 # 1:12 long ramp runs parallel to frontage; landing then sloped ramp mesh.
 rampstart=loc(ru,DEP/2+1.2,1.45);rampend=loc(ru+17.4,DEP/2+1.2,.0)
 for dv in [-.75,.75]:be0('Ramp handrail',(ru,DEP/2+1.2+dv,2.45),(ru+17.4,DEP/2+1.2+dv,1.0),.045,M['steel'])
 a=[loc(ru,DEP/2+.45,1.45),loc(ru,DEP/2+1.95,1.45),loc(ru+17.4,DEP/2+1.95,.0),loc(ru+17.4,DEP/2+.45,.0)];mesh('Accessible approach ramp',a,[(0,1,2,3)],M['stone'])
 if style in ['flat','clerestory']:
  rooflocal(0,0,LEN+1,DEP+1,eave+.23,.35,M['roof'])
  if style=='clerestory':
   cw=min(16,LEN*.65);b0('Raised center clerestory',0,0,eave+.55,cw,DEP*.68,1.1,wall)
   for u in [-cw*.35,0,cw*.35]:window(u,DEP*.34+.03,2,1,eave+.55)
   b0('Clerestory projecting roof',0,0,eave+1.16,cw+1,DEP*.68+1,.20,wall)
   for u in [-cw/2+.8,-cw/4,0,cw/4,cw/2-.8]:
    for j in range(3):b0('Stepped corbel',u,DEP*.34+.22+j*.1,eave+.8+j*.12,.35,.5,.14,M['red'])
 elif style=='twin_gable':
  rooflocal(0,0,LEN+1,DEP+1,eave,.9,M['tile'])
  for u in [-4.5,4.5]:
   # Pair of Kerala gables faces the forecourt.
   vtx=[loc(u-3.8,DEP/2+2.9,eave-.35),loc(u+3.8,DEP/2+2.9,eave-.35),loc(u,DEP/2+2.9,eave+1.25)];mesh('Twin front gable',vtx,[(0,1,2)],wall)
   be0('Gable border',(u-3.8,DEP/2+3,eave-.35),(u,DEP/2+3,eave+1.25),.18,M['red']);be0('Gable border',(u,DEP/2+3,eave+1.25),(u+3.8,DEP/2+3,eave-.35),.18,M['red'])
 elif style=='gable':
  rooflocal(0,0,LEN+1,DEP+1,eave,1.4,M['tile'])
  vtx=[loc(-5,DEP/2+3,eave-.2),loc(5,DEP/2+3,eave-.2),loc(0,DEP/2+3,eave+1.7)];mesh('Kerala frontage pediment',vtx,[(0,1,2)],trim)
 if CODE=='HAD':
  for u in range(int(-min(15,LEN/2)),int(min(15,LEN/2))+1,3):
   for j in range(3):b0('Haripad red stepped eave bracket',u,DEP/2+.22+j*.12,eave-.15+j*.17,.46,.56,.18,trim)
 elif style=='two_storey':
  cw=min(36,LEN*.50);b0('Upper floor slab',0,0,eave+.22,cw,DEP,.26,wall)
  for u in [-cw/2,cw/2]:b0('Upper end wall',u,0,eave+1.7,.3,DEP,3,wall)
  for u in range(int(-cw/2),int(cw/2)+1,4):
   b0('Upper gallery pier',u,DEP/2,eave+1.7,.45,.4,3,M['cream']);b0('Upper gallery base',u+1.7,DEP/2,eave+.75,3.4,.23,.5,wall)
   for zz in [eave+1.1+k*.11 for k in range(17)]:b0('Maroon upper ventilation louver',u+1.7,DEP/2-.14,zz,3.45,.20,.065,M['red'])
  b0('Upper rear wall',0,-DEP/2,eave+1.7,cw,.28,3,wall);b0('Upper flat roof slab',0,0,eave+3.3,cw+1,DEP+1,.25,wall)
  # Feb2020 photograph shows a bare roof-frame; represented as dated architectural variant.
  for u in range(int(-cw/2),int(cw/2)+1,4):
   be0('Dated rooftop frame truss',(u,-DEP/2,eave+3.5),(u,0,eave+5),.08,M['red']);be0('Dated rooftop frame truss',(u,0,eave+5),(u,DEP/2,eave+3.5),.08,M['red'])
  for v in [-DEP/2,0,DEP/2]:be0('Rooftop longitudinal purlin',(-cw/2,v,eave+3.5+(1.5 if v==0 else 0)),(cw/2,v,eave+3.5+(1.5 if v==0 else 0)),.07,M['red'])
  # Hipped portico covers main entrance, cream fascia and dark stone-clad piers.
  pw=porchwidth;pv=DEP/2+1.7;pd=4.3;zz=eave-.20;rr=1.0
  vv=[loc(-pw/2,pv-pd/2,zz),loc(pw/2,pv-pd/2,zz),loc(pw/2,pv+pd/2,zz),loc(-pw/2,pv+pd/2,zz),loc(-pw/2+2.0,pv,zz+rr),loc(pw/2-2.0,pv,zz+rr)]
  mesh('Alappuzha hipped tile entrance roof',vv,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],M['tile'])
  tex0('Alappuzha raised-name panel',0,DEP/2+.26,eave+3.28,min(23,cw-2),.95,FASC)
  for u in [-porchwidth/2+.4,porchwidth/2-.4,-porchwidth/5,porchwidth/5]:b0('Black polished entry column',u,DEP/2+porchdepth-.2,z0+(H-.45)/2,.7,.72,H-.45,M['dark'])
  for u in [-9,-3,3,9]:window(u,-DEP/2-.04,2.7,1.7,eave+1.7)
  for u in [-porchwidth*.38,porchwidth*.38]:
   for a in range(6):
    for b in range(6):b0('Entrance decorative lattice',u+(a-2.5)*.22,DEP/2+.12,2.1+b*.22,.15,.10,.15,wall)
 elif style=='broad_portal':
  b0('Broad junction portal upper',0,0,eave+1.25,porchwidth+5,DEP,2.4,wall);b0('Junction broad red crown',0,DEP/2+.55,eave+3.0,porchwidth+7,1.6,1.8,trim)
  b0('Junction stepped crown cap',0,DEP/2+.55,eave+4.0,porchwidth*.45,1.5,.40,trim)
  # Low wide gabled portal roof, visible trilingual face and small terracotta ceremonial cap.
  pw=porchwidth;v=DEP/2+porchdepth+.02
  vv=[loc(-pw/2,v,eave-.40),loc(pw/2,v,eave-.40),loc(0,v,eave+1.25)];mesh('Kayamkulam entrance gable',vv,[(0,1,2)],wall)
  be0('Entrance red rake',(-pw/2,v+.05,eave-.40),(0,v+.05,eave+1.25),.16,trim);be0('Entrance red rake',(0,v+.05,eave+1.25),(pw/2,v+.05,eave-.40),.16,trim)
  vv=[loc(-2.7,DEP/2,eave+1.4),loc(2.7,DEP/2,eave+1.4),loc(2.7,DEP/2+4,eave+1.4),loc(-2.7,DEP/2+4,eave+1.4),loc(0,DEP/2+2,eave+2.8)];mesh('Terracotta pyramidal entrance crown',vv,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],M['tile']);cyl('Terracotta finial',loc(0,DEP/2+2,eave+3.12),.11,.7,M['tile'],12)
  for u in [-porchwidth/2+.4,0,porchwidth/2-.4]:b0('Pale central portal column',u,DEP/2+porchdepth-.2,z0+(H-.45)/2,.65,.65,H-.45,wall)
  for u in [-11,-5.5,0,5.5,11]:b0('Junction roofline vertical trim',u,DEP/2+1.17,eave+1.45,.23,.08,2.6,trim)
 if CODE=='KUMM':
  b0('Kumbalam salmon upper pavilion',0,0,6.23,LEN,DEP,1.95,M['peach']);rooflocal(0,0,LEN+.7,DEP+.7,7.23,.38,M['roof'])
  for u in [-LEN/2+.5,-LEN/4,0,LEN/4,LEN/2-.5]:
   for j in range(3):b0('Salmon stepped upper buttress',u,DEP/2+.15+j*.10,6.3+j*.30,.40,.50,.32,M['peach'])
 if CODE=='KVTA':
  for v in [-DEP/2-.15,DEP/2+.15]:b0('Karuvatta broad orange parapet',0,v,eave+.13,LEN+.35,.25,.48,M['orange'])
 if CODE=='CHPD':
  for v in [-DEP/2-.16,DEP/2+.16]:
   b0('Cheppad salmon lower wall band',0,v,z0+.4,LEN,.08,.8,M['peach']);b0('Cheppad thin upper entry stripe',0,v,eave-.28,LEN,.10,.16,M['orange'])
   for u in [-3,3]:
    b0('Cheppad black timetable board',u,v+(.06 if v>0 else -.06),3.0,1.5,.045,1.4,M['dark'])
    for j in range(7):b0('Timetable chalk rules',u,v+(.09 if v>0 else -.09),2.55+j*.14,1.2,.01,.012,M['ivory'])
 if CODE=='TMPY':
  rooflocal(0,0,LEN+2.7,DEP+3.0,eave+1.5,.45,M['roof'])
  for u in [-LEN/2,LEN/2]:
   for v in [-DEP/2,DEP/2]:be0('Tumboli raised roof frame',(u,v,eave+.15),(u,v,eave+1.65),.075,M['dark'])
  for u in [-LEN*.30,LEN*.30]:
   b0('Small separate window brow',u,DEP/2+.37,4.36,2.15,.75,.14,M['red'])
   for j in range(7):be0('Tumboli red grille diagonal',(u-.67+j*.18,DEP/2+.14,2.75),(u-.15+j*.18,DEP/2+.14,4.00),.027,M['red'])
 if CODE in ['VAY','PNPR']:
  rm=M['roofgreen'] if CODE=='VAY' else M['blue'];rooflen=LEN+2.0
  # Full-front lean-to awning copied in form from photographed rural facade.
  verts=[];faces=[];n=int(rooflen/.18)
  for vv,zz in [(DEP/2,eave+.40),(DEP/2+4.2,eave-.45)]:
   for j in range(n+1):verts.append(loc(-rooflen/2+rooflen*j/n,vv,zz+.028*(j%2)))
  for j in range(n):faces.append((j,j+1,n+j+2,n+j+1))
  mesh('Photographed full-front lean-to awning',verts,faces,rm)
  be0('White front rain gutter',(-rooflen/2,DEP/2+4.2,eave-.44),(rooflen/2,DEP/2+4.2,eave-.44),.10,M['white'])
  for u in [-LEN/2+.4,0,LEN/2-.4]:be0('Thin veranda post',(u,DEP/2+4,1.45),(u,DEP/2+4,eave-.45),.065,M['dark'] if CODE=='VAY' else M['blue'])
  b0('Halt parapet fascia',0,DEP/2+.08,eave+.60,LEN+.3,.22,.50,M['aqua'] if CODE=='VAY' else M['red'])
  tex0('Photographed white upper name panel',0,DEP/2+.22,eave+.63,min(LEN-1,6),.63,FASC)
 if CODE=='TZH':
  rooflocal(0,0,LEN+5,DEP+7,eave+1.1,.35,M['roofblue'])
  for v in [-DEP/2-.12,DEP/2+.12]:
   b0('Thakazhi deep orange fascia',0,v,eave-.10,LEN+.2,.2,.48,M['orange'])
   tex0('Thakazhi white station-name panel',LEN*.23,v+.01,eave-.60,5.6,.66,FASC)
  for u in [-LEN*.27,LEN*.27]:
   for j in range(6):be0('Thakazhi lattice diagonals',(u-.72+j*.24,-DEP/2-.16,2.9),(u-.1+j*.24,-DEP/2-.16,4.0),.04,M['orange'])
 if CODE=='AROR':
  rooflocal(0,1.0,LEN+3,DEP+5,eave+.85,.50,M['roof'])
  for u in [-LEN/2-1,LEN/2+1]:
   for v in [-DEP/2-.5,DEP/2+2]:be0('Aroor overroof steel post',(u,v,1.45),(u,v,eave+.85),.07,M['steel'])
  b0('Aroor red-brown flatroof fascia',0,DEP/2+.18,eave+.05,LEN+.3,.14,.28,M['red'])
 # Rear station identity, notices and clock.
 tex0('Platform station fascia',0,-DEP/2-.18,eave-.1,min(LEN-1,13),.78,FASC)
 for u in [-2.5,2.5]:tex0('Station notice',u,DEP/2+.20,2.9,.6,.85,NOTICE)
 text0('Building room label','BOOKING OFFICE',LEN*.30,DEP/2+.24,4.0,.23,M['dark'])
 # Exposed downpipes, coping and portico details seen on regional station facades.
 for u in [-LEN/2+.4,LEN/2-.4]:
  be0('Rainwater downpipe',(u,DEP/2+.26,1.55),(u,DEP/2+.26,eave+.1),.075,M['ivory'])
  for zz in [1.9,3.1,4.5]:b0('Downpipe wall clamp',u,DEP/2+.22,zz,.16,.13,.035,M['dark'])
 for u in ([] if CODE=='TMPY' else [-porchwidth/2+.4,porchwidth/2-.4]):
  b0('Portico column capital',u,DEP/2+porchdepth-.2,eave-.62,.62,.65,.16,trim)
 b0('Front porch bench seat',-porchwidth/2+2,DEP/2+1.0,1.95,2.7,.58,.14,M['red'])
 for u in [-porchwidth/2+1,-porchwidth/2+3]:b0('Front bench pedestal',u,DEP/2+1,1.70,.30,.48,.45,M['stone'])
 coll('05 | Furnished reconstructed interiors')
 # Ticket-office partition with real service opening and counter shelf.
 tu=min(LEN/2-3.3,6.4);vfront=.4
 # Staff enclosure behind counter only. Public foreground stays open to the through hall.
  # Left side includes a 1.1 m door opening into the room, avoiding sealed inaccessible rooms.
 b0('Ticket office end partition',tu+2.2,-DEP/4+.45,3.0,.16,DEP/2-.1,3.1,wall)
 for vv,dd in [((-DEP/2+.5-2.3)/2,max(.2,DEP/2-2.8)),((-.9+.4)/2,1.3)]:b0('Ticket office doorway jamb wall',tu-2.2,vv,3.0,.16,dd,3.1,wall)
 b0('Ticket office door lintel',tu-2.2,-1.6,4.18,.16,1.4,.80,wall)
 b0('Ticket counter lower wall',tu,vfront,2.01,4.25,.17,1.12,wall);b0('Ticket counter upper wall',tu,vfront,4.27,4.25,.17,.87,wall)
 b0('Ticket counter worktop',tu,vfront,2.65,4.5,.65,.10,M['wood'])
 for u in [tu-1.8,tu,tu+1.8]:b0('Ticket window mullion',u,vfront,3.45,.055,.08,1.50,M['steel'])
 for u in [tu-1,tu+1]:
  b0('Computer monitor',u,vfront-1,3.0,.48,.10,.36,M['dark']);b0('Desk work surface',u,vfront-1.3,2.24,1.6,.8,.08,M['wood']);b0('Desk pedestal',u-.5,vfront-1.3,1.83,.45,.7,.76,M['ivory']);chair(u,vfront-2.1)
  b0('Keyboard',u,vfront-1.03,2.31,.43,.17,.045,M['dark']);b0('Ticket printer',u+.5,vfront-1.3,2.45,.28,.33,.30,M['ivory'])
 text0('Ticket window label','TICKETS',tu,vfront+.13,4.35,.32,M['blue'])
 wu=-min(LEN/2-3.5,6.5)
 for u in [wu-.9,wu,wu+.9]:
  for v in [1.25,2.65]:chair(u,v)
 for u in [wu-1.0,wu+1.0]:b0('Waiting table',u,-.4,1.9,.6,.6,.7,M['wood'])
 for u in [-min(4,LEN/4),min(4,LEN/4)]:fan(u,0,eave-.15);b0('Ceiling LED batten',u,1.6,eave-.16,1.25,.12,.07,M['white'])
 # Reconstructed basic water/sanitary fittings: no hidden large concourse.
 if LEN>25:
  u=-LEN/2+3.5
  for v in [-2,1]:
   b0('Toilet cubicle partition',u,v,2.9,.14,2.3,2.9,wall);b0('Toilet floor',u-1.2,v,1.49,2.3,2.1,.07,M['white']);b0('Cubicle door',u-1.1,v+1.1,2.60,1.5,.08,2.2,M['blue'])
   cyl('Toilet pedestal',loc(u-1.0,v-.4,1.73),.25,.46,M['white']);b0('Cistern',u-1,v-.8,2.14,.50,.21,.66,M['white'])
  b0('Wash basin plinth',u+2,2,1.98,.65,.52,.65,M['ivory']);b0('Basin rim',u+2,2,2.32,.77,.6,.12,M['white']);be0('Tap',(u+2,2.2,2.35),(u+2,2.2,2.65),.025,M['steel'])
 # Furnish reconstructed wing rooms instead of leaving long station blocks empty.
 if LEN>40:
  for sg in [-1,1]:
   for ii in range(int((LEN/2-10)/8)):
    uc=sg*(14+8*ii)
    if abs(uc)+3.7>LEN/2-.4:continue
    roomdepth=max(2.7,DEP/2-1.0);vc=-DEP/2+roomdepth/2+.25
    for uu in [uc-3.65,uc+3.65]:b0('Wing room partition',uu,vc,3.0,.14,roomdepth,3.1,wall)
    vf=-DEP/2+roomdepth+.25
    # Front with open 1.2 m doorway; keeps2m-plus shared circulation in foreground.
    b0('Wing room frontage',uc-1.0,vf,3.0,5.3,.14,3.1,wall);b0('Wing door far jamb',uc+3.3,vf,3.0,.65,.14,3.1,wall);b0('Wing door lintel',uc+2.05,vf,4.20,1.8,.14,.8,wall)
    if ii%2==0:
     b0('Wing office desk',uc,vc,2.22,1.8,.8,.09,M['wood'])
     for du in [-.72,.72]:b0('Office desk side support',uc+du,vc,1.83,.18,.72,.7,M['steel'])
     chair(uc,vc-.95);b0('Office monitor',uc,vc,2.56,.50,.12,.34,M['dark']);b0('Office keyboard',uc,vc+.25,2.29,.48,.18,.04,M['dark']);b0('Filing cabinet',uc-2.4,vc,2.40,.9,.55,1.9,M['ivory'])
     for zz in [1.70,2.1,2.5,2.9]:b0('Filing drawer handle',uc-2.4,vc+.29,zz,.27,.045,.035,M['steel'])
    else:
     for du in [-2.0,-1,0,1,2.0]:chair(uc+du,vc)
     b0('Waiting room luggage shelf',uc,vc-1,2.15,5,.48,.07,M['wood'])
    text0('Reconstructed room label','OFFICE' if ii%2==0 else 'WAITING',uc,vf+.10,4.33,.25,M['blue']);fan(uc,vc,eave-.15)
 # Subtle original terrazzo tile grid across the inspectable public lobby.
 for uu in range(int(-min(12,LEN/2-.8)*2),int(min(12,LEN/2-.8)*2)):
  for vv in range(int((-DEP/2+.7)*2),int((DEP/2-.5)*2)):
   if (uu+vv)%3==0:b0('Terrazzo patterned lobby tile',uu*.5,vv*.5,1.501,.485,.485,.002,M['ivory'])
 # Roof tanks are seen at Turavur; other small fittings are labeled visual reconstruction.
 if CODE=='TUVR':
  coll('04 | Turavur roof water tanks')
  for u in [-5,0,5]:
   b0('Turavur masonry tank pedestal',u,-1,eave+.40,1.65,1.60,.80,M['stone'])
   for du in [-.52,.52]:
    for dv in [-.52,.52]:be0('Turavur tank stand steel leg',(u+du,-1+dv,eave+.80),(u+du,-1+dv,eave+1.65),.065,M['steel'])
   b0('Tank stand steel deck',u,-1,eave+1.68,1.48,1.48,.08,M['steel']);cyl('Roof water tank',loc(u,-1,eave+2.42),.65,1.4,M['dark'],24)
   for j in range(1,7):
    zz=eave+1.72+j*.19;pts=[loc(u+.66*math.cos(k*math.tau/24),-1+.66*math.sin(k*math.tau/24),zz)for k in range(25)];tube('Tank moulded reinforcing ring',pts,.018,M['dark'])
   cyl('Tank filler cap',loc(u,-1,eave+3.18),.12,.12,M['dark'],12)

# Canopies and amenity kits sized to platform geometry; every placement tests bounds.
coll('06 | Platform shelters and furniture')
for i,p in enumerate(platform_info):
 b=p['bounds'];pp=p['poly'];length=(b[3]-b[1]);shelter_length=min(220 if CODE in ['ALLP','KYJ'] else 100 if CODE in ['SRTL','HAD','AMPA'] else 60 if CODE in ['TUVR','MAKM','KVTA','TZH','CHPD'] else 30,length*.60);cy=max(b[1]+shelter_length/2+12,min(by,b[3]-shelter_length/2-12));span=platform_span(pp,cy)
 if not span:continue
 cx=(span[0]+span[1])/2;width=max(2.7,min(7.6,span[1]-span[0]-1));z=5.30
 # halt small single lean roof; larger railway butterfly canopy clear track envelope.
 for yy in range(int(cy-shelter_length/2),int(cy+shelter_length/2)+1,7):
  if len(platform_info)>1 and by+BO-17<yy<by+BO+4:continue
  if abs(yy-by)<2:continue
  sp=platform_span(pp,yy)
  if not sp:continue
  xx=(sp[0]+sp[1])/2
  beam('Shelter central steel stanchion',(xx,yy,1.45),(xx,yy,z),.13,M['steel']);box('Shelter column base',(xx,yy,1.63),(.45,.45,.35),M['stone'])
  for sg in [-1,1]:
   beam('Butterfly roof truss',(xx,yy,z-.05),(xx+sg*width/2,yy,z+.70),.095,M['steel']);beam('Canopy lower truss',(xx,yy,z-.5),(xx+sg*width/2,yy,z+.7),.055,M['steel'])
   for tt in [.33,.66]:beam('Truss vertical web',(xx+sg*width/2*tt,yy,z-.5+1.2*tt),(xx+sg*width/2*tt,yy,z-.05+.75*tt),.035,M['steel'])
 for sg in [-1,1]:
  verts=[];faces=[];n=int(shelter_length/.22)
  for xx,zz in [(cx,z),(cx+sg*width/2,z+.72)]:
   for j in range(n+1):verts.append((xx,cy-shelter_length/2+shelter_length*j/n,zz+.032*(j%2)))
  for j in range(n):
   ym=cy-shelter_length/2+shelter_length*(j+.5)/n
   if len(platform_info)>1 and by+BO-17<ym<by+BO+4:continue
   faces.append((j,j+1,n+j+2,n+j+1))
  roofmat=M['roofblue'] if CODE in ['TZH','KVTA','KYJ','ALLP'] else M['roof']
  if CODE=='ALLP' and i==min(range(len(platform_info)),key=lambda k:abs(platform_info[k]['x']-bx)):roofmat=M['ivory']
  mesh('Corrugated butterfly roof sheet',verts,faces,roofmat)
 if CODE=='ALLP' and i==min(range(len(platform_info)),key=lambda k:abs(platform_info[k]['x']-bx)):
  # Observed cream ceiling panels and red-brown outer fascia on main platform canopy.
  for yy in range(int(cy-shelter_length/2),int(cy+shelter_length/2),3):
   if by+BO-17<yy<by+BO+4:continue
   box('Alappuzha cream canopy ceiling panel',(cx,yy,5.18),(width-.15,2.94,.08),M['ivory'])
  for sg in [-1,1]:box('Alappuzha red-brown canopy fascia',(cx+sg*width/2,cy,5.33),(.14,shelter_length,.34),M['red'])
 for yy in [cy-10,cy+10]:
  x=cx+.7;box('Litter bin blue body',(x,yy,1.92),(.45,.45,.9),M['blue']);box('Litter bin lid',(x,yy,2.39),(.50,.50,.07),M['dark'])
 if shelter_length>50:
  yy=cy+shelter_length/2+12;sp=platform_span(pp,yy)
  if sp:
   x=(sp[0]+sp[1])/2;box('Drinking water cabinet',(x,yy,2.15),(1.1,.65,1.4),M['steel']);box('Water basin shelf',(x,yy-.42,2.28),(1.15,.3,.08),M['white'])
   for q in [-.30,.30]:beam('Water tap',(x+q,yy-.34,2.5),(x+q,yy-.52,2.5),.023,M['steel'])
# Footbridge only where multi-platform station; exact span/position is reconstructed if no mapped bridge.
if len(platform_info)>1 and CODE not in ['TNU','KYJ']:
 coll('07 | Pedestrian footbridge reconstructed geometry')
 yy=by+BO;px=[]
 for p in platform_info:
  sp=platform_span(p['poly'],yy)
  if sp and sp[1]-sp[0]>4:px.append((sum(sp)/2,sp[1]-sp[0]))
 if len(px)>1:
  x0=min(q[0] for q in px);x1=max(q[0] for q in px);deck=8.55;box('Bridge deck',(sum([x0,x1])/2,yy,deck),(x1-x0+3,2.5,.30),M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
  for ys in [-1.17,1.17]:
   segments=[(x0-1.4,x1+1.4)]
   if ys<0:
    for xx,ww in px:
     out=[]
     for a,b in segments:
      if a<xx-1.15:out.append((a,min(b,xx-1.15)))
      if b>xx+1.15:out.append((max(a,xx+1.15),b))
     segments=[(a,b) for a,b in out if b>a]
   for a,b in segments:
    beam('Footbridge top rail',(a,yy+ys,deck+1.2),(b,yy+ys,deck+1.2),.065,M['white'] if CODE in ['KVTA','TZH'] else M['steel']);beam('Footbridge lower rail',(a,yy+ys,deck+.35),(b,yy+ys,deck+.35),.05,M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
   for xx in range(int(x0),int(x1)+2):
    if ys<0 and any(abs(xx-x)<1.15 for x,w in px):continue
    beam('Bridge baluster',(xx,yy+ys,deck),(xx,yy+ys,deck+1.2),.035,M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
  for x,w in px:
   for xx in [x-1.15,x+1.15]:
    beam('Footbridge pier',(xx,yy,1.45),(xx,yy,deck),.18,M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
   run=15.2;rise=deck+.15-1.45;steps=44;syend=yy-1.25
   for j in range(steps):
    zz=1.45+(j+1)*rise/steps-.05;sy=syend-run+(j+.5)*run/steps;box('Footbridge anti-slip tread',(x,sy,zz),(2.2,run/steps+.025,.10),M['red'] if CODE=='KVTA' else M['white'] if CODE=='TZH' else M['steel'])
   if CODE in ['KVTA','TZH']:
    verts=[(x-1.5,syend-run,3.80),(x+1.5,syend-run,3.80),(x+1.5,syend,deck+2.4),(x-1.5,syend,deck+2.4)];mesh('Photographed blue stair hood',verts,[(0,1,2,3)],M['roofblue'])
    for sg in [-1,1]:
     for frac in [0,.25,.50,.75,1]:
      yy1=syend-run+frac*run;floor=1.45+frac*rise;roof=3.80+frac*(deck+2.4-3.80);beam('Stair hood outside support',(x+sg*1.34,yy1,floor),(x+sg*1.34,yy1,roof),.065,M['white'])
   for sg in [-1,1]:
    beam('Stair stringer',(x+sg*1.05,syend-run,1.35),(x+sg*1.05,syend,deck+.05),.14,M['white'] if CODE in ['KVTA','TZH'] else M['steel']);beam('Stair handrail',(x+sg*1.02,syend-run,2.45),(x+sg*1.02,syend,deck+1.15),.055,M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
    for j in range(0,steps,4):beam('Stair baluster',(x+sg*1.02,syend-run+j*run/steps,1.45+j*rise/steps),(x+sg*1.02,syend-run+j*run/steps,2.45+j*rise/steps),.035,M['white'] if CODE in ['KVTA','TZH'] else M['steel'])
  box('Footbridge covered roof',(sum([x0,x1])/2,yy,deck+2.4),(x1-x0+4,3.2,.10),M['roofblue'] if CODE in ['KVTA','TZH'] else M['roof'])
  metrics['bridge_deck_underside_m']=deck-.15;metrics['bridge_deck_top_m']=deck+.15;metrics['stair_end_y']=yy-1.25;metrics['stair_landing_method']='Last tread ends at deck leading edge and top equals slab top8.70m; no treads run underneath solid deck.'

# Kayamkulam has a mapped dogleg pedestrian bridge. Preserve that distinctive plan.
if CODE=='KYJ' and D.get('bridge_deck_polygon'):
 coll('07 | Pedestrian footbridge reconstructed geometry')
 deck=8.55;pp=D['bridge_deck_polygon'];polyplate('KYJ mapped dogleg bridge deck',pp,8.40,8.70,M['steel']);polyplate('KYJ mapped dogleg roof',D['bridge_roof_polygon'],10.90,11.00,M['roofblue']);route=D['bridge_source']['xy'];flights=[]
 def deck_front_at(x):
  vals=[]
  for a,b in zip(pp,pp[1:]+pp[:1]):
   if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>.000001:vals.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
  return min(vals) if vals else None
 for p in platform_info:
  cx=p['x'];cand=[]
  for a,b in zip(route,route[1:]):
   if min(a[0],b[0])<=cx<=max(a[0],b[0]) and abs(b[0]-a[0])>.0001:cand.append((cx,a[1]+(b[1]-a[1])*(cx-a[0])/(b[0]-a[0])))
  if cand:fx,fy=cand[0]
  else:fx,fy=min(route,key=lambda v:abs(v[0]-cx))
  sp=platform_span(p['poly'],fy)
  if not sp or sp[1]-sp[0]<4:continue
  fx=max(sp[0]+1.30,min(sp[1]-1.30,fx));syend=deck_front_at(fx)
  if syend is None:continue
  flights.append({'x':fx,'end_y':syend,'start_y':syend-15.2,'deck_top_m':8.70,'platform_ref':p['ref']})
 for a,b in zip(pp,pp[1:]):
  le=math.dist(a,b);nn=max(1,int(math.ceil(le/.7)))
  for i in range(nn):
   t0=i/nn;t1=(i+1)/nn;aa=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0);bb=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1);mx,my=(aa[0]+bb[0])/2,(aa[1]+bb[1])/2
   if any(abs(mx-f['x'])<1.15 and abs(my-f['end_y'])<.32 for f in flights):continue
   beam('KYJ dogleg upper handrail',(*aa,9.75),(*bb,9.75),.055,M['steel']);beam('KYJ dogleg lower guard rail',(*aa,8.98),(*bb,8.98),.045,M['steel']);beam('KYJ bridge railing post',(*aa,8.70),(*aa,9.75),.033,M['steel'])
 for f in flights:
  x=f['x'];syend=f['end_y'];run=15.2;rise=7.25;steps=44;yc=syend+1.25
  for xx in[x-1.15,x+1.15]:
   beam('KYJ bridge platform support',(xx,yc,1.45),(xx,yc,8.55),.18,M['steel']);beam('KYJ bridge roof support',(xx,yc,8.70),(xx,yc,10.9),.08,M['steel'])
  for i in range(steps):
   zz=1.45+(i+1)*rise/steps-.05;yy=syend-run+(i+.5)*run/steps;box('KYJ dogleg stair tread',(x,yy,zz),(2.2,run/steps+.025,.10),M['steel'])
  for sg in[-1,1]:
   beam('KYJ stair stringer',(x+sg*1.05,syend-run,1.35),(x+sg*1.05,syend,8.60),.14,M['steel']);beam('KYJ stair handrail',(x+sg*1.02,syend-run,2.45),(x+sg*1.02,syend,9.70),.055,M['steel'])
   for i in range(0,steps,4):beam('KYJ stair baluster',(x+sg*1.02,syend-run+i*run/steps,1.45+i*rise/steps),(x+sg*1.02,syend-run+i*run/steps,2.45+i*rise/steps),.035,M['steel'])
 metrics['bridge_flights']=flights;metrics['bridge_deck_top_m']=8.70;metrics['bridge_deck_underside_m']=8.40;metrics['bridge_source_way']=D['bridge_source']['way_id'];metrics['stair_landing_method']='Three source-aligned dogleg-bridge flights meet exact deck leading boundary; all final tread tops8.70m.'

# Station context uses actual mapped road centerlines, not imagined adjacent urban blocks.
coll('08 | Surroundings and approach context')
box('Terrain',(0,0,-.24),(1000 if CODE=='KYJ' else 560,3000 if CODE=='KYJ' else 2400,.32),M['ground'])
for w in D['context_water']:
 if len(w)>3:polyplate('Mapped water body',w,-.13,-.10,M['water'])
for r in D['context_roads']:
 if r['tags'].get('bridge')=='yes' and r['tags'].get('highway')=='footway':continue
 pp=r['xy'];wid=2 if r['tags'].get('highway') in ['path','footway'] else 4.5
 for a,b in zip(pp,pp[1:]):beam('Mapped road surfacing',(a[0],a[1],-.06),(b[0],b[1],-.06),wid,M['road'],.045)
if CODE!='TNU':box('Station forecourt',(bx+SIDE*(DEP/2+9),by,.015),(18,min(130,LEN+25),.10),M['stone'])
# Context foliage: shape and placing illustrative, not surveyed species/inventory.
def palm(x,y,height):
 n=7;points=[(x+.16*height*(i/n)**2,y+.05*height*(i/n)**2,height*i/n) for i in range(n+1)]
 for a,b in zip(points,points[1:]):beam('Palm segmented trunk',a,b,.24,M['wood'])
 xx,yy,zz=points[-1]
 for i in range(9):
  a=i*math.tau/9;end=(xx+4*math.cos(a),yy+4*math.sin(a),zz-.8);mid=(xx+2*math.cos(a),yy+2*math.sin(a),zz+.45);beam('Palm frond rib',(xx,yy,zz),mid,.025,M['leaf']);beam('Palm frond rib',mid,end,.023,M['leaf'])
  for j in range(1,8):
   t=j/8;px=xx+4*t*math.cos(a);py=yy+4*t*math.sin(a);pz=zz+math.sin(t*math.pi)*.5-t*.8;w=.7*math.sin(t*math.pi)
   v=[(px,py,pz),(px-math.sin(a)*w,py+math.cos(a)*w,pz-.32),(px+.34*math.cos(a),py+.34*math.sin(a),pz-.12),(px+math.sin(a)*w,py-math.cos(a)*w,pz-.32)];batchgeom(v,[(0,1,2),(0,2,3)],M['leaflight'] if i%2 else M['leaf'])
def broadtree(x,y,height):
 beam('Broadleaf trunk',(x,y,0),(x,y,height*.75),.27,M['wood'])
 for j in range(6):
  ang=j*math.tau/6;cx=x+math.cos(ang)*1.1;cy=y+math.sin(ang)*1.1;cz=height*.73+(j%2)*.5;radius=2.5
  vv=[(cx,cy,cz+radius*.72),(cx,cy,cz-radius*.5)]+[(cx+math.cos(k*math.tau/9)*radius,cy+math.sin(k*math.tau/9)*radius,cz+random.uniform(-.3,.3)) for k in range(9)]
  ff=[(0,2+k,2+(k+1)%9) for k in range(9)]+[(1,2+(k+1)%9,2+k) for k in range(9)];batchgeom(vv,ff,M['leaf'] if j%2 else M['leaflight'])
 for j in range(3):beam('Branch',(x,y,height*.45),(x+math.cos(j*2)*1.8,y+math.sin(j*2)*1.8,height*.75),.12,M['wood'])
for i in range(100):
 y=random.uniform(-480,520);r0=min(D['routes'],key=lambda r:abs(at_y(r['xy'],y)));railx=at_y(r0['xy'],y);x=railx+random.choice([-1,1])*random.uniform(30,90)
 if CODE!='TNU' and abs(y-by)<LEN/2+25 and abs(x-bx)<DEP/2+30:continue
 broadtree(x,y,random.uniform(5,10))
for i in range(70):
 y=random.uniform(-600,650);r0=min(D['routes'],key=lambda r:abs(at_y(r['xy'],y)));railx=at_y(r0['xy'],y);x=railx+random.choice([-1,1])*random.uniform(35,105)
 if CODE!='TNU' and abs(y-by)<LEN/2+25 and abs(x-bx)<DEP/2+30:continue
 palm(x,y,random.uniform(8,15))
# Low plants and ballast stone geometry near platform; deterministic samples add material scale.
for r in D['routes']:
 for x,y,dx,dy in sample(r['xy'],3.5):
  if abs(y)>380:continue
  for sg in [-1,1]:
   xx=x-dy*sg*1.45+random.uniform(-.15,.15);yy=y+dx*sg*1.45+random.uniform(-.8,.8);rr=random.uniform(.035,.065);v=[(xx-rr,yy,.31),(xx,yy-rr,.31),(xx+rr,yy,.31),(xx,yy+rr,.31),(xx,yy,.31+rr*1.3)];batchgeom(v,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],M['sleeper'])
if CODE=='TNU':
 coll('09 | Closed historical record, no operational station invented')
 txt('Historical explanatory label','TIRUNETTUR  /  CLOSED 10 JULY 2017',(25,0,3.8),1.0,M['dark'])
 txt('Historical uncertainty label','Mapped corridor only. Historic platform footprint unresolved.',(25,0,2.3),.50,M['dark'])
 metrics['historical_site_note']='The scene shows OSM mapped corridor near legacy station marker, not a verified remnant location. No ticket hall, operational platform, or fabricated active station is supplied.'

# Flush consolidated batches into semantic material meshes, avoiding tens of thousands of objects.
for (cat,mn),d in BATCH.items():
 COL=d['col'];mesh(cat+' / '+mn,d['v'],d['f'],d['m'])
BATCH.clear()
# Render camera lineage: exact frozen .blend reused for every view.
coll('90 | Cameras and lighting')
def camera(name,loc,target,lens=42,ortho=None):
 ca=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,ca);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens;ca.clip_end=10000
 if ortho:ca.type='ORTHO';ca.ortho_scale=ortho
 return o
if platform_info:
 p=platform_info[0];cy=sum([min(q['bounds'][1] for q in platform_info),max(q['bounds'][3] for q in platform_info)])/2;length=max(q['bounds'][3] for q in platform_info)-min(q['bounds'][1] for q in platform_info)
else:cy=0;length=550
cam1=camera('01_Overall_station',(SIDE*300,cy-length*.6,240),(0,cy,0),45,ortho=max(450,length*1.12))
if CODE!='TNU':
 cam2=camera('02_Entrance_architecture',(bx+SIDE*(DEP/2+(22 if LEN<22 else 29)),by-(18 if LEN<22 else 25),9.3 if LEN<22 else 11.6),(bx+SIDE*DEP/2,by,3.7),44)
 p=min(platform_info,key=lambda p:abs(p['x']-bx)) if platform_info else {'x':bx,'y':by}
 cam3=camera('03_Platform_and_tracks',(p['x']-SIDE*min(1.8,p.get('width',6)/2-.9),by-66,3.35),(p['x']-SIDE*7,by+70,3.4),32)
 cam4=camera('04_Reconstructed_interior',loc(-min(LEN/2-1.0,7),DEP/2-.9,3.10),loc(min(LEN/2-2.2,5.6),-.5,2.72),25)
else:
 cam2=camera('02_Closed_corridor',(25,-50,9),(-18,50,2),40);cam3=camera('03_Mapped_trackwork',(-10,-10,4),(-18,35,1),40);cam4=None
if D['turnout_nodes']:
 pw=json.load(open(P/'references/pointwork.json')) if (P/'references/pointwork.json').exists() else {'crossings':[]}
 if pw['crossings']:
  cp=max(pw['crossings'],key=lambda t:abs(t['xy'][1]));tx,ty=cp['xy'];camera('05_Mapped_turnout_detail',(tx+4.5,ty-7,5.8),(tx,ty,.635),43);metrics['pointwork_proof_crossing']=cp
 else:
  t=max(D['turnout_nodes'],key=lambda t:abs(t['xy'][1]));tx,ty=t['xy'];camera('05_Mapped_turnout_detail',(tx+6,ty-9,5.8),(tx,ty,.635),35)

sun=bpy.data.lights.new('Tropical morning sun','SUN');sun.energy=2.2;sun.angle=math.radians(10);so=bpy.data.objects.new('Tropical morning sun',sun);COL.objects.link(so);so.rotation_euler=(math.radians(27),math.radians(-23),math.radians(-35))
if CODE!='TNU':
 for u,v in [(-2,0),(4,0)]:
  l=bpy.data.lights.new('Interior soft ceiling light','AREA');l.energy=220;l.shape='DISK';l.size=5;o=bpy.data.objects.new('Interior soft ceiling light',l);COL.objects.link(o);o.location=loc(u,v,eave-.35)
sc.camera=cam2
for a in bpy.context.screen.areas if bpy.context.screen else []:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_distance=80
# Structured scene properties and reproducibility notes.
sc['station_code']=CODE;sc['station_name']=S['station_name'];sc['status']=S['operational_status'];sc['evidence']='See references/plan.json, SOURCES_AND_UNCERTAINTIES.md';sc['interiors']='Reconstructed, not measured';sc['no_trains']=True;sc['nominal_gauge_m']=1.676
for o in sc.objects:
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=False
bpy.ops.file.pack_all();out=P/(CODE+'_coastal_station_'+VERSION+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
metrics.update({'blender':bpy.app.version_string,'render_engine':sc.render.engine,'render_samples':sc.cycles.samples,'object_count':len(sc.objects),'mesh_objects':sum(o.type=='MESH' for o in sc.objects),'mesh_vertices':sum(len(o.data.vertices) for o in sc.objects if o.type=='MESH'),'mesh_faces':sum(len(o.data.polygons) for o in sc.objects if o.type=='MESH'),'packed_images':all(im.packed_file for im in bpy.data.images if im.source=='FILE'),'images':[{'name':im.name,'packed':bool(im.packed_file),'path':im.filepath} for im in bpy.data.images if im.source=='FILE'],'build_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_plan_sha256':hashlib.sha256((P/'references/plan.json').read_bytes()).hexdigest(),'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'building_dimensions_m':{'width':DEP,'length':LEN,'position_xy':[bx,by],'height':eave if CODE!='TNU' else None},'platform_parameters':[{k:v for k,v in p.items() if k!='poly'} for p in platform_info],'cameras':[{'name':o.name,'position':list(o.location),'rotation':list(o.rotation_euler)} for o in sc.objects if o.type=='CAMERA'],'peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
(P/'QA_BUILD.json').write_text(json.dumps(metrics,indent=2));print('BUILD_COMPLETE',json.dumps({k:metrics[k] for k in ['station_code','mesh_vertices','blend_bytes','peak_rss_kb']}),flush=True)
