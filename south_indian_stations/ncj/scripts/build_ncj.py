"""NCJ 2010 photo-informed architectural reconstruction. Blender 4.3+. Metres."""
import bpy, math, random, json, os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; random.seed(22)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.collections):
 if d.name!='Collection':bpy.data.collections.remove(d)
base=bpy.data.collections.get('Collection');base.name='00_SITE'
def collection(n):
 c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c);return c
cols={n:collection(n) for n in ['01_MAIN_2010_PHOTO','02_LEFT_VERANDA_2010_PHOTO','03_ANNEX_PHOTO_INFERRED','04_SIGNAGE','05_FORECOURT','06_PLATFORM_CONTEXT_NOT_SURVEYED','07_TRACK_CONTEXT','08_SET_DRESSING','09_LIGHTS_CAMERAS']};active=base
def group(n):
 global active;active=cols[n]
def assign(o,n,m):
 o.name=n
 for c in list(o.users_collection):c.objects.unlink(o)
 active.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def mat(n,c,rough=.7,metal=0,noise=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4;tex.inputs['Detail'].default_value=4
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*[a*(1-noise) for a in c],1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*c,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.018;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
 return m
peach=mat('2010 faded peach lime render',(.72,.37,.24),noise=.19);pink=mat('2010 salmon fascia',(.62,.28,.26),noise=.15);ivory=mat('Warm white painted concrete',(.84,.81,.69),noise=.13);grey=mat('Weathered concrete',(.32,.34,.32),noise=.23);dark=mat('Deep interior shadow',(.025,.034,.032));metal=mat('Painted charcoal steel',(.08,.105,.105),.47,.5);glass=mat('Dark blue window glass',(.075,.12,.13),.22,.45);rust=mat('Red oxide window frames',(.27,.12,.08),.53,.2);roof=mat('Aged zinc sheet',(.38,.43,.42),.65,.55,noise=.3);terracotta=mat('Veranda red oxide paving',(.42,.16,.09),noise=.22);asphalt=mat('Forecourt asphalt',(.12,.13,.125),noise=.4);yellow=mat('Auto ochre enamel',(.89,.52,.015),.3,.2);black=mat('Tyre rubber and vinyl',(.018,.022,.019),.8);white=mat('Paint line',(.8,.79,.7));red=mat('Rooftop English sign crimson',(.43,.035,.06),.38,.3);blue=mat('Tamil/Hindi rooftop blue',(.045,.13,.23),.4,.25);leaf=mat('Palm leaves',(.1,.25,.065),.8);trunk=mat('Palm bark',(.29,.22,.15),noise=.4);sand=mat('Ballast and dry ground',(.34,.29,.22),noise=.6);poster=mat('Generic period advertising ivory',(.78,.76,.65));teal=mat('Generic panel deep teal',(.06,.25,.2));gold=mat('Generic ornament brass',(.68,.44,.12),.33,.5)
def cube(n,loc,dim,m,bev=.025):
 x,y,z=[a/2 for a in dim];v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 o=mesh(n,v,f,m);o.location=loc
 if bev:
  b=o.modifiers.new('Soft architectural edges','BEVEL');b.width=bev;b.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);active.objects.link(o);o.data.materials.append(m);return o
def cyl(n,loc,r,depth,m,verts=16,rot=None):
 v=[(r*math.cos(i*2*math.pi/verts),r*math.sin(i*2*math.pi/verts),z) for z in [-depth/2,depth/2] for i in range(verts)]
 f=[tuple(range(verts-1,-1,-1)),tuple(range(verts,verts*2))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)]
 o=mesh(n,v,f,m);o.location=loc
 if rot:o.rotation_euler=rot
 return o
