"""TVC heritage kit. Blender 4.3+. All lengths metres; photo-inferred, not survey."""
import bpy, math, random, os, json, sys
from mathutils import Vector
from pathlib import Path
random.seed(1931)
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
current=None
def collection(name):
 global current
 current=bpy.data.collections.new(name); scene.collection.children.link(current); return current
def link(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 current.objects.link(o); return o
def mat(name,col,rough=.65,metal=0,noise=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*col,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 if noise:
  t=n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value=noise; t.inputs['Detail'].default_value=3
  ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*(v*.65 for v in col),1); ramp.color_ramp.elements[1].color=(*(min(v*1.2,1) for v in col),1)
  l.new(t.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],p.inputs['Base Color'])
  b=n.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.25; b.inputs['Distance'].default_value=.045; l.new(t.outputs['Fac'],b.inputs['Height']); l.new(b.outputs[0],p.inputs['Normal'])
 return m
stone=[mat('Granite variation %02d'%i,(.14+i*.014,.15+i*.014,.145+i*.014),noise=8) for i in range(7)]
mortar=mat('Recessed grey mortar',(.105,.115,.11),noise=24)
cream=mat('Weathered ivory limework',(.66,.63,.52),noise=5)
shutter=mat('Aged painted timber',(.47,.46,.37),noise=18)
dark=mat('Unlit aperture',(.025,.035,.037))
roof=mat('Corrugated charcoal sheet',(.12,.15,.16),.72,.22,8)
steel=mat('Painted canopy steel',(.42,.48,.46),.55,.32,7)
red=mat('Raised red enamel lettering',(.48,.025,.035),.35,.15)
yellow=mat('Station board ochre',(.86,.48,.025),noise=10)
black=mat('Iron and rubber',(.025,.03,.03),.65)
asphalt=mat('Road aggregate',(.12,.135,.14),noise=45)
paving=mat('Warm paving',(.43,.38,.31),noise=35)
terracotta=mat('Platform tactile tile',(.44,.21,.14),noise=32)
white=mat('Faded white',(.78,.77,.66),noise=9)
glass=mat('Glass blue green',(.11,.23,.24),.19,.3)
leaf=mat('Tropical foliage',(.075,.20,.06),noise=6)
wood=mat('Bark',(.18,.12,.065),noise=16)

def cube(name,loc,scale,material,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=link(bpy.context.object); o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:o.data.materials.append(material)
 if bev:
  m=o.modifiers.new('Edge wear bevel','BEVEL'); m.width=bev; m.segments=2
 return o

def cyl(name,a,b,r,material,verts=12):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=link(bpy.context.object); o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); return o

def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); current.objects.link(o); o.data.materials.append(material); return o

def text(name,body,loc,size,material,width=None):
 cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.size=size; cu.extrude=.018; cu.bevel_depth=.003
 try:cu.font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf')
 except:pass
 o=bpy.data.objects.new(name,cu); current.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); cu.materials.append(material); bpy.context.view_layer.update()
 if width and o.dimensions.x>0:o.scale.x=width/o.dimensions.x
 return o

def arch_poly(x,bottom,spring,r,y):
 return [(x-r,y,bottom),(x+r,y,bottom)]+[(x+r*math.cos(t*math.pi/32),y,spring+r*math.sin(t*math.pi/32)) for t in range(33)]
def arch_face(name,x,y,bottom,spring,r,material):
 vs=arch_poly(x,bottom,spring,r,y);return mesh(name,vs,[tuple(range(len(vs)))],material)
def ring(name,x,y,spring,r,t,material):
 vs=[]
 for i in range(49):
  a=i*math.pi/48
  for rr in (r,r+t):vs.append((x+rr*math.cos(a),y,spring+rr*math.sin(a)))
 return mesh(name,vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(48)],material)
def in_open(x,z,opening,margin=0):
 cx,b,s,r=opening; dx=abs(x-cx)
 return z>=b-margin and dx<r+margin and (z<=s or dx*dx+(z-s)**2<(r+margin)**2)
