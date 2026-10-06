"""Editable representative WAP-7 HOG machinery-room visual assemblies.

The plan follows the inspected SKEL-5051 Alt.2 WAP7 WITH HOTEL LOAD CONVERTER
layout. Cabinet forms and small hardware are class-level visual interpretations,
not a surveyed 39002 installation. No Kavach overlay equipment is reproduced.

API: apply(context=None). All additions use MACHV02_. Source meshes, roots,
external shell, view layers, cameras, lights and files are never modified here.
"""
import bpy, math, json
from pathlib import Path
from math import sin, cos, pi
from mathutils import Vector, Matrix

PREFIX='MACHV02_'
SOURCE_PLAN='https://iriset.railnet.gov.in/content/CoE/docs/All%20Electrical%20Locos_Kavach%20Fitment_Interface%20drawings.pdf'
SOURCE_PHOTO='https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/6/3/6/1366636/0/machineroomofawap7227181.jpg'
SOURCE_HLC='https://www.scribd.com/document/470581078/131008-001-Final-Specification-of-Hotel-load-IGBT-Alt'
SOURCE_DUCT='https://clw.indianrailways.gov.in/uploads/Draft%20Specification%20of%20_Transition%20Duct%20Assembly%281%29.pdf'


def material(name,color,metal=0,rough=.5,noise=0):
 n=PREFIX+name;m=bpy.data.materials.get(n)
 if m:return m
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*color,1)
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if noise:
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=2
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.00036
  nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m


def palette():
 m={
 'wall':material('Grey green structural enamel',(.27,.299,.276),.14,.59,170),
 'cabinet':material('Warm grey equipment enamel',(.29,.322,.297),.18,.47,320),
 'door':material('Satin folded door panel',(.275,.305,.281),.18,.48,310),
 'blower':material('Old pale blue blower enamel',(.26,.389,.386),.24,.47,230),
 'cooler':material('Oil cooler grey enamel',(.345,.382,.352),.25,.47,320),
 'steel':material('Satin zinc fasteners',(.32,.35,.34),.76,.32,600),
 'aluminium':material('Pressed aluminium cable trays',(.42,.446,.433),.76,.42,330),
 'black':material('Recessed vent darkness',(.005,.008,.006),.05,.87),
 'rubber':material('Black cable insulation',(.021,.027,.023),.0,.76,150),
 'brass':material('Muted brass pipe fittings',(.285,.23,.114),.73,.38,350),
 'pipe':material('Grey steel pipe enamel',(.205,.237,.210),.55,.44,340),
 'red':material('Muted red valve enamel',(.31,.038,.026),.25,.47),
 'ivory':material('Faded equipment legend',(.73,.76,.686),.04,.61),
 'motor':material('Motor dark green enamel',(.072,.14,.115),.25,.50,210),
 'glass':material('Inspection glass',(.24,.30,.25),.25,.25),
 'diffuser':material('Fluorescent opal diffuser',(.72,.76,.694),0,.4),
 'floor':material('Worn chequer plate steel',(.29,.321,.293),.72,.53,380),
 'edge':material('Dark folded channel edges',(.12,.15,.127),.5,.5),
 }
 for key in['wall','cabinet','door','blower','cooler','pipe','motor','red','ivory','edge','black']:
  dielectric_enamel(m[key])
 for key in['steel','aluminium','brass','floor']:
  m[key].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=1.0
 glass=m['glass'].node_tree.nodes.get('Principled BSDF');glass.inputs['Metallic'].default_value=0;glass.inputs['Base Color'].default_value=(.94,.96,.93,1);glass.inputs['Roughness'].default_value=.08;glass.inputs['Transmission Weight'].default_value=1;glass.inputs['IOR'].default_value=1.48
 return m


class Builder:
 """World-space geometry with batched tiny details to keep editing responsive."""
 def __init__(self,body,coll,m,half_width=1.40):self.body=body;self.coll=coll;self.m=m;self.created=[];self.batches={};self.equipment=[];self.half_width=half_width
 def obj(self,n,v,f,mat,b=0,smooth=False,batch=False):
  if batch:
   key=(n,mat)
   if key not in self.batches:self.batches[key]=[[],[]]
   vv,ff=self.batches[key];off=len(vv);vv.extend(v);ff.extend([tuple(off+i for i in face) for face in f]);return None
  name=PREFIX+n;me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);self.coll.objects.link(o);o.parent=self.body;o.matrix_parent_inverse=self.body.matrix_world.inverted()
  me.materials.append(self.m[mat] if isinstance(mat,str) else mat)
  if b:
   mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=b;mod.segments=2;mod.affect='EDGES';o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
  if smooth:
   for p in me.polygons:p.use_smooth=True
  o['static_visual_detail']=True;o['exact_unit_survey']=False
  self.created.append(o);return o
 def flush(self):
  for (name,mat),(v,f) in self.batches.items():self.obj(name,v,f,mat)
  self.batches={}
 def box(self,n,c,d,mat,b=.003,batch=False):
  X,Y,Z=c;x,y,z=[p/2 for p in d];v=[(X+a,Y+bb,Z+cc) for a,bb,cc in[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
  return self.obj(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,b,batch=batch)
 def cyl(self,n,c,r,d,mat,axis=(0,0,1),N=32,b=0,batch=False):
  c=Vector(c);A=Vector(axis).normalized();R=A.orthogonal().normalized();U=A.cross(R).normalized();v=[c+R*(r*cos(2*pi*i/N))+U*(r*sin(2*pi*i/N))+A*z for z in[-d/2,d/2] for i in range(N)]
  fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  o=self.obj(n,v,fs,mat,b,batch=batch)
  if o:
   for p in o.data.polygons:
    if len(p.vertices)==4:p.use_smooth=True
  return o
 def rod(self,n,a,b,r,mat,N=12,batch=False):
  a,b=Vector(a),Vector(b);return self.cyl(n,(a+b)/2,r,(b-a).length,mat,b-a,N,batch=batch)
 def tube(self,n,pts,r,mat,N=10,batch=False):
  pts=[Vector(p) for p in pts];v=[]
  for i,p in enumerate(pts):
   A=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();R=A.orthogonal().normalized();U=A.cross(R).normalized()
   v.extend([p+R*r*cos(2*pi*j/N)+U*r*sin(2*pi*j/N) for j in range(N)])
  fs=[tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))]+[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
  return self.obj(n,v,fs,mat,smooth=True,batch=batch)
 def ring(self,n,c,ro,ri,d,mat,axis=(0,0,1),N=40,batch=False):
  c=Vector(c);A=Vector(axis).normalized();R=A.orthogonal().normalized();U=A.cross(R).normalized();v=[]
  for z,r in[(-d/2,ro),(d/2,ro),(-d/2,ri),(d/2,ri)]:
   for j in range(N):v.append(c+R*r*cos(2*pi*j/N)+U*r*sin(2*pi*j/N)+A*z)
  fs=[]
  for i in range(N):
   j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)])
  return self.obj(n,v,fs,mat,smooth=True,batch=batch)
 def bolt(self,n,c,r=.008,axis=(0,0,1),batch=True):
  A=Vector(axis);c=Vector(c);self.cyl(n+'_hex_heads',c,r,.009,'steel',A,6,batch=batch);self.cyl(n+'_washers',c-A*.005,r*1.35,.003,'steel',A,16,batch=batch)
 def screw(self,n,c,axis=(0,1,0),r=.005,batch=True):
  A=Vector(axis);c=Vector(c);self.cyl(n+'_heads',c,r,.003,'steel',A,16,batch=batch)
  # Mesh slots align with the chosen panel rather than using repeated stickers.
  R=A.orthogonal().normalized();U=A.cross(R);self.slab(n+'_slots',c+A*.0018,r*1.2,.001,.0005,'black',R,U,b=0,batch=batch)
 def slab(self,n,c,w,h,d,mat,R=(1,0,0),U=(0,0,1),b=.002,batch=False):
  c,R,U=Vector(c),Vector(R),Vector(U);N=R.cross(U).normalized();v=[c+R*(a*w/2)+U*(bb*h/2)+N*(cc*d/2) for a,bb,cc in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  return self.obj(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,b,batch=batch)
 def text(self,n,txt,c,size=.035,mat='ivory',R=(1,0,0),U=(0,0,1)):
  R,U=Vector(R),Vector(U);N=R.cross(U).normalized();cu=bpy.data.curves.new(PREFIX+n,'FONT');cu.body=txt;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.resolution_u=3;cu.fill_mode='BOTH';o=bpy.data.objects.new(PREFIX+n,cu);self.coll.objects.link(o);o.parent=self.body;o.matrix_parent_inverse=self.body.matrix_world.inverted();o.matrix_basis=Matrix((R,U,N)).transposed().to_4x4();o.location=c;cu.materials.append(self.m[mat]);o['label_scope']='Equipment-type identity, representative placement';self.created.append(o);return o
 def tag(self,n,txt,c,w=.19,side=1):
  R=(side,0,0);N=Vector((0,-side,0));self.slab(n+'_black_nameplate',c,w,.064,.002,'black',R);self.text(n+'_equipment_designator',txt,Vector(c)+N*.002,.035,'ivory',R)
  for off in[-w/2+.008,w/2-.008]:self.screw(n+'_nameplate_screw',Vector(c)+Vector((off,0,0))+N*.002,N,.0026)
 def grip(self,n,x,y,z,side=1,h=.22):
  front=y-side*.032
  for zz in[z-h/2,z+h/2]:
   self.box(n+'_handle_bracket',(x,y,zz),(.042,.033,.037),'steel',.004)
   self.rod(n+'_handle_standoff',(x,y,zz),(x,front,zz),.007,'steel',12)
  self.rod(n+'_handle_grip',(x,front,z-h/2),(x,front,z+h/2),.009,'steel',20)
 def louvre(self,n,x,y,z,w,h,side=1):
  self.box(n+'_vent_dark_recess',(x,y,z),(w,.012,h),'black',.002)
  for j in range(max(3,int(h/.027))):
   zz=z-h/2+.017+j*.027
   # Each formed blade has a fold and a real dark gap below it.
   v=[(x+dx,y-side*dy,zz+dz) for dx,dy,dz in[(-w/2,.014,.006),(w/2,.014,.006),(w/2,.002,.016),(-w/2,.002,.016),(-w/2,.014,-.001),(w/2,.014,-.001),(w/2,.001,.010),(-w/2,.001,.010)]]
   self.obj(n+'_vent_folded_blades',v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)],'door',batch=True)
  for xx in[x-w/2-.009,x+w/2+.009]:self.box(n+'_vent_side_flange',(xx,y-side*.009,z),(.017,.017,h+.021),'door',.002)
  for xx in[x-w/2+.015,x+w/2-.015]:
   for zz in[z-h/2-.008,z+h/2+.008]:self.screw(n+'_vent_screws',(xx,y-side*.015,zz),(0,-side,0),.0035)


