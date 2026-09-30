"""Original WAG-9 modelling master. Blender 4.3+ / CPU.
Run: blender -b -t 4 --python build_wag9.py
All dimensions metres. No downloaded geometry, photographs or external assets.
"""
import bpy, math, json, os, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from math import pi, sin, cos
OUT=Path(__file__).resolve().parent
for d in ('renders','qa'): (OUT/d).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=25
asset=bpy.data.collections.new('WAG9_ASSET');sc.collection.children.link(asset)
stage=bpy.data.collections.new('PRESENTATION_ONLY');sc.collection.children.link(stage)
def mat(name,c,metal=0,rough=.45,trans=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Transmission Weight'].default_value=trans;p.inputs['IOR'].default_value=1.46
 return m
M={
 'green':mat('01_CLW_green_enamel',(.045,.265,.132),.18,.37),
 'green2':mat('02_Access_panel_green',(.053,.29,.148),.16,.39),
 'yellow':mat('03_Indian_Railways_yellow',(.97,.63,.075),.12,.38),
 'roof':mat('04_Weathered_roof_grey',(.37,.39,.36),.38,.58),
 'frame':mat('05_Underframe_graphite',(.075,.086,.086),.53,.50),
 'bogie':mat('06_Cast_bogie_grey',(.18,.195,.185),.53,.52),
 'black':mat('07_Rubber_and_recess',(.008,.014,.015),.05,.66),
 'steel':mat('08_Burnished_steel',(.40,.44,.45),.8,.28),
 'rim':mat('09_Wheel_tread_steel',(.50,.54,.56),.85,.25),
 'silver':mat('10_Handrail_aluminium',(.62,.66,.63),.72,.30),
 'white':mat('11_Lettering_ivory',(.88,.89,.77),.05,.42),
 'glass':mat('12_Clear_cab_laminated_glass',(.73,.86,.83),0,.09,.96),
 'lens':mat('13_Headlamp_glass',(.88,.92,.84),.18,.18,.55),
 'red':mat('14_Tail_lens_red',(.46,.012,.006),.12,.19),
 'ceramic':mat('15_HV_brown_ceramic',(.19,.085,.035),.1,.22),
 'copper':mat('16_HV_copper',(.40,.19,.065),.76,.31),
 'panto':mat('17_Pantograph_ochre',(.51,.34,.125),.65,.38),
 'carbon':mat('18_Carbon_contact_strip',(.042,.043,.040),.3,.56),
 'cab':mat('19_Cab_warm_grey',(.48,.53,.48),.08,.54),
 'desk':mat('20_Desk_slate_green',(.19,.27,.23),.15,.42),
 'panel':mat('21_Instrument_panel_charcoal',(.035,.048,.047),.2,.35),
 'seat':mat('22_Seat_vinyl',(.073,.105,.104),.05,.7),
 'dial':mat('23_Gauge_ivory',(.88,.90,.83),.05,.43),
 'orange':mat('24_Warning_amber',(.94,.26,.015),.1,.25),
 'blue':mat('25_Diagnostic_screen',(.05,.23,.28),.1,.26),
 'saffron':mat('26_Flag_saffron',(.95,.30,.035),.05,.48),
 'flaggreen':mat('27_Flag_green',(.03,.28,.09),.05,.48),
 'navy':mat('28_Flag_navy',(.023,.034,.13),.05,.48),
 'grime':mat('29_Brake_dust',(.19,.155,.11),.35,.7),
}
def link(o,parent=None,coll=asset):
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o)
 if parent:o.parent=parent
 return o
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);asset.objects.link(o);o.location=loc;o.empty_display_type='ARROWS';o.empty_display_size=.18
 if parent:o.parent=parent
 return o
root=empty('WAG9_ROOT');root['asset_version']='WAG9_v01';root['prototype']='Conventional CLW WAG-9, green/yellow, representative 31034';root['units']='metres';root['up_axis']='Z';root['forward_axis']='X';root['rail_tread_z_m']=0.
body=empty('BODY',parent=root)
def mesh(name,verts,faces,ma,parent=body,bevel=0):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);asset.objects.link(o);o.parent=parent
 if ma:me.materials.append(M[ma] if isinstance(ma,str) else ma)
 if bevel:
  b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=bevel;b.segments=2
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def box(name,loc,dim,ma,parent=body,b=.012):
 x,y,z=[v/2 for v in dim];v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 o=mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,parent,b);o.location=loc;return o
def cyl(name,loc,r,d,ma,parent=body,axis='Z',n=24):
 v=[(r*cos(j*2*pi/n),r*sin(j*2*pi/n),z) for z in (-d/2,d/2) for j in range(n)]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,n+(j+1)%n,n+j) for j in range(n)]
 o=mesh(name,v,f,ma,parent);o.location=loc
 if axis=='Y':o.rotation_euler.x=pi/2
 if axis=='X':o.rotation_euler.y=pi/2
 for p in o.data.polygons:
  if len(p.vertices)==4:p.use_smooth=True
 return o
def rod(name,a,b,r,ma,parent=body,n=10):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,ma,parent,n=n);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def path(name,pts,r,ma,parent=body,n=8):
 # Joined tube with smooth segment tangents, closed at the ends.
 vv=[];ff=[]
 for i,pt in enumerate(pts):
  pt=Vector(pt);w=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
  w.normalize();u=w.cross(Vector((0,0,1)))
  if u.length<.01:u=w.cross(Vector((0,1,0)))
  u.normalize();v=w.cross(u)
  vv.extend([tuple(pt+r*(u*cos(j*2*pi/n)+v*sin(j*2*pi/n))) for j in range(n)])
 ff=[tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]
 for i in range(len(pts)-1):
  for j in range(n):ff.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 o=mesh(name,vv,ff,ma,parent)
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return o
def text(name,t,loc,size,ma,rot=(pi/2,0,0),parent=body):
 d=bpy.data.curves.new(name,'FONT');d.body=t;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.00025;d.resolution_u=2
 o=bpy.data.objects.new(name,d);asset.objects.link(o);o.parent=parent;o.location=loc;o.rotation_euler=rot;d.materials.append(M[ma]);return o
def panelpoly(name,yz,thick,ma,parent=body):
 # Front cab surface follows nose rake, positive X local.
 vv=[(nose_x(z)+dx,y,z) for dx in (-thick/2,thick/2) for y,z in yz];n=len(yz)
 return mesh(name,vv,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],ma,parent,.006)
def nose_x(z): return 9.59-.245*max(0,z-2.03)
def rounded_rect(cx,cz,w,h,r=.045,segments=4):
 a=[]
 for yy,zz,start in [(cx+w/2-r,cz+h/2-r,0),(cx-w/2+r,cz+h/2-r,90),(cx-w/2+r,cz-h/2+r,180),(cx+w/2-r,cz-h/2+r,270)]:
  for j in range(segments+1):
   ang=math.radians(start+j*90/segments);a.append((yy+r*cos(ang),zz+r*sin(ang)))
 return a
