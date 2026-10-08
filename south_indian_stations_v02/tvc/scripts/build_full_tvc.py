"""Rebuild full metre-scale TVC visual environment. Blender 4.3, no add-ons.
Current mapped railway geometry, 2022 heritage reference; unknown interiors reconstructed.
"""
import bpy,math,json,random,sys,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];random.seed(22022)
bpy.ops.wm.open_mainfile(filepath=str(R/'source/TVC_heritage_source.blend'))
S=bpy.context.scene
autocol=bpy.data.collections.new('00_TEMP_AUTOS');S.collection.children.link(autocol)
for ob in list(S.objects):
 if ob.name.startswith('Auto '):
  autocol.objects.link(ob)
  for cc in list(ob.users_collection):
   if cc!=autocol:cc.objects.unlink(ob)
for c in list(bpy.data.collections):
 if not c.name.startswith(('00_TEMP','01_','02_')):
  for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(c)
for o in list(bpy.data.objects):
 if 'recess' in o.name and o.type=='MESH' and max(v.co.z for v in o.data.vertices)<5:bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith('Pavilion rear'):
  h=o.dimensions.z;o.dimensions.z=h-4.5;o.location.z=(h+4.5)/2
S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
current=None;batch={};counts={};active_route=None
def col(n):
 global current
 flush();current=bpy.data.collections.new(n);S.collection.children.link(current);print('COLLECTION',n,flush=True);return current
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);current.objects.link(o)
 if m:me.materials.append(m)
 return o
def material(n,c,rough=.7,metal=0,noise=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  nd=m.node_tree.nodes;ln=m.node_tree.links;t=nd.new('ShaderNodeTexNoise');tc=nd.new('ShaderNodeTexCoord');ln.new(tc.outputs['Object'],t.inputs['Vector']);t.inputs['Scale'].default_value=noise;t.inputs['Detail'].default_value=3;cr=nd.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(*(v*.65 for v in c),1);cr.color_ramp.elements[1].color=(*(min(v*1.12,1) for v in c),1);ln.new(t.outputs['Fac'],cr.inputs[0]);ln.new(cr.outputs[0],p.inputs['Base Color']);b=nd.new('ShaderNodeBump');b.inputs['Strength'].default_value=.3;b.inputs['Distance'].default_value=.001 if 'leather' in n.lower() else (.002 if metal or 'terrazzo' in n.lower() else .007);ln.new(t.outputs['Fac'],b.inputs['Height']);ln.new(b.outputs[0],p.inputs['Normal'])
 return m
def emit(n,c,power):
 m=material(n,c);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=power;return m
cream=bpy.data.materials['Weathered ivory limework'];dark=bpy.data.materials['Iron and rubber'];stone=bpy.data.materials['Granite variation 03'];white=material('Chalky off-white limewash',(.71,.73,.68),noise=4)
plaster=material('Warm ochre lime plaster',(.64,.54,.34),noise=7);red=material('Oxide red skirting',(.32,.055,.033),noise=9);teal=material('Aged institutional teal',(.10,.26,.24),noise=12);wood=material('Varnished teak grain',(.25,.105,.035),noise=25)
steel=material('Galvanised metal patina',(.38,.43,.43),.36,.7,16);rail=material('Polished rail head',(.48,.49,.46),.23,.87);rust=material('Oxidised rail webs',(.24,.085,.035),.68,.4,20);ballast=material('Crushed grey granite aggregate',(.29,.27,.22),noise=85);concrete=material('Stained concrete sleepers',(.48,.47,.40),noise=28)
ballast_stones=[material('Ballast stone shade %d'%i,(.16+i*.045,.155+i*.042,.14+i*.035),noise=40) for i in range(4)]
nd=ballast.node_tree.nodes;ln=ballast.node_tree.links;voro=nd.new('ShaderNodeTexVoronoi');voro.feature='DISTANCE_TO_EDGE';voro.inputs['Scale'].default_value=28;tc=nd.new('ShaderNodeTexCoord');ln.new(tc.outputs['Object'],voro.inputs['Vector']);bump=nd.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.75;bump.inputs['Distance'].default_value=.045;ln.new(voro.outputs['Distance'],bump.inputs['Height']);ln.new(bump.outputs['Normal'],nd.get('Principled BSDF').inputs['Normal'])
roof=material('Weathered blue-grey sheet',(.13,.24,.29),.56,.3,15);roofalt=material('Roof repaired sheet',(.26,.32,.33),.55,.3,14);tile=material('Warm cream terrazzo',(.60,.56,.45),noise=70);tile2=material('Terrazzo shade variation',(.48,.44,.34),noise=70);tactile=material('Oxide tactile tiles',(.48,.22,.12),noise=35);yellow=material('Faded railway yellow',(.88,.53,.03),noise=14);glass=material('Smoky window glass',(.10,.22,.24),.18,.2);green=material('Tropical leaves',(.055,.19,.035),noise=8);soil=material('Earth and verge',(.24,.23,.13),noise=18);asphalt=material('Road asphalt',(.095,.11,.12),noise=60);paper=material('Aged paper',(.78,.74,.59),noise=25);lit=emit('Warm fluorescent diffuser',(.86,.91,.80),3);led=emit('Red LED coach display',(.9,.012,.004),2)
# Batch all repeated primitives by material. Every semantic collection remains editable mesh parts.
def add(n,v,f,m):
 key=(current.name,n,m.name if m else '')
 if key not in batch:batch[key]=[[],[],m]
 a,b,_=batch[key];i=len(a);a.extend(v);b.extend(tuple(i+k for k in face) for face in f);counts[n]=counts.get(n,0)+1

def flush():
 for (cn,n,mn),(v,f,m) in list(batch.items()):
  me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.data.collections[cn].objects.link(o)
  if m:me.materials.append(m)
  if cn=='10_TRACK_NETWORK_MAPPED_PROFILES' and active_route:o['route_id']=active_route
 batch.clear()
def box(n,p,d,m,a=0):
 x,y,z=[v/2 for v in d];cs=math.cos(a);sn=math.sin(a)
 v=[(p[0]+xx*cs-yy*sn,p[1]+xx*sn+yy*cs,p[2]+zz) for xx,yy,zz in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]]
 add(n,v,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],m)
def rod(n,a,b,r,m,N=8):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 else:u.normalize()
 v=d.cross(u);vs=[tuple(p+r*(u*math.cos(i*math.tau/N)+v*math.sin(i*math.tau/N))) for p in (a,b) for i in range(N)];fs=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];add(n,vs,fs,m)
def txt(n,s,p,h,m=dark,rot=0):
 cu=bpy.data.curves.new(n,'FONT');cu.body=s;cu.size=h;cu.align_x='CENTER';cu.extrude=.002;cu.materials.append(m);o=bpy.data.objects.new(n,cu);current.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,rot);return o
def sign(s,p,w=3,h=.65,m=teal,size=.23,rot=0):
 box('Sign enamel panel',p,(w,.07,h),m,rot);cs=math.cos(rot);sn=math.sin(rot);txt('Sign '+s,s,(p[0]+.05*sn,p[1]-.05*cs,p[2]-size*.35),size,white,rot)