def facade(name,cx,width,height,y,openings):
 # True apertures in structural wall, with inset interior beyond.
 wall=cube(name+' structural masonry',(cx,y+.26,height/2),(width,.52,height),mortar)
 for idx,(x,b,s,r) in enumerate(openings):
  pts=arch_poly(x,b,s,r,y-1); n=len(pts); vs=pts+[(a,y+1.2,c) for a,bb,c in pts]
  fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  cut=mesh('TEMP_arch_cut',vs,fs,dark)
  bpy.context.view_layer.objects.active=wall; md=wall.modifiers.new('Arched opening %d'%idx,'BOOLEAN'); md.operation='DIFFERENCE'; md.object=cut; bpy.ops.object.modifier_apply(modifier=md.name); bpy.data.objects.remove(cut,do_unlink=True)
 # Individually modelled dressed stones; clip boundary blocks by omitting stones that touch an opening.
 for row in range(int(height/.235)):
  z=.12+row*.235
  x=cx-width/2-.5*(row%2)
  while x<cx+width/2:
   w=random.uniform(.52,.91); lo=max(x,cx-width/2); hi=min(x+w,cx+width/2); xx=(lo+hi)/2
   if hi-lo>.07 and not any(any(in_open(px,pz,op,.025) for px in (lo,xx,hi) for pz in (z-.11,z+.11)) for op in openings):
    cube(name+' granite course %02d'%row,(xx,y-.017-random.uniform(0,.018),z),(hi-lo-.022,.095,.211),random.choice(stone),.022)
   x+=w
 for idx,(x,b,s,r) in enumerate(openings):
  ring(name+' arch surround',x,y-.09,s,r,.22,cream)
  for side in (-1,1):cube(name+' reveal',(x+side*(r+.11),y-.05,(b+s)/2),(.22,.18,s-b),cream,.025)
  cube(name+' sill',(x,y-.12,b-.07),(r*2+.48,.36,.14),cream,.025)
  arch_face(name+' recess',x,y+.48,b,s,r,dark)
 return wall

def window(x,y,b=6.05,s=10.85,r=.83):
 # Rectangular shutter pairs and curved fan-light, as observed on the raised tower.
 arch_face('Arched timber fanlight',x,y+.1,b,s,r*.96,shutter)
 for z0,z1 in [(b+.12,b+2.65),(b+2.93,s+.03)]:
  count=4 if r>1 else 2; panel=2*r/count
  for j in range(count):
   xx=x-r+panel*(j+.5)
   cube('Timber shutter panel',(xx,y+.025,(z0+z1)/2),(panel-.05,.09,z1-z0),shutter,.018)
   for dx in (-panel/2+.045,panel/2-.045):cube('Shutter stile',(xx+dx,y-.045,(z0+z1)/2),(.065,.065,z1-z0),cream,.008)
   for zz in (z0+.055,z1-.055):cube('Shutter rail',(xx,y-.045,zz),(panel-.055,.07,.08),cream,.008)
   for k in range(int((z1-z0-.22)/.09)):
    o=cube('Individual louvre blade',(xx,y-.048,z0+.16+k*.09),(panel-.16,.095,.036),cream,.008); o.rotation_euler.x=.32
   for zz in (z0+.3,z1-.3):cube('Black hinge strap',(xx+panel*.28,y-.1,zz),(.09,.025,.065),black,.005)
 for dx in [-.45,0,.45]:
  if abs(dx)<r:cube('Fanlight upright',(x+dx,y-.05,s+.25),(.045,.06,.6),cream)

def cornice(cx,w,y,depth,h):
 for z,extra,hh,m in [(h-.95,.1,.2,cream),(h-.62,.18,.18,stone[1]),(h-.43,.27,.20,cream),(h-.2,.4,.22,cream),(h,.3,.12,stone[3])]:
  cube('Projecting stepped cornice',(cx,y+depth/2,z),(w+extra*2,depth+extra*2,hh),m,.025)
 cube('Roof parapet',(cx,y+depth/2,h+.2),(w,depth,.4),stone[2],.035)