def front_ring(name,cy,cz,w,h,th,ma,parent,offset=.035):
 outer=rounded_rect(cy,cz,w,h,.075);inner=rounded_rect(cy,cz,w-2*th,h-2*th,.04)
 v=[(nose_x(z)+offset,y,z) for a in (outer,inner) for y,z in a];n=len(outer)
 return mesh(name,v,[(j,(j+1)%n,n+(j+1)%n,n+j) for j in range(n)],ma,parent)
def torus(name,loc,R,r,ma,parent=body,rot=(0,0,0),n=32,m=8):
 v=[((R+r*cos(j*2*pi/m))*cos(i*2*pi/n),(R+r*cos(j*2*pi/m))*sin(i*2*pi/n),r*sin(j*2*pi/m)) for i in range(n) for j in range(m)]
 f=[(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m) for i in range(n) for j in range(m)]
 o=mesh(name,v,f,ma,parent);o.location=loc;o.rotation_euler=rot
 for p in o.data.polygons:p.use_smooth=True
 return o
# Structural underframe and machinery enclosure. Cab volumes remain genuinely hollow.
box('Main welded underframe',(0,0,1.44),(19.28,3.04,.32),'frame',b=.035)
box('Underframe upper deck',(0,0,1.65),(19.0,3.07,.12),'roof',b=.025)
for s in (-1,1):
 box('Full length side sill',(0,s*1.527,1.54),(18.90,.07,.16),'roof')
 box('Machinery room side',(0,s*1.502,2.61),(13.76,.058,1.85),'green',b=.008)
 box('Yellow waist stripe',(0,s*1.535,2.30),(13.8,.012,.215),'yellow',b=.002)
 box('Long roof shoulder',(0,s*1.399,3.68),(14.0,.31,.22),'roof',b=.11)
 # sheet seams and high roof rail are slender, not toy-like thick ridges
 for xx in (-6.75,-3.65,0,3.65,6.75):
  box('Welded bodyside seam',(xx,s*1.537,2.63),(.009,.004,1.82),'green2',b=0)
 for xx in (-4.3,4.3):
  box('Vent flange',(xx,s*1.545,3.12),(.74,.04,1.015),'roof')
  box('Vent dark well',(xx,s*1.557,3.12),(.63,.016,.91),'black',b=.006)
  for j in range(22):box('Vent horizontal louvre',(xx,s*1.569,2.70+j*.039),(.61,.012,.014),'bogie',b=.002)
  for z in (2.66,3.58):
   for x in (xx-.32,xx+.32):cyl('Vent flange fastener',(x,s*1.572,z),.011,.006,'steel',axis='Y',n=8)
 # Documentation-class numbers intentionally representative, not a claim to surveyed unit.
 rot=(pi/2,0,pi if s>0 else 0)
 text('Bodyside railway title','INDIAN RAILWAYS',(0,s*1.543,3.10),.37,'white',rot)
 text('Bodyside number','31034',(-5.65,s*1.546,1.94),.29,'white',rot)
 text('Bodyside class','WAG-9',(5.63,s*1.546,1.94),.22,'white',rot)
 text('Bodyside maintenance stencil','CLW  /  123 t',(-2.7,s*1.546,1.84),.069,'white',rot)
# Roof crown, subdivided service lids and gutters.
box('Central roof crown',(0,0,3.797),(14.0,2.65,.17),'roof',b=.08)
for x in (-4.8,-1.65,1.65,4.8):
 box('Removable roof panel',(x,0,3.886),(2.95,2.42,.035),'roof',b=.014)
 for y in (-1.12,1.12):
  for dx in (-1.34,1.34):
   box('Roof hatch lifting lug',(x+dx,y,3.922),(.09,.025,.075),'steel',b=.01)
 for y in (-.75,.75):
  box('Roof panel seam',(x,y,3.909),(2.83,.012,.006),'frame',b=0)
for s in (-1,1):
 box('Roof rain gutter',(0,s*1.47,3.71),(17.7,.055,.055),'silver')
 for x in (-3.0,0,3.0):
  box('Roof walkway plate',(x,s*1.13,3.929),(2.6,.23,.027),'frame',b=.005)
  for j in range(20):box('Walkway raised grip',(x-1.22+j*.125,s*1.13,3.946),(.012,.22,.006),'steel',b=0)
