#!/usr/bin/env python3
"""ERS 2017 visual reconstruction. Run blender -b -t 4 --python build_ers.py -- --render.
Full station scene using inspected map-derived plan, photo-derived facade and reconstructed interiors.
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
 print('COLLECTION',name,flush=True)
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
 v=[(r*math.cos(i*math.tau/verts),r*math.sin(i*math.tau/verts),z) for z in [-dep/2,dep/2] for i in range(verts)]
 f=[tuple(range(verts-1,-1,-1)),tuple(range(verts,verts*2))]
 for i in range(verts):j=(i+1)%verts;f.append((i,j,j+verts,i+verts))
 o=mesh(name,v,f,m);o.location=loc;return o

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
# V02 FULL-STATION GEOMETRY. x follows station north; y points east.
# OSM trace origins and all inferred replacement dimensions are in DIMENSIONS.csv.
for o in list(scene.objects):
 if any(o.name.startswith(k) for k in ['Presentation ground','Entry rear wall','Ticket hall window','Ticket window','Left wing rear','Recessed shop doors','Security shutter','Right wing rear wall','Small gallery ground doorway','Broad gallery ground doorway']):bpy.data.objects.remove(o,do_unlink=True)
# Build efficient repeated components in editable, semantically named meshes.
class Batch:
 def __init__(self,name,m):self.name=name;self.m=m;self.v=[];self.f=[]
 def box(self,p,s,ang=0):
  k=len(self.v);c=math.cos(ang);q=math.sin(ang)
  for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
   a*=s[0]/2;b*=s[1]/2;d*=s[2]/2;self.v.append((p[0]+a*c-b*q,p[1]+a*q+b*c,p[2]+d))
  self.f.extend([tuple(k+i for i in face) for face in [(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)]])
 def finish(self):return mesh(self.name,self.v,self.f,self.m) if self.v else None
floor=mat('Polished grey terrazzo with fine aggregate',(.36,.39,.37),.32,0,72)
tile=mat('Warm cream sanitary ceramic',(.73,.77,.70),.24,0,22)
seat=mat('Waiting room blue molded seating',(.035,.15,.28),.36)
soil=mat('Humid Kerala laterite soil',(.24,.17,.105),noise=35)
collection('02B | FULL SITE • mapped envelope')
cube('Full railway site base',(175,58,-.42),(1400,240,.65),soil)
cube('West access road',(120,-34,-.035),(850,20,.12),road)
cube('East Karshaka Road',(20,134,-.035),(760,13,.12),road)
# Reconstructed support rooms fit behind retained photo-derived frontage.
collection('03 | WEST INTERIORS • furnished reconstruction')
# roof stays removable by collection/object; all room walls have physical doors.
def wall_door(name,x,y,w,h=3.3,door=1.6,axis='x',m=white,z=.35):
 for s in [-1,1]:
  p=(x+s*(w+door)/4,y,z+h/2) if axis=='x' else (x,y+s*(w+door)/4,z+h/2)
  sc=((w-door)/2,.18,h) if axis=='x' else (.18,(w-door)/2,h)
  cube(name+' doorway side',p,sc,m)
 cube(name+' overdoor',(x,y,z+h-.35),(door,.18,.7) if axis=='x' else (.18,door,.7),m)
def bench(x,y,z=.35,w=2.4):
 for xx in [x-w*.35,x+w*.35]:
  cube('Seat steel legs',(xx,y,z+.25),(.055,.50,.5),steel)
 cube('Bench seat rail',(x,y,z+.40),(w,.10,.09),steel)
 for i in range(4):
  xx=x-w*.36+i*w*.24
  cube('Molded blue passenger seat',(xx,y,z+.52),(w*.215,.48,.11),seat,.03)
  o=cube('Molded blue backrest',(xx,y+.22,z+.82),(w*.215,.085,.50),seat,.03);o.rotation_euler[0]=-.10
  for sy in [-1,1]:cube('Seat armrest',(xx+sy*w*.108,y,z+.74),(.035,.44,.05),steel)
def desk(x,y,z=.35):
 cube('Desk laminate top',(x,y,z+.77),(1.7,.75,.08),wood,.02)
 for xx in [x-.69,x+.69]:cube('Desk pedestal',(xx,y,z+.38),(.30,.63,.72),cream)
 cube('Desktop monitor foot',(x,y+.10,z+.83),(.36,.25,.035),black)
 cube('Monitor stand',(x,y+.16,z+1.01),(.06,.05,.34),black)
 cube('Computer monitor',(x,y+.18,z+1.21),(.62,.065,.39),black,.01)
 cube('Computer display',(x,y+.14,z+1.21),(.55,.01,.31),roofblue)
 cube('Keyboard',(x,y-.14,z+.83),(.48,.15,.02),black)
 bench(x,y-.8,z, .75)
def fan(x,y,z):
 cyl('Ceiling fan stem',(x,y,z),.025,.5,steel,8);cyl('Ceiling fan motor',(x,y,z-.3),.13,.16,cream,16)
 for j in range(3):
  a=j*2*math.pi/3;o=cube('Ceiling fan blade',(x+.36*math.cos(a),y+.36*math.sin(a),z-.31),(.65,.14,.024),cream);o.rotation_euler[2]=a
# Floor at facade level, platform connection via shallow ramp.
cube('Ticket hall terrazzo floor',(-5,1,.35),(20,12.5,.10),floor)
for x in range(-14,5,2):cube('Hall floor grout',(x,1,.406),(.008,12.3,.005),cream)
for y in range(-5,8,2):cube('Hall transverse grout',(-5,y,.406),(19.6,.008,.005),cream)
# Eight actual ticket openings, rear clerks' service aisle, connected to right side corridor.
for i in range(5):
 x=-12.3+i*3.1
 cube('Ticket counter masonry',(x,4.8,.98),(2.9,.34,1.25),red)
 cube('Ticket polished counter',(x,4.64,1.63),(3,.65,.095),black)
 for dx in [-1.45,1.45]:cube('Ticket glazed divider frame',(x+dx,4.8,2.31),(.055,.07,1.45),steel)
 cube('Ticket overhead transom',(x,4.8,3.04),(2.9,.08,.08),steel)
 for dx in [-.9,.9]:cube('Ticket safety glass side',(x+dx,4.81,2.34),(1.0,.025,1.31),glass)
 cube('Ticket transaction opening sill',(x,4.68,1.75),(.65,.32,.035),steel)
 text('Ticket counter number','0'+str(i+1),(x,4.56,2.87),.25,cream)
 desk(x,6.0)
 for yy in [-.6,1.4,3.3]:cyl('Queue post',(x-1.0,yy,.86),.038,1,steel,10)
 for yy in [-.6,1.4]:beam('Queue barrier',(x-1,yy,1.29),(x-1,yy+2,1.29),.04,steel)
text('Ticket hall header','UNRESERVED TICKETS  |  RESERVATIONS',(-5,4.52,3.52),.32,blue)
for x in [-11,-5,1]:fan(x,.2,5.4)
# departure board with plausible generic content, never fictional timetable claims.
cube('Electronic departures cabinet',(-5,3.9,4.6),(6,.20,.95),black)
text('Departures display','ERNAKULAM JN  •  ENQUIRY  •  PLATFORMS 1–6',(-5,3.77,4.43),.24,yellow)
for x in [-28,-21]:
 for y in [-.6,1.4,3.4]:bench(x,y,.30,3.8)
cube('West waiting floor',(-24,.6,.29),(17,13,.12),floor)
wall_door('Waiting room rear passage',-24,6.6,17,3.4,2.5)
text('Waiting room sign','WAITING HALL',(-24,6.46,2.85),.45,blue)
for x in [-29,-23,-17]:fan(x,1,3.20)
# Right wing rooms: enquiry, office, waiting lounge and sanitary block.
for x,w,title in [(10.5,9,'ENQUIRY'),(20,10,'STATION OFFICE'),(30,10,'WAITING LOUNGE')]:
 cube(title+' floor',(x,1,.54),(w,12,.09),floor)
 wall_door(title+' back wall',x,7.25,w,3,1.3)
 wall_door(title+' partition',x-w/2,1,12,3,1.2,'y')
 text(title+' label',title,(x,-3.82,2.9),.35,blue)
 if title=='WAITING LOUNGE':
  for yy in [-1.2,1,3.2]:bench(x,yy,.6,5)
 else:
  for xx in [x-2,x+2]:desk(xx,2,.6)
  for xx in [x-3,x-1,x+1,x+3]:
   cube('Office filing cabinet',(xx,5.9,1.6),(.75,.65,1.9),cream)
   for z in [1,1.5,2,2.5]:cube('Cabinet drawer face',(xx,5.56,z),(.68,.02,.43),white);cube('Drawer handle',(xx,5.52,z),(.15,.045,.035),steel)
 fan(x,1,3.15)
# Toilet annex extended along western side, with open stall aisles and drain grates.
collection('04 | SANITARY AND SERVICE INTERIORS')
cube('Sanitary block floor',(49,1,.34),(18,12,.18),tile)
for x in [40,58]:wall_door('Toilet block end wall',x,1,12,3.3,1.4,'y')
wall_door('Toilet front wall',49,-5,18,3.3,1.6)
cube('Sanitary rear wall',(49,7,2),(18,.20,3.6),white)
cube('Removable sanitary roof',(49,1,3.9),(18.4,12.4,.18),white)
text('Toilets sign','TOILETS / WASHROOMS',(49,-5.14,3.05),.45,blue)
for i in range(6):
 x=41.5+i*2.6
 for xx in [x-1.15,x+1.15]:cube('Toilet cubicle partition',(xx,4,1.65),(.09,4.4,2.45),tile)
 cube('Toilet cubicle door',(x+0.25,1.7,1.5),(1.4,.08,2.3),roofblue)
 cube('Door latch',(x-.28,1.62,1.55),(.14,.04,.04),steel)
 cyl('WC pedestal',(x,5.0,.64),.24,.4,tile,20)
 cyl('WC bowl',(x,5.0,.92),.32,.16,tile,24)
 cyl('WC bowl opening',(x,5.0,1.007),.21,.01,black,24)
 cube('WC cistern',(x,5.45,1.24),(.58,.21,.60),tile,.03)
 cube('Flush button',(x,5.45,1.55),(.10,.05,.01),steel)
for x in [43,46,49,52,55]:
 cube('Wash basin pedestal',(x,-3,.82),(.25,.32,.75),tile)
 cube('Wash basin',(x,-3,1.22),(.70,.55,.20),tile,.08)
 cube('Basin dark recess',(x,-3,1.33),(.43,.34,.01),glass)
 tube('Basin chrome tap',[(x,-2.8,1.3),(x,-2.8,1.57),(x,-3,1.57)],.022,steel)
 cube('Washroom mirror',(x,-4.89,2.1),(.8,.04,.95),steel)
for x in range(42,57):cube('Washroom floor drain grille',(x,-.3,.439),(.12,.5,.014),steel)
# Service corridor behind retained west building, connects all rooms to PF1.
cube('Rear circulation floor',(10,9.8,.48),(105,5,.25),floor)
for x in [-30,-10,10,30,50]:
 cube('Rear colonnade pillar',(x,11.6,2.4),(.35,.35,3.8),white)
 cube('Passage light',(x,9.7,3.7),(1.2,.15,.08),cream)
cube('Rear passage canopy',(10,9.7,4.0),(105,5.5,.18),roof)
mesh('Accessible west hall to platform ramp',[(-15,7.4,.4),(4,7.4,.4),(4,17.3,1.16),(-15,17.3,1.16)],[(0,1,2,3)],stone)
# Map-derived tracks and platform polygons.
W=json.loads((P/'references'/'osm_rail.json').read_text())
def xy(p):
 e=(p[0]-76.29105)*109640;n=(p[1]-9.9693)*111195
 return (n*.981-e*.194,e*.981+n*.194+14)
def prism(name,pts,lo,hi,m):
 n=len(pts);v=[(x,y,z) for z in [lo,hi] for x,y in pts];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;f.append((i,j,n+j,n+i))
 return mesh(name,v,f,m)
def strip(name,pts,width,z,depth,m):
 vs=[]
 for i,p in enumerate(pts):
  a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);v=(b-a).normalized();nx=-v.y;ny=v.x
  for dz in [-depth/2,depth/2]:
   for s in [-1,1]:vs.append((p[0]+nx*width*s/2,p[1]+ny*width*s/2,z+dz))
 fs=[]
 for i in range(len(pts)-1):
  a=i*4;b=a+4;fs.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 return mesh(name,vs,fs,m)
collection('05 | SIX PLATFORM FACES • map polygon plan')
platforms=[]
for w in W:
 if w['tags'].get('railway')!='platform':continue
 pts=[xy(p) for p in w['points'][:-1]];name=w['tags']['name'];platforms.append((name,pts))
 prism(name+' red retaining body',pts,.05,1.05,red);prism(name+' concrete tiled surface',pts,1.05,1.16,stone)
 strip(name+' pale perimeter coping',pts+[pts[0]],.30,1.18,.05,cream)
 for i in range(len(pts)):
  a=pts[i];b=pts[(i+1)%len(pts)];v=Vector(b)-Vector(a)
  if v.length>25:
   for t in range(int(v.length/3)):
    q=Vector(a)+v*((t+.5)*3/v.length);o=cube('Platform tactile edge slab',(q.x,q.y,1.214),(.55,.28,.024),yellow);o.rotation_euler[2]=math.atan2(v.y,v.x)
# Rail paths clip to entire 1.35km station/throats. Avoid including separate depot 1.5km away.
collection('06 | CONNECTED YARD • map-derived 1676mm track')
paths=[];nodes={};trackledger=[]
for w in W:
 if w['tags'].get('railway')!='rail':continue
 pp=[xy(p) for p in w['points']];segs=[];seg=[]
 for p in pp:
  if -510<p[0]<850 and -30<p[1]<155:seg.append(p)
  else:
   if len(seg)>1:segs.append(seg)
   seg=[]
 if len(seg)>1:segs.append(seg)
 for j,pts in enumerate(segs):
  paths.append((w['id'],pts,w['tags']));trackledger.append({'OSM_way':w['id'],'service':w['tags'].get('service','running'),'length_m':sum((Vector(b)-Vector(a)).length for a,b in zip(pts,pts[1:]))})
  for i,p in enumerate(pts):
   for k in [i-1,i+1]:
    if 0<=k<len(pts):
     key=tuple(round(q,3) for q in p);nkey=tuple(round(q,3) for q in pts[k]);existing=nodes.setdefault(key,[])
     if not any(tuple(round(q,3) for q in pair[0][1])==nkey for pair in existing):existing.append(([p,pts[k]],w['id']))
  # Mesh rail sections: true inner head faces separated by 1.676m.
  strip('Ballast formation '+w['id'],pts,3.7,.17,.30,ballast)
  for side in [-1,1]:
   off=[]
   for i,p in enumerate(pts):
    v=(Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])).normalized();off.append((p[0]-v.y*.868*side,p[1]+v.x*.868*side))
   strip('Rail foot '+w['id'],off,.150,.475,.03,railmat)
   strip('Rail web '+w['id'],off,.018,.548,.12,railmat)
   strip('Rail crown exact gauge '+w['id'],off,.060,.620,.045,railhead)
  sleepers=Batch('Concrete sleepers '+w['id'],stone);plates=Batch('Fastening baseplates '+w['id'],railmat);clips=Batch('Pandrol clips '+w['id'],black)
  total=0
  for a,b in zip(pts,pts[1:]):
   va=Vector(a);vb=Vector(b);v=vb-va;l=v.length;d=v.normalized();ang=math.atan2(v.y,v.x)
   for k in range(math.ceil(total/.65),math.floor((total+l)/.65)+1):
    f=k*.65-total;p=va+d*f;sleepers.box((p.x,p.y,.36),(.24,2.75,.18),ang)
    for side in [-1,1]:
     q=p+Vector((-d.y,d.x))*.868*side;plates.box((q.x,q.y,.465),(.30,.23,.025),ang)
     for fside in [-1,1]:
      r=q+Vector((-d.y,d.x))*.085*fside;clips.box((r.x,r.y,.50),(.12,.045,.055),ang)
   total+=l
  sleepers.finish();plates.finish();clips.finish()
# Turnout hardware follows shared branch points; continuous parent/branch rails above carry routes.
collection('07 | TURNOUTS • blades frogs motors checkrails')
switch_count=0
for p,connections in nodes.items():
 if len(connections)<3:continue
 switch_count+=1;x,y=p
 cube('Point machine '+str(switch_count),(x,y+2.15,.5),(1.25,.60,.45),steel)
 cube('Point machine lid',(x,y+2.15,.74),(1.31,.64,.05),black)
 beam('Point drive linkage',(x,y+2,.45),(x,y,.45),.045,steel)
 for pts,wid in connections[:3]:
  if (Vector(pts[0])-Vector(p)).length<.1:q=pts[min(1,len(pts)-1)]
  else:q=pts[-2]
  d=(Vector(q)-Vector(p)).normalized();per=Vector((-d.y,d.x))
  for side in [-1,1]:
   a=Vector(p)+d*.6+per*(.70*side);b=Vector(p)+d*10+per*(.84*side)
   strip('Tapered switch blade '+str(switch_count),[a,b],.034,.61,.065,railhead)
   a=Vector(p)+d*13+per*(.69*side);b=a+d*4
   strip('Turnout check rail '+str(switch_count),[a,b],.055,.61,.07,railhead)
  a=Vector(p)+d*16
  prism('Cast manganese crossing nose '+str(switch_count),[(a.x,a.y),(a.x+d.x*3+per.x*.10,a.y+d.y*3+per.y*.10),(a.x+d.x*3-per.x*.10,a.y+d.y*3-per.y*.10)],.53,.645,railhead)
 for k in range(6):cube('Point machine conduit',(x-2+k*.6,y+2.15,.28),(.55,.15,.15),stone)
# Buffers only at actual mapped dead-end tracks, no train stock.
for p,connections in nodes.items():
 if len(connections)!=1:continue
 pts,wid=connections[0]
 if not (-350<p[0]<740):continue
 if not any(w['id']==wid and w['tags'].get('service') in ['siding','yard'] for w in W):continue
 q=pts[1] if (Vector(pts[0])-Vector(p)).length<.1 else pts[-2];d=(Vector(p)-Vector(q)).normalized();per=Vector((-d.y,d.x));a=Vector(p)
 for s in [-1,1]:
  b=a+per*.9*s;beam('Buffer-stop steel triangular brace',(b.x-d.x*1.8,b.y-d.y*1.8,.3),(b.x,b.y,1.4),.18,railmat)
 beam('Buffer beam',(a.x-per.x*1.35,a.y-per.y*1.35,1.35),(a.x+per.x*1.35,a.y+per.y*1.35,1.35),.28,red)
 for s in [-1,1]:
  b=a+per*.86*s;cube('Buffer impact pad',(b.x,b.y,1.35),(.4,.32,.38),black)
(P/'track_network.json').write_text(json.dumps({'origin_lat':9.9693,'origin_lon':76.29105,'extent_x_m':[-510,850],'gauge_m':1.676,'paths':trackledger,'shared_node_turnout_groups':switch_count},indent=2))
print('ERS TRACK GEOMETRY COMPLETE',len(paths),'paths',switch_count,'turnout groups',flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_checkpoint.blend'))
collection('08 | PLATFORM CANOPIES • full span trusses gutters lights')
platform_specs=[('1',19,-190,395,5.8),('2 / 3',48,-155,410,7.2),('4 / 5',68,-150,390,7.0),('6',98,-130,110,5.2)]
for label,y,lo,hi,width in platform_specs:
 for x in range(lo,hi,12):
  if abs(x+60)<15 or abs(x-100)<15:continue
  cube('Canopy pad PF'+label,(x,y,1.35),(.6,.6,.35),stone)
  beam('Canopy riveted steel column PF'+label,(x,y,1.5),(x,y,4.85),.14,steel)
  for s in [-1,1]:
   beam('Open canopy diagonal',(x,y,3.75),(x,y+s*width*.43,4.9),.07,steel)
   beam('Canopy roof slope',(x,y,5.5),(x,y+s*width/2,4.85),.10,steel)
   beam('Canopy bottom chord',(x,y,4.85),(x,y+s*width/2,4.85),.09,steel)
   for f in [.25,.5,.75]:beam('Canopy truss web',(x,y+s*width*.5*f,4.85),(x,y+s*width*.5*(f-.15),5.5-.65*(f-.15)),.04,steel)
  cube('Suspended fluorescent fitting',(x,y,4.65),(1.4,.16,.085),cream)
  if x%24==lo%24:fan(x,y,4.35)
 for a,b in [(lo,-78),(-40,82),(122,hi)]:
  if b<=a:continue
  for side in [-1,1]:
   o=corrugated('Long corrugated canopy PF'+label,(a+b)/2,y+side*width*.25,5.175,b-a,width/2+.18,roof);o.rotation_euler[0]=-side*math.atan(.65/(width/2))
  for sy in [-1,1]:tube('Continuous gutter PF'+label,[(a,y+sy*width*.52,4.83),(b,y+sy*width*.52,4.83)],.08,steel)
  for off in [-.4,0,.4]:beam('Canopy purlin',(a,y+width*off,5.5-abs(off)*1.3),(b,y+width*off,5.5-abs(off)*1.3),.075,steel)
 for x in range(lo,hi,36):
  tube('Rainwater downpipe',[(x,y+width*.50,4.83),(x,y+.28,4.6),(x,y+.28,1.21)],.05,steel)
  bench(x+4,y,1.18,2.6)
  cyl('Lidded red waste bin',(x+7,y+.7,1.65),.24,.86,red,16);cyl('Waste bin top',(x+7,y+.7,2.10),.26,.055,black,16)
  cube('Platform number board',(x,y,3.95),(1.05,.11,.72),blue)
  text('Platform numbers '+label,label,(x,y-.065,3.78),.38,cream)
 for x in [lo+8,hi-8]:
  cube('Station name board',(x,y,2.92),(4,.12,1.6),yellow)
  sign('ERS multilingual platform sign',x,y-.07,2.92,3.88,1.48,'platform_name')
  for xx in [x-1.85,x+1.85]:cube('Nameboard pointed post',(xx,y,2.27),(.12,.14,2.2),yellow)
 for x in range(lo+16,hi-15,24):
  cyl('Coach-position pole',(x,y-1.25,2.5),.035,2.6,steel,8)
  cube('Coach position backing',(x,y-1.25,3.60),(.55,.06,.7),white)
  text('Coach position index',str(1+(x-lo)//24),(x,y-1.29,3.48),.32,blue)
 # tactile route runs centrally inside platform, repeated concrete slab detail.
 for x in range(lo,hi,3):cube('Platform transverse slab joint',(x,y,1.164),(.012,width,.004),black)
 for x in range(lo,hi,80):
  cube('Drinking-water cabinet',(x+15,y,1.83),(1.6,.7,1.3),white)
  cube('Drinking-water drip tray',(x+15,y-.5,1.65),(1.6,.45,.1),steel)
  for dx in [-.45,0,.45]:tube('Drinking-water tap',[(x+15+dx,y-.4,2.2),(x+15+dx,y-.6,2.2),(x+15+dx,y-.6,2.10)],.024,steel)
  text('Water cabinet legend','DRINKING WATER',(x+15,y-.365,2.28),.15,blue)
# Platform kiosks are properly stocked, detailed four-sided assemblies.
collection('09 | KIOSKS AND PLATFORM EQUIPMENT')
def kiosk(x,y):
 cube('Catering kiosk floor',(x,y,1.25),(3.6,3,.16),stone)
 cube('Catering stall rear',(x,y+1.40,2.6),(3.6,.12,2.7),green)
 for xx in [x-1.72,x+1.72]:cube('Kiosk corner pier',(xx,y,2.65),(.17,2.9,2.8),green)
 cube('Kiosk serving counter',(x,y-1.4,1.85),(3.5,.20,1.3),green)
 cube('Yellow counter top',(x,y-1.45,2.53),(3.7,.5,.1),yellow)
 cube('Kiosk fascia',(x,y-1.48,3.75),(3.8,.14,.55),green)
 sign('Catering fascia art',x,y-1.57,3.75,3.65,.5,'catering')
 corrugated('Kiosk roof',x,y,4.15,4,3.5,roof)
 for z in [2.0,2.4,2.8,3.2]:
  cube('Merchandise shelf',(x,y+1.05,z),(3.2,.50,.05),yellow)
  for k in range(13):cube('Packaged goods',(x-1.42+k*.23,y+.95,z+.16),(.18,.18,.28),[yellow,cream,red,blue][k%4])
 for k in range(10):
  cyl('Water bottles',(x-1.35+k*.3,y-.6,2.82),.075,.43,glass,10);cyl('Bottle caps',(x-1.35+k*.3,y-.6,3.05),.065,.045,blue,10)
for x,y in [(6,48),(250,48),(15,68),(245,68),(-96,98),(75,19)]:kiosk(x,y)
# Physical pedestrian bridges and stairs to each actual platform, open landing gates.
collection('10 | FOOTBRIDGES • traversable stairs and landings')
for bx in [-60,100]:
 cube('Footbridge deck',(bx,59,7.7),(3.6,94,.24),steel)
 for sy in [-1,1]:
  xx=bx+sy*1.75
  for yy in range(12,107,4):beam('Bridge lattice upright',(xx,yy,7.8),(xx,yy,10.3),.12,steel)
  for yy in range(12,103,4):
   # leave stair landing openings at each platform
   if sy==1 and any(abs(yy-p)<4 for p in [19,48,68,98]):continue
   beam('Bridge X lattice',(xx,yy,7.8),(xx,yy+4,10.2),.085,steel);beam('Bridge reverse X lattice',(xx,yy,10.2),(xx,yy+4,7.8),.085,steel)
  for z in [7.85,10.25]:
   sections=[(12,17.5),(20.5,46.5),(49.5,66.5),(69.5,96.5),(99.5,106)] if sy==1 and z<8 else [(12,106)]
   for a,b in sections:beam('Bridge longitudinal beam',(xx,a,z),(xx,b,z),.14,steel)
 corrugated('Pedestrian bridge roof',bx,59,10.45,4.25,95,roof)
 for yy in [19,48,68,98]:
  for xx in [bx-1.55,bx+1.55]:beam('Footbridge steel support',(xx,yy,1.18),(xx,yy,7.55),.19,steel)
  start=bx+1.8;end=bx+16;steps=38
  for i in range(steps):
   x=start+(end-start)*(i+.5)/steps;z=7.7-(7.7-1.18)*(i+1)/steps
   cube('Stair concrete tread',(x,yy,z),((end-start)/steps+.012,2.5,.11),stone)
   cube('Stair red riser',(x-.17,yy,z+.08),(.045,2.5,.17),red)
   cube('Stair anti-slip nosing',(x-.16,yy,z+.063),(.045,2.5,.022),black)
  for side in [-1,1]:
   y=yy+side*1.3
   beam('Stair side stringer',(start,y,7.5),(end,y,1),.20,steel)
   beam('Stair accessible handrail',(start,y,8.78),(end,y,2.26),.055,steel)
   beam('Stair lower guard',(start,y,8.25),(end,y,1.73),.04,steel)
   for i in range(20):
    t=i/19;x=start+(end-start)*t;z=7.7-6.52*t;beam('Stair baluster',(x,y,z),(x,y,z+1.08),.04,steel)
   mesh('Blue stair hood',[(start,yy,10.35),(end+.6,yy,3.6),(end+.6,y+side*.25,3.2),(start,y+side*.25,9.95)],[(0,1,2,3)],roofblue)
   for i in range(6):
    t=i/5;x=start+(end-start)*t;z=7.7-6.52*t;beam('Stair hood stanchion',(x,y,z),(x,y,z+2.32),.065,steel)
# East entrance footprint read from OSM, historical ticket/waiting functions documented NTCA2005–06.
collection('11 | EAST ENTRY • reconstructed booking and waiting hall')
ex=0;ey=111
cube('East entrance floor',(ex,ey,1.02),(62,18.4,.25),floor)
cube('East platform doorway threshold',(0,101.8,1.08),(5,1.1,.16),stone)
for x in [-31,31]:wall_door('East entrance side wall',x,ey,18.4,3.8,2.2,'y',z=1.1)
for x in [-24,-12,0,12,24]:
 cube('East frontage pier',(x,120,3.1),(.50,.45,4.0),white)
 cube('East facade red base',(x,120,1.55),(.55,.48,.85),red)
wall_door('East platform wall',0,102,62,3.8,5,z=1.1)
cube('East frontage lintel',(0,120,5.08),(62.5,.5,.55),white)
cube('East terminal blue fascia',(0,120.3,4.45),(63,.25,.55),blue)
cube('East terminal removable roof',(0,111,5.5),(63,19.2,.25),white)
# signage faces east outward
for i,t in enumerate(['en','hi','ml']):
 o=sign('East entrance identity',-19+i*19,120.45,4.45,18,.5,'entry_'+t);o.rotation_euler[2]=math.pi
for x in [-23,-17,-11]:
 desk(x,107,1.15);cube('East booking counter',(x,109,1.75),(4.8,.35,1.25),red)
 cube('East counter granite',(x,109,2.4),(5,.55,.08),black)
 for xx in [x-2.35,x+2.35]:cube('Booking window frame',(xx,109,3),(.05,.08,1.2),steel)
 text('East booking identification','TICKETS',(x,109.12,3.35),.30,blue)
for x in [4,12,20]:
 for y in [106,110,114]:bench(x,y,1.14,4.8)
for x in [-24,-12,0,12,24]:fan(x,111,4.6)
text('East waiting hall identity','EAST ENTRY • WAITING HALL',(13,102.14,4.3),.48,blue)
cube('East forecourt',(0,124,.05),(90,15,.2),stone)
# Gentle entrance ramp and handrails.
mesh('East entry ramp',[(-4,120,1.15),(4,120,1.15),(4,132,.18),(-4,132,.18)],[(0,1,2,3)],stone)
for side in [-1,1]:beam('East ramp handrail',(side*4,120,2.15),(side*4,132,1.18),.055,steel)
# OHE on each actual electrified mapped centreline, with sag/dropper geometry.
collection('12 | OHE NETWORK • masts wires insulators')
for wid,pts,tags in paths:
 if tags.get('electrified')!='contact_line':continue
 tube('25kV contact wire '+wid,[(x,y,6.2) for x,y in pts],.012,railmat)
 dist=0
 for a,b in zip(pts,pts[1:]):
  va=Vector(a);v=Vector(b)-va;l=v.length
  if l<.1:continue
  for k in range(math.ceil(dist/48),math.floor((dist+l)/48)+1):
   p=va+v*((k*48-dist)/l);x,y=p
   if abs(x+60)<5 or abs(x-100)<5:continue
   # Narrow lattice masts placed away from running gauge.
   my=y+2.75
   cube('OHE foundation',(x,my,.6),(.65,.7,1.0),stone)
   for dx in [-.11,.11]:beam('OHE mast chord',(x+dx,my,.9),(x+dx,my,8.7),.075,steel)
   for z in [1.5,2.5,3.5,4.5,5.5,6.5,7.5]:beam('OHE lattice diagonal',(x-.11,my,z),(x+.11,my,z+.9),.035,steel)
   beam('OHE cantilever',(x,my,7.6),(x,y,7.5),.065,steel);beam('OHE cantilever brace',(x,my,8.5),(x,y,7.5),.045,steel)
   for z in [7.1,7.17,7.24,7.31,7.38]:cyl('Brown porcelain insulator',(x,y,z),.085,.04,wood,12)
  for k in range(math.ceil(dist/6),math.floor((dist+l)/6)+1):
   p=va+v*((k*6-dist)/l);tube('Catenary dropper',[(p.x,p.y,6.2),(p.x,p.y,6.9)],.009,railmat)
  # messenger retains sag in each map segment
  tube('Sagged messenger '+wid,[(a[0]+v.x*i/12,a[1]+v.y*i/12,7.2-.30*math.sin(math.pi*i/12)) for i in range(13)],.016,railmat)
  dist+=l
# Signals, cable cabinets, troughs and drains distributed through actual yard.
collection('13 | SIGNALS DRAINAGE AND SERVICES')
for x,y in [(-180,27),(-160,41),(-155,61),(-135,79),(-255,89),(415,25),(438,39),(413,61),(390,77),(105,93),(-340,44),(610,40)]:
 cube('Signal concrete footing',(x,y,.35),(.8,.8,.6),stone);cyl('Signal steel pole',(x,y,2.5),.085,4.3,steel,12)
 cube('Three aspect signal head',(x,y,4.2),(.5,.26,1.45),black,.06)
 for dz,m in [(-.4,green),(0,yellow),(.4,red)]:
  o=cyl('Signal lens',(x,y-.15,4.2+dz),.12,.035,m,20);o.rotation_euler[0]=math.pi/2
  cube('Signal sun hood',(x,y-.23,4.36+dz),(.30,.30,.055),black)
 for z in [1,1.4,1.8,2.2,2.6,3,3.4]:beam('Signal access ladder rung',(x-.25,y+.15,z),(x+.25,y+.15,z),.035,steel)
 for dx in [-.25,.25]:beam('Signal ladder upright',(x+dx,y+.15,.7),(x+dx,y+.15,3.8),.045,steel)
for x in [-200,-120,10,95,190,320,445,590]:
 for y in [12,108]:
  cube('Relay cabinet base',(x,y,.45),(1.4,.85,.55),stone)
  cube('Relay cabinet',(x,y,1.44),(1.1,.65,1.5),white)
  cube('Relay cabinet door',(x,y-.335,1.44),(1.0,.035,1.38),cream)
  for z in [1.7,1.8,1.9,2.0]:cube('Relay cabinet louvre',(x,y-.36,z),(.7,.025,.025),black)
  cube('Relay door lock',(x+.35,y-.38,1.35),(.025,.04,.12),steel)
for y in [11,106]:
 cube('Cable trough concrete',(110,y,.13),(1000,.5,.28),stone)
 for x in range(-385,610,2):cube('Cable trough lid joint',(x,y,.278),(.02,.5,.016),black)
 tube('Blue platform service water main',[(-190,y,.6),(410,y,.6)],.055,roofblue)
 for x in range(-180,410,30):tube('Water hydrant standpipe',[(x,y,.6),(x,y,1.2),(x,y+.3,1.2)],.04,roofblue)
for y in [4,115]:
 cube('Open storm drainage channel',(110,y,-.03),(1050,1,.18),black)
 for dy in [-.55,.55]:cube('Storm drain raised sidewall',(110,y+dy,.08),(1050,.18,.42),stone)
 for x in range(-400,635,5):cube('Drain crossing grate',(x,y,.25),(.6,1,.035),steel)
# Tropical boundary context: perimeter fence and deliberately modest low-rise surroundings.
collection('14 | BOUNDARIES AND TROPICAL SURROUNDS')
for y in [-21,121]:
 for x in range(-400,700,10):
  if -60<x<70 or (y==121 and 495<x<545):continue
  cube('Boundary concrete post',(x,y,1),(.14,.14,2),white)
  for z in [.4,.8,1.2,1.6,2]:beam('Boundary wire',(x,y,z),(x+10,y,z),.012,steel)
for x in range(-350,670,55):
 for y in [-52,153]:
  h=random.uniform(6,10);xx=x+random.uniform(-5,5)
  tube('Coconut palm trunk',[(xx,y,0),(xx+.4,y,h*.5),(xx+.8,y,h)],.16,wood)
  for j in range(10):
   a=j*math.tau/10;tip=(xx+.8+4*math.cos(a),y+4*math.sin(a),h-1.6)
   verts=[(xx+.8,y,h),(xx+.8+2*math.cos(a-.15),y+2*math.sin(a-.15),h+.4),tip,(xx+.8+2*math.cos(a+.15),y+2*math.sin(a+.15),h+.4)]
   mesh('Palm drooping frond',verts,[(0,1,2,3)],leaf)
# Service building with real workshop benches/shelves next to sidings.
collection('15 | YARD MAINTENANCE WORKSHOP INTERIOR')
cube('Workshop slab',(520,123,.2),(30,14,.35),stone)
for x in [505,535]:wall_door('Workshop gable',x,123,14,4,3,'y',z=.4)
wall_door('Workshop frontage',520,116,30,4,4,z=.4)
cube('Workshop rear wall',(520,130,2.4),(30,.20,4),white)
corrugated('Workshop roof',520,123,4.6,31,15,roof)
for x in [510,517,524,531]:
 desk(x,127,.4)
 for z in [1.1,1.8,2.5,3.2]:
  cube('Workshop storage rack',(x,129,z),(4,.7,.08),steel)
  for dx in [-1.4,-.5,.5,1.4]:cube('Maintenance spares bin',(x+dx,129,z+.2),(.65,.5,.35),[blue,red,yellow][int(x)%3])
text('Workshop identification','PERMANENT WAY / STORES',(520,115.87,3.6),.6,blue)
# Move inferred workshop outside every mapped track with audited5m clearance.
for ob in COL.objects:ob.location.y+=45
cube('Workshop approach paving',(520,166,.06),(42,24,.16),stone)
# Presentation and editable full asset checkpoint.
collection('90 | REVIEW CAMERAS AND LIGHTING')
world=bpy.data.worlds.new('Kerala soft daylight');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.73,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
bpy.ops.object.light_add(type='SUN',location=(0,0,50));o=move(bpy.context.object);o.name='Tropical afternoon';o.rotation_euler=(.48,-.35,-.6);o.data.energy=2.5;o.data.angle=.12
for x,y,z,size,energy in [(-5,0,5.8,12,1500),(-24,0,3.5,10,650),(20,1,3.3,12,950),(49,0,3.5,10,850),(0,111,5.1,40,2000),(520,168,4.3,20,1300)]:
 bpy.ops.object.light_add(type='AREA',location=(x,y,z));o=move(bpy.context.object);o.name='Interior broad ceiling fill';o.data.energy=energy;o.data.shape='DISK';o.data.size=size
# Cameras use real eye heights and aerial coverage; no hidden trains/stock.
def camera(name,loc,target,lens=38,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=move(bpy.context.object);o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=4000
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
cams=[camera('01_West_architecture',(74,-92,18),(6,0,3.5),48),camera('02_Ticket_hall',(-12,-3.7,2.1),(-3,4.8,2.1),23),camera('03_Waiting_hall',(-31,-3,1.9),(-20,3,1.1),26),camera('04_Platform_concourse',(-4,44.5,2.85),(45,48,3.0),30),camera('05_Track_turnouts',(435,70,6),(500,49,.4),39),camera('06_Full_station_aerial',(950,-670,700),(130,55,0),48),camera('07_Full_yard_plan',(155,55,1100),(155,55,0),35,1430),camera('08_East_waiting_hall',(27,118,2.8),(-10,109,2.8),26),camera('09_Toilet_interior',(56,-3.4,2.05),(45,3,1.7),23),camera('10_Footbridge_and_platform',(-33,49,3.2),(-62,58,7.5),24),camera('11_Service_workshop',(532,163,2.0),(514,173,1.7),24)]
scene.camera=cams[0];scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.5
scene['asset']='ERS full station v02: 2017 photo architecture + mixed-date mapped track plan + reconstructed interiors'
scene['survey_status']='No surveyed2017 as-built claim. Current OSM ways mixed dates; furnishings and turnout hardware reconstructed. See SOURCES and COVERAGE.'
scene['gauge_m']=1.676;scene['no_rolling_stock']=True;scene['coordinate_system']='X station-north, Y station-east, Z up, metres; mapped origin9.9693N76.29105E'
for o in scene.objects:
 if o.type=='MESH':o['asset_part']='ERS_FULL_V02'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
qa={'blender':bpy.app.version_string,'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'materials':len(bpy.data.materials),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'gauge_m':1.676,'rail_head_width_m':.060,'rail_centres_m':1.736,'platform_polygon_count':len(platforms),'platform_faces':6,'mapped_track_paths':len(paths),'turnout_groups':switch_count,'rolling_stock':0,'render_threads':4,'render_samples':24}
(P/'qa_build.json').write_text(json.dumps(qa,indent=2));print('ERS FULL SOURCE SAVED',json.dumps(qa),flush=True)
if '--render' in sys.argv:
 for cam in cams:
  scene.camera=cam;scene.render.filepath=str(P/'renders'/(cam.name+'.png'));bpy.ops.render.render(write_still=True)
if '--export' in sys.argv:
 bpy.ops.object.select_all(action='DESELECT')
 for o in scene.objects:
  if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(P/'exports'/'ERS_full_station_v02.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
scene.camera=cams[0];bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
