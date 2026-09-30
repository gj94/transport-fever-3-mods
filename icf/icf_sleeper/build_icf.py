import bpy, math, os, json, random
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials:bpy.data.materials.remove(d)
random.seed(21)
def mat(n,c,metal=0,rough=.45):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
blue=mat('ICF deep blue enamel',(.018,.13,.29),.28,.38);pale=mat('ICF pale cyan window band',(.39,.69,.73),.2,.44)
roof=mat('Weathered silver roof',(.47,.51,.52),.6,.58);steel=mat('Machined wheel tread',(.32,.36,.39),.82,.28);dark=mat('Underframe graphite',(.055,.065,.068),.5,.61);rubber=mat('Rubber black',(.017,.022,.024),.03,.7);springmat=mat('Springs patinated steel',(.15,.16,.15),.65,.45);cream=mat('Warm ivory interior',(.61,.63,.53),.1,.68);seat=mat('Blue vinyl berth',(.035,.15,.27),.03,.6);red=mat('Emergency red',(.63,.05,.025),.2,.4);white=mat('Lettering ivory',(.79,.85,.73),.0,.55);yellow=mat('End warning yellow',(.91,.61,.07),.15,.5);glass=mat('Dark window recess',(.035,.065,.072),.12,.23)
coll=bpy.data.collections.new('ICF Sleeper | original dimensioned prototype');bpy.context.scene.collection.children.link(coll)
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def parent(o,p):
 if p: o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted()
 return o