# Complete mirrored cabs, each authored in +X-facing local coordinates.
cabs=[]
for idx,end in enumerate((1,-1)):
 cab=empty('CAB_'+('A' if end==1 else 'B'),parent=body);cab.rotation_euler.z=0 if end==1 else pi;cabs.append(cab)
 box('Cab floor',(8.15,0,1.765),(2.93,2.88,.08),'cab',cab)
 box('Cab rear bulkhead',(6.92,0,2.68),(.065,2.9,1.80),'cab',cab)
 box('Machinery access door',(6.963,0,2.58),(.035,.71,1.52),'desk',cab)
 for y in (-.36,.36):rod('Inner door upright',(6.99,y,1.83),(6.99,y,3.35),.018,'silver',cab)
 box('Inner door handle',(7.011,-.25,2.54),(.06,.025,.14),'silver',cab)
 # Main front: separate opaque strips around clear aperture rectangles.
 panelpoly('Cab nose lower', [(-1.44,1.73),(1.44,1.73),(1.44,2.84),(-1.44,2.84)],.08,'green',cab)
 panelpoly('Cab front header',[(-1.43,3.57),(1.43,3.57),(1.31,3.77),(-1.31,3.77)],.08,'green',cab)
 panelpoly('Cab central windscreen pillar',[(-.095,2.84),(.095,2.84),(.095,3.58),(-.095,3.58)],.08,'green',cab)
 for side in (-1,1):
  panelpoly('Cab outer windscreen pillar',[(side*1.27,2.84),(side*1.45,2.84),(side*1.43,3.58),(side*1.27,3.58)],.08,'green',cab)
  # Corner transition sheets from front y=1.44 to body side y=1.50.
  vs=[]
  for z in (1.73,3.56):vs.extend([(nose_x(z),side*1.44,z),(nose_x(z)-.24,side*1.50,z)])
  mesh('Faceted cab corner',vs,[(0,1,3,2) if side>0 else (2,3,1,0)],'green',cab)
  # Cab side lower wall + aperture-built upper bands. No backing wall behind glass.
  box('Cab side lower wall forward',(8.555,side*1.501,2.22),(1.62,.07,.91),'green',cab)
  box('Cab side lower wall aft',(7.005,side*1.501,2.22),(.22,.07,.91),'green',cab)
  box('Cab side upper header',(8.10,side*1.47,3.58),(2.39,.09,.13),'green',cab)
  for x,w in [(7.015,.20),(7.87,.18),(8.85,.18)]:box('Cab side pillar',(x,side*1.50,3.03),(w,.075,1.02),'green',cab)
  # Close the tapered cab corner aft of the nose without covering side lookout glass.
  mesh('Cab side tapered corner closure',[(8.93,side*1.501,2.675),(nose_x(2.675)-.24,side*1.501,2.675),(nose_x(3.59)-.24,side*1.501,3.59),(8.93,side*1.501,3.59)],[(0,1,2,3) if side<0 else (3,2,1,0)],'green',cab)
  # Front side lookout glazing between x7.96..8.76.
  box('Side lookout lower sill',(8.36,side*1.514,2.713),(.82,.078,.045),'silver',cab)
  box('Side lookout upper sill',(8.36,side*1.514,3.521),(.82,.078,.045),'silver',cab)
  for x in (7.953,8.765):box('Side lookout window jamb',(x,side*1.514,3.117),(.037,.078,.825),'silver',cab)
  g=box('GLASS_side_lookout_'+str(idx)+'_'+str(side),(8.36,side*1.509,3.117),(.775,.012,.778),'glass',cab,b=.015);g['closed_glazing']=True
  box('Side sliding glass divider',(8.36,side*1.536,3.117),(.026,.032,.776),'silver',cab)
  # Door has a true upper glazing cutout and inset bottom panel.
  door=empty('CAB_'+str(idx+1)+'_DOOR_'+str(side)+'_HINGE',(7.105,side*1.515,1.77),cab);door['motion']='Optional inward hinge; closed pose is delivery default'
  box('Door lower leaf',(.30,0,.42),(.59,.036,.83),'green2',door)
  box('Door top rail',(.30,0,1.73),(.59,.036,.085),'green2',door)
  for dx in (.02,.58):box('Door window stile',(dx,0,1.26),(.07,.038,.88),'green2',door)
  box('Door glass seal',(.30,0,1.245),(.48,.017,.83),'black',door,b=.015)
  # Seal is a frame, remove opaque middle via four strips instead of backing.
  seal=bpy.data.objects.get('Door glass seal');bpy.data.objects.remove(seal,do_unlink=True)
  for dx in (.079,.521):box('Door glazing vertical seal',(dx,0,1.255),(.021,.021,.84),'black',door,b=.002)
  for zz in (.844,1.666):box('Door glazing horizontal seal',(.30,0,zz),(.46,.021,.022),'black',door,b=.002)
  g=box('GLASS_door_'+str(idx)+'_'+str(side),(.30,0,1.255),(.421,.012,.803),'glass',door,b=.014);g['closed_glazing']=True
  for zz in (.20,1.1,1.58):cyl('Door external hinge',(0,side*.028,zz),.022,.10,'silver',door)
  rod('Door latch',(.49,side*.035,.70),(.49,side*.035,.85),.012,'silver',door)
  for xx in (7.02,7.82):path('External door grabrail',[(xx,side*1.50,1.72),(xx,side*1.561,1.82),(xx,side*1.561,2.79),(xx,side*1.50,2.87)],.015,'silver',cab)
  for z in (1.03,1.27,1.51):
   box('Cab access step',(7.41,side*1.405,z),(.60,.32,.05),'bogie',cab)
   for j in range(8):box('Step tread serration',(7.16+j*.072,side*1.42,z+.029),(.025,.25,.01),'steel',cab,b=0)
  # side yellow band extends through closed door lower panel and front body
  box('Cab yellow waist stripe',(8.18,side*1.543,2.30),(2.05,.01,.215),'yellow',cab,b=.002)
  # triangular front yellow chevron band
  yz=[(side*.0,1.90),(side*.59,2.406),(side*1.447,2.406),(side*1.447,2.62),(side*.60,2.62),(side*.0,2.10)]
  o=panelpoly('Front yellow V',yz,.012,'yellow',cab);o.location.x=.056
  cy=side*.685
  front_ring('Windscreen black rubber',cy,3.205,1.20,.83,.04,'black',cab,.047)
  front_ring('Windscreen metal gasket',cy,3.205,1.23,.86,.016,'silver',cab,.053)
  # closed 12 mm planar glass slab fitted within aperture
  glassverts=[(nose_x(z)+d,y,z) for d in (.022,.034) for y,z in [(cy-.572,2.837),(cy+.572,2.837),(cy+.572,3.573),(cy-.572,3.573)]]
  g=mesh('GLASS_windscreen_'+str(idx)+'_'+str(side),glassverts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'glass',cab);g['closed_glazing']=True
  # Welded stone guard plus diagonal wiper beneath it.
  for j in range(12):
   yy=cy-.525+j*.0955;rod('Windscreen guard vertical',(nose_x(2.86)+.105,yy,2.86),(nose_x(3.55)+.105,yy,3.55),.0055,'steel',cab,n=6)
  for zz in (2.85,3.20,3.56):rod('Windscreen guard horizontal',(nose_x(zz)+.106,cy-.566,zz),(nose_x(zz)+.106,cy+.566,zz),.008,'silver',cab,n=8)
  path('Windscreen wiper',[(nose_x(2.77)+.068,cy,2.77),(nose_x(3.15)+.071,cy-.20,3.15),(nose_x(3.43)+.072,cy-.17,3.43)],.008,'black',cab)
  cyl('Wiper spindle',(nose_x(2.78)+.064,cy,2.78),.028,.045,'black',cab,axis='X',n=12)
  # marker lamps are distinct clear and red lenses.
  box('Marker lamp backing',(nose_x(2.47)+.075,side*.98,2.47),(.06,.16,.45),'frame',cab,b=.025)
  for z,ma,kind in [(2.61,'lens','WHITE'),(2.34,'red','TAIL')]:
   cyl('Marker chrome bezel',(nose_x(z)+.125,side*.98,z),.067,.035,'silver',cab,axis='X',n=24)
   cyl('LENS_'+kind+'_'+str(idx)+'_'+str(side),(nose_x(z)+.149,side*.98,z),.05,.014,ma,cab,axis='X',n=24)
   a=empty('LIGHT_'+kind+'_'+str(idx)+'_'+str(side),(nose_x(z)+.16,side*.98,z),cab);a['outward_axis']='+X local'
  text('Nose class' if side<0 else 'Nose number','WAG-9' if side<0 else '31034',(9.637,side*.85,1.98),.16 if side<0 else .23,'white',(pi/2,0,pi/2),cab)
 # Twin main headlight recessed pod.
 box('Dual headlamp recessed housing',(nose_x(2.50)+.057,0,2.50),(.083,.54,.30),'frame',cab,b=.025)
 for y in (-.135,.135):
  cyl('Headlamp machined bezel',(nose_x(2.50)+.108,y,2.50),.124,.042,'silver',cab,axis='X',n=32)
  cyl('LENS_HEAD_'+str(idx)+'_'+str(y),(nose_x(2.50)+.137,y,2.50),.100,.015,'lens',cab,axis='X',n=32)
  torus('Headlamp fine ring',(nose_x(2.50)+.147,y,2.50),.106,.006,'steel',cab,(0,pi/2,0))
  empty('LIGHT_HEAD_'+str(idx)+'_'+str(y),(nose_x(2.50)+.16,y,2.50),cab)
 path('Nose handrail',[(nose_x(1.85)+.08,-1.27,1.85),(nose_x(2.72)+.10,-1.27,2.72),(nose_x(2.74)+.10,1.27,2.74),(nose_x(1.85)+.08,1.27,1.85)],.016,'silver',cab)
 box('Front foot ledge',(9.66,0,1.70),(.32,2.81,.054),'steel',cab)
 for j in range(24):box('Nose ledge perforation',(9.68,-1.31+j*.113,1.731),(.15,.054,.003),'black',cab,b=0)
 # Roof over cab: horizontal cap and shoulder strips only above sightline.
 box('Cab roof',(8.14,0,3.742),(2.45,2.68,.155),'roof',cab,b=.075)
 for s in (-1,1):box('Cab roof shoulder',(8.05,s*1.38,3.65),(2.38,.25,.20),'roof',cab,b=.09)
 # Air horns, flasher and lifting mounts.
 for y,l in [(-.37,.41),(.37,.34)]:
  cyl('Horn stem',(8.35-l/2,y,3.92),.065,l,'roof',cab,axis='X',n=24)
  cyl('Horn mouth',(8.36,y,3.92),.117,.024,'steel',cab,axis='X',n=24)
  cyl('Horn dark bell',(8.374,y,3.92),.093,.008,'black',cab,axis='X',n=24)
 cyl('Flasher pedestal',(8.20,0,3.875),.072,.12,'black',cab)
 cyl('Flasher amber lens',(8.20,0,3.966),.062,.08,'orange',cab)
 # Furnished cab with two seats, desk, dials, diagnostic terminal and labels.
 box('Control desk lower pedestal',(8.77,0,2.18),(.57,2.47,.72),'desk',cab,b=.055)
 desk=box('Sloped desk top',(8.59,0,2.59),(.81,2.48,.085),'desk',cab,b=.028);desk.rotation_euler.y=-.16
 box('Instrument vertical fascia',(8.967,0,2.81),(.06,2.40,.29),'panel',cab,b=.025)
 # Faces are aimed toward cab (negative X); needles and graduations are real geometry.
 for k,(yy,zz,rr,label) in enumerate([(-.93,2.83,.090,'BP'),(-.68,2.83,.090,'FP'),(-.40,2.83,.084,'BC'),(.78,2.82,.108,'km/h')]):
  cyl('Gauge bezel',(8.921,yy,zz),rr+.013,.022,'steel',cab,axis='X',n=32)
  cyl('Gauge dial',(8.905,yy,zz),rr,.009,'dial',cab,axis='X',n=32)
  for j in range(12):
   a=j*2*pi/12;rod('Gauge tick',(8.899,yy+(rr-.010)*cos(a),zz+(rr-.010)*sin(a)),(8.899,yy+(rr-.022)*cos(a),zz+(rr-.022)*sin(a)),.002,'black',cab,n=6)
  rod('Gauge needle',(8.895,yy,zz),(8.895,yy+rr*.65*cos(2.2+k*.4),zz+rr*.65*sin(2.2+k*.4)),.003,'red',cab,n=6)
  text('Gauge label',label,(8.889,yy,zz-.043),.018,'black',(pi/2,0,-pi/2),cab)
 box('Diagnostic terminal bezel',(8.91,.20,2.84),(.08,.49,.28),'black',cab,b=.016)
 box('Diagnostic terminal screen',(8.859,.20,2.85),(.005,.40,.19),'blue',cab,b=.004)
 text('Diagnostic display','SYSTEM READY',(8.852,.20,2.875),.028,'white',(pi/2,0,-pi/2),cab)
 text('Diagnostic screen telemetry','25 kV   |   0 km/h',(8.852,.20,2.81),.022,'white',(pi/2,0,-pi/2),cab)
 # Original generic controls reflecting legacy WAG-9 arrangements, not operational exactness.
 for row in range(2):
  for j in range(9):
   yy=-1.08+j*.265;xx=8.40+row*.18;z=2.64+(xx-8.59)*.16
   cyl('Switch chrome collar',(xx,yy,z+.012),.024,.011,'silver',cab,n=16)
   cyl('Control switch cap',(xx,yy,z+.029),.016,.024,'red' if j==7 else ('orange' if j%4==0 else 'black'),cab,n=12)
   text('Control label',['ZPT','BLDJ','BLCP','BLHO','BPCS','WIPER','LIGHT','STOP','SAND'][j],(xx-.052,yy,z+.012),.019,'white',(0,0,pi/2),cab)
 for y in (-.70,.73):
  box('Controller slotted base',(8.26,y,2.65),(.17,.22,.028),'panel',cab,b=.01)
  rod('Controller handle',(8.26,y,2.665),(8.22,y,2.79),.012,'steel',cab)
  box('Controller grip',(8.22,y,2.80),(.06,.11,.036),'black',cab,b=.018)
 for s in (-1,1):
  y=s*.76
  cyl('Seat mounting pedestal',(7.72,y,1.982),.092,.38,'steel',cab)
  box('Seat slide frame',(7.72,y,2.16),(.49,.48,.065),'frame',cab)
  box('Seat cushion',(7.74,y,2.242),(.51,.52,.12),'seat',cab,b=.057)
  back=box('Seat backrest',(7.45,y,2.58),(.10,.53,.63),'seat',cab,b=.047);back.rotation_euler.y=-.11
  for yy in (y-.31,y+.31):
   rod('Seat armrest support',(7.5,yy,2.23),(7.5,yy,2.50),.016,'steel',cab)
   box('Seat arm pad',(7.66,yy,2.505),(.40,.065,.055),'seat',cab,b=.025)
  for xx in (8.10,8.26):
   ob=box('Driver foot pedal',(xx,y,1.96),(.16,.21,.035),'black',cab,b=.008);ob.rotation_euler.y=.20
  if s==-1:
   driver=empty('DRIVER_'+str(idx+1).zfill(3),(7.69,y,2.302-.483),cab);driver['role']='Seated character root, +X forward';driver['seat_cushion_top_z_m']=2.302;driver['assumed_hip_offset_m']=.483;driver['rear_cab_forward_mapping_requires_review']=bool(end==-1)
   eye=empty('CAB_EYE_CAMERA_REFERENCE_'+str(idx+1),(7.78,y,3.10),cab);eye['purpose']='Authoring view only; no game camera field'
 # cab fans, sun blinds and ceiling lighting
 for y in (-.80,.80):
  box('Windscreen sunblind cassette',(9.12,y,3.59),(.07,.94,.07),'cab',cab)
  box('Sunblind fabric',(9.12,y,3.51),(.009,.88,.13),'seat',cab,b=.002)
  cyl('Cab fan cage',(7.10,y,3.29),.135,.065,'steel',cab,axis='X',n=32)
  cyl('Cab fan dark interior',(7.14,y,3.29),.12,.012,'black',cab,axis='X',n=24)
  for j in range(12):
   a=j*pi/6;rod('Fan cage spoke',(7.152,y,3.29),(7.152,y+.126*cos(a),3.29+.126*sin(a)),.0025,'silver',cab,n=6)
  box('Cab ceiling light',(7.75,y,3.64),(.48,.12,.025),'lens',cab,b=.018)
 box('Cab fire extinguisher bracket',(7.05,1.15,2.1),(.09,.25,.47),'frame',cab)
 cyl('Cab fire extinguisher',(7.15,1.15,2.17),.085,.38,'red',cab,n=20)
 cyl('Fire extinguisher neck',(7.15,1.15,2.39),.036,.075,'steel',cab,n=12)
