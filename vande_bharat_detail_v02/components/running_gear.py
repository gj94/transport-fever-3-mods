"""Two-air-spring bolsterless VB2 visual bogies with preserved yaw/axle pivots."""
import bpy,math
from common import *
P='VB02_GEAR_'
def apply(ctx):
 remove_prefix(P);M=ctx['materials'];C=ctx['collection'];body=ctx['body'];kind=ctx['kind'];powered=kind.startswith('MC');L=ctx['layout'];U=L['underframe']
 old=('Bogie_','Air_spring_','Damper_','Axle_shafts_','Wheel_tread_','Wheel_web_','Wheel_flange_','Wheel_hub_','Axleboxes_','Primary_springs_','Traction_motors_','Gearboxes_')
 for o in list(bpy.data.objects):
  if o.type=='MESH' and o.name.startswith(old):bpy.data.objects.remove(o,do_unlink=True)
 def B(n,c,d,m,p,b=.004):return box(P+n,c,d,M[m],p,C,b,local=True)
 def CY(n,c,r,d,m,p,axis='Z',N=32):return cyl(P+n,c,r,d,M[m],p,C,axis,N,local=True)
 def R(n,a,b,r,m,p,N=16):return rod(P+n,a,b,r,M[m],p,C,N,local=True)
 def T(n,pts,r,m,p,N=12):return tube(P+n,pts,r,M[m],p,C,N,local=True)
 def L(n,c,profile,m,p,axis='Z',N=48):return lathe(P+n,c,profile,M[m],p,C,axis,N,True)
 def bolt(n,c,p,axis='Y',r=.018):
  CY(n+' washer',c,r*1.35,.007,'steel',p,axis,20);cc=list(c);cc['XYZ'.index(axis)]+=.007;CY(n+' hex',cc,r,.020,'brushed',p,axis,6)
 def spring(n,c,r,h,turns,p):
  x,y,z=c;pts=[(x+r*math.cos(i*math.tau*turns/100),y+r*math.sin(i*math.tau*turns/100),z+h*i/100) for i in range(101)];T(n,pts,.020,'dark_metal',p,10)
 for lab in ['A','B']:
  p=bpy.data.objects[f'BOGIE_{lab}_YAW_Z']
  # Fabricated Y-shaped side frame silhouette; two secondary bellows, one each side.
  for s in [-1,1]:
   poly=[(-2.04,s*.99,.02),(-1.34,s*1.04,.17),(-.56,s*.89,-.13),(.56,s*.89,-.13),(1.34,s*1.04,.17),(2.04,s*.99,.02)]
   for a,b in zip(poly,poly[1:]):
    beam(P+'Y_frame_box',a,b,.23,.255,M['dark_metal'],p,C,True,.020)
    for zz in [-.104,.104]:
     T('frame_fabricated_edge_weld',[(a[0],a[1]+s*.115,a[2]+zz),(b[0],b[1]+s*.115,b[2]+zz)],.0038,'alloy',p,8)
   for xx in [-.58,.58]:
    B('frame_joint_reinforcement',(xx,s*1.013,-.125),(.145,.020,.219),'dark_metal',p,.018)
    for zz in [-.19,-.06]:bolt('frame_joint_fastener',(xx,s*1.030,zz),p,r=.011)
   for x in [-1.43,1.43]:
    B('axle_pedestal_horn',(x,s*1.02,-.13),(.35,.18,.22),'dark_metal',p,.020)
    for dx in [-.11,.11]:bolt('frame_cover_bolt',(x+dx,s*1.135,-.10),p)
   L('secondary_air_bellow',(0,s*.87,.125),[(0,0), (0,.272),(.03,.29),(.09,.295),(.13,.28),(.16,.29),(.21,.285),(.245,.264),(.26,.264),(.26,0)],'rubber',p,N=64)
   CY('air_spring_upper_plate',(0,s*.87,.401),.306,.022,'alloy',p);CY('air_spring_lower_plate',(0,s*.87,.117),.30,.020,'dark_metal',p)
   for a in range(8):
    ang=a*math.tau/8;bolt('air_spring_flange',(math.cos(ang)*.259,s*.87+math.sin(ang)*.259,.416),p,'Z',.011)
   # Lateral/yaw dampers with exposed piston section and separate clevis eyes.
   R('yaw_damper_cylinder',(-.53,s*1.10,.16),(.32,s*1.22,.25),.048,'dark_metal',p);R('yaw_damper_polished_rod',(.30,s*1.22,.25),(.71,s*1.28,.285),.020,'steel',p)
   for x,y,z in [(-.53,s*1.10,.16),(.71,s*1.28,.285)]:
    CY('yaw_damper_eye',(x,y,z),.065,.095,'alloy',p,'Y');bolt('yaw_damper_pin',(x,y+s*.055,z),p)
   T('air_spring_feed',[(0,s*.89,.16),(.24,s*.71,.16),(.43,s*.68,.04),(.54,s*.48,.04)],.012,'rubber',p)
  for x in [-.68,.68]:B('transverse_welded_beam',(x,0,.006),(.24,1.9,.225),'dark_metal',p,.015)
  B('centre_transom',(0,0,.010),(.22,1.70,.21),'dark_metal',p,.015)
  CY('centre_pivot_socket',(0,0,.166),.20,.18,'dark_metal',p)
  for j,xx in enumerate([-1.35,1.35],1):
   axle=bpy.data.objects[f'AXLE_{lab}_{j}_ROLL_Y'];CY('rotating_axle',(0,0,0),.095,2.30,'steel',axle,'Y',48)
   for s in [-1,1]:
    # Continuous turned wheel profile. Tread radius .476, inward flange .504 exactly.
    prof=[(.712,0),(.712,.15),(.748,.38),(.756,.492),(.768,.504),(.782,.497),(.791,.478),(.905,.474),(.924,.446),(.934,.392),(.963,.367),(1.002,.265),(1.046,.17),(1.09,.14),(1.10,0)]
    wheel=L('turned_wheel',(0,0,0),[(s*y,r) for y,r in prof],'steel',axle,'Y',72)
    wheel.data.materials.append(M['dark_metal'])
    for poly in wheel.data.polygons:
     coords=[wheel.data.vertices[i].co for i in poly.vertices];rr=sum(math.hypot(v.x,v.z) for v in coords)/len(coords);yy=sum(abs(v.y) for v in coords)/len(coords)
     if yy>.916 and .17<rr<.435:poly.material_index=1
    # Dark wheelweb cover keeps machined rim distinguished, with inset boss and inspection plugs.
    L('wheelweb',(0,0,0),[(s*.938,.174),(s*.938,.370),(s*.956,.354),(s*1.024,.20),(s*1.024,.174),(s*.938,.174)],'dark_metal',axle,'Y',64)
    CY('wheel_hub_cap',(0,s*1.105,0),.146,.030,'alloy',axle,'Y',48)
    for k in range(8):
     a=k*math.tau/8;CY('wheel_hub_bolt',(.107*math.cos(a),s*1.128,.107*math.sin(a)),.010,.014,'steel',axle,'Y',6)
    # Bearings/control arms remain NON rotating and follow bogie yaw only.
    B('axlebox_casting',(xx,s*1.13,-.234),(.32,.29,.27),'dark_metal',p,.035)
    CY('axlebox_end_lid',(xx,s*1.296,-.234),.119,.045,'alloy',p,'Y',48)
    for k in range(6):
     a=k*math.tau/6;bolt('axlebox_lid_bolt',(xx+.091*math.cos(a),s*1.325,-.234+.091*math.sin(a)),p,r=.010)
    sign=1 if xx<0 else -1
    beam(P+'axle_control_arm',(xx,s*1.08,-.205),(xx+sign*.56,s*1.015,-.045),.105,.105,M['dark_metal'],p,C,True,.025)
    CY('control_arm_bush',(xx+sign*.56,s*1.015,-.045),.075,.19,'rubber',p,'Y');bolt('control_arm_pivot',(xx+sign*.56,s*1.125,-.045),p,r=.024)
    spring('primary_coil',(xx,s*1.07,-.02),.112,.247,5.3,p)
    spring('primary_inner_counterwound_coil',(xx,s*1.07,-.02),.066,.247,-6.3,p)
    CY('primary_spring_lower_seat',(xx,s*1.07,-.023),.143,.026,'alloy',p);CY('primary_spring_top',(xx,s*1.07,.242),.143,.024,'alloy',p)
    R('primary_vertical_damper',(xx+sign*.27,s*1.215,-.19),(xx+sign*.27,s*1.215,.10),.033,'dark_metal',p);R('primary_damper_rod',(xx+sign*.27,s*1.215,.10),(xx+sign*.27,s*1.215,.26),.015,'steel',p)
    T('bearing_sensor_cable',[(xx,s*1.295,-.18),(xx+.13,s*1.34,-.11),(xx+.30,s*1.24,.02),(xx+.42,s*1.10,.08)],.008,'rubber',p)
    # Disc brakes on axle, calipers fixed to frame; representative hardware positions.
    for yy in ([s*.982] if powered else [s*.43]):
     L('brake_disc',(0,yy,0),[(-.020,.174),(-.020,.363),(-.012,.375),(.012,.375),(.020,.363),(.020,.174),(-.020,.174)] if powered else [(-.035,.13),(-.035,.31),(-.025,.319),(.025,.319),(.035,.31),(.035,.13),(-.035,.13)],'brushed',axle,'Y',64)
     for k in range(8 if powered else 12):
      a=k*math.tau/(8 if powered else 12);r=.294 if powered else .252;cc=(r*math.cos(a),yy+s*.023,r*math.sin(a))
      CY('disc_counterbored_mount',cc,.019,.006,'black',axle,'Y',32)
      CY('disc_recessed_mount_bolt',(cc[0],cc[1]+s*.004,cc[2]),.010,.006,'steel',axle,'Y',6)
     B('brake_caliper',(xx+(.37 if xx>0 else -.37),yy,.005),(.16,.15,.30),'dark_metal',p,.035);CY('brake_cylinder',(xx+(.40 if xx>0 else -.40),yy,-.016),.097,.17,'alloy',p,'X')
     T('brake_air_hose',[(xx-.30,yy,.08),(xx-.46,yy,.16),(xx-.53,yy*.7,.22),(xx-.56,0,.22)],.014,'rubber',p)
   if powered:
    CY('traction_motor_body',(xx+.29,0,-.06),.238,1.04,'dark_metal',p,'Y',48)
    for yy in [-.50,.50]:CY('traction_motor_endbell',(xx+.29,yy,-.06),.246,.070,'alloy',p,'Y',48)
    for k in range(12):
     a=k*math.tau/12;B('motor_cooling_rib',(xx+.29+.238*math.cos(a),0,-.06+.238*math.sin(a)),(.019,.89,.022),'dark_metal',p,.003)
    B('reduction_gearcase',(xx,.61,-.13),(.45,.28,.44),'dark_metal',p,.05)
    CY('gear_bearing_cover',(xx,.766,-.15),.162,.036,'alloy',p,'Y',48)
    T('motor_power_cable',[(xx+.36,-.38,.12),(xx+.53,-.51,.20),(xx+.62,-.36,.29),(xx+.60,0,.30)],.024,'rubber',p)
  # Brake distributor with body-welded pipes, clipped at cross members.
  B('brake_valve_manifold',(-.31,0,.19),(.28,.34,.12),'alloy',p,.013)
  for y in [-.13,0,.13]:T('bogie_brake_pipe',[(-1.72,y,.17),(-.63,y,.17),(-.45,y,.22),(.62,y,.22),(1.70,y,.16)],.011,'steel',p)
 # Cabinet finish detail under the car body, retains role-distinct original equipment positions.
 for obj in list(bpy.data.objects):
  if obj.type!='MESH' or not obj.name.startswith(('Traction_converter_cabinets','Auxiliary_converter','Battery_box','Compressor','Transformer_case')):continue
  verts=[obj.matrix_world@v.co for v in obj.data.vertices];xmin=min(v.x for v in verts);xmax=max(v.x for v in verts);zmin=min(v.z for v in verts);zmax=max(v.z for v in verts)
  for s in [-1,1]:
   y=s*(max(abs(v.y) for v in verts)+.013)
   for x in [xmin+.07,xmax-.07]:
    B('cabinet_hinged_edge',(x,y,(zmin+zmax)/2),(.023,.026,zmax-zmin-.06),'dark_metal',body,.003)
    for z in [zmin+.065,zmax-.065]:bolt('cabinet_captive_fastener',(x,y+s*.023,z),body,r=.012)
   B('cabinet_service_plaque',((xmin+xmax)/2,y,(zmin+zmax)/2),(.25,.009,.09),'brushed',body,.003)
 # Underfloor auxiliaries follow the existing car electrical roles, with separate material finishes.
 if not powered and not kind.startswith('TC'):
  hand=-1 if kind=='NDTC_EC2' else 1;cx=hand*U['compressor_x']
  for o in list(bpy.data.objects):
   if o.type=='MESH' and o.name.split('.')[0]=='Compressor':bpy.data.objects.remove(o,do_unlink=True)
  B('compressor_isolation_skid',(cx,0,.515),(1.0,1.36,.055),'dark_metal',body,.008)
  for dx in [-.39,.39]:
   for y in [-.54,.54]:CY('compressor_rubber_mount',(cx+dx,y,.567),.055,.07,'rubber',body)
  CY('compressor_motor',(cx-.12,-.13,.735),.176,.64,'dark_metal',body,'Y',48)
  for y in [-.46,.20]:CY('compressor_motor_end',(cx-.12,y,.735),.184,.035,'alloy',body,'Y',48)
  for j in range(16):
   a=j*math.tau/16;B('compressor_motor_fin',(cx-.12+.176*math.cos(a),-.13,.735+.176*math.sin(a)),(.012,.57,.014),'alloy',body,.002)
  for y in [-.35,.25]:
   CY('compressor_pump_cylinder',(cx+.23,y,.80),.100,.30,'alloy',body)
   for z in [.68,.72,.76,.80,.84,.88,.92]:CY('compressor_pump_cooling_fin',(cx+.23,y,z),.125,.012,'dark_metal',body)
   B('compressor_cylinder_head',(cx+.23,y,.967),(.24,.24,.055),'alloy',body,.012)
  T('compressor_copper_delivery',[(cx+.23,.25,1.0),(cx+.40,.25,1.035),(cx+.40,-.42,1.035),(cx+.35,-.65,.94),(cx-.50,-.65,.84)],.012,'alloy',body)
  CY('compressor_air_filter',(cx-.33,.45,.83),.115,.22,'black',body)
  T('compressor_flexible_intake',[(cx-.32,.45,.94),(cx-.04,.45,.99),(cx+.23,.25,.995)],.022,'rubber',body)
  for yy,rr,center in [(-.6,.247,hand*U['reservoir_x']),(.65,.287,hand*U['water_x'])]:
   # Clamps follow the independently positioned full-size tanks.
   for xx in [center-.8,center+.8]:
    ring(P+'tank_support_strap',(xx,yy,.74),rr+.012,rr,.035,M['steel'],body,C,'X',48,True)
    B('tank_saddle',(xx,yy,.99),(.085,rr*1.75,.05),'dark_metal',body,.007)
  CY('reservoir_drain_tap',(hand*U['reservoir_x'],-.60,.455),.022,.055,'alloy',body)
  T('reservoir_delivery_pipe',[(hand*U['reservoir_x']-1.30,-.60,.73),(hand*U['reservoir_x']-1.51,-.60,.73),(hand*U['reservoir_x']-1.59,-.24,.73),(hand*U['reservoir_x']-1.72,-.24,.93)],.013,'steel',body)
 elif powered:
  for xx in U['converter_centres']:
   for s in [-1,1]:
    B('converter_filter_access',(xx,s*1.195,.76),(1.02,.025,.38),'equipment',body,.015)
    for j in range(12):B('converter_air_filter_slit',(xx-.45+j*.082,s*1.216,.76),(.027,.013,.30),'black',body,.004)
    for dx in [-.47,.47]:
     CY('converter_panel_cam',(xx+dx,s*1.227,.91),.019,.011,'steel',body,'Y',20)
   T('converter_power_bundle',[(xx+.98,.55,.63),(xx+1.25,.55,.61),(xx+1.36,.30,.75),(xx+1.38,.30,.97)],.037,'rubber',body)
 else:
  for s in [-1,1]:
   for x in [U['transformer_x']-1.22,U['transformer_x']+1.22]:
    CY('transformer_terminal_bushing',(x,s*.84,1.045),.070,.17,'ivory',body)
    for z in [.995,1.026,1.057,1.088]:CY('transformer_bushing_rib',(x,s*.84,z),.089,.011,'ivory',body)
   T('transformer_oil_pipe',[(U['transformer_x']-1.30,s*1.22,.89),(U['transformer_x']-1.55,s*1.22,.89),(U['transformer_x']-1.59,s*.96,.57),(U['transformer_x']-1.30,s*.96,.56)],.019,'dark_metal',body)
  B('transformer_service_box',(U['transformer_x']+1.04,-1.23,.72),(.52,.16,.24),'equipment',body,.018)
 # Continuous underfloor pipe tray and regular supports within the original sill envelope.
 for yy in [-.34,-.18]:
  T('underfloor_service_main',[(-11.1,yy,1.085),(-5.2,yy,1.085),(-3.0,yy,1.035),(3.0,yy,1.035),(5.2,yy,1.085),(11.1,yy,1.085)],.012,'alloy',body)
  for x in [-10,-8,-6,-4,-2,0,2,4,6,8,10]:B('service_pipe_clip',(x,yy,1.076),(.035,.048,.032),'dark_metal',body,.003)
 return {'secondary_air_springs_per_bogie':2,'bogies_per_car':2,'motor_equipment':powered,'axle_and_bogie_parenting':'retained inherited controls; rotating wheels/discs under axle, bearings and calipers under bogie','wheel_tread_radius_m':.476,'flange_radius_m':.504,'scope':'Photo/manual-informed representative components; subtype-specific factory drawings not fully traced','objects':sum(o.name.startswith(P) for o in bpy.data.objects)}
