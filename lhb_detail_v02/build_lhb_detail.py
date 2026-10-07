"""Detailed LHB coach family revision 02. Blender 4.3.2, metres, X forward, Z up.
Usage: blender -b -t 2 --python build_lhb_detail.py [-- 1A 2A ...]
No photographs, external meshes or textures are used in generated assets.
"""
import bpy, math, os, sys, json, bmesh, hashlib
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
SOURCE_HASHES={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['build_lhb_detail.py','lhb_shell.py','lhb_finish_detail.py','lhb_running_gear.py','lhb_identity_detail.py']}
from lhb_running_gear import build_running_gear

CFG={
'1A':dict(code='LWFAC',capacity=24,ac=True,label='AC FIRST CLASS',layout='4 four-berth cabins + 4 two-berth coupes',color=(.58,.025,.045)),
'2A':dict(code='LWACCW',capacity=52,ac=True,label='AC TWO TIER',layout='8 full six-berth bays + four-berth end bay',color=(.58,.025,.045)),
'3A':dict(code='LWACCN',capacity=72,ac=True,label='AC THREE TIER',layout='9 eight-berth bays; middle berths folded for daytime',color=(.58,.025,.045)),
'2S':dict(code='LWSCZ1',capacity=102,ac=False,label='SECOND SITTING',layout='17 rows of 3+3 upright chairs',color=(.055,.19,.39)),
'CC':dict(code='LWSCZAC',capacity=78,ac=True,label='AC CHAIR CAR',layout='15 rows of 2+3 reclining chairs + 3-seat end row',color=(.04,.17,.35)),
'SL':dict(code='LWSCN1',capacity=80,ac=False,label='SLEEPER',layout='10 eight-berth bays; middle berths folded for daytime',color=(.58,.025,.045)),
'GS':dict(code='LS1',capacity=100,ac=False,label='GENERAL SECOND CLASS',layout='10 ten-seat bays, 4+4 transverse and 2 longitudinal; centre entry',color=(.58,.025,.045)),
}
FLOOR=1.303; TOP=1.840; HIP=.483

def material(n,c,metal=0,rough=.48):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m

def empty(n,loc=(0,0,0),parent=None,coll=None,yaw=0):
 o=bpy.data.objects.new(n,None);(coll or C).objects.link(o);o.parent=parent;o.location=loc;o.rotation_euler.z=yaw;o.empty_display_type='ARROWS';o.empty_display_size=.16;return o

def mesh(n,v,f,m,parent=None,coll=None):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);(coll or C).objects.link(o);o.parent=parent or body;d.materials.append(m)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free();return o