# Co-Co bogies, independent yaw groups, axles and wheel rolls.
for k,x0 in [('A',6.0),('B',-6.0)]:
 bg=empty('BOGIE_'+k+'_YAW_Z',(x0,0,0),root);bg['pivot_axis']='Z';bg['wheelbase_m']=3.7
 for sy in (-1,1):
  # Upper forged rail plus lowered portions and bearing carriers.
  box('Bogie cast longitudinal beam',(0,sy*1.16,1.08),(4.68,.24,.27),'bogie',bg,b=.052)
  for xx in (-2.18,2.18):box('Bogie end casting',(xx,sy*1.16,.89),(.34,.26,.40),'bogie',bg,b=.055)
  for xx in (-.94,.94):
   box('Bogie spring cradle',(xx,sy*1.16,.82),(.50,.32,.18),'bogie',bg,b=.04)
   for yy in (sy*1.02,sy*1.29):
    pts=[(xx+.085*cos(t*.5*pi),yy+.085*sin(t*.5*pi),.91+t*.019) for t in range(24)]
    path('Secondary helical spring',pts,.013,'frame',bg,n=8)
   rod('Vertical suspension damper',(xx-.23,sy*1.32,.70),(xx-.15,sy*1.32,1.31),.034,'steel',bg,n=12)
  for xx in (-1.85,0,1.85):
   box('Axlebox bearing housing',(xx,sy*1.24,.55),(.37,.21,.32),'bogie',bg,b=.05)
   cyl('Axlebox bolted cover',(xx,sy*1.36,.55),.122,.045,'roof',bg,axis='Y',n=24)
   for j in range(6):
    a=j*pi/3;cyl('Axlebox cover bolt',(xx+.086*cos(a),sy*1.39,.55+.086*sin(a)),.012,.009,'steel',bg,axis='Y',n=6)
   for dx in (-.26,.26):
    cyl('Primary spring cap',(xx+dx,sy*1.17,.72),.105,.05,'steel',bg,n=16)
    pts=[(xx+dx+.075*cos(j*pi/2),sy*1.17+.075*sin(j*pi/2),.74+j*.012) for j in range(20)]
    path('Primary coil spring',pts,.013,'frame',bg,n=8)
   # Brake blocks and visible rigging just clear the wheel profile.
   for dx in (-.58,.58):
    box('Brake shoe',(xx+dx,sy*.93,.60),(.095,.16,.26),'grime',bg,b=.02)
    rod('Brake hanger',(xx+dx,sy*1.0,.71),(xx+dx-.05,sy*1.0,1.10),.024,'frame',bg,n=10)
  rod('Bogie traction link',(-2.0,sy*1.35,.68),(2.0,sy*1.35,.91),.032,'steel',bg,n=12)
  for xx in (-2.18,2.18):
   box('Sand hopper',(xx,sy*1.09,1.26),(.37,.40,.29),'bogie',bg,b=.045)
   path('Sand delivery pipe',[(xx,sy*1.02,1.12),(xx+.10,sy*1.02,.75),(xx+.20,sy*.86,.16)],.018,'steel',bg,n=8)
 for xx in (-1.10,1.10):box('Bogie transverse bolster',(xx,0,1.12),(.29,2.4,.22),'bogie',bg,b=.04)
 cyl('Bogie centre yaw pivot',(0,0,1.20),.38,.23,'frame',bg,n=24)
 for j,xx in enumerate((-1.85,0,1.85),1):
  ax=empty('AXLE_'+k+'_'+str(j)+'_ROLL_Y',(xx,0,.546),bg);ax['spin_axis']='Y';ax['nominal_wheel_diameter_m']=1.092
  cyl('Wheelset axle',(0,0,0),.105,2.37,'steel',ax,axis='Y',n=24)
  for sy in (-1,1):
   # Lathed tyre profile: tread on z=0; inward flange extends 28 mm below rail top.
   prof=[(.785,.455),(.798,.574),(.827,.574),(.846,.546),(.978,.546),(.996,.51),(.996,.325),(.930,.305),(.908,.16),(.82,.16)]
   vv=[(rr*cos(i*2*pi/48),sy*yy,rr*sin(i*2*pi/48)) for yy,rr in prof for i in range(48)]
   ff=[(q*48+i,q*48+(i+1)%48,((q+1)%len(prof))*48+(i+1)%48,((q+1)%len(prof))*48+i) for q in range(len(prof)) for i in range(48)]
   wh=mesh('Wheel_'+k+str(j)+'_'+str(sy),vv,ff,'rim',ax)
   for p in wh.data.polygons:p.use_smooth=True
   cyl('Wheel hub',(0,sy*.957,0),.185,.15,'frame',ax,axis='Y',n=24)
   cyl('Wheel hub cap',(0,sy*1.04,0),.083,.03,'steel',ax,axis='Y',n=16)
  cyl('Axle hung traction motor',(xx+.21,0,.72),.26,1.46,'frame',bg,axis='Y',n=24)
  box('Gearcase',(xx+.20,.49,.66),(.54,.28,.69),'bogie',bg,b=.14)
