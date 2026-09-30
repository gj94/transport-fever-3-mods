import bpy, math, os, json
from mathutils import Vector
from math import pi,sin,cos
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials): bpy.data.materials.remove(x)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
asset=bpy.data.collections.new('WAP7_ASSET');scene.collection.children.link(asset)
stage=bpy.data.collections.new('PRESENTATION_ONLY');scene.collection.children.link(stage)
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
white=mat('Signal white | RAL9003 approximation',(.78,.8,.78),.15,.38);red=mat('Oxide red belt',(.48,.035,.02),.1,.42);dark=mat('Graphite underframe',(.065,.079,.083),.6,.48);black=mat('Rubber and cavities',(.012,.017,.019),.1,.7);steel=mat('Machined wheel rims',(.30,.34,.35),.85,.27);glass=mat('Smoked blue cab glazing',(.022,.072,.085),.65,.18);roofmat=mat('Roof grey',(.30,.33,.33),.4,.55);copper=mat('Copper HV conductor',(.34,.15,.048),.75,.32);ochre=mat('Pantograph ochre',(.46,.29,.07),.55,.4);ceramic=mat('Brown ceramic insulators',(.12,.059,.029),.1,.3);lamp=mat('Headlamp lenses',(.76,.84,.79),.5,.18);silver=mat('Handrail silver',(.48,.51,.49),.75,.3);navy=mat('Railway lettering',(.033,.055,.068),.05,.6);orange=mat('Flag saffron',(.9,.29,.02));green=mat('Flag green',(.015,.3,.075))
def assign(o,n,m,p=None,coll=asset):
 o.name=n
 for c in list(o.users_collection): c.objects.unlink(o)
 coll.objects.link(o)
 if m:o.data.materials.append(m)
 if p:o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted()
 return o
def empty(n,loc=(0,0,0),p=None):
 o=bpy.data.objects.new(n,None);asset.objects.link(o);o.location=loc
 if p:o.parent=p
 return o
root=empty('WAP7_ROOT');body=empty('BODY',p=root)
def cube(n,loc,scale,m,p=body,b=.015,coll=asset):
 x,y,z=[v/2 for v in scale]
 vv=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 ff=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 d=bpy.data.meshes.new(n);d.from_pydata(vv,[],ff);d.update();o=bpy.data.objects.new(n,d);o.location=loc;assign(o,n,m,p,coll)
 if b:mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=b;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,d,m,p=body,axis='Z',vertices=24):
 vv=[(r*cos(2*pi*i/vertices),r*sin(2*pi*i/vertices),z) for z in [-d/2,d/2] for i in range(vertices)]
 ff=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
 me=bpy.data.meshes.new(n);me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new(n,me);o.location=loc;assign(o,n,m,p)
 if axis=='Y':o.rotation_euler[0]=pi/2
 if axis=='X':o.rotation_euler[1]=pi/2
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return o
def rod(n,a,b,r,m,p=body,vertices=12):
 a=Vector(a);b=Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,p,vertices=vertices);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mesh(n,verts,faces,m,p=body):
 d=bpy.data.meshes.new(n);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(n,d);asset.objects.link(o);o.data.materials.append(m);o.parent=p;return o
def text(n,t,loc,size,m,rot):
 d=bpy.data.curves.new(n,'FONT');d.body=t;d.size=size;d.align_x='CENTER';d.extrude=.0005;o=bpy.data.objects.new(n,d);asset.objects.link(o);o.location=loc;o.rotation_euler=rot;o.data.materials.append(m);o.parent=body;return o
# Swept shell with cab corner facets and roof shoulders. X longitudinal.
rings=[(1.45,9.52,1.576),(2.35,9.52,1.576),(3.55,9.17,1.576),(3.78,8.93,1.36)]
verts=[]
for z,L,W in rings:
 verts.extend([(L,-W+.28,z),(L,W-.28,z),(L-.36,W,z),(-L+.36,W,z),(-L,W-.28,z),(-L,-W+.28,z),(-L+.36,-W,z),(L-.36,-W,z)])
faces=[tuple(reversed(range(8))),tuple(range(24,32))]
for k in range(3):
 for j in range(8):faces.append((8*k+j,8*k+(j+1)%8,8*(k+1)+(j+1)%8,8*(k+1)+j))
