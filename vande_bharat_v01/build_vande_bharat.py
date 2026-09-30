"""Original compact Vande Bharat 2.0 modelling handoff. Blender 4.3.2.
blender -b -t 2 --python build_vande_bharat.py -- [output_directory]
No game conversion; no external meshes or photographic textures.
"""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path(__file__).resolve().parent
for d in ['cars','assemblies','qa','renders']: (P/d).mkdir(parents=True,exist_ok=True)
PITCH=19.375; HALF=PITCH/2; BODYEND=9.33; BOGIE=5.85; WBASE=2.7
M={}; batches={}; COL=None; ROOT=None

def mat(n,c,metal=0,rough=.4,glass=False,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if glass:p.inputs['Transmission Weight'].default_value=.96;p.inputs['IOR'].default_value=1.45
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 M[n]=m;return m

def materials():
 for n,c,me,r in [('Pearl_white',(.78,.83,.88),.22,.27),('Cobalt_blue',(.017,.047,.24),.32,.24),('Roof_silver',(.32,.38,.42),.55,.4),('Graphite',(.028,.037,.048),.2,.52),('Rubber',(.009,.014,.018),0,.69),('Steel',(.46,.54,.6),.85,.23),('Interior_ivory',(.7,.71,.67),0,.48),('Floor',(.21,.23,.25),0,.7),('Seat_CC',(.08,.18,.30),0,.8),('Seat_EC',(.055,.066,.085),0,.83),('Headrest',(.26,.50,.65),0,.75),('Panto_red',(.58,.032,.017),.4,.3),('Insulator',(.17,.09,.047),.1,.35),('Display_black',(.004,.009,.014),0,.29),('Amber',(.9,.35,.015),0,.4),('Green',(.06,.54,.17),0,.4),('Red',(.67,.013,.016),0,.3),('Orange',(.94,.22,.012),0,.4)]:mat(n,c,me,r)
 mat('Clear_glass',(.78,.90,.95),rough=.09,glass=True);mat('Headlamp',(.78,.91,1),rough=.2,emit=2);mat('LED_warm',(.88,.91,.83),rough=.4,emit=1.5);mat('Screen',(.09,.38,.47),rough=.35,emit=.5)

def empty(n,parent=None,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);COL.objects.link(o);o.parent=parent;o.location=loc;o.empty_display_size=.1;o.empty_display_type='ARROWS';return o

def add(n,par,verts,faces,ma):
 key=(n,par.name,ma)
 if key not in batches:batches[key]=[[],[]]
 v,f=batches[key];off=len(v);v.extend(verts);f.extend([tuple(i+off for i in face) for face in faces])

def flush():
 for (n,pa,ma),(v,f) in batches.items():
  me=bpy.data.meshes.new(n+'_mesh');me.from_pydata(v,[],f);me.materials.append(M[ma]);me.update();o=bpy.data.objects.new(n,me);COL.objects.link(o);o.parent=bpy.data.objects[pa]
  if n.startswith(('Sculpted_nose','Nose_side','Cab_side','Cab_inner','Nose_windscreen','Curved_roof','Curved_ceiling')):
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(me);bm.free()
   for poly in me.polygons:poly.use_smooth=True
  if n in ['Window_clear_glazing','Door_glass','Saloon_door_glass','Nose_windscreen','Cab_side_glass']:
   # Closed 6mm panes avoid single-backface total internal reflection from the cabin.
   bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Closed_glazing_thickness','SOLIDIFY');mod.thickness=.006;mod.offset=-1;mod.use_even_offset=True;mod.use_quality_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 batches.clear()

def box(n,pa,c,d,ma,rot=None):
 v=[Vector((x*d[0]/2,y*d[1]/2,z*d[2]/2)) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 if rot:v=[rot@p for p in v]
 v=[tuple(p+Vector(c)) for p in v];add(n,pa,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],ma)

def rod(n,pa,a,b,r,ma,seg=12):
 a,b=Vector(a),Vector(b);w=(b-a).normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.1:u=w.cross(Vector((0,1,0)))
 u.normalize();v=w.cross(u);vv=[]
 for c in [a,b]:
  for i in range(seg):vv.append(tuple(c+r*(u*math.cos(i*math.tau/seg)+v*math.sin(i*math.tau/seg))))
 ff=[tuple(range(seg-1,-1,-1)),tuple(range(seg,2*seg))]+[(i,(i+1)%seg,seg+(i+1)%seg,seg+i) for i in range(seg)];add(n,pa,vv,ff,ma)

def line(n,pa,pts,r,ma,seg=8):
 for a,b in zip(pts,pts[1:]):rod(n,pa,a,b,r,ma,seg)

def panel(n,pa,pts,ma):
 # Exterior side surfaces have outward winding; glazing remains separate double-sided material.
 if n in ['Window_clear_glazing','Door_glass','Cab_side_glass','Nose_side_cheeks'] and sum(v[1] for v in pts)>0:pts=list(reversed(pts))
 add(n,pa,pts,[tuple(range(len(pts)))],ma)

def rounded(n,pa,c,d,ma,r=.05):
 # Low-poly bevelled cuboid, 3 ring layers, 24 outline vertices. Rounded XY then rotate as needed at seat assembly.
 x,y,z=c;dx,dy,dz=d;r=min(r,dx*.25,dy*.25,dz*.4);vs=[]
 for zz,rr in [(-dz/2,r*.55),(-dz/2+r,r),(dz/2-r,r),(dz/2,r*.55)]:
  for xx,yy,base in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
   for j in range(4):
    an=math.radians(base+j*30);vs.append((x+xx*(dx/2-r)+rr*math.cos(an),y+yy*(dy/2-r)+rr*math.sin(an),z+zz))
 fs=[tuple(range(15,-1,-1)),tuple(range(48,64))]
 for k in range(3):
  for j in range(16):fs.append((16*k+j,16*k+(j+1)%16,16*(k+1)+(j+1)%16,16*(k+1)+j))
 add(n,pa,vs,fs,ma)

def text(n,pa,txt,loc,size,ma,rot):
 cu=bpy.data.curves.new(n,'FONT');cu.body=txt;cu.align_x='CENTER';cu.size=size;cu.extrude=.0003;cu.resolution_u=4;o=bpy.data.objects.new(n,cu);COL.objects.link(o);o.parent=pa;o.location=loc;o.rotation_euler=rot;cu.materials.append(M[ma]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)

def ring(n,pa,x,width,bottom,top,ma,thick=.045):
 # Hollow gangway frame, never an opaque plate across passage.
 box(n,pa,(x,0,top),(thick,width,.08),ma);box(n,pa,(x,0,bottom),(thick,width,.07),ma)
 for s in [-1,1]:box(n,pa,(x,s*width/2,(top+bottom)/2),(thick,.065,top-bottom),ma)

def bogies(body,powered):
 for label,x in [('A',BOGIE),('B',-BOGIE)]:
  b=empty('BOGIE_'+label+'_YAW_Z',ROOT,(x,0,.71));b['pivot_axis']='Z';b['compact_center_offset_m']=x
  for s in [-1,1]:
   rounded('Bogie_'+label+'_frame',b,(0,s*1.07,0),(3.55,.17,.35),'Graphite',.04)
   for xx in [-.75,.75]:
    rod('Air_spring_'+label,b,(xx,s*.78,.05),(xx,s*.78,.33),.23,'Rubber',16)
    rod('Damper_'+label,b,(xx,s*1.17,-.03),(xx+.3,s*1.17,.36),.035,'Steel',10)
  for xx in [-.72,.72]:box('Bogie_crossmember_'+label,b,(xx,0,0),(.19,2.12,.23),'Graphite')
  for j,xx in enumerate([-WBASE/2,WBASE/2]):
   a=empty(f'AXLE_{label}_{j+1}_ROLL_Y',b,(xx,0,.476-.71));a['pivot_axis']='Y';a['wheel_diameter_m']=.952
   rod('Axle_shafts_'+label+str(j),a,(0,-1.22,0),(0,1.22,0),.095,'Steel',16)
   for s in [-1,1]:
    # Rolling circle at track gauge; flanges inside rail gauge.
    rod('Wheel_tread_'+label+str(j),a,(0,s*.838-.067,0),(0,s*.838+.067,0),.476,'Steel',40)
    rod('Wheel_web_'+label+str(j),a,(0,s*.91,0),(0,s*1.00,0),.375,'Graphite',32)
    rod('Wheel_flange_'+label+str(j),a,(0,s*.759,0),(0,s*.782,0),.504,'Steel',40)
    rod('Wheel_hub_'+label+str(j),a,(0,s*.94,0),(0,s*1.13,0),.145,'Steel',20)
    # Non-rotating axlebox and primary coil approximation under bogie, not axle.
    rounded('Axleboxes_'+label,b,(xx,s*1.16,-.15),(.30,.26,.27),'Graphite',.03)
    for dx in [-.2,.2]:
     for iz in range(5):rod('Primary_springs_'+label,b,(xx+dx,s*1.07,-.02+iz*.039),(xx+dx,s*1.07,.003+iz*.039),.10,'Steel',12)
   if powered:
    rod('Traction_motors_'+label,b,(xx+.25,-.5,-.12),(xx+.25,.5,-.12),.23,'Graphite',16)
    box('Gearboxes_'+label,b,(xx,.54,-.13),(.45,.25,.44),'Graphite')

def roof(body,x0,x1):
 # Curved shoulder and crown strips; double skin only, no opaque window-backing shell.
 cross=[(-1.62,3.13),(-1.59,3.36),(-1.46,3.58),(-1.23,3.73),(-.82,3.8),(0,3.82),(.82,3.8),(1.23,3.73),(1.46,3.58),(1.59,3.36),(1.62,3.13)]
 for i,(a,b) in enumerate(zip(cross,cross[1:])):
  ma='Cobalt_blue' if i in [0,9] else 'Pearl_white'
  panel('Curved_roof_outer',body,[(x0,*a),(x1,*a),(x1,*b),(x0,*b)],ma)
  panel('Curved_ceiling_inner',body,[(x0,a[0]*.955,a[1]-.095),(x1,a[0]*.955,a[1]-.095),(x1,b[0]*.955,b[1]-.095),(x0,b[0]*.955,b[1]-.095)],'Interior_ivory')
 for x in [-5.05,5.05]:
  if x>x1-1.3:x=x1-1.3
  rounded('HVAC_packages',body,(x,0,3.93),(2.6,1.85,.42),'Roof_silver',.07)
  for y in [-.5,.5]:
   rod('HVAC_fan_grilles',body,(x,y,4.137),(x,y,4.141),.31,'Graphite',24)
   for k in range(-3,4):box('HVAC_louvres',body,(x+.05*k,y,4.145),(.012,.49,.008),'Roof_silver')
  for j in range(9):box('HVAC_end_grille',body,(x-1.307,0,3.82+j*.025),(.015,1.55,.012),'Graphite')

def windows_sides(body,dtc):
 front=5.65 if dtc else BODYEND;doors=[-7.70,4.65] if dtc else [-7.70,7.70]
 windows=[(-5.55,1.95),(-3.25,1.95),(-.95,1.95),(1.35,1.95)] if dtc else [(x,1.99) for x in [-5.75,-3.45,-1.15,1.15,3.45,5.75]]
 for s in [-1,1]:
  # All wall pieces are segmented explicitly around doors and glazed holes.
  holes=[(x-w/2,x+w/2,1.91,3.05,'window') for x,w in windows]+[(x-.48,x+.48,1.23,3.14,'door') for x in doors]
  edges=sorted(set([-BODYEND,front]+[a for h in holes for a in h[:2]]));zs=[1.20,1.23,1.91,3.05,3.14]
  for a,b in zip(edges,edges[1:]):
   if a<-BODYEND or b>front:continue
   for za,zb in zip(zs,zs[1:]):
    xm=(a+b)/2;zm=(za+zb)/2
    if any(h[0]<xm<h[1] and h[2]<zm<h[3] for h in holes):continue
    ma='Pearl_white'
    box('Open_sidewall',body,(xm,s*1.572,(za+zb)/2),(b-a,.096,zb-za),ma)
  # low blue belt: segmented around door apertures
  for a,b in zip(edges,edges[1:]):
   if a<-BODYEND or b>front or any(h[4]=='door' and h[0]<(a+b)/2<h[1] for h in holes):continue
   box('Lower_blue_belt',body,((a+b)/2,s*1.623,1.51),(b-a,.008,.07),'Cobalt_blue')
  for k,(x,w) in enumerate(windows):
   y=s*1.605
   for z in [1.898,3.062]:box('Window_seals',body,(x,y,z),(w+.035,.055,.028),'Rubber')
   for xx in [x-w/2,x+w/2]:box('Window_seals',body,(xx,y,2.48),(.03,.055,1.16),'Rubber')
   panel('Window_clear_glazing',body,[(x-w/2+.015,s*1.614,1.92),(x+w/2-.015,s*1.614,1.92),(x+w/2-.015,s*1.614,3.044),(x-w/2+.015,s*1.614,3.044)],'Clear_glass')
   for z in [1.89,3.08]:box('Window_inner_trim',body,(x,s*1.506,z),(w+.07,.035,.055),'Interior_ivory')
   box('Window_roller_blinds',body,(x,s*1.503,3.018),(w,.035,.11),'Floor')
  for j,x in enumerate(doors):
   e=empty(f'DOOR_{"L" if s>0 else "R"}_{j+1}_SLIDE',body,(x,s*1.58,1.23));e['open_translation_local_m']=[1.00,s*.09,0];e['type']='single plug sliding door; suggested outward then longitudinal motion';e['closed_location_m']=list(e.location)
   # Door is a frame around a true narrow glazed opening.
   for xx in [-.375,.375]:box('Door_leaf',e,(xx,0,.95),(.20,.075,1.90),'Pearl_white')
   for z,h in [(.28,.56),(1.74,.32)]:box('Door_leaf',e,(0,0,z),(.95,.075,h),'Pearl_white')
   box('Door_blue_footer',e,(0,s*.041,.27),(.95,.01,.1),'Cobalt_blue')
   panel('Door_glass',e,[(-.27,s*.044,.56),(.27,s*.044,.56),(.27,s*.044,1.58),(-.27,s*.044,1.58)],'Clear_glass')
   for xx in [-.285,.285]:box('Door_seals',e,(xx,s*.043,1.07),(.028,.023,1.05),'Rubber')
   for z in [.55,1.59]:box('Door_seals',e,(0,s*.043,z),(.59,.023,.028),'Rubber')
   rod('Door_handles',e,(.39,s*.09,.8),(.39,s*.09,1.16),.016,'Steel',10)
   box('Door_threshold',body,(x,s*1.62,1.20),(1.07,.22,.05),'Steel')
   rod('Door_open_button',body,(x+.62,s*1.623,2.10),(x+.62,s*1.638,2.10),.042,'Green',12)
   box('Flag_orange',body,(x+.67,s*1.624,2.87),(.28,.004,.04),'Orange');box('Flag_white',body,(x+.67,s*1.624,2.82),(.28,.004,.04),'Pearl_white');box('Flag_green',body,(x+.67,s*1.624,2.77),(.28,.004,.04),'Green')
  # Side signs readable on both sides.
  rot=(math.pi/2,0,0) if s<0 else (math.pi/2,0,math.pi)
  text('Side_identity',body,'VANDE BHARAT',(0,s*1.63,1.68),.14,'Cobalt_blue',rot)
  text('Side_railway',body,'INDIAN RAILWAYS',(0,s*1.63,3.23),.09,'Pearl_white',rot)
  box('Destination_display',body,(-7.0,s*1.626,3.24),(.62,.025,.15),'Display_black')

def seat_geometry(body,x,y,ec,idx,facing=1,driver=False):
 # Seat built in one orientation, reflected through local Z for reverse rows.
 anchor=empty(('DRIVER_' if driver else 'PAX_')+f'{idx:03d}',body,(x,y,1.31+.44-.483));anchor.rotation_euler.z=0 if facing>0 else math.pi;anchor['facing_local_axis']='+X';anchor['cushion_top_z_m']=1.75;anchor['posed_hip_offset_assumed_m']=.483
 # Small batches use transformed temporary coordinates, retaining static BODY grouping.
 nm='Driver_seats' if driver else ('EC_seating' if ec else 'CC_seating');ma='Graphite' if driver else ('Seat_EC' if ec else 'Seat_CC');w=.54 if ec or driver else .44
 before={k:len(v[0]) for k,v in batches.items()}
 rounded(nm,body,(.02,0,1.69),(.48,w,.12),ma,.05)
 rounded(nm,body,(-.205,0,2.07),(.14,w,.72),ma,.065)
 rounded(nm,body,(-.185,0,2.47),(.15,w*.82,.23),ma,.07)
 if not driver:rounded('Seat_headrest_covers',body,(-.1,0,2.45),(.024,w*.60,.25),'Headrest',.01)
 for s in ([-1,1] if driver or y in ([1.09,-.49] if ec else [1.14,-.26]) else [-1]):
  s=s*facing
  rounded('Seat_armrests',body,(.01,s*(w/2+.02),1.91),(.49,.034,.065),'Graphite',.015)
  rod('Seat_armrest_posts',body,(-.08,s*(w/2+.02),1.73),(-.08,s*(w/2+.02),1.90),.018,'Steel',8)
 rod('Seat_pedestals',body,(-.02,0,1.34),(-.02,0,1.63),.073,'Graphite',12)
 box('Seat_mounts',body,(-.02,0,1.335),(.30,w*.73,.035),'Steel')
 if not driver:
  box('Seat_back_trays',body,(-.29,0,1.99),(.025,w*.71,.30),'Interior_ivory')
  box('Seat_back_pockets',body,(-.298,0,1.75),(.03,w*.66,.13),'Graphite')
 for key,(vs,fs) in batches.items():
  start=before.get(key,0)
  for i in range(start,len(vs)):
   p=vs[i];vs[i]=(x+facing*p[0],y+facing*p[1],p[2])
 return anchor

def interior(body,dtc,ec,hand):
 end=5.65 if dtc else BODYEND
 box('Saloon_floor',body,((-BODYEND+end)/2,0,1.25),(end+BODYEND,3.09,.12),'Floor')
 count=8 if dtc else (10 if ec else 12);pitch=.93 if not ec else 1.09;start=-5.30 if dtc else -(count-1)*pitch/2
 ys=[-1.09,-.49,.49,1.09] if ec else [-1.22,-.74,-.26,.65,1.14]
 idx=1
 for j in range(count):
  x=start+j*pitch
  for y in ys:seat_geometry(body,x,y,ec,idx,1 if j<count/2 else -1);idx+=1
 xmin=-6.6;xmax=3.35 if dtc else 6.6
 for s in [-1,1]:
  # Racks are slender open supports with glazed shelf, mounted outside passenger headspace.
  box('Luggage_rack_edge',body,((xmin+xmax)/2,s*1.01,3.18),(xmax-xmin,.035,.055),'Steel')
  box('Luggage_rack_shelf',body,((xmin+xmax)/2,s*1.28,3.145),(xmax-xmin,.49,.018),'Clear_glass')
  for x in range(-6,4 if dtc else 7,2):line('Rack_brackets',body,[(x,s*1.49,2.98),(x,s*1.49,3.16),(x,s*1.00,3.16)],.014,'Steel')
  box('Ceiling_LED',body,((xmin+xmax)/2,s*.79,3.59),(xmax-xmin,.055,.018),'LED_warm')
  for x in range(-6,4 if dtc else 7):
   rod('Reading_lights',body,(x,s*1.09,3.43),(x,s*1.09,3.445),.027,'LED_warm',10)
   for k in range(3):box('HVAC_interior_vents',body,(x+.06*k,s*1.23,3.47),(.023,.16,.007),'Graphite')
 for x in [xmin,xmax]:
  # Saloon bulkhead open centre passage with separately framed sliding glass.
  for s in [-1,1]:box('Saloon_bulkheads',body,(x,s*.98,2.35),(.055,1.08,2.14),'Interior_ivory')
  box('Bulkhead_lintel',body,(x,0,3.40),(.09,1.2,.20),'Interior_ivory')
  ring('Sliding_saloon_frame',body,x,.92,1.31,3.24,'Steel',.035)
  panel('Saloon_door_glass',body,[(x, -.43,1.34),(x,.43,1.34),(x,.43,3.21),(x,-.43,3.21)],'Clear_glass')
  box('Info_screen_frame',body,(x+(.04 if x<0 else-.04),0,3.43),(.04,.65,.23),'Display_black')
  box('Info_screen',body,(x+(.065 if x<0 else-.065),0,3.43),(.006,.59,.18),'Screen')
 # Vestibule/service volumes preserve longitudinal through passage of .9m.
 for x in [-8.85] if dtc else[-8.85,8.85]:
  for s in [-1,1]:
   rounded('Service_cabin',body,(x,s*1.03,2.27),(.82,.93,1.91),'Interior_ivory',.06)
   box('Service_door_handle',body,(x,s*.558,2.21),(.16,.03,.03),'Steel')
 # Pantry hand differs in NDTC_EC2; positioned ahead of passenger seats without blocking aisle.
 px=3.87 if dtc else 7.04;py=hand*1.1
 box('Pantry_counter',body,(px,py,1.77),(.65,.67,.90),'Interior_ivory');box('Pantry_worktop',body,(px,py,2.24),(.71,.72,.04),'Steel')
 for z in [1.5,1.83,2.08]:box('Pantry_drawer_front',body,(px,py-hand*.342,z),(.53,.018,.20),'Floor')
 return idx-1

def underframe(body,kind):
 box('Underframe_spine',body,(0,0,1.07),(18.36,.55,.23),'Graphite')
 for s in [-1,1]:
  box('Body_sill',body,(0,s*1.46,1.15),(18.4,.19,.19),'Roof_silver')
  for x in [-3.8,-1.3,1.3,3.8]:
   rounded('Equipment_skirts',body,(x,s*1.40,.95),(2.1,.16,.38),'Pearl_white',.025)
 # Distinguish actual electrical roles by visible equipment families.
 if kind.startswith('MC'):
  for x in [-2.5,2.5]:
   box('Traction_converter_cabinets',body,(x,0,.76),(2.5,2.35,.53),'Roof_silver')
   for j in range(13):box('Converter_cooling_grilles',body,(x-1.12+j*.185,-1.184,.77),(.06,.012,.35),'Graphite')
  if kind=='MC2':box('Electrical_changeover_switch',body,(0,-.70,.75),(.88,.7,.51),'Graphite')
  for s in [-1,1]:
   box('Motor_vent_side_grille',body,(6.68,s*1.628,1.77),(.47,.015,.33),'Graphite')
   for k in range(6):box('Motor_vent_slats',body,(6.68,s*1.64,1.65+k*.048),(.44,.012,.016),'Roof_silver')
 elif kind.startswith('TC'):
  box('Transformer_case',body,(0,0,.71),(3.0,2.30,.55),'Graphite')
  for k in range(16):box('Transformer_cooling_fins',body,(-1.42+k*.19,0,.72),(.045,2.52,.58),'Roof_silver')
  box('Auxiliary_converter',body,(-3.65,0,.76),(2.0,2.27,.49),'Roof_silver')
 else:
  hand=-1 if kind=='NDTC_EC2' else 1
  box('Battery_box',body,(hand*2.8,0,.76),(2.4,2.2,.48),'Roof_silver')
  rod('Main_reservoir',body,(-1.5,-.6,.73),(1.1,-.6,.73),.24,'Graphite',20)
  rod('Water_tank',body,(-1.2,.65,.75),(1.2,.65,.75),.28,'Roof_silver',20)
  box('Compressor',body,(-hand*3.5,0,.76),(1.0,1.45,.50),'Graphite')

def gangway(body,end):
 x=end*BODYEND
 # End wall around clear central aperture.
 for s in [-1,1]:box('End_wall',body,(x,s*1.03,2.23),(.09,1.08,2.06),'Pearl_white')
 box('End_wall_top',body,(x,0,3.44),(.09,3.06,.36),'Pearl_white')
 for k in range(7):ring('Gangway_bellows',body,end*(BODYEND+.045+k*.047),1.19,1.25,3.38,'Rubber',.036)
 box('Gangway_floor_bridge',body,(end*9.50,0,1.28),(.34,1.1,.065),'Steel')
 # Semi-permanent bar to mating plane; no AAR knuckle on internal coaches.
 rod('Semipermanent_coupling_bar',body,(end*8.95,0,1.02),(end*HALF,0,1.02),.085,'Graphite',12)
 for s in [-1,1]:line('Intercar_hoses',body,[(end*9.30,s*.31,1.1),(end*9.48,s*.32,.93),(end*(HALF-.024),s*.31,1.04)],.022,'Rubber',8)

def nose(body):
 # Front is an explicitly gridded sculpted skin. Omit central windshield region.
 zlist=[.78,1.04,1.30,1.62,1.94,2.18,2.30,2.64,3.02,3.22,3.48,3.72,3.91,4.00]
 xlist=[9.60,9.96,10.05,9.99,9.72,9.42,9.24,8.81,8.32,8.04,7.74,7.45,7.11,6.85]
 widths=[1.15,1.36,1.43,1.48,1.52,1.55,1.55,1.53,1.49,1.44,1.34,1.19,.94,.65]
 # Four subdivisions per measured/profile control interval, cubic interpolation in Z.
 oldz=zlist[:];oldx=xlist[:];oldw=widths[:]
 def interp(vals,i,t):
  a=vals[max(0,i-1)];b=vals[i];c=vals[i+1];d=vals[min(len(vals)-1,i+2)]
  return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
 zlist=[];xlist=[];widths=[]
 for i in range(len(oldz)-1):
  for j in range(4):
   t=j/4;zlist.append(oldz[i]+t*(oldz[i+1]-oldz[i]));xlist.append(interp(oldx,i,t));widths.append(interp(oldw,i,t))
 zlist.append(oldz[-1]);xlist.append(oldx[-1]);widths.append(oldw[-1])
 oldus=[-1,-.92,-.82,-.73,-.62,-.43,0,.43,.62,.73,.82,.92,1];us=[]
 for a,b in zip(oldus,oldus[1:]):us.extend([a+(b-a)*i/3 for i in range(3)])
 us.append(1)
 def front_x(z,y):
  i=next((i for i in range(len(zlist)-1) if zlist[i]<=z<=zlist[i+1]),len(zlist)-2);t=(z-zlist[i])/(zlist[i+1]-zlist[i]);xx=xlist[i]*(1-t)+xlist[i+1]*t;ww=widths[i]*(1-t)+widths[i+1]*t
  return xx-.24*(y/ww)**2
 def pt(i,u,offset=0):return(xlist[i]-.24*u*u+offset,widths[i]*u,zlist[i])
 for i in range(len(zlist)-1):
  for j in range(len(us)-1):
   u=(us[j]+us[j+1])/2;z=(zlist[i]+zlist[i+1])/2
   isglass=2.30<z<3.22 and abs(u)<.73
   ma='Clear_glass' if isglass else ('Display_black' if z>=2.18 and abs(u)<.82 else('Cobalt_blue' if .73<abs(u)<.93 else'Pearl_white'))
   pts=[pt(i,us[j]),pt(i,us[j+1]),pt(i+1,us[j+1]),pt(i+1,us[j])]
   panel('Nose_windscreen' if isglass else'Sculpted_nose_skin',body,pts,ma)
   if not isglass:panel('Cab_inner_nose_lining',body,[(x-.045,y*.989,z) for x,y,z in reversed(pts)],'Interior_ivory')
 # side wings run from front edge back into fullwidth body; forward side window is a proper omitted quad.
 for s in [-1,1]:
  for i in range(len(zlist)-1):
   zmid=(zlist[i]+zlist[i+1])/2
   # subdivide along fore-aft fraction and leave a glazed patch
   for j in range(5):
    t0=j/5;t1=(j+1)/5
    def sp(ii,t):
     z=zlist[ii];by=1.62 if z<=3.13 else (1.62-(z-3.13)*.75 if z<3.73 else max(0,1.17-(z-3.73)*4.333));bz=min(z,3.82)
     a=Vector((5.65,s*by,bz));b=Vector(pt(ii,s));return tuple(a.lerp(b,t))
    ma='Clear_glass' if 2.30<zmid<3.22 and j in [1,2] else('Cobalt_blue' if j==4 else'Pearl_white')
    pts=[sp(i,t0),sp(i,t1),sp(i+1,t1),sp(i+1,t0)]
    panel('Cab_side_glass' if ma=='Clear_glass' else'Nose_side_cheeks',body,pts,ma)
    if ma!='Clear_glass':panel('Cab_inner_side_lining',body,[(x-.018,y-s*.045,z) for x,y,z in (reversed(pts) if s<0 else pts)],'Interior_ivory')
  # Swept lower teardrop headlight pods, raised slightly from nose.
  coords=[(front_x(z,s*y)+.015,s*y,z) for y,z in [(1.22,1.63),(1.43,1.92),(1.30,2.42),(1.07,2.18)]]
  panel('Nose_lamp_pods',body,coords,'Display_black')
  for j,z in enumerate([1.90,2.12]):
   yy=s*1.25;xx=front_x(z,yy)+.028
   rod('Marker_lamp_bezel',body,(xx,yy,z),(xx+.035,yy,z),.100,'Steel',20)
   rod('Marker_lamp_lens',body,(xx+.036,yy,z),(xx+.041,yy,z),.079,'Headlamp' if j else'Red',20)
   e=empty(f'LIGHT_{"L" if s>0 else"R"}_{j}_ANCHOR',body,(xx+.042,yy,z));e['role']='head/marker upper; tail lower'
 # Windshield seals and wipers follow slope.
 for s in [-1,1]:line('Front_wipers',body,[(9.29,s*.8,2.29),(8.75,s*.66,2.72),(8.50,s*.36,2.98)],.016,'Graphite',10)
 for y in [-.14,.14]:rod('Upper_headlamps',body,(7.69,y,3.55),(7.75,y,3.55),.105,'Headlamp',24)
 box('Front_headcode',body,(7.99,0,3.31),(.04,1.15,.20),'Display_black',Matrix.Rotation(-.60,3,'Y'))
 text('Front_headcode_text',body,'VANDE BHARAT',(8.04,0,3.30),.105,'Amber',(math.pi/2,0,math.pi/2))
 text('ICF_nose_marking',body,'ICF',(10.045,0,1.49),.23,'Cobalt_blue',(math.pi/2,0,math.pi/2))
 # split coupler cover seam, fairing and exposed rescue coupler recessed low.
 line('Nose_cover_seam',body,[(10.052,0,1.29),(9.996,0,1.61),(9.729,0,1.94)],.005,'Floor',6)
 panel('Nose_underlip',body,[(9.6,-1.15,.77),(9.6,1.15,.77),(9.97,1.33,1.02),(9.97,-1.33,1.02)],'Cobalt_blue')
 box('DTC_rescue_coupler_recess',body,(9.38,0,.95),(.50,.40,.27),'Rubber')
 for s in [-1,1]:
  rod('Roof_horns',body,(6.21,s*.39,3.99),(6.54,s*.39,4.01),.065,'Graphite',12)
  rod('Roof_horn_bells',body,(6.54,s*.39,4.01),(6.59,s*.39,4.01),.10,'Graphite',16)
 # roof and lower closure at rear transition.
 panel('Cab_crown',body,[(5.65,0,3.82),(6.85,.65,4.0),(6.85,-.65,4.0)],'Pearl_white')
 box('Cab_floor',body,(6.90,0,1.25),(3.1,2.98,.12),'Floor')
 # Dashboard is wrapped round the two driver positions, all controls real geometry.
 rounded('Cab_console',body,(7.54,0,1.91),(.69,2.70,.43),'Graphite',.06)
 for s in [-1,1]:rounded('Console_wings',body,(7.24,s*1.18,1.94),(1.04,.40,.38),'Graphite',.05)
 for y in [-.73,.73]:
  seat_geometry(body,6.39,y,False,1 if y<0 else 2,1,True)
  box('Driver_pedals',body,(7.16,y,1.36),(.32,.34,.065),'Graphite')
  box('Driver_screen_frame',body,(7.20,y,2.10),(.03,.39,.28),'Display_black')
  box('Driver_screens',body,(7.179,y,2.10),(.009,.32,.22),'Screen')
  for k in range(4):box('Screen_UI_lines',body,(7.173,y,2.04+k*.039),(.004,.24,.006),'Headlamp')
 for y in [-1.04,.28,1.01]:
  rod('Analog_gauges',body,(7.18,y,2.10),(7.155,y,2.10),.105,'Steel',24)
  rod('Gauge_faces',body,(7.15,y,2.10),(7.147,y,2.10),.087,'Interior_ivory',24)
  line('Gauge_needles',body,[(7.14,y,2.10),(7.14,y+.033,2.16)],.005,'Graphite',6)
 for iy in range(5):
  for iz in range(3):rod('Console_buttons',body,(7.168,-.27+iy*.1,2.03+iz*.08),(7.151,-.27+iy*.1,2.03+iz*.08),.021,['Red','Amber','Green'][iz],10)
 for y in [-.43,.43]:line('Control_levers',body,[(7.17,y,1.98),(7.07,y,2.16),(7.06,y+.10,2.16)],.022,'Steel',10)
 empty('CAB_EYE_CAMERA_REFERENCE',body,(6.43,-.73,2.48))['note']='Authoring view only, not a passenger marker or runtime camera'
 # cab partition to keep service area distinct; central opening.
 for s in [-1,1]:box('Cab_partition',body,(5.56,s*.99,2.35),(.065,1.15,2.15),'Interior_ivory')
 box('Cab_partition_lintel',body,(5.56,0,3.34),(.065,.85,.20),'Interior_ivory')

def pantograph(body):
 base=empty('PANTO_BASE',body,(-1.40,0,3.82));r=empty('PANTO_CTRL',base,(0,0,.18));r['extension']=0.;r.id_properties_ui('extension').update(min=0,max=1,description='0 folded; 1 contact top 5.917m, illustrative regular-height geometry')
 l1=1.5;l2=1.2;a0=math.radians(1);amax=math.asin((5.917-4.0-.032)/(l1+l2));r['lower_length_m']=l1;r['upper_length_m']=l2;r['angle_min_rad']=a0;r['angle_max_rad']=amax;r['contact_top_offset_m']=.032;r['base_rail_z_m']=4.0
 lo=empty('PANTO_LOWER_PIVOT',r);up=empty('PANTO_ELBOW_PIVOT',lo,(l1,0,0));he=empty('PANTO_HEAD_LEVEL_PIVOT',up,(-l2,0,0))
 for o,fac in [(lo,-1),(up,2),(he,-1)]:
  d=o.driver_add('rotation_euler',1).driver;v=d.variables.new();v.name='e';v.targets[0].id=r;v.targets[0].data_path='["extension"]';d.expression=f'{fac}*({a0}+max(0,min(1,e))*{amax-a0})'
 for x in [-.28,.55]:
  for y in [-.54,.54]:
   rod('Panto_insulators',base,(x,y,-.04),(x,y,.125),.062,'Insulator',12)
   for j in range(4):rod('Panto_insulator_sheds',base,(x,y,-.015+j*.035),(x,y,-.004+j*.035),.093,'Insulator',12)
 box('Panto_base_frame',base,(.14,0,.13),(1.12,1.22,.06),'Panto_red')
 for y in [-.39,.39]:rod('Panto_lower_arms',lo,(0,y,0),(l1,y,0),.024,'Panto_red');rod('Panto_upper_arms',up,(0,y*.81,0),(-l2,y*.81,0),.019,'Panto_red')
 rod('Panto_lower_crossbrace',lo,(.34,-.39,0),(.34,.39,0),.014,'Panto_red')
 for pa,name,rad in [(r,'base',.037),(up,'elbow',.03),(he,'head',.02)]:rod('Panto_'+name+'_hinge',pa,(0,-.46,0),(0,.46,0),rad,'Steel')
 for x in [-.065,.065]:
  box('Panto_contact_strips',he,(x,0,.025),(.045,1.70,.014),'Graphite')
  for s in [-1,1]:line('Panto_contact_horns',he,[(x,s*.85,.025),(x,s*.98,0),(x,s*1.08,-.045)],.012,'Graphite')
 # Adjacent switchgear and bus, roof positions approximate from photo.
 for x in [1.20,2.02]:
  rod('HV_roof_insulator',body,(x,.70,3.81),(x,.70,4.10),.07,'Insulator',12)
  for j in range(6):rod('HV_roof_insulator_shed',body,(x,.70,3.84+j*.042),(x,.70,3.85+j*.042),.10,'Insulator',12)
 box('Vacuum_circuit_breaker',body,(1.65,-.33,3.95),(.65,.56,.22),'Roof_silver')
 line('HV_bus',body,[(-.90,.70,3.97),(.20,.70,4.08),(1.2,.70,4.11),(2.02,.70,4.11)],.014,'Panto_red')
 return r,lo,up,he

def bounds():
 bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in COL.objects if o.type=='MESH' for v in o.data.vertices]
 return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}