# Central underfloor transformer and air systems.
box('Main transformer belly',(0,0,.91),(3.24,2.16,.91),'frame',b=.06)
for sy in (-1,1):
 box('Transformer cooler side',(0,sy*1.10,.94),(2.67,.08,.69),'bogie',b=.015)
 for x in [i*.12-1.26 for i in range(22)]:box('Transformer cooling rib',(x,sy*1.17,.94),(.03,.12,.68),'frame',b=.006)
 for xx in (-3.1,3.1):
  cyl('Main air reservoir',(xx,sy*.94,.93),.245,1.76,'bogie',axis='X',n=32)
  for dx in (-.60,.60):torus('Reservoir retaining strap',(xx+dx,sy*.94,.93),.254,.018,'steel',rot=(0,pi/2,0),n=24)
  path('Air reservoir feed',[(xx+.73,sy*.94,1.10),(xx+.93,sy*.94,1.1),(xx+.93,sy*1.28,1.31)],.018,'copper')
 for xx in (-4.15,4.15):box('Battery service enclosure',(xx,sy*.97,1.06),(1.10,.66,.61),'frame',b=.025)
# Buffer, CBC knuckle, brake hoses, uncoupling gear and pilot sheets.
for end in (1,-1):
 e=empty('END_A_COUPLER_ASSEMBLY' if end==1 else 'END_B_COUPLER_ASSEMBLY',parent=body);e.rotation_euler.z=0 if end==1 else pi
 box('Headstock',(9.63,0,1.24),(.25,3.03,.57),'bogie',e,b=.025)
 # Pilot wide trapezoid, flat metal sheet below buffer beam.
 vv=[(9.70,y,z) for y,z in [(-1.43,1.0),(1.43,1.0),(1.28,.26),(.94,.19),(-.94,.19),(-1.28,.26)]]
 pilot=mesh('Pilot scraper sheet',vv,[(0,1,2,3,4,5)],'roof',e);sol=pilot.modifiers.new('Pilot plate thickness','SOLIDIFY');sol.thickness=.025
 for y in (-.98,-.49,0,.49,.98):rod('Pilot stiffener',(9.66,y,.33),(9.66,y,.97),.025,'frame',e)
 for sy in (-1,1):
  cyl('Buffer stock',(9.86,sy*1.025,1.105),.129,.39,'frame',e,axis='X',n=24)
  cyl('Buffer telescopic shaft',(10.10,sy*1.025,1.105),.087,.18,'steel',e,axis='X',n=24)
  cyl('Buffer face',(10.240,sy*1.025,1.105),.224,.08,'steel',e,axis='X',n=40)
  cyl('Buffer face wear plate',(10.2805,sy*1.025,1.105),.207,.001,'bogie',e,axis='X',n=40)
  for yy in (sy*.48,sy*.72):
   box('Pneumatic end cock',(9.82,yy,1.13),(.12,.095,.12),'bogie',e)
   path('Flexible brake hose',[(9.86,yy,1.1),(10.00,yy,.84),(9.98,yy,.64),(9.85,yy+.09,.57),(9.78,yy+.15,.72)],.032,'black',e,n=10)
   cyl('Hose coupling end',(9.78,yy+.15,.73),.049,.11,'steel',e,n=12)
   rod('End cock colored lever',(9.89,yy,1.18),(9.89,yy+.09,1.20),.018,'red' if abs(yy)<.6 else 'yellow',e)
 path('Uncoupling lever',[(9.80,-1.23,1.35),(9.83,-.65,1.35),(9.88,-.25,1.18)],.018,'silver',e)
 box('CBC draft gear',(9.82,0,1.105),(.67,.28,.30),'frame',e,b=.04)
 # asymmetric head casting leaves a real knuckle opening; model mating X is 10.281.
 vs=[(x,y,z) for x in (10.03,10.281) for y,z in [(-.18,.95),(.11,.95),(.20,1.03),(.20,1.22),(.02,1.26),(-.18,1.19)]]
 kn=mesh('CBC knuckle fixed casting',vs,[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)],'bogie',e,.025)
 box('CBC knuckle recess',(10.288,.03,1.105),(.012,.16,.18),'black',e,b=.025)
 box('CBC locking knuckle',(10.295,-.10,1.12),(.052,.09,.28),'steel',e,b=.028)
 cyl('CBC knuckle hinge pin',(10.16,-.11,1.13),.042,.37,'steel',e,n=16)
 path('CBC release chain',[(9.96,-.12,1.15),(9.88,-.14,.83),(9.75,-.18,.78)],.009,'steel',e,n=6)
 anchor=empty('COUPLING_FRONT' if end==1 else 'COUPLING_REAR',(end*10.281,0,1.105),root);anchor.rotation_euler.z=0 if end==1 else pi;anchor['mating_plane']='CBC visual spacing convention';anchor['not_mesh_envelope']=True