o=mesh('Chamfered welded body shell',verts,faces,white);bev=o.modifiers.new('Body weld edge softness','BEVEL');bev.width=.035;bev.segments=3;o.modifiers.new('Body weighted normals','WEIGHTED_NORMAL')
cube('Main load bearing underframe',(0,0,1.36),(19.05,3.1,.28),dark)
cube('Central roof equipment deck',(0,0,3.79),(14.55,2.69,.09),roofmat,b=.055)
for s in [-1,1]:
 cube('Continuous red bodyside band',(0,s*1.58,2.04),(18.2,.014,.24),red,b=.003)
 cube('Bodyside lower sill',(0,s*1.58,1.52),(18.05,.045,.09),roofmat)
 for x in [-7.35,-3.3,0,3.3,7.35]:cube('Shell vertical joint',(x,s*1.581,2.64),(.012,.006,1.85),roofmat,b=0)
 text('Indian Railways bodyside','INDIAN RAILWAYS',(0,s*1.594,2.94),.28,navy,(pi/2,0,pi if s==1 else 0))
 text('Class designation','WAP-7',(0,s*1.594,1.68),.23,navy,(pi/2,0,pi if s==1 else 0))
 # large side intake screen, narrow switchgear ventilation, pairs at rear
 for x,w,h,z in [(-5.55,1.36,1.17,2.88),(5.55,1.36,1.17,2.88),(-2.6,.45,1.1,2.94),(2.6,.45,1.1,2.94)]:
  cube('Air intake rim',(x,s*1.603,z),(w+.09,.065,h+.08),roofmat)
  cube('Recessed intake screen',(x,s*1.64,z),(w,.02,h),black,b=.008)
  for zz in range(int(h/.055)):
   cube('Intake horizontal slat',(x,s*1.655,z-h/2+.03+zz*.055),(w,.022,.012),dark,b=.002)
  for xx in [-w/2,0,w/2]:cube('Intake screen mullion',(x+xx,s*1.674,z),(.024,.022,h),roofmat,b=.004)
 # double-ended cab doors and side windows
 for end in [-1,1]:
  x=end*7.8
  cube('Cab door gasket',(x,s*1.594,2.58),(.69,.032,2.02),dark,b=.06)
  cube('Cab door leaf',(x,s*1.617,2.58),(.64,.035,1.97),white,b=.055)
  cube('Door window seal',(x,s*1.642,3.02),(.45,.024,.81),black,b=.06)
  cube('Door glazing',(x,s*1.66,3.02),(.395,.018,.755),glass,b=.05)
  cube('Latch base',(x-end*.20,s*1.66,2.4),(.07,.032,.15),dark)
  rod('Door latch',(x-end*.22,s*1.69,2.44),(x-end*.10,s*1.69,2.44),.018,silver)
  for zz in [1.83,2.56,3.38]:cube('Door hinges',(x+end*.30,s*1.657,zz),(.055,.05,.1),silver)
  xx=end*8.55
  cube('Cab side window surround',(xx,s*1.59,3.03),(.60,.045,.84),roofmat,b=.075)
  cube('Cab side glazing',(xx,s*1.624,3.03),(.51,.023,.74),glass,b=.06)
  cube('Sliding window divider',(xx,s*1.647,3.03),(.022,.025,.73),silver)
  for z in [1.0,1.22,1.44]:
   cube('Cab access tread',(x,s*1.55,z),(.58,.32,.045),dark)
   for dx in [-.2,0,.2]:cube('Anti slip tread',(x+dx,s*1.6,z+.027),(.015,.25,.008),steel,b=0)
  for dx in [-.38,.38]:rod('Cab entry grab rail',(x+dx,s*1.69,1.48),(x+dx,s*1.69,2.68),.018,silver)