def beam(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf')
def text(n,body,loc,size,m,width=None,rot=(math.pi/2,0,0),fontpath=None):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.009;d.bevel_depth=.002;d.font=bpy.data.fonts.load(fontpath) if fontpath else font;o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=loc;o.rotation_euler=rot;d.materials.append(m);bpy.context.view_layer.update()
 if width and o.dimensions.x>width:o.scale.x*=width/o.dimensions.x
 return o
def corbel(x,y,z,scale=1):
 for k,(w,dep,h) in enumerate([(.48,.65,.25),(.68,.95,.25),(.92,1.24,.25)]):cube('Stepped corbel tier', (x,y,z+k*.25*scale),(w*scale,dep*scale,h*scale),ivory,.015)
def window(x,y,z,w=1.8,h=1.65):
 cube('Recessed window black reveal',(x,y+.025,z),(w+.2,.19,h+.2),dark,.015);cube('Glazing',(x,y-.1,z),(w,.04,h),glass,.004)
 for dx in [-w/2,0,w/2]:cube('Red-oxide mullion',(x+dx,y-.14,z),(.065,.08,h+.1),rust,.01)
 for dz in [-h/2,h/2,0]:cube('Window transom',(x,y-.15,z+dz),(w,.07,.055),rust,.005)
 for dx in [i*w/8-w/2 for i in range(1,8)]:cube('Security grille vertical',(x+dx,y-.23,z),(.018,.03,h),metal,.003)
 for dz in [-h*.33,h*.33]:cube('Security grille crossbar',(x,y-.24,z+dz),(w,.03,.024),metal,.004)
 cube('Cast window sill',(x,y-.21,z-h/2-.08),(w+.3,.48,.12),ivory)
def curved_fascia(n,x,w,y,z):
 # Quarter-circle-style rounded parapet visible on both January/October 2010 photos.
 pts=[(y+1.3-i*1.3/16,z+.72*math.sqrt(max(0,1-(i/16)**2))) for i in range(17)]
 pts += [(y,z-.1),(y+1.3,z-.1)]
 v=[(xx,yy,zz) for xx in [x-w/2,x+w/2] for yy,zz in pts];N=len(pts);f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh(n,v,f,ivory)
print('BUILD_MAIN',flush=True)
# Raised station base and main open entrance building.
group('01_MAIN_2010_PHOTO')
cube('Main building plinth',(0,4,.26),(37,18,.52),grey)
cube('Public veranda red oxide floor',(0,-2.7,.57),(36.5,6.8,.12),terracotta)
# Main street wall has true entrance gaps; interior behind is spatial, not a flat dark rectangle.
for x,w in [(-15.8,5.4),(-8.25,3.1),(8.25,3.1),(15.8,5.4)]:cube('Ground storey masonry piers',(x,.1,2.25),(w,.5,3.3),peach)
for x in [-12,-4.4,4.4,12]:cube('Entrance jamb',(x,0,2.25),(.45,.65,3.3),ivory)
cube('First floor spandrel',(0,.15,4.1),(36.2,.5,.6),peach)
cube('Upper storey backing wall',(0,.25,6.48),(36.2,.4,4.15),peach)
for x in [-15,-11,-7,-3,3,7,11,15]:window(x,-.02,6.45,1.4,2.1)
for x in [-17.9,17.9]:cube('End wall',(x,5,4.53),(.42,10,8),peach)
cube('Rear wall',(0,10,4.3),(36,.4,7.6),peach)
cube('Interior mezzanine floor',(0,5.3,4.2),(36,9.1,.24),grey)
cube('Interior floor',(0,5.3,.58),(36,9.2,.14),terracotta)
for x in [-13,-8,8,13]:cube('Internal pier',(x,5,2.4),(.42,.42,3.6),ivory)
# Door and ticketing details visible beneath the hanging panels.
for x in [-15.2,15.2]:
 window(x,-.18,2.25,1.6,1.65)
 cube('Ticket window counter',(x,-.63,1.52),(2,.72,.12),grey)
 text('Ticket plaque','TICKETS',(x,-.75,3.42),.23,blue,width=2)
for x in [-6.7,6.7]:
 for i in range(6):cube('Folded steel gate bar',(x+(i-2.5)*.07,.05,2.2),(.03,.12,2.9),metal,.005)
# Twelve slender columns, eleven principal bays, measured proportionally from photograph.
xs=[-16.5+i*3 for i in range(12)]
for x in xs:
 cube('Tall entrance column',(x,-4.4,4.48),(.36,.48,7.8),ivory,.025)
 cube('Column plinth darkened',(x,-4.4,1),(.4,.51,.85),grey,.012)
 corbel(x,-4.4,8.4)
 cube('Column front shallow flute',(x,-4.65,4.9),(.07,.022,6.4),grey,.004)
cube('Tall canopy soffit',(0,-2.25,9.18),(37,6.5,.35),ivory)
cube('Salmon entablature',(0,-5.33,9.28),(37.25,.45,.62),pink)
cube('White fascia lip',(0,-5.49,9.66),(37.6,.3,.24),ivory)
curved_fascia('Rounded roof silhouette',0,37.25,-5.35,9.74)
cube('Main roof slab',(0,4.4,9.26),(37,16.3,.26),grey)
for x in [-18.3,18.3]:cube('Roof side parapet',(x,3.8,9.67),(.22,17.1,.62),ivory)
cube('Rear parapet',(0,12.1,9.65),(37,.23,.6),ivory)
# Suspended advertisements are intentionally newly designed placeholders, not copied ads.
for i in range(11):
 x=-15+i*3
 cube('Replaceable period advertising panel',(x,-4.43,6.12),(2.55,.08,3.72),poster,.018)
 for xx in [x-1.3,x+1.3]:cube('Advertisement frame',(xx,-4.5,6.12),(.045,.05,3.8),metal,.005)
 cube('Teal lower panel',(x,-4.485,5.35),(2.42,.014,1.8),teal,0)
 text('Unbranded period panel top','SOUTH TAMIL NADU',(x,-4.51,7.53),.14,blue,width=2.15)
 text('Original ad placeholder','JEWELLERS',(x,-4.51,6.78),.26,blue,width=2.15)
 text('Ad footer','PERIOD DISPLAY',(x,-4.515,4.49),.105,blue,width=2.15)
 # Geometric jewellery-inspired rings, entirely newly drawn.
 for k in range(3):
  bpy.ops.mesh.primitive_torus_add(major_radius=.43-k*.065,minor_radius=.018,major_segments=36,minor_segments=8,location=(x,-4.53-k*.005,5.43),rotation=(math.pi/2,0,0));assign(bpy.context.object,'Original decorative ring',gold)
# Rooftop nameboards supported on paired small piers.
group('04_SIGNAGE')
for x,w,body,m,fp in [(-11.6,12.2,'NAGERCOIL JUNCTION',red,None),(1.55,10.7,'நாகர்கோவில் சந்திப்பு',blue,'/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf'),(12.15,8.7,'नागरकोविल जंक्शन',blue,'/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf')]:
 for dx in [-w*.35,w*.35]:cube('Rooftop board support',(x+dx,-2.65,10.42),(.15,.2,.7),ivory)
 cube('Rooftop nameboard',(x,-2.65,11.01),(w,.18,.91),ivory,.025)
 text('Rooftop station lettering',body,(x,-2.756,11.02),.72,m,width=w-.28,fontpath=fp)
beam('Photographed bare flagpole',(0,-2.2,9.5),(0,-2.2,15.2),.035,metal)
# Left lower two-storey veranda, clearly evidenced by side photograph.
group('02_LEFT_VERANDA_2010_PHOTO')
cube('Lower wing base',(-27.1,3,.28),(17.8,15,.56),grey)
cube('Lower wing building',(-27.1,4.1,3.99),(17.8,10,6.88),peach)
for x in [-34,-30.5,-27,-23.5,-20]:
 window(x,-.98,2.13,1.4,2.4);window(x,-.98,5.59,2.25,1.5)
 for z,h in [(2.14,3.0),(5.47,2.96)]:cube('Wing veranda column',(x,-3.8,z),(.27,.34,h),ivory);corbel(x,-3.8,z+h/2-.25,.66)
cube('Wing red oxide walk',(-27,-2.5,.64),(18.2,4.4,.14),terracotta)
cube('Wing first floor balcony',(-27,-2.3,3.8),(18.4,4.4,.23),ivory)
cube('Wing lower salmon fascia',(-27,-4.4,3.59),(18.5,.24,.48),pink)
cube('Wing roof canopy',(-27,-2.1,7.43),(18.5,5,.25),ivory)
cube('Wing upper fascia',(-27,-4.43,7.26),(18.6,.28,.4),pink)
curved_fascia('Wing rounded fascia',-27,18.5,-4.42,7.6)
for x in [-35.8,-18.2]:cube('Wing roof side parapet',(x,2.8,7.81),(.2,13.8,.6),ivory)
# Forecourt connection and secondary annex: footprint inferred, not exact.
group('03_ANNEX_PHOTO_INFERRED')
cube('Annex block',(-47.6,7.8,3.66),(17.7,9.4,6.2),peach)
for x in [-54,-49.5,-45,-40.5]:
 window(x,3.01,5,3.3,1.47)
 cube('Annex ground doorway',(x,2.98,1.9),(2.35,.12,2.55),dark)
for x in [-55.4,-53.6,-51.8,-50,-48.2,-46.4,-44.6,-42.8,-41,-39.2]:
 cube('Annex raised parapet fin',(x,7.8,7.1),(.18,9.5,.85),ivory)
for x in [-54,-51,-48,-45,-42,-39]:
 cube('Annex entrance post',(x,1.55,1.93),(.25,.3,2.76),ivory);corbel(x,1.55,3.2,.65)
cube('Annex porch canopy',(-47,2.05,3.87),(18.2,3.2,.23),ivory)
cube('Link covered walkway fascia',(-63.5,6.9,3.6),(14,.5,.6),pink)
cube('Link canopy',(-63.5,8,3.94),(14,3.3,.16),ivory)
for x in [-70,-67,-64,-61,-58]:cube('Link slender post',(x,6.9,2.1),(.2,.2,3.4),ivory)
# Forecourt pavement, ramps and striped curb.
group('05_FORECOURT')
cube('Asphalt forecourt',(-12,-19,-.08),(124,37,.2),asphalt,.08)
cube('Station footpath',(-10,-6.35,.24),(95,2.15,.44),grey)
for x in range(-56,39):cube('Forecourt red-white curb',(x,-7.48,.29),(.98,.2,.36),ivory if x%2 else pink,.025)
for i in range(2):cube('Entrance step',(0,-6.35-i*.48,.42-i*.14),(13,1.1,.16),terracotta)
# Wheelchair ramp along left veranda, visible rails supported by photo.
verts=[(-35,-6.3,.03),(-22,-6.3,.58),(-22,-4.75,.58),(-35,-4.75,.03),(-35,-6.3,0),(-22,-6.3,0),(-22,-4.75,0),(-35,-4.75,0)]
mesh('Access ramp',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3)],grey)
for y in [-6.3,-4.8]:
 for x in range(-35,-21,2):beam('Ramp upright',(x,y,(x+35)*.042),(x,y,1+(x+35)*.042),.024,metal)
 for z in [.5,1]:beam('Ramp handrail',(-35,y,z),(-22,y,z+.55),.027,metal)