# HV roof line, disconnectors and ceramic insulators.
def insulator(name,x,y,z,h=.22,r=.07,parent=body):
 cyl(name+' core',(x,y,z+h/2),r*.65,h,'ceramic',parent,n=16)
 for i in range(6):cyl(name+' rib',(x,y,z+.018+i*(h-.03)/5),r,.015,'ceramic',parent,n=20)
 cyl(name+' foot',(x,y,z),r*1.08,.025,'steel',parent,n=16)
for x in (-3.65,-1.7,.5,2.5,3.7):
 insulator('HV bus support',x,.20,3.92,.22,.075)
path('Copper roof bus',[(-5.05,.20,4.15),(-3.65,.20,4.15),(-1.7,.20,4.15),(.5,.20,4.15),(2.5,.20,4.15),(5.05,.20,4.15)],.021,'copper',n=12)
box('Vacuum breaker cabinet',(-.5,-.40,3.99),(.80,.53,.20),'roof',b=.04)
for x in (-.74,-.28):insulator('Vacuum breaker bushing',x,-.40,4.02,.20,.07)
rod('Vacuum breaker crossbar',(-.74,-.4,4.23),(-.28,-.4,4.23),.024,'copper')
for xx in (-2.4,2.4):
 insulator('Lightning arrester',xx,-.57,3.92,.30,.083)
 path('Arrester roof lead',[(xx,-.57,4.23),(xx,.20,4.23),(xx,.20,4.15)],.018,'copper')