def pavilion(cx,w,h,main=False):
 openings=[]
 xs=[cx-4.35,cx,cx+4.35] if main else [cx]
 for x in xs:openings.append((x,6.05 if main else 5.2,10.85 if main else 8.3,1.18 if x==cx and main else .83))
 openings.append((cx,.15,2.55,1.65 if main else 1.25))
 facade('Central pavilion' if main else 'Secondary pavilion',cx,w,h,0,openings)
 cube('Pavilion rear',(cx,7.7,h/2),(w,.55,h),stone[2])
 for side in (-1,1):
  cube('Pavilion side wall',(cx+side*(w/2-.25),4,h/2),(.5,8,h),stone[3])
 for x,b,s,r in openings[:-1]:window(x,0,b,s,r)
 for x in ([cx-w/2+.48,cx-2.5,cx+2.5,cx+w/2-.48] if main else [cx-w/2+.42,cx+w/2-.42]):
  cube('Full height pale pilaster',(x,-.16,(h-1.4)/2),(.99,.43,h-1.4),cream,.025)
  for z,ww,hh in [(.24,1.16,.48),(h-1.6,1.16,.14),(h-1.42,1.4,.23),(h-1.2,1.58,.16)]:cube('Pilaster base or capital',(x,-.19,z),(ww,.57,hh),cream,.025)
  for z in range(1,int(h-2)):cube('Ashlar joint on pilaster',(x,-.385,z),(.97,.008,.013),stone[4])
 cornice(cx,w,0,8,h)
 cube('Raised plinth',(cx,3.8,.10),(w+.5,8.4,.2),cream,.03)
 # Service conduits and drain pipes as seen on the heritage facade.
 for x in [cx-w/2+.1,cx+w/2-.1]:
  cyl('Rainwater pipe',(x,-.44,.3),(x,-.44,h-.5),.052,steel)
  for z in range(1,int(h),2):cube('Pipe clip',(x,-.48,z),(.17,.10,.045),black,.008)
 if main:
  cube('Rooftop nameboard',(cx,.15,h+1.01),(12.8,.17,.95),white,.025)
  text('TVC rooftop identity','THIRUVANANTHAPURAM CENTRAL',(cx,.045,h+.75),.60,red,12.15)
  for x in [-5,5]:cyl('Sign brace',(x,.3,h+.5),(x,2,h+.25),.035,black)
  cyl('Flagstaff',(cx,2,h+.35),(cx,2,h+4),.032,steel)

collection('01_HERITAGE_CENTRAL_3_BAY')
pavilion(0,14.4,14.9,True)
collection('02_GALLERIES_AND_END_PAVILIONS')
for sg in (-1,1):
 cx=sg*14.1; w=13.4
 ops=[(cx+d,.18,2.6,1.35) for d in (-4.45,0,4.45)]
 facade('Gallery lower arcade',cx,w,5.3,1.5,ops)
 cube('Gallery rear upper wall',(cx,6,7.1),(w,.3,3.6),cream)
 for x in [cx-5.8+i*1.93 for i in range(7)]:
  for dx in (-.15,.15):
   cyl('Paired veranda column',(x+dx,1.3,5.35),(x+dx,1.3,8.4),.09,cream)
   for z in (5.42,8.25):cube('Column collar',(x+dx,1.3,z),(.26,.27,.14),cream,.025)
  cube('Veranda column pedestal',(x,1.35,5.65),(.65,.6,.68),cream,.025)
 for z in (5.08,5.32):cube('Gallery stringcourse',(cx,1.38,z),(w,.5,.18),cream,.015)
 for x in [cx-w/2+.18+i*.25 for i in range(int(w/.25))]:cyl('Veranda baluster',(x,1.3,5.4),(x,1.3,6),.027,cream)
 cube('Veranda handrail',(cx,1.3,6.05),(w,.12,.13),cream,.02)
 # Sheet roof slopes towards forecourt.
 verts=[(cx-w/2-.25,.8,8.6),(cx+w/2+.25,.8,8.6),(cx+w/2+.25,6.8,10),(cx-w/2-.25,6.8,10)]
 mesh('Gallery sloping sheet roof',verts,[(0,1,2,3)],roof)
 for i in range(int(w/.16)+1):cyl('Gallery corrugation ridge',(cx-w/2+i*.16,.8,8.61),(cx-w/2+i*.16,6.8,10.01),.019,roof,6)
 cube('Gallery eaves gutter',(cx,.8,8.58),(w+.6,.17,.2),steel,.02)
 for x in [cx-3.9,cx,cx+3.9]:
  arch_face('Upper gallery window',x,5.82,6.2,7.5,.6,dark)
 pavilion(sg*24.05,6.5,11.4)

collection('03_FORECOURT_CONTEXT_GAME_ADJUSTED')
cube('Presentation ground',(0,5,-.19),(88,66,.25),paving,.08)
cube('Forecourt road',(0,-12,-.035),(80,13,.12),asphalt,.04)
cube('Footpath',(0,-3.4,.09),(65,4.8,.25),paving,.03)
for x in range(-32,33):cube('Alternating roadside kerb',(x,-5.8,.15),(.97,.26,.32),white if x%2 else black,.025)
for x in range(-31,32,3):
 cyl('Forecourt railing upright',(x,-4.9,.25),(x,-4.9,1.25),.035,black)
 for z in (.52,1.16):cyl('Railing horizontal',(x,-4.9,z),(x+3,-4.9,z),.032,black)
 for xx in (x+.75,x+1.5,x+2.25):cyl('Railing infill',(xx,-4.9,.5),(xx,-4.9,1.15),.019,black,8)
