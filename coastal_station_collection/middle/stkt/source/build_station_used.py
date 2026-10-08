"""Build a source-traceable middle-route station, no rolling stock.
Run only through ../shared/run_blender_locked.py. Blender4.3+ native geometry.
"""
import bpy,math,json,random,sys,os,time,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(os.environ.get('COASTAL_MIDDLE_ROOT',str(Path(__file__).resolve().parents[1])));CODE=sys.argv[sys.argv.index('--')+1];R=ROOT/CODE.lower();D=json.loads((R/'source/adopted_geometry.json').read_text());SP=D['spec'];RAW=json.loads((R/'source/mapped_geometry.json').read_text());random.seed(sum(map(ord,CODE)))
if (R/'FROZEN_MANIFEST.json').exists():raise RuntimeError('Frozen scene is immutable; build revisions in a new directory')
(R/'renders').mkdir(exist_ok=True);(R/'export').mkdir(exist_ok=True);(R/'source/build_station_used.py').write_bytes(Path(__file__).read_bytes());(R/'source/reference_spec.json').write_text(json.dumps(SP,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1;S.render.engine='CYCLES' if False else 'CYCLES'
# The packaged scene is renderer independent. Eevee is selected for bounded preview jobs.
S.render.engine='BLENDER_EEVEE_NEXT';S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.film_transparent=False
if hasattr(S,'eevee'):S.eevee.taa_render_samples=48
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.world=bpy.data.worlds.new('Kerala daylight');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.76,.88,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.45
current=None;batch={};counts={};all_props=[];F=1.018

def mat(n,c,rough=.7,metal=0,noise=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  nd=m.node_tree.nodes;ln=m.node_tree.links;tc=nd.new('ShaderNodeTexCoord');t=nd.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=noise;t.inputs['Detail'].default_value=3;ln.new(tc.outputs['Object'],t.inputs['Vector']);r=nd.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(x*.72 for x in c),1);r.color_ramp.elements[1].color=(*(min(1,x*1.15)for x in c),1);ln.new(t.outputs['Fac'],r.inputs[0]);ln.new(r.outputs[0],p.inputs['Base Color']);b=nd.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.003 if metal else .008;ln.new(t.outputs['Fac'],b.inputs['Height']);ln.new(b.outputs[0],p.inputs['Normal'])
 return m
cream=mat('Faded cream limewash',(.74,.70,.56),noise=8);white=mat('Chalk white masonry',(.80,.80,.74),noise=7);mint=mat('Pale mint station plaster',(.45,.66,.54),noise=8);blue=mat('Institutional cobalt lower band',(.065,.20,.38),noise=6);red=mat('Oxide red masonry and tile',(.40,.070,.040),noise=14);ochre=mat('Warm station ochre',(.72,.45,.13),noise=7);greenpaint=mat('Dark green painted piers',(.12,.35,.13),noise=8);yellow=mat('Railway enamel yellow',(.94,.65,.025),noise=14)
steel=mat('Galvanised structural steel',(.38,.43,.44),.36,.75,20);dark=mat('Dark iron and rubber',(.035,.045,.045),.45,.3);rail=mat('Polished steel running heads',(.51,.56,.57),.22,.91);rust=mat('Oxidised rail web',(.25,.07,.025),.6,.45,22);wood=mat('Weathered timber',(.22,.085,.028),noise=35);concrete=mat('Precast concrete sleepers',(.41,.43,.39),noise=40);ballast=mat('Crushed granite ballast',(.24,.245,.225),noise=65);earth=mat('Laterite and tropical earth',(.25,.235,.13),noise=7);grass=mat('Tropical groundcover',(.13,.20,.065),noise=9);leaf=mat('Coconut palm leaves',(.055,.17,.036),noise=5);trunk=mat('Palm bark',(.30,.235,.12),noise=8);roof=mat('Blue corrugated platform sheet',(.075,.245,.36),.5,.35,18);roofgrey=mat('Galvanised canopy underside',(.50,.56,.57),.5,.45,18);tile=mat('Small red platform pavers',(.41,.155,.085),noise=50);floor=mat('Terrazzo public room floor',(.60,.59,.50),noise=70);glass=mat('Blue tinted glazing',(.07,.19,.22),.15,.30);paper=mat('Printed paper',(.78,.78,.69));asphalt=mat('Asphalt forecourt',(.075,.085,.09),noise=65);water=mat('Backwater surface',(.095,.28,.30),.13,.2,2)
# Generated paving texture; no third-party image pixels are embedded.
nd=tile.node_tree.nodes;ln=tile.node_tree.links;tc=nd.new('ShaderNodeTexCoord');bt=nd.new('ShaderNodeTexBrick');bt.offset=0;bt.inputs['Scale'].default_value=1;bt.inputs['Mortar Size'].default_value=.006;bt.inputs['Brick Width'].default_value=.4;bt.inputs['Row Height'].default_value=.4;bt.inputs['Color1'].default_value=(.43,.16,.085,1);bt.inputs['Color2'].default_value=(.38,.135,.065,1);bt.inputs['Mortar'].default_value=(.22,.16,.10,1);ln.new(tc.outputs['Object'],bt.inputs['Vector']);ln.new(bt.outputs['Color'],nd.get('Principled BSDF').inputs['Base Color'])
lit=mat('Fluorescent diffusers',(.86,.91,.79));lit.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.86,.91,.79,1);lit.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=2
salmon=mat('Faded salmon facade panels',(.55,.25,.18),noise=8)
nameboardmat=mat('Generated bilingual station lettering',(.94,.66,.05));nameboardimg=bpy.data.images.load(str(R/'source/station_nameboard.png'));nameboardimg.pack();nd=nameboardmat.node_tree.nodes;imnode=nd.new('ShaderNodeTexImage');imnode.image=nameboardimg;nameboardmat.node_tree.links.new(imnode.outputs['Color'],nd.get('Principled BSDF').inputs['Base Color'])
paleyellow=mat('Pale yellow halt plaster',(.79,.73,.45),noise=8)
paleblue=mat('Historical Iravipuram pale blue',(.46,.64,.70),noise=8)
peach=mat('Kappil salmon plaster',(.76,.43,.31),noise=8);turquoise=mat('Kappil turquoise accents',(.07,.40,.43),noise=8);rosem=mat('Kappil deep rose canopy',(.43,.035,.12),.6,.15,12)
palette={'peach':(peach,turquoise),'irpwhite':(white,paleblue),'paleyellow':(paleyellow,concrete),'salmon':(white,salmon),'mint':(mint,greenpaint),'mintblue':(mint,blue),'cream':(cream,red),'creamred':(cream,red),'creamblue':(cream,blue),'mintred':(mint,red),'ochre':(ochre,red),'kollam':(mint,red)};wall,trim=palette[SP['facade']]

def flush():
 for (cn,n,mn),(vs,fs,m) in batch.items():
  me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(n,me);bpy.data.collections[cn].objects.link(ob);me.materials.append(m);ob['component_count']=counts.get(n,1)
 batch.clear()
def col(n):
 global current
 flush();current=bpy.data.collections.new(n);S.collection.children.link(current);return current
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(n,me);current.objects.link(ob)
 if m:me.materials.append(m)
 return ob
def add(n,vs,fs,m):
 key=(current.name,n,m.name)
 if key not in batch:batch[key]=[[],[],m]
 vv,ff,_=batch[key];off=len(vv);vv.extend(vs);ff.extend(tuple(off+i for i in f)for f in fs);counts[n]=counts.get(n,0)+1

def box(n,p,d,m,a=0):
 x,y,z=[v/2 for v in d];cs=math.cos(a);sn=math.sin(a);vs=[(p[0]+xx*cs-yy*sn,p[1]+xx*sn+yy*cs,p[2]+zz)for xx,yy,zz in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];add(n,vs,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],m)
def rod(n,a,b,r,m,N=8):
 a=Vector(a);b=Vector(b);d=b-a
 if d.length<1e-5:return
 d.normalize();u=d.cross(Vector((0,0,1)));u=Vector((1,0,0)) if u.length<.01 else u.normalized();v=d.cross(u);vs=[tuple(p+r*(u*math.cos(i*math.tau/N)+v*math.sin(i*math.tau/N)))for p in(a,b)for i in range(N)];fs=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)];add(n,vs,fs,m)
def txt(n,s,p,h=.25,m=None,rot=0):
 cu=bpy.data.curves.new(n,'FONT');cu.body=s;cu.size=h;cu.align_x='CENTER';cu.extrude=.001;cu.materials.append(m or dark);ob=bpy.data.objects.new(n,cu);current.objects.link(ob);ob.location=p;ob.rotation_euler=(math.pi/2,0,rot);return ob
def sign(s,p,w=3,h=.6,size=.20,m=None,rot=0,textmat=None):
 box('Enamel wayfinding panel',p,(w,.055,h),m or blue,rot);txt('Wayfinding '+s,s,(p[0]+.035*math.sin(rot),p[1]-.035*math.cos(rot),p[2]-size*.34),size,textmat or white,rot)
def area(n,p,target,power,size=3):
 da=bpy.data.lights.new(n,'AREA');da.energy=power;da.shape='DISK';da.size=size;ob=bpy.data.objects.new(n,da);current.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def sample(ps,step,offset=0):
 rem=offset
 for a,b in zip(ps,ps[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];ll=math.hypot(dx,dy)
  if ll<1e-7:continue
  while rem<ll:
   yield(a[0]+dx*rem/ll,a[1]+dy*rem/ll,math.atan2(dy,dx));rem+=step
  rem-=ll

def railclear(x,y,dist=2.1):
 for ps in routes:
  for a,b in zip(ps,ps[1:]):
   vx,vy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*vx+(y-a[1])*vy)/(vx*vx+vy*vy+1e-12)))
   if (x-a[0]-t*vx)**2+(y-a[1]-t*vy)**2<dist*dist:return False
 return True