for x in range(-61,45):cube('Black white parking island curb',(x,-24.5,.18),(.98,.3,.36),white if x%2 else black,.035)
cube('Pedestrian island',(-8,-25.6,.08),(106,2,.18),grey)
# Ground panel expansion joints and service drains.
for x in range(-54,39,3):cube('Footpath expansion joint',(x,-6.3,.468),(.016,2,.005),dark,0)
for x in [-15,14,31]:
 cube('Drain frame',(x,-7.83,.02),(1.5,.4,.055),metal)
 for j in range(12):cube('Drain slot',(x-.67+j*.12,-7.83,.052),(.055,.32,.015),dark,.005)
print('BUILD_PLATFORM',flush=True)
# Context platform is deliberately a short separable demonstration module.
group('06_PLATFORM_CONTEXT_NOT_SURVEYED')
cube('Partial platform module 84 m',(0,14.75,.41),(84,8.5,.82),grey)
cube('Red oxide platform surfacing',(0,14.75,.84),(84,8.5,.06),terracotta)
cube('White coping edge',(0,19.0,.82),(84,.45,.16),ivory)
cube('Safety line',(0,18.42,.885),(84,.12,.012),yellow,0)
for x in range(-40,43,2):cube('Coping joint',(x,19,.912),(.014,.45,.008),dark,0)
for x in range(-32,33,8):
 for y in [12.2,16.65]:
  cube('Canopy column foot',(x,y,1.0),(.5,.5,.3),grey);cube('Canopy steel column',(x,y,2.95),(.12,.14,4.2),metal,.01)
 beam('Canopy tie',(x,11.2,4.95),(x,18,4.95),.055,metal)
 beam('Canopy rafter',(x,11.2,4.95),(x,14.6,5.8),.055,metal);beam('Canopy rafter',(x,14.6,5.8),(x,18,4.95),.055,metal)
 for y in [12,13.2,14.6,16,17.2]:beam('Canopy truss web',(x,y,4.95),(x,14.6,5.8),.025,metal)