# Rigid pantographs. Same theta on opposing segments; head exactly level at any extension.
L1,L2,ZBASE,STRIP=1.38,1.15,4.105,.044
A0=math.asin((4.255-ZBASE-STRIP)/(L1+L2));A1=math.asin((5.917-ZBASE-STRIP)/(L1+L2));rigs={}
for side,x,az in [('FRONT',5.2,0),('REAR',-5.2,pi)]:
 pre='PANTO_'+side;ctrl=empty(pre+'_CTRL',(x,0,ZBASE),body);ctrl.rotation_euler.z=az
 ctrl['extension']=0.;ctrl.id_properties_ui('extension').update(min=0.,max=1.,description='Independent extension. 0:4.255m strip top; 1:5.917m strip top.')
 ctrl['lower_length_m']=L1;ctrl['upper_length_m']=L2;ctrl['strip_top_offset_m']=STRIP;ctrl['lower_angle_rad']=A0;ctrl['raised_angle_rad']=A1
 lo=empty(pre+'_LOWER_PIVOT',parent=ctrl);up=empty(pre+'_ELBOW_PIVOT',(L1,0,0),lo);he=empty(pre+'_HEAD_LEVEL_PIVOT',(-L2,0,0),up)
 for o,factor in [(lo,-1),(up,2),(he,-1)]:
  d=o.driver_add('rotation_euler',1).driver;d.type='SCRIPTED';v=d.variables.new();v.name='e';v.targets[0].id=ctrl;v.targets[0].data_path='["extension"]';d.expression=f'{factor}*({A0}+(max(0,min(1,e)))*{A1-A0})'
 for yy in (-.47,.47):
  box(pre+'_BASE_RAIL',(.45,yy,-.045),(1.50,.07,.065),'panto',ctrl)
  for xx in (-.10,.98):insulator(pre+'_MOUNT',xx,yy,-.185,.135,.063,ctrl)
  rod(pre+'_LOWER_ARM',(0,yy*.78,0),(L1,yy*.78,0),.028,'panto',lo,n=12)
 for yy in (-.27,.27):rod(pre+'_UPPER_ARM',(0,yy,0),(-L2,yy,0),.021,'panto',up,n=12)
 for xx in (.18,.56,1.14):rod(pre+'_LOWER_CROSSBAR',(xx,-.37,0),(xx,.37,0),.012,'panto',lo)
 rod(pre+'_LOWER_DIAGONAL',(.14,-.37,0),(1.20,.37,0),.013,'panto',lo)
 rod(pre+'_UPPER_CROSSBAR',(-.96,-.27,0),(-.96,.27,0),.012,'panto',up)
 for pa,r in [(ctrl,.04),(up,.035),(he,.025)]:
  rod(pre+'_HINGE_SHAFT',(0,-.49,0),(0,.49,0),r,'steel',pa,n=16)
  for y in (-.48,.48):cyl(pre+'_HINGE_CAP',(0,y,0),r*1.3,.04,'steel',pa,axis='Y',n=16)
 for yy in (-.27,.27):
  path(pre+'_HEAD_SPRING',[(0,yy,0),(-.10,yy,.022),(.10,yy,.035)],.011,'steel',he)
 box(pre+'_HEAD_CARRIER',(0,0,.021),(.30,1.72,.030),'steel',he,b=.005)
 for i,xx in enumerate((-.105,.105),1):
  box(pre+'_CONTACT_STRIP_'+str(i),(xx,0,.037),(.052,1.67,.014),'carbon',he,b=.003)
  for sy in (-1,1):path(pre+'_CONTACT_HORN',[(xx,sy*.835,.034),(xx,sy*.96,.011),(xx,sy*1.05,-.045)],.011,'carbon',he,n=10)
 # actuator hardware stays at base, visually independent of moving mechanism
 cyl(pre+'_PNEUMATIC_CYLINDER',(.15,0,-.052),.062,.48,'steel',ctrl,axis='X',n=20)
 rigs[side]=(ctrl,lo,up,he)
print('GEOMETRY_CREATED',len(asset.objects),flush=True)
# Apply bevels and convert text to meshes so exports contain no evaluated surprises.
bpy.context.view_layer.update()
for o in list(asset.objects):
 if o.type=='FONT':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
for o in list(asset.objects):
 if o.type=='MESH' and o.modifiers:
  bpy.context.view_layer.objects.active=o
  for m in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=m.name)
   except Exception as ex:print('MODIFIER WARNING',o.name,str(ex))
print('MODIFIERS_APPLIED',flush=True)
# Recalculate manifold normals independently (especially mirrored wheel/corner facets).
import bmesh
for o in asset.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Presentation gallery: railway slab, two broad-gauge rails and low-key studio stage.
stage_mat=mat('STAGE_concrete',(.145,.166,.174),.08,.85)
def stage_obj(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 stage.objects.link(o);o.parent=None;return o
stage_obj(box('DISPLAY_GROUND',(0,0,-.20),(200,200,.22),stage_mat,parent=None,b=0))
for y in (-.873,.873):
 stage_obj(box('DISPLAY_RAIL_HEAD',(0,y,-.036),(29,.07,.072),'steel',parent=None,b=.013))
 stage_obj(box('DISPLAY_RAIL_WEB',(0,y,-.095),(29,.02,.095),'frame',parent=None,b=.005))
for j in range(44):stage_obj(box('DISPLAY_SLEEPER',(-13.8+j*.64,0,-.16),(.24,2.75,.09),'frame',parent=None,b=.015))
world=bpy.data.worlds.new('Studio ambient') if not bpy.data.worlds else bpy.data.worlds[0];sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.24,.30,1);world.node_tree.nodes['Background'].inputs[1].default_value=.36
for name,loc,energy,size in [('Key softbox',(4,-9,14),3100,9),('Long roof fill',(-4,5,11),2400,8),('Front rim',(12,4,7),1600,6)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.8))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,lens=48):
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.03;d.clip_end=400;o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cams={
 'exterior':camera('CAM_Exterior_three_quarter',(19,-24,11),(0,0,2.0),48),
 'front':camera('CAM_Front_detail',(15,-9,5.4),(7.4,0,2.25),48),
 'side':camera('CAM_Side_elevation',(0,-30,4),(0,0,2.2),43),
 'cab_a':camera('CAM_Cab_A',(7.30,.94,3.20),(8.95,-.25,2.64),20),
 'cab_b':camera('CAM_Cab_B',(-7.30,-.94,3.20),(-8.95,.25,2.64),20),
 'roof':camera('CAM_Roof_pantograph',(10,-9,9),(4.5,0,4.6),49),
}
for idx,cab in enumerate(cabs):
 ld=bpy.data.lights.new('CAB_REVIEW_FILL_'+str(idx),'AREA');ld.energy=110;ld.shape='DISK';ld.size=1.2;lo=bpy.data.objects.new(ld.name,ld);stage.objects.link(lo);lo.location=(8.0 if idx==0 else -8.0,0,3.54)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=48;sc.cycles.use_denoising=False
sc.render.resolution_x=1800;sc.render.resolution_y=1050;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.render.film_transparent=False
# QA with measured geometry, links, strip surfaces and clear sight rays.
def pose(f,r):
 for name,val in [('FRONT',f),('REAR',r)]:rigs[name][0]['extension']=val;rigs[name][0].update_tag()
 bpy.context.view_layer.update()
def rig_measure():
 out={}
 for n,(ctrl,lo,up,he) in rigs.items():
  pts=[]
  for i in (1,2):
   ob=bpy.data.objects['PANTO_'+n+'_CONTACT_STRIP_'+str(i)];pts += [ob.matrix_world@v.co for v in ob.data.vertices]
  upvec=he.matrix_world.to_3x3()@Vector((0,0,1))
  out[n]={'strip_top_m':max(p.z for p in pts),'strip_top_level_spread_m':max(p.z for p in pts)-sorted(p.z for p in pts)[-4], 'lower_length_m':(lo.matrix_world.translation-up.matrix_world.translation).length,'upper_length_m':(up.matrix_world.translation-he.matrix_world.translation).length,'head_up_vector':list(upvec),'head_pivot_world_m':list(he.matrix_world.translation)}
 return out
