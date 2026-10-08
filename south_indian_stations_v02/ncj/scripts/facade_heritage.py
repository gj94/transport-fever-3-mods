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
fontfile=Path('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf')
font=bpy.data.fonts.load(str(fontfile)) if fontfile.exists() else bpy.data.fonts.get('Bfont')
def text(n,body,loc,size,m,width=None,rot=(math.pi/2,0,0),fontpath=None):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.009;d.bevel_depth=.002;d.font=bpy.data.fonts.load(fontpath) if fontpath else font;o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=loc;o.rotation_euler=rot;d.materials.append(m);bpy.context.view_layer.update()
 if width and o.dimensions.x>width:o.scale.x*=width/o.dimensions.x
 return o
def outlined_sign(n,file,loc,width,m):
 before=set(bpy.data.objects)
 bpy.ops.import_curve.svg(filepath=str(ROOT/'assets'/file))
 obs=list(set(bpy.data.objects)-before)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object
 coords=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector((min(v.x for v in coords),min(v.y for v in coords),0));hi=Vector((max(v.x for v in coords),max(v.y for v in coords),0));center=(lo+hi)/2
 scale=min(width/(hi.x-lo.x),.71/(hi.y-lo.y))
 for vert,p in zip(o.data.vertices,coords):vert.co=(p-center)*scale
 o.matrix_world.identity();o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.data.materials.clear();assign(o,n,m)
 sol=o.modifiers.new('Raised shaped letters','SOLIDIFY');sol.thickness=.018
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
for x in [-17.9,17.9]:cube('End wall',(x,5,4.875),(.42,10,8.75),peach)
cube('Rear wall',(0,10,4.875),(36,.4,8.75),peach)
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
# Small irregular paint losses, based on worn entablature/soffit in 2010 references.
for i in range(95):
 x=random.uniform(-18.2,18.2);z=random.uniform(9.08,9.51);w=random.uniform(.05,.3);h=random.uniform(.015,.05)
 mesh('Fascia worn paint patch',[(x-w,-5.565,z),(x-w*.4,-5.567,z+h),(x+w*.7,-5.567,z+h*.45),(x+w,-5.566,z-h*.3),(x,-5.565,z-h)],[(0,1,2,3,4)],ivory if i%3 else grey)
# Rooftop nameboards supported on paired small piers.
group('04_SIGNAGE')
for x,w,body,m,fp in [(-11.6,12.2,'NAGERCOIL JUNCTION',red,None),(1.55,10.7,'நாகர்கோவில் சந்திப்பு',blue,'/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf'),(12.15,8.7,'नागरकोविल जंक्शन',blue,'/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf')]:
 for dx in [-w*.35,w*.35]:cube('Rooftop board support',(x+dx,-2.65,10.42),(.15,.2,.7),ivory)
 cube('Rooftop nameboard',(x,-2.65,11.01),(w,.18,.91),ivory,.025)
 outlined_sign('Shaped '+body,('tamil_outlined.svg' if 'Tamil' in fp else 'hindi_outlined.svg') if fp else 'english_outlined.svg',(x,-2.772,11.02),w-.28,m)
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
cube('Wing-annex low connection',(-37.2,5.2,1.45),(2.9,4.5,1.8),peach)
mesh('Wing-annex inferred lean-to roof',[(-38.7,2.8,2.7),(-35.7,2.8,2.7),(-35.7,7.7,3.8),(-38.7,7.7,3.8)],[(0,1,2,3)],roof)
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
