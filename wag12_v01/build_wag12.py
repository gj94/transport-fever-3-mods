"""Original WAG12B modelling-only handoff, Blender4.3.2.
Run: blender -b -t 2 --python build_wag12.py -- [output_directory]
This script is self-contained and changes only its output directory.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path(__file__).resolve().parent
for d in ('sections','assemblies','qa','renders'):(P/d).mkdir(parents=True,exist_ok=True)
M={};BATCH={};COL=None;ROOT=None;BODY=None
PI=math.pi;SPAN=19.2;BW=3.058;HALF=BW/2;PANTO_BASE=4.136;L1=2.4;L2=2.;STRIP=.032
A0=math.asin((4.245-PANTO_BASE-STRIP)/(L1+L2));A1=math.asin((7.52-PANTO_BASE-STRIP)/(L1+L2));NORMAL=(math.asin((5.917-PANTO_BASE-STRIP)/(L1+L2))-A0)/(A1-A0)

def material(name,color,metal=0,rough=.4,trans=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;n.inputs['Transmission Weight'].default_value=trans;n.inputs['IOR'].default_value=1.45
 if emit:n.inputs['Emission Color'].default_value=(*color,1);n.inputs['Emission Strength'].default_value=emit
 M[name]=m

def materials():
 for vals in [('IR_blue',(.014,.19,.48),.25,.29),('Cyan_chevron',(.11,.52,.85),.25,.3),('Nose_dark',(.027,.038,.043),.15,.35),('Roof_aluminium',(.49,.56,.58),.6,.43),('Bogie_grey',(.105,.125,.13),.45,.5),('Machinery_dark',(.041,.05,.055),.35,.5),('Steel',(.36,.41,.44),.9,.26),('Wheel_edge',(.60,.65,.67),.9,.22),('Rubber',(.008,.012,.015),0,.8),('White_marking',(.88,.9,.89),.1,.4),('Safety_yellow',(.97,.63,.015),.2,.35),('Copper',(.43,.20,.07),.8,.34),('Insulator',(.24,.12,.065),.1,.24),('Interior_cream',(.66,.69,.68),0,.5),('Desk_bluegrey',(.16,.25,.28),.1,.4),('Seat_cloth',(.045,.07,.085),0,.83),('Cab_floor',(.063,.071,.077),0,.85),('Switch_black',(.014,.018,.021),.1,.34),('Red',(.66,.015,.012),.1,.34),('Green',(.012,.43,.07),.1,.4),('Orange',(.95,.24,.008),.15,.35)]:material(*vals)
 material('Clear_glass',(.86,.96,1),rough=.055,trans=.98)
 material('Lamp_white',(.76,.87,1),rough=.2,emit=.6);material('Screen_teal',(.035,.29,.29),rough=.3,emit=.3);material('Screen_blue',(.025,.11,.29),rough=.2,emit=.2)

def empty(n,pa=None,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);COL.objects.link(o);o.parent=pa;o.location=loc;o.empty_display_type='ARROWS';o.empty_display_size=.12;return o

def add(n,pa,v,f,ma):
 key=(n,pa.name,ma)
 if key not in BATCH:BATCH[key]=[[],[]]
 vv,ff=BATCH[key];off=len(vv);vv.extend(v);ff.extend(tuple(off+j for j in p) for p in f)

def box(n,pa,c,d,ma,rot=None):
 v=[Vector((x*d[0]/2,y*d[1]/2,z*d[2]/2)) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 if rot:v=[rot@p for p in v]
 add(n,pa,[tuple(p+Vector(c)) for p in v],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],ma)

def rounded(n,pa,c,d,ma,r=.04):
 x,y,z=c;dx,dy,dz=d;r=min(r,dx*.22,dy*.22,dz*.4);v=[]
 for zz,rr in [(-dz/2,r*.50),(-dz/2+r,r),(dz/2-r,r),(dz/2,r*.50)]:
  for xx,yy,a in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
   for k in range(4):
    th=math.radians(a+k*30);v.append((x+xx*(dx/2-r)+rr*math.cos(th),y+yy*(dy/2-r)+rr*math.sin(th),z+zz))
 f=[tuple(range(15,-1,-1)),tuple(range(48,64))]
 for k in range(3):
  for j in range(16):f.append((16*k+j,16*k+(j+1)%16,16*(k+1)+(j+1)%16,16*(k+1)+j))
 add(n,pa,v,f,ma)

def rod(n,pa,a,b,r,ma,seg=12):
 a,b=Vector(a),Vector(b);w=(b-a).normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.1:u=w.cross(Vector((0,1,0)))
 u.normalize();v=w.cross(u);verts=[]
 for p in [a,b]:
  for i in range(seg):verts.append(tuple(p+r*(u*math.cos(i*math.tau/seg)+v*math.sin(i*math.tau/seg))))
 faces=[tuple(range(seg-1,-1,-1)),tuple(range(seg,seg*2))]+[(i,(i+1)%seg,seg+(i+1)%seg,seg+i) for i in range(seg)]
 add(n,pa,verts,faces,ma)

def line(n,pa,pts,r,ma,seg=8):
 for a,b in zip(pts,pts[1:]):rod(n,pa,a,b,r,ma,seg)

def slab(n,pa,pts,thickness,ma,axis=(0,0,1)):
 # Closed prism so glazing always has a real inward thickness.
 v=[Vector(p) for p in pts];delta=Vector(axis)*thickness;v=v+[p-delta for p in v];k=len(pts)
 faces=[tuple(range(k)),tuple(range(2*k-1,k-1,-1))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 add(n,pa,[tuple(p) for p in v],faces,ma)

def text(n,pa,s,c,size,ma,rot=(PI/2,0,0)):
 cu=bpy.data.curves.new(n,'FONT');cu.body=s;cu.align_x='CENTER';cu.size=size;cu.extrude=.0005;cu.resolution_u=3
 o=bpy.data.objects.new(n,cu);COL.objects.link(o);o.parent=pa;o.location=c;o.rotation_euler=rot;cu.materials.append(M[ma]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)

def flush():
 for (n,pa,ma),(v,f) in BATCH.items():
  me=bpy.data.meshes.new(n+'_mesh');me.from_pydata(v,[],f);me.materials.append(M[ma]);me.update()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  o=bpy.data.objects.new(n,me);COL.objects.link(o);o.parent=bpy.data.objects[pa]
 BATCH.clear()

def coil(n,pa,c,r,h,ma):
 pts=[(c[0]+r*math.cos(6*math.tau*i/72),c[1]+r*math.sin(6*math.tau*i/72),c[2]+h*i/72) for i in range(73)];line(n,pa,pts,.022,ma,6)

def bogies():
 for label,x in [('A',5.1),('B',-5.1)]:
  b=empty('BOGIE_'+label+'_YAW_Z',ROOT,(x,0,.88));b['pivot_axis']='Z';b['wheelbase_m']=2.6
  for s in (-1,1):
   rounded('Bogie_'+label+'_sideframe',b,(0,s*1.11,.12),(3.65,.18,.24),'Bogie_grey',.035)
   for xx in (-.54,.54):rod('Secondary_springs_'+label,b,(xx,s*.98,.30),(xx,s*.98,.54),.22,'Rubber',24)
   for xx in (-1.3,1.3):
    rounded('Axleboxes_'+label,b,(xx,s*1.12,-.255),(.39,.32,.34),'Bogie_grey',.04)
    rod('Axlebox_caps_'+label,b,(xx,s*1.27,-.255),(xx,s*1.30,-.255),.16,'Steel',24)
    for k in range(6):
     a=k*math.tau/6;rod('Axlebox_bolts_'+label,b,(xx+.115*math.cos(a),s*1.30,-.255+.115*math.sin(a)),(xx+.115*math.cos(a),s*1.32,-.255+.115*math.sin(a)),.022,'Machinery_dark',6)
    for dx in (-.29,.29):
     coil('Primary_coils_'+label,b,(xx+dx,s*1.09,-.24),.092,.36,'Steel')
     box('Spring_seats_'+label,b,(xx+dx,s*1.09,-.255),(.24,.24,.05),'Bogie_grey')
    rod('Primary_dampers_'+label,b,(xx+.38,s*1.28,-.17),(xx+.24,s*1.28,.27),.038,'Machinery_dark',12)
    rod('Damper_rods_'+label,b,(xx+.28,s*1.28,.13),(xx+.24,s*1.28,.38),.021,'Steel',10)
   # Open triangulated frame web; no plate painted over wheels.
   for dx in (-1,1):
    slab('Bogie_web_brackets_'+label,b,[(dx*.16,s*1.20,.07),(dx*1.00,s*1.20,.07),(dx*.67,s*1.20,-.37),(dx*.28,s*1.20,-.29)],.10,'Bogie_grey',(0,s,0))
   for xx in (-.43,.43):rod('Frame_inspection_rings_'+label,b,(xx,s*1.24,-.08),(xx,s*1.28,-.08),.12,'Steel',24);rod('Frame_recess_'+label,b,(xx,s*1.28,-.08),(xx,s*1.29,-.08),.087,'Machinery_dark',24)
   line('Bogie_pipework_'+label,b,[(-1.9,s*1.27,-.28),(-.8,s*1.27,-.54),(.75,s*1.27,-.54),(1.95,s*1.27,-.23)],.026,'Steel')
   rod('Yaw_damper_'+label,b,(-.55,s*1.32,.34),(.35,s*1.32,.45),.05,'Bogie_grey',12)
   rod('Yaw_damper_chrome_'+label,b,(.32,s*1.32,.445),(.74,s*1.32,.50),.022,'Steel',10)
  for xx in (-.7,.7):box('Bogie_crossmembers_'+label,b,(xx,0,.07),(.26,2.20,.20),'Bogie_grey')
  rod('Bogie_central_pivot_'+label,b,(0,0,.2),(0,0,.60),.24,'Steel',24)
  for i,xx in enumerate((1.3,-1.3),1):
   a=empty(f'AXLE_{label}_{i}_ROLL_Y',b,(xx,0,.625-.88));a['pivot_axis']='Y';a['wheel_tread_diameter_m']=1.25
   rod('Axle_shaft_'+label+str(i),a,(0,-1.18,0),(0,1.18,0),.1,'Steel',16)
   for s in (-1,1):
    rod('Wheels_tread_'+label+str(i),a,(0,s*.838-.073,0),(0,s*.838+.073,0),.625,'Wheel_edge',64)
    rod('Wheels_web_'+label+str(i),a,(0,s*.903,0),(0,s*.975,0),.50,'Bogie_grey',48)
    rod('Wheels_flange_'+label+str(i),a,(0,s*.742,0),(0,s*.765,0),.652,'Steel',64)
    rod('Wheels_hub_'+label+str(i),a,(0,s*.96,0),(0,s*1.09,0),.17,'Steel',24)
    for k in range(8):
     an=k*math.tau/8;rod('Wheel_web_recess_'+label+str(i),a,(.365*math.cos(an),s*.978,.365*math.sin(an)),(.365*math.cos(an),s*.982,.365*math.sin(an)),.04,'Machinery_dark',8)
    box('Brake_shoes_'+label,b,(xx+.59,s*.90,-.19),(.10,.22,.31),'Machinery_dark')
    rod('Brake_cylinders_'+label,b,(xx+.43,s*1.02,.13),(xx+.71,s*1.02,.13),.105,'Bogie_grey',16)
    line('Sand_delivery_'+label,b,[(xx+.77,s*1.10,.02),(xx+.80,s*.84,-.36),(xx+.56,s*.84,-.52)],.028,'Safety_yellow')
   rod('Traction_motors_'+label,b,(xx-.24,-.55,-.09),(xx-.24,.55,-.09),.25,'Machinery_dark',20)
   rounded('Gearcase_'+label,b,(xx,.56,-.22),(.48,.28,.54),'Bogie_grey',.04)

def nose_x(z,y=0):return 9.13-.39*max(0,z-2.35)/1.55-.105*abs(y)/HALF
def crown_z(y):return 3.92-.14*(abs(y)/HALF)**4
def front_z(z,y):return 3.62+(z-3.62)/.30*(crown_z(y)-3.62) if z>3.62 else z

def body_shell(section):
 body=BODY
 rounded('Underframe_main',body,(0,0,1.405),(18.15,2.93,.29),'Bogie_grey',.05)
 for s in (-1,1):
  box('Underframe_sill',body,(-.02,s*1.49,1.47),(18.1,.13,.27),'Machinery_dark')
  box('Cyan_lower_belt',body,(-.35,s*1.534,1.685),(17.50,.015,.095),'Cyan_chevron')
  # Machine-room sides and cab apertures. Large side intake at x4.0, small service window rear.
  holes=[(6.10,6.88,1.59,3.55),(7.12,8.54,2.58,3.56),(-7.90,-7.26,2.67,3.38)]
  xs=sorted(set([-9.02,8.72]+[q for h in holes for q in h[:2]]));zs=sorted(set([1.61,3.78]+[q for h in holes for q in h[2:]]))
  for a,b in zip(xs,xs[1:]):
   for za,zb in zip(zs,zs[1:]):
    if any(h[0]<(a+b)/2<h[1] and h[2]<(za+zb)/2<h[3] for h in holes):continue
    if a>8.54 and za>2.58:continue
    ma='Nose_dark' if a>6.88 and za>=2.58 else 'IR_blue'
    box('Body_side_open_shell',body,((a+b)/2,s*(HALF-.035),(za+zb)/2),(b-a,.07,zb-za),ma)
  # Cab interior side wall follows real openings, never a full backing cube.
  for a,b in [(5.85,6.1),(6.88,7.12),(8.54,8.68)]:box('Cab_side_pillars',body,((a+b)/2,s*1.44,2.65),(b-a,.10,1.98),'Interior_cream')
  for a,b in [(7.12,8.54)]:
   for z,h in [(2.105,.95),(3.66,.20)]:box('Cab_side_inner_panels',body,((a+b)/2,s*1.444,z),(b-a,.10,h),'Interior_cream')
  for x0,x1,z0,z1 in [(7.12,8.54,2.58,3.56),(-7.9,-7.26,2.67,3.38)]:
   box('Sidewindow_glass',body,((x0+x1)/2,s*1.517,(z0+z1)/2),(x1-x0-.05,.006,z1-z0-.05),'Clear_glass')
   for x in (x0,x1):box('Sidewindow_rubber',body,(x,s*1.536,(z0+z1)/2),(.035,.032,z1-z0+.04),'Rubber')
   for z in (z0,z1):box('Sidewindow_rubber',body,((x0+x1)/2,s*1.536,z),(x1-x0,.032,.035),'Rubber')
  # Cab door with open glazing and working hinge group.
  d=empty(f'DOOR_{"L" if s>0 else "R"}_CAB_HINGE_Z',body,(6.10,s*1.50,1.59));d['open_rotation_z_deg']=s*72;d['type']='hinged cab access door'
  for x,w in [(.08,.16),(.69,.18)]:box('Cab_door_frame',d,(x,0,.98),(w,.08,1.96),'IR_blue')
  for z,h in [(.43,.86),(1.845,.23)]:box('Cab_door_leaf',d,(.38,0,z),(.44,.08,h),'IR_blue')
  box('Cab_door_glass',d,(.38,s*.044,1.30),(.42,.006,.84),'Clear_glass')
  for x in (.15,.61):box('Cab_door_glass_seals',d,(x,s*.052,1.30),(.025,.022,.88),'Rubber')
  for z in (.86,1.74):box('Cab_door_glass_seals',d,(.38,s*.052,z),(.49,.022,.027),'Rubber')
  rod('Door_handle',d,(.67,s*.085,.88),(.67,s*.085,1.06),.016,'Steel',10)
  for z in (.35,1.50):rod('Door_hinges',body,(6.08,s*1.55,1.59+z),(6.08,s*1.55,1.73+z),.024,'Steel',10)
  for x in (5.98,7.02):line('Cab_grab_rails',body,[(x,s*1.54,1.56),(x,s*1.59,1.76),(x,s*1.59,2.77)],.017,'Steel')
  for z,x in [(1.13,6.50),(.73,6.50),(.36,6.50)]:
   box('Cab_step_treads',body,(x,s*1.53,z),(.70,.155,.042),'Steel')
   for xx in [x-.25,x-.1,x+.1,x+.25]:box('Step_antislip',body,(xx,s*1.53,z+.025),(.018,.14,.01),'Machinery_dark')
  for x in (6.16,6.84):box('Cab_step_stringers',body,(x,s*1.45,.8),(.055,.08,1.45),'Machinery_dark')
  # Long recessed radiator grille and small hardware details.
  gx=3.83;box('Main_intake_recess',body,(gx,s*1.535,2.56),(1.30,.032,1.75),'Rubber')
  for xx in (gx-.69,gx+.69):box('Intake_rim',body,(xx,s*1.56,2.56),(.048,.065,1.82),'Bogie_grey')
  for z in (1.65,3.47):box('Intake_rim',body,(gx,s*1.56,z),(1.41,.065,.045),'Bogie_grey')
  for j in range(32):box('Intake_louvres',body,(gx,s*1.565,1.73+j*.052),(1.30,.038,.018),'Machinery_dark')
  for xx in (gx-.40,gx,gx+.40):box('Intake_verticals',body,(xx,s*1.574,2.56),(.012,.026,1.65),'Steel')
  for x in (-8.7,-5,-1,2,5.6):
   box('Sill_lifting_lugs',body,(x,s*1.564,1.38),(.16,.085,.22),'Bogie_grey');rod('Sill_tie_downs',body,(x-.045,s*1.59,1.44),(x+.045,s*1.59,1.44),.013,'Steel',8)
  # Rear cyan arrow motif, separately authored in shallow layer.
  for offset in (0,1.12):
   pts=[(-8.75+offset,s*1.537,1.74),(-7.97+offset,s*1.537,1.74),(-6.93+offset,s*1.537,2.63),(-7.97+offset,s*1.537,3.70),(-8.75+offset,s*1.537,3.70),(-7.77+offset,s*1.537,2.63)]
   slab('Rear_chevrons',body,pts,.004,'Cyan_chevron',(0,s,0))
  rot=(PI/2,0,0) if s<0 else (PI/2,0,PI)
  text('Side_railway_lettering',body,'INDIAN RAILWAYS',(-.9,s*1.553,2.98),.32,'White_marking',rot)
  text('Side_number',body,'60027',(-.9,s*1.553,2.42),.245,'White_marking',rot)
  for x in (-4.8,1.95):text('Lifting_stencil',body,'LIFT',(x,s*1.568,1.44),.068,'White_marking',rot)
  text('Section_stencil',body,'SECTION '+section,(-8.2,s*1.551,1.80),.068,'White_marking',rot)
 # Roof shoulder facets and shallow removable panels.
 cross=[(y,crown_z(y)) for y in (-HALF,-1.40,-1.15,0,1.15,1.40,HALF)]
 for (y0,z0),(y1,z1) in zip(cross,cross[1:]):slab('Body_roof_facets',body,[(-9.02,y0,z0),(nose_x(z0,y0),y0,z0),(nose_x(z1,y1),y1,z1),(-9.02,y1,z1)],.055,'Roof_aluminium' if abs(y0)<1.41 and abs(y1)<1.41 else 'IR_blue')
 for x in (-7.8,-3.1,1.2,4.2):
  box('Roof_removable_panels',body,(x,0,3.947),(2.15,2.20,.025),'Roof_aluminium')
  for s in (-1,1):rod('Roof_panel_lift_eyes',body,(x-.4,s*.95,3.959),(x-.26,s*.95,3.959),.018,'Steel',10)
 # Cab front segmented around true windshield openings.
 ys=[-HALF,-1.24,-.10,.10,1.24,HALF];zs=[1.63,2.48,2.65,3.62,3.78,3.92]
 for ya,yb in zip(ys,ys[1:]):
  for za,zb in zip(zs,zs[1:]):
   if za==2.65 and (ya==-1.24 or ya==.10):continue
   pts=[(nose_x(front_z(z,y),y),y,front_z(z,y)) for y,z in [(ya,za),(yb,za),(yb,zb),(ya,zb)]]
   slab('Front_open_cab_shell',body,pts,.065,'Nose_dark' if za>=2.48 and za<3.78 else 'IR_blue',(1,0,0))
 for s in (-1,1):
  ya,yb=(.10,1.24) if s>0 else(-1.24,-.10)
  pts=[(nose_x(z,y)+.008,y,z) for y,z in [(ya+.02,2.67),(yb-.02,2.67),(yb-.02,3.60),(ya+.02,3.60)]]
  slab('Windscreen_clear_glass',body,pts,.008,'Clear_glass',(1,0,0))
  for y in (ya,yb):line('Windscreen_seals',body,[(nose_x(2.65,y)+.012,y,2.65),(nose_x(3.62,y)+.012,y,3.62)],.022,'Rubber')
  for z in (2.65,3.62):line('Windscreen_seals',body,[(nose_x(z,ya)+.012,ya,z),(nose_x(z,yb)+.012,yb,z)],.022,'Rubber')
  # Steel wildlife guard bars visible on actual cabs, 5mm radius.
  for j in range(14):
   y=ya+.034+(yb-ya-.068)*j/13;line('Windscreen_guard_bars',body,[(nose_x(2.62,y)+.09,y,2.62),(nose_x(3.67,y)+.09,y,3.67)],.006,'Steel',6)
  for z in (2.61,3.68):rod('Windscreen_guard_frame',body,(nose_x(z,ya)+.09,ya,z),(nose_x(z,yb)+.09,yb,z),.016,'Machinery_dark',10)
  y=.55*s;line('Windscreen_wipers',body,[(nose_x(2.51,y)+.05,y,2.51),(nose_x(2.98,y+.24*s)+.052,y+.24*s,2.98),(nose_x(3.18,y+.33*s)+.052,y+.33*s,3.18)],.012,'Rubber',8)
  # Clipped front corner, closing side/front envelope outside glazing.
  slab('Cab_corner_cheek',body,[(8.72,s*HALF,1.63),(nose_x(1.63,s*HALF),s*HALF,1.63),(nose_x(2.58,s*HALF),s*HALF,2.58),(8.72,s*HALF,2.58)],.06,'IR_blue',(0,s,0))
 # Close sloping outer A pillars around the windshield, leaving true side windows.
 for s in (-1,1):
  slab('Cab_upper_corner_pillar',body,[(8.54,s*HALF,2.58),(nose_x(2.58,s*HALF),s*HALF,2.58),(nose_x(3.78,s*HALF),s*HALF,3.78),(8.54,s*HALF,3.78)],.058,'Nose_dark',(0,s,0))
 # Rear end open central doorway and bellows collar.
 for s in (-1,1):box('Rear_end_wall',body,(-9.02,s*.99,2.69),(.10,1.06,2.18),'IR_blue')
 box('Rear_end_header',body,(-9.02,0,3.58),(.10,1.00,.42),'IR_blue');box('Rear_end_threshold',body,(-9.02,0,1.68),(.10,1.00,.12),'Bogie_grey')
 for x in [-9.08-j*.064 for j in range(8)]:
  for s in (-1,1):box('Gangway_bellows',body,(x,s*.54,2.56),(.048,.08,1.77),'Rubber')
  for z in (1.69,3.43):box('Gangway_bellows',body,(x,0,z),(.048,1.16,.08),'Rubber')
 box('Gangway_bridge_half',body,(-9.32,0,1.665),(.54,.99,.06),'Steel')
 for s in (-1,1):line('Intersection_hose_half',body,[(-9.07,s*.80,1.40),(-9.31,s*.83,1.10),(-9.60,s*.83,1.10)],.031,'Rubber')

def underframe_and_front():
 body=BODY
 for x,d in [(-1.9,(2.5,1.65,.59)),(1.0,(1.65,1.9,.66))]:rounded('Transformer_and_converter_cases',body,(x,0,.93),d,'Bogie_grey',.05)
 for s in (-1,1):
  for x in (-1.9,1.):
   rounded('Underframe_side_cabinets',body,(x,s*1.12,1.02),(1.28,.44,.61),'Roof_aluminium',.025)
   for xx in (x-.47,x+.47):box('Cabinet_corner_hardware',body,(xx,s*1.35,1.03),(.026,.025,.46),'Steel')
   text('Danger_stencil',body,'HV',(x,s*1.348,.99),.10,'Switch_black',(PI/2,0,0) if s<0 else(PI/2,0,PI))
  rod('Main_air_reservoir',body,(-3.4,s*.9,.84),(-2.6,s*.9,.84),.23,'Machinery_dark',24)
  line('Air_lines',body,[(-8.1,s*1.37,1.20),(-4,s*1.37,1.20),(0,s*1.37,1.20),(4.2,s*1.37,1.20),(8.8,s*1.37,1.20)],.021,'Copper')
  for x in (-8.15,8.0):rounded('Sandboxes',body,(x,s*1.01,1.10),(.66,.49,.49),'Bogie_grey',.04)
 # Robust central buffer beam and simplified CBC knuckle; face plane x9.60.
 box('Front_bufferbeam',body,(9.00,0,1.105),(.25,2.90,.48),'Machinery_dark')
 for s in (-1,1):
  rod('Buffer_stems',body,(9.11,s*.99,1.105),(9.51,s*.99,1.105),.11,'Steel',20)
  rod('Buffer_heads',body,(9.49,s*.99,1.105),(9.56,s*.99,1.105),.25,'Bogie_grey',48)
 box('CBC_shank',body,(9.30,0,1.105),(.60,.22,.26),'Steel')
 slab('CBC_knuckle',body,[(9.49,-.23,.95),(9.69,-.23,.95),(9.69,.02,.95),(9.62,.18,.95),(9.48,.24,.95),(9.45,.10,.95),(9.58,.05,.95),(9.58,-.10,.95),(9.49,-.10,.95)],.30,'Bogie_grey',(0,0,-1))
 rod('CBC_lock_pin',body,(9.53,.08,1.06),(9.53,.08,1.35),.035,'Steel',12)
 for s in (-1,1):
  line('Air_brake_hoses',body,[(9.14,s*.48,1.13),(9.23,s*.53,.73),(9.38,s*.75,.62),(9.53,s*.98,.82)],.034,'Rubber')
  rod('Air_cock',body,(9.17,s*.47,1.10),(9.27,s*.47,1.10),.049,'Safety_yellow',12)
  line('Front_step_rails',body,[(9.04,s*1.38,1.35),(9.16,s*1.38,1.63),(9.16,s*.68,1.63)],.019,'Steel')
 # U shaped blue obstacle deflector clear of CBC.
 slab('Front_blue_plough',body,[(9.11,-1.46,.22),(9.18,0,.20),(9.11,1.46,.22),(9.07,1.46,.94),(9.07,1.22,.94),(9.15,.78,.59),(9.20,0,.54),(9.15,-.78,.59),(9.07,-1.22,.94),(9.07,-1.46,.94)],.08,'IR_blue',(1,0,0))
 box('Internal_drawbar_half',body,(-9.35,0,1.105),(.50,.20,.24),'Steel')
 rod('Internal_drawbar_pin',body,(-9.12,0,.94),(-9.12,0,1.28),.055,'Bogie_grey',16)
 # Lamps: lower paired inset clusters and nose central twins.
 for s in (-1,1):
  x=nose_x(1.88,s*1.14)+.016;rounded('Lower_lamp_housing',body,(x,s*1.16,1.88),(.06,.45,.23),'Rubber',.04)
  for yy,ma in [(s*1.07,'Lamp_white'),(s*1.25,'Red')]:
   rod('Lower_light_lenses',body,(x+.03,yy,1.89),(x+.047,yy,1.89),.055,ma,24)
   e=empty(('HEADLIGHT_' if ma=='Lamp_white' else 'TAILLIGHT_')+('L' if s>0 else 'R'),body,(x+.06,yy,1.89));e['direction_local']='+X';e['runtime_mapping_required']=True
  rod('Nose_centre_lamps',body,(nose_x(2.27)+.008,s*.13,2.27),(nose_x(2.27)+.055,s*.13,2.27),.084,'Steel',32)
  rod('Nose_centre_lenses',body,(nose_x(2.27)+.055,s*.13,2.27),(nose_x(2.27)+.064,s*.13,2.27),.066,'Lamp_white',32)
  line('Front_grab_rails',body,[(nose_x(2.45,s*.22)+.027,s*.22,2.45),(nose_x(2.58,s*1.31)+.027,s*1.31,2.58)],.013,'Steel')
 text('Front_class',body,'WAG12B',(9.171,-.76,1.75),.14,'White_marking',(PI/2,0,PI/2))
 text('Front_number',body,'60027',(9.171,.77,1.75),.14,'White_marking',(PI/2,0,PI/2))
 # Flag is original plain geometry; no photograph decal.
 for z,ma in [(2.39,'Orange'),(2.31,'White_marking'),(2.23,'Green')]:box('Front_flag',body,(nose_x(z,-.91)+.018,-.91,z),(.010,.42,.078),ma)
 rod('Flag_chakra',body,(nose_x(2.31,-.91)+.025,-.91,2.31),(nose_x(2.31,-.91)+.031,-.91,2.31),.030,'Screen_blue',20)

def cab_interior(section):
 c=empty('CAB_INTERIOR',BODY);c['cab_facing_local']='+X'
 box('Cab_floor',c,(7.3,0,1.555),(2.98,2.85,.10),'Cab_floor')
 for i in range(32):box('Floor_antislip_ribs',c,(5.92+i*.086,0,1.608),(.018,2.74,.006),'Machinery_dark')
 box('Cab_ceiling',c,(7.30,0,3.75),(2.87,2.82,.07),'Interior_cream')
 for s in (-1,1):
  box('Cab_rear_bulkhead',c,(5.85,s*.96,2.67),(.10,1.04,2.10),'Interior_cream')
  box('Rear_door_jamb',c,(5.90,s*.425,2.46),(.09,.06,1.79),'Steel')
  rounded('Cab_rear_lockers',c,(6.05,s*1.14,2.05),(.27,.45,.85),'Interior_cream',.025)
 box('Cab_rear_door_header',c,(5.85,0,3.54),(.10,.89,.36),'Interior_cream')
 box('Cab_machine_door',c,(5.84,0,2.45),(.06,.78,1.76),'Desk_bluegrey')
 rod('Cab_machine_door_handle',c,(5.90,.25,2.45),(5.90,.25,2.64),.014,'Steel',10)
 # Broad metal desk with real leg space at pilot/assistant.
 rounded('Desk_top',c,(8.31,0,2.31),(.85,2.71,.13),'Desk_bluegrey',.065)
 for y in (-1.15,1.15):rounded('Desk_pedestals',c,(8.40,y,1.95),(.66,.35,.72),'Interior_cream',.045)
 rounded('Desk_center_pedestal',c,(8.48,0,1.98),(.49,.42,.77),'Interior_cream',.035)
 # Sloped instrument fascia, its local outward normal faces pilot -X.
 angle=math.radians(-17);rot=Matrix.Rotation(angle,3,'Y')
 box('Instrument_fascia',c,(8.53,0,2.53),(.055,2.60,.46),'Desk_bluegrey',rot)
 for y,w in [(-.53,.45),(.15,.35)]:
  box('Display_frames',c,(8.482,y,2.555),(.028,w,.28),'Switch_black',rot)
  box('Display_screens',c,(8.466,y,2.561),(.006,w-.055,.223),'Screen_teal' if y<0 else 'Screen_blue',rot)
  for k in range(5):box('Display_data_rows',c,(8.457,y,2.489+k*.032),(.006,w-.085,.006),'White_marking')
  for yy in [y-w/2+.018,y+w/2-.018]:
   for z in (2.48,2.53,2.58,2.63):box('Display_softkeys',c,(8.450,yy,z),(.014,.016,.016),'Interior_cream')
 # Analog brake gauges on pilot side, dials face rear.
 for y,z in [(-1.03,2.61),(-.85,2.46),(-1.08,2.40)]:
  rod('Analog_gauge_bezels',c,(8.462,y,z),(8.425,y,z),.074,'Steel',32)
  rod('Analog_gauge_faces',c,(8.424,y,z),(8.420,y,z),.062,'Switch_black',32)
  for k in range(10):
   a=math.radians(-135+k*30);rod('Gauge_tick_marks',c,(8.416,y+.048*math.cos(a),z+.048*math.sin(a)),(8.416,y+.056*math.cos(a),z+.056*math.sin(a)),.0025,'White_marking',6)
  rod('Gauge_needles',c,(8.41,y,z),(8.41,y-.029,z+.035),.003,'Red',6)
 # Toggles and colour pushbuttons, pilot throttle and brake handles.
 for y in [-.64,-.49,-.34,-.19]:
  rod('Rotary_switches',c,(8.28,y,2.37),(8.28,y,2.405),.025,'Switch_black',12)
  box('Rotary_levers',c,(8.28,y,2.417),(.06,.018,.023),'Switch_black')
 for i,(y,ma) in enumerate([(.28,'Red'),(.40,'Safety_yellow'),(.52,'Green'),(.64,'Red')]):
  rod('Pushbutton_collars',c,(8.44,y,2.44),(8.408,y,2.44),.026,'Steel',16)
  rod('Pushbuttons',c,(8.409,y,2.44),(8.397,y,2.44),.019,ma,16)
 for y in (-.90,-.33,.98):
  rounded('Control_lever_base',c,(8.13,y,2.395),(.22,.15,.035),'Switch_black',.02)
  rod('Control_lever_stems',c,(8.13,y,2.41),(8.08,y,2.59),.018,'Steel',12)
  rounded('Control_lever_grips',c,(8.07,y,2.61),(.08,.09,.075),'Switch_black',.024)
 text('Desk_label',c,'BRAKE    TRACTION',(7.988,-.62,2.397),.045,'White_marking',(0,0,-PI/2))
 # Two seats per outer cab, driver on right in local travel direction (-Y).
 for i,y in enumerate((-.69,.78),1):
  x=7.45;rounded('Crew_seat_cushions',c,(x,y,2.015),(.58,.53,.14),'Seat_cloth',.05)
  rounded('Crew_seat_backrests',c,(x-.26,y,2.41),(.14,.54,.71),'Seat_cloth',.05)
  rounded('Crew_headrests',c,(x-.24,y,2.83),(.15,.36,.19),'Seat_cloth',.05)
  rod('Seat_pedestals',c,(x,y,1.61),(x,y,1.94),.095,'Steel',20)
  rounded('Seat_base',c,(x,y,1.65),(.46,.47,.07),'Machinery_dark',.035)
  for s in (-1,1):
   rod('Seat_arm_posts',c,(x-.12,y+s*.31,2.08),(x-.12,y+s*.31,2.33),.017,'Steel',10)
   rounded('Seat_armrests',c,(x-.01,y+s*.31,2.35),(.43,.067,.07),'Switch_black',.023)
  e=empty('DRIVER_'+f'{i:03d}',c,(x,y,2.085-.483));e['cushion_top_z_m']=2.085;e['posed_hip_offset_assumed_m']=.483;e['facing_local_axis']='+X';e['role']='loco pilot' if i==1 else 'assistant loco pilot';e['needs_game_character_fit']=True
  for yy in (y-.09,y+.09):box('Driver_pedals',c,(8.00,yy,1.695),(.23,.14,.055),'Steel',Matrix.Rotation(-.30,3,'Y'))
 empty('CAB_EYE_CAMERA_REFERENCE',c,(7.49,-.69,2.94))['purpose']='authoring viewpoint, not runtime seat/camera metadata'
 # Sun blinds and interior windscreen central pillar.
 for y in (-.68,.68):rounded('Sunblind_rolls',c,(8.60,y,3.64),(.075,1.08,.08),'Switch_black',.02)
 box('Cab_central_window_pillar',c,(8.84,0,3.12),(.12,.13,1.0),'Interior_cream')
 for z in (2.99,3.07,3.43,3.51):box('Cab_pillar_vents',c,(8.765,0,z),(.01,.095,.011),'Switch_black')
 text('Section_cab_label',c,'SECTION '+section,(8.743,0,3.40),.041,'Switch_black',(PI/2,0,-PI/2))
 # Side fans and ceiling light details.
 for y in (-1.19,1.19):
  rod('Cab_fan_mounts',c,(8.15,y,3.05),(8.15,y,3.18),.022,'Steel',10)
  rod('Cab_fan_rings',c,(8.20,y,3.27),(8.16,y,3.27),.14,'Machinery_dark',32)
  for k in range(12):
   a=k*math.tau/12;rod('Cab_fan_guards',c,(8.15,y,3.27),(8.15,y+.13*math.cos(a),3.27+.13*math.sin(a)),.0035,'Steel',6)
  rod('Cab_fan_hub',c,(8.13,y,3.27),(8.16,y,3.27),.032,'Steel',16)
 box('Cab_ceiling_lamp',c,(6.87,0,3.702),(.55,.24,.025),'Lamp_white')
 for y in (-.81,.81):
  box('HVAC_cab_vent_frame',c,(7.28,y,3.699),(.34,.22,.027),'Desk_bluegrey')
  for j in range(5):box('HVAC_cab_vent_slats',c,(7.16+j*.052,y,3.676),(.017,.20,.016),'Switch_black')
 # Small fire extinguisher is static visual, no functions.
 rod('Cab_extinguisher',c,(6.17,.68,1.72),(6.17,.68,2.17),.082,'Red',20)
 box('Extinguisher_label',c,(6.262,.68,1.97),(.01,.10,.19),'White_marking')
 line('Extinguisher_hose',c,[(6.17,.68,2.21),(6.29,.68,2.21),(6.28,.68,1.83)],.013,'Rubber')

def roof_equipment():
 body=BODY
 rounded('Cab_HVAC',body,(7.05,0,4.047),(1.69,1.72,.25),'Roof_aluminium',.04)
 for s in (-1,1):
  for j in range(12):box('HVAC_vertical_slats',body,(6.4+j*.115,s*.869,4.045),(.038,.014,.17),'Bogie_grey')
 for y in (-.47,.47):
  rod('HVAC_fan_discs',body,(7.10,y,4.177),(7.10,y,4.186),.29,'Machinery_dark',32)
  for k in range(-4,5):box('HVAC_fan_guards',body,(7.10+k*.06,y,4.190),(.012,.50,.01),'Steel')
 for y in (-.37,.37):
  rod('Roof_horn_necks',body,(8.02,y,3.94),(8.26,y,4.08),.04,'Steel',16)
  rod('Roof_horn_bells',body,(8.21,y,4.07),(8.48,y,4.14),.078 if y<0 else .065,'Machinery_dark',24)
 rod('Radio_aerial',body,(5.9,.55,3.96),(5.9,.55,4.22),.006,'Steel',8)
 rounded('Roof_aux_cooling_box',body,(.1,0,4.001),(1.44,1.45,.12),'Roof_aluminium',.04)
 for y in (-.38,.38):
  rod('Aux_fan_disc',body,(.1,y,4.064),(.1,y,4.075),.27,'Bogie_grey',32)
  for k in range(-3,4):box('Aux_fan_grille',body,(.1+k*.07,y,4.08),(.013,.43,.008),'Steel')
 # Roof HV chain behind pantograph folding envelope.
 for x in (-8.30,-7.90,-2.85):
  for z in [3.96+i*.044 for i in range(5)]:rod('HV_insulator_sheds',body,(x,.45,z),(x,.45,z+.026),.10,'Insulator',20)
  rod('HV_insulator_core',body,(x,.45,3.95),(x,.45,4.21),.037,'Insulator',16)
 line('Copper_roof_bus',body,[(-8.30,.45,4.21),(-7.90,.45,4.21),(-7.5,.45,4.18),(-7.5,1.02,4.03),(-2.85,1.02,4.03),(-2.85,.45,4.21)],.016,'Copper')
 rounded('Vacuum_circuit_breaker',body,(-8.2,-.30,4.05),(.48,.60,.15),'Machinery_dark',.03)
 for y in (-.45,-.15):rod('VCB_terminal',body,(-8.2,y,4.10),(-8.2,y,4.24),.045,'Steel',12)
 for x in (-7.5,-2.1,2.5,4.5):
  for s in (-1,1):rod('Roof_lifting_eyes',body,(x,s*1.24,3.91),(x+.16,s*1.24,3.91),.013,'Steel',8)

def pantograph():
 base=empty('PANTO_BASE',BODY,(-4.7,0,0));ctrl=empty('PANTO_CTRL',base,(0,0,0));ctrl['extension']=0.;ctrl.id_properties_ui('extension').update(min=0,max=1);ctrl['normal_wire_extension']=NORMAL;ctrl['strip_top_min_m']=4.245;ctrl['strip_top_max_m']=7.52;ctrl['approximate_high_reach_visual_rig']=True
 for x in (-.40,.45):
  for y in (-.46,.46):
   for z in [3.96+i*.031 for i in range(5)]:rod('Panto_base_insulators',base,(x,y,z),(x,y,z+.020),.080,'Insulator',16)
   rod('Panto_base_insulator_core',base,(x,y,3.94),(x,y,4.115),.032,'Insulator',12)
 for y in (-.47,.47):box('Panto_baseframe',base,(0,y,4.116),(1.10,.065,.046),'Steel')
 box('Panto_base_crossframe',base,(0,0,4.116),(.075,1.03,.046),'Steel')
 lower=empty('PANTO_LOWER_PIVOT',ctrl,(0,0,PANTO_BASE));elbow=empty('PANTO_ELBOW_PIVOT',lower,(-L1,0,0));head=empty('PANTO_HEAD_LEVEL_PIVOT',elbow,(L2,0,0))
 for o,mul in [(lower,1),(elbow,-2),(head,1)]:
  f=o.driver_add('rotation_euler',1);d=f.driver;d.type='SCRIPTED';v=d.variables.new();v.name='e';v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path='["extension"]';d.expression=f'{mul}*({A0}+({A1-A0})*min(1,max(0,e)))'
  o['rotation_axis']='Y';o['rigid_joint']=True
 for y in (-.32,.32):
  rod('Panto_lower_arms',lower,(0,y,0),(-L1,y,0),.040,'Steel',12)
  rod('Panto_upper_arms',elbow,(0,y,0),(L2,y,0),.027,'Steel',12)
  rod('Panto_lower_braces',lower,(-.20,y,0),(-L1+.20,-y,0),.016,'Bogie_grey',8)
 for x in (-.12,-L1+.12):rod('Panto_lower_crossbars',lower,(x,-.38,0),(x,.38,0),.032,'Steel',12)
 for pa in (lower,elbow,head):rod('Panto_joint_shafts',pa,(0,-.42,0),(0,.42,0),.023 if pa==head else .052,'Bogie_grey',20)
 for y in (-.26,.26):rod('Panto_head_supports',head,(-.22,y,-.004),(.22,y,-.004),.025,'Steel',12)
 for x in (-.14,.14):
  box('Panto_contact_strips',head,(x,0,.020),(.056,1.72,.024),'Machinery_dark')
  for s in (-1,1):line('Panto_head_horns',head,[(x,s*.86,.020),(x,s*.95,-.025),(x,s*1.015,-.14)],.013,'Steel',10)
 rod('Panto_air_actuator',base,(.04,-.67,4.015),(.70,-.67,4.015),.075,'Bogie_grey',16)
 for i in range(10):rod('Panto_base_spring',base,(-.65+i*.061,.67,4.031),(-.618+i*.061,.67,4.031),.062,'Steel',12)
 return ctrl,[lower,elbow,head]

def fresh_scene(section):
 global COL,ROOT,BODY,M,BATCH
 bpy.ops.wm.read_factory_settings(use_empty=True);M={};BATCH={};COL=bpy.data.collections.new('WAG12B_SECTION_'+section);bpy.context.scene.collection.children.link(COL)
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.;sc.render.fps=24;sc.frame_start=1;sc.frame_end=81
 materials();ROOT=empty('WAG12B_'+section+'_ROOT');ROOT['asset_type']='WAG12B independently convertible locomotive section';ROOT['section']=section;ROOT['coupling_span_m']=SPAN;ROOT['rail_top_z_m']=0.;ROOT['axis_convention']='+X forward, Y lateral, Z up';ROOT['source_commit']='7de48a11bd95a69e03acb16043629b40a89f35ec'
 BODY=empty('BODY',ROOT)
 for n,x in [('FRONT',9.6),('REAR',-9.6)]:
  e=empty('COUPLING_'+n,ROOT,(x,0,1.105));e.rotation_euler.z=0 if x>0 else PI;e['outward_axis']='+X';e['kind']='outer CBC mating plane' if x>0 else 'internal drawbar mating plane';e['not_mesh_extremity']=True
 bogies();body_shell(section);underframe_and_front();cab_interior(section);roof_equipment();ctrl,piv=pantograph();flush();bpy.context.view_layer.update()
 return ctrl,piv

def asset_select():
 bpy.ops.object.select_all(action='DESELECT')
 for o in COL.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=ROOT

def export(path,bake=False):
 # FBX has no portable Principled Transmission; provide explicit alpha fallback only for export.
 glass=M['Clear_glass'];bsdf=glass.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Alpha'].default_value=.18;glass.diffuse_color=(*glass.diffuse_color[:3],.18)
 asset_select();bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='X',axis_up='Z',apply_unit_scale=True,use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=bake,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,path_mode='AUTO',use_custom_props=True)
 bsdf.inputs['Alpha'].default_value=1.;glass.diffuse_color=(*glass.diffuse_color[:3],1.)

def measure():
 dg=bpy.context.evaluated_depsgraph_get();mins=[1e9]*3;maxs=[-1e9]*3;tri=0;vertices=0;meshes=0
 for o in COL.objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);vertices+=len(me.vertices);meshes+=1
  for v in me.vertices:
   w=o.matrix_world@v.co
   for k in range(3):mins[k]=min(mins[k],w[k]);maxs[k]=max(maxs[k],w[k])
  ev.to_mesh_clear()
 return {'bounds_min_m':mins,'bounds_max_m':maxs,'visible_dimensions_m':[b-a for a,b in zip(mins,maxs)],'triangles':tri,'vertices':vertices,'meshes':meshes,'material_count':len(M),'root_identity':all(abs(ROOT.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))}

def build(section):
 ctrl,piv=fresh_scene(section);key='WAG12B_'+section;path=P/'sections';low=measure();low['anchors']={n:list(bpy.data.objects[n].matrix_world.translation) for n in ('COUPLING_FRONT','COUPLING_REAR')};low['bogies']=2;low['axles']=4;low['crew_markers']=2;low['cab_count']=1;low['pantograph_count']=1
 bpy.ops.wm.save_as_mainfile(filepath=str(path/(key+'.blend')));export(path/(key+'_lowered.fbx'))
 ctrl['extension']=NORMAL;ctrl.update_tag();bpy.context.view_layer.update();export(path/(key+'_standard_raised.fbx'))
 ctrl['extension']=1.;ctrl.update_tag();bpy.context.view_layer.update();export(path/(key+'_highreach.fbx'));high=measure()
 # Bake actual evaluated local transforms, then remove live drivers for portable rigid FBX tracks.
 samples={o:[] for o in piv}
 for frame in range(1,82):
  ext=(frame-1)/40 if frame<=41 else (81-frame)/40;ctrl['extension']=ext;ctrl.update_tag();bpy.context.view_layer.update()
  for o in piv:samples[o].append(tuple(o.rotation_euler))
 for o in piv:
  o.driver_remove('rotation_euler',1)
  for frame,rot in enumerate(samples[o],1):o.rotation_euler=rot;o.keyframe_insert(data_path='rotation_euler',frame=frame,group='Rigid highreach samples')
  o.animation_data.action.name=o.name+'_HIGHREACH_MOTION'
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(path/(key+'_baked_motion.blend')));export(path/(key+'_motion.fbx'),True)
 report={'section':section,'lowered':low,'highreach':high,'pantograph':{'base_joint_z_m':PANTO_BASE,'arm_lengths_m':[L1,L2],'theta_min_rad':A0,'theta_max_rad':A1,'contact_top_min_m':4.245,'contact_top_max_m':7.52,'standard_contact_top_m':5.917,'standard_extension':NORMAL,'formula':'4.136 + 4.4*sin(theta) + 0.032','motion_frames':[1,41,81],'fps':24}}
 (P/'qa'/(key+'_geometry.json')).write_text(json.dumps(report,indent=2));print('WAG12_COMPLETE',json.dumps(report))

if __name__=='__main__':
 for section in ('A','B'):build(section)