qa={'prototype_sources':['CLW Driver manual 3EHW411172 Ver-1 ch2 p4','RDSO WAG9 specification'], 'latest_repo_base':'7de48a11bd95a69e03acb16043629b40a89f35ec','unit_scale':sc.unit_settings.scale_length,'root_matrix':[list(r) for r in root.matrix_world],'coupling':{},'rig_sweeps':[]}
for a in range(11):
 pose(a/10,1-a/10);m=rig_measure();qa['rig_sweeps'].append({'extensions':[a/10,1-a/10],'measurements':m})
 for q in m.values():
  assert abs(q['lower_length_m']-L1)<1e-5 and abs(q['upper_length_m']-L2)<1e-5
  assert (Vector(q['head_up_vector'])-Vector((0,0,1))).length<1e-5
pose(0,0)
for n in ('COUPLING_FRONT','COUPLING_REAR'):
 o=bpy.data.objects[n];qa['coupling'][n]={'position_m':list(o.matrix_world.translation),'outward_normal':list(o.matrix_world.to_3x3()@Vector((1,0,0))),'parent':o.parent.name}
qa['coupling']['mating_span_m']=(bpy.data.objects['COUPLING_FRONT'].matrix_world.translation-bpy.data.objects['COUPLING_REAR'].matrix_world.translation).length
meshes=[o for o in asset.objects if o.type=='MESH'];allpts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
qa['evaluated_bounds_lowered']={'min':[min(v[i] for v in allpts) for i in range(3)],'max':[max(v[i] for v in allpts) for i in range(3)]}
qa['mesh_objects']=len(meshes);qa['triangles']=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons);qa['asset_materials']=len({m.name for o in meshes for m in o.data.materials});qa['bogies']=[o.name for o in asset.objects if '_YAW_Z' in o.name];qa['axles']=[o.name for o in asset.objects if '_ROLL_Y' in o.name]
qa['sole_parentless_root']=[o.name for o in asset.objects if o.parent is None];assert qa['sole_parentless_root']==['WAG9_ROOT'];assert qa['asset_materials']<=64
qa['closed_glass']=[]
for o in meshes:
 if o.name.startswith('GLASS_'):
  bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free();qa['closed_glass'].append({'name':o.name,'nonmanifold_edges':bad});assert bad==0
qa['driver_markers']=[{'name':o.name,'world_m':list(o.matrix_world.translation),'seat_cushion_top_m':o['seat_cushion_top_z_m'],'hip_offset_m':o['assumed_hip_offset_m']} for o in asset.objects if o.name.startswith('DRIVER_')]
qa['passed']=True
(OUT/'qa/mesh_rig_validation.json').write_text(json.dumps(qa,indent=2))
# Saved master retains live drivers and uncluttered collection separation.
sc.camera=cams['exterior'];sc.frame_start=1;sc.frame_end=161
for n,f in [('BOTH_LOWERED',1),('FRONT_ONLY_RAISED',41),('BOTH_RAISED',81),('REAR_ONLY_RAISED',121),('BOTH_LOWERED_END',161)]:sc.timeline_markers.new(n,frame=f)
readme=bpy.data.texts.new('WAG9_START_HERE');readme.write('Original WAG-9 modelling handoff. Metres. +X forward. Z=0 tread. Select PANTO_FRONT_CTRL or PANTO_REAR_CTRL and set extension 0..1. Strip tops 4.255m to5.917m. CBC mating anchors ±10.281m at1.105m. See external README.md and qa files. Presentation collection is NOT exported. Driver roots provisional; rear mapping requires converter review.')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAG9_master.blend'),compress=True)
def export(name,anim=False):
 bpy.ops.object.select_all(action='DESELECT')
 for o in asset.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=root
 m=M['glass'];p=m.node_tree.nodes['Principled BSDF'];saved=(tuple(m.diffuse_color),tuple(p.inputs['Base Color'].default_value),p.inputs['Alpha'].default_value)
 m.diffuse_color=(*saved[0][:3],.25);p.inputs['Base Color'].default_value=(*saved[1][:3],.25);p.inputs['Alpha'].default_value=.25
 bpy.ops.export_scene.fbx(filepath=str(OUT/name),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_space_transform=False,add_leaf_bones=False,bake_anim=anim,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,path_mode='AUTO',use_custom_props=True)
 m.diffuse_color=saved[0];p.inputs['Base Color'].default_value=saved[1];p.inputs['Alpha'].default_value=saved[2]
export('WAG9_lowered.fbx')
pose(1,1);export('WAG9_raised.fbx');pose(0,0)
# Render gallery from live scene before baking.
for key in (() if os.environ.get('WAG9_SKIP_RENDER') else ('exterior','front','side','cab_a','cab_b','roof')):
 if key in ('exterior','roof'):pose(0,1 if key=='exterior' else 0);pose(1 if key=='roof' else 0,1 if key=='exterior' else 0)
 else:pose(0,0)
 sc.cycles.samples=128 if key in ('cab_a','cab_b') else 64
 sc.camera=cams[key];sc.render.filepath=str(OUT/'renders'/('WAG9_'+key+'.png'));sc.render.resolution_x=1800 if key not in ('cab_a','cab_b') else 1400;sc.render.resolution_y=1050 if key not in ('cab_a','cab_b') else 1000
 bpy.ops.render.render(write_still=True)
pose(0,0)
# Bake independent motion poses to portable rigid EMPTY transforms.
for ctrl,lo,up,he in rigs.values():
 for o in (lo,up,he):o.driver_remove('rotation_euler',1)
for f in range(1,162):
 front=min(1,max(0,(f-1)/40)) if f<=81 else max(0,1-(f-81)/40)
 rear=max(0,min(1,(f-41)/40)) if f<=121 else max(0,1-(f-121)/40)
 for n,e in [('FRONT',front),('REAR',rear)]:
  ctrl,lo,up,he=rigs[n];a=A0+(A1-A0)*e
  for o,v in [(lo,-a),(up,2*a),(he,-a)]:o.rotation_euler.y=v;o.keyframe_insert(data_path='rotation_euler',frame=f,group=n+'_PANTOGRAPH')
for o in asset.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
sc.frame_set(1);sc.camera=cams['exterior'];bpy.context.view_layer.update()
export('WAG9_motion.fbx',True);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAG9_baked_motion.blend'),compress=True)
(OUT/'qa/build_complete.json').write_text(json.dumps({'status':'complete','triangles':qa['triangles'],'mesh_objects':qa['mesh_objects'],'rig_parameters':{'L1':L1,'L2':L2,'base':ZBASE,'strip_offset':STRIP,'a0':A0,'a1':A1}},indent=2))
import zipfile
with zipfile.ZipFile(OUT/'WAG9_motion.fbx.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:archive.write(OUT/'WAG9_motion.fbx','WAG9_motion.fbx')
print('BUILD_COMPLETE',qa['triangles'],qa['mesh_objects'])