def cube(n,l,s,m,p=None,b=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=link(bpy.context.object);o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:mod=o.modifiers.new('Manufactured softened edges','BEVEL');mod.width=b;mod.segments=2;mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return parent(o,p)
def cyl(n,l,r,d,m,axis='Z',p=None,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d,location=l);o=link(bpy.context.object);o.name=n
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 if axis=='X':o.rotation_euler[1]=math.pi/2
 o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return parent(o,p)
def path(n,pts,r,m,p=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,v in zip(sp.points,pts):a.co=(*v,1)
 o=bpy.data.objects.new(n,cu);coll.objects.link(o);o.data.materials.append(m);return parent(o,p)
def empty(n,l,p=None):
 o=bpy.data.objects.new(n,None);coll.objects.link(o);o.location=l;bpy.context.view_layer.update();return parent(o,p)
def text(n,string,l,size,m,side=-1,p=None):
 cu=bpy.data.curves.new(n,'FONT');cu.body=string;cu.size=size;cu.align_x='CENTER';cu.extrude=.0005;o=bpy.data.objects.new(n,cu);coll.objects.link(o);o.location=l;o.rotation_euler=(math.pi/2,0,0) if side==-1 else (math.pi/2,0,math.pi);cu.materials.append(m);return parent(o,p)
def rounded(n,x,y,z,w,h,r,m,p=None,tube=.014):
 pts=[]
 for cx,cz,ang in [(x+w/2-r,z+h/2-r,0),(x-w/2+r,z+h/2-r,90),(x-w/2+r,z-h/2+r,180),(x+w/2-r,z-h/2+r,270)]:
  for j in range(7):
   a=math.radians(ang+j*90/6);pts.append((cx+r*math.cos(a),y,cz+r*math.sin(a)))
 pts.append(pts[0]);return path(n,pts,tube,m,p)
root=empty('ICF_ROOT_metres_X_forward',(0,0,0));body=empty('BODY',(0,0,0),root)
root['body_length_m']=21.337;root['length_over_buffers_m']=22.297;root['width_m']=3.245;root['height_rail_to_roof_m']=4.025;root['bogie_centres_m']=14.783;root['gauge_m']=1.676;root['status']='VISUAL PROTOTYPE — not game-ready';root['interior_nominal_berths']=72
# Structural floor and longitudinal solebars
cube('Floor',(0,0,1.265),(21.337,3.15,.12),cream,body)
for y in [-1.45,1.45]:
 cube('Longitudinal solebar',(0,y,1.18),(21.0,.14,.24),dark,body)
for x in range(-10,11):cube('Cross bearer',(x,0,1.12),(.08,2.83,.12),dark,body)
# Skin divided around true open window apertures. Nine eight-berth bays.
windows=[-7.2675+i*.855 for i in range(18)]
for s in [-1,1]:
 y=s*1.596
 # lower continuous skin and top letterboard
 cube('Lower blue bodyside',(0,y,1.635),(21.337,.053,.66),blue,body)
 cube('Upper blue letterboard',(0,y,3.095),(21.337,.053,.65),blue,body)
 # pale strips around window apertures
 cube('Lower cyan band',(0,y,2.005),(21.337,.055,.11),pale,body)
 cube('Upper cyan band',(0,y,2.735),(21.337,.055,.11),pale,body)
 # window zone interrupted by pillars, including door and toilet positions
 openings=[(x,.66,'main') for x in windows]+[(-9.13,.78,'door'),(9.13,.78,'door'),(-10.12,.43,'toilet'),(10.12,.43,'toilet')]
 openings.sort();edge=-10.6685
 for x,w,k in openings:
  left=x-w/2
  if left>edge:cube('Window pier',((edge+left)/2,y,2.37),(left-edge,.055,.62),pale,body,b=.002)
  edge=x+w/2
 if edge<10.6685:cube('End window pier',((edge+10.6685)/2,y,2.37),(10.6685-edge,.055,.62),pale,body,b=.002)
 for i,x in enumerate(windows):
  rounded('Rubber window gasket',x,s*1.632,2.37,.70,.71,.10,rubber,body,tube=.02)
  rounded('Aluminium window surround',x,s*1.654,2.37,.66,.67,.09,steel,body,tube=.011)
  # Fixed bars; authentic shutter split and alternating open/closed heights
  for j in range(5):path('Horizontal window security bar',[(x-.315,s*1.674,2.12+j*.116),(x+.315,s*1.674,2.12+j*.116)],.008,steel,body)
  openheight=[.18,.33,.06,.24,.36,.12][i%6]
  shutterh=.64-openheight
  cube('Sliding louvred shutter',(x,s*1.589,2.695-shutterh/2),(.615,.022,shutterh),pale,body,b=.015)
  for j in range(int(shutterh/.045)):
   cube('Stamped shutter slat',(x,s*1.615,2.685-j*.045),(.58,.016,.012),roof,body,b=.003)
  path('Shutter centre spine',[(x,s*1.625,2.695-shutterh),(x,s*1.625,2.695)],.008,pale,body)
  if i in [4,13]:
   text('Emergency marking','EMERGENCY WINDOW',(x,s*1.634,1.89),.056,red,s,body)
   for xx in [x-.31,x+.31]:cube('Emergency latch',(xx,s*1.66,2.05),(.025,.018,.06),red,body,b=.004)
  if i%2==0:text('Berth range',f'{i//2*8+1}–{i//2*8+8}',(x+.42,s*1.634,2.86),.061,white,s,body)
 for x in [-10.12,10.12]:
  cube('Toilet frosted glass',(x,s*1.599,2.37),(.42,.015,.63),cream,body,b=.05)
  rounded('Toilet window',x,s*1.64,2.37,.45,.69,.12,rubber,body,tube=.016)
  for j in range(5):path('Toilet grille',[(x-.16+j*.08,s*1.656,2.1),(x-.16+j*.08,s*1.656,2.65)],.009,steel,body)
 for x in [-9.13,9.13]:
  # Recessed closed door laid in its tall blue surround
  cube('Door recessed blue panel',(x,s*1.569,2.32),(.76,.055,2.08),blue,body,b=.025)
  cube('Door pale band',(x,s*1.603,2.37),(.74,.018,.81),pale,body,b=.006)
  cube('Door window dark recess',(x,s*1.618,2.4),(.57,.022,.63),glass,body,b=.06)
  rounded('Door window frame',x,s*1.642,2.4,.6,.68,.09,steel,body)
  for j in range(5):path('Door barred window',[(x-.28,s*1.66,2.16+j*.11),(x+.28,s*1.66,2.16+j*.11)],.009,steel,body)
  for dx in [-.47,.47]:
   path('Entrance grab rail',[(x+dx,s*1.64,1.40),(x+dx,s*1.75,1.49),(x+dx,s*1.75,2.8),(x+dx,s*1.64,2.89)],.018,steel,body)
  for z in [.43,.70,.97,1.24]:cube('Entrance tread',(x,s*1.70,z),(.79,.36,.04),steel,body,b=.006)
  for dx in [-.37,.37]:path('Step ladder stringer',[(x+dx,s*1.7,.39),(x+dx,s*1.7,1.25)],.024,dark,body)
  cube('Door threshold',(x,s*1.634,1.30),(.8,.12,.06),dark,body)
  cube('Door handle',(x+.28,s*1.642,2.03),(.027,.027,.19),steel,body)
  text('Exit','EXIT',(x-.61,s*1.635,3.02),.077,white,s,body)
 text('Sleeper legend','S L E E P E R',(0,s*1.635,3.09),.18,white,s,body)
 text('Prototype identification','ICF  /  72 BERTH',(5.4,s*1.635,3.12),.092,white,s,body)
 cube('Route board blank',(-4.7,s*1.64,3.12),(1.35,.03,.21),roof,body,b=.018)
 for x in [-10.61,10.61]:cube('End warning stripe',(x,s*1.63,2.38),(.045,.016,1.97),yellow,body,b=.001)
# Elliptical pressed-steel roof, closed longitudinal mesh cross section
verts=[];N=40
for x in [-10.6685,10.6685]:
 for j in range(N+1):
  a=math.pi*j/N;verts.append((x,1.6225*math.cos(a),3.39+.635*math.sin(a)))
faces=[(j,j+1,N+2+j,N+1+j) for j in range(N)]
mesh=bpy.data.meshes.new('Elliptical roof shell mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(roof);o=bpy.data.objects.new('ICF compound-curved roof shell',mesh);coll.objects.link(o);parent(o,body)
for f in mesh.polygons:f.use_smooth=True
mod=o.modifiers.new('Roof sheet thickness','SOLIDIFY');mod.thickness=.035
for x in [-9,-6,-3,0,3,6,9]:
 path('Roof welded panel seam',[(x,1.624*math.cos(math.pi*j/N),3.3845+.637*math.sin(math.pi*j/N)) for j in range(N+1)],.0035,steel,body)
for x in [-7.7,-6,-4.3,-2.6,-.9,.9,2.6,4.3,6,7.7]:
 cube('Roof torpedo vent base',(x,0,4.015),(.43,.35,.018),roof,body)
 # low raised cover within max crown exception removed height: vents included apex 4.025 only
# End walls contain recessed vestibule opening
for s in [-1,1]:
 x=s*10.648
 for y in [-1.045,1.045]:cube('Coach end wall',(x,y,2.34),(.04,1.08,2.12),blue,body,b=.06)
 cube('End upper arch panel',(x,0,3.38),(.045,2.85,.38),blue,body,b=.08)
 cube('Vestibule recessed inner door',(s*10.42,0,2.30),(.045,.92,1.89),cream,body)
 cube('Vestibule door glazing',(s*10.45,0,2.64),(.023,.56,.57),glass,body,b=.07)
 for j in range(7):
  xx=s*(10.66+j*.035)
  for y in [-.61,.61]:cube('Gangway bellows fold',(xx,y,2.26),(.028,.11,1.96),rubber,body,b=.018)
  cube('Gangway bellows top',(xx,0,3.24),(.028,1.28,.10),rubber,body,b=.025)
 cube('Gangway tread plate',(s*10.78,0,1.31),(.38,1.14,.07),steel,body)
 cube('Buffer beam',(s*10.48,0,1.04),(.19,2.86,.29),dark,body)
 for y in [-.875,.875]:
  cyl('Buffer shank',(s*10.78,y,1.105),.105,.48,dark,'X',body)
  cyl('Buffer housing',(s*10.64,y,1.105),.16,.28,dark,'X',body)
  cyl('Buffer head',(s*11.1185,y,1.105),.225,.06,steel,'X',body)
 # simplified screw coupling chain with central draw hook
 path('Draw hook',[(s*10.57,0,1.07),(s*10.93,0,1.07),(s*10.97,0,.99),(s*10.87,0,.96)],.033,steel,body)
 path('Screw coupling loop',[(s*10.87,-.045,.99),(s*10.94,-.07,.70),(s*10.74,.07,.70),(s*10.72,.045,.94),(s*10.87,-.045,.99)],.024,dark,body)
 cyl('Screw coupling spindle',(s*10.84,0,.73),.039,.23,steel,'Y',body)
 for y in [-.37,.37]:
  path('Air brake hose',[(s*10.56,y,1.0),(s*10.85,y,.87),(s*10.86,y,.53),(s*10.7,y,.44)],.031,rubber,body)
  cube('Brake hose cock',(s*10.60,y,1.025),(.11,.10,.07),red,body)
# Bogies and wheelsets
for k,bx in enumerate([-7.3915,7.3915],1):
 bog=empty(f'BOGIE_{k}_PIVOT',(bx,0,1.0),root);bog['wheelbase_m']=2.896
 for y in [-1.12,1.12]:
  cube('Bogie longitudinal frame',(bx,y,.98),(3.93,.16,.23),dark,bog,b=.05)
  cube('Lower spring plank',(bx,y,.57),(1.15,.27,.12),dark,bog)
  for xx in [-.34,.34]:
   points=[]
   for t in range(145):
    a=t/144*math.pi*12;points.append((bx+xx+.128*math.cos(a),y+.128*math.sin(a),.64+.36*t/144))
   path('Secondary bolster coil spring',points,.028,springmat,bog)
  for xx in [-.66,.66]:path('Swing hanger',[(bx+xx,y,.96),(bx+xx*.86,y,.53)],.026,steel,bog)
  cyl('Secondary damper',(bx+.68,y,.8),.047,.4,steel,'Z',bog)
 for xx in [-1.73,0,1.73]:cube('Bogie transverse frame',(bx+xx,0,.91),(.15,2.34,.17),dark,bog)
 cube('Bolster',(bx,0,1.10),(.40,2.24,.14),dark,bog)
 for y in [-.8,.8]:cube('Side bearer',(bx,y,1.2),(.34,.27,.1),steel,bog)
 for j,ax in enumerate([bx-1.448,bx+1.448],1):
  axle=empty(f'BOGIE_{k}_AXLE_{j}_ROTATE_Y',(ax,0,.4575),bog)
  cyl('Axle',(ax,0,.4575),.095,2.25,steel,'Y',axle)
  for s in [-1,1]:
   cyl('Wheel tread 915mm',(ax,s*.8875,.4575),.4575,.13,steel,'Y',axle,64)
   cyl('Wheel web',(ax,s*.96,.4575),.375,.07,dark,'Y',axle,48)
   cyl('Wheel flange',(ax,s*.815,.4575),.482,.026,steel,'Y',axle,64)
   cyl('Wheel hub',(ax,s*1.0,.4575),.15,.11,steel,'Y',axle)
   cube('Axle box',(ax,s*1.14,.51),(.35,.26,.30),dark,bog,b=.055)
   cyl('Axlebox bearing cover',(ax,s*1.30,.51),.112,.025,springmat,'Y',bog)
   for angle in range(0,360,60):
    a=math.radians(angle);cyl('Bearing cover bolt',(ax+.083*math.cos(a),s*1.319,.51+.083*math.sin(a)),.015,.018,steel,'Y',bog,6)
   for dx in [-.28,.28]:
    pts=[]
    for t in range(97):
     a=t/96*math.pi*10;pts.append((ax+dx+.095*math.cos(a),s*1.13+.095*math.sin(a),.59+.31*t/96))
    path('Primary axlebox coil spring',pts,.022,springmat,bog)
    cyl('Primary dashpot',(ax+dx,s*1.13,.735),.036,.31,dark,'Z',bog)
   for dx in [-.44,.44]:
    cube('Brake shoe',(ax+dx,s*.89,.49),(.10,.16,.29),dark,bog,b=.03)
    path('Brake hanger',[(ax+dx,s*.89,.50),(ax+dx*.84,s*.89,.94)],.02,steel,bog)
  for dx in [-.5,.5]:cyl('Brake cross beam',(ax+dx,0,.45),.031,1.90,dark,'Y',bog)
 path('Brake longitudinal pull rod',[(bx-1.85,.35,.42),(bx+1.85,.35,.42)],.023,steel,bog)
 cyl('Brake cylinder',(bx,.3,.76),.13,.52,dark,'X',bog)
# underfloor equipment
for x in [-3.5,3.5]:
 cube('Battery box',(x,-.9,.77),(1.58,.62,.52),dark,body,b=.045)
 for xx in [-.52,0,.52]:cube('Battery access lid',(x+xx,-1.23,.79),(.48,.027,.43),springmat,body,b=.013)
 for xx in [-.7,.7]:cube('Battery cradle',(x+xx,-.9,.53),(.065,.74,.07),steel,body)
for x in [-2.8,2.8]:
 cyl('Underframe water tank',(x,.68,.76),.27,1.50,roof,'X',body)
 for dx in [-.5,.5]:path('Tank retaining strap',[(x+dx,.39,.83),(x+dx,.40,.54),(x+dx,.96,.54),(x+dx,.97,.83)],.025,dark,body)
cyl('Air reservoir',(0,.05,.74),.20,1.45,dark,'X',body)
path('Train brake air pipe',[(-10.55,.26,1.09),(10.55,.26,1.09)],.023,steel,body)
cube('Electrical junction box',(0,-1.0,.88),(.6,.42,.38),dark,body)
# 9 x eight berth layout, simplified original interior
for bay in range(9):
 cx=-6.84+bay*1.71
 for dx in [-.55,.55]:
  for z in [1.64,2.25,2.92]:cube('Transverse sleeper berth',(cx+dx,-.60,z),(.59,1.76,.075),seat,body,b=.032)
 for z in [1.67,2.86]:cube('Side sleeper berth',(cx,1.15,z),(1.59,.56,.075),seat,body,b=.03)
 for dx in [-.85,.85]:cube('Compartment partition',(cx+dx,-.55,2.24),(.028,1.85,1.86),cream,body,b=.006)
 for dx in [-.35,.35]:path('Berth ladder upright',[(cx+dx,.33,1.32),(cx+dx,.33,2.95)],.015,steel,body)
 for z in [1.52,1.8,2.08,2.36,2.64]:path('Berth ladder rung',[(cx-.35,.33,z),(cx+.35,.33,z)],.012,steel,body)
 cube('Aisle ceiling lamp',(cx,.55,3.60),(.44,.13,.04),white,body,b=.02)
for x in [-8.32,8.32]:cube('Vestibule compartment bulkhead',(x,0,2.32),(.035,3.03,1.98),cream,body)
# Curved end caps close the roof-end void.
for s in [-1,1]:
 vs=[(s*10.648,1.6225*math.cos(math.pi*j/40),3.39+.635*math.sin(math.pi*j/40)) for j in range(41)]
 me=bpy.data.meshes.new('Closed curved roof end');me.from_pydata(vs,[],[tuple(range(41))]);me.materials.append(blue);ob=bpy.data.objects.new('Curved roof end cap',me);coll.objects.link(ob);parent(ob,body)
# convert all details to meshes for FBX portability
bpy.ops.object.select_all(action='DESELECT')
for o in coll.objects:
 if o.type in {'CURVE','FONT','MESH'}:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in coll.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH')
# render-only studio excluded from FBX
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
studio=bpy.data.collections.new('STUDIO_render_only');scene.collection.children.link(studio)
def studio_obj(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 studio.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.31));o=bpy.context.object;o.name='Studio ground';o.data.materials.append(mat('Ground',(.19,.22,.25),0,.75));studio_obj(o)
# rail top at zero and broad-gauge measured between inner rail faces
for y in [-.8755,.8755]:
 o=cube('Display rail',(0,y,-.086),(29,.075,.172),steel,b=.007);studio_obj(o)
for i in range(-23,24):
 o=cube('Display sleeper',(i*.60,0,-.225),(.23,2.72,.12),roof,b=.02);studio_obj(o)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.40,.47,.58,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
for n,l,power,size in [('Key',(0,-9,14),2300,10),('Fill',(-8,4,10),1900,9),('Rim',(10,7,11),2500,8)]:
 bpy.ops.object.light_add(type='AREA',location=l);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler();studio_obj(o)
bpy.ops.object.camera_add(location=(22,-30,13));cam=bpy.context.object;cam.name='ICF three quarter';cam.rotation_euler=(Vector((0,0,1.55))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=27;scene.camera=cam;studio_obj(cam)
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
# Asset selection export, scene includes studio
bpy.ops.object.select_all(action='DESELECT')
for o in coll.objects:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'icf_sleeper_prototype.fbx'),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',add_leaf_bones=False,bake_anim=False)
checks={'blender':bpy.app.version_string,'objects_asset':len(coll.objects),'mesh_objects':sum(o.type=='MESH' for o in coll.objects),'triangles_base':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in coll.objects if o.type=='MESH'),'dimensions':{k:root[k] for k in root.keys()},'bogie_centres':[list(o.location) for o in coll.objects if o.name.startswith('BOGIE_') and 'PIVOT' in o.name],'berth_objects':sum('sleeper berth' in o.name for o in coll.objects),'window_count_per_side':18,'notes':'Rail top Z0. Wheel tread radius .4575; flanges project below rail top as expected. Original geometry. No third-party photo texture.'}
open(os.path.join(OUT,'validation.json'),'w').write(json.dumps(checks,indent=2))
scene.render.filepath=os.path.join(OUT,'icf_preview.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'icf_sleeper_prototype.blend'));bpy.ops.render.render(write_still=True)
cam.location=(7.5,-11,4.1);cam.rotation_euler=(Vector((7.4,0,1.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.9;scene.render.filepath=os.path.join(OUT,'icf_detail.png');bpy.ops.render.render(write_still=True)