for y in [11.25,12.1,13.1,14.6,16.1,17.1,18]:
 z=5.82-abs(y-14.6)*.25;beam('Roof longitudinal purlin',(-35,y,z),(35,y,z),.05,metal)
# Actual corrugated mesh roof, two pitches.
for y0,y1 in [(10.9,14.6),(14.6,18.3)]:
 v=[];n=560
 for i in range(n+1):
  x=-35+i*70/n;wave=.035*math.cos(i*math.pi)
  for y in [y0,y1]:v.append((x,y,5.91-abs(y-14.6)*.25+wave))
 mesh('Corrugated canopy sheets',v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(n)],roof)
for x in [-24,0,24]:
 for dx in [-.95,.95]:cube('Platform bench leg',(x+dx,15,1.1),(.13,.55,.6),grey)
 for j in range(5):cube('Bench seat slat',(x,14.75+j*.11,1.42),(2.35,.085,.075),rust)
 for j in range(4):cube('Bench back slat',(x,15.32,1.7+j*.11),(2.35,.075,.085),rust)
for x in [-30,-14,14,30]:cube('Canopy fluorescent luminaire',(x,14.6,4.85),(1.1,.18,.11),ivory)
# Broad gauge illustrative straight track segment, no invented turnouts/yard.
group('07_TRACK_CONTEXT')
cube('Ballast bed',(0,21.6,.13),(91,4.15,.27),sand)
for x in [i*.64-45 for i in range(141)]:
 cube('PSC sleeper',(x,21.6,.28),(.25,2.7,.19),grey,.04)
 for y in [20.7295,22.4705]:
  cube('Rail fastening plate',(x,y,.394),(.18,.23,.05),metal,.012)
  for yy in [y-.09,y+.09]:cube('Rail clip',(x,yy,.434),(.075,.04,.04),rust,.008)