for x in range(-30,31,6):
 for yy in (-14,-17):cube('Road lane dash',(x,yy,.035),(2,.09,.018),white)
# Compact three-wheeler context models, separate editable pieces.
for x,y in [(-13,-8.2),(-8,-8.1),(10,-8.1),(15,-8.2),(21,-8.25)]:
 cube('Auto yellow lower body',(x,y,.64),(1.32,2.55,.70),yellow,.15)
 cube('Auto black passenger hood',(x,y+.35,1.54),(1.38,1.7,1.04),black,.22)
 cube('Auto windscreen',(x,y-.83,1.46),(1.14,.08,.58),glass,.08)
 cube('Auto nose',(x,y-1.21,.94),(1.18,.26,.50),yellow,.12)
 for dx in (-.48,.48):cube('Auto headlamp',(x+dx,y-1.36,.93),(.2,.035,.17),white,.05)
 for dx,dy in [(-.7,.72),(.7,.72),(0,-.86)]:
  cyl('Auto tyre',(x+dx-.08,y+dy,.36),(x+dx+.08,y+dy,.36),.29,black,20)
  cyl('Auto wheel hub',(x+dx-.09,y+dy,.36),(x+dx+.09,y+dy,.36),.13,steel,16)
 cube('Auto yellow registration',(x,y-1.38,.63),(.35,.025,.14),yellow,.02)
# Trees confined to side planting, no obstruction of facade.
for x,y in [(-30,-2),(30,-2),(-33,8),(33,7)]:
 cyl('Tree trunk',(x,y,0),(x+.18,y,5.2),.17,wood)
 for i in range(12):
  a=i*2.4; end=(x+math.cos(a)*random.uniform(1.2,2.3),y+math.sin(a)*random.uniform(1.2,2.3),random.uniform(4,6.3))
  cyl('Branch',(x,y,3.7),end,.047,wood)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=end); o=link(bpy.context.object); o.name='Foliage cluster'; o.scale=(1.2,.9,.55); o.data.materials.append(leaf)
 for dx in range(-2,3):cube('Planter edging',(x+dx*.5,y-1.5,.23),(.5,.18,.46),cream,.03)

collection('04_MODULAR_PLATFORM_CANOPY_DEMONSTRATOR')
# An independent 36 m demonstration strip, not a mapped yard or five-platform arrangement.
Y=19; L=36
cube('Platform module 36m',(0,Y,.34),(L,7,.68),paving,.03)
cube('Platform vertical edge',(0,Y-3.5,.28),(L,.16,.8),terracotta,.015)
for i in range(72):
 x=-L/2+.25+i*.5
 cube('Platform coping slab',(x,Y-3.35,.715),(.49,.48,.09),white,.009)
 cube('Tactile tile',(x,Y-2.87,.70),(.49,.42,.035),terracotta,.006)
 for k in range(5):cube('Tactile raised rib',(x,Y-3.03+k*.067,.726),(.44,.018,.019),cream,.004)
for x in range(-16,17,8):
 cube('Canopy concrete footing',(x,Y+.1,.92),(.72,.75,.45),cream,.035)
 for dx in (-.14,.14):cube('Canopy built-up column flange',(x+dx,Y,2.82),(.09,.3,4),steel,.009)
 cube('Canopy column web',(x,Y,2.82),(.3,.06,4),steel,.008)
 # Sloped Warren-like bracket copying visible reference character.
 A=(x,Y-3.25,5.85); B=(x,Y+3.25,4.65)
 cyl('Canopy sloping principal',A,B,.10,steel)
 cyl('Canopy bracket lower chord',(x,Y-3.25,5.37),(x,Y+3.25,4.3),.07,steel)
 for j in range(8):
  yy=Y-3.25+j*.8125; zz=5.85-j*.15
  cyl('Canopy triangular web',(x,yy,zz),(x,yy+.8125,zz-.63),.035,steel)
 for yy in (Y-1.8,Y+1.8):
  cyl('Canopy knee brace',(x,Y,3.8),(x,yy,5.25 if yy<Y else 4.62),.06,steel)
 for dx in (-.2,.2):
  for z in (1.15,4.5):cyl('Bolt head',(x+dx,Y-.19,z),(x+dx,Y-.24,z),.035,black,6)
 cube('Canopy fluorescent fitting',(x,Y-1.15,5.12),(1.1,.15,.12),white,.02)