# Front surface projection follows sloped upper nose
for end in [-1,1]:
 def fx(z): return end*(9.52-(max(z,2.35)-2.35)*(.35/1.2)+.018)
 for sy in [-1,1]:
  y=sy*.67
  # tilted face glazing rectangular extrusions parallel cab rake
  for name,ww,hh,dep,ma in [('Windscreen rubber seal',1.16,.99,.04,black),('Front windscreen glass',1.045,.89,.052,glass)]:
   ob=cube(name,(fx(3.015),y,3.015),(dep,ww,hh),ma,b=.055);ob.rotation_euler[1]=end*(-math.atan(.35/1.2))
  # protective windshield lattice following rake
  for j in range(12):
   yy=y-.52+j*.095
   rod('Windscreen protection vertical',(fx(2.54)+end*.075,yy,2.54),(fx(3.48)+end*.075,yy,3.48),.009,silver)
  for z in [2.54,2.7,3.34,3.48]:rod('Windscreen protection crossbar',(fx(z)+end*.08,y-.55,z),(fx(z)+end*.08,y+.55,z),.014,silver)
  rod('Wiper arm',(fx(2.61)+end*.10,y-.1,2.61),(fx(2.94)+end*.10,y+.25,2.94),.012,black)
  rod('Wiper blade',(fx(2.84)+end*.115,y+.19,2.84),(fx(3.18)+end*.115,y+.30,3.18),.018,black)
 cube('Front red band',(end*9.544,0,2.04),(.016,2.58,.24),red,b=.004)
 cube('Twin headlight recess',(end*9.567,0,1.98),(.08,.58,.34),dark)
 for y in [-.155,.155]:
  cyl('Headlight bezel',(end*9.635,y,1.99),.137,.10,silver,axis='X');cyl('Headlight glass',(end*9.694,y,1.99),.105,.018,lamp,axis='X')
 for y in [-1.13,1.13]:
  cyl('Marker lamp body',(end*9.568,y,1.77),.095,.045,dark,axis='X');cyl('Marker lamp red lens',(end*9.595,y,1.77),.067,.02,red,axis='X')
 # front flag geometrical markings
 for z,ma in [(2.205,orange),(2.145,white),(2.085,green)]:cube('Tricolour marking',(end*9.56,-.87,z),(.014,.37,.06),ma,b=0)
 for y in [-1.12,1.12]:rod('Nose safety railing upright',(end*9.61,y,1.67),(end*9.61,y,2.33),.023,silver)
 rod('Nose safety railing',(end*9.61,-1.12,2.33),(end*9.61,1.12,2.33),.023,silver)
 cube('Buffer beam',(end*9.60,0,1.16),(.25,2.95,.28),dark)
 for y in [-1.02,1.02]:
  cyl('Buffer shank',(end*9.86,y,1.12),.11,.40,dark,axis='X');cyl('Buffer plate',(end*10.075,y,1.12),.245,.07,steel,axis='X')
 cube('CBC draft gear',(end*9.86,0,1.10),(.50,.28,.26),dark)
 cube('CBC knuckle housing',(end*10.19,0,1.10),(.182,.32,.25),steel,b=.04)
 cube('CBC knuckle cutout',(end*10.282,-.1,1.12),(.006,.09,.105),black,b=.02)
 # flexible brake hoses polygonal curves
 for yy in [-.47,.47,.69]:
  pts=[(end*9.72,yy,1.31),(end*9.89,yy,.99),(end*9.97,yy,.72),(end*9.82,yy,.62)]
  for a,b in zip(pts,pts[1:]):rod('Brake air hose',a,b,.031,black)
  cyl('Hose connector',pts[-1],.054,.09,red,axis='X')
 # Pilot grid
 for y in [-1.32,-.88,-.44,0,.44,.88,1.32]:rod('Pilot vertical strut',(end*9.38,y,.44),(end*9.61,y,.98),.035,dark)
 for z in [.48,.69,.9]:rod('Pilot transverse bar',(end*(9.4+(z-.44)*.4),-1.38,z),(end*(9.4+(z-.44)*.4),1.38,z),.036,dark)
 # roof horn box and trumpet horns
 cube('Cab roof horn enclosure',(end*8.35,0,3.91),(.8,.92,.29),roofmat)
 for y in [-.56,.56]:
  rod('Horn trumpet stem',(end*8.26,y,3.99),(end*8.64,y,3.99),.06,dark)
  bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.125,radius2=.048,depth=.25,location=(end*8.68,y,3.99));o=assign(bpy.context.object,'Horn flared bell',roofmat,body);o.rotation_euler[1]=-end*pi/2
  cyl('Horn mouth',(end*8.806,y,3.99),.102,.008,black,axis='X')
