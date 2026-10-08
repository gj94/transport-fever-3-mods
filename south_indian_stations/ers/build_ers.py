#!/usr/bin/env python3
"""ERS 2017 visual reconstruction. Run blender -b -t 4 --python build_ers.py -- --render.
Not a surveyed yard: demo tracks/platform length and component placement are configurable.
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent;random.seed(2017)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection':bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
COL=None

def collection(name):
 global COL
 COL=bpy.data.collections.new(name);scene.collection.children.link(COL);return COL

def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);return o

def mat(name,color,rough=.7,metal=0,noise=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if noise:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=3
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(*(v*.68 for v in color),1);ramp.color_ramp.elements[1].position=.87;ramp.color_ramp.elements[1].color=(*color,1)
  m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],bs.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.035;m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
 return m
white=mat('Warm white | weathered painted masonry',(.78,.78,.68),noise=4)
blue=mat('2017 cobalt blue painted bands',(.038,.085,.28),noise=5)
red=mat('Oxide red platform walls',(.48,.135,.10),noise=6)
steel=mat('Galvanised bridge members',(.46,.52,.51),.39,.68,9)
black=mat('Dark recesses and rubber',(.022,.033,.032))
glass=mat('Smoked blue glazing',(.055,.12,.14),.22,.55)
roof=mat('Weathered corrugated steel',(.32,.37,.34),.7,.35,12)
roofblue=mat('Blue stair hood painted steel',(.025,.28,.51),.45,.45,12)
stone=mat('Platform stone concrete',(.48,.46,.40),noise=24)
road=mat('Asphalt',(.095,.104,.097),noise=44)
yellow=mat('Safety ochre',(.89,.61,.085),noise=10)
cream=mat('Cream rail signage',(.82,.79,.61))
green=mat('Kiosk green',(.045,.27,.20),noise=6)
wood=mat('Bench dark timber',(.23,.10,.043),noise=8)
railmat=mat('Rusty rail web',(.27,.12,.055),.66,.5,13)
railhead=mat('Polished rail crown',(.39,.42,.41),.25,.85)
ballast=mat('Angular ballast gravel',(.23,.25,.24),noise=80)
leaf=mat('Palm leaf',(.12,.25,.045),noise=6)


def cube(name,loc,scale,m,bev=0):
 sx,sy,sz=[v/2 for v in scale]
 v=[(-sx,-sy,-sz),(-sx,-sy,sz),(-sx,sy,-sz),(-sx,sy,sz),(sx,-sy,-sz),(sx,-sy,sz),(sx,sy,-sz),(sx,sy,sz)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)]);me.update()
 o=bpy.data.objects.new(name,me);COL.objects.link(o);o.location=loc
 if m:o.data.materials.append(m)
 if bev:
  q=o.modifiers.new('Soft manufactured edges','BEVEL');q.width=bev;q.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def beam(name,a,b,width,m,depth=None):
 a,b=Vector(a),Vector(b);o=cube(name,(a+b)/2,(width,depth or width,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def cyl(name,loc,r,dep,m,verts=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=dep,location=loc);o=move(bpy.context.object);o.name=name;o.data.materials.append(m);return o

def tube(name,pts,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);COL.objects.link(o);o.data.materials.append(m);return o

def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o);o.data.materials.append(m);return o

def sign(name,x,y,z,w,h,texture):
 o=mesh(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],cream)
 uv=o.data.uv_layers.new();coords=[(0,0),(1,0),(1,1),(0,1)]
 for i in range(4):uv.data[i].uv=coords[i]
 m=bpy.data.materials.new(name+' | original RAQM sign art');m.use_nodes=True;n=m.node_tree.nodes;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(P/'textures'/f'{texture}.png'),check_existing=True);im.image.pack();m.node_tree.links.new(im.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);n.get('Principled BSDF').inputs['Roughness'].default_value=.72;o.data.materials.clear();o.data.materials.append(m);return o

def text(name,body,loc,size,m):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.002;o=bpy.data.objects.new(name,cu);COL.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(m);return o

def corrugated(name,x,y,z,w,d,m,pitch=.22):
 # explicit sinusoidal profile: X cross-section, Y span
 n=max(2,int(w/pitch)*4);v=[]
 for yy in [y-d/2,y+d/2]:
  for i in range(n+1):v.append((x-w/2+w*i/n,yy,z+.045*math.cos(i*math.pi/2)))
 o=mesh(name,[(a-x,b-y,c-z) for a,b,c in v],[(i,i+1,n+i+2,n+i+1) for i in range(n)],m);o.location=(x,y,z);so=o.modifiers.new('Sheet thickness 6 mm','SOLIDIFY');so.thickness=.006;return o

collection('01 | WEST FRONTAGE • 2017 photo-derived')
# Central pavilion: genuinely open doorways, separate piers/lintel instead of solid box.
cube('Entry foundation',(-5,0,.16),(21,15,.32),stone,.04)
for x in [-15,-11.4,1.4,5]:cube('Central masonry pier',(x,-5.8,4.3),(.7,1,8),white,.04)
# Façade above arched void: polygonal spandrel, no filled entrance.
N=48;xs=[-14+18*i/N for i in range(N+1)];zs=[3.3+3.35*(1-((x+5)/9)**2) for x in xs]
v=[]
for yy in [-6.15,-5.45]:
 for x,z in zip(xs,zs):v.extend([(x,yy,z),(x,yy,9.1)])
f=[]
for i in range(N):
 a=2*i;b=2*(N+1);f.extend([(a,a+2,a+3,a+1),(b+a+1,b+a+3,b+a+2,b+a),(a,a+b,a+b+2,a+2)])
mesh('White parabolic spandrel wall',v,f,white)
# Cobalt curve remains visually separate from pale spandrel.
av=[]
for yy in [-6.48,-6.04]:
 for x,z in zip(xs,zs):av.extend([(x,yy,z-.35),(x,yy,z+.13)])
af=[];n=len(xs)*2
for i in range(len(xs)-1):
 a=2*i;af.extend([(a,a+2,a+3,a+1),(n+a+1,n+a+3,n+a+2,n+a),(a,n+a,n+a+2,a+2),(a+1,a+3,n+a+3,n+a+1)])
mesh('Flat blue arched portal fascia',av,af,blue)
for s in [-1,1]:
 beam('Blue diagonal portal leg',(-5+s*8.7,-6.2,.35),(-5+s*5.8,-6.2,3.7),.52,blue,.8)
 cube('Portal outer side strip',(-5+s*9.2,-6.15,2),(.46,.8,3.5),blue)
cube('Entrance flat awning',(-5,-7.05,3.73),(20,3.1,.25),blue,.045)
for i,t in enumerate(['ml','hi','en']):sign('Trilingual yellow entrance '+t,-11.6+i*6.6,-8.64,3.8,6.55,.7,'entry_'+t)
cube('Top station name stone fascia',(-5,-6.21,8.54),(20.2,.21,1),white,.035)
for i,t in enumerate(['en','hi','ml']):sign('Roofline identity '+t,-11.65+i*6.65,-6.34,8.55,6.5,.78,'top_'+t)
cube('Entry rear wall',(-5,6.7,3.3),(20,.4,6.6),white)
cube('Entry roof slab',(-5,.6,7.9),(20.8,13.8,.26),white,.04)
for x in [-10.5,-6.8,-3.1,.6]:
 cube('Ticket hall window dark opening',(x,6.46,2.55),(2.4,.06,2.5),glass)
 for xx in [x-1.15,x,x+1.15]:cube('Ticket window jamb',(xx,6.36,2.55),(.07,.12,2.5),steel)
 cube('Ticket window crossbar',(x,6.33,2.75),(2.4,.1,.07),steel)
for x in [-10,0]:
 cube('Red lower entrance column',(x,-5.7,.9),(.5,.7,1.5),red)
 cube('White upper entrance column',(x,-5.7,2.3),(.5,.7,1.3),white)
# Clock face in front of arch.
o=cyl('Clock rim',(-5,-6.57,6.86),.64,.13,steel,64);o.rotation_euler[0]=math.pi/2
o=cyl('Clock ivory dial',(-5,-6.66,6.86),.58,.03,cream,64);o.rotation_euler[0]=math.pi/2
for i in range(12):
 a=2*math.pi*i/12;beam('Clock hour mark',(-5+.48*math.sin(a),-6.69,6.86+.48*math.cos(a)),(-5+.53*math.sin(a),-6.69,6.86+.53*math.cos(a)),.028,black)
beam('Clock minute hand',(-5,-6.72,6.86),(-5+.39,-6.72,6.86+.1),.03,black)
beam('Clock hour hand',(-5,-6.73,6.86),(-5-.16,-6.73,6.86+.24),.045,black)
# Narrow low left wing with deep doorway rhythm and blue fascia.
cube('Left wing roof',(-24,0,3.8),(17,13.5,.27),white,.035)
cube('Left wing rear',(-24,6.5,1.9),(17,.4,3.8),white)
for x in [-32,-28,-24,-20,-16]:
 cube('Left wing piers',(x,-5.8,1.8),(.48,.55,3.6),white)
 cube('Left wing red plinth',(x,-5.86,.55),(.5,.58,1.1),red)
cube('Left wing blue awning',(-24,-6.25,3.42),(17.8,2.2,.35),blue,.025)
for x in [-30,-26,-22,-18]:
 cube('Recessed shop doors',(x,-3.7,1.6),(2.5,.1,3),glass)
 for i in range(11):cube('Security shutter seams',(x,-3.77,.3+i*.245),(2.5,.015,.018),steel)
sign('ATM panel',-24,-7.38,4.12,3.1,.8,'atm')
# Right wing strong white piers, curved parapet and screened first-floor galleries.
cube('Right wing main floor',(22,1,.25),(34,13,.5),stone)
cube('Right wing first floor',(22,1,3.65),(34,13,.32),white)
cube('Right wing rear wall',(22,7.3,4.1),(34,.4,7.8),white)
# Four near-entry arched gallery recesses, then two broad curved-header bays.
# This asymmetry is visible in the cropped Shady59 2017 photograph.
for x in [6,18,28.5,39]:
 cube('Right wing major white pier',(x,-5.55,4.3),(.72,1.05,8.6),white,.035)
for x in [6.5,9.3,12.1,14.9,17.6]:
 cube('Near gallery blue vertical fin',(x,-5.94,5.5),(.24,.32,3.5),blue)

def arch_spandrel(name,x,w,opening_low,opening_rise,outer_edge,outer_dip,y=-5.5):
 n=32;v=[]
 for yy in [y-.25,y+.25]:
  for i in range(n+1):
   t=i/n;xx=x-w/2+w*t;arch=math.sin(math.pi*t)
   v.extend([(xx,yy,opening_low+opening_rise*arch),(xx,yy,outer_edge-outer_dip*arch)])
 faces=[];off=2*(n+1)
 for i in range(n):
  q=2*i;faces.extend([(q,q+2,q+3,q+1),(off+q+1,off+q+3,off+q+2,off+q),(q,off+q,off+q+2,q+2),(q+1,q+3,off+q+3,off+q+1)])
 return mesh(name,v,faces,white)

# First gallery has small open arch crowns; glazing sits recessed behind the masonry.
for x in [7.8,10.6,13.4,16.2]:
 w=2.55
 arch_spandrel('Small gallery arched masonry crown',x,w,6.55,.52,7.8,0)
 cube('Small gallery recessed glazing',(x,-5.10,5.2),(w-.16,.07,3.45),glass)
 cube('Small gallery pale sill',(x,-5.41,3.58),(w,.37,.16),white)
 for xx in [x-.77,x+.77]:cube('Small gallery dark mullion',(xx,-5.23,5.05),(.055,.10,2.9),steel)
 cube('Small gallery horizontal transom',(x,-5.24,5.1),(w-.13,.1,.055),steel)
 cube('Small gallery ground doorway',(x,-3.9,1.8),(w-.35,.1,2.65),black)
cube('Small gallery flat roof',(12,1,7.61),(12,13,.21),white)
# Broad curved openings beneath a concave parapet, not rectangular blue wall panels.
for x,w in [(23.25,9.7),(33.75,9.7)]:
 arch_spandrel('Broad gallery curved spandrel',x,w,6.3,.53,8.15,.74)
 cube('Broad gallery recessed glazing',(x,-5.13,5.0),(w-.18,.075,3.8),glass)
 cube('Broad gallery sill',(x,-5.43,3.45),(w,.42,.22),white)
 for i in range(8):
  xx=x-w/2+.52+i*(w-1.04)/7
  top=6.3+.53*math.sin(math.pi*(xx-x+w/2)/w)
  cube('Broad gallery vertical dark mullion',(xx,-5.29,(top+3.55)/2),(.075,.14,top-3.55),steel)
 for z in [4.3,5.15]:cube('Broad gallery horizontal transom',(x,-5.27,z),(w-.13,.13,.045),steel)
 for xx in [x-2.5,x+2.5]:
  cube('Broad gallery ground doorway',(xx,-3.9,1.78),(4.3,.1,2.6),black)
 cube('Broad wing roof slab',(x,1,7.35),(w,13,.2),white)
 cube('Broad wing blue ground fascia',(x,-5.59,3.1),(w,.36,.26),blue)
# blue upright beside entrance; flush fascia
cube('Tall cobalt entrance blade',(5.55,-6.14,5.2),(.8,1.1,10.4),blue,.04)
# lattice screen genuine open repeating masonry slots
for x0 in [-13.9,3.5]:
 for zz in [1.0,1.55,2.1,2.65]:
  for xx in range(3):cube('Entrance perforated screen pier',(x0+xx*.23,-5.1,zz),(.06,.2,.5),white)
 for zz in [.75,1.3,1.85,2.4,2.95]:cube('Entrance perforated screen lintel',(x0+.23,-5.1,zz),(.75,.2,.06),white)
sign('Ticket hall wayfinding',-5,6.23,4.32,6.5,.85,'tickets')
# Forecourt adaptable stage, not cadastral boundary.
print('Building 02 | FORECOURT',flush=True)
collection('02 | FORECOURT • inferred dressing')
cube('Presentation ground',(2,2,-.32),(120,105,.5),road)
cube('Paved footway',(2,-9.8,.09),(76,5.5,.18),stone,.02)
for x in range(-36,41):
 cube('Kerb painted segment',(x,-12.5,.23),(.98,.28,.3),white if x%2 else black,.025)
for x in range(-34,40,3):
 cube('Forecourt paving expansion seam',(x,-9.8,.19),(.012,5.3,.006),black)
for x in range(-26,38,6):
 cube('Parking bay line',(x,-22,.0),(.1,8,.015),cream)
cube('Parking bay end',(4,-26,.0),(64,.1,.015),cream)
for x in range(-30,39,8):cube('Road dashed guide',(x,-31,.0),(3,.12,.015),cream)
for x in [-29,10,31]:
 cyl('Concrete planter',(x,-10,.45),1.05,.7,white,32)
 cyl('Planter earth',(x,-10,.82),.91,.08,wood,32)
 for i in range(4):
  xx=x+random.uniform(-.35,.35);yy=-10+random.uniform(-.3,.3);h=random.uniform(2.5,4)
  tube('Palm stem',[(xx,yy,.9),(xx+.15,yy,2),(xx+.3,yy,h)],.06,wood)
  for j in range(8):
   a=j*math.pi/4;verts=[(xx+.3,yy,h),(xx+.3+.85*math.cos(a-.12),yy+.85*math.sin(a-.12),h+.28),(xx+.3+1.6*math.cos(a),yy+1.6*math.sin(a),h-.5),(xx+.3+.85*math.cos(a+.12),yy+.85*math.sin(a+.12),h+.28)]
   mesh('Palm lanceolate frond',verts,[(0,1,2,3)],leaf)
for x in [-34,18,38]:
 cyl('Forecourt lamp post',(x,-15,3.5),.075,7,steel)
 cube('Forecourt lamp head',(x,-15,7.1),(.85,.4,.16),cream,.04)
for x in [-13,-9,-1,3]:
 cyl('Short entry bollard',(x,-10.8,.56),.07,1.1,steel)
for x in [17,26]:
 for i in range(5):cube('Forecourt timber bench slat',(x,-10.2+i*.12,.58),(2.2,.1,.09),wood,.015)
 for xx in [x-.8,x+.8]:cube('Bench concrete leg',(xx,-9.95,.28),(.17,.55,.55),white)
sign('Forecourt parking direction',31,-17.0,3.0,4.5,1.4,'parking')
for xx in [29,33]:cyl('Parking sign post',(xx,-16.85,1.7),.055,3.4,steel)
# Trackside stage. Separate collections clearly communicate assembly rather than yard survey.
print('Building 03 | PLATFORM',flush=True)
collection('03 | PLATFORM KIT • configurable 96 m demonstration')
L=96; platform_y=16.5
cube('Platform retaining wall',(0,platform_y,.53),(L,8.6,1.06),red,.035)
cube('Platform coping',(0,platform_y,1.09),(L,8.8,.17),stone,.035)
for yy in [12.28,20.72]:
 cube('Platform edge pale coping',(0,yy,1.18),(L,.35,.055),cream)
 cube('Platform safety paint',(0,yy+(.5 if yy<16 else -.5),1.186),(L,.1,.015),yellow)
for x in range(-47,49,3):cube('Platform slab transverse seam',(x,16.5,1.183),(.015,8.3,.009),black)
# Low canopy with visible open web brackets and corrugated sheet.
for x in [-40,-32,-28,-12,-8,0,8,16,24,32,40,48]:
 for yy in [14.5,18.5]:
  cube('Canopy concrete foot',(x,yy,1.36),(.6,.6,.38),stone)
  beam('Canopy steel column',(x,yy,1.5),(x,yy,4.7),.13,steel)
  beam('Canopy cantilever knee',(x,yy,3.7),(x,yy+(-1.8 if yy<16 else 1.8),4.7),.085,steel)
 beam('Canopy cross tie',(x,11.9,4.75),(x,21.1,4.75),.12,steel)
 beam('Canopy roof rafter left',(x,11.9,4.75),(x,16.5,5.25),.11,steel)
 beam('Canopy roof rafter right',(x,16.5,5.25),(x,21.1,4.75),.11,steel)
 for i in range(6):
  yy=12+i*1.75;beam('Canopy open web diagonal',(x,yy,4.76),(x,yy+.75,5.25-abs(yy+.75-16.5)*.108),.046,steel)
for yy in [12.2,14.4,16.5,18.6,20.8]:
 for a,b in [(-44,-27),(-11,48)]:beam('Canopy longitudinal purlin',(a,yy,5.25-abs(yy-16.5)*.108),(b,yy,5.25-abs(yy-16.5)*.108),.08,steel)
for side in [-1,1]:
 for a,b in [(-44,-27),(-11,48)]:
  o=corrugated('Platform corrugated roof '+str(side),(a+b)/2,16.5+side*2.35,5.02,b-a,4.78,roof);o.rotation_euler[0]=side*-.108
for yy in [11.84,21.16]:tube('Canopy rainwater gutter',[(-44,yy,4.71),(48,yy,4.71)],.09,steel)
for x in [-35,-11,13,37]:
 tube('Platform rainwater downpipe',[(x,21,4.7),(x,20.1,4.6),(x,20.1,1.3)],.055,steel)
 cube('Canopy fluorescent light',(x,16.5,4.61),(1.2,.14,.08),cream)
# furniture and ticket-style station name boards, observed weathered yellow with finials.
for x in [-43,43]:
 for xx in [x-2,x+2]:
  cube('Yellow nameboard post',(xx,12.95,2.55),(.15,.2,2.8),yellow)
  bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=.18,depth=.24,location=(xx,12.95,4.08));o=move(bpy.context.object);o.data.materials.append(yellow)
 cube('Nameboard backing',(x,12.95,3.15),(4,.16,1.78),yellow,.03)
 sign('Station multilingual nameboard',x,12.85,3.15,3.84,1.64,'platform_name')
for x in [-30,-8,14,36]:
 for i in range(5):cube('Platform bench timber slat',(x,16.2+i*.12,1.72),(2.3,.09,.08),wood,.013)
 for i in range(4):cube('Platform bench back slat',(x,16.86,1.94+i*.12),(2.3,.08,.09),wood,.013)
 for xx in [x-.85,x+.85]:
  beam('Bench cast iron foot',(xx,16.2,1.2),(xx,16.2,1.7),.09,black)
  beam('Bench back frame',(xx,16.8,1.2),(xx,16.8,2.4),.085,black)
# green/yellow kiosk directly grounded in November 2017 platform photo.
kiosk_existing=set(bpy.data.objects)
x=2;y=16
cube('Kiosk base',(x,y,1.33),(3.4,2.8,.3),stone)
for xx in [x-1.6,x+1.6]:cube('Kiosk green side pier',(xx,y,2.63),(.24,2.6,2.3),green)
cube('Kiosk rear wall',(x,y+1.25,2.66),(3.4,.16,2.5),green)
cube('Kiosk front counter lower',(x,y-1.28,1.98),(3.4,.16,1.2),green)
cube('Kiosk yellow counter edging',(x,y-1.4,2.61),(3.6,.3,.12),yellow,.025)
cube('Kiosk fascia',(x,y-1.25,4),(3.6,.2,.85),green)
sign('Catering stall sign',x,y-1.37,4,3.5,.78,'catering')
corrugated('Kiosk roof',x,y,4.52,4,3.25,roof)
for zz in [1.65,2,2.33]:
 cube('Snack shelf',(x,y-1.4,zz),(2.7,.2,.045),yellow)
 for j in range(11):
  m=[red,yellow,blue,cream,green][(j+int(zz*10))%5];cube('Generic packaged snack',(x-1.2+j*.24,y-1.45,zz+.12),(.2,.07,.2),m,.01)
for j in range(10):
 cyl('Unbranded water bottle',(x-1.2+j*.25,y-.6,2.9),.075,.45,glass,12)
 cyl('Bottle cap',(x-1.2+j*.25,y-.6,3.15),.05,.035,blue,12)
# The kiosk shopfront faces along the platform, as the 2017 photograph does.
# Rotate the complete assembly (including artwork and merchandise) around its centre.
rot=Matrix.Translation(Vector((2,16,0))) @ Matrix.Rotation(math.pi/2,4,'Z') @ Matrix.Translation(Vector((-2,-16,0)))
bpy.context.view_layer.update()
for ko in set(bpy.data.objects)-kiosk_existing:ko.matrix_world=rot @ ko.matrix_world
for x in [-16,7,28]:
 cyl('Waste bin body',(x,18,1.62),.24,.85,red,24);cyl('Waste bin rim',(x,18,2.06),.27,.08,black,24)
# coach-position sign is NOT platform number 13
cyl('Coach-position post',(-12,13,2.6),.04,2.9,blue)
sign('Coach position 13 (not platform number)',-12,12.92,3.5,.75,.9,'coach_position')
# Two sample broad-gauge tracks. No switches or invented complete yard.
print('Building 04 | TRACK',flush=True)
collection('04 | TRACK MODULES • demo placement only')
for y in [24,29.8]:
 cube('Ballast bed',(0,y,.13),(110,3.6,.3),ballast,.08)
 for x in [i*.62-54.7 for i in range(177)]:
  cube('Concrete broad-gauge sleeper',(x,y,.34),(.23,2.75,.19),stone,.03)
 for yy in [y-.87,y+.87]:
  cube('Rail foot',(0,yy,.49),(110,.14,.03),railmat)
  cube('Rail web',(0,yy,.565),(110,.025,.13),railmat)
  cube('Rail head',(0,yy,.645),(110,.065,.045),railhead,.01)
 # sparse explicit rail fastening plates, adequate demonstration
 for x in range(-53,55,2):
  for yy in [y-.87,y+.87]:cube('Rail fastener plate',(x,yy,.45),(.22,.26,.025),railmat)
# blue utility water pipe seen beside 2017 tracks
for y in [22,32.5]:
 tube('Blue trackside water main',[(-53,y,.55),(53,y,.55)],.055,roofblue)
 for x in range(-50,54,4):beam('Utility pipe support',(x,y,.1),(x,y,.55),.06,white)
# electrification grounded in observed masts, adjustable assembly
print('Building 05 | OHE',flush=True)
collection('05 | OHE MODULE • indicative spacing')
for x in [-42,-10,22,48]:
 for y in [22.1,32.2]:
  cube('OHE mast concrete foundation',(x,y,.45),(.72,.72,.9),stone)
  beam('OHE steel mast',(x,y,.8),(x,y,8.5),.18,steel)
  for z in [1.5,2.8,4.1,5.4,6.7,8]:cube('OHE mast inset',(x,y-.105,z),(.085,.025,.66),black)
  end=y+2 if y<25 else y-2
  beam('OHE cantilever',(x,y,7.7),(x,end,7.5),.065,steel)
  beam('OHE diagonal stay',(x,y,8.25),(x,end,7.5),.042,steel)
  for k in range(7):cyl('Cantilever insulator shed',(x,end,7.3+k*.044),.105,.026,wood)
for yy in [24,29.8]:
 tube('Contact wire',[(-54,yy,6.15),(54,yy,6.15)],.012,railmat)
 for a,b in [(-54,-42),(-42,-10),(-10,22),(22,48),(48,54)]:
  pts=[(a+(b-a)*i/16,yy,6.9-.3*math.sin(math.pi*i/16)) for i in range(17)];tube('Messenger catenary',pts,.016,railmat)
 for x in range(-50,55,5):beam('Catenary dropper',(x,yy,6.15),(x,yy,6.68),.009,railmat)
# photo-anchored silver lattice footbridge, across demo tracks; x fixed, long axis y
print('Building 06 | FOOTBRIDGE',flush=True)
collection('06 | FOOTBRIDGE KIT • 2017 steel lattice and stairs')
bx=-25;zdeck=7.2
cube('Footbridge walkway',(bx,24,zdeck),(3.5,28,.24),steel)
for yy in [10,17,24,31,38]:
 for xx in [bx-1.5,bx+1.5]:
  beam('Bridge supporting column',(xx,yy,1.2),(xx,yy,7.15),.16,steel)
  beam('Bridge transverse knee',(xx,yy,6.1),(bx,yy,7.08),.1,steel)
for xx in [bx-1.65,bx+1.65]:
 for y in range(10,39,4):beam('Bridge vertical truss post',(xx,y,7.25),(xx,y,9.8),.12,steel)
 for y in range(10,38,4):
  if xx>bx and y==14:continue # actual stair opening in east-side truss
  beam('Bridge X brace',(xx,y,7.32),(xx,y+4,9.72),.105,steel)
  beam('Bridge X brace',(xx,y,9.72),(xx,y+4,7.32),.105,steel)
 for z in [7.35,7.85,8.22,8.6,9.77]:
  segments=[(10,15.25),(17.75,38)] if xx>bx and z<9 else [(10,38)]
  for a,b in segments:beam('Bridge horizontal rail',(xx,a,z),(xx,b,z),.07 if z<9 else .14,steel)
corrugated('Footbridge corrugated roof',bx,24,9.98,4.35,29,roof)
# covered straight stair connects platform to bridge, axis x, with risers and guards.
sx=bx+1.75;ex=bx+13.75;yy=16.5;n=34
for i in range(n):
 xx=sx+(ex-sx)*(i+.5)/n;zz=zdeck-(zdeck-1.18)*(i+1)/n
 cube('Footbridge stair tread',(xx,yy,zz),((ex-sx)/n+.015,2.3,.12),stone)
 cube('Footbridge stair riser',(xx-(ex-sx)/n*.48,yy,zz+.09),(.055,2.3,.18),red)
for sy in [-1,1]:
 y=yy+sy*1.2
 beam('Stair steel stringer',(sx,y,zdeck-.15),(ex,y,1.03),.22,steel)
 beam('Stair handrail',(sx,y,zdeck+1.12),(ex,y,2.3),.065,steel)
 beam('Stair lower guardrail',(sx,y,zdeck+.65),(ex,y,1.83),.05,steel)
 for i in range(0,n+1,3):
  xx=sx+(ex-sx)*i/n;zz=zdeck-(zdeck-1.18)*i/n;beam('Stair guard upright',(xx,y,zz),(xx,y,zz+1.12),.05,steel)
# Blue hood slopes with staircase; independent roof mesh with corrugation ribs.
for sy in [-1,1]:
 v=[(sx,yy,10.1),(ex+.6,yy,3.94),(ex+.6,yy+sy*1.65,3.45),(sx,yy+sy*1.65,9.61)]
 mesh('Blue stair hood slope',v,[(0,1,2,3)],roofblue)
 for i in range(65):
  t=i/64;xx=sx+(ex+.6-sx)*t;zz=10.1-(10.1-3.94)*t;beam('Stair hood transverse corrugation',(xx,yy,zz),(xx,yy+sy*1.65,zz-.49),.035,roofblue)
 for i in range(5):
  t=i/4;xx=sx+(ex-sx)*t;zz=zdeck-(zdeck-1.18)*t
  beam('Stair canopy upright',(xx,yy+sy*1.35,zz),(xx,yy+sy*1.35,zz+2.45),.07,steel)
# Utility cabinets from trackside reference
for x in [-39,-37.5]:
 cube('Relay cabinet concrete base',(x,33.6,.35),(1.2,.8,.5),stone)
 cube('Relay cabinet',(x,33.6,1.18),(1,.6,1.45),white,.04)
 cube('Relay cabinet door',(x,33.28,1.16),(.85,.025,1.29),cream,.01)
 cube('Relay cabinet handle',(x+.28,33.24,1.18),(.035,.03,.14),steel)
 for i in range(4):cube('Relay cabinet ventilation slot',(x,33.245,1.54+i*.06),(.45,.02,.017),black)
# presentation cameras
print('Building 90 | PRESENTATION',flush=True)
collection('90 | PRESENTATION • cameras lights')
world=bpy.data.worlds.new('Soft Kerala daylight');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.61,.72,.81,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
bpy.ops.object.light_add(type='SUN',location=(0,0,30));o=move(bpy.context.object);o.name='Afternoon sun';o.rotation_euler=(.45,-.5,-.55);o.data.energy=2.2;o.data.angle=.12
bpy.ops.object.light_add(type='AREA',location=(0,-20,25));o=move(bpy.context.object);o.name='Sky bounce';o.data.energy=1800;o.data.shape='DISK';o.data.size=35

def camera(name,loc,target,lens=44,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=move(bpy.context.object);o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=500
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
cams=[camera('01_Hero_west_frontage',(60,-96,18),(2,-1,3.7),52),camera('02_Front_elevation',(2,-85,7),(2,-2,4.6),50,81),camera('03_Platform_and_footbridge',(10,11.5,2.8),(-8,16,3.6),28),camera('04_Entrance_detail',(-20,-29,10),(-5,-5,4.2),47)]
scene.camera=cams[0];scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.65;scene.render.image_settings.file_format='PNG'
scene['asset']='ERS Ernakulam Junction | coherent pre-redevelopment 2017 modular visual reconstruction'
scene['survey_status']='Photo-inferred dimensions. Demo track placement, canopy length, rear/roof depth and interior are artistic completion, not a measured yard.'
scene['references']='Shady59 2017-08-02 frontage; KannanVM 2017-11-19 platform / bridge, CC BY-SA 4.0; see SOURCES.md'
scene['units']='Metres; track gauge 1.675 m; other dimensions inferred'
for o in bpy.data.objects:
 if o.type=='MESH':o['asset_part']='ERS_2017'
# Pack all sign textures; make saved scene portable.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_2017_station.blend'))
# glTF converts editable curves/text through depsgraph; exclude presentation lights and cameras.
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
 if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'exports'/'ERS_2017_station.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
qa={'blender':bpy.app.version_string,'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'materials':len(bpy.data.materials),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'metres_per_unit':scene.unit_settings.scale_length,'gauge_m':1.675,'render_threads':4,'render_samples':64,'source_saved':True,'export_glb_bytes':(P/'exports'/'ERS_2017_station.glb').stat().st_size}
qa['indian_broad_gauge_standard_m']=1.676
qa['model_gauge_target_m']=1.675
qa['gauge_compliance']='Approximate visual context: model about 1 mm narrower than 1.676 m standard; no exact compliance claimed'
(P/'qa_build.json').write_text(json.dumps(qa,indent=2))
print('ERS_SOURCE_CHECKPOINT_SAVED',flush=True)
if '--render' in sys.argv:
 for cam in cams:
  scene.render.resolution_y=400 if cam.name.startswith('02_') else 1000
  scene.camera=cam;scene.render.filepath=str(P/'renders'/(cam.name+'.png'));bpy.ops.render.render(write_still=True)
 scene.camera=cams[0];scene.render.resolution_y=1000;bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_2017_station.blend'))