def box(n,loc,dim,m,bev=0,parent=None,coll=None,yaw=0):
 x,y,z=[q/2 for q in dim];o=mesh(n,[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m,parent,coll);o.location=loc;o.rotation_euler.z=yaw
 if bev:
  md=o.modifiers.new('Fabricated edge radius','BEVEL');md.width=min(bev,.45*min(dim));md.segments=3;md.harden_normals=True
  wn=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');wn.keep_sharp=True
 return o

def rod(n,a,b,r,m=None,N=10,parent=None,coll=None):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.01:u=d.cross(Vector((0,1,0)))
 u.normalize();v=d.cross(u);vs=[tuple(c+r*(u*math.cos(i*math.tau/N)+v*math.sin(i*math.tau/N))) for c in [a,b] for i in range(N)];ob=mesh(n,vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m or steel,parent,coll)
 for poly in ob.data.polygons[2:]:poly.use_smooth=True
 return ob

def text(n,t,loc,size=.13,rot=(math.pi/2,0,0),m=None,coll=None):
 d=bpy.data.curves.new(n,'FONT');d.body=t;d.size=size;d.align_x='CENTER';d.extrude=.0004;d.resolution_u=2;o=bpy.data.objects.new(n,d);(coll or C).objects.link(o);o.parent=body;o.location=loc;o.rotation_euler=rot;d.materials.append(m or white);return o

def frame(n,x,y,z,w,h,depth,border=.04,mat=None,parent=None,coll=None):
 # Four closed solids leave a genuine through aperture; no coplanar face behind pane.
 for dx in [-1,1]:box(n+'_jamb',(x+dx*(w-border)/2,y,z),(border,depth,h),mat or rubber,.008,parent,coll)
 for dz in [-1,1]:box(n+'_rail',(x,y,z+dz*(h-border)/2),(w-2*border,depth,border),mat or rubber,.008,parent,coll)

def seatmark(n,x,y,yaw,cushion=TOP,kind='day_seat'):
 o=empty('PAX_'+n,(x,y,cushion-HIP),body,marks,yaw);o['purpose']='TF3 seated character ROOT, not pelvis or cushion';o['pose']='sitting';o['forward_axis']='+X';o['cushion_top_z_m']=cushion;o['posed_hip_offset_m']=HIP;o['placement_kind']=kind;pax.append(o);return o

def berthmark(n,x,y,z,kind):
 o=empty('BERTH_'+n,(x,y,z),body,marks);o['purpose']='Sleeping-capacity reference only. Exclude from seated passenger provider';o['berth_type']=kind;berths.append(o)

def fan(x,y):
 rod('FAN_stem',(x,y,3.53),(x,y,3.38),.025,steel,8,coll=inter)
 rod('FAN_motor',(x,y,3.30),(x,y,3.41),.075,ivory,12,coll=inter)
 for a in range(3):box('FAN_blade',(x+math.cos(a*math.tau/3)*.13,y+math.sin(a*math.tau/3)*.13,3.34),(.26,.075,.012),ivory,.01,coll=inter,yaw=a*math.tau/3)
 for z in [3.28,3.38]:
  for k in range(20):
   a=k*math.tau/20;b=(k+1)*math.tau/20;rod('FAN_guard',(x+.24*math.cos(a),y+.24*math.sin(a),z),(x+.24*math.cos(b),y+.24*math.sin(b),z),.005,steel,6,coll=inter)

def rack(x,y,w):
 for z in [2.96]:
  for yy in [y-.18,y,y+.18]:rod('LUGGAGE_RACK_rail',(x-w/2,yy,z),(x+w/2,yy,z),.012,steel,8,coll=inter)
  for j in range(max(2,int(w/.13))):
   xx=x-w/2+j*w/max(1,int(w/.13)-1);rod('LUGGAGE_RACK_crossbar',(xx,y-.20,z),(xx,y+.20,z),.008,steel,6,coll=inter)


def common(k,c):
 global root,body,C,inter,roof,glasscoll,marks,pax,berths,steel,ivory,blue,rubber,white,floor,paint,grey,glass,wood,edge
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 C=bpy.data.collections.new('LHB_'+k+'_ASSET');sc.collection.children.link(C)
 def collection(n):q=bpy.data.collections.new(n);C.children.link(q);return q
 inter=collection('INTERIOR_'+k);roof=collection('ROOF_REMOVABLE');glasscoll=collection('GLASS_TRANSMISSIVE');marks=collection('PASSENGER_AND_BERTH_MARKERS')
 root=empty('LHB_'+k+'_ROOT_metres');body=empty('BODY_PIVOT',parent=root)
 root['source_module_sha256']=json.dumps(SOURCE_HASHES,sort_keys=True)
 root['lavatory_count']=3 if k=='1A' else 4;root['family']='LHB';root['variant']=k;root['prototype_code']=c['code'];root['physical_capacity']=c['capacity'];root['game_capacity']='Unassigned; physical capacity is not game payload';root['provenance']='Original procedural geometry; representative equipment positions; not manufacturer CAD'
 pax=[];berths=[]
 paint=material('Class_livery',c['color'],.08,.30);grey=material('Lower_body_light_grey',(.48,.52,.55),.08,.35);steel=material('Satin_stainless',(.36,.43,.46),.78,.28);rubber=material('Rubber_and_equipment',(.016,.022,.025),.05,.72);ivory=material('Warm_FRP_liners',(.70,.71,.65));blue=material('Upholstery_'+k, (.29,.025,.032) if k=='1A' else ((.04,.16,.24) if k=='CC' else (.045,.14,.28)),0,.63);white=material('Signs_and_diffusers',(.83,.88,.87));floor=material('Non_slip_floor',(.115,.16,.19),0,.85);wood=material('Pale_table_laminate',(.56,.43,.24));edge=material('Upholstery_piping',(.015,.047,.073))
 glass=material('GLASS_source_transmission_FBX_alpha',(.86,.94,.95),0,.075);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.96;p.inputs['IOR'].default_value=1.45;glass['export_note']='FBX material uses Alpha 0.22 fallback; source master uses Transmission .96 Alpha1'
 box('UNDERFRAME_main',(0,0,1.155),(23.54,2.96,.26),rubber,.025)
 box('INTERIOR_floor',(0,0,FLOOR-.025),(23.40,3.10,.05),floor,coll=inter)
 for y in [-1.53,1.53]:box('UNDERFRAME_edge',(0,y,1.22),(23.54,.10,.21),grey,.025)
 for x in [-8,-6,-4,-2,0,2,4,6,8]:box('UNDERFRAME_crossmember',(x,0,1.09),(.12,2.8,.12),steel,.008)
 # Detailed gear is isolated in an independently reviewed module.
 build_running_gear(None,root,body,C,c["ac"])
 import lhb_shell
 lhb_shell.build(globals(),k,c)
 # Lighting/fan/AC distinction, spaced along passenger area.
 for x in [-7.5,-5.6,-3.7,-1.8,.1,2.0,3.9,5.8,7.7]:
  box('LIGHT_diffuser',(x,.63 if k in ['1A','2A','3A','SL','GS'] else 0,3.578),(.7,.18,.025),white,.012,coll=inter)
  if c['ac']:
   for y in [-1.05,1.05]:
    box('AC_ceiling_vent',(x,y,3.58),(.6,.18,.025),rubber,.006,coll=inter)
    for j in range(6):box('AC_vent_slats',(x-.25+j*.10,y,3.565),(.015,.175,.01),ivory,coll=inter)
  else:
   for y in [-.55,.78]:fan(x,y)
 for e in [-1,1]:
  box('VESTIBULE_cabinet',(e*9.15,-1.13,2.25),(.55,.68,1.88),ivory,.018,coll=inter)
  rod('FIRE_EXTINGUISHER',(e*9.28,-.72,1.75),(e*9.28,-.72,2.28),.074,paint,12,coll=inter)
 return sc


def sleeping(k,c):
 if k=='1A':
  lengths=[2.50,1.73,2.50,1.73,1.73,2.50,1.73,2.50];cur=-sum(lengths)/2
  for i,L in enumerate(lengths):
   x=cur+L/2;cab=L>2;ends=[-1,1] if cab else [-1]
   box('CABIN_partition_'+str(i),(cur,-.51,2.45),(.055,1.98,2.25),ivory,.008,coll=inter)
   # Full corridor wall with actual sliding-door opening; door shown partly stowed.
   for a,b in [(cur, x-.37),(x+.37,cur+L)]:
    if b>a:box('CABIN_corridor_wall',((a+b)/2,.505,2.45),(b-a,.055,2.25),ivory,.008,coll=inter)
   box('CABIN_door_header',(x,.505,3.43),(.74,.055,.25),ivory,.006,coll=inter)
   box('CABIN_sliding_door_partly_open',(x+.55,.545,2.37),(.69,.035,2.1),wood,.014,coll=inter)
   rod('CABIN_door_handle',(x+.28,.573,2.0),(x+.28,.573,2.31),.012,steel,coll=inter)
   text('CABIN_label',chr(65+i)+' '+('CABIN' if cab else 'COUPE'),(x,.548,3.41),.065,rot=(math.pi/2,0,math.pi),m=rubber,coll=inter)
   for e in ends:
    xx=x+e*(L/2-.40);cid=chr(65+i)+('_A' if e<0 else '_B')
    for z,typ in [(TOP-.06,'LOWER'),(3.02,'UPPER')]:
     box('FIRST_'+typ+'_'+cid,(xx,-.49,z),(.73,1.92,.12),blue,.05,coll=inter)
     box('FIRST_berth_pan',(xx,-.49,z-.078),(.75,1.94,.03),steel,.01,coll=inter)
     berthmark(cid+'_'+typ,xx,-.49,z+.06,typ)
    box('FIRST_backrest',(xx+e*.325,-.49,2.20),(.12,1.92,.70),blue,.04,coll=inter)
    for yy in [-.96,-.04]:seatmark(cid+str(yy),xx-e*.08,yy,0 if e<0 else math.pi)
    for yy in [-1.2,.22]:rod('FIRST_berth_support',(xx,yy,FLOOR),(xx,yy,1.7),.025,steel,coll=inter)
    # short stair at aisle end (outside seat root positions)
    for j in range(4):box('FIRST_upper_access_step',(xx-e*.30,.31,1.7+j*.30),(.23,.25,.045),wood,.02,coll=inter)
    rod('FIRST_upper_guard',(xx-.28,.48,3.24),(xx+.28,.48,3.24),.017,steel,coll=inter)
   box('CABIN_window_table',(x,-1.24,2.10),(.50,.43,.035),wood,.015,coll=inter)
   rack(x,-1.13,min(.70,L-.9));cur+=L
  box('CABIN_end_partition',(cur,-.51,2.45),(.055,1.98,2.25),ivory,.008,coll=inter)
  return
 if k=='2A':bayxs=[(-7.6+j*1.9,False) for j in range(8)]+[(7.93,True)];pitch=1.9
 else:n=9 if k=='3A' else 10;pitch=1.85 if k=='3A' else 1.80;bayxs=[(-(n-1)*pitch/2+j*pitch,False) for j in range(n)]
 for i,(x,partial) in enumerate(bayxs):
  ends=[-1] if partial else [-1,1]
  for e in ends:
   xx=x+e*(pitch/2-.31);name=f'{i+1:02d}_'+('A' if e<0 else 'B')
   for z,typ in [(TOP-.06,'LOWER'),(3.15 if k!='2A' else 3.05,'UPPER')]:
    box('MAIN_'+typ+'_'+name,(xx,-.56,z),(.60,1.82,.12),blue,.042,coll=inter)
    box('BERTH_pan',(xx,-.56,z-.076),(.63,1.85,.028),steel,.008,coll=inter)
    berthmark(name+'_'+typ,xx,-.56,z+.06,typ)
   backx=x+e*(pitch/2-.075)
   box(('MIDDLE_FOLDED_' if k!='2A' else 'LOWER_BACKREST_')+name,(backx,-.56,2.19),(.12,1.82,.69),blue,.038,coll=inter)
   if k!='2A':berthmark(name+'_MIDDLE',xx,-.56,2.50,'MIDDLE_STOWED_REFERENCE')
   nseat=2 if k=='2A' else 3
   ys=[-.99,.02] if nseat==2 else [-1.14,-.56,.02]
   for j,yy in enumerate(ys):seatmark(name+f'_{j+1}',xx-e*.065,yy,0 if e<0 else math.pi)
   for yy in [-1.29,.20]:box('LOWER_support',(xx,yy,1.53),(.055,.055,.43),steel,.008,coll=inter)
   for dx in [-.19,.19]:rod('LADDER_rail',(xx+dx,.39,1.40),(xx+dx,.39,3.31),.014,steel,coll=inter)
   for zz in [1.66,1.96,2.26,2.56,2.86]:rod('LADDER_rung',(xx-.19,.39,zz),(xx+.19,.39,zz),.013,steel,coll=inter)
   rod('BERTH_upper_guard',(xx-.24,.39,3.37),(xx+.24,.39,3.37),.014,steel,coll=inter)
  # Each partial end bay still has a side pair. No fictional middle side berth.
  for z,typ in [(TOP-.06,'LOWER'),(3.08,'UPPER')]:
   box('SIDE_'+typ+f'_{i}',(x,1.24,z),(pitch-.14,.57,.12),blue,.04,coll=inter);berthmark(f'{i+1:02d}_SIDE_'+typ,x,1.24,z+.06,'SIDE_'+typ)
  for e in [-1,1]:
   box('SIDE_day_backrest',(x+e*(pitch/2-.12),1.24,2.13),(.10,.57,.55),blue,.03,coll=inter)
   seatmark(f'{i+1:02d}_SIDE_'+str(e),x+e*(pitch/2-.37),1.24,0 if e<0 else math.pi)
  box('BAY_partition',(x+pitch/2,-.56,2.43),(.045,1.86,2.20),ivory,.007,coll=inter)
  box('SIDE_partition',(x+pitch/2,1.24,2.43),(.045,.57,2.20),ivory,.007,coll=inter)
  box('WINDOW_table',(x,-1.28,2.025),(.36,.40,.03),wood,.012,coll=inter)
  if k=='2A':
   rod('BAY_curtain_track',(x-pitch/2,.43,3.47),(x+pitch/2,.43,3.47),.012,steel,coll=inter)
   for j in range(4):box('PRIVACY_curtain_gathered',(x-pitch/2+.04+j*.023,.455,2.42),(.029,.035,1.95),blue,.005,coll=inter)
  text('BAY_NUMBER',str(i+1),(x+pitch/2,.392,3.39),.075,rot=(math.pi/2,0,math.pi),m=rubber,coll=inter)


def chair(k,c):
 rows=17 if k=='2S' else 16;pitch=1.04 if k=='2S' else 1.07
 ys=[-1.28,-.85,-.42,.42,.85,1.28] if k=='2S' else [-1.24,-.72,.25,.75,1.25]
 for i in range(rows):
  x=(i-(rows-1)/2)*pitch;ylist=ys if k=='2S' or i<15 else ys[2:]
  # Half saloon faces inward; seats are individually upholstered, not berth recolours.
  facing=1 if i<rows//2 else -1
  for j,y in enumerate(ylist):
   n=f'{i+1:02d}_{j+1}';w=.390 if k=='2S' else .455
   box('CHAIR_cushion_'+n,(x,y,TOP-.06),(.49,w,.12),blue,.045,coll=inter)
   back=box('CHAIR_back_'+n,(x-facing*.225,y,2.14),(.105,w,.65),blue,.047,coll=inter);back.rotation_euler.y=-facing*(.05 if k=='2S' else .13)
   box('CHAIR_pedestal_'+n,(x-.06*facing,y,1.52),(.09,.10,.43),steel,.016,coll=inter)
   if k=='CC':
    box('HEADREST_'+n,(x-facing*.265,y,2.43),(.13,w*.79,.18),white,.034,coll=inter)
    box('SEATBACK_tray_'+n,(x-facing*.30,y,2.11),(.033,w*.76,.27),ivory,.019,coll=inter)
   for s in ([-1,1] if k!='2S' or j==len(ylist)-1 or ylist[j+1]-y>.60 else [-1]):
    box('CHAIR_armrest_'+n,(x,y+s*(w/2+.008),2.00),(.43,.035,.045),rubber,.014,coll=inter)
    rod('ARM_support_'+n,(x-facing*.10,y+s*(w/2+.008),1.79),(x-facing*.10,y+s*(w/2+.008),1.99),.011,steel,coll=inter)
   seatmark(n,x+.035*facing,y,0 if facing>0 else math.pi)
 for y in [-1.17,1.17]:rack(0,y,17.8)
 if k=='CC':
  box('CC_luggage_stack',(8.7,-.96,2.14),(.85,1.0,1.66),ivory,.02,coll=inter)
  for z in [1.8,2.35,2.90]:box('CC_luggage_shelf',(8.68,-.95,z),(.78,.94,.04),steel,.006,coll=inter)


def general(c):
 # Legacy LS1 drawing: ten 10-seat bays with central pair of doors.
 for s in [-1,1]:
  for i in range(5):
   x=s*(1.25+i*1.68)
   for e in [-1,1]:
    xx=x+e*.54;n=f'{s}_{i}_{e}'
    box('GS_main_bench_'+n,(xx,-.54,TOP-.06),(.53,1.92,.12),blue,.027,coll=inter)
    box('GS_bench_back_'+n,(xx+e*.23,-.54,2.10),(.09,1.92,.55),blue,.02,coll=inter)
    for j,y in enumerate([-1.26,-.78,-.30,.18]):seatmark(n+'_'+str(j),xx-e*.045,y,0 if e<0 else math.pi)
    for y in [-1.27,.18]:box('GS_bench_leg',(xx,y,1.52),(.05,.05,.43),steel,.01,coll=inter)
    rack(xx,-.55,.58)
   box('GS_side_bench',(x,1.24,TOP-.06),(1.46,.56,.12),blue,.03,coll=inter)
   for e in [-1,1]:
    box('GS_side_back',(x+e*.68,1.24,2.10),(.09,.56,.55),blue,.02,coll=inter)
    seatmark(f'{s}_{i}_SIDE_{e}',x+e*.43,1.24,0 if e<0 else math.pi)
   rack(x,1.20,1.5)
   # Luggage racks, not sleeping berths, have no BERTH markers.
   for yy in [.48,.96]:rod('GS_vertical_grab',(x+.79,yy,FLOOR),(x+.79,yy,3.38),.015,steel,coll=inter)


def finish(k,c):
 sc=bpy.context.scene;bpy.context.view_layer.update()
 assert len(pax)==c['capacity'],(k,len(pax),c['capacity'])
 assert len(berths)==(c['capacity'] if k in ['1A','2A','3A','SL'] else 0),(k,len(berths))
 root['seated_character_root_count']=len(pax);root['berth_reference_count']=len(berths);root['cushion_top_z_m']=TOP;root['PAX_root_z_m']=TOP-HIP;root['hip_offset_reference']='TF3-INSTALL.md revision11 stock sitting pelvis test; full-character runtime fit remains untested'
 # Numeric topology/bounds in separate verifier; save uncluttered source with studio collection.
 studio=bpy.data.collections.new('PRESENTATION_ONLY');sc.collection.children.link(studio)
 world=bpy.data.worlds.new('Studio_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.38,.46,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;sc.world=world
 for name,loc,power,size in [('Key',(2,-10,16),2400,12),('Fill',(-10,6,11),1800,10),('Rim',(10,3,12),1900,8)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.8))-o.location).to_track_quat('-Z','Y').to_euler()
 for x in [-7,-3,1,5,8]:
  d=bpy.data.lights.new('Interior_fill','AREA');d.energy=25;d.shape='RECTANGLE';d.size=2;d.size_y=1;o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.location=(x,.1,3.50)
 d=bpy.data.cameras.new('CAMERA_exterior');o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.location=(20,-29,13);o.rotation_euler=(Vector((0,0,1.9))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=27;d.clip_start=.01;sc.camera=o
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1400;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 path=P/'models'/('LHB_'+k);bpy.ops.wm.save_as_mainfile(filepath=str(path)+'.blend',compress=True)
 # Export only root descendants, with the explicitly documented alpha fallback material.
 p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=0;p.inputs['Alpha'].default_value=.22;glass.diffuse_color=(*glass.diffuse_color[:3],.22)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.fbx(filepath=str(path)+'.fbx',use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
 payload={'source_module_sha256':SOURCE_HASHES,'variant':k,'prototype_code':c['code'],'physical_capacity':c['capacity'],'capacity_type':'berths' if berths else 'seats','daytime_seats':len(pax),'PAX_roots':len(pax),'BERTH_references':len(berths),'layout':c['layout'],'game_capacity':None,'root':'LHB_'+k+'_ROOT_metres','body_length_m':23.54,'coupling_span_m':24.0,'body_width_m':3.24,'roof_height_m':4.039,'bogie_centres_m':14.9,'bogie_wheelbase_m':2.56,'wheel_tread_diameter_m':.915,'floor_height_m':FLOOR,'seat_cushion_top_z_m':TOP,'seat_character_root_z_m':TOP-HIP,'glass_source_transmission':.96,'glass_fbx_alpha':.22,'native_TF3_conversion':False,'runtime_tested':False}
 (P/'models'/('LHB_'+k+'_manifest.json')).write_text(json.dumps(payload,indent=2))
 markers_payload={'source_module_sha256':SOURCE_HASHES,'variant':k,'PAX_character_roots':[{'name':o.name,'parent':o.parent.name,'position_parent_m':list(o.location),'yaw_radians':o.rotation_euler.z,'cushion_top_z_m':TOP,'pose':'sitting'} for o in sorted(pax,key=lambda o:o.name)],'BERTH_sleeping_references':[{'name':o.name,'position_parent_m':list(o.location),'berth_type':o['berth_type'],'use_as_seated_passenger':False} for o in sorted(berths,key=lambda o:o.name)]}
 (P/'models'/('LHB_'+k+'_markers.json')).write_text(json.dumps(markers_payload,indent=2))
 print('FINISHED',k,len(pax),len(berths),flush=True)

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(CFG)
for d in ['models','previews','qa','docs']:(P/d).mkdir(exist_ok=True)
for k in args:
 c=CFG[k];common(k,c)
 if k in ['1A','2A','3A','SL']:sleeping(k,c)
 elif k in ['2S','CC']:chair(k,c)
 else:general(c)
 import lhb_finish_detail
 lhb_finish_detail.refine(globals(),k,c)
 import lhb_identity_detail
 lhb_identity_detail.apply(globals(),k,c)
 finish(k,c)