def export(path,anim=False):
 bpy.ops.object.select_all(action='DESELECT')
 for o in COL.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_space_transform=False,add_leaf_bones=False,bake_anim=anim,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='AUTO')

def build(kind):
 global COL,ROOT
 bpy.ops.wm.read_factory_settings(use_empty=True);M.clear();batches.clear();materials();sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=24
 COL=bpy.data.collections.new('VB_'+kind+'_ASSET');sc.collection.children.link(COL);ROOT=empty('VB_'+kind+'_ROOT');body=empty('BODY',ROOT)
 ROOT['asset_type']=kind;ROOT['coupling_pitch_m']=PITCH;ROOT['status']='Compact original modelling handoff, not converted TF3 resource';ROOT['coordinate_system']='X front, Y lateral, Z up; rail=0; metres'
 for label,s in [('FRONT',1),('REAR',-1)]:
  e=empty('COUPLING_'+label,ROOT,(s*HALF,0,1.02));e.rotation_euler.z=0 if s>0 else math.pi;e['mating_plane_axis']='local +X outward';e['not_visual_tip']=True
  e['datum_role']='stowed rescue-coupler/formation-spacing datum inside closed nose; whole-set coupling unsupported' if kind=='DTC' and s>0 else 'internal semi-permanent mating plane'
 dtc=kind=='DTC';ec='EC' in kind;hand=-1 if kind=='NDTC_EC2' else 1
 windows_sides(body,dtc);roof(body,-BODYEND,5.65 if dtc else BODYEND);n=interior(body,dtc,ec,hand);underframe(body,kind);bogies(body,kind.startswith('MC'));gangway(body,-1)
 if dtc:nose(body)
 else:gangway(body,1)
 rig=pantograph(body) if kind.startswith('TC') else None
 flush();bpy.context.view_layer.update()
 # Ensure readable materials, no custom-model external path dependencies.
 sc.world=bpy.data.worlds.new('World');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.24,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 bb=bounds();tris=sum(len(p.vertices)-2 for o in COL.objects if o.type=='MESH' for p in o.data.polygons)
 qa={'kind':kind,'passenger_seats':n,'driver_seats':2 if dtc else 0,'meshes':sum(o.type=='MESH' for o in COL.objects),'triangles':tris,'objects':len(COL.objects),'bounds_lowered_m':bb,'coupling_front_m':[HALF,0,1.02],'coupling_rear_m':[-HALF,0,1.02],'coupling_pitch_m':PITCH,'body_end_planes_m':[-BODYEND,5.65 if dtc else BODYEND],'gangway_mating_extent_m':[-HALF] if dtc else[-HALF,HALF],'bogie_centres_m':[-BOGIE,BOGIE],'wheelbase_m':WBASE,'wheelbase_status':'provisional: secondary corroboration; not certified from drawing','wheel_diameter_m':.952,'panto':None}
 if rig:
  r,lo,up,he=rig;poses=[]
  for i in range(101):
   r['extension']=i/100;r.update_tag();bpy.context.view_layer.update();po={'e':i/100,'head_z':he.matrix_world.translation.z,'top_z':he.matrix_world.translation.z+.032,'level_error':max(abs(v) for v in he.matrix_world.to_euler()),'lower_length':(up.matrix_world.translation-lo.matrix_world.translation).length,'upper_length':(he.matrix_world.translation-up.matrix_world.translation).length};poses.append(po)
  qa['panto']={'samples':poses,'base_z_m':4,'nominal_contact_top_m':5.917,'angle_min_rad':r['angle_min_rad'],'angle_max_rad':r['angle_max_rad'],'lower_length_m':1.5,'upper_length_m':1.2,'scope':'Rigid articulated visual approximation, independent per car; no runtime wire binding'}
  r['extension']=0;r.update_tag();bpy.context.view_layer.update()
 sc.name='VB_'+kind+'_AUTHORING';bpy.ops.wm.save_as_mainfile(filepath=str(P/'cars'/('VB_'+kind+'.blend')),compress=True);export(P/'cars'/('VB_'+kind+'.fbx'))
 if rig:
  r['extension']=1;r.update_tag();bpy.context.view_layer.update();export(P/'cars'/('VB_'+kind+'_raised.fbx'));r['extension']=0;r.update_tag();bpy.context.view_layer.update()
  for o in [lo,up,he]:o.driver_remove('rotation_euler',1)
  for f in range(1,82):
   e=(f-1)/40 if f<=41 else(81-f)/40;a=r['angle_min_rad']+e*(r['angle_max_rad']-r['angle_min_rad'])
   for o,v in [(lo,-a),(up,2*a),(he,-a)]:o.rotation_euler.y=v;o.keyframe_insert(data_path='rotation_euler',frame=f)
  sc.frame_start=1;sc.frame_end=81;sc.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'cars'/('VB_'+kind+'_baked.blend')),compress=True);export(P/'cars'/('VB_'+kind+'_motion.fbx'),True)
 (P/'qa'/('VB_'+kind+'.json')).write_text(json.dumps(qa,indent=2));return qa

if __name__=='__main__':
 kinds=['DTC','MC','MC2','TC_CC','TC_EC','NDTC_EC','NDTC_EC2'];summary={}
 for k in kinds:
  summary[k]=build(k);print('BUILT',k,summary[k]['triangles'],flush=True)
 (P/'qa'/'car_summary.json').write_text(json.dumps(summary,indent=2))