print('Cab and shell complete',flush=True)
# Bogies, six driven wheelsets, animated local-Y pivots
for bi,bx in enumerate([-6,6]):
 bog=empty('BOGIE_%s_YAW_Z'%('A' if bi==0 else 'B'),(bx,0,.82),root);bpy.context.view_layer.update()
 for s in [-1,1]:
  cube('Bogie fabricated side beam',(bx,s*1.10,.91),(5.50,.25,.34),dark,bog,b=.07)
  for xx in [-2.75,2.75]:cube('Bogie frame end transom',(bx+xx,0,.86),(.21,2.48,.28),dark,bog)
 for ai,dx in enumerate([-1.85,0,1.85]):
  ax=empty('AXLE_%s_%d_ROLL_Y'%('A' if bi==0 else 'B',ai+1),(bx+dx,0,.546));ax.parent=bog;ax.matrix_parent_inverse=bog.matrix_world.inverted();bpy.context.view_layer.update()
  cyl('Axle shaft',(bx+dx,0,.546),.105,2.18,steel,ax,axis='Y')
  for s in [-1,1]:
   cyl('Wheel disc',(bx+dx,s*.902,.546),.506,.16,dark,ax,axis='Y',vertices=48)
   cyl('Wheel tyre',(bx+dx,s*.926,.546),.546,.13,steel,ax,axis='Y',vertices=48)
   cyl('Wheel outer web',(bx+dx,s*1.005,.546),.423,.022,dark,ax,axis='Y',vertices=40)
   cyl('Wheel flange',(bx+dx,s*.845,.546),.57,.022,steel,ax,axis='Y',vertices=48)
   cube('Axlebox housing',(bx+dx,s*1.22,.58),(.43,.25,.31),dark,bog,b=.065)
   cyl('Axlebox bearing cover',(bx+dx,s*1.367,.58),.125,.055,steel,bog,axis='Y')
   for dd in [-.37,.37]:
    cyl('Primary spring core',(bx+dx+dd,s*1.13,.89),.09,.34,black,bog)
    # actual coiled steel spring geometry
    pts=[(bx+dx+dd+.105*cos(t*.25*pi),s*1.13+.105*sin(t*.25*pi),.72+t*.007) for t in range(49)]
    for a,b in zip(pts,pts[1:]):rod('Primary coil spring',a,b,.019,steel,bog,8)
   rod('Brake rigging',(bx+dx-.5,s*1.27,.44),(bx+dx+.5,s*1.27,.44),.032,dark,bog)
   cube('Brake shoe',(bx+dx+.48,s*.96,.55),(.10,.21,.23),dark,bog)
  cyl('Traction motor',(bx+dx+.4,0,.60),.25,1.13,dark,bog,axis='Y')
 for s in [-1,1]:
  for dx in [-.8,.8]:
   cyl('Secondary spring',(bx+dx,s*1.10,1.21),.18,.23,black,bog)
   for z in [1.12,1.17,1.22,1.27,1.32]:cyl('Secondary suspension coil',(bx+dx,s*1.1,z),.193,.025,steel,bog)
  rod('Lateral suspension link',(bx-1.6,s*1.28,.97),(bx+1.6,s*1.28,1.04),.035,steel,bog)
print('Bogies complete',flush=True)
# transformer, battery boxes, reservoirs, cable runs
cube('Traction transformer underfloor',(0,0,.99),(4.45,2.35,.55),dark,b=.08)
for s in [-1,1]:
 cube('Transformer fin bank',(0,s*1.2,.98),(2.9,.10,.46),black)
 for i in range(37):cube('Transformer cooling fin',(-1.4+i*.078,s*1.28,.98),(.018,.16,.44),steel,b=.002)
 for x in [-2.3,2.3]:cube('Underfloor equipment cabinet',(x,s*.8,1.06),(.68,.64,.51),roofmat)
 for z in [.75,.87,1.02]:rod('Bodyside air line',(-3.3,s*1.38,z),(3.3,s*1.38,z),.025,dark)
 cyl('Main air reservoir',(s*2.9,0,1.01),.22,1.6,dark,axis='Y')
# roof panels and folded pantographs
for x in [-6,-3,0,3,6]:
 cube('Removable roof panel',(x,0,3.85),(2.83,2.35,.045),roofmat)
 for y in [-1.05,1.05]:
  for dx in [-1.25,1.25]:cyl('Roof panel bolt',(x+dx,y,3.886),.025,.015,steel,vertices=8)
def insulator(x,y):
 cyl('Insulator stem',(x,y,4.00),.071,.24,ceramic)
 for z in [3.9,3.94,3.98,4.02,4.06,4.1]:cyl('Insulator ceramic skirt',(x,y,z),.11,.023,ceramic)