def area(n,p,target,power,size):
 da=bpy.data.lights.new(n,'AREA');da.energy=power;da.shape='DISK';da.size=size;o=bpy.data.objects.new(n,da);current.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def bench(x,y,z=.85,n=4):
 box('Perforated seat support',(x,y,z+.34),(n*.55,.42,.09),steel)
 for i in range(n):
  xx=x+(i-(n-1)/2)*.55
  for k in range(5):box('Seat ventilation slats',(xx,y-.18+k*.09,z+.42),(.48,.055,.055),steel)
  for k in range(5):box('Seat back ventilation slats',(xx,y+.23,z+.61+k*.085),(.48,.045,.05),steel)
  for sg in (-1,1):rod('Seat armrest',(xx+sg*.24,y-.16,z+.63),(xx+sg*.24,y+.24,z+.7),.022,steel)
 for dx in (-n*.20,n*.20):box('Seat pedestal',(x+dx,y,z+.2),(.07,.30,.4),dark);box('Bench anchor plate',(x+dx,y,z+.03),(.26,.32,.06),steel)
def fan(x,y,z):
 rod('Ceiling fan suspension',(x,y,z+.65),(x,y,z),.022,dark);rod('Fan motor',(x,y,z-.06),(x,y,z+.08),.16,cream,16)
 for a in (0,math.tau/3,2*math.tau/3):box('Fan blade',(x+.41*math.cos(a),y+.41*math.sin(a),z),(.69,.13,.025),cream,a)
def light(x,y,z):
 box('Fluorescent casing',(x,y,z),(1.25,.16,.1),steel);box('Fluorescent diffuser',(x,y,z-.055),(1.15,.12,.022),lit)
def desk(x,y):
 box('Desk teak top',(x,y,1.64),(1.9,.78,.08),wood)
 for dx in (-.8,.8):box('Desk side pedestal',(x+dx,y,1.19),(.25,.66,.85),teal)
 box('Monitor base',(x,y+.12,1.73),(.35,.25,.05),dark);box('Monitor stem',(x,y+.20,1.93),(.05,.06,.38),dark);box('Monitor bezel',(x,y+.23,2.13),(.55,.08,.35),dark);box('Monitor green screen',(x,y+.18,2.13),(.48,.018,.28),glass);box('Keyboard',(x,y-.17,1.71),(.53,.17,.035),dark)
 for dx in (-.28,.28):
  for yy in (-.27,.27):rod('Office chair legs',(x+dx,y-.9+yy,.85),(x+dx,y-.9+yy,1.25),.025,steel)
 box('Chair cushion',(x,y-.9,1.26),(.62,.58,.09),teal);box('Chair back',(x,y-1.14,1.63),(.62,.09,.55),teal)
 for k in range(3):box('Paper forms',(x+.55,y-.07,1.715+k*.012),(.35,.25,.012),paper,.06*k)
def doorwall(n,x,y,w,h=4.2,opening=1.5):
 dh=min(2.8,h-.15)
 for sg in (-1,1):box(n+' wall pier',(x+sg*(opening/2+(w-opening)/4),y,.85+h/2),((w-opening)/2,.23,h),plaster)
 box(n+' door lintel',(x,y,.85+(dh+h)/2),(opening,.23,h-dh),plaster)
 for sg in (-1,1):box(n+' door jamb',(x+sg*(opening/2+.035),y-.14,.85+dh/2),(.10,.12,dh),wood)
 box(n+' door head',(x,y-.14,.85+dh),(opening+.2,.12,.12),wood)
 box(n+' door leaf open',(x-opening/2+.06,y+.58,.85+(dh-.1)/2),(.065,1.18,dh-.1),teal)
 rod(n+' lever handle',(x-opening/2-.025,y+1.04,2.10),(x-opening/2-.16,y+1.04,2.10),.015,steel)
def room(n,cx,cy,w,d):
 box(n+' floor',(cx,cy,.73),(w,d,.24),tile);box(n+' ceiling',(cx,cy,5.17),(w,d,.16),white)
 for xx in (cx-w/2,cx+w/2):box(n+' side wall',(xx,cy,3),(.24,d,4.3),plaster);box(n+' skirting',(xx,cy,1.02),(.28,d,.32),red)
 doorwall(n+' rear access',cx,cy+d/2,w);doorwall(n,cx,cy-d/2,w)
 for x in range(int(cx-w/2+2),int(cx+w/2),4):
  light(x,cy,5.02);fan(x,cy+1,4.38);area(n+' interior light',(x,cy,4.9),(x,cy,1),130,3)
 sign(n.upper(),(cx,cy-d/2-.15,4.25),min(w-1,4),.55,size=.22)
# Restore usable rear portals and match expanded station to mapped footprint.
col('03_HERITAGE_HALL_AND_EXTENDED_ARCADE_RECONSTRUCTED')
for x,w in [(0,14.4),(-24.05,6.5),(24.05,6.5)]:
 for sg in (-1,1):box('Rear hall portal pier',(x+sg*(w/4+1.4),7.7,2.25),(w/2-2.8,.55,4.5),stone)
 box('Rear hall portal lintel',(x,7.7,4.28),(5.6,.55,.45),cream)
box('Central entrance terrazzo',(0,7.5,.70),(13.5,15,.26),tile)
# Entry rises gently from street to platform level, no blocked doorway.
verts=[(-1.55,-10,.05),(1.55,-10,.05),(1.55,1,.85),(-1.55,1,.85),(-1.55,-10,-.10),(1.55,-10,-.10),(1.55,1,.60),(-1.55,1,.60)];add('Accessible entrance ramp',verts,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],tile)
for x in (-1.7,1.7):rod('Entrance ramp handrail',(x,-10,1),(x,1,1.8),.035,steel)
for x in (-5,5):bench(x,4,n=3)
sign('PLATFORMS 1 - 5  /  ENQUIRY',(0,7.30,3.75),5.2,.7,size=.26)
for x in (-4,4):fan(x,4,4.4);light(x,5,4.9);area('Heritage hall light',(x,4,4.7),(x,4,1),220,3)
# Back-concourse arcade is continuous and open onto platform 1.
box('Continuous heritage back concourse',(-9,11.3,.72),(135,7.2,.24),tile)
for x in range(-74,59,5):
 box('Arcade square column',(x,14.2,3),(.52,.52,4.3),white);box('Arcade column oxide plinth',(x,14.2,1.08),(.58,.58,.46),red);light(x,12,4.85)
box('Arcade ceiling',(-9,11.3,5.05),(136,7.5,.20),white)
for x in range(-75,61,2):box('Ceiling panel seam',(x,11.3,4.94),(.018,7.2,.018),steel)
for lo,hi in [(-77,-27.5),(27.5,59)]:
 w=hi-lo;cx=(hi+lo)/2
 box('Extended heritage wing roof',(cx,5.5,5.42),(w,12,.22),roof)
 for x in range(math.ceil(lo)+2,math.floor(hi),4):
  box('Extended granite facade pier',(x,0,2.3),(1.1,.5,4.6),stone);box('Pale lintel bands',(x,0,4.45),(4.0,.65,.3),cream)
  for z in [1.2,2.2,3.2]:box('Masonry corner dressing',(x,-.28,z),(1.15,.09,.15),cream)
  box('Wing room clerestory frame',(x,5.4,4.38),(2.8,.2,.85),wood);box('Wing room clerestory glass',(x,5.25,4.38),(2.65,.07,.72),glass)