def cabinet(b,n,x,y,w,d,h=1.76,doors=2,label=None,vent=True,kind='converter'):
 side=1 if y>0 else -1;z=1.67+h/2;front=y-side*d/2;R=(side,0,0);N=(0,-side,0)
 b.box(n+'_plinth',(x,y,1.68),(w+.045,d+.038,.115),'edge',.005)
 b.box(n+'_folded_enclosure',(x,y,z),(w,d,h),'cabinet',.010)
 b.box(n+'_top_return',(x,y,z+h/2+.002),(w+.024,d+.018,.024),'aluminium',.004)
 b.box(n+'_front_gasket_plane',(x,front-side*.006,z),(w-.026,.014,h-.044),'black',.002)
 dw=(w-.045)/doors
 for j in range(doors):
  xx=x-w/2+.023+dw*(j+.5);yn=front-side*.018
  b.box(n+f'_door_{j+1}',(xx,yn,z),(dw-.010,.025,h-.067),'door',.005)
  for zz in[z-h*.31,z+h*.31]:
   b.box(n+'_hinge_leaf',(xx-dw/2+.024,yn-side*.017,zz),(.030,.017,.059),'steel',.002)
   b.cyl(n+'_hinge_knuckles',(xx-dw/2+.023,yn-side*.030,zz),.009,.077,'steel',(0,0,1),16,batch=True)
   for dz in[-.020,.020]:b.screw(n+'_hinge_screw',(xx-dw/2+.036,yn-side*.027,zz+dz),N,.0035)
  if kind in['hotel_load_converter','hotel_load_companion']:
   rx=xx+dw/2-.047;rz=z+.10
   b.box(n+'_recessed_latch_frame',(rx,yn-side*.017,rz),(.064,.012,.118),'steel',.003)
   b.box(n+'_recessed_latch_pocket',(rx,yn-side*.024,rz),(.048,.005,.101),'black',.004)
   b.box(n+'_flush_latch_lever',(rx,yn-side*.028,rz-.009),(.025,.010,.059),'rubber',.003)
   b.cyl(n+'_latch_keyhole',(rx,yn-side*.035,rz+.033),.006,.003,'steel',N,20,batch=True)
  else:b.grip(n+f'_door_{j+1}',xx+dw/2-.057,yn-side*.020,z-.070,side,.20)
  b.cyl(n+'_captive_latch',(xx+dw/2-.055,yn-side*.037,z+.15),.012,.012,'steel',N,24,batch=True)
  if kind=='hotel_load_converter':perforated_grille(b,n+f'_door_{j+1}',xx,yn-side*.017,z-h*.30,min(.34,dw-.11),.29,side)
  if vent:
   for zz,hh in[(z+h*.29,.23),(z-h*.33,.22)]:b.louvre(n+f'_door_{j+1}',xx,yn-side*.019,zz,max(.1,dw-.10),hh,side)
  elif kind=='hb':
   # Visible inspection opening on HB2 photo, with gasket and interior breaker rows.
   wz=.54;ww=min(dw-.14,.29);cz=z+.05
   b.box(n+'_inspection_recess',(xx,yn-side*.017,cz),(ww+.035,.018,wz+.035),'black',.015)
   b.box(n+'_inspection_glass',(xx,yn-side*.036,cz),(ww,.003,wz),'glass',.006)
   for dx in[-ww/2-.006,ww/2+.006]:b.box(n+'_inspection_frame_vertical',(xx+dx,yn-side*.041,cz),(.012,.009,wz+.024),'rubber',.002)
   for dz in[-wz/2-.006,wz/2+.006]:b.box(n+'_inspection_frame_horizontal',(xx,yn-side*.041,cz+dz),(ww+.024,.009,.012),'rubber',.002)
   for zz in[cz-.19,cz,cz+.19]:
    for dx in[-.065,0,.065]:b.box(n+'_breaker_forms',(xx+dx,yn-side*.028,zz),(.028,.007,.059),'edge',.002,batch=True)
  for zz in[z-h/2+.025,z+h/2-.025]:
   for xxx in[xx-dw/2+.030,xx+dw/2-.030]:b.screw(n+'_door_retainer',(xxx,yn-side*.019,zz),N,.004)
 if label:b.tag(n,label,(x,front-side*.036,z+h/2-.135),max(.19,min(.34,w*.3)),side)
 for xx in[x-w*.34,x+w*.34]:
  # Welded lifting ears and anchoring feet stay inside the equipment envelope.
  b.box(n+'_mounting_foot',(xx,y,1.659),(.18,d+.028,.042),'steel',.004)
  for yy in[y-d*.39,y+d*.39]:b.bolt(n+'_mounting_bolt',(xx,yy,1.687),.010)
  b.box(n+'_lifting_lug',(xx,y,z+h/2+.025),(.11,.035,.067),'steel',.008)
  b.cyl(n+'_lifting_lug_hole',(xx,y-side*.020,z+h/2+.029),.014,.004,'black',N,24,batch=True)
 # Discreet earthing braid and cable glands by each end of the cabinet base.
 b.tube(n+'_earth_bond',[(x-w/2+.035,front-side*.024,1.82),(x-w/2-.006,front-side*.035,1.75),(x-w/2+.018,front-side*.016,1.68)],.0045,'brass',8)
 for k in range(3):
  xx=x-w*.22+k*.064;b.cyl(n+'_cable_glands',(xx,y+side*d*.26,1.689),.020,.040,'rubber',(0,0,1),12,batch=True)
 b.equipment.append({'name':n,'kind':kind,'center':[x,y,z],'dimensions':[w,d,h],'front_y':front,'source':'SKEL-5051 Alt2 placement / corridor photo cabinet class','fine_hardware':'inferred representative visual detail'})