for px in [-5.0,5.0]:
 for dx in [-.8,.8]:
  for y in [-.58,.58]:insulator(px+dx,y)
 cube('Pantograph base',(px,0,4.105),(1.98,1.4,.07),dark)
 for y in [-.43,.43]:
  # lowered articulated single-arm assembly
  rod('Pantograph lower arm',(px-.75,y,4.14),(px+.65,y,4.20),.035,ochre)
  rod('Pantograph upper arm',(px+.65,y,4.20),(px-.38,y,4.235),.025,ochre)
  cyl('Pantograph hinge',(px+.65,y,4.20),.065,.11,steel,axis='Y')
 for xx in [-.45,-.32]:rod('Contact shoe',(px+xx,-.89,4.255),(px+xx,.89,4.255),.022,dark)
 for y in [-1,1]:rod('Contact horn',(px-.4,y*.87,4.255),(px-.4,y*1.03,4.19),.016,dark)
 for y in [-.18,.18]:cyl('Pantograph pneumatic cylinder',(px+.35,y,4.15),.08,.43,dark,axis='X')
for x in [-2.65,-1.4,.35,2.65]:insulator(x,.62)
for x in [-2.65,-1.4,.35,2.65]:
 rod('High voltage copper bus', (x,.62,4.135),(x+.5,.62,4.135),.022,copper)
rod('Roof high voltage bus',(-4.0,.62,4.135),(4.0,.62,4.135),.025,copper)
cube('Vacuum circuit breaker',(0,-.25,3.99),(.80,.66,.23),roofmat)
for x in [-.5,.5]:insulator(x,-.25)
print('Roof hardware complete',flush=True)
# stage collection; excluded from asset FBX export
floor= cube('Studio floor',(0,0,-.20),(200,200,.10),mat('Studio floor material',(.105,.139,.16)),None,b=0,coll=stage)
# two rails for dimensional context; separate stage
for y in [-.873,.873]:cube('Display rail',(0,y,-.034),(24,.07,.06),steel,None,b=.008,coll=stage)
for x in range(-11,12):cube('Display sleeper',(x,0,-.085),(.20,2.65,.075),roofmat,None,b=.01,coll=stage)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.34,.40,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,power,size in [('Large softbox',(2,-8,14),2600,12),('Roof fill',(-8,4,10),2000,10),('Nose rim',(11,6,7),1700,8)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Three quarter camera');cam=bpy.data.objects.new('Three quarter camera',d);stage.objects.link(cam);cam.location=(25,-30,16);target=Vector((0,0,1.8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=25.0;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(OUT,'WAP7_preview.png')
# asset metadata and animation naming convention
root['asset_status']='Detailed visual prototype; not yet optimized or validated in Transport Fever 3';root['units']='metres';root['length_over_couplers_m']=20.562;root['track_gauge_m']=1.676;root['wheel_diameter_m']=1.092;root['bogie_centres_m']=12.0;root['reference']='Indian Railways WAP-7; generic white/red livery with no assigned number or shed'
body.scale.y=3.152/3.416
for o in asset.objects:
 if o.name.startswith(('Contact shoe','Contact horn')):o.location.z-=.022
 if o.name.startswith('CBC knuckle cutout'):o.location.x=(10.278 if o.location.x>0 else -10.278)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'WAP7_prototype.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'WAP7_prototype.fbx'),use_selection=True,object_types={'MESH','EMPTY','OTHER'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False)
summary={'objects':len(asset.objects),'mesh_objects':sum(o.type=='MESH' for o in asset.objects),'source_vertices':sum(len(o.data.vertices) for o in asset.objects if o.type=='MESH'),'source_polygons':sum(len(o.data.polygons) for o in asset.objects if o.type=='MESH'),'axles':[o.name for o in asset.objects if o.name.startswith('AXLE_')],'bogies':[o.name for o in asset.objects if o.name.startswith('BOGIE_')]}
open(os.path.join(OUT,'geometry_report.json'),'w').write(json.dumps(summary,indent=2))
bpy.ops.render.render(write_still=True)
cam.location=(20,-13,8);cam.rotation_euler=(Vector((6,0,2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13;scene.render.filepath=os.path.join(OUT,'WAP7_cab_detail.png');bpy.ops.render.render(write_still=True)