for y in [20.7295,22.4705]:
 cube('Rail foot',(0,y,.425),(92,.14,.025),metal,.006);cube('Rail web',(0,y,.482),(92,.016,.11),metal,.005);cube('Rail head',(0,y,.553),(92,.065,.036),metal,.008)
# Context props: original auto-rickshaw geometry, not a downloaded vehicle.
group('08_SET_DRESSING')
def auto(x,y,ang=0):
 before=set(bpy.data.objects)
 cube('Auto yellow floor',(0,0,.63),(1.32,2.36,.24),yellow,.12)
 cube('Auto front apron',(0,-.94,1.01),(1.2,.47,.66),yellow,.18)
 cube('Auto rear panel',(0,1.05,1.05),(1.3,.12,.9),yellow,.07)
 cube('Auto vinyl roof',(0,.24,1.97),(1.46,1.98,.21),black,.1)
 cube('Auto rear hood',(0,1.03,1.56),(1.37,.12,.7),black,.07)
 cube('Auto windscreen',(0,-.74,1.54),(1.11,.055,.55),glass,.07)
 for xx in [-.61,.61]:beam('Auto screen pillar',(xx,-.88,1.16),(xx,-.72,1.94),.042,metal);beam('Auto cabin upright',(xx,.9,.65),(xx,.9,1.96),.035,metal)
 for yy,xx in [(-1.04,0),(.83,-.66),(.83,.66)]:
  cyl('Auto tyre',(xx,yy,.42),.31,.16,black,24,(0,math.pi/2,0));cyl('Auto wheel hub',(xx+(.09 if xx>=0 else -.09),yy,.42),.13,.02,metal,20,(0,math.pi/2,0))
 for xx in [-.4,.4]:cube('Auto headlamp',(xx,-1.188,1.12),(.2,.027,.16),ivory,.06)
 cube('Auto passenger bench',(0,.62,1.0),(1.08,.45,.19),black,.1)
 cube('Auto registration plate',(0,-1.2,.79),(.42,.025,.14),yellow,.005)
 text('Auto plate','TN 74',(0,-1.222,.8),.07,black,width=.36)
 for o in set(bpy.data.objects)-before:
  vx,vy=o.location.x,o.location.y;o.location.x=x+vx*math.cos(ang)-vy*math.sin(ang);o.location.y=y+vx*math.sin(ang)+vy*math.cos(ang);o.rotation_euler.z+=ang