def bench(x,y,z=F,style='slats',a=0):
 if CODE=='QLN' or style=='concrete':
  box('Concrete bench seat',(x,y,z+.47),(2.35,.48,.12),red,a)
  for dx in(-.82,.82):box('Blue bench masonry pedestal',(x+dx*math.cos(a),y+dx*math.sin(a),z+.22),(.34,.36,.44),blue,a)
  return
 for k in range(5):box('Timber bench seat slat',(x,y-.20+k*.10,z+.46),(2.15,.07,.055),wood,a)
 for k in range(4):box('Bench back slat',(x,y+.27,z+.67+k*.085),(2.15,.055,.055),wood,a)
 for dx in(-.80,.80):
  for yy in(-.18,.2):rod('Bench steel leg',(x+dx,y+yy,z),(x+dx,y+yy,z+.43),.028,dark)
  rod('Bench back iron upright',(x+dx,y+.27,z+.1),(x+dx,y+.27,z+1),.025,dark)
  box('Bench anchor foot',(x+dx,y,z+.025),(.16,.50,.05),steel)
def fan(x,y,z):
 rod('Ceiling fan drop rod',(x,y,z+.5),(x,y,z),.022,dark);rod('Ceiling fan motor',(x,y,z-.06),(x,y,z+.06),.13,cream,12)
 for a in(0,math.tau/3,2*math.tau/3):box('Ceiling fan blade',(x+.35*math.cos(a),y+.35*math.sin(a),z),(.63,.14,.025),cream,a)
def luminaire(x,y,z):
 box('Fluorescent housing',(x,y,z),(1.2,.16,.12),steel);box('Fluorescent luminous face',(x,y,z-.065),(1.12,.11,.025),lit)
def desk(x,y,z=F):
 box('Staff desk timber top',(x,y,z+.78),(1.75,.75,.08),wood)
 for dx in(-.64,.64):box('Staff desk pedestal',(x+dx,y,z+.37),(.35,.64,.74),blue)
 box('Desktop monitor pedestal',(x,y+.15,z+.85),(.32,.26,.05),dark);box('Desktop monitor stalk',(x,y+.2,z+1),(.045,.045,.30),steel);box('Desktop monitor bezel',(x,y+.17,z+1.19),(.52,.08,.35),dark);box('Desktop monitor screen',(x,y+.12,z+1.19),(.46,.018,.28),glass);box('Keyboard',(x,y-.18,z+.845),(.53,.16,.033),dark)
 for row in range(3):
  for k in range(11):box('Keyboard individual keys',(x-.22+k*.044,y-.23+row*.045,z+.87),(.035,.030,.009),steel)
 box('Mouse',(x+.38,y-.15,z+.855),(.075,.115,.045),dark)
 for dx in(-.23,.23):
  for dy in(-.21,.21):rod('Staff chair legs',(x+dx,y-.85+dy,z),(x+dx,y-.85+dy,z+.45),.022,steel)
 box('Staff chair seat',(x,y-.85,z+.48),(.57,.54,.08),blue);box('Staff chair padded back',(x,y-1.08,z+.85),(.57,.08,.55),blue)
 for k in range(4):box('Paper service ledgers',(x+.5,y,z+.84+k*.013),(.3,.23,.013),paper,.02*k)
 txt('Station desk screen','SOUTHERN RAILWAY\n'+CODE+'  /  OPERATIONS',(x,y+.106,z+1.23),.027,white)
def binunit(x,y):
 for dx,ma in [(-.24,greenpaint),(.24,blue)]:
  rod('Waste bin body',(x+dx,y,F+.10),(x+dx,y,F+.73),.20,ma,12);rod('Waste bin rim',(x+dx,y,F+.72),(x+dx,y,F+.78),.215,steel,12)
def waterunit(x,y):
 box('Water dispenser plinth',(x,y,F+.1),(1.4,.7,.2),concrete);box('Drinking water stainless unit',(x,y,F+.63),(1.15,.55,.95),steel);box('Drip tray',(x,y-.32,F+.71),(1.16,.25,.06),dark)
 for dx in(-.32,0,.32):rod('Drinking water faucet',(x+dx,y-.32,F+.95),(x+dx,y-.45,F+.95),.017,steel)
 sign('DRINKING WATER',(x,y-.29,F+1.6),1.8,.35,.13)