# Public rooms off the covered rear circulation. Fully furnished, explicitly reconstructed.
col('04_FURNISHED_WAITING_LOUNGE_RECONSTRUCTED')
room('Waiting lounge',-48,5.6,23,10)
leather=material('Chocolate leather upholstery',(.055,.030,.023),.40,noise=85)
for x in (-55,-48,-41):
 for y in (3.8,7.5):
  box('Sofa upholstered base',(x,y,1.19),(3.0,.86,.36),leather)
  for j in range(3):
   xx=x+(j-1)*.91;box('Sofa seat cushion',(xx,y-.06,1.42),(.88,.74,.16),leather);box('Sofa back cushion',(xx,y+.37,1.80),(.89,.21,.67),leather)
   for sg in(-1,1):box('Sofa cushion seam',(xx+sg*.42,y-.075,1.507),(.008,.67,.009),wood)
  for sg in(-1,1):box('Sofa curved arm',(x+sg*1.51,y,1.59),(.19,.94,.43),leather)
  for xx in (x-1.22,x+1.22):
   for yy in(y-.28,y+.28):rod('Sofa chrome feet',(xx,yy,.85),(xx,yy,1.13),.034,steel,12)
  box('Lounge side table',(x+2.12,y,1.43),(.70,.75,.055),wood)
  for dx in(-.28,.28):rod('Lounge table legs',(x+2.12+dx,y,.85),(x+2.12+dx,y,1.40),.025,steel)
flush()
for ob in current.objects:
 if ob.name.startswith(('Sofa upholstered','Sofa seat','Sofa back','Sofa curved')):
  md=ob.modifiers.new('Soft upholstery edge radius','BEVEL');md.width=.055;md.segments=3
# Primary2017 Southern Railway waiting-hall photograph informs finishes, not dimensions.
cove=emit('Waiting-room blue cove glow',(.08,.42,1.0),2.5);wainscot=material('Waiting room taupe wainscot',(.46,.42,.35),.55)
for x in(-59.3,-36.7):
 box('AC lounge side wainscot',(x,5.6,1.70),(.065,9.5,1.68),wainscot);box('AC lounge brown wall band',(x,5.6,1.72),(.075,9.5,.32),wood);box('Waiting ceiling cove',(x+.1 if x< -48 else x-.1,5.6,4.98),(.20,9.4,.10),cove)
for y in(.95,10.23):box('Waiting ceiling cove',(-48,y,4.98),(22.5,.18,.10),cove)
box('Lounge wall television',(-48,10.27,3.65),(1.55,.14,.90),dark);box('TV screen',(-48,10.18,3.65),(1.40,.035,.75),glass);txt('TV passenger information','SOUTHERN RAILWAY',(-48,10.15,3.65),.12,white)
rod('TV power cable',(-48,10.20,3.2),(-48,10.20,2.75),.012,dark);box('TV receiver shelf',(-48,10.17,2.73),(.62,.3,.07),steel);box('Set top receiver',(-48,10.15,2.82),(.44,.20,.10),dark)

box('Lounge information board',(-48,10.42,3.25),(4,.12,1.3),teal)
txt('Passenger information','PASSENGER INFORMATION\nKeep your belongings with you\nDrinking water  >',(-48,10.33,3.45),.23,white)
box('Newspaper rack',(-58,6,1.45),(1.2,.35,1.2),wood)
for z in (1.3,1.65,1.95):box('Rack newspapers',(-58,5.80,z),(1.08,.09,.30),paper)
col('05_OFFICES_SERVICE_AND_TOILETS_RECONSTRUCTED')
room('Station office',41,5.6,15,10)
for x in (36,41,46):desk(x,7.5)
for x in (36,38):
 box('Office filing cabinet',(x,9.8,2.1),(1.3,.55,2.5),teal)
 for z in (1.1,1.6,2.1,2.6,3.1):box('File drawer',(x,9.48,z),(1.18,.07,.43),steel);box('Drawer pull',(x,9.40,z),(.3,.035,.03),dark)
sign('DUTY ROSTER',(45,10.43,3.4),3,1.1,size=.27)
room('Toilets',-68,5.6,15,10)
# Cubicles at rear; central accessible turning space and sinks by front wall.
for x in (-73,-70,-67,-64):
 box('Cubicle partition',(x-1.1,8.2,2.0),(.08,3.1,2.3),teal);doorwall('WC cubicle',x,6.6,2.2,h=2.5,opening=.85)
 rod('Toilet pedestal',(x,8.8,.9),(x,8.8,1.22),.21,white,16);box('Toilet bowl',(x,8.62,1.22),(.45,.65,.16),white);box('Toilet cistern',(x,9.28,1.62),(.48,.23,.54),white);rod('Flush pipe',(x,9.21,1.25),(x,9.21,1.58),.027,steel)
for x in (-73,-70,-67):
 box('Washbasin counter',(x,2.3,1.7),(1.5,.64,.12),white);rod('Washbasin bowl',(x,2.25,1.73),(x,2.25,1.8),.25,white,16);rod('Tap stem',(x,2.53,1.76),(x,2.53,2),.025,steel);rod('Tap spout',(x,2.53,2),(x,2.31,2),.025,steel);box('Washroom mirror',(x,.81,2.7),(1.3,.045,1.2),glass)
box('Toilet floor drain',(-68,4.4,.87),(.38,.38,.03),steel)
for k in range(7):box('Drain grate slot',(-68-.14+k*.045,4.4,.89),(.02,.3,.01),dark)
room('Staff pantry',54,5.6,9,10)
box('Pantry worktop',(55,9.7,1.7),(5,.6,.12),steel)
for x in (53,55,57):box('Pantry base cupboard',(x,9.7,1.26),(1.9,.6,.78),teal)
rod('Tea urn',(55,9.65,1.8),(55,9.65,2.6),.30,steel,20);box('Pantry refrigerator',(51,8,1.9),(.9,.75,2.1),white)
for k in range(6):rod('Tea cups',(53+k*.15,9.5,1.79),(53+k*.15,9.5,1.90),.05,white,12)
# A separate booking building north/west of heritage; complete counter workflow.
col('06_TICKET_BOOKING_HALL_RECONSTRUCTED')
room('Booking and reservation',113,3,46,20)
for i,x in enumerate(range(96,132,5)):
 box('Ticket counter base',(x,7,1.45),(4.8,.55,1.2),teal);box('Counter stone ledge',(x,6.92,2.03),(4.95,.90,.10),stone)
 for xx in (x-2.3,x+2.3):box('Ticket grille stile',(xx,7,2.9),(.07,.08,1.7),steel)
 for xx in [x-2.1+k*.23 for k in range(19)]:rod('Ticket grille bar',(xx,7,2.20),(xx,7,3.68),.009,steel)
 box('Ticket transaction opening frame',(x,6.92,2.42),(.70,.09,.055),steel);sign('%02d  TICKETS'%(i+1),(x,6.9,4.12),3.3,.65,size=.24);desk(x,9)
 for yy in (-3,-1,1,3,5):
  rod('Queue railing post',(x-1.3,yy,.85),(x-1.3,yy,1.85),.028,steel)
 for xx in (x-1.3,x+1.3):
  rod('Queue guide rail',(xx,-3,1.75),(xx,5.4,1.75),.025,steel)
  for yy in (-3,5.4):
   rod('Queue terminal upright',(xx,yy,.85),(xx,yy,1.80),.032,steel);rod('Queue terminal cap',(xx,yy,1.78),(xx,yy,1.82),.042,steel,12);box('Queue terminal baseplate',(xx,yy,.87),(.17,.17,.04),steel)
for x in (99,107,119,127):bench(x,-4,n=5)
box('Token dispenser',(113,-4,1.52),(.55,.48,1.35),teal);box('Token dispenser screen',(113,-4.26,1.91),(.42,.035,.26),glass)
sign('TOKEN 048   COUNTER 03',(113,7,4.85),7,.60,size=.34)
# Use separate collection for lift-off ceiling visual review.
flush()
D=json.loads((R/'source/mapped_geometry.json').read_text());ways=D['ways'];rails=[w for w in ways if w['tags'].get('railway')=='rail'];platforms=[w for w in ways if w['tags'].get('railway')=='platform']
# Graph uses every internal node too, so branch endpoints cannot become false buffers.
adj={};nodepos={}
for w in rails:
 for nd,p in zip(w['nodes'],w['xy']):nodepos[nd]=p
 for a,b in zip(w['nodes'],w['nodes'][1:]):adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)