for x,y,a in [(-10,-11,0),(-5,-11,0),(1,-11,0),(17,-12,-.2),(23,-12,-.2)]:auto(x,y,a)
def palm(x,y,h):
 for j in range(16):
  cyl('Palm ringed trunk',(x+.18*math.sin(j/16),y,.5+j*h/16),.17-j*.004,h/16+.015,trunk,10)
 top=Vector((x+.18,y,h))
 for a in [i*math.pi/4 for i in range(8)]:
  end=top+Vector((math.cos(a)*3.2,math.sin(a)*3.2,-.9));mid=top+Vector((math.cos(a)*1.3,math.sin(a)*1.3,.75));beam('Palm frond midrib',top,mid,.025,leaf);beam('Palm frond midrib',mid,end,.018,leaf)
  for k in range(1,10):
   t=k/10;p=(1-t)**2*top+2*(1-t)*t*mid+t*t*end;width=.62*math.sin(t*math.pi)
   side=Vector((-math.sin(a)*width,math.cos(a)*width,-.22));tip=p+Vector((math.cos(a)*.45,math.sin(a)*.45,-.25))
   mesh('Palm leaflet',[p,p+side,tip,p-side],[(0,1,2),(0,2,3)],leaf)
for x,y,h in [(-61,-25,9),(-40,-26,10),(37,-26,9.5),(42,8,11),(-62,18,12)]:palm(x,y,h)
for x in [-39,33]:
 cyl('Forecourt lamp pole',(x,-22,3.5),.065,7,metal);beam('Lamp arm',(x,-22,6.9),(x,-20.5,7.2),.05,metal);cube('Street light fitting',(x,-20.35,7.2),(.36,.8,.14),grey)
print('BUILD_CAMERAS',flush=True)
# Base ground and presentation cameras.
active=base;cube('Ground slab',(-10,1,-.35),(153,92,.5),sand,.2)
# Scale datum, collection metadata and camera setup.
for name,c in cols.items():c['scope']='Photo-traced/inferred historical architecture' if name[:2] in ['01','02','03','04'] else 'Separable scenic/context module, not surveyed layout'
group('09_LIGHTS_CAMERAS')
def camera(n,loc,target,lens=48,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=assign(bpy.context.object,n,None);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
cams=[camera('01_HERO_FORECOURT',(48,-77,29),(-9,-1,3.2),46),camera('02_FRONT_ELEVATION',(-9,-100,12),(-9,-1,5.7),48,102),camera('03_ENTRANCE_DETAIL',(24,-33,13),(2,-3,5.5),50),camera('04_PLATFORM_CONTEXT',(48,40,14),(-3,13,3.4),47)]
bpy.ops.object.light_add(type='SUN',location=(0,-15,35));sun=assign(bpy.context.object,'Sun warm late morning',None);sun.rotation_euler=(math.radians(27),math.radians(-20),math.radians(-32));sun.data.energy=2.5;sun.data.angle=.15
world=bpy.data.worlds.new('Soft coastal sky');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.67,.83,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.camera=cams[0];scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene['asset_title']='Nagercoil Junction NCJ | 2010 photo-informed reconstruction';scene['scale']='1 Blender unit = 1 metre. Dimensions are inferred, not as-built.';scene['historical_basis']='Kkdrua 9 Jan 2010 + Danymaddy 17 Oct 2010, CC BY-SA 3.0';scene['yard_warning']='Rear wall, platform and track are modular context; neither cited photograph shows the rail side. No exact yard claimed.'
for f in bpy.data.fonts:
 if f.filepath and f.filepath!='<builtin>':f.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'NCJ_2010_station.blend'))
# Portable mesh export excludes lights/cameras. Text converted for export only.
for o in bpy.context.selected_objects:o.select_set(False)
for o in scene.objects:
 if o.type in {'MESH','FONT','CURVE'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/NCJ_2010_station.glb'),export_format='GLB',use_selection=True,export_apply=True)
report={'object_count':len(scene.objects),'mesh_count':sum(o.type=='MESH' for o in scene.objects),'material_count':len(bpy.data.materials),'unit':'metres','blender':bpy.app.version_string,'nonfinite_vertices':0,'cameras':[c.name for c in cams],'reference_scope':'Street facade and left annex only; platform and yard not surveyed','render_threads':4}
for o in scene.objects:
 if o.type=='MESH':
  for v in o.data.vertices:
   if not all(math.isfinite(a) for a in v.co):report['nonfinite_vertices']+=1
(ROOT/'QA.json').write_text(json.dumps(report,indent=2));print('NCJ_SAVED_CHECKPOINT',flush=True)
if '--render' in __import__('sys').argv:
 for cam in cams:
  scene.camera=cam;scene.render.filepath=str(ROOT/'renders'/f'{cam.name}.png');bpy.ops.render.render(write_still=True)