def round_duct_transition(b,n,c,r,top,w,d,height,mat='blower'):
 x,y,z=c;tx,ty=top;N=48;v=[]
 for level in[0,1]:
  for j in range(N):
   a=2*pi*j/N
   if level==0:v.append((x+r*cos(a),y+r*sin(a),z))
   else:
    scale=1/max(abs(cos(a)),abs(sin(a)));v.append((tx+w/2*cos(a)*scale,ty+d/2*sin(a)*scale,z+height))
 f=[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
 b.obj(n+'_eccentric_transition_duct',v,f,mat,.001)
 b.ring(n+'_lower_flange',(x,y,z),r+.025,r-.009,.022,'steel',N=64)
 for j in range(12):
  a=j*2*pi/12;b.bolt(n+'_lower_flange_bolts',(x+(r+.012)*cos(a),y+(r+.012)*sin(a),z+.016),.007)
 b.box(n+'_upper_rectangular_flange',(tx,ty,z+height), (w+.045,d+.045,.023),'aluminium',.002)


def blower(b,n,x,y,w=.74,d=.80,h=1.60,kind='machine_room_blower'):
 side=1 if y>0 else -1;r=min(w,d)*.39;zbase=1.685;cy=y+.02*side
 b.box(n+'_baseframe',(x,y,zbase),(w,d,.105),'edge',.005)
 for dx in[-w*.32,w*.32]:
  b.box(n+'_mounting_foot',(x+dx,y,zbase+.047),(.095,d*.80,.036),'steel',.003)
  for yy in[y-d*.32,y+d*.32]:b.bolt(n+'_floor_bolt',(x+dx,yy,zbase+.073),.010)
 # Vertical cylindrical blower pot and bolted split casing match the inspected real corridor view.
 b.cyl(n+'_lower_drum',(x,cy,2.066),r,.664,'blower',(0,0,1),64,b=.005)
 b.ring(n+'_lower_body_flange',(x,cy,1.78),r+.020,r-.02,.025,'blower',N=64)
 b.ring(n+'_upper_split_flange',(x,cy,2.397),r+.028,r-.018,.027,'aluminium',N=64)
 for j in range(16):
  a=j*2*pi/16;b.bolt(n+'_split_flange_bolt',(x+(r+.012)*cos(a),cy+(r+.012)*sin(a),2.417),.0065)
 # Motor casing, fine cooling fins, electrical terminal box and hand access panel.
 front=cy-side*r
 b.box(n+'_rectangular_motor_bed',(x,front-side*.042,1.944),(.35,.142,.414),'blower',.007)
 b.box(n+'_service_access_panel',(x,front-side*.121,1.944),(.215,.018,.294),'blower',.009)
 for xx in[x-.083,x+.083]:
  for zz in[1.821,2.067]:b.screw(n+'_access_panel_screw',(xx,front-side*.134,zz),(0,-side,0),.0045)
 b.cyl(n+'_motor_body',(x+side*.24,cy,1.875),.095,.237,'motor',(1,0,0),40,b=.004)
 for j in range(9):b.ring(n+'_motor_cooling_fins',(x+side*.14+side*j*.023,cy,1.875),.112,.096,.008,'motor',(1,0,0),32,batch=True)
 b.box(n+'_terminal_box',(x+side*.22,cy-side*.056,2.001),(.14,.105,.083),'motor',.006)
 # Wide cylindrical throat and deliberately eccentric fabricated transition beneath roof.
 b.cyl(n+'_upper_neck',(x,cy,2.664),r*.92,.51,'blower',(0,0,1),64,b=.004)
 round_duct_transition(b,n,(x,cy,2.901),r*.92,(x+.045,cy+side*.035),w*.89,d*.86,.327,'aluminium')
 b.box(n+('_side_filter_plenum' if kind=='machine_room_blower' else '_upper_filter_connector'),(x+.045,cy+side*.035,3.455),(w*.89,d*.86,.44),'aluminium',.005)
 if kind=='machine_room_blower':
  outer=side*(b.half_width-.018);inner=cy+side*(d*.43+.035);mid=(outer+inner)/2
  b.box(n+'_sidewall_filter_transition',(x+.045,mid,3.406),(w*.70,abs(outer-inner)+.032,.30),'aluminium',.005)
  b.box(n+'_sidewall_filter_flange',(x+.045,outer,3.406),(w*.74,.024,.34),'steel',.003)
 for zz in[3.249,3.653]:
  b.box(n+'_connector_fold',(x+.045,cy+side*.035,zz),(w*.91,d*.88,.025),'steel',.002)
 b.tube(n+'_motor_supply_lead',[(x+side*.22,cy-side*.108,2.017),(x+side*.27,cy-side*.16,2.12),(x+w*.47,cy-side*.16,2.38),(x+w*.47,cy-side*.16,3.42)],.012,'rubber',12)
 for zz in[2.23,2.66,3.11]:b.box(n+'_cable_p_clip',(x+w*.47,cy-side*.17,zz),(.036,.014,.019),'aluminium',.001,batch=True)
 b.tag(n,'MRB' if kind=='machine_room_blower' else 'TMB',(x,front-side*.134,2.128),.18,side)
 b.equipment.append({'name':n,'kind':kind,'center':[x,y,2.58],'dimensions':[w,d,1.93],'source':'Inspected machinery corridor blower / CLW transition duct specification','fine_hardware':'inferred representative'})


def cooling_unit(b,n,x,y,w=1.12,d=.83):
 side=1 if y>0 else -1;front=y-side*d/2
 b.box(n+'_support_skid',(x,y,1.72),(w,d,.13),'edge',.005)
 b.box(n+'_cooler_lower_housing',(x,y,2.06),(w-.07,d-.04,.65),'cooler',.008)
 b.box(n+'_radiator_core_dark',(x,front-side*.025,2.668),(w-.13,.025,.61),'black',.002)
 for j in range(int((w-.16)/.016)):
  xx=x-w/2+.088+j*.016;b.box(n+'_radiator_folded_fins',(xx,front-side*.041,2.668),(.008,.022,.592),'aluminium',.0,batch=True)
 for zz in[2.357,2.973]:b.box(n+'_radiator_header',(x,front-side*.029,zz),(w-.057,.045,.042),'cooler',.004)
 for xx in[x-w/2+.023,x+w/2-.023]:
  b.box(n+'_radiator_vertical_frame',(xx,front-side*.025,2.665),(.041,.046,.66),'cooler',.003)
  for z in[2.388,2.58,2.78,2.941]:b.bolt(n+'_radiator_frame_bolt',(xx,front-side*.054,z),.007,(0,-side,0))
 b.cyl(n+'_cooler_fan_casing',(x,y,3.102),min(w*.35,d*.44),.207,'cooler',(0,0,1),64,b=.006)
 round_duct_transition(b,n,(x,y,3.208),min(w*.35,d*.44),(x,y),w-.06,d-.04,.244,'aluminium')
 b.box(n+'_roof_duct',(x,y,3.56),(w-.06,d-.04,.216),'aluminium',.003)
 for dx in[-w*.3,w*.3]:
  xx=x+dx;b.tube(n+'_oil_pipe',[(xx,front-side*.066,1.735),(xx,front-side*.066,2.020),(xx,front-side*.076,2.135),(xx+dx*.2,front-side*.05,2.205)],.019,'pipe',16)
  for z in[1.85,2.07]:b.ring(n+'_pipe_union',(xx,front-side*.066,z),.026,.019,.039,'brass',(0,0,1),12,batch=True)
  b.cyl(n+'_service_plug',(xx,front-side*.071,2.249),.028,.028,'brass',(0,-side,0),6,batch=True)
 b.tag(n,'OCU',(x,front-side*.030,2.227),.20,side)
 b.equipment.append({'name':n,'kind':'oil_cooling_unit','center':[x,y,2.63],'dimensions':[w,d,1.9],'source':'SKEL-5051 / CLW OCU duct description; radiator details representative'})


def reservoir(b,n,x,y,height=1.67,r=.30,base=1.952,capacity_l=450):
 # Official ZRTI wording and the HOG plan both establish vertical vessels.
 # Diameter / height are transparent capacity-and-bay-fit estimates, not a drawing.
 side=1 if y>0 else -1;N=64;dish=.135;profile=[(0,0),(.014,r*.42),(.048,r*.72),(.090,r*.93),(dish,r),(height-dish,r),(height-.090,r*.93),(height-.048,r*.72),(height-.014,r*.42),(height,0)];v=[]
 for zz,rr in profile:
  for j in range(N):
   a=2*pi*j/N;v.append((x+rr*cos(a),y+rr*sin(a),base+zz))
 f=[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(len(profile)-1) for j in range(N)]
 b.obj(n+'_vertical_dished_pressure_vessel',v,f,'pipe',smooth=True)
 for zz in[base+dish+.026,base+height-dish-.026]:b.ring(n+'_circumferential_weld_seam',(x,y,zz),r+.0025,r-.001,.005,'pipe',N=64)
 for zz in[base+height*.24,base+height*.75]:
  b.ring(n+'_tank_retaining_band',(x,y,zz),r+.014,r+.005,.041,'aluminium',N=64)
  b.box(n+'_rear_bracket',(x,side*(b.half_width-.065),zz),(.23,.050,.15),'steel',.004)
  for xx in[x-.083,x+.083]:
   b.rod(n+'_wall_bracket_arm',(xx,y+side*(r-.006),zz),(xx,side*(b.half_width-.055),zz),.014,'steel',16)
   b.bolt(n+'_wall_bracket_bolts',(xx,side*(b.half_width-.094),zz),.008,(0,-side,0))
 # Raised cradle bridges the bogie-spring pockets; its legs stay outside their Y footprint.
 top=base+.008;front=side*.60;rear=side*(b.half_width-.090)
 b.box(n+'_cradle_crossbearer',(x,(front+rear)/2,top-.027),(.145,abs(rear-front)+.07,.055),'edge',.004)
 for yy in[front,rear]:
  if top>1.74:b.box(n+'_cradle_leg',(x,yy,(1.648+top)/2),(.099,.074,top-1.648),'steel',.004)
  b.box(n+'_cradle_floor_foot',(x,yy,1.650),(.22,.125,.030),'steel',.003)
  for xx in[x-.073,x+.073]:b.bolt(n+'_cradle_anchor',(xx,yy,1.672),.008)
 b.cyl(n+'_crown_plug',(x,y,base+height+.010),.031,.021,'brass',(0,0,1),6)
 b.cyl(n+'_lower_drain_union',(x,y-side*(r-.060),base+.077),.024,.058,'brass',(0,-side,0),6)
 b.rod(n+'_drain_tap_handle',(x-.04,y-side*(r-.03),base+.061),(x+.04,y-side*(r-.03),base+.061),.0055,'red',16)
 frontpipe=y-side*(r+.040)
 b.tube(n+'_pressure_line',[(x+.10,y-side*(r-.026),base+height-.17),(x+.10,frontpipe,base+height-.20),(x+.10,frontpipe,base+.24),(x+.16,frontpipe,1.75)],.013,'pipe',16)
 for zz in[base+.30,base+height-.24]:b.ring(n+'_pressure_line_union',(x+.10,frontpipe,zz),.021,.013,.034,'brass',(0,0,1),12,batch=True)
 b.tag(n,'MR' if capacity_l==450 else 'AR',(x,y-side*(r+.018),base+height*.56),.18,side)
 b.equipment.append({'name':n,'kind':'vertical_air_reservoir','center':[x,y,base+height/2],'dimensions':[r*2,r*2,height],'capacity_identity_litres':capacity_l,'source':'CR/ZRTI manual: vertical reservoirs and450L MR; WAG9-GM2021 section8.2: WAP7/WAG9 AR240L; SKEL-5051 locations','geometry_note':'Vessel dimensions and cradle inferred from capacity and available bay, not manufacturer drawing'})


def pneumatic_panel(b,n,x,y,w=.97,d=.30):
 side=1 if y>0 else -1;front=y-side*d/2
 b.box(n+'_support_frame',(x,y,2.452),(w,d,1.526),'edge',.008)
 b.box(n+'_mounting_backplate',(x,front,2.47),(w-.025,.024,1.467),'aluminium',.004)
 for xx in[x-w/2+.041,x+w/2-.041]:
  for zz in[1.80,2.47,3.14]:b.bolt(n+'_mounting_fasteners',(xx,front-side*.022,zz),.008,(0,-side,0))
 # Plausible visual E70-style piping group, not a working pneumatic schematic.
 for j in range(4):
  xx=x-w*.30+j*w*.20;b.rod(n+'_vertical_pipe',(xx,front-side*.048,1.85),(xx,front-side*.048,3.056),.009,'pipe',16)
  for zz in[1.902,2.51,2.963]:
   b.box(n+'_pipe_clip',(xx,front-side*.050,zz),(.037,.025,.014),'steel',.002,batch=True)
   b.screw(n+'_pipe_clip_screw',(xx+.017,front-side*.066,zz),(0,-side,0),.003)
  for zz in[2.1,2.67]:b.cyl(n+'_compression_unions',(xx,front-side*.048,zz),.018,.029,'brass',(0,0,1),6,batch=True)
 for j in range(3):
  xx=x-w*.27+j*w*.27;zz=2.15 if j!=1 else 2.70
  b.box(n+'_valve_manifold',(xx,front-side*.077,zz),(.15,.07,.112),'steel',.008)
  b.cyl(n+'_valve_stem',(xx,front-side*.124,zz),.016,.066,'brass',(0,-side,0),16)
  b.ring(n+'_red_valve_handwheel',(xx,front-side*.165,zz),.051,.044,.010,'red',(0,-side,0),32)
  for k in range(3):
   a=k*2*pi/3;b.rod(n+'_handwheel_spokes',(xx,front-side*.165,zz),(xx+.046*cos(a),front-side*.165,zz+.046*sin(a)),.004,'red',8)
  b.cyl(n+'_handwheel_hub',(xx,front-side*.165,zz),.012,.014,'red',(0,-side,0),16)
 for j in range(2):
  xx=x+(-.23+j*.46)*w;zz=2.964
  b.cyl(n+'_gauge_metal_case',(xx,front-side*.065,zz),.057,.059,'steel',(0,-side,0),48,b=.004)
  b.cyl(n+'_gauge_face',(xx,front-side*.097,zz),.047,.003,'ivory',(0,-side,0),48)
  for k in range(11):
   a=pi*.22+k*pi*1.55/10;r=.039;pt=Vector((xx+r*cos(a),front-side*.100,zz+r*sin(a)));end=Vector((xx+(r-.005)*cos(a),front-side*.100,zz+(r-.005)*sin(a)));b.rod(n+'_gauge_minor_ticks',pt,end,.0007,'black',6,batch=True)
  b.rod(n+'_gauge_pointer',(xx,front-side*.104,zz),(xx-.022,front-side*.104,zz+.019),.0014,'black',8)
  b.cyl(n+'_gauge_spindle',(xx,front-side*.106,zz),.004,.005,'black',(0,-side,0),16)
 b.tag(n,'PNEUMATIC',(x,front-side*.024,3.108),.30,side)
 b.equipment.append({'name':n,'kind':'pneumatic_panel','center':[x,y,2.46],'dimensions':[w,d,1.526],'source':'SKEL-5051 location; panel piping nonfunctional representative'})


def oil_pump(b,n,x,y):
 side=1 if y>0 else -1
 b.box(n+'_skid',(x,y,1.733),(.40,.43,.12),'edge',.005)
 b.cyl(n+'_motor',(x,y,1.93),.131,.26,'motor',(1,0,0),40,b=.005)
 for j in range(8):b.ring(n+'_cooling_fins',(x-.12+j*.034,y,1.93),.145,.132,.008,'motor',(1,0,0),32,batch=True)
 b.cyl(n+'_pump_volute',(x+.19,y,1.93),.143,.109,'blower',(1,0,0),40,b=.004)
 b.box(n+'_connection_box',(x,y,2.068),(.133,.155,.083),'motor',.004)
 for yy in[y-.125,y+.125]:
  b.tube(n+'_pipe',[(x+.20,yy,1.932),(x+.23,yy,2.13),(x+.34,yy,2.18)],.016,'pipe',16)
  b.ring(n+'_union',(x+.23,yy,2.08),.024,.016,.034,'brass',(0,0,1),12,batch=True)
 for dx in[-.15,.15]:
  for dy in[-.16,.16]:b.bolt(n+'_skid_bolt',(x+dx,y+dy,1.803),.007)
 b.equipment.append({'name':n,'kind':'oil_pump','center':[x,y,1.94],'dimensions':[.50,.43,.48],'source':'SKEL-5051 pump location; motor construction inferred'})


def scavenge_blower(b,n,x,y,z=3.27):
 side=1 if y>0 else -1
 b.box(n+'_wall_mount',(x,y+side*.067,z),(.235,.035,.255),'aluminium',.004)
 b.cyl(n+'_volute',(x,y,z),.108,.16,'blower',(0,side,0),40,b=.004)
 b.cyl(n+'_motor',(x,y-side*.126,z),.067,.122,'motor',(0,side,0),32,b=.003)
 for j in range(6):b.ring(n+'_motor_fins',(x,y-side*(.090+j*.017),z),.074,.066,.006,'motor',(0,side,0),24,batch=True)
 b.tube(n+'_duct',[(x+.071,y,z+.071),(x+.137,y,z+.112),(x+.242,y,z+.112)],.042,'aluminium',20)
 b.ring(n+'_duct_joint',(x+.182,y,z+.112),.051,.040,.018,'steel',(1,0,0),32)
 for xx in[x-.085,x+.085]:
  for zz in[z-.096,z+.096]:b.bolt(n+'_mount_bolts',(xx,y-side*.079,zz),.006,(0,-side,0))


def structure(b):
 HW=b.half_width
 # Thin lining and open end frames. The integration owner alone hollows original body shell.
 b.box('Walkway_subfloor',(0,0,1.602),(14.22,.724,.040),'edge',.002)
 for j in range(20):
  x=-6.758+j*.711
  b.box('Walkway_removable_floor_panel_'+str(j),(x,0,1.631),(.701,.666,.018),'floor',.002)
  for yy in[-.287,.287]:
   for xx in[x-.306,x+.306]:b.screw('Walkway_countersunk_fasteners',(xx,yy,1.642),(0,0,1),.0045)
 # Actual raised alternating oval lozenges, batched into a single mesh.
 for i in range(178):
  xx=-7.04+i*.079
  for j in range(7):
   yy=-.283+j*.093+(.024 if i%2 else 0)
   if yy>.30:continue
   a=pi/4 if (i+j)%2 else-pi/4;R=Vector((cos(a),sin(a),0));U=Vector((-sin(a),cos(a),0));c=Vector((xx,yy,1.6434));rr=.0031;L=.016;v=[]
   for zz in[-.0008,.0008]:
    for k in range(12):
     t=2*pi*k/12;v.append(c+R*(L*cos(t))+U*(rr*sin(t))+Vector((0,0,zz)))
   fs=[tuple(reversed(range(12))),tuple(range(12,24))]+[(k,(k+1)%12,(k+1)%12+12,k+12) for k in range(12)]
   b.obj('Walkway_raised_chequer_tread',v,fs,'aluminium',batch=True)
 for side in[-1,1]:
  for j in range(10):
   x=-6.399+j*1.422
   b.box('Inner_sidewall_panel',(x,side*(HW+.004),2.615),(1.412,.020,1.970),'wall',.002)
   for xx in[x-.67,x+.67]:
    for zz in[1.78,3.30]:b.screw('Inner_sidewall_panel_screws',(xx,side*(HW-.008),zz),(0,-side,0),.0045)
  b.box('Inner_lower_longitudinal_sill',(0,side*(HW-.033),1.699),(14.2,.08,.15),'edge',.003)
  b.box('Walkway_floor_return',(0,side*.358,1.661),(14.2,.037,.059),'steel',.003)
  # Skinny wall channel ribs are mostly occluded by cabinets, readable in service gaps.
  for x in[-6.5,-4.6,-2.5,0,2.5,4.6,6.5]:b.box('Body_inner_channel_rib',(x,side*(HW-.027),2.61),(.07,.051,1.80),'wall',.003)
 # Flat central ceiling with separate removable panels; nominated render-only cutaway group.
 for j in range(10):
  x=-6.4+j*1.422;o=b.box('Ceiling_removable_liner_'+str(j),(x,0,3.713),(1.412,2.605,.023),'wall',.002);o['cutaway_hide']=True
  for xx in[x-.66,x+.66]:
   for yy in[-.92,.92]:b.screw('Ceiling_panel_retainer',(xx,yy,3.698),(0,0,-1),.0045)
 for side in[-1,1]:
  for j in range(10):
   x=-6.4+j*1.422;w=1.412;v=[]
   for dy,dz in[(0,0),(.005,.005)]:
    v += [(x-w/2,side*(HW-.006+dy),3.600+dz),(x+w/2,side*(HW-.006+dy),3.600+dz),(x+w/2,side*(1.3025+dy),3.7015+dz),(x-w/2,side*(1.3025+dy),3.7015+dz)]
   o=b.obj('Ceiling_sloped_shoulder_liner',v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'wall');o['cutaway_hide']=True
 for x in[-6.55,-4.35,-2.18,0,2.18,4.35,6.55]:
  o=b.box('Ceiling_crossbearer',(x,0,3.672),(.06,2.39,.048),'wall',.002);o['cutaway_hide']=True
 # Match the canonical cab rear doorway after the original BODY Y scale.
 halfdoor=.374*abs(b.body.matrix_world.to_scale().y)
 for e in[-1,1]:
  x=e*7.103
  for side in[-1,1]:
   w=HW-halfdoor;b.box('End_bulkhead_jamb',(x,side*(halfdoor+w/2),2.612),(.034,w,2.015),'wall',.003)
   b.box('End_door_rebate',(x-e*.019,side*(halfdoor+.011),2.56175),(.04,.025,1.9065),'aluminium',.002)
   b.rod('End_entry_grab_rail',(x-e*.075,side*(halfdoor+.11),2.05),(x-e*.075,side*(halfdoor+.11),2.83),.011,'steel',20)
   for z in[2.05,2.83]:
    b.rod('End_entry_grab_standoff',(x,side*(halfdoor+.11),z),(x-e*.075,side*(halfdoor+.11),z),.009,'steel',16)
  b.box('End_bulkhead_header',(x,0,3.60825),(.034,halfdoor*2,.1865),'wall',.003)
  b.box('End_walkway_bridge_plate',(e*7.116,0,1.635),(.078,halfdoor*2,.018),'steel',.002)
 # Long ladder cable trays at corridor shoulders, with true open gaps and side lips.
 for side in[-1,1]:
  y=side*.22
  for yy in[y-.126,y+.126]:b.box('Cabletray_folded_side_channel',(0,yy,3.518),(13.95,.014,.072),'aluminium',.002)
  for j in range(65):b.box('Cabletray_ladder_rung',(-6.94+j*.217,y,3.492),(.026,.263,.018),'aluminium',.001,batch=True)
  for j in range(5):
   yy=y-.09+j*.042
   b.tube('Cabletray_longitudinal_cable_'+str(side)+'_'+str(j),[(-6.95,yy,3.531),(-3.5,yy+.009*sin(j),3.538),(0,yy,3.531),(3.5,yy-.006*cos(j),3.539),(6.95,yy,3.531)],.012 if j<3 else .008,'rubber',12)
  for x in[-6.6,-5.4,-4.2,-3,-1.8,-.6,.6,1.8,3,4.2,5.4,6.6]:
   b.box('Cabletray_cable_band',(x,y,3.545),(.012,.244,.012),'ivory',.001,batch=True)
   b.box('Cabletray_support_hanger',(x,side*.354,3.590),(.032,.034,.180),'steel',.002,batch=True)
 # Practical light housings visible along the ceiling centerline. Light emitters are probe-only.
 for j,x in enumerate([-6.0,-3.6,-1.2,1.2,3.6,6.0]):
  b.box('Ceiling_fluorescent_housing_'+str(j),(x,0,3.524),(.72,.132,.064),'aluminium',.008)
  b.cyl('Ceiling_fluorescent_diffuser_'+str(j),(x,0,3.488),.023,.674,'diffuser',(1,0,0),40,b=.002)
  for xx in[x-.30,x+.30]:
   b.box('Ceiling_lamp_mounting_stem',(xx,0,3.60),(.025,.047,.15),'wall',.003)
   b.box('Ceiling_fluorescent_endclip',(xx,0,3.481),(.022,.118,.029),'steel',.002)
   b.screw('Ceiling_lamp_captive_screw',(xx,0,3.465),(0,0,-1),.0035)


def services(b):
 # Longitudinal low service piping remains outside the walking envelope.
 for side in[-1,1]:
  for j in range(3):
   y=side*(1.106+j*.034);z=1.744+j*.069
   inner=side*(.80+j*.035)
   b.tube('Low_longitudinal_service_pipe_'+str(side)+'_'+str(j),[(-6.85,y,z),(-6.70,y,z),(-6.53,inner,z),(-5.45,inner,z),(-5.28,y,z),(5.28,y,z),(5.45,inner,z),(6.53,inner,z),(6.70,y,z),(6.85,y,z)],.012 if j!=2 else .017,'pipe',16)
   for x in[-6.1,-4.1,-2.1,0,2.1,4.1,6.1]:
    yy=inner if 5.45<abs(x)<6.53 else y
    b.ring('Service_pipe_union',(x,yy,z),.020 if j!=2 else .026,.012 if j!=2 else .017,.039,'brass',(1,0,0),12,batch=True)
    b.box('Service_pipe_clip',(x,yy+side*.040,z),(.036,.043,.048),'steel',.003,batch=True)
 # Upper harness drops are stationed in real equipment gaps by the layout builder.
 for eq in b.equipment:
  if eq['kind'] not in['converter','hb','auxiliary_converter','hotel_load_converter']:continue
  x,y,z=eq['center'];w,d,h=eq['dimensions'];side=1 if y>0 else-1;xx=x+w*.40
  for j in range(3):
   yy=side*(.55+j*.047)
   b.tube(eq['name']+'_roof_cable_drop_'+str(j),[(xx-.20,yy,3.55),(xx-.09,yy,3.54),(xx+.01,yy,3.49),(xx+.045,yy,3.38),(xx+.045,yy,3.30)],.013,'rubber',12)
  for zz in[3.39,3.49]:b.box(eq['name']+'_roof_cable_band',(xx+.045,side*.596,zz),(.040,.142,.013),'ivory',.001,batch=True)


def build_layout(b):
 """NTS plan order, with manufacturer longitudinal envelopes when available.

 +X is CAB1; +Y is the upper row of the inspected plan. Unseen height/depth
 details are fitted visual estimates within the preserved exterior cavity.
 """
 Y=.825
 # Upper row, CAB2 (-X) to CAB1 (+X).
 reservoir(b,'AR_auxiliary_reservoir',-6.69,.93,1.60,.23,1.70,240)
 reservoir(b,'MR1_main_reservoir',-6.12,.93,1.67,.30,1.995,450)
 scavenge_blower(b,'Scavenge1',-5.67,1.05,3.21)
 blower(b,'Traction_motor_blower1',-4.90,Y,.87,.81,kind='traction_motor_blower')
 pneumatic_panel(b,'Pneumatic_panel',-3.94,1.025,.76,.30)
 oil_pump(b,'Auxiliary_compressor_visual',-3.94,.715)
 b.equipment[-1]['kind']='auxiliary_compressor';b.equipment[-1]['source']='Plan location; compact compressor motor/casing representative'
 cooling_unit(b,'Oil_cooling_unit1',-2.77,Y,1.10,.82)
 oil_pump(b,'Converter_oil_pump1',-1.90,Y)
 cabinet(b,'Traction_converter1',-.05,Y,3.00,.82,1.93,3,'SR1',False,'converter')
 blower(b,'Machine_room_blower1',2.20,Y,.88,.80,kind='machine_room_blower')
 scavenge_blower(b,'MRB1_scavenge',1.60,1.06,3.22)
 cabinet(b,'Auxiliary_converter1',3.37,Y,1.16,.82,1.82,2,'BUR1',True,'auxiliary_converter')
 cabinet(b,'Control_and_traction_cubicle1',4.42,Y,.73,.81,1.78,1,'C&T1',False,'hb')
 cabinet(b,'Hotel_load_converter1',5.66,Y,1.40,.82,1.63,2,'HL1',False,'hotel_load_converter')
 cabinet(b,'Hotel_load_equipmentA1',6.60,Y,.30,.82,1.63,1,None,False,'hotel_load_companion')
 # Lower row, CAB2 (-X) to CAB1 (+X).
 cabinet(b,'Hotel_load_converter2',-5.73,-Y,1.40,.82,1.63,2,'HL2',False,'hotel_load_converter')
 cabinet(b,'Hotel_load_equipmentA2',-6.67,-Y,.30,.82,1.63,1,None,False,'hotel_load_companion')
 cabinet(b,'Control_and_traction_cubicle2',-4.60,-Y,.72,.81,1.78,1,'C&T2',False,'hb')
 cabinet(b,'Auxiliary_converter2',-3.45,-Y,1.52,.82,1.82,2,'BUR2',True,'auxiliary_converter')
 blower(b,'Machine_room_blower2',-2.10,-Y,.88,.80,kind='machine_room_blower')
 scavenge_blower(b,'MRB2_scavenge',-1.53,-1.05,3.22)
 cabinet(b,'Traction_converter2',.05,-Y,3.00,.82,1.93,3,'SR2',False,'converter')
 oil_pump(b,'Converter_oil_pump2',1.91,-Y)
 cooling_unit(b,'Oil_cooling_unit2',2.78,-Y,1.10,.82)
 cabinet(b,'Filter_block2',3.78,-Y,.66,.78,1.22,1,'FB2',True,'filter_block')
 blower(b,'Traction_motor_blower2',4.68,-Y,.87,.81,kind='traction_motor_blower')
 scavenge_blower(b,'Scavenge2',5.47,-1.04,3.20)
 reservoir(b,'MR2_main_reservoir',6.05,-.93,1.67,.30,1.995,450)
 cabinet(b,'PB_plan_cubicle',6.72,-Y,.43,.76,1.26,1,'PB',False,'plan_cubicle')
 # Small central electronics cover above the C&T breaker inspection sections.
 for index,x,y,w in[(1,4.42,Y,.73),(2,-4.60,-Y,.72)]:
  side=1 if y>0 else-1;front=y-side*.405
  b.box('VCU'+str(index)+'_bolted_access',(x,front-side*.046,3.148),(w-.095,.038,.317),'aluminium',.005)
  b.tag('VCU'+str(index),'VCU',(x,front-side*.068,3.14),.23,side)
  for xx in[x-w/2+.065,x+w/2-.065]:
   for zz in[3.02,3.272]:b.screw('VCU'+str(index)+'_cover_retainer',(xx,front-side*.070,zz),(0,-side,0),.004)
 # Traction-converter service covers and restrained real cable termination detail.
 for index,x,y in[(1,-.05,Y),(2,.05,-Y)]:
  side=1 if y>0 else-1;front=y-side*.41
  for j in range(3):
   xx=x-.99+j*.99
   b.box('SR'+str(index)+'_separate_module_cover',(xx,front-side*.040,2.61),(.72,.018,.79),'cabinet',.004)
   for xx2 in[xx-.32,xx+.32]:
    for zz in[2.262,2.96]:b.screw('SR'+str(index)+'_module_retainer',(xx2,front-side*.054,zz),(0,-side,0),.0055)
   b.louvre('SR'+str(index)+'_upper_cooling_slots',xx,front-side*.055,3.168,.66,.165,side)
  # A small mechanical earth isolator symbol is not invented: only shaft/collar geometry is shown.
  xx=x+1.32;b.cyl('SR'+str(index)+'_isolator_collar',(xx,front-side*.048,2.303),.032,.023,'steel',(0,-side,0),32)
  b.rod('SR'+str(index)+'_isolator_handle',(xx,front-side*.066,2.303),(xx,front-side*.066,2.383),.011,'rubber',16)


def apply(context=None):
 """Add the representative machinery-room visual model and return its QA metadata.

 Optional context: body (preserved BODY object), material_overrides. The caller
 owns shell hollowing and presentation. Default source opens with cab doors shut.
 """
 ctx=context if isinstance(context,dict) else {};body=ctx.get('body') or bpy.data.objects.get('BODY')
 active_name=bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None
 if body is None:raise ValueError('The preserved BODY root is required')
 for o in list(bpy.data.objects):
  if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
 for datablocks in[bpy.data.meshes,bpy.data.curves]:
  for data in list(datablocks):
   if data.name.startswith(PREFIX) and data.users==0:datablocks.remove(data)
 coll=bpy.data.collections.get(PREFIX+'MACHINERY_ROOM')
 if not coll:coll=bpy.data.collections.new(PREFIX+'MACHINERY_ROOM');bpy.context.scene.collection.children.link(coll)
 coll['source_plan']=SOURCE_PLAN;coll['source_photo']=SOURCE_PHOTO;coll['source_duct']=SOURCE_DUCT;coll['source_hlc_envelope']=SOURCE_HLC
 coll['reference_scope']='WAP7 HOG SKEL-5051 Alt2 base equipment layout. Kavach overlay excluded. Not a measured 39002 survey.'
 coll['coordinate_map']='Drawing CAB1 right = +X; top row = +Y. CAB2 left = -X.'
 coll['equipment_status']='Static visual model, no working high-voltage, pneumatic or traction simulation'
 m=palette();m.update(ctx.get('material_overrides') or {})
 half_width=ctx.get('machinery_half_width',min(1.46,1.576*abs(body.matrix_world.to_scale().y)-.055))
 b=Builder(body,coll,m,half_width)
 structure(b)
 for o in b.created:
  if o.name.startswith((PREFIX+'Ceiling_fluorescent',PREFIX+'Ceiling_lamp_')):
   if o.type=='MESH':
    for v in o.data.vertices:v.co.z+=.035
 # Trays are raised another20mm to leave comfortable continuous headroom.
 for o in b.created:
  if o.name.startswith(PREFIX+'Cabletray_') and o.type=='MESH':
   for v in o.data.vertices:v.co.z+=.020
 # Lamp screws and repeated cable-tray hardware are batched.
 for (name,mat),(verts,faces) in b.batches.items():
  dz=.035 if name.startswith('Ceiling_lamp_') else .020 if name.startswith('Cabletray_') else 0
  if dz:
   for i,v in enumerate(verts):verts[i]=Vector(v)+Vector((0,0,dz))
 build_layout(b);b.flush();envelope_report=fit_sourced_envelopes(b);services(b);b.flush();relief_report=[];raised_mount_report=raised_hog_mounts(b)
 for o in list(b.created):
  if o.type=='MESH' and len(o.data.vertices)==0:b.created.remove(o);bpy.data.objects.remove(o,do_unlink=True)
 for data in list(bpy.data.meshes):
  if data.name.startswith(PREFIX) and data.users==0:bpy.data.meshes.remove(data)
 bpy.context.view_layer.objects.active=bpy.data.objects.get(active_name) if active_name else None
 bpy.context.view_layer.update()
 for o in b.created:
  o['module']='machinery_room';o['reference_scope']='Class-level representative fine hardware; exact unit not claimed'
 stats={'added_objects':len(b.created),'equipment_groups':len(b.equipment),'equipment_layout':b.equipment,'world_bounds_target':{'x':[-7.155,7.155],'y':[-half_width-.014,half_width+.014],'z':[1.545,3.73]},'walking_clear_half_width':min(.320,half_width-1.11),'cabinet_envelope_clear_width':2*(half_width-1.11),'headroom_benchmark_m':1.83,'floor_height':1.64,'roof_liner_height':3.713,'sourced_envelopes':envelope_report,'spring_pocket_reliefs':relief_report,'raised_hlc_mounts':raised_mount_report,'cavity_half_width':half_width,'static_visual_model':True,'source_plan':'SKEL-5051 Alt2 WAP7 with hotel load converter, inspected full plan; NTS','kavach_overlay_modelled':False,'exact_unit_survey':False,'source_images_embedded':False,'new_shell_cuts':False,'manufacturing_envelope_note':'TC and BUR existing external envelopes retained; HLC main and companion cases fit documented CLW2013 installation-bay maxima. Vendor faces and raised pocket-bridging installation frames remain representative; no HLC cabinet cutouts are used.','lighting_suggestion':'Six low-power rectangular sources under fluorescent diffusers at x +/-1.2,+/-3.6,+/-6.0; z3.498; confined to presentation.'}
 coll['build_report']=json.dumps(stats);return stats


def fit_sourced_envelopes(b):
 """Fit complete visual assemblies to documented external envelopes.

 This is a geometric envelope constraint, not a claim that internal modules or
 vendor-specific door hardware were measured. Service cables are added later.
 """
 bpy.context.view_layer.update();report=[]
 specs=[
 ('Traction_converter1',('SR1_',),3.000,1.100,2.087,1.545),
 ('Traction_converter2',('SR2_',),3.000,1.100,2.087,1.545),
 ('Auxiliary_converter1',(),1.160,1.020,1.860,1.650),
 ('Auxiliary_converter2',(),1.520,1.020,1.860,1.650),
 ('Hotel_load_converter1',(),1.380,1.040,1.700,1.945),
 ('Hotel_load_converter2',(),1.380,1.040,1.700,1.945),
 ('Hotel_load_equipmentA1',(),.290,.700,.435,2.420),
 ('Hotel_load_equipmentA2',(),.290,.700,.435,2.420),
 ]
 for name,aliases,L,D,H,z0 in specs:
  eq=next(e for e in b.equipment if e['name']==name);side=1 if eq['center'][1]>0 else-1
  group=[o for o in b.created if o.name.startswith(tuple(PREFIX+x for x in(name,)+aliases))]
  vs=[o.matrix_world@Vector(v) for o in group for v in o.bound_box];mn=Vector(tuple(min(v[k] for v in vs) for k in range(3)));mx=Vector(tuple(max(v[k] for v in vs) for k in range(3)));old_dims=mx-mn
  y1=b.half_width-.01;y0=y1-D;x=eq['center'][0];target_min=Vector((x-L/2,y0 if side>0 else-y1,z0));target_dims=Vector((L,D,H))
  scale=Vector(tuple(target_dims[k]/old_dims[k] for k in range(3)));T=Matrix.Diagonal((*scale,1));T.translation=target_min-Vector(tuple(mn[k]*scale[k] for k in range(3)))
  for o in group:
   if o.type=='MESH':
    local=o.matrix_world.inverted()@T@o.matrix_world
    for v in o.data.vertices:v.co=local@v.co
    o.data.update()
   else:o.matrix_world=T@o.matrix_world
   o['envelope_group']=name;o['envelope_source']='RDSO existing TC or BUR external envelope' if 'Hotel' not in name else 'Inferred smaller case inside CLW2013 available HLC bay, not measured cabinet'
  eq['center']=[x,side*(y0+y1)/2,z0+H/2];eq['dimensions']=[L,D,H];eq['front_y']=side*y0
  entry={'name':name,'external_envelope_m':[L,D,H],'min_world':list(target_min),'max_world':list(target_min+target_dims),'documented_envelope':'Hotel' not in name,'envelope_type':'existing equipment' if 'Hotel' not in name else 'inferred cabinet inside documented available bay','geometry_fit_scale':list(scale)}
  if 'Hotel' not in name:entry['source']='RDSO 2017 WAP7 upgrade p43' if name.startswith('Traction') else 'RDSO auxiliary converter specification 0071 Rev6, existing BUR envelope'
  else:
   entry['source']='CLW/ES/3/IGBT/0490 Alt.B, Oct2013, section8.18 available space, not measured cabinet'
   entry['available_bay_m']=[1.400,1.075,1.750] if 'converter' in name else [.300,1.075,1.750]
   entry['actual_case_dimensions_inferred']=True
  report.append(entry)
 for index in[1,2]:
  name='Hotel_load_equipmentA'+str(index);eq=next(e for e in b.equipment if e['name']==name);x,y,z=eq['center'];L,D,H=eq['dimensions'];side=1 if y>0 else-1
  for xx in[x-.099,x+.099]:
   for yy in[y-D/2+.045,y+D/2-.045]:b.box(name+'_open_support_rail',(xx,yy,2.046),(.027,.034,.772),'steel',.002)
  b.box(name+'_support_shelf',(x,y,2.411),(L+.022,D+.015,.018),'aluminium',.002)
  b.tube(name+'_service_cable_bundle',[(x,y+side*.20,2.76),(x,y+side*.20,2.94),(x-.035,y+side*.20,3.34)],.015,'rubber',12)
 bpy.context.view_layer.update();return report



def perforated_grille(b,n,x,y,z,w,h,side):
 """Open circular perforations in a real thin sheet, not a photo or dark decal."""
 b.box(n+'_filter_dark_interior',(x,y+side*.006,z),(w,.010,h),'black',.001)
 cols=max(4,int(w/.014));rows=max(4,int(h/.014));cw=w/cols;ch=h/rows;r=min(cw,ch)*.245;R=Vector((1,0,0));U=Vector((0,0,1));N=Vector((0,-side,0));thick=.0014
 for ix in range(cols):
  for iz in range(rows):
   c=Vector((x-w/2+cw*(ix+.5),y-side*.009,z-h/2+ch*(iz+.5)));v=[]
   for dd,inner in[(-thick/2,False),(-thick/2,True),(thick/2,False),(thick/2,True)]:
    for j in range(8):
     a=pi/4*j;ca,sa=cos(a),sin(a)
     if inner:xx,zz=r*ca,r*sa
     else:
      fac=1/max(abs(ca),abs(sa));xx,zz=cw/2*ca*fac,ch/2*sa*fac
     v.append(c+R*xx+U*zz+N*dd)
   fs=[]
   for j in range(8):
    k=(j+1)%8;fs.extend([(j,k,8+k,8+j),(16+j,24+j,24+k,16+k),(8+j,8+k,24+k,24+j)])
   b.obj(n+'_punched_filter_sheet',v,fs,'aluminium',batch=True)
 for xx in[x-w/2-.006,x+w/2+.006]:b.box(n+'_perforated_grille_edge',(xx,y-side*.009,z),(.012,.014,h+.024),'steel',.001)
 for zz in[z-h/2-.006,z+h/2+.006]:b.box(n+'_perforated_grille_edge',(x,y-side*.009,zz),(w,.014,.012),'steel',.001)
 for xx in[x-w/2+.014,x+w/2-.014]:
  for zz in[z-h/2-.007,z+h/2+.007]:b.screw(n+'_perforated_grille_screw',(xx,y-side*.018,zz),(0,-side,0),.0032)


def dielectric_enamel(m):
 """Controlled object-metric paint finish, shared recipe with the surface QA owner."""
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');rough=p.inputs['Roughness'].default_value
 p.inputs['Metallic'].default_value=0;p.inputs['IOR'].default_value=1.5;p.inputs['Specular IOR Level'].default_value=.5;p.inputs['Coat Weight'].default_value=0
 for node in list(nt.nodes):
  if node.type not in['BSDF_PRINCIPLED','OUTPUT_MATERIAL']:nt.nodes.remove(node)
 tc=nt.nodes.new('ShaderNodeTexCoord');tc.name='Object-metric paint coordinates'
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.name='1500 per metre paint microfinish';noise.inputs['Scale'].default_value=1500;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.55;nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
 rr=nt.nodes.new('ShaderNodeMapRange');rr.name='Restrained roughness +/- 0.015';rr.inputs['From Min'].default_value=0;rr.inputs['From Max'].default_value=1;rr.inputs['To Min'].default_value=max(0,rough-.015);rr.inputs['To Max'].default_value=min(1,rough+.015);nt.links.new(noise.outputs['Fac'],rr.inputs['Value']);nt.links.new(rr.outputs['Result'],p.inputs['Roughness'])
 bump=nt.nodes.new('ShaderNodeBump');bump.name='Forty micrometre enamel finish';bump.inputs['Distance'].default_value=.000040;bump.inputs['Strength'].default_value=.18;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 m['finish_model']='Dielectric enamel: metallic0, IOR1.5, object-metric1500/m, 40micrometre bump x0.18, roughness +/-0.015'


def raised_hog_mounts(b):
 """Open frames bridge spring pockets; cabinet cases remain intact above them."""
 report=[]
 for index in[1,2]:
  name='Hotel_load_converter'+str(index);eq=next(e for e in b.equipment if e['name']==name);x,y,z=eq['center'];L,D,H=eq['dimensions'];side=1 if y>0 else-1
  front=side*(b.half_width-.01-D+.025);rear=side*(b.half_width-.085);z0=1.524;ztop=1.964
  for xx in[x-L*.37,x+L*.37]:
   b.box(name+'_raised_frame_crossmember',(xx,(front+rear)/2,1.949),(.062,abs(rear-front)+.045,.030),'steel',.003)
   for yy in[front,rear]:
    b.box(name+'_raised_frame_leg',(xx,yy,(z0+ztop)/2),(.049,.039,ztop-z0),'steel',.003)
    b.box(name+'_raised_frame_foot',(xx,yy,z0+.006),(.155,.095,.016),'steel',.002)
    for dx in[-.052,.052]:b.bolt(name+'_raised_frame_anchor',(xx+dx,yy,z0+.022),.007,batch=False)
  for yy in[front,rear]:b.box(name+'_raised_frame_longitudinal',(x,yy,1.949),(L+.021,.047,.030),'steel',.003)
  report.append({'equipment':name,'cabinet_base_z':1.945,'lowest_bridge_z':1.934,'legs_y':[front,rear],'spring_pocket_top_z':1.915,'geometry_claim':'Inferred raised installation frame inside available HLC bay; original cabinet envelope is intact'})
 return report