verts=[(-L/2,Y-3.5,5.95),(L/2,Y-3.5,5.95),(L/2,Y+3.5,4.65),(-L/2,Y+3.5,4.65)]
mesh('Canopy roof sheet',verts,[(0,1,2,3)],roof)
for i in range(int(L/.18)+1):cyl('Canopy corrugation',(-L/2+i*.18,Y-3.5,5.97),(-L/2+i*.18,Y+3.5,4.67),.021,roof,6)
for yy in [Y-3.4,Y-1.6,Y,Y+1.7,Y+3.4]:
 zz=5.95-(yy-(Y-3.5))*1.3/7
 cube('Longitudinal purlin',(0,yy,zz-.12),(L,.1,.16),steel,.01)
for x in (-10,6):
 for yy in (Y-.1,Y+.45):cube('Station bench seat',(x,yy,1.2),(2.3,.16,.12),shutter,.03)
 for dx in (-.85,.85):cyl('Bench iron leg',(x+dx,Y+.12,.7),(x+dx,Y+.12,1.15),.045,black)
 cube('Bench back',(x,Y+.65,1.62),(2.3,.13,.53),shutter,.045)
# One illustrative broad-gauge straight track. Rail gauge measured standard, not yard survey.
for i in range(60):
 x=-18+i*.6; cube('Concrete sleeper',(x,Y-5.2,.14),(.22,2.7,.18),cream,.025)
for yy in (Y-5.2-.838,Y-5.2+.838):
 cube('Rail foot',(0,yy,.29),(L,.15,.025),steel,.005); cube('Rail web',(0,yy,.36),(L,.024,.14),steel); cube('Rail head',(0,yy,.44),(L,.068,.055),steel,.009)
cube('Ballast bed',(0,Y-5.2,.02),(L,3.6,.16),stone[2],.04)
# Yellow nameboard, intentionally independent of facade sign.
for x in (12,17.5):cube('Nameboard upright',(x,Y+1.8,2),(.16,.17,2.7),yellow,.025)
cube('Yellow TVC board',(14.75,Y+1.8,3.5),(5.9,.18,2.05),yellow,.035)
text('Platform name English','THIRUVANANTHAPURAM CENTRAL',(14.75,Y+1.688,3.04),.36,black,5.5)
text('Platform code','TVC',(14.75,Y+1.68,3.70),.62,black,1.2)
text('Module provenance label','36 m CANOPY STUDY',(14.75,Y+1.68,4.2),.20,black,3.7)

collection('05_PRESENTATION_CAMERAS_LIGHTING')
world=bpy.data.worlds.new('Kerala bright overcast');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.71,.82,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN',location=(0,-15,25));sun=link(bpy.context.object);sun.name='Warm daylight';sun.data.energy=2;sun.data.angle=.22;sun.rotation_euler=(math.radians(30),math.radians(-25),math.radians(-30))
bpy.ops.object.light_add(type='AREA',location=(5,-16,18));a=link(bpy.context.object);a.data.energy=1900;a.data.shape='DISK';a.data.size=18;a.rotation_euler=(Vector((0,0,6))-a.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,lens=48,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=link(bpy.context.object);o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
hero=cam('CAM_Hero',(37,-58,23),(0,2,6.6),48)
elev=cam('CAM_Elevation',(0,-70,8),(0,0,8),48,62)
detail=cam('CAM_Heritage_detail',(12,-24,12),(0,0,8.5),53)
canopy=cam('CAM_Canopy_detail',(24,7,7),(4,19,3.1),44)
scene.camera=hero;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=75
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene['README']='Photo-reconstructed November 2022 TVC heritage module. Metres, no surveyed dimensions. Read README.md. Canopy is detached study, not exact yard.'
scene['reference_era']='2022-11-14';scene['source_measured_station_dimensions']=False
# Packed files only procedural materials; fonts packed by Blender.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'TVC_heritage_2022.blend'))
metrics={'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'units':'metres','central_upper_front_bays':3,'station_specific_measured_dimensions':0,'blender':bpy.app.version_string}
(ROOT/'qa_geometry.json').write_text(json.dumps(metrics,indent=2))
if '--render' in sys.argv:
 for c,n in [(hero,'hero'),(elev,'elevation'),(detail,'heritage_detail'),(canopy,'canopy_detail')]:
  scene.camera=c;scene.render.filepath=str(ROOT/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
