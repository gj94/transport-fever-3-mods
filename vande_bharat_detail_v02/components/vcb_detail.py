"""VB-specific Schneider22CB silhouette and visible terminal paths from OEM drawings.
The body is below its roof mounting plate. Fine fastening/earthing forms remain representative.
"""
import bpy,bmesh,math
from mathutils import Vector
from common import *
from materials import make
P='VB02_VCB_'
def apply(ctx):
 if not ctx['kind'].startswith('TC'):return {'applied':False}
 remove_prefix(P);M=dict(ctx['materials']);body=ctx['body'];C=ctx['collection']
 M['porcelain']=make('22CB_grey_glazed_porcelain',(.61,.66,.68),.05,.22,.025,280)
 M['orange_cast']=make('22CB_orange_cast_terminal',(.43,.059,.017),.42,.32,.045,190)
 M['housing']=make('22CB_anodized_case',(.23,.27,.285),.58,.42,.06,150)
 M['copper']=make('HV_copper_braid',(.34,.145,.063),.9,.31,.08,1400)
 for obj in list(bpy.data.objects):
  if obj.type=='MESH' and (obj.name.startswith('VB02_ROOF_VCB') or obj.name.startswith('VB02_ROOF_HV_busbar') or obj.name.startswith('VB02_ROOF_roof_control_conduit')):bpy.data.objects.remove(obj,do_unlink=True)
 def B(n,c,d,ma='housing',be=.003):return box(P+n,c,d,M[ma],body,C,b=be)
 def CY(n,c,r,d,ma='steel',axis='Z',N=48):return cyl(P+n,c,r,d,M[ma],body,C,axis,N)
 def T(n,pts,r,ma='alloy',N=14):return tube(P+n,pts,r,M[ma],body,C,N=N)
 def bolt_at(n,c,axis='Z',r=.0105):return bolt(P+n,c,r,.010,M['steel'],body,C,axis,True)
 x=7.55;y=-1.15;z=3.752
 # Roof cutout and sloped saddle follow the actual curved shoulder instead of floating a box above it.
 roof=bpy.data.objects.get('Curved_roof_outer')
 cut=[x-.54,x+.54,y-.30,y+.30]
 if roof:
  bm=bmesh.new();bm.from_mesh(roof.data)
  for co,no in [((cut[0],0,0),(1,0,0)),((cut[1],0,0),(1,0,0)),((0,cut[2],0),(0,1,0)),((0,cut[3],0),(0,1,0))]:
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=co,plane_no=no,clear_inner=False,clear_outer=False)
  faces=[f for f in bm.faces if cut[0]+1e-5<f.calc_center_median().x<cut[1]-1e-5 and cut[2]+1e-5<f.calc_center_median().y<cut[3]-1e-5]
  bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY');bm.to_mesh(roof.data);bm.free();roof.data.update()
 profile=[(-1.62,3.13),(-1.59,3.36),(-1.46,3.58),(-1.23,3.73),(-.82,3.8),(0,3.82)]
 def roofz(yy):
  for (a,za),(b,zb) in zip(profile,profile[1:]):
   if a<=yy<=b:return za+(zb-za)*(yy-a)/(b-a)
  return 3.82
 outer=[(cut[0],cut[2],roofz(cut[2])),(cut[1],cut[2],roofz(cut[2])),(cut[1],cut[3],roofz(cut[3])),(cut[0],cut[3],roofz(cut[3]))]
 inner=[(x-.42,y-.213,z),(x+.42,y-.213,z),(x+.42,y+.213,z),(x-.42,y+.213,z)]
 mesh(P+'pressed_roof_mounting_saddle',outer+inner,[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)],M['white'],body,C)
 B('mounting_gasket',(x,y,z-.003),(.858,.443,.012),'rubber',.014)
 B('cast_baseplate',(x,y,z+.004),(.840,.426,.014),'housing',.018)
 B('under_roof_operating_box',(x,y,z-.095),(.800,.324,.178),'housing',.018)
 for xx in [x-.38,x,x+.38]:
  for yy in [y-.184,y+.184]:bolt_at('six_M12_mountings',(xx,yy,z+.018))
 # Two porcelain sections, orange cast mid terminal and orange upper incoming cap.
 CY('lower_flange',(x,y,z+.038),.112,.047,'orange_cast')
 CY('lower_insulator_core',(x,y,z+.143),.077,.192,'porcelain')
 for h in [.070,.105,.140,.175,.210]:
  lathe(P+'lower_porcelain_shed',(x,y,z+h),[(-.010,.077),(-.003,.151),(.007,.154),(.014,.087),(.022,.077)],M['porcelain'],body,C,'Z',64)
 CY('mid_outgoing_casting',(x,y,z+.263),.113,.056,'orange_cast')
 for h in [.240,.282]:ring(P+'mid_casting_flange',(x,y,z+h),.123,.105,.013,M['orange_cast'],body,C,'Z',48)
 CY('upper_insulator_core',(x,y,z+.372),.077,.188,'porcelain')
 for h in [.317,.352,.387,.422]:
  lathe(P+'upper_porcelain_shed',(x,y,z+h),[(-.010,.077),(-.003,.151),(.007,.154),(.014,.087),(.022,.077)],M['porcelain'],body,C,'Z',64)
 CY('top_incoming_casting',(x,y,z+.480),.118,.029,'orange_cast')
 B('top_terminal_lug',(x,y+.135,z+.494),(.114,.130,.008),'orange_cast',.008)
 B('middle_terminal_lug',(x,y+.135,z+.270),(.114,.130,.010),'orange_cast',.008)
 for hh in [.495,.271]:
  for xx in [x-.033,x+.033]:bolt_at('M12_live_terminal',(xx,y+.145,z+hh+.006),r=.0105)
 # Small opposite-side earth pads remain separate from the live terminals.
 for hh in [.270,.493]:
  B('earth_contact_pad',(x,y-.125,z+hh),(.09,.09,.010),'brushed',.004)
  bolt_at('M10_earth_contact',(x,y-.139,z+hh+.007),r=.0085)
 # Open-position earthing arms and their grounded pivot brackets. No live-terminal short.
 for sg,hh in [(-1,.270),(1,.493)]:
  xx=x+sg*.28
  B('earthing_pivot_bracket',(xx,y-.105,z+.061),(.07,.07,.095),'orange_cast',.009)
  CY('earthing_pivot_pin',(xx,y-.105,z+.108),.014,.095,'steel','Y',32)
  beam(P+'open_earth_switch_blade',(xx,y-.105,z+.108),(xx+sg*.060,y-.185,z+hh-.045),.024,.009,M['brushed'],body,C,b=.002)
  for j in [-1,1]:bolt_at('earth_pivot_fixing',(xx+j*.025,y-.105,z+.016),r=.0085)
 # Lifting eyes, service labels, connector and compressed-air fitting on the under-roof case.
 for xx in [x-.31,x+.31]:
  ring(P+'lifting_eye',(xx,y,z+.046),.026,.014,.010,M['steel'],body,C,'Y',40)
  B('lifting_eye_foot',(xx,y,z+.023),(.052,.037,.025),'steel',.005)
 B('identification_plate',(x-.245,y+.083,z+.013),(.18,.079,.003),'brushed',.003)
 B('warning_plate',(x+.252,y+.081,z+.013),(.16,.072,.003),'orange_cast',.003)
 CY('35pin_connector_flange',(x+.410,y-.065,z-.079),.040,.015,'black','X',40)
 ring(P+'35pin_lockring',(x+.421,y-.065,z-.079),.032,.023,.019,M['steel'],body,C,'X',40)
 CY('airline_compression_union',(x+.422,y+.066,z-.084),.018,.036,'steel','X',6)
 T('control_air_hose',[(x+.44,y+.066,z-.084),(x+.51,y+.066,z-.10),(x+.54,y+.15,z-.14)],.007,'rubber')
 # S-curved case bonding strap goes to roof metal, never between live terminals.
 T('ground_bond_braid',bezier_points([(x+.31,y-.19,z+.012),(x+.40,y-.23,z-.012),(x+.49,y-.23,z-.044),(x+.52,y-.21,roofz(y-.21)+.01)],8),.006,'copper')
 bolt_at('roof_ground_bond',(x+.52,y-.21,roofz(y-.21)+.015),r=.0085)
 # Traceable visible electrical path: panto frame terminal -> upper22CBcap;
 # middle22CBterminal -> separate support/bushing path. The vacuum gap is internal.
 base=bpy.data.objects['PANTO_BASE']
 box(P+'panto_output_pad',(-.30,-.45,.245),(.15,.12,.040),M['brushed'],base,C,b=.005,local=True)
 bolt(P+'panto_output_stud',(-.30,-.45,.282),.0105,.015,M['steel'],base,C,'Z',True,True)
 T('incoming_bus',[(9.80,.45,4.10),(9.80,.70,4.13),(8.50,.70,4.17),(7.80,.70,4.11),(7.80,.30,4.20),(7.65,-.45,4.247),(x,y+.16,z+.494)],.012,'alloy')
 T('outgoing_bus',[(x,y+.16,z+.270),(7.40,-.55,4.025),(7.35,.10,4.08),(7.35,.70,4.11),(7.19,.88,4.08),(7.20,1.08,3.80)],.012,'alloy')
 for xx in [7.35,7.80]:
  B('support_terminal_saddle',(xx,.70,4.123),(.11,.09,.018),'brushed',.004)
  for yy in [.672,.728]:bolt_at('bus_clamp_bolt',(xx,yy,4.137),r=.0075)
 CY('roof_bushing_boot',(7.20,1.08,3.807),.060,.085,'rubber')
 for zz in [3.779,3.798,3.817]:ring(P+'bushing_boot_rib',(7.20,1.08,zz),.065,.052,.006,M['rubber'],body,C,'Z',36)
 # Named service interfaces make the intended visual connectivity inspectable.
 for name,loc in [('TOP_INCOMING',(x,y+.16,z+.494)),('MID_OUTGOING',(x,y+.16,z+.270)),('PANTO_OUTPUT',(9.80,.45,4.10)),('ROOF_BUSHING',(7.20,1.08,3.80))]:
  ob=bpy.data.objects.new(P+name,None);C.objects.link(ob);ob.parent=body;ob.location=loc;ob.empty_display_size=.018;ob['role']='Visual electrical interface; not an electrical simulation'
 for name,txt,loc in [('type','22CB',(x-.245,y+.083,z+.016)),('label','HV',(x+.252,y+.081,z+.016))]:
  cu=bpy.data.curves.new(P+name,'FONT');cu.body=txt;cu.align_x='CENTER';cu.size=.026;cu.extrude=.00015;cu.materials.append(M['black']);ob=bpy.data.objects.new(P+name,cu);C.objects.link(ob);ob.parent=body;ob.location=loc
 bpy.context.view_layer.update()
 return {'applied':True,'source':'VB-specific CAMTECH photo and Schneider22CB OEM outline/earthing drawing June2022','tower_above_mount_plate_m':.507,'mount_plate_rail_z_m':z,'under_roof_box':True,'six_M12_base_fixings':True,'live_path':'Panto output to top incoming cap; middle outgoing terminal to separate roof bushing','earth_blades':'Representative open position, never shown bridging live terminals','scope':'Source-led tower/form/connection identity; small hardware and roof saddle are representative, not electrical-operating certification'}