def noticeboard(x,y,z=F+1.9):
 box('Station noticeboard timber frame',(x,y,z),(1.6,.10,1.05),wood);box('Noticeboard felt',(x,y-.058,z),(1.45,.014,.90),greenpaint)
 for j in range(4):
  xx=x-.52+(j%2)*.65;zz=z-.21+(j//2)*.4;box('Notice sheet',(xx,y-.07,zz),(.50,.012,.32),paper)
  for r in range(5):box('Notice printed line',(xx,y-.08,zz-.11+r*.047),(.37,.004,.006),dark)

# --- MAPPED RAILS AND CONNECTED YARD ---
routes=[r['xy'] for r in D['routes']]
col('01_MAPPED_TRACK_NETWORK')
for typ,ma in [('ballast',ballast),('foot',rust),('web',rust),('head',rail)]+([('guards',rail)]if 'guards'in D['meshes'] else[]):
 md=D['meshes'][typ]
 if not md['faces']:continue
 ob=mesh('Continuous '+typ+' union | full mapped network',md['vertices'],md['faces'],ma);ob['basis']='OSM paths; head footprints unioned with 45mm flangeways; 1.676m inside-face gauge'
# Main concrete sleepers outside switch influence, long shared bearers inside.
col('02_SLEEPERS_FASTENINGS_AND_POINTWORK')
switches=D['switches'];bearer_seen=set();sleeper_seen=set()
def inswitch(x,y):
 for sw in switches:
  q=sw['xy'];a=sw['angle'];dx=x-q[0];dy=y-q[1];along=dx*math.cos(a)+dy*math.sin(a);across=-dx*math.sin(a)+dy*math.cos(a)
  if -3<along<32 and abs(across)<3.9:return sw
 return None
for route in D['routes']:
 for x,y,a in sample(route['xy'],.60):
  key=(round(x*3),round(y*3))
  if key in sleeper_seen:continue
  sleeper_seen.add(key)
  if CODE=='QLN' and 125<x<305 and any(abs(y-p['track_y'])<.5 for p in D.get('maintenance_pits',[])):
   nx,ny=-math.sin(a),math.cos(a)
   for sg in(-1,1):box('MEMU pit rail-support pedestal',(x+nx*sg*.872,y+ny*sg*.872,-.48),(.22,.38,.94),concrete,a)
   continue
  sw=inswitch(x,y)
  if sw:
   # One consistent sleeper direction through each points fan.
   aa=sw['angle'];q=sw['xy'];t=round(((x-q[0])*math.cos(aa)+(y-q[1])*math.sin(aa))/.6);k=(sw['node'],t)
   if k in bearer_seen:continue
   bearer_seen.add(k);xx=q[0]+t*.6*math.cos(aa);yy=q[1]+t*.6*math.sin(aa);box('Long timber turnout bearer',(xx,yy,-.09),(.28,5.1,.17),wood,aa)
  else:box('Precast broad-gauge sleeper',(x,y,-.095),(.24,2.75,.16),concrete,a)
  # Fastenings remain three-dimensional even outside the detail view.
  nx,ny=-math.sin(a),math.cos(a)
  for sg in(-1,1):
   xx,yy=x+nx*sg*.872,y+ny*sg*.872;box('Rail elastic base pad',(xx,yy,.001),(.20,.18,.03),dark,a)
   for sd in(-1,1):box('Rail spring clip shoulder',(xx+nx*sd*.11,yy+ny*sd*.11,.035),(.13,.045,.046),rust,a)
for sw in switches:
 x,y=sw['xy'];a=sw['angle'];nx,ny=-math.sin(a),math.cos(a);cx,cy=x+nx*2.65,y+ny*2.65
 for side in(1,-1):
  if railclear(x+nx*2.65*side,y+ny*2.65*side,1.9):cx,cy=x+nx*2.65*side,y+ny*2.65*side;break
 box('Point machine sealed housing',(cx,cy,.21),(1.05,.58,.38),steel,a);box('Point machine inspection lid',(cx,cy,.42),(1.13,.65,.045),dark,a);rod('Point drive stretcher rod',(cx,cy,.09),(x-nx*.8,y-ny*.8,.09),.022,steel)
for bb in D['buffers']:
 x,y=bb['xy'];a=bb['angle'];nx,ny=-math.sin(a),math.cos(a)
 for sg in(-1,1):rod('True mapped dead-end buffer diagonal',(x-math.cos(a)*1.4+nx*sg*.8,y-math.sin(a)*1.4+ny*sg*.8,.10),(x+nx*sg*.8,y+ny*sg*.8,1.12),.08,rust)
 box('Buffer stop red crossbeam',(x,y,1.05),(.25,2.6,.35),red,a)
 for sg in(-1,1):box('Buffer white reflector',(x+nx*sg*.65+math.cos(a)*.14,y+ny*sg*.65+math.sin(a)*.14,1.05),(.025,.30,.23),white,a)

if D.get('bridges'):
 col('02B_MAPPED_RAIL_BRIDGES_RECONSTRUCTED_VERTICALS')
 md=D['meshes']['bridge_decks'];mesh('Mapped railway bridge deck slabs',md['vertices'],md['faces'],concrete)
 for r in D['bridges']:
  for x,y,a in sample(r['xy'],14):
   box('Rail bridge concrete pier',(x,y,-2.55),(1.1,3.5,2.9),concrete,a)
   box('Rail bridge bearing cap',(x,y,-1.14),(1.55,4.1,.35),concrete,a)
  for side in(-1,1):
   ps=r['xy']
   for a,b in zip(ps,ps[1:]):
    ang=math.atan2(b[1]-a[1],b[0]-a[0]);nx,ny=-math.sin(ang)*side,math.cos(ang)*side
    rod('Bridge safety kerb',(a[0]+nx*1.92,a[1]+ny*1.92,-.18),(b[0]+nx*1.92,b[1]+ny*1.92,-.18),.085,concrete)
   for x,y,a in sample(ps,3.5):
    nx,ny=-math.sin(a)*side,math.cos(a)*side
    rod('Bridge maintenance walkway post',(x+nx*2.0,y+ny*2.0,-.22),(x+nx*2.0,y+ny*2.0,.70),.025,steel)

# --- PLATFORMS, EDGES, PARTIAL SHELTERS ---
col('03_PLATFORM_BODIES_CLEARANCE_CORRECTED')
for p in D['platforms']:
 md=p['mesh'];ob=mesh('Platform body '+p['label'],md['vertices'],md['faces'],earth if SP.get('platform_finish')=='earth' else (concrete if SP.get('platform_finish')=='concrete' else tile));ob['source_id']=p['id'];ob['basis']=p['basis'];ob['numbered_positions']=p['label'];ob['rail_center_clearance_m']=p['clearance_min_m']
 ps=p['outline'];cx,cy=p['center_xy']
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<3:continue
  for x,y,aa in sample([a,b],.65):
   if railclear(x,y,3.1):continue
   box('Platform white coping block',(x,y,F+.015),(.635,.28,.075),white,aa)
   nx,ny=-math.sin(aa),math.cos(aa)
   if (cx-x)*nx+(cy-y)*ny<0:nx,ny=-nx,-ny
   box('Platform tactile strip',(x+nx*.43,y+ny*.43,F+.014),(.63,.39,.06),ochre,aa)
   if abs(x)<130:
    for k in(-.13,-.045,.045,.13):box('Tactile tile ribs',(x+nx*(.43+k),y+ny*(.43+k),F+.050),(.55,.015,.015),cream,aa)
col('04_PLATFORM_SHELTERS_AND_AMENITIES')
def widthat(p,x):
 ys=[];ps=p['outline']
 for a,b in zip(ps,ps[1:]):
  if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>1e-5:ys.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
 return (min(ys),max(ys))if len(ys)>1 else None
canopies=[]
for pi,p in enumerate(D['platforms']):
 lo,_,hi,_=p['bbox'];L=min(SP['canopy_length'],(hi-lo)*.72);center=max(lo+L/2+5,min((lo+hi)/2,hi-L/2-5));start,end=center-L/2,center+L/2
 # Keep actual partial coverage and distinct split shelter bays at larger stations.
 if SP['kind']=='junction':start,end=-145,305
 for x in range(math.ceil(start/8)*8,int(end)+1,8):
  if SP['footbridge'] and 58<=x<=92:continue
  yy=widthat(p,x)
  if not yy or yy[1]-yy[0]<3:continue
  y=sum(yy)/2;w=min(yy[1]-yy[0]-.75,9.0);canopies.append((x,y,w));h=5.45;butter=SP['canopy_style']=='butterfly';zmid=h-.70 if butter else h+.6;zedge=h+.25 if butter else h-.10
  box('Canopy steel column web',(x,y,(F+h-.25)/2),(.12,.16,h-.25-F),steel)
  for sg in(-1,1):box('Canopy steel column flange',(x+sg*.09,y,(F+h-.25)/2),(.06,.32,h-.25-F),steel)
  box('Canopy column footing',(x,y,F+.13),(.48,.52,.26),concrete)
  for side in(-1,1):
   if SP['canopy_style']=='mono':zmid=h+.1;zedge=h+.1+side*.65
   rod('Canopy principal rafter',(x,y,zmid),(x,y+side*w/2,zedge),.065,steel);rod('Canopy roof truss bottom chord',(x,y,h-.6),(x,y+side*w/2,h-.3),.044,steel)
   rod('Canopy diagonal truss web',(x,y,h-.55),(x,y+side*w*.32,(zedge+zmid)/2),.032,steel)
   vs=[(x-4,y,zmid),(x+4,y,zmid),(x+4,y+side*w/2,zedge),(x-4,y+side*w/2,zedge)];add('Corrugated shelter roof sheets',vs,[(0,1,2,3)],rosem if CODE=='KFI' else (roofgrey if butter or CODE in['MQO','MYY','PRND'] else roof))
   for k in range(12):
    xx=x-3.8+k*.68;rod('Canopy corrugation ribs',(xx,y,zmid+.018),(xx,y+side*w/2,zedge+.018),.016,roofgrey if butter else roof,6)
   rod('Shelter eaves purlin',(x-4,y+side*w/2,zedge-.10),(x+4,y+side*w/2,zedge-.10),.045,steel)
  if int(x)%24==0:fan(x,y,h-.65);luminaire(x+2,y,h-.25)
  if int(x)%32==0:bench(x+2,y);binunit(x-2,y)
 for x in (max(lo+18,min(lo+30,hi-20)),min(hi-18,max(hi-30,lo+20))):
  yy=widthat(p,x)
  if not yy:continue
  y=sum(yy)/2;boardw=max(3.3,min(6.2,len(SP['name'])*.28));box('Yellow station nameboard',(x,y,F+1.8),(boardw,.12,1.14),yellow)
  for dx in(-boardw/2-.1,boardw/2+.1):
   box('Nameboard concrete post',(x+dx,y,F+1.16),(.16,.20,2.32),white);box('Nameboard black post foot',(x+dx,y,F+.28),(.19,.23,.56),dark)
  ob=mesh('Generated station nameboard face',[(x-boardw/2+.04,y-.066,F+1.8-.53),(x+boardw/2-.04,y-.066,F+1.8-.53),(x+boardw/2-.04,y-.066,F+1.8+.53),(x-boardw/2+.04,y-.066,F+1.8+.53)],[(0,1,2,3)],nameboardmat);uv=ob.data.uv_layers.new(name='Station sign UV')
  for li,coord in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=coord
 yy=widthat(p,center)
 if yy:
  y=sum(yy)/2;waterunit(center+8,y);noticeboard(center-9,y);sign('PLATFORM '+p['label'].replace(';',' / '),(center,y,F+3.3),2.1,.55,.21)
 # Small tiled joints, litter bins and seating along the uncovered end segments.
 for x in range(int(lo)+35,int(hi)-20,45):
  if SP['footbridge'] and 58<=x<=96:continue
  yy=widthat(p,x)
  if yy and yy[1]-yy[0]>3.5:bench(x,sum(yy)/2,style='concrete')

# --- STATION-SPECIFIC BUILDING, PHYSICAL OPENINGS AND FURNISHED ROOMS ---
bx,by,bw,bd=SP['building'];side=SP['side'];fronty=by+side*bd/2;backy=by-side*bd/2;bh=SP.get('building_height',4.0 if SP['kind']!='halt' else 3.25);frontrot=math.pi if side>0 else 0
col('05_STATION_ARCHITECTURE_PHOTO_GUIDED')
box('Station building raised floor',(bx,by,F-.14),(bw,bd,.28),floor)
# Long walls are assembled from piers, lintels and window openings, never solid painted panels.
def facade_bays(width):
 n=max(3,int(width/4));return n if n%2 else n+1
def openingwall(label,y,width,height,cx,front=True):
 n=facade_bays(width);bay=width/n;outward=side if front else -side
 for i in range(n):
  x=cx-width/2+(i+.5)*bay;isdoor=(i==n//2)or(i%4==0)
  if CODE=='IRP':isdoor=(i==n//2)
  opening=1.45 if isdoor else 1.22;sill=0 if isdoor else 1.02;top=2.60 if isdoor else 2.48
  if CODE=='AMY' and i==n-1:opening=2.8;sill=.75;top=2.55
  for sg in(-1,1):box(label+' wall pier',(x+sg*(opening/2+(bay-opening)/4),y,F+height/2),((bay-opening)/2,.25,height),wall)
  box(label+' lintel',(x,y,F+(top+height)/2),(opening,.25,height-top),wall)
  if not isdoor:
   box(label+' window sill wall',(x,y,F+sill/2),(opening,.25,sill),wall);box('Timber window sill',(x,y,F+sill),(opening+.20,.38,.10),wood)
   for sg in(-1,1):box('Timber window jamb',(x+sg*(opening/2-.025),y,F+(sill+top)/2),(.08,.29,top-sill),wood)
   box('Window header',(x,y,F+top),(opening+.12,.28,.10),wood)
   for dx in(-.38,0,.38):rod('Window security bars',(x+dx,y,F+sill+.05),(x+dx,y,F+top-.05),.012,dark)
   if not((CODE=='AMY' and i==n-1) or CODE=='IRP'):box('Window glass pane',(x,y,F+(sill+top)/2),(opening-.12,.028,top-sill-.12),glass)
   if SP['facade']=='mintblue':
    # Observed awning shutters at Sasthankotta.
    vs=[(x-opening/2,y,F+top),(x+opening/2,y,F+top),(x+opening/2,y+outward*.45,F+top-.40),(x-opening/2,y+outward*.45,F+top-.40)];add('Outward timber window awning shutter',vs,[(0,1,2,3)],wood)
  else:
   for sg in(-1,1):box('Open doorway timber jamb',(x+sg*(opening/2+.03),y,F+top/2),(.10,.30,top),wood)
   box('Open doorway lintel timber',(x,y,F+top),(opening+.2,.3,.13),wood)
   # Door leaf swung clear of the pedestrian opening.
   box('Open door panel',(x-opening/2+.05,y-side*.51,F+(top-.1)/2),(.07,1.08,top-.1),trim)
   rod('Door lever handle',(x-opening/2-.02,y-side*.88,F+1.05),(x-opening/2-.15,y-side*.88,F+1.05),.015,steel)
  box('Masonry lower plinth',(x,y+side*.01,F+.36),(bay,.28,.65),trim) if not isdoor else None
openingwall('Street facade',fronty,bw,bh,bx);openingwall('Platform facade',backy,bw,bh,bx,front=False)
for x in(bx-bw/2,bx+bw/2):box('Station end wall',(x,by,F+bh/2),(.25,bd,bh),wall);box('Station end plinth',(x,by,F+.34),(.28,bd,.68),trim)
box('Facade cornice front',(bx,fronty,F+bh-.12),(bw+.3,.40,.25),trim);box('Facade cornice platform',(bx,backy,F+bh-.12),(bw+.3,.4,.25),trim)
# Clear entrance veranda and approach.
veranda_depth=3.2
probes=[bx-bw/2-1+i*(bw+2)/16 for i in range(17)]
while veranda_depth>.20 and any(not railclear(xx,backy-side*veranda_depth,1.95)for xx in probes):veranda_depth=round(veranda_depth-.10,3)
if veranda_depth>.20:box('Station veranda',(bx,backy-side*veranda_depth/2,F-.12),(bw+2,veranda_depth,.24),floor)
if 'entrance_apron'in D['meshes']:
 md=D['meshes']['entrance_apron']
 if md['faces']:mesh('Raised entrance-to-platform apron reconstructed',md['vertices'],md['faces'],floor)
for x in range(math.ceil((bx-bw/2)/4)*4,int(bx+bw/2)+1,4):
 if veranda_depth<.70:continue
 box('Veranda column',(x,backy-side*(veranda_depth-.30),F+1.7),(.26,.28,3.4),greenpaint if CODE=='QLN' else (peach if CODE=='KFI' else white));box('Veranda column plinth',(x,backy-side*(veranda_depth-.30),F+.22),(.39,.40,.44),trim)
 if CODE!='KFI':box('Veranda roof',(x,backy-side*veranda_depth/2,F+3.6),(4.2,veranda_depth+.1,.12),roofgrey if CODE in['PRND','MYY'] else roof)
# Station name and typical exterior details are real meshes/text, dimensions reconstructed.
sign(SP['name'],(bx,fronty+side*.18,F+bh-.62),min(bw-1,max(7,len(SP['name'])*.45)),.76,min(.38,bw/(max(1,len(SP['name']))*.80)),m=blue,rot=frontrot)
for i in range(max(1,int(bw/16))):
 x=bx-bw/2+3+i*16
 nportal=facade_bays(bw);pw=bw/nportal;portalx=[bx-bw/2+(j+.5)*pw for j in range(nportal)if j==nportal//2 or j%4==0]
 if any(abs(x-dx)<1.5 or abs(x+2-dx)<1.75 for dx in portalx):continue
 box('External distribution cabinet',(x,backy-side*.20,F+.62),(.8,.35,1.18),steel);box('Cabinet warning label',(x,backy-side*.39,F+.8),(.25,.02,.20),yellow)
 noticeboard(x+2,backy-side*.18)
# Exterior ramp uses actual rising mesh; handrails do not block front entry.
nbays=facade_bays(bw);baywidth=bw/nbays;frontdoors=[bx-bw/2+(i+.5)*baywidth for i in range(nbays) if i==nbays//2 or i%4==0];rampx=frontdoors[0];stairsx=frontdoors[len(frontdoors)//2];run=14;yy0=fronty+side*run;yy1=fronty+side*1.0
box('Continuous front entrance landing',(bx,fronty+side*.5,F-.12),(bw,1.0,.24),floor)
vs=[(rampx-1.1,yy0,.05),(rampx+1.1,yy0,.05),(rampx+1.1,yy1,F),(rampx-1.1,yy1,F),(rampx-1.1,yy0,-.1),(rampx+1.1,yy0,-.1),(rampx+1.1,yy1,F-.18),(rampx-1.1,yy1,F-.18)];add('Accessible ramp from forecourt',vs,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],floor)
for x in(rampx-1.2,rampx+1.2):
 rod('Accessible ramp handrail',(x,yy0,.97),(x,yy1,F+.92),.032,steel)
 for k in range(7):
  t=k/6;yy=yy0+(yy1-yy0)*t;zz=.05+(F-.05)*t;rod('Ramp rail upright',(x,yy,zz),(x,yy,zz+.92),.026,steel)
for k in range(6):box('Front approach granite step',(stairsx,fronty+side*(2.6-k*.40),F*(k+1)/12),(min(7,bw*.4),.42,F*(k+1)/6),concrete)
# Roof shapes vary by observed station, with real terracotta tile rows and ridge.
col('06_LIFT_OFF_ROOFS')
if CODE=='QLN':
 box('Interior ceiling clear of staff stair',(bx+4.5,by,F+bh+.05),(bw-9,bd,.16),white)
 box('Interior stair-side ceiling',(bx-bw/2+4.5,by+1.2,F+bh+.05),(9,bd-2.4,.16),white)
else:box('Interior plaster ceiling',(bx,by,F+bh+.05),(bw+.15,bd+.15,.16),white)
if CODE=='QLN':
 hroof=F+bh+3.30
 box('Kollam predominantly flat upper roof',(bx,by,hroof),(bw+.7,bd+.7,.22),concrete)
 # Dated facade photo has distinct red-tile patches, not one repeated full-length gable.
 for rc,rw in[(bx-43,34),(bx,25)]:
  for sy in(-1,1):
   add('Kollam discrete red-tiled roof pavilion',[(rc-rw/2,by,hroof+1.55),(rc+rw/2,by,hroof+1.55),(rc+rw/2,by+sy*(bd/2+.6),hroof+.08),(rc-rw/2,by+sy*(bd/2+.6),hroof+.08)],[(0,1,2,3)],red)
   for k in range(int(rw/.48)+1):
    xx=rc-rw/2+k*.48;rod('Kollam pavilion terracotta tile rolls',(xx,by,hroof+1.59),(xx,by+sy*(bd/2+.6),hroof+.12),.035,red,6)
  rod('Kollam pavilion ridge',(rc-rw/2,by,hroof+1.62),(rc+rw/2,by,hroof+1.62),.08,red,10)
elif SP['roof'] in['tile','tileflat','sheet']:
 extra=3.15 if CODE=='QLN' else (1.5 if CODE=='KPY' else 0);span=bd+1.5;peak=F+bh+extra+SP.get('roof_rise',1.7);eave=F+bh+extra+.10
 for sy in(-1,1):
  vs=[(bx-bw/2-.8,by,peak),(bx+bw/2+.8,by,peak),(bx+bw/2+.8,by+sy*span/2,eave),(bx-bw/2-.8,by+sy*span/2,eave)];add('Terracotta pitched roof plane' if SP['roof']!='sheet' else 'Grey corrugated station roof plane',vs,[(0,1,2,3)],red if SP['roof']!='sheet' or SP.get('roof_color')=='red' else roofgrey)
  for i in range(int(bw/.45)+4):
   x=bx-bw/2-.5+i*.45;rod('Terracotta half-round tile channels' if SP['roof']!='sheet' else 'Station roof corrugations',(x,by,peak+.035),(x,by+sy*span/2,eave+.035),.040 if SP['roof']!='sheet' else .018,red if SP['roof']!='sheet' or SP.get('roof_color')=='red' else roofgrey,6)
  for j in range(1,9):
   t=j/9;rod('Terracotta horizontal tile laps',(bx-bw/2-.7,by+sy*span/2*t,peak+(eave-peak)*t+.025),(bx+bw/2+.7,by+sy*span/2*t,peak+(eave-peak)*t+.025),.032,red if SP['roof']!='sheet' or SP.get('roof_color')=='red' else roofgrey,6)
 rod('Terracotta ridge cap',(bx-bw/2-.8,by,peak+.07),(bx+bw/2+.8,by,peak+.07),.09,red if SP['roof']!='sheet' or SP.get('roof_color')=='red' else roofgrey,10)
else:
 box('Flat concrete weathered roof slab',(bx,by,F+bh+.20),(bw+.8,bd+.8,.22),concrete)
 for yy in(fronty,backy):box('Low blue parapet',(bx,yy,F+bh+.45),(bw+.8,.23,.42),trim)

# Station-specific roof pavilion and clerestory details from dated photographs.
if CODE=='KPY':
 col('06B_KARUNAGAPPALLI_2017_CLERESTORY')
 for yy in(fronty,backy):
  box('KPY white clerestory wall',(bx,yy,F+bh+.74),(bw,.25,1.5),white)
  box('KPY dark intermediate eave',(bx,yy+side*.24,F+bh+.02),(bw+1,.65,.16),dark)
  for xx in range(int(bx-bw/2)+3,int(bx+bw/2),5):
   box('KPY clerestory ventilator',(xx,yy+side*.14,F+bh+.82),(.82,.08,.38),dark)
   box('KPY salmon vertical panel',(xx,yy,F+1.9),(.65,.28,3.8),salmon)
  box('KPY central salmon cross-gable',(bx,yy+side*.20,F+bh+.66),(5,.45,1.62),salmon)
  add('KPY central triangular gable',[(bx-2.7,yy+side*.4,F+bh+1.5),(bx+2.7,yy+side*.4,F+bh+1.5),(bx,yy+side*.4,F+bh+2.75)],[(0,1,2)],salmon)
  for sg in(-1,1):rod('KPY gable dark verge',(bx,yy+side*.43,F+bh+2.83),(bx+sg*2.85,yy+side*.43,F+bh+1.4),.09,wood)
 for xx in range(int(bx-bw/2),int(bx+bw/2),1):box('KPY yellow garden picket',(xx,fronty+side*3,.62),(.09,.08,1.1),yellow)
if CODE=='VAK':
 col('06C_VARKALA_SIVAGIRI_CENTRAL_PAVILION')
 box('Varkala raised central ochre pavilion',(bx,by,F+bh+.65),(8,bd*.65,1.6),ochre)
 # A small Kerala-style uplift at the roof corners, not an invented tower.
 for sy in(-1,1):
  ys=[0,bd*.28,bd*.48,bd*.58];zs=[F+bh+3.0,F+bh+2.5,F+bh+1.85,F+bh+2.08]
  for j in range(3):add('Varkala pavilion upturned roof segment',[(bx-5,by+sy*ys[j],zs[j]),(bx+5,by+sy*ys[j],zs[j]),(bx+5.3,by+sy*ys[j+1],zs[j+1]),(bx-5.3,by+sy*ys[j+1],zs[j+1])],[(0,1,2,3)],red)
  rod('Varkala decorative roof finial',(bx,by,F+bh+3.0),(bx,by,F+bh+3.85),.045,ochre)
 sign('VARKALA SIVAGIRI',(bx,fronty+side*.35,F+bh+1.0),7.4,.55,.32,m=ochre,rot=frontrot)

if CODE=='OCR':
 col('06D_OCHIRA_2019_ADJACENT_LOW_WING')
 wx=bx+bw/2+6.3;wy=by
 box('Ochira low wing floor',(wx,wy,F-.12),(12.6,8.4,.24),floor)
 openingwall('Ochira ancillary platform wing',wy-side*4.2,12.6,3.1,wx,front=False)
 openingwall('Ochira ancillary road wing',wy+side*4.2,12.6,3.1,wx)
 box('Ochira ancillary end wall',(wx+6.3,wy,F+1.55),(.24,8.4,3.1),mint)
 box('Ochira ancillary blue sheet roof',(wx,wy,F+3.25),(13.8,9.1,.15),roof)
 desk(wx-2,wy);bench(wx+2,wy+1);luminaire(wx,wy,F+2.98);area('Ochira wing light',(wx,wy,F+2.85),(wx,wy,F),180,3)
 for xx in(bx-bw/2-.5,bx+bw/2+.5):
  rod('Ochira raised white roof verge',(xx,by-bd/2-.5,F+bh+.2),(xx,by,F+bh+1.9),.10,white)
  rod('Ochira raised white roof verge',(xx,by,F+bh+1.9),(xx,by+bd/2+.5,F+bh+.2),.10,white)
if CODE=='AMY':
 col('06E_AKATHUMURI_YELLOW_ENTRY_AND_BREEZE_BLOCKS')
 # The perforated screen is genuine open mesh rather than an opaque painted panel.
 sx=bx+bw/2-(bw/max(3,int(bw/4)))/2;yy=fronty+side*.16
 for i in range(8):
  for j in range(7):
   xx=sx-1.15+i*.30;zz=F+.8+j*.23
   box('Akathumuri breeze-block vertical web',(xx,yy,zz),(.045,.09,.23),white)
   box('Akathumuri breeze-block horizontal web',(xx+.13,yy,zz-.09),(.30,.09,.045),white)
 box('Akathumuri yellow entrance sunshade',(bx,fronty+side*.32,F+2.85),(bw+.3,.70,.18),ochre)
 for xx in(bx-1,bx+1):
  for zz in(F+.3,F+1,F+1.7,F+2.4):box('Akathumuri open gate horizontal rail',(xx,fronty-side*.7,zz),(.07,1.3,.018),dark)
 for k in range(6):box('Akathumuri upper vent louvre',(bx+bw*.35,fronty+side*.15,F+bh+.12+k*.07),(1.1,.08,.04),wood)
if CODE=='EVA':
 col('06F_EDAVAI_VENTILATORS_AND_GEOMETRIC_GRILLES')
 for xx in range(int(bx-bw/2)+2,int(bx+bw/2),4):
  box('Edavai high horizontal vent',(xx,backy-side*.16,F+3.28),(1.05,.10,.42),wood)
  if any(abs(xx-dx)<1.2 for dx in frontdoors):continue
  for dx in(-.35,0,.35):box('Edavai grille upright',(xx+dx,backy-side*.20,F+1.0),(.035,.05,1.9),blue)
  for k in range(4):
   z=F+.35+k*.4
   rod('Edavai diamond grille',(xx-.35,backy-side*.21,z),(xx,backy-side*.21,z+.24),.017,blue)
   rod('Edavai diamond grille',(xx,backy-side*.21,z+.24),(xx+.35,backy-side*.21,z),.017,blue)
if CODE=='IRP':
 col('06H_IRAVIPURAM_2016_GEOMETRIC_WINDOW_GRILLES')
 for yy in(fronty,backy):
  for xx in(bx-bw/3,bx+bw/3):
   for dx in(-.4,0,.4):
    rod('Iravipuram white grille upright',(xx+dx,yy,F+1.0),(xx+dx,yy,F+2.48),.023,white)
    for z in(F+1.18,F+1.65,F+2.12):
     rod('Iravipuram diagonal grille',(xx+dx-.12,yy,z),(xx+dx+.12,yy,z+.22),.020,white)
     rod('Iravipuram diagonal grille',(xx+dx+.12,yy,z+.22),(xx+dx-.12,yy,z+.42),.020,white)

if CODE=='MYY':
 col('06I_MAYYANAD_2023_BLUE_CROSS_GABLE')
 yy=fronty+side*.20
 for dx in(-1.75,1.75):box('Mayyanad blue central entry pier',(bx+dx,yy,F+bh/2),(.65,.38,bh),blue)
 box('Mayyanad blue upper entrance bay',(bx,yy,F+(2.65+bh)/2),(4.2,.38,bh-2.65),blue)
 add('Mayyanad red cross-gable boards',[(bx-4.1,yy+side*.3,F+bh+.05),(bx+4.1,yy+side*.3,F+bh+.05),(bx,yy+side*.3,F+bh+2.0)],[(0,1,2)],red)
 for i in range(19):
  xx=bx-3.8+i*.42;top=F+bh+2.0-abs(xx-bx)*1.95/4.1
  rod('Mayyanad vertical gable board seam',(xx,yy+side*.34,F+bh+.08),(xx,yy+side*.34,top),.014,wood)
  rod('Mayyanad scalloped gable board end',(xx,yy+side*.34,F+bh+.08),(xx,yy+side*.36,F+bh+.08),.17,red,12)
 for dx,dz in[(0,.26),(-.18,0),(.18,0)]:rod('Mayyanad trefoil vent motif',(bx+dx,yy+side*.35,F+bh+.75+dz),(bx+dx,yy+side*.37,F+bh+.75+dz),.17,dark,14)
 box('Mayyanad projecting entry hood',(bx,fronty+side*.80,F+2.9),(4.8,1.7,.14),concrete)
 sign('MAYYANAD',(bx,yy+side*.22,F+4.0),3.6,.60,.35,m=yellow,rot=frontrot,textmat=dark)
 for xx in(bx-8,bx,bx+8):box('Mayyanad upper timber vent',(xx,yy,F+3.5),(1.1,.25,.55),wood)
if CODE=='KFI':
 col('06J_KAPPIL_2017_PEACH_ROSE_VERANDA')
 for xx in range(int(bx-bw/2)+1,int(bx+bw/2),3):box('Kappil blue parapet accent',(xx,fronty+side*.13,F+bh+.43),(1.15,.05,.30),turquoise)
 add('Kappil rose sloping veranda roof',[(bx-bw/2-.7,backy,F+3.8),(bx+bw/2+.7,backy,F+3.8),(bx+bw/2+.7,backy-side*3.2,F+3.1),(bx-bw/2-.7,backy-side*3.2,F+3.1)],[(0,1,2,3)],rosem)
 for p in D['platforms']:
  lo,_,hi,_=p['bbox']
  for xx in range(int(lo)+12,int(hi)-10,7):
   yy=widthat(p,xx)
   if not yy:continue
   cy=sum(yy)/2
   for j in range(3):
    x=xx+j*.18;y=cy+random.uniform(-1.3,1.3)
    add('Kappil sparse platform-end grass',[(x-.05,y,F+.02),(x+.05,y,F+.02),(x+.03,y,F+random.uniform(.15,.27))],[(0,1,2)],leaf)
if CODE=='KVU':
 col('06K_KADAKKAVUR_2019_WHITE_GRILLE_FRONT')
 box('Kadakkavur long ochre sunshade',(bx,fronty+side*.36,F+3.1),(bw+.5,.85,.18),ochre)
 for xx in range(int(bx-bw/2)+3,int(bx+bw/2)-1,4):
  box('Kadakkavur brown clerestory window',(xx,fronty+side*.15,F+3.9),(1.1,.20,.55),wood)
  if any(abs(xx-dd)<1.7 for dd in frontdoors):continue
  for dx in(-.5,0,.5):
   rod('Kadakkavur white grille upright',(xx+dx,fronty+side*.18,F+.9),(xx+dx,fronty+side*.18,F+2.55),.032,white)
   for z in(F+1.05,F+1.55,F+2.05):
    rod('Kadakkavur white grille diamond',(xx+dx-.17,fronty+side*.18,z),(xx+dx+.17,fronty+side*.18,z+.25),.026,white)
    rod('Kadakkavur white grille diamond',(xx+dx+.17,fronty+side*.18,z+.25),(xx+dx-.17,fronty+side*.18,z+.5),.026,white)

if CODE=='CRY':
 col('06G_CHIRAYINKEEZH_2025_REDEVELOPED_GATEWAY')
 gy=fronty+side*29;gw=24;gh=7.6
 for dx in(-gw/2,0,gw/2):
  box('Chirayinkeezh white entrance pier',(bx+dx,gy,gh/2),(.72,.85,gh),white)
  box('Chirayinkeezh dark red pier plinth',(bx+dx,gy,.60),(1.15,1.15,1.2),red)
 box('Chirayinkeezh wide white gateway fascia',(bx,gy,gh),(gw+2,1.65,1.05),white)
 for sy in(-1,1):add('Chirayinkeezh gateway red tiled roof',[(bx-gw/2-1.5,gy,gh+1.45),(bx+gw/2+1.5,gy,gh+1.45),(bx+gw/2+1.5,gy+sy*1.3,gh+.5),(bx-gw/2-1.5,gy+sy*1.3,gh+.5)],[(0,1,2,3)],red)
 box('Chirayinkeezh raised central gateway panel',(bx,gy+side*.1,gh+1.42),(3,1.9,1.7),salmon)
 add('Chirayinkeezh central gateway gable',[(bx-1.65,gy+side*1.05,gh+2.2),(bx+1.65,gy+side*1.05,gh+2.2),(bx,gy+side*1.05,gh+3.20)],[(0,1,2)],salmon)
 for sg in(-1,1):rod('Chirayinkeezh white gable trim',(bx,gy+side*1.09,gh+3.25),(bx+sg*1.75,gy+side*1.09,gh+2.14),.065,white)
 sign('CHIRAYINKEEZH',(bx+8,gy+side*.86,gh),8,.55,.32,m=white,rot=frontrot,textmat=red)
 # Long covered pedestrian approach, entirely outside the station running roads.
 for xx in range(int(bx-bw/2),int(bx+bw/2)+1,5):
  for yy in(fronty+side*4,fronty+side*6.5):rod('Chirayinkeezh approach canopy post',(xx,yy,.05),(xx,yy,3.35),.045,white)
  box('Chirayinkeezh blue approach canopy',(xx,fronty+side*5.25,3.55),(5.2,3.2,.15),roof)

# Fully modelled partitioned ticket / waiting / staff / WC rooms; layouts intentionally reconstructed.
col('07_FURNISHED_INTERIORS_RECONSTRUCTED')
rooms=3 if SP['kind']in['small','medium'] else (2 if SP['kind']=='halt' else 6);roomw=bw/rooms
for ri in range(rooms):
 x=bx-bw/2+(ri+.5)*roomw;wallslots=[x+roomw*f for f in(.28,-.28,.12,-.12,.38,-.38)if all(abs(x+roomw*f-dd)>1.8 for dd in frontdoors)];nx=wallslots[0]if wallslots else x;tx=wallslots[-1]if wallslots else x;label=['TICKETS','WAITING','STATION OFFICE','WAITING LOUNGE','STAFF / CONTROL','TOILETS'][ri if rooms>2 else ri]
 if ri>0:
  px=bx-bw/2+ri*roomw
  # Side partitions leave a rear circulation opening.
  if not(CODE=='QLN' and abs(px-bx)<3):box('Internal room partition',(px,by,F+bh/2),(.14,max(1,bd-3.0),bh),cream)
 for lx in [x] if roomw<8 else[x-roomw*.25,x+roomw*.25]:
  luminaire(lx,by,F+bh-.15);fan(lx,by-.8,F+bh-.75);area('Interior daylight fluorescent',(lx,by,F+bh-.30),(lx,by,F),180 if SP['kind']=='halt' else 250,3)
 sign(label,(x,backy-side*.17,F+2.95),min(roomw-.5,4.6),.48,.20,rot=0 if side>0 else math.pi)
 if ri==0:
  cy=by;count=SP.get('ticket_counters',{'halt':1,'small':1,'medium':2,'junction':4}[SP['kind']])
  for j in range(count):
   xx=x+(j-(count-1)/2)*2.5;box('Ticket counter masonry base',(xx,cy,F+.53),(2.35,.5,1.06),trim);box('Ticket counter polished ledge',(xx,cy,F+1.1),(2.47,.84,.09),dark)
   for dx in(-1.12,1.12):box('Counter grille mullion',(xx+dx,cy,F+1.8),(.07,.08,1.4),steel)
   for k in range(15):
    dx=-1.02+k*.145
    if abs(dx)>.34:rod('Booking counter security grille',(xx+dx,cy,F+1.15),(xx+dx,cy,F+2.48),.011,steel)
   for zz in(F+1.63,F+2.05,F+2.47):rod('Ticket grille horizontal bar',(xx-1.1,cy,zz),(xx+1.1,cy,zz),.011,steel)
   box('Counter transaction tray',(xx,cy-.30,F+1.13),(.60,.35,.035),steel);sign('%02d  TICKETS'%(j+1),(xx,cy-.065,F+2.73),2,.38,.16);desk(xx,cy+1.9)
   for dx in(-.85,.85):
    for yy in(cy-1.0,cy-2.2):rod('Ticket queue upright',(xx+dx,yy,F),(xx+dx,yy,F+1.0),.024,steel)
    rod('Ticket queue guide rail',(xx+dx,cy-2.2,F+.93),(xx+dx,cy-.8,F+.93),.023,steel)
  if roomw>8:
   for xx in(x-roomw*.33,x+roomw*.33):bench(xx,by-bd*.27)
  noticeboard(nx,fronty-side*.15)
 elif label in['WAITING','WAITING LOUNGE']:
  for yy in(by-bd*.22,by+bd*.22):
   for xx in[x]if roomw<7 else[x-roomw*.23,x+roomw*.23]:bench(xx,yy)
  noticeboard(nx,fronty-side*.15);binunit(x-roomw*.35,by);box('Passenger information television',(tx,fronty-side*.2,F+2.5),(1.30,.12,.75),dark);box('Television screen',(tx,fronty-side*.28,F+2.5),(1.15,.025,.63),glass)
  for xx in(x-roomw*.30,x+roomw*.30):box('Wall charging outlet',(xx,fronty-side*.16,F+1.2),(.14,.05,.12),white)
 elif label=='TOILETS':
  for j in range(max(2,int(roomw/2))):
   xx=x-roomw/2+1.1+j*2;box('WC cubicle partition',(xx-.95,by+bd*.20,F+1.1),(.08,bd*.45,2.2),blue);box('WC bowl',(xx,by+bd*.25,F+.40),(.45,.65,.23),white);rod('WC pedestal',(xx,by+bd*.25,F),(xx,by+bd*.25,F+.32),.18,white,12);box('WC cistern',(xx,by+bd*.37,F+.78),(.46,.2,.54),white)
  for j in range(2):
   xx=x-.7+j*1.4;box('WC washbasin',(xx,by-bd*.3,F+.79),(.8,.55,.14),white);rod('Washbasin tap',(xx,by-bd*.3+.17,F+.85),(xx,by-bd*.3+.17,F+1.08),.020,steel);box('Washroom mirror',(xx,fronty-side*.17,F+1.72),(.9,.03,.94),glass)
 else:
  for xx in[x]if roomw<8 else[x-roomw*.23,x+roomw*.23]:desk(xx,by)
  for xx in(x-roomw*.32,x+roomw*.32):
   box('Office filing cabinet',(xx,fronty-side*.45,F+1),(.8,.55,2),blue)
   for zz in(.3,.7,1.1,1.5,1.9):box('Cabinet drawer face',(xx,fronty-side*.76,F+zz),(.72,.06,.33),steel);box('Cabinet drawer pull',(xx,fronty-side*.80,F+zz),(.20,.035,.025),dark)
  noticeboard(nx,fronty-side*.18)
# A halt still has useful small-scale real details, without invented concourses.
for x in(bx-bw/2+1,bx+bw/2-1):
 box('Wall switch plate',(x,backy-side*.16,F+1.4),(.15,.05,.2),white);box('Wall electrical conduit',(x,backy-side*.17,F+2.3),(.025,.03,1.6),steel)

# Distinctive Kollam historic facade and service-yard buildings.
if CODE=='QLN':
 col('08_KOLLAM_HISTORIC_TERMINAL_2017_2020')
 upper=3.15
 for y in(fronty,backy):
  box('Kollam first floor slab',(bx,y,F+bh+.15),(bw,.6,.30),red)
  for x in range(int(bx-bw/2)+2,int(bx+bw/2)-1,5):
   box('Kollam upper red mullion',(x,y,F+bh+upper/2),(.33,.35,upper),red);box('Kollam upper green pier',(x+2.5,y,F+bh+upper/2),(.65,.35,upper),greenpaint);box('Kollam upper dark window',(x+1.25,y,F+bh+1.55),(1.75,.06,1.48),dark)
  box('Kollam upper lintel',(bx,y,F+bh+upper),(bw,.55,.36),red);box('Kollam upper sill',(bx,y,F+bh+.72),(bw,.48,.45),mint)
 box('Kollam central entrance portico',(bx,fronty-side*0+side*3,F+3.35),(22,6.5,.5),red)
 for dx in(-9,9):box('Kollam yellow portico column',(bx+dx,fronty+side*5.6,F+1.65),(.55,.60,3.3),yellow)
 for xx in(bx-bw/2,bx+bw/2):box('Kollam upper end wall',(xx,by,F+bh+upper/2),(.25,bd,upper),mint)
 upperfloor=F+bh+.30
 box('Kollam upper staff main floor',(bx+4.5,by,upperfloor-.12),(bw-9,bd,.24),floor)
 box('Kollam upper staff stair-side floor',(bx-bw/2+4.5,by+1.2,upperfloor-.12),(9,bd-2.4,.24),floor)
 for xx in range(int(bx-bw/2)+8,int(bx+bw/2)-5,15):
  desk(xx,by,upperfloor);luminaire(xx,by,upperfloor+2.70);fan(xx,by-2,upperfloor+2.22)
  box('Kollam upper filing cabinet',(xx+4,by+bd*.28,upperfloor+1),(.9,.6,2),greenpaint)
  for yy in(by-bd/2+1.4,by+bd/2-1.4):
   if xx<bx-bw/2+12 and yy<by:continue
   bench(xx,yy,z=upperfloor)
  area('Kollam reconstructed upper office light',(xx,by,upperfloor+2.55),(xx,by,upperfloor),220,3)
 # Reconstructed internal staff stair and upper access landing.
 for k in range(24):box('Kollam upper staff stair tread',(bx-bw/2+2+k*.27,by-bd/2+1.2,F+(upperfloor-F)*(k+1)/24-.045),(.29,1.8,.09),concrete)
 for yy in(by-bd/2+.30,by-bd/2+2.10):
  rod('Kollam upper staff stair stringer',(bx-bw/2+1.85,yy,F-.12),(bx-bw/2+8.45,yy,upperfloor-.12),.09,steel)
  for k in range(7):
   t=k/6;xx=bx-bw/2+2+6.5*t;zz=F+(upperfloor-F)*t
   rod('Kollam upper stair rail baluster',(xx,yy,zz),(xx,yy,zz+1.05),.024,steel)
 for yy in(by-bd/2+.25,by-bd/2+2.15):rod('Kollam upper staff stair rail',(bx-bw/2+2,yy,F+1.05),(bx-bw/2+8.5,yy,upperfloor+1.05),.03,steel)
 box('Kollam upper stair landing',(bx-bw/2+8.8,by-bd/2+1.2,upperfloor-.10),(1.0,2.4,.2),floor)
 # Circular station emblem, not an unsupported clock.
 rod('Kollam circular railway emblem',(bx,fronty+side*.32,F+bh+1.55),(bx,fronty+side*.44,F+bh+1.55),1.08,white,48)
 txt('Kollam emblem lettering','SR',(bx,fronty+side*.47,F+bh+1.45),.44,blue,frontrot)
 for sg in(-1,1):
  x0=bx+sg*13
  for k in range(6):box('Kollam red-white stepped entry panel',(x0+sg*k*.55,fronty+side*.15,F+.38+k*.42),(.52,.12,.70),red if k%2==0 else white)
 sign('KOLLAM JUNCTION',(bx,fronty+side*.38,F+bh+3.50),13,.72,.46,m=greenpaint,rot=frontrot)
 col('09_KOLLAM_YARD_SERVICE_BUILDINGS_RECONSTRUCTED')
 # The service yard is populated without rolling stock; these are approximate enclosures.
 for name,x,y,w,d,h in [('MEMU maintenance shed',216.4,-40.3,210.2,20.0,9),('Goods shed',-415.3,30.1,65.3,21.2,6),('FCI storage',-412.7,8.6,79.4,19.4,6),('Reservation centre',12,-48,17,30,4.3),('Second terminal',-146.6,99.8,29.0,16.4,4.6)]:
  if name.startswith('MEMU'):
   md=D['meshes']['shed_floor'];mesh(name+' pit-cut floor',md['vertices'],md['faces'],concrete)
  else:box(name+' floor',(x,y,.0),(w,d,.20),concrete)
  for sg in(-1,1):box(name+' long side',(x,y+sg*d/2,h/2),(w,.25,h),cream)
  for sx in(-1,1):
   for sy in(-1,1):box(name+' door jamb',(x+sx*w/2,y+sy*(d/2-.22),h/2),(.30,.44,h),white)
  box(name+' metal roof',(x,y,h+.1),(w+1,d+1,.22),roof)
  for xx in range(int(x-w/2)+5,int(x+w/2),8):box(name+' steel portal',(xx,y,h-.6),(.18,d,.30),steel)
  sign(name.upper(),(x,y-d/2-.2,h-.9),min(w*.6,18),.9,.4)
 # Maintenance details are reconstructions within the mapped shed footprint.
 for yy in(-32.85,-39.93,-46.61):
  for xx in range(125,306,15):
   luminaire(xx,yy,8.2)
  for syy in(yy-1.0,yy+1.0):box('MEMU inspection pit painted rim',(216,syy,-.04),(180,.14,.13),yellow)
  box('MEMU inspection pit floor',(215,yy,-1.22),(180,1.0,.14),concrete)
  for syy in(yy-.55,yy+.55):box('MEMU inspection pit retaining wall',(215,syy,-.62),(180,.10,1.2),concrete)
  for xx in(125,305):box('MEMU inspection pit end wall',(xx,yy,-.62),(.12,1.1,1.2),concrete)
 for xx in range(130,305,18):
  for yy in(-36.1,-43.2):
   box('MEMU workshop tool cabinet',(xx,yy,.68),(1.4,.50,1.25),blue)
   for z in(.3,.6,.9,1.2):box('MEMU cabinet drawer pull',(xx,yy-.27,z),(.30,.03,.025),steel)
 for xx in(130,205,280):
  rod('MEMU shed crane runway support',(xx,-40.5,7.7),(xx,-40.5,8.5),.055,steel)
  box('MEMU travelling hoist beam',(xx,-40.5,7.85),(.4,16,.45),yellow)
 # The separate FCI Godown is anchored to its actual mapped footprint, including its oblique orientation.
 godowns=json.loads((R/'source/yard_building_footprints.json').read_text())
 gg=next(b for b in godowns if b['id']=='243514280');pp=gg['xy'][:-1]
 gx=sum(p[0]for p in pp)/4;gy=sum(p[1]for p in pp)/4;ang=math.atan2(pp[2][1]-pp[1][1],pp[2][0]-pp[1][0]);gw=math.dist(pp[1],pp[2]);gd=math.dist(pp[0],pp[1])
 box('Mapped FCI Godown floor',(gx,gy,-.04),(gw,gd,.16),concrete,ang)
 for a,b in zip(pp,pp[1:]+pp[:1]):
  mid=((a[0]+b[0])/2,(a[1]+b[1])/2);aa=math.atan2(b[1]-a[1],b[0]-a[0]);box('Mapped FCI Godown masonry wall',(*mid,3.1),(math.dist(a,b),.30,6.2),cream,aa)
 box('Mapped FCI Godown roof',(gx,gy,6.4),(gw+1.3,gd+1.3,.25),roof,ang)
 for k in range(12):
  dx=-gw*.4+k*gw*.07
  for dy in(-gd*.27,gd*.27):
   xx=gx+dx*math.cos(ang)-dy*math.sin(ang);yy=gy+dx*math.sin(ang)+dy*math.cos(ang)
   box('FCI reconstructed storage pallets',(xx,yy,.24),(2.4,1.8,.25),wood,ang)
   for z in(.65,1.25,1.85):box('FCI reconstructed bag-stack proxy',(xx,yy,z),(2.2,1.6,.55),paper,ang)
 # Secondary gateway is a separate documented feature, not another copy of main facade.
 sx,sy=-146.6,125
 for dx in(-7,-5,5,7):rod('Secondary terminal dark gateway column',(sx+dx,sy,0),(sx+dx,sy,5.4),.34,dark,16)
 box('Secondary terminal white gateway beam',(sx,sy,5.6),(17,1.25,.85),white);sign('KOLLAM JUNCTION',(sx,sy-.67,5.62),14,.52,.44,m=white,textmat=greenpaint)

# --- PEDESTRIAN OVERBRIDGE (where supported); OHE CONTACT SYSTEM ---
col('10_FOOTBRIDGE_AND_SAFE_ACCESS_RECONSTRUCTED')
bridge_x=80
if SP['footbridge']:
 centers=[]
 for p in D['platforms']:
  yy=widthat(p,bridge_x)
  if yy:centers.append(sum(yy)/2)
 if centers:
  miny,maxy=min(centers),max(centers);deck=8.60;flight_top=bridge_x-1.5;flight_start=flight_top-14.7;box('Footbridge deck',(bridge_x,(miny+maxy)/2,deck-.12),(3.0,maxy-miny+4,.24),steel)
  for yy in sorted(set(centers)):
   # Straight stair flight along X, wholly within platform width.
   for k in range(42):box('Footbridge individual stair tread',(flight_start+(k+.5)*.35,yy,F+(deck-F)*(k+1)/42-.05),(.37,2.45,.10),concrete)
   for sg in(-1,1):
    rod('Footbridge stair stringer',(flight_start,yy+sg*1.25,F-.10),(flight_top,yy+sg*1.25,deck-.12),.12,steel)
    rod('Footbridge stair top rail',(flight_start,yy+sg*1.27,F+1.08),(flight_top,yy+sg*1.27,deck+1.08),.035,steel)
    for k in range(15):
     t=k/14;xx=flight_start+t*14.7;zz=F+(deck-F)*t;rod('Footbridge stair baluster',(xx,yy+sg*1.27,zz),(xx,yy+sg*1.27,zz+1.08),.02,steel)
   add('Covered footbridge stair flight roof',[(flight_start-.5,yy-1.6,F+2.50),(flight_start-.5,yy+1.6,F+2.50),(flight_top+.4,yy+1.6,deck+2.50),(flight_top+.4,yy-1.6,deck+2.50)],[(0,1,2,3)],roofgrey)
   for k in range(5):
    t=k/4;xx=flight_start+14.7*t;zz=F+(deck-F)*t
    for sg in(-1,1):rod('Covered stair roof upright',(xx,yy+sg*1.43,zz),(xx,yy+sg*1.43,zz+2.45),.030,steel)
   for dy in(-1.43,1.43):rod('Footbridge platform support',(bridge_x+1.15,yy+dy,F),(bridge_x+1.15,yy+dy,deck-.2),.085,steel)
  for xx in(bridge_x-1.48,bridge_x+1.48):
   for yy in range(math.floor(miny)-2,math.ceil(maxy)+2):
    if xx<bridge_x and any(abs(yy-c)<2 or abs(yy+1-c)<2 for c in centers):continue
    rod('Footbridge horizontal handrail',(xx,yy,deck+1.13),(xx,yy+1,deck+1.13),.035,steel)
    rod('Footbridge deck baluster',(xx,yy,deck),(xx,yy,deck+1.13),.020,steel)
  box('Footbridge blue roof',(bridge_x,(miny+maxy)/2,deck+2.4),(3.7,maxy-miny+5,.12),roof)
  for yy in range(math.floor(miny),math.ceil(maxy)+1,4):
   for xx in(bridge_x-1.5,bridge_x+1.5):
    if xx<bridge_x and any(abs(yy-c)<1.6 for c in centers):continue
    rod('Footbridge roof upright',(xx,yy,deck),(xx,yy,deck+2.4),.035,steel)
col('11_OVERHEAD_ELECTRIFICATION_RECONSTRUCTED')
# Wires follow every electrified mapped route; fittings are explicit reconstructions.
for r in D['routes']:
 if r['tags'].get('electrified')=='no':continue
 ps=r['xy']
 for a,b in zip(ps,ps[1:]):
  rod('OHE contact wire',(a[0],a[1],6.08),(b[0],b[1],6.08),.009,dark,6);rod('OHE catenary wire',(a[0],a[1],6.78),(b[0],b[1],6.78),.011,dark,6)
 for x,y,a in sample(ps,9):rod('OHE vertical dropper',(x,y,6.08),(x,y,6.78),.008,steel,6)
# Portal spacing restrained around station; no forest of duplicate masts.
for x in range(math.ceil(D['coverage_bbox_m'][0]/54)*54,int(D['coverage_bbox_m'][2])+1,54):
 ys=[]
 for ps in routes:
  for a,b in zip(ps,ps[1:]):
   if min(a[0],b[0])<=x<max(a[0],b[0]) and abs(b[0]-a[0])>1e-5:ys.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
 ys.sort();groups=[]
 for y in ys:
  if not groups or y-groups[-1][-1]>25:groups.append([y])
  else:groups[-1].append(y)
 for group in groups:
  lo,hi=min(group)-3.2,max(group)+3.2
  if abs(x-bx)<bw/2+1 and by-bd/2-1<lo<by+bd/2+1:lo=by-bd/2-2
  if abs(x-bx)<bw/2+1 and by-bd/2-1<hi<by+bd/2+1:hi=by+bd/2+2
  if SP['footbridge'] and abs(x-bridge_x)<5:continue
  for y in(lo,hi):
   if not railclear(x,y,2.05):continue
   box('OHE mast concrete base',(x,y,.20),(.72,.72,.5),concrete)
   for sx in(-.15,.15):box('OHE lattice upright',(x+sx,y,4.05),(.06,.16,8.0),steel)
   for z in range(1,8):rod('OHE lattice diagonal',(x-.15,y,z),(x+.15,y,z+.8),.018,steel,6)
  rod('OHE portal crossbeam',(x,lo,7.85),(x,hi,7.85),.09,steel)
  for y in group:
   rod('OHE registration arm',(x,y-1,7.5),(x,y+.20,6.32),.026,steel)
   for z in(7.12,7.20,7.28):rod('OHE porcelain insulator',(x,y-1,z),(x,y-1,z+.03),.072,white,8)

# --- FORECOURT, LANDSCAPE, SMALL DETAILS ---
col('12_GROUND_FORECOURT_AND_TROPICAL_CONTEXT')
bbox=D['coverage_bbox_m'];gx=(bbox[0]+bbox[2])/2;gy=(bbox[1]+bbox[3])/2;gw=bbox[2]-bbox[0]+70;gd=bbox[3]-bbox[1]+70
if 'terrain'in D['meshes']:
 md=D['meshes']['terrain'];mesh('Continuous terrain with service pit openings',md['vertices'],md['faces'],grass)
else:box('Continuous evidence-boundary terrain',(gx,gy,-.44),(gw,gd,.20),grass)
box('Station approach forecourt',(bx,fronty+side*12,-.03),(bw+22,22,.16),asphalt)
for x in range(int(bx-bw/2)-8,int(bx+bw/2)+9,2):box('Forecourt alternating kerb',(x,fronty+side*22,.12),(1.95,.35,.30),white if x%4==0 else dark)
for xx in(bx-bw/2-5,bx+bw/2+5):
 rod('Forecourt lamp mast',(xx,fronty+side*18,.1),(xx,fronty+side*18,7.0),.055,steel);box('Forecourt LED lamp',(xx,fronty+side*17.6,7.0),(.6,1.0,.13),dark)
# Source-mapped water polygons are used where they fall within the scene, without inventing a lake.
if 'water' in D['meshes']:
 for key,ma in [('water',water),('shorebanks',earth)]:
  md=D['meshes'][key]
  if md['faces']:mesh('Mapped '+key+' with reconstructed elevations',md['vertices'],md['faces'],ma)
else:
 for cc in D['context']:
  if cc['tags'].get('natural')=='water' and len(cc['xy'])>3 and cc['xy'][0]==cc['xy'][-1]:
   ps=cc['xy'][:-1];mesh('Mapped backwater surface '+cc['id'],[(x,y,-.25)for x,y in ps],[tuple(range(len(ps)))],water)
# Low-poly fronds model a coconut crown with a visible stem and split leaflets.
def palm(x,y,h):
 lean=random.uniform(-1.1,1.1);rod('Palm tapered trunk base',(x,y,-.30),(x+lean*.5,y,h*.5),.20,trunk,10);rod('Palm tapered upper trunk',(x+lean*.5,y,h*.5),(x+lean,y,h),.14,trunk,10)
 for z in range(1,int(h)):rod('Palm bark ring',(x+lean*z/h,y,z),(x+lean*z/h,y,z+.04),.205 if z<h*.5 else .15,cream,10)
 for j in range(9):
  a=j*math.tau/9+random.random()*.2;cx,cy=x+lean,y
  pts=[(cx,cy,h),(cx+math.cos(a)*1.5,cy+math.sin(a)*1.5,h+.6),(cx+math.cos(a)*3.8,cy+math.sin(a)*3.8,h-.5)]
  for u,v in zip(pts,pts[1:]):rod('Palm frond rachis',u,v,.025,leaf,6)
  for k in range(1,11):
   t=k/11;xx=cx+math.cos(a)*3.8*t;yy=cy+math.sin(a)*3.8*t;zz=h+math.sin(t*math.pi)*.65-t*.5;w=.65*math.sin(t*math.pi)
   for sg in(-1,1):add('Palm paired leaflets',[(xx,yy,zz),(xx-math.sin(a)*w*sg-math.cos(a)*.25,yy+math.cos(a)*w*sg-math.sin(a)*.25,zz-.18),(xx+math.cos(a)*.30,yy+math.sin(a)*.30,zz-.06)],[(0,1,2)],leaf)
for k in range(50 if CODE=='QLN' else 28):
 x=random.uniform(-400,450);y=random.choice([-1,1])*random.uniform(60,115)
 if abs(x-bx)<bw/2+15 and abs(y-by)<bd/2+20:continue
 if railclear(x,y,6):palm(x,y,random.uniform(7,12))
# Deliberately sparse low roadside buildings establish scale, not copied station facades.
for k in range(8):
 x=-240+k*70;y=side*(100+(k%2)*18)
 if railclear(x,y,15):box('Distant context house',(x,y,2),(random.uniform(9,16),7,4),cream);box('Distant context flat roof',(x,y,4.15),(16,8,.22),concrete)
# Rail-side electrical/location cases, safe outside running envelopes.
for x in(-220,210):
 candidates=[(x,y)for y in(-50,45,65,-75)]
 for xx,yy in candidates:
  if railclear(xx,yy,3):
   box('Relay equipment concrete plinth',(xx,yy,.15),(1.8,.9,.40),concrete);box('Relay equipment case',(xx,yy,1.13),(1.5,.65,1.65),steel)
   for dx in(-.36,.36):box('Relay cabinet access door',(xx+dx,yy-.35,1.12),(.67,.05,1.52),cream);box('Relay cabinet latch',(xx+dx,yy-.39,1.07),(.045,.035,.15),dark)
   break
flush()

# --- NAMED CAMERAS, LIGHTING, PACKED FILE ---
col('90_CAMERAS_LIGHTS_AND_DOCUMENTATION')
da=bpy.data.lights.new('Sun late-morning Kerala','SUN');da.energy=2.3;da.angle=math.radians(8);sun=bpy.data.objects.new('Sun late-morning Kerala',da);current.objects.link(sun);sun.rotation_euler=(math.radians(24),math.radians(-32),math.radians(-25))
area('Wide sky fill',(0,0,180),(0,0,0),12000,160)
cameras=[]
def camera(n,p,target,lens=40,ortho=None):
 ca=bpy.data.cameras.new(n);ob=bpy.data.objects.new(n,ca);current.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens;ca.clip_end=15000
 if ortho:ca.type='ORTHO';ca.ortho_scale=ortho
 cameras.append(ob);return ob
maxextent=max(bbox[2]-bbox[0],(bbox[3]-bbox[1])*1.5);center=((bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2,0)
camera('01_FULL_MAPPED_LAYOUT',(center[0]-maxextent*.12,center[1]-maxextent*.60,maxextent*.65),center,ortho=maxextent*1.03)
# Station-scale overview remains legible even for very long industrial spur coverage.
camera('02_STATION_AND_PLATFORMS',(bx-110,by+side*170,125),(bx+40,by-side*12,1),ortho=360 if SP['kind']!='junction' else 650)
p0=D['platforms'][0];targetp=p0['center_xy'];px=max(bx+bw/2+25,targetp[0]+38);yy=widthat(p0,px);py=sum(yy)/2 if yy else targetp[1];camera('03_PLATFORM_TRACK_DETAILS',(px,py-1.4,F+2.20),(px-65,py-.6,F+1.55),lens=30)
camera('04_FACADE_AND_APPROACH',(bx-18,fronty+side*(max(35,bw*.65)),F+9),(bx,fronty,F+2.7),lens=38)
# Interior view lives inside waiting/booking room and sees counters, desk, lighting and joinery.
rx=bx-bw/2+roomw*.5;camera('05_TICKET_INTERIOR',(rx-roomw*.34,by+.4,F+1.95),(rx+.25,by+1.4,F+.85),lens=21 if SP['kind']=='halt' else 24)
for ob in cameras:ob['purpose']='Verified source-scene render camera';ob['station']=CODE
S.camera=cameras[1];S['station_code']=CODE;S['no_rolling_stock']=True;S['model_scale']='1 Blender unit = 1 metre';S['geometry_source']='OpenStreetMap contributors, retrieved2026-10-08; see source/adopted_geometry.json';S['uncertainty']='Hidden interiors reconstructed; photo-era facade dates and current redevelopment are distinguished in SOURCES_AND_UNCERTAINTIES.md';S['gauge_m']=1.676;S['platform_positions_reported']=str(D['reported_platform_positions']);S['platform_bodies_modelled']=len(D['platforms'])
textblock=bpy.data.texts.new('READ_ME_EVIDENCE_AND_DIMENSIONS');textblock.write(json.dumps({'code':CODE,'note':SP['notes'],'gauge_m':1.676,'metres':True,'no_trains':True,'platform_positions_reported':D['reported_platform_positions'],'platform_bodies':len(D['platforms']),'interiors':'Furnished reconstruction; not a measured interior survey','facade':'Photo-guided; date-specific evidence in accompanying source report','corrections':D['corrections']},indent=2))
# No external textures are used. Pack fonts and any incidental resources before saving.
bpy.ops.file.pack_all();S.render.engine='BLENDER_EEVEE_NEXT'
blend=R/f'{CODE}_coastal_station_v01.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
obs=[o for o in S.objects if o.type=='MESH'];verts=sum(len(o.data.vertices)for o in obs);polys=sum(len(o.data.polygons)for o in obs)
report={'station_code':CODE,'blend':blend.name,'generated_at_unix':time.time(),'builder_sha256':hashlib.sha256((R/'source/build_station_used.py').read_bytes()).hexdigest(),'source_adopted_sha256':hashlib.sha256((R/'source/adopted_geometry.json').read_bytes()).hexdigest(),'units':'metres','gauge_inside_faces_m':1.676,'veranda_depth_adopted_m':veranda_depth,'platform_top_m':F,'rail_top_m':.178,'platform_positions_reported':D['reported_platform_positions'],'physical_platform_bodies':len(D['platforms']),'track_routes':len(D['routes']),'track_route_total_length_m':sum(r['length_m']for r in D['routes']),'mapped_switch_nodes':len(D['switches']),'mapped_true_service_buffers':len(D['buffers']),'mesh_objects':len(obs),'total_objects':len(S.objects),'vertices':verts,'polygons':polys,'no_rolling_stock':True,'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'packed_resources':True,'cameras':[o.name for o in cameras],'platforms':[{'label':p['label'],'basis':p['basis'],'width_min_sample_m':p['sampled_usable_width_min_m'],'clearance_m':p['clearance_min_m']}for p in D['platforms']],'corrections':D['corrections'],'notes':SP['notes']}
(R/'BUILD_QA.json').write_text(json.dumps(report,indent=2));print('BUILD_COMPLETE',CODE,verts,polys,flush=True)