def pathmesh(n,pts,profile,m):
 vs=[];L=len(profile)
 for i,p in enumerate(pts):
  d=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)]);d.normalize();nx=-d.y;ny=d.x
  for off,z in profile:vs.append((p[0]+nx*off,p[1]+ny*off,z))
 fs=[]
 for i in range(len(pts)-1):
  for j in range(L):fs.append((i*L+j,i*L+(j+1)%L,(i+1)*L+(j+1)%L,(i+1)*L+j))
 fs.extend([tuple(reversed(range(L))),tuple(range((len(pts)-1)*L,len(pts)*L))]);return mesh(n,vs,fs,m)
def samples(pts,step):
 rem=0
 for a,b in zip(pts,pts[1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy)
  if ll<1e-6:continue
  angle=math.atan2(dy,dx)
  while rem<ll:
   yield (a[0]+dx*rem/ll,a[1]+dy*rem/ll,angle)
   rem+=step
  rem-=ll

def clippts(pts,xlim=820):
 # Keep real route scale; a bounded segment of mainline is deliberately cropped.
 out=[]
 for a,b in zip(pts,pts[1:]):
  if min(a[0],b[0])>xlim or max(a[0],b[0])<-xlim:continue
  aa=list(a);bb=list(b)
  for p,q in ((aa,bb),(bb,aa)):
   if abs(p[0])>xlim:
    xx=math.copysign(xlim,p[0]);t=(xx-p[0])/(q[0]-p[0]);p[1]+=t*(q[1]-p[1]);p[0]=xx
  if not out or math.dist(out[-1],aa)>.01:out.append(aa)
  out.append(bb)
 return out
# Precompute switch influence and clearance helpers from the complete map graph.
allsegments=[(Vector(a),Vector(b)) for w in rails for a,b in zip(w['xy'],w['xy'][1:])]
def railclear(p,clearance=1.95):
 p=Vector(p)
 for a,b in allsegments:
  v=b-a;t=max(0,min(1,(p-a).dot(v)/max(v.length_squared,1e-12)))
  if (p-a-v*t).length<clearance:return False
 return True
def safe_service_xy(x,y,clearance=2.25):
 if railclear((x,y),clearance):return x,y
 for i in range(1,81):
  off=i*.5
  for q in((x,y-off),(x,y+off),(x-off,y),(x+off,y)):
   if railclear(q,clearance):return q
 raise RuntimeError('No rail-clear service placement found')
switchzones=[]
for nd,neighbours in adj.items():
 if len(neighbours)<3:continue
 p=Vector(nodepos[nd]);vv=[(Vector(nodepos[n])-p).normalized() for n in neighbours];_,ii,jj=max((vv[i].dot(vv[j]),i,j) for i in range(len(vv)) for j in range(i+1,len(vv)));d=(vv[ii]+vv[jj]).normalized();switchzones.append((p,d,Vector((-d.y,d.x))))
# One shared timber grid per crossing corridor prevents double bearer arrays.
woodgrid={};woodrails={}
for gi in range(-1333,1334):
 x=gi*.6;points=[]
 for aa,bb in allsegments:
  if min(aa.x,bb.x)<=x<=max(aa.x,bb.x) and abs(bb.x-aa.x)>.001:
   y=aa.y+(bb.y-aa.y)*(x-aa.x)/(bb.x-aa.x);p=Vector((x,y))
   if any(-4<(p-q).dot(d)<34 and abs((p-q).dot(n))<3.35 for q,d,n in switchzones):points.append((y,math.atan2(bb.y-aa.y,bb.x-aa.x)))
 points.sort();unique=[]
 for y,a in points:
  if not unique or abs(y-unique[-1][0])>.03:unique.append((y,a))
 intervals=[]
 for y,a in unique:
  lo=y-1.45;hi=y+1.45
  if intervals and lo<=intervals[-1][1]+.08:intervals[-1][1]=max(hi,intervals[-1][1])
  else:intervals.append([lo,hi])
 if intervals:woodgrid[gi]=intervals;woodrails[gi]=unique
def switchbearer(x,y):return any(lo+.4<y<hi-.4 for lo,hi in woodgrid.get(round(x/.6),[]))
# Spatially filter real ballast stones against every sleeper/bearer and running
# rail/flangeway footprint, including neighboring routes at points and crossings.
scatter_obstacles={}
def scatter_block(x,y,a,hx,hy):
 cs=math.cos(a);sn=math.sin(a);hx+=.035;hy+=.035;ex=abs(cs)*hx+abs(sn)*hy;ey=abs(sn)*hx+abs(cs)*hy;item=(x,y,cs,sn,hx,hy)
 for ix in range(math.floor(x-ex),math.floor(x+ex)+1):
  for iy in range(math.floor(y-ey),math.floor(y+ey)+1):scatter_obstacles.setdefault((ix,iy),[]).append(item)
def scatter_clear(x,y):
 for cx,cy,cs,sn,hx,hy in scatter_obstacles.get((math.floor(x),math.floor(y)),[]):
  dx=x-cx;dy=y-cy
  if abs(dx*cs+dy*sn)<=hx and abs(-dx*sn+dy*cs)<=hy:return False
 return True
for gi,intervals in woodgrid.items():
 for lo,hi in intervals:scatter_block(gi*.6,(lo+hi)/2,0,.145,(hi-lo)/2)
for ww in rails:
 pp=clippts(ww['xy'])
 if len(pp)<2:continue
 for xx,yy,aa in samples(pp,.60):
  if not switchbearer(xx,yy):scatter_block(xx,yy,aa,.12,1.375)
 for xx,yy,aa in samples(pp,.70):
  for ss in(-1,1):scatter_block(xx-math.sin(aa)*ss*.872,yy+math.cos(aa)*ss*.872,aa,.50,.16)
col('10_TRACK_NETWORK_MAPPED_PROFILES')
route_lengths={};route_paths={}
for wi,w in enumerate(rails):
 pts=clippts(w['xy'])
 if len(pts)<2:continue
 active_route=w['id']
 tag=w['tags'];label=tag.get('service',tag.get('usage','rail'));wid=w['id'];route_paths[wid]=pts;route_lengths[wid]=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
 for x,y,a in samples(pts,.60):
  if switchbearer(x,y):continue
  box('Precast PSC sleepers',(x,y,-.09),(.24,2.75,.16),concrete,a)
  nx=-math.sin(a);ny=math.cos(a)
  for sg in (-1,1):
   xx=x+nx*sg*.872;yy=y+ny*sg*.872
   box('Elastic rail pad',(xx,yy,.005),(.23,.18,.025),dark,a)
   for sd in (-1,1):
    xxx=xx+nx*sd*.115;yyy=yy+ny*sd*.115
    box('Rail clip and shoulder',(xxx,yyy,.032),(.13,.055,.046),rust,a)
 for x,y,a in samples(pts,4):
  for k in range(80):
   off=random.uniform(-1.73,1.73);t=random.uniform(-2,2);xx=x-math.sin(a)*off+t*math.cos(a);yy=y+math.cos(a)*off+t*math.sin(a)
   if not scatter_clear(xx,yy):continue
   rx=random.uniform(.015,.030);ry=random.uniform(.015,.030);ang=random.random()*math.tau;cs=math.cos(ang);sn=math.sin(ang)
   vv=[(xx,yy,random.uniform(-.055,-.025)),(xx,yy,-.09)]+[(xx+dx*cs-dy*sn,yy+dx*sn+dy*cs,-.065) for dx,dy in [(rx,0),(0,ry),(-rx,0),(0,-ry)]]
   ff=[(0,2+i,2+(i+1)%4) for i in range(4)]+[(1,2+(i+1)%4,2+i) for i in range(4)];add('Individual angular ballast stones',vv,ff,ballast_stones[k%4])
 flush()
# Physically identifiable switch components at each mapped junction.
col('11_TURNOUTS_CHECKRAILS_DRIVES_AND_BUFFERS')
turnouts=[];buffers=[]
for nd,neighbours in adj.items():
 x,y=nodepos[nd]
 if abs(x)>790:continue
 if len(neighbours)>=3:
  vectors=[]
  for nb in neighbours:
   p=nodepos[nb];d=Vector((p[0]-x,p[1]-y));d.normalize();vectors.append(d)
  # Pair of closest outgoing directions is main vs divergent branch.
  pairs=[(vectors[i].dot(vectors[j]),i,j) for i in range(len(vectors)) for j in range(i+1,len(vectors))];_,i,j=max(pairs);d=(vectors[i]+vectors[j]).normalized();a=math.atan2(d.y,d.x);n=Vector((-d.y,d.x));turnouts.append(nd)
  p=Vector((x,y))+n*2.25+d*2
  candidates=[Vector((x,y))+n*sg*off+d*along for off in (2.5,3.5,4.5,5.5) for sg in (-1,1) for along in (2,5,9)]
  p=next((q for q in candidates if railclear(q,1.95)),p)
  box('Point machine housing',(*p,.16),(1.05,.62,.35),steel,a);box('Point machine lid',(*p,.36),(1.12,.67,.055),dark,a)
  rod('Switch stretcher rod',(x+n.x*2.2,y+n.y*2.2,.04),(x-n.x*.85,y-n.y*.85,.04),.025,steel)
  for k in range(5):box('Point machine bolt',(p.x+(k%3)*.2-.2,p.y+(k//3)*.25-.12,.405),(.045,.045,.025),steel,a)
 elif len(neighbours)==1 and abs(x)<650:
  # True dead end only; boundary crop is not buffered.
  nb=next(iter(neighbours));p=nodepos[nb];a=math.atan2(y-p[1],x-p[0]);nx=-math.sin(a);ny=math.cos(a);dx=math.cos(a);dy=math.sin(a);buffers.append(nd)
  for sg in (-1,1):rod('Buffer stop diagonal',(x-dx*1.4+nx*sg*.8,y-dy*1.4+ny*sg*.8,.12),(x+nx*sg*.8,y+ny*sg*.8,1.15),.09,rust)
  box('Red buffer beam',(x,y,1.05),(.25,2.6,.35),red,a)
  for sg in (-1,1):box('Buffer white marker',(x+nx*sg*.65+dx*.15,y+ny*sg*.65+dy*.15,1.05),(.025,.35,.23),white,a)
for gi,intervals in woodgrid.items():
 x=gi*.6
 for lo,hi in intervals:box('Single aligned turnout timber bearers',(x,(lo+hi)/2,-.10),(.29,hi-lo,.17),wood)
 for y,a in woodrails[gi]:
  for sg in(-1,1):
   yy=y+sg*.872/max(abs(math.cos(a)),.7);box('Turnout elastic rail pad',(x,yy,.005),(.23,.18,.025),dark,a)
   for sd in(-1,1):
    box('Turnout rail clips',(x,yy+sd*.115,.032),(.13,.055,.046),rust,a);rod('Turnout clip bolts',(x,yy+sd*.115,.051),(x,yy+sd*.115,.075),.023,steel,6)
exec(compile((R/'scripts/load_running_rails.py').read_text(),str(R/'scripts/load_running_rails.py'),'exec'))
# Modelled tracks remain geographic paths. Detailed component placements reconstructed.
col('12_MAPPED_PLATFORMS_AND_EDGES')
for w in platforms:
 pts=w['xy'][:-1]
 if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0:pts=list(reversed(pts))
 n=len(pts);vs=[(x,y,z) for z in (-.24,.85) for x,y in pts];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];o=mesh('Mapped platform '+w['tags'].get('ref','1'),vs,fs,tile);o['osm_way']=w['id'];o['xy_status']='OSM mapped outline; vertical reconstruction'
 for a,b in zip(pts,pts[1:]+pts[:1]):
  length=math.dist(a,b)
  if w['id']=='921797273' and (a[1]+b[1])/2<19:continue
  if length<3:continue
  d=Vector(b)-Vector(a);d.normalize();aa=math.atan2(d.y,d.x)
  for x,y,ang in samples([a,b],.6):
   box('White coping stone',(x,y,.88),(.58,.40,.10),cream,ang)
   # Polygon interior is on right for mapped clockwise boundary; find inward via centre.
   cx=sum(p[0] for p in pts)/n;cy=sum(p[1] for p in pts)/n;nv=Vector((-d.y,d.x))
   if nv.dot(Vector((cx-x,cy-y)))<0:nv=-nv
   box('Platform edge tactile strip',(x+nv.x*.45,y+nv.y*.45,.87),(.58,.42,.06),tactile,ang)
   for k in (-.15,-.075,0,.075,.15):box('Tactile ridges',(x+nv.x*(.45+k),y+nv.y*(.45+k),.909),(.52,.016,.017),cream,ang)
# Long shelter spans fit broad part of mapped platforms, preserve real full lengths.
col('13_PLATFORM_SHELTERS_AND_PASSENGER_DETAILS')
def canopy(lo,hi,y,w,label):
 for x in range(lo,hi,8):
  if -119<x<-90 or 163<x<193:continue
  for sg in (-1,1):box('Canopy built-up flange',(x+sg*.14,y,3.2),(.08,.32,4.6),steel)
  box('Canopy column web',(x,y,3.2),(.30,.055,4.6),steel);box('Canopy column plinth',(x,y,1.01),(.6,.6,.32),concrete)
  for sg in (-1,1):
   rod('Canopy principal rafter',(x,y,5.95),(x,y+sg*w/2,5.20),.085,steel)
   rod('Canopy lower chord',(x,y,5.05),(x,y+sg*w/2,4.90),.055,steel)
   rod('Canopy knee brace',(x,y,3.8),(x,y+sg*w*.36,5.0),.055,steel)
   for k in range(4):
    yy=y+sg*k*w/8;zz=5.95-k*.75/4;rod('Canopy web bracing',(x,yy,zz),(x,yy+sg*w/8,4.98),.023,steel)
  for dx in (-.2,.2):
   for z in (1.15,4.5):rod('Canopy bolts',(x+dx,y-.18,z),(x+dx,y-.24,z),.032,dark,6)
  light(x,y-1.25,5.18)
  if x%16==0:fan(x,y+1.2,4.60)
 for sg in (-1,1):
  
  intervals=[(lo-1,-119),(-90,163),(193,hi+1)]
  for aa,bb in intervals:
   aa=max(aa,lo-1);bb=min(bb,hi+1)
   if bb<=aa:continue
   v=[(aa,y,5.98),(bb,y,5.98),(bb,y+sg*(w/2+.25),5.19),(aa,y+sg*(w/2+.25),5.19)]
   if sg<0:v.reverse()
   add('Shelter roof planes',v,[(0,1,2,3)],roof)
  for xx in [lo+i*.4 for i in range(int((hi-lo)/.4)) if not (-119<lo+i*.4<-90 or 163<lo+i*.4<193)]:rod('Corrugated sheet ribs',(xx,y,5.99),(xx,y+sg*(w/2+.25),5.20),.018,roof,6)
  rod('Shelter gutter',(lo,y+sg*(w/2+.25),5.17),(hi,y+sg*(w/2+.25),5.17),.07,steel)
  for k in range(4):
   yy=y+sg*k*w/8;zz=5.92-k*.75/4;
   for aa,bb in intervals:
    aa=max(aa,lo);bb=min(bb,hi)
    if bb>aa:box('Longitudinal roof purlin',((aa+bb)/2,yy,zz),(bb-aa,.09,.12),steel)
 for x in range(max(lo+30,-175),hi-18,28):
  if -122<x<-87 or 160<x<196:continue
  bench(x,y+1.5,n=4);bench(x+3,y+1.5,n=4)
  for sg in (-1,1):
   box('Waste segregation bin',(x+7,y+sg*.45,1.27),(.48,.45,.82),teal if sg==1 else roof);box('Bin lid',(x+7,y+sg*.45,1.72),(.52,.49,.10),dark)
  sign(label,(x,y,4.25),2.4,.55,size=.27)
  box('Coach indicator cabinet',(x,y-2.2,4.65),(1.15,.20,.42),dark);txt('Coach display','S %02d'%((x-lo)//28+1),(x,y-2.32,4.54),.23,led)
 for x in range(max(lo+40,-170),hi-20,90):
  if -122<x<-87 or 160<x<196:continue
  box('Water cooler',(x,y,1.47),(1.3,.85,1.2),steel);box('Cooler basin',(x,y-.47,1.2),(1.3,.22,.13),steel)
  for dx in (-.35,.35):rod('Drinking water tap',(x+dx,y-.46,1.57),(x+dx,y-.61,1.57),.025,steel)
  sign('DRINKING WATER',(x,y,2.75),2.4,.50,size=.18)
canopy(-255,195,18.6,9,'PLATFORM 1')
canopy(-225,215,40.4,7.0,'PLATFORMS 2 / 3')
canopy(-205,245,60,7.4,'PLATFORMS 4 / 5')
# Small retail rooms with stock rather than solid blank blocks.
for x,y in [(-155,18.8),(55,40.3),(-45,60),(140,18.8)]:
 box('Kiosk back',(x,y+1.0,2.1),(4,.10,2.5),teal)
 for dx in (-2,2):box('Kiosk side',(x+dx,y,2.1),(.1,2,2.5),teal)
 box('Kiosk roof',(x,y,3.43),(4.3,2.3,.15),roof);box('Kiosk counter',(x,y-.85,1.8),(4,.5,.18),wood)
 for z in (1.4,2.0,2.65):
  box('Kiosk stock shelf',(x,y+.6,z),(3.8,.65,.07),wood)
  for i in range(14):
   xx=x-1.6+i*.25;rod('Bottled water',(xx,y+.54,z+.04),(xx,y+.54,z+.35),.055,glass,8);rod('Bottle cap',(xx,y+.54,z+.35),(xx,y+.54,z+.40),.028,teal)
 sign('TEA  /  SNACKS',(x,y-1.07,3),3.8,.55,size=.25)
col('14_FOOTBRIDGES_STAIRS_AND_GROUND_RAMPS_RECONSTRUCTED')
for bx in (-105,178):
 box('FOB deck',(bx,43,7.35),(4.2,62,.28),concrete)
 for sg in (-1,1):
  x=bx+sg*2.1
  for y in range(12,75,3):
   if (sg==1 if bx<0 else sg==-1) and any(abs(y-yy)<2.5 for yy in (18.6,40.4,60)):continue
   rod('FOB upright',(x,y,7.35),(x,y,10),.075,steel);rod('FOB diagonal truss',(x,y,7.6),(x,y+3,9.8),.055,steel)
   for yy in [y+k*.18 for k in range(17) if not ((sg==1 if bx<0 else sg==-1) and any(abs(y+k*.18-zz)<1.5 for zz in (18.6,40.4,60)))]:rod('Bridge safety grille',(x,yy,7.7),(x,yy,9.5),.009,steel,6)
  rod('FOB top chord',(x,12,9.8),(x,74,9.8),.09,steel)
  if (sg==1 if bx<0 else sg==-1):
   for ya,yb in [(12,17.1),(20.1,38.9),(41.9,58.5),(61.5,74)]:rod('FOB lower chord with landing openings',(x,ya,7.55),(x,yb,7.55),.09,steel)
  else:rod('FOB lower chord',(x,12,7.55),(x,74,7.55),.09,steel)
 box('FOB blue sheet roof',(bx,43,10.13),(4.7,63,.18),roof)
 for y in (18.6,40.4,60):
  # Broad straight 38-step flights beside the platform centre, land directly on deck.
  direction=1 if bx<0 else -1
  for k in range(38):
   x=bx+direction*(2.1+(38-k)*.30);top=.85+(k+1)*6.64/38
   box('FOB individual stair tread',(x,y,top-.07),(.32,2.4,.14),concrete);box('Stair nosing',(x-direction*.14,y,top+.01),(.045,2.42,.025),yellow)
  low=(bx+direction*13.8,y,.85);high=(bx+direction*2.2,y,7.49)
  for sg in (-1,1):
   rod('Stair stringer',(low[0],y+sg*1.2,.73),(high[0],y+sg*1.2,7.36),.11,steel)
   rod('Stair handrail',(low[0],y+sg*1.2,1.9),(high[0],y+sg*1.2,8.54),.036,steel)
   for k in range(12):
    t=k/11;x=low[0]*(1-t)+high[0]*t;z=.85+t*6.64;rod('Stair baluster',(x,y+sg*1.2,z),(x,y+sg*1.2,z+1.05),.023,steel)
  box('FOB landing',(bx+direction*2.05,y,7.39),(.55,2.5,.2),concrete)
 for y in (18.6,40.4,60):
  for dx in (-1.55,1.55):box('Footbridge support pier',(bx+dx,y,3.6),(.35,.4,7.2),steel)
# Platform-end service ramp, gentle slope with integral kerb.
for x,y,direction in [(-271,18,1),(-266,39,1),(-226,55,1)]:
 add('Platform end service ramp',[(x-8,y-1,-.05),(x-8,y+1,-.05),(x,y+1,.85),(x,y-1,.85)],[(3,2,1,0)],concrete)
col('15_OHE_PORTALS_SIGNALS_AND_CABLES_RECONSTRUCTED')
for x in range(-790,791,45):
 ys=[]
 for w in rails:
  if w['tags'].get('electrified')!='contact_line':continue
  for a,b in zip(w['xy'],w['xy'][1:]):
   if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>.001:
    ys.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
 if not ys:continue
 ymin=min(ys)-3.8;ymax=max(ys)+3.8
 while not railclear((x,ymin),2.9):ymin-=.5
 while not railclear((x,ymax),2.9):ymax+=.5
 candidates=[ymin,ymax]+[y for y in (18.6,40.4,60) if ymin<y<ymax]
 for y in candidates:
  if not railclear((x,y),2.9):continue
  for dx in (-.25,.25):rod('Lattice OHE mast chord',(x+dx,y,-.1),(x+dx,y,8.2),.055,steel)
  for k in range(10):rod('Lattice mast bracing',(x-.25,y,k*.8),(x+.25,y,(k+1)*.8),.027,steel)
  box('OHE mast concrete footing',(x,y,.15),(1,1,.65),concrete)
 for z in (7.7,8.25):rod('OHE portal crossbeam',(x,ymin,z),(x,ymax,z),.072,steel)
 for k in range(math.ceil((ymax-ymin)/3)):
  ya=ymin+k*3;yb=min(ya+3,ymax);rod('OHE portal zigzag',(x,ya,7.7),(x,yb,8.25),.030,steel)
 for y in ys:
  rod('Contact wire suspension',(x,y,7.7),(x,y,5.9),.018,dark)
  for z in (6.9,7.0,7.1,7.2):rod('Porcelain insulator',(x,y,z),(x,y,z+.05),.12,cream,10)
# Catenary follows mapped electrified tracks including their curves, not a parallel straight substitute.
for w in rails:
 if w['tags'].get('electrified')!='contact_line':continue
 pts=route_paths.get(w['id'],[])
 for a,b in zip(pts,pts[1:]):
  rod('Contact copper wire',(*a,5.8),(*b,5.8),.011,rust,6);rod('Messenger wire',(*a,6.55),(*b,6.55),.014,dark,6)
 for x,y,a in samples(pts,9):rod('Catenary dropper',(x,y,5.8),(x,y,6.55),.009,dark,6)
for x,y,sg in [(-325,28,1),(-310,46,1),(-295,68,1),(340,29,-1),(353,49,-1),(365,70,-1),(-450,36,1),(475,36,-1)]:
 x,y=safe_service_xy(x,y,2.4)
 rod('Colour light signal post',(x,y,.1),(x,y,4.8),.09,steel);box('Signal black head',(x,y,4.6),(.40,.28,1.35),dark)
 for i,m in enumerate((red,yellow,green)):
  rod('Signal lens',(x,y-.15,4.16+i*.43),(x,y-.22,4.16+i*.43),.115,m,16);box('Signal hood',(x,y-.25,4.32+i*.43),(.32,.36,.055),dark)
 for z in [k*.28 for k in range(16)]:rod('Signal ladder rung',(x-.19,y+.25,z),(x+.19,y+.25,z),.018,steel)
 for xx in (x-.19,x+.19):rod('Signal ladder rail',(xx,y+.25,.1),(xx,y+.25,4.6),.018,steel)
 box('Signal cabinet',(x+1,y,1.0),(.6,.5,1.5),steel)
for x in range(-760,761,2):
 ys=[]
 for aa,bb in allsegments:
  if min(aa.x,bb.x)<=x<=max(aa.x,bb.x) and abs(bb.x-aa.x)>.001:ys.append(aa.y+(bb.y-aa.y)*(x-aa.x)/(bb.x-aa.x))
 if not ys:continue
 for y0,sg in [(min(ys)-3.3,-1),(max(ys)+3.3,1)]:
  y=y0
  while not all(railclear((x+dx,y),2.0) for dx in(-1.05,0,1.05)):y+=sg*.4
  box('Rail-clear perimeter cable trough',(x,y,-.15),(1.94,.38,.25),concrete);box('Cable trough lid',(x,y,-.007),(1.93,.43,.04),cream)
  if x%30==0:box('Cable junction marker',(x,y,.25),(.20,.20,.50),yellow)
# Open drains, sumps and visible water pipes alongside platforms and maintenance roads.
col('16_DRAINAGE_WATERING_AND_COACHING_INFRASTRUCTURE')
for y in (26,46.6,66.7,114,138):
 for yy in (y-.24,y+.24):box('Open drain concrete wall',(0,yy,-.30),(1030,.12,.36),concrete)
 box('Open drain dark channel',(0,y,-.36),(1030,.38,.035),dark)
 for x in range(-500,501,32):
  box('Drain catchpit',(x,y,-.18),(1,.7,.45),dark)
  for k in range(8):box('Catchpit iron grating',(x-.42+k*.12,y,-.07),(.045,.75,.035),steel)
exec(compile((R/'scripts/add_railside_services.py').read_text(),str(R/'scripts/add_railside_services.py'),'exec'))
for x,y in [(350,120),(-250,130),(-300,145)]:
 box('Depot service workshop floor',(x,y,.0),(25,12,.25),concrete)
 for dx in (-12,12):box('Workshop wall',(x+dx,y,2.6),(.25,12,5.2),plaster)
 box('Workshop back wall',(x,y+6,2.6),(25,.25,5.2),plaster);box('Workshop sheet roof',(x,y,5.3),(27,13,.16),roof)
 for dx in (-8,-3,3,8):
  box('Tool cabinet',(x+dx,y+4,1.1),(2,.7,2),teal);box('Workshop bench',(x+dx,y+2,1.1),(3,.7,.1),wood)
  for k in range(5):box('Workshop supply crate',(x+dx,y+4,2.2+k*.18),(.8,.55,.16),wood)
 sign('CARRIAGE & WAGON  /  MAINTENANCE',(x,y-6,4.1),20,.8,size=.42)
col('17_FORECOURT_BOUNDARIES_AND_URBAN_CONTEXT')
box('Station landscape base',(0,60,-.58),(1660,410,.45),soil)
box('Forecourt paved apron',(-7,-14,-.04),(315,27,.16),tile)
box('Frontage carriageway',(-5,-38,-.11),(810,15,.2),asphalt)
for x in range(-400,401):box('Black and white roadside kerb',(x,-30.8,.06),(.98,.25,.30),white if x%2 else dark)
for x in range(-395,396,5):box('Road centre dash',(x,-38,.006),(2.5,.13,.012),white)
for x in range(-135,150,4):
 if -4<x<4 or (x<117 and x+4>109):continue
 rod('Forecourt fence post',(x,-8,.1),(x,-8,1.12),.028,dark)
 for z in (.48,1.03):rod('Forecourt railing',(x,-8,z),(x+4,-8,z),.023,dark)
for x in (-135,-100,-80,-40,40,80,145):
 rod('Forecourt lamp post',(x,-25,0),(x,-25,6),.065,steel);box('Street lamp',(x,-25,6),(1.1,.35,.18),lit)
# A curving boundary follows service district without crossing sidings.
for x in range(-540,561,3):
 y=225 if x<180 else 140
 box('Railway boundary wall',(x,y,1.1),(2.97,.25,2.2),plaster);box('Boundary wall coping',(x,y,2.24),(3.02,.33,.12),concrete)
# Palm crowns are individual fronds in geometry.
def palm(x,y,h):
 x,y=safe_service_xy(x,y,5.0)
 rod('Coconut palm trunk',(x,y,0),(x+.6,y,h),.18,wood,10)
 for k in range(12):
  a=k*math.tau/12;ex=x+.6+math.cos(a)*3.1;ey=y+math.sin(a)*3.1;ez=h-.7
  rod('Palm frond midrib',(x+.6,y,h),(ex,ey,ez),.028,green,6)
  for j in range(9):
   t=j/9;cx=x+.6+math.cos(a)*3.1*t;cy=y+math.sin(a)*3.1*t;zz=h-.7*t
   for sg in (-1,1):
    dx=-math.sin(a)*sg*.5*(1-t);dy=math.cos(a)*sg*.5*(1-t)
    add('Palm leaflets',[(cx,cy,zz),(cx+dx,cy+dy,zz-.20),(cx+math.cos(a)*.22,cy+math.sin(a)*.22,zz-.02)],[(0,1,2)],green)
for x,y in [(-150,-21),(-85,-22),(-33,-22),(34,-23),(73,-23),(153,-21),(230,128),(275,128),(-235,208),(-300,175),(-460,130),(400,124),(485,90)]:palm(x,y,random.uniform(7,10))
# Select nearby real mapped building footprints only, and keep secondary city detail subdued.
for w in ways:
 t=w['tags'];p=w['xy']
 if not t.get('building') or w['id']=='478308341' or len(p)<4:continue
 cx=sum(q[0] for q in p)/len(p);cy=sum(q[1] for q in p)/len(p)
 if abs(cx)>620 or cy<-110 or cy>270 or (-300<cx<320 and -30<cy<220):continue
 if p[0]==p[-1]:p=p[:-1]
 if sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))<0:p=list(reversed(p))
 n=len(p);h=min(float(t.get('building:levels','2'))*3.1,22) if t.get('building:levels','2').replace('.','').isdigit() else 6.2
 vs=[(x,y,z) for z in (-.1,h) for x,y in p];fs=[tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh('Mapped urban mass '+w['id'],vs,fs,plaster if int(w['id'])%2 else white)
 for a,b in zip(p,p[1:]+p[:1]):
  ll=math.dist(a,b)
  if ll<4:continue
  angle=math.atan2(b[1]-a[1],b[0]-a[0]);nx=math.sin(angle);ny=-math.cos(angle)
  for xx,yy,ang in samples([a,b],3.0):
   for z in range(2,int(h),3):box('Context building windows',(xx+nx*.05,yy+ny*.05,z),(1.0,.10,1.2),glass,angle)
# Save build before optional expensive rendering or exchange operations.
exec(compile((R/'scripts/add_rich_details.py').read_text(),str(R/'scripts/add_rich_details.py'),'exec'))
exec(compile((R/'scripts/finish_entry_access.py').read_text(),str(R/'scripts/finish_entry_access.py'),'exec'))
col('09_EDITABLE_MAPPED_ROUTE_GUIDES')
current.hide_render=True;current.hide_viewport=True
for wid,pts in route_paths.items():
 cu=bpy.data.curves.new('Mapped centreline '+wid,'CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for pt,xy in zip(sp.points,pts):pt.co=(xy[0],xy[1],.18,1)
 ob=bpy.data.objects.new('SOURCE ROUTE '+wid,cu);current.objects.link(ob);ob['osm_way']=wid;ob['source_geometry']='Editable mapped centreline; rerun rail preprocessing after XY edits in source/mapped_geometry.json'
col('90_REVIEW_CAMERAS_AND_LIGHTS')
world=bpy.data.worlds.new('Kerala soft daylight');S.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.57,.69,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
sun=bpy.data.lights.new('Late morning sun','SUN');sun.energy=2.2;sun.angle=.16;o=bpy.data.objects.new('Late morning sun',sun);current.objects.link(o);o.rotation_euler=(.4,-.5,-.45)
def camera(n,p,target,lens=42,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);current.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=4000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
camera('01_Overall_full_station',(0,-1250,1100),(0,65,0),32)
camera('02_Heritage_forecourt',(-72,-85,32),(-6,1,6),48)
camera('03_Entrance_hall',(0,1.6,2.45),(0,12,2.8),20)
camera('04_Booking_hall',(119,-1.5,2.45),(110,7.2,2.65),24)
camera('14_Counter_working_detail',(109,10.8,2.3),(113,6.8,1.9),24)
camera('05_Waiting_lounge',(-56,2.3,2.4),(-47,8,2),20)
camera('06_Washroom',(-73,3.4,2.4),(-66,8,1.7),19)
camera('07_Station_office',(35,2.4,2.4),(42,8,1.9),20)
camera('08_Platform_one',(-171,16.4,2.55),(-153,18.5,2.25),27)
camera('09_Island_platform',(1,37.5,2.45),(90,40,3),30)
target=json.loads((R/'source/turnout_review_target.json').read_text())['xy'];tx,ty=target
camera('10_Turnout_detail',(tx-11,ty-10,8),(tx,ty,.1),43)
camera('15_Frog_closeup',(tx-3,ty-3,2.8),(tx,ty,.1),52)
camera('11_Maintenance_yard',(-105,230,50),(90,160,1),44)
camera('12_Full_yard_top',(0,75,1050),(0,75,0),45,1680)
camera('17_Platform_amenities_service_side',(-157,12.4,2.55),(-157,18.8,2.30),20)
camera('16_Furnished_building_roof_off',(80,-150,165),(20,3,0),40)
camera('13_Footbridge_detail',(-78,86,17),(-105,42,7),43)
S.camera=bpy.data.objects['02_Heritage_forecourt'];S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=4;S.render.resolution_x=1440;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
S['README']='Full-station TVC visual reconstruction in metres, mixed-date mapped rail network,2022 heritage photographs,furnished reconstructed interiors. Read README.md and evidence ledger. No rolling stock.'
S['asset_status']='TVC full-scale visual reconstruction, 2022 heritage plus mixed-date OSM railway footprint; not surveyed as-built'
S['no_rolling_stock']=True;S['gauge_inner_head_metres']=1.676;S['mapping_attribution']='© OpenStreetMap contributors, ODbL';S['interior_status']='Functional furnished reconstructions; exact floorplan unverified'
flush()
# Isolate ceiling/roof objects for documented roof-off navigation and reviews.
roofcol=bpy.data.collections.new('80_LIFT_OFF_ROOFS_AND_CEILINGS');S.collection.children.link(roofcol)
for o in list(S.objects):
 if o.type=='MESH' and any(s in o.name.lower() for s in (' ceiling','room ceiling','wing roof')):
  for c in list(o.users_collection):c.objects.unlink(o)
  roofcol.objects.link(o)
# Start with a usable full-campus viewport rather than the old36m study framing.
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.clip_end=5000;sp.shading.color_type='MATERIAL'
   if sp.region_3d:
    sp.region_3d.view_location=(0,60,0);sp.region_3d.view_distance=800;sp.region_3d.view_rotation=bpy.data.objects['01_Overall_full_station'].rotation_euler.to_quaternion()
exec(compile((R/'scripts/audit_stair_clearance.py').read_text(),str(R/'scripts/audit_stair_clearance.py'),'exec'))
for f in bpy.data.fonts:
 if f.filepath and f.filepath!='<builtin>':
  path=Path('/usr/share/fonts/truetype/dejavu')/Path(f.filepath).name
  if path.exists():f.filepath=str(path)
  try:f.pack()
  except:pass
try:bpy.ops.file.pack_all()
except:pass
bpy.ops.wm.save_as_mainfile(filepath=str(R/'TVC_full_station_v02.blend'),compress=True)
qa={'objects':len(S.objects),'meshes':sum(o.type=='MESH' for o in S.objects),'vertices':sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),'route_count':len(route_paths),'total_route_length_m':sum(route_lengths.values()),'route_lengths_m':route_lengths,'graph_turnouts':len(turnouts),'true_dead_end_buffers':len(buffers),'nominal_inner_rail_head_gauge_m':1.676,'mapped_platform_bodies':3,'platform_faces':5,'rolling_stock_objects':0,'units':'metres','component_counts':counts,'physical_frog_crossings':frog_count,'flangeway_width_m':.045,'turnout_nodes':turnouts,'buffer_nodes':buffers,'interiors':'Reconstructed furnished rooms, not as-built floor plans','rail_evidence':'Mixed-date current OSM coordinates; source map not a2022 survey'}
(R/'BUILD_QA.json').write_text(json.dumps(qa,indent=2));print('BUILD_COMPLETE',json.dumps({k:qa[k] for k in ('objects','vertices','route_count','total_route_length_m','graph_turnouts','true_dead_end_buffers')}),flush=True)
