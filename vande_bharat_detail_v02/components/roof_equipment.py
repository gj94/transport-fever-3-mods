"""Roof HVAC, VCB and WBL22.03-informed pantograph hardware; authored rig retained."""
import bpy,math
from common import *
P='VB02_ROOF_'
def apply(ctx):
 remove_prefix(P);M=ctx['materials'];body=ctx['body'];C=ctx['collection'];kind=ctx['kind'];dtc=kind=='DTC';L=ctx['layout']
 def B(n,c,d,m='alloy',pa=body,b=.004,local=False):return box(P+n,c,d,M[m],pa,C,b,local)
 def R(n,a,z,r,m='steel',pa=body,local=False):return rod(P+n,a,z,r,M[m],pa,C,16,local)
 def T(n,pts,r,m='rubber',pa=body,local=False):return tube(P+n,pts,r,M[m],pa,C,12,local)
 def CY(n,c,r,d,m='alloy',pa=body,axis='Z',N=48,local=False):return cyl(P+n,c,r,d,M[m],pa,C,axis,N,local=local)
 def remove(names):
  for o in list(bpy.data.objects):
   if o.type=='MESH' and any(o.name==n or o.name.startswith(n+'.') for n in names):bpy.data.objects.remove(o,do_unlink=True)
 remove(['HVAC_packages','HVAC_fan_grilles','HVAC_louvres','HVAC_end_grille'])
 for x in L['hvac_centres']:
  B('HVAC_perimeter_plinth',(x,0,3.755),(2.61,1.88,.085),'dark_metal',b=.025)
  B('HVAC_formed_casing',(x,0,3.93),(2.60,1.85,.42),'alloy',b=.045)
  for dx in [-1.16,-.43,.43,1.16]:B('HVAC_panel_seam',(x+dx,0,4.144),(.007,1.70,.004),'dark_metal',b=.001)
  for y in [-.51,.51]:
   CY('fan_recess',(x+.13,y,4.143),.334,.009,'black')
   ring(P+'fan_outer_guard',(x+.13,y,4.146),.337,.322,.006,M['brushed'],body,C,'Z',64)
   CY('fan_hub',(x+.13,y,4.146),.065,.009,'alloy')
   # Separate aerofoil-like fan blades under a real wire cage.
   for k in range(7):
    a=k*math.tau/7;pts=[]
    for r,t in [(.075,a-.08),(.28,a+.17),(.30,a+.37),(.18,a+.41),(.08,a+.15)]:pts.append((x+.13+r*math.cos(t),y+r*math.sin(t),4.147))
    mesh(P+'fan_blade',pts,[tuple(range(5))],M['dark_metal'],body,C)
   for rr in [.09,.145,.20,.255,.31]:
    T('fan_wire_guard',[(x+.13+rr*math.cos(k*math.tau/64),y+rr*math.sin(k*math.tau/64),4.148) for k in range(65)],.0016,'steel')
   for k in range(8):
    a=k*math.tau/8;R('fan_guard_spoke',(x+.13+.07*math.cos(a),y+.07*math.sin(a),4.148),(x+.13+.321*math.cos(a),y+.321*math.sin(a),4.148),.0022,'steel')
  for s in [-1,1]:
   B('HVAC_side_air_inlet',(x,s*.929,3.962),(2.19,.012,.20),'black',b=.013)
   for j in range(8):B('HVAC_air_inlet_louvre',(x,s*.939,3.875+j*.024),(2.12,.012,.012),'alloy',b=.002)
   for dx in [-1.21,1.21]:
    B('HVAC_lifting_lug',(x+dx,s*.78,4.117),(.085,.040,.058),'dark_metal',b=.011)
   for dx in [-1.18,-.39,.39,1.18]:
    CY('HVAC_cover_fastener',(x+dx,s*.83,4.147),.009,.004,'steel',N=6)
  B('HVAC_service_cover',(x-.84,0,4.144),(.61,1.65,.008),'alloy',b=.01)
  for s in [-1,1]:T('HVAC_condensate_drain',[(x-.95,s*.83,3.77),(x-.95,s*1.08,3.74),(x-.81,s*1.18,3.68)],.016,'rubber')
 # Grille peaks define the nominal4.140m non-pantograph envelope.
 for obj in list(C.objects):
  if obj.type=='MESH' and obj.name.startswith((P+'HVAC_',P+'fan_')):
   for v in obj.data.vertices:v.co.z-=.0105
 if dtc:
  B('cab_AC_casing',(8.2,0,4.015),(1.2,1.3,.20),'alloy',b=.035)
  CY('cab_AC_fan_recess',(8.2,0,4.118),.235,.006,'black')
  ring(P+'cab_AC_guard',(8.2,0,4.126),.240,.231,.009,M['brushed'],body,C,'Z',48)
  for j in range(-4,5):B('cab_AC_grille',(8.2+j*.044,0,4.132),(.009,.40,.005),'alloy',b=.001)
  for s in [-1,1]:
   for j in range(5):B('cab_AC_side_louvre',(8.2,s*.656,3.97+j*.026),(1.07,.012,.012),'dark_metal',b=.002)
 # Roof service walk strips and seam clips, fitted flush to the crown.
 for s in [-1,1]:
  for x in [-7.9,-3.5,.6,3.0,7.8]:
   if dtc and x>7:continue
   B('roof_anti_slip_patch',(x,s*.85,3.799),(1.0,.19,.007),'dark_metal',b=.012)
 # No panto visual changes on cars without a live source mechanism.
 if not kind.startswith('TC'):return {'HVAC_units':2,'pantograph':False}
 remove(['Panto_insulators','Panto_insulator_sheds','Panto_base_frame','Panto_lower_arms','Panto_upper_arms','Panto_lower_crossbrace','Panto_base_hinge','Panto_elbow_hinge','Panto_head_hinge','Panto_contact_strips','Panto_contact_horns','HV_roof_insulator','HV_roof_insulator_shed','Vacuum_circuit_breaker','HV_bus'])
 base=bpy.data.objects['PANTO_BASE'];ctrl=bpy.data.objects['PANTO_CTRL'];lo=bpy.data.objects['PANTO_LOWER_PIVOT'];up=bpy.data.objects['PANTO_ELBOW_PIVOT'];head=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT']
 for x in [-.28,.55]:
  for y in [-.54,.54]:
   CY('panto_insulator_core',(x,y,.052),.042,.18,'ivory',base,local=True)
   for z in [-.018,.017,.052,.087]:
    lathe(P+'panto_insulator_shed',(x,y,z),[(-.008,.043),(-.004,.092),(.005,.095),(.012,.051),(-.008,.043)],M['ivory'],base,C,'Z',48,True)
   CY('panto_insulator_top',(x,y,.144),.077,.018,'steel',base,local=True)
 for xx in [-.28,.55]:B('panto_base_crossframe',(xx,0,.155),(.14,1.22,.035),'dark_metal',base,.006,True)
 for y in [-.45,.45]:B('panto_base_channel',(.15,y,.186),(1.28,.085,.09),'dark_metal',base,.007,True)
 # Main lower arm is triangulated from two feet to a central elbow support.
 for s in [-1,1]:
  beam(P+'panto_lower_box_arm',(0,s*.36,0),(1.5,s*.13,0),.072,.052,M['dark_metal'],lo,C,True,.009)
  beam(P+'panto_upper_tube',(0,s*.13,0),(-1.2,s*.32,0),.034,.031,M['steel'],up,C,True,.006)
  R('panto_upper_cross_diagonal',(-.10,s*.13,0),(-1.06,-s*.28,0),.010,'steel',up,True)
  R('panto_parallel_guide',(.10,s*.43,-.045),(1.40,s*.20,-.045),.013,'steel',lo,True)
 R('panto_lower_torsion_crossbeam',(.18,-.34,0),(.18,.34,0),.033,'dark_metal',lo,True)
 for pa,n,r,w in [(ctrl,'base',.048,.82),(up,'elbow',.042,.41),(head,'head',.034,.86)]:
  hz=-.055 if n=='head' else 0
  CY('panto_'+n+'_crossshaft',(0,0,hz),r,w,'steel',pa,'Y',48,True)
  for s in [-1,1]:CY('panto_'+n+'_bearing',(0,s*w/2,hz),r*1.55,.038,'dark_metal',pa,'Y',48,True);CY('panto_'+n+'_bearing_bolt',(0,s*(w/2+.025),hz),r*.64,.018,'brushed',pa,'Y',6,True)
 # Pneumatic bellows and spring cylinder live on static base, clear of the arm sweep.
 CY('panto_air_bellow',(-.32,0,.245),.122,.11,'rubber',base,N=48,local=True)
 for z in [.195,.222,.248,.275]:ring(P+'panto_bellow_fold',(-.32,0,z),.125,.108,.012,M['rubber'],base,C,'Z',48,True)
 T('panto_air_feed',[(-.45,-.45,.15),(-.23,-.45,.21),(.06,-.24,.24),(-.32,0,.24)],.009,'rubber',base,True)
 # OEM head: 1800mm total width and 390mm fore/aft carbon strip spacing.
 for x in [-.195,.195]:
  B('carbon_strip_aluminium_carrier',(x,0,.003),(.046,1.35,.022),'alloy',head,.005,True)
  B('carbon_contact_strip',(x,0,.025),(.035,1.35,.014),'dark_metal',head,.003,True)
  for s in [-1,1]:
   pts=[(x,s*.675,.017),(x,s*.75,.003),(x,s*.82,-.025),(x,s*.872,-.069),(x,s*.888,-.10)]
   T('carbon_downturned_horn',pts,.012,'dark_metal',head,True)
 for s in [-1,1]:
  B('head_rocker_box',(0,s*.40,-.085),(.20,.16,.09),'alloy',head,.015,True)
  for x in [-.18,.18]:
   T('head_leaf_spring',[(0,s*.4,-.073),(x*.4,s*.4,-.060),(x,s*.4,-.010)],.006,'steel',head,True)
   R('head_braided_shunt',(x,s*.30,-.018),(0,s*.43,-.10),.009,'alloy',head,True)
  CY('head_rocker_pin',(0,s*.492,-.080),.028,.028,'steel',head,'Y',32,True)
 # VCB: twin ribbed isolators and grounded housing with conduit rather than plain box.
 for x in [7.35,7.80]:
  CY('HV_support_core',(x,.70,3.96),.054,.29,'ivory')
  for z in [3.84+i*.039 for i in range(7)]:
   lathe(P+'HV_support_shed',(x,.7,z),[(-.006,.046),(0,.10),(.01,.095),(.017,.049),(-.006,.046)],M['ivory'],body,C,'Z',48)
  CY('HV_terminal_cap',(x,.70,4.105),.070,.014,'steel')
 B('VCB_grounded_housing',(7.52,-.33,3.945),(.65,.56,.22),'alloy',b=.018)
 for s in [-1,1]:
  B('VCB_panel_gasket',(7.52,-.33+s*.285,3.945),(.59,.008,.16),'rubber',b=.009)
  B('VCB_service_panel',(7.52,-.33+s*.292,3.945),(.56,.007,.135),'alloy',b=.008)
  for dx in [-.25,.25]:CY('VCB_cover_screw',(7.52+dx,-.33+s*.298,3.945),.009,.006,'steel',axis='Y',N=6)
 T('HV_busbar',[(9.35,.70,4.12),(8.50,.70,4.18),(7.80,.70,4.11),(7.35,.70,4.11)],.014,'alloy')
 T('VCB_HV_connection',[(7.35,.70,4.11),(7.35,.19,4.11),(7.52,-.12,4.04)],.013,'alloy')
 T('roof_control_conduit',[(7.85,-.36,3.88),(8.09,-.36,3.83),(8.34,-.54,3.79)],.018,'rubber')
 return {'HVAC_units':2,'pantograph':True,'head_width_m':1.8,'strip_width_m':.035,'strip_center_spacing_m':.390,'head_contact_top_offset_m':.032,'source':'Schunk WBL22.03 OEM manual on IRIMEE official server; matching VB2 parts procurement','scope':'OEM-informed head geometry; inherited regular-height 1.5/1.2m authoring kinematics preserved'}
