"""Fine fabricated surfaces, class furniture and end service-room fittings.
Procedural materials remain editable; geometry is original and representative.
"""
import bpy, math, random
from mathutils import Vector

def refine(g,k,c):
 box,mesh,rod,text,material=[g[n] for n in ['box','mesh','rod','text','material']]
 steel,ivory,blue,rubber,white,floor,paint,grey,glass,wood,edge=[g[n] for n in ['steel','ivory','blue','rubber','white','floor','paint','grey','glass','wood','edge']]
 root,body,inter,roof,glasscoll=[g[n] for n in ['root','body','inter','roof','glasscoll']]
 brass=material('Satin_anodised_bronze',(.41,.30,.14),.72,.32)
 ceramic=material('Porcelain_white',(.73,.77,.75),.0,.24)
 linen=material('Cotton_linen',(.78,.79,.74),0,.87)
 red=material('Fire_safety_red',(.43,.014,.013),.12,.38)
 darkblue=material('Upholstery_sewn_panels',(.027,.08,.16) if k!='1A' else (.18,.014,.020),0,.76)
 light=material('Warm_light_diffuser',(.88,.83,.65),0,.35)
 lp=light.node_tree.nodes.get('Principled BSDF');lp.inputs['Emission Color'].default_value=(1,.86,.62,1);lp.inputs['Emission Strength'].default_value=2
 mirror=material('Silvered_mirror',(.86,.89,.90),1,.055)
 labels=material('Engraved_charcoal',(.025,.035,.041),0,.5)
 def noise_surface(mat,scale,strength,detail=2,rough_variation=.10):
  nt=mat.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.name='Fine manufacturing texture';tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=detail
  coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=strength;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');r=p.inputs['Roughness'].default_value;ramp.color_ramp.elements[0].color=(max(.01,r-rough_variation),)*3+(1,);ramp.color_ramp.elements[1].color=(min(1,r+rough_variation),)*3+(1,);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Roughness'])
 for mat,scale,strength in [(paint,100,.00018),(grey,140,.00014),(steel,210,.00012),(ivory,150,.0001),(blue,330,.00065),(darkblue,330,.00055),(linen,580,.00045),(floor,95,.0008),(wood,65,.0001)]:noise_surface(mat,scale,strength)
 # Soft fabric weave uses crossed procedural waves rather than photographic maps.
 for mat in [blue,linen,darkblue]:
  p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=.22;p.inputs['Sheen Roughness'].default_value=.70
 # Four-corner rounded cord or sewn edge, on a plane parallel to XY/XZ/YZ.
 def loop(name,center,w,h,r,plane,mat,radius=.0035):
  pts=[]
  for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for j in range(6):
    a=math.radians(start+90*j/5);u=cx+r*math.cos(a);v=cy+r*math.sin(a)
    q=(u,v,0) if plane=='XY' else ((u,0,v) if plane=='XZ' else (0,u,v));pts.append(tuple(center[i]+q[i] for i in range(3)))
  for a,b in zip(pts,pts[1:]+pts[:1]):rod(name,a,b,radius,mat,6,coll=inter)
 def tube(name,pts,r,mat=steel):
  for a,b in zip(pts,pts[1:]):rod(name,a,b,r,mat,10,coll=inter)
 def lathe(name,loc,profile,mat,segments=40):
  vs=[(loc[0]+rad*math.cos(j*math.tau/segments),loc[1]+rad*math.sin(j*math.tau/segments),loc[2]+z) for rad,z in profile for j in range(segments)]
  fs=[(i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j) for i in range(len(profile)-1) for j in range(segments)]
  fs += [tuple(range(segments-1,-1,-1)),tuple(range((len(profile)-1)*segments,len(profile)*segments))]
  ob=mesh(name,vs,fs,mat,coll=inter)
  for p in ob.data.polygons:p.use_smooth=True
  return ob
 def screw(name,loc,axis='Y',r=.005):
  a=list(loc);b=list(loc);ix={'X':0,'Y':1,'Z':2}[axis];a[ix]-=.002;b[ix]+=.002;rod(name,a,b,r,steel,8,coll=inter)
 def plaque(name,label,loc,w=.16,h=.08,rot=(math.pi/2,0,0)):
  box(name+'_plate',loc,(w,.006,h),ivory,.009,coll=inter)
  text(name+'_print',label,(loc[0],loc[1]-.006,loc[2]-h*.21),h*.43,rot=rot,m=labels,coll=inter)
 # Wall and floor finishing: coved skirting, ceiling panel breaks and inspection hatches.
 for s in [-1,1]:
  box('INTERIOR_coved_skirting',(0,s*1.502,1.382),(19.08,.036,.12),steel,.014,coll=inter)
  box('CEILING_coveline',(0,s*1.395,3.584),(19.1,.045,.028),white,.013,coll=roof)
 for x in [-8.4,-6.6,-4.8,-3.,-1.2,.6,2.4,4.2,6.,7.8]:
  box('CEILING_panel_joint',(x,0,3.593),(.008,2.8,.008),grey,.001,coll=roof)
  for y in [-1.31,1.31]:
   box('CEILING_access_panel',(x,y,3.586),(.39,.22,.016),ivory,.015,coll=roof)
   for dx in [-.16,.16]:rod('CEILING_panel_screw',(x+dx,y,3.573),(x+dx,y,3.581),.004,steel,8,coll=roof)
 # Distinct sewn upholstery: raised edge cord and seat-centre inset panels.
 bpy.context.view_layer.update()
 originals=list(inter.objects)
 for ob in originals:
  n=ob.name
  if n.startswith(('MAIN_LOWER','SIDE_LOWER','FIRST_LOWER','MAIN_UPPER','SIDE_UPPER','FIRST_UPPER','CHAIR_cushion','GS_main_bench','GS_side_bench')):
   x,y,z=ob.location;dx,dy,dz=ob.dimensions
   loop('UPHOLSTERY_edge_piping',(x,y,z+dz*.41),dx-.045,dy-.045,.035,'XY',edge,.003)
   if n.startswith('CHAIR_cushion'):
    box('SEAT_cushion_centre_sewn_panel',(x+.035,y,z+dz*.47),(dx*.66,dy*.76,.012),darkblue,.034,coll=inter)
   if n.startswith(('FIRST_UPPER','MAIN_UPPER','SIDE_UPPER')) and k in ['1A','2A']:
    # Folded bedding stored on upper sleeping berth; daytime benches remain unobstructed.
    yy=y-.48 if dy>1 else y;xx=x if dy>1 else x+.34
    box('UPPER_folded_cotton_sheet',(xx,yy,z+dz*.5+.045),(.42,.49,.068),linen,.042,coll=inter)
    loop('LINEN_hem',(xx,yy,z+dz*.5+.081),.37,.44,.03,'XY',white,.0015)
  if n.startswith(('CHAIR_back','FIRST_backrest','LOWER_BACKREST','MIDDLE_FOLDED','GS_bench_back')):
   x,y,z=ob.location;dx,dy,dz=ob.dimensions
   # Use facing passenger side based on seat/back position; seams are on both sides for folded berths.
   for sx in [-1,1]:
    loop('UPHOLSTERY_back_seam',(x+sx*dx*.51,y,z),dy-.055,dz-.06,.035,'YZ',edge,.0028)
   if n.startswith('CHAIR_back'):
    face=1 if x<0 else -1
    box('CHAIR_lumbar_bolster',(x+face*.057,y,z-.15),(.055,dy*.87,.16),blue,.031,coll=inter)
    # Discrete metal hinge and bolted frame visible beneath upholstered shell.
    for sy in [-1,1]:rod('CHAIR_recline_hinge',(x,y+sy*dy*.46,z-.29),(x,y+sy*(dy*.46+.018),z-.29),.028,steel,16,coll=inter)
  if n.startswith('SEATBACK_tray'):
   x,y,z=ob.location;dx,dy,dz=ob.dimensions;face=1 if x<0 else -1
   box('TRAY_latch',(x-face*.021,y,z+.107),(.018,.085,.022),steel,.006,coll=inter)
   for sy in [-1,1]:rod('TRAY_hinge',(x,y+sy*dy*.38,z-.123),(x,y+sy*(dy*.38+.026),z-.123),.012,steel,12,coll=inter)
  if n.startswith('HEADREST'):
   x,y,z=ob.location;dx,dy,dz=ob.dimensions;face=1 if x<0 else -1
   text('HEADREST_embroidery','IR',(x+face*.07,y,z-.025),.045,rot=(math.pi/2,0,face*math.pi/2),m=blue,coll=inter)
 # Readily visible berth hardware, individual reading lamps, sockets and mesh bottle holders.
 if k in ['1A','2A','3A','SL']:
  for ob in originals:
   if not ob.name.startswith(('MAIN_LOWER','FIRST_LOWER')):continue
   x,y,z=ob.location;face=1 if x<0 else -1
   # The corresponding bay wall supports the plate; not placed in passenger aisle.
   wallx=x+(-.30 if 'MAIN_' in ob.name else -.365)
   box('BERTH_hinge_mount',(wallx,y,2.18),(.045,1.74,.042),steel,.005,coll=inter)
   for yy in [y-.62,y+.62]:
    rod('BERTH_hinge_barrel',(wallx,yy-.045,2.20),(wallx,yy+.045,2.20),.022,steel,16,coll=inter)
    for zz in [2.04,2.34]:box('BERTH_hinge_fixing',(wallx,yy,zz),(.012,.073,.051),steel,.004,coll=inter)
   if k in ['2A','3A','SL']:
    for yy in [y-.77,y+.77]:
     rod('UPPER_berth_support_stay',(x,yy,3.19),(wallx,yy,3.49),.014,steel,12,coll=inter)
   box('PASSENGER_socket_panel',(x,-1.487,2.20),(.16,.018,.115),ivory,.015,coll=inter)
   for dx,dz in [(-.021,0),(.021,0),(0,.031)]:rod('SOCKET_pin_aperture',(x+dx,-1.498,2.20+dz),(x+dx,-1.502,2.20+dz),.006,rubber,10,coll=inter)
   box('SOCKET_switch',(x+.052,-1.504,2.21),(.019,.012,.032),white,.004,coll=inter)
   if k!='SL':
    box('READING_LIGHT_mount',(x,-1.487,2.78),(.10,.02,.08),steel,.014,coll=inter)
    rod('READING_LIGHT_stem',(x,-1.47,2.78),(x,-1.40,2.74),.012,steel,12,coll=inter)
    box('READING_LIGHT_housing',(x,-1.385,2.726),(.105,.07,.041),grey,.015,coll=inter)
    box('READING_LIGHT_lens',(x,-1.380,2.703),(.079,.047,.007),light,.009,coll=inter)
   # Wire bottle cages on low wall, clearly hollow rather than a black rectangular decal.
   bx=x+.12;by=-1.457;bz=1.975
   for zz in [bz-.08,bz+.08]:
    for j in range(12):
     a=j*math.tau/12;b=(j+1)*math.tau/12;rod('BOTTLE_HOLDER_ring',(bx+.043*math.cos(a),by+.043*math.sin(a),zz),(bx+.043*math.cos(b),by+.043*math.sin(b),zz),.0028,steel,6,coll=inter)
   for j in range(6):
    a=j*math.tau/6;rod('BOTTLE_HOLDER_wire',(bx+.043*math.cos(a),by+.043*math.sin(a),bz-.08),(bx+.043*math.cos(a),by+.043*math.sin(a),bz+.08),.0028,steel,6,coll=inter)
 # Class-specific privacy curtains with actual folds, not rectangular strips.
 if k in ['1A','2A','3A','CC']:
  for ob in list(bpy.data.objects):
   if ob.name.startswith('CURTAIN_gathered') or ob.name.startswith('PRIVACY_curtain_gathered'):bpy.data.objects.remove(ob,do_unlink=True)
  def curtain(n,x,y,z,width,height,folds=5):
   vs=[];nx=folds*8;nz=8
   for iz in range(nz+1):
    for ix in range(nx+1):
     u=ix/nx;v=iz/nz;vs.append((x+(u-.5)*width,y+.013*math.sin(u*folds*math.tau)*(1-.12*v),z+(v-.5)*height+.008*math.cos(u*folds*math.tau)*(1-v)))
   fs=[(iz*(nx+1)+ix,iz*(nx+1)+ix+1,(iz+1)*(nx+1)+ix+1,(iz+1)*(nx+1)+ix) for iz in range(nz) for ix in range(nx)]
   ob=mesh(n,vs,fs,blue,coll=inter);md=ob.modifiers.new('Fabric thickness','SOLIDIFY');md.thickness=.002
   for p in ob.data.polygons:p.use_smooth=True
   return ob
  # Window curtains remain gathered, preserving the characteristic large glazed apertures.
  for ob in list(bpy.data.objects):
   if ob.name.startswith('CURTAIN_rail'):
    vs=[ob.matrix_world@v.co for v in ob.data.vertices];x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=sum(v.y for v in vs)/len(vs);w=max(v.x for v in vs)-min(v.x for v in vs)
    for s in [-1,1]:curtain('WINDOW_pleated_curtain',x+s*(w/2-.067),y,2.52,.12,.72,4)
  if k=='2A':
   for j in range(9):
    x=-7.6+j*1.9 if j<8 else 7.93
    curtain('BAY_privacy_curtain',x-.84,.454,2.43,.16,1.99,6)
    for q in range(7):rod('CURTAIN_hanger', (x-.91+q*.024,.451,3.435),(x-.91+q*.024,.451,3.455),.004,steel,8,coll=inter)
 # Vestibules, washrooms and linen room with real fixtures.
 for e in [-1,1]:
  # Electrical cubicle facia, breaker banks, gauges and labelled controls.
  x=e*9.15;y=-.776
  box('ELECTRICAL_panel_recess',(x,y,2.47),(.44,.012,1.16),grey,.015,coll=inter)
  box('ELECTRICAL_door_gasket',(x,y-.009,2.47),(.39,.006,1.10),rubber,.011,coll=inter)
  box('ELECTRICAL_front_panel',(x,y-.014,2.47),(.372,.010,1.082),ivory,.009,coll=inter)
  for row in range(5):
   for col in range(4):
    xx=x-.12+col*.079;zz=2.22+row*.115
    box('BREAKER_base',(xx,y-.026,zz),(.039,.018,.065),rubber,.005,coll=inter)
    box('BREAKER_toggle',(xx,y-.04,zz+.01),(.015,.015,.027),white,.002,coll=inter)
  for off in [-.09,.09]:
   rod('ELECTRICAL_gauge_rim',(x+off,y-.035,2.925),(x+off,y-.046,2.925),.049,steel,24,coll=inter)
   rod('ELECTRICAL_gauge_face',(x+off,y-.046,2.925),(x+off,y-.048,2.925),.043,white,24,coll=inter)
   rod('ELECTRICAL_gauge_needle',(x+off,y-.05,2.925),(x+off+.019,y-.05,2.949),.002,rubber,6,coll=inter)
  text('ELECTRICAL_panel_label','LIGHTS  /  FAN  /  SUPPLY',(x,y-.049,3.025),.025,coll=inter,m=rubber)
  for z in [1.99,3.0]:screw('ELECTRICAL_panel_screw',(x-.155,y-.025,z));screw('ELECTRICAL_panel_screw',(x+.155,y-.025,z))
  rod('ELECTRICAL_cabinet_handle',(x+.177,y-.048,2.04),(x+.177,y-.048,2.17),.008,steel,12,coll=inter)
  # Detailed replacement extinguishers with valve, pressure gauge and black hose.
  ex=e*9.28;ey=-.72
  for ob in list(inter.objects):
   if ob.name.startswith('FIRE_EXTINGUISHER') and abs(ob.location.x-ex)<.1:bpy.data.objects.remove(ob,do_unlink=True)
  lathe('FIRE_EXTINGUISHER_cylinder',(ex,ey,1.72),[(.04,0),(.073,.035),(.074,.40),(.045,.47),(.024,.48)],red,32)
  box('FIRE_EXTINGUISHER_label',(ex,ey-.073,1.94),(.083,.005,.13),white,.006,coll=inter)
  text('FIRE_EXTINGUISHER_label_print','FIRE',(ex,ey-.079,1.955),.025,m=red,coll=inter)
  box('FIRE_EXTINGUISHER_handle',(ex,ey,2.234),(.105,.032,.015),rubber,.006,coll=inter)
  rod('FIRE_EXTINGUISHER_valve',(ex,ey,2.19),(ex,ey,2.237),.014,brass,12,coll=inter)
  tube('FIRE_EXTINGUISHER_hose',[(ex+.02,ey,2.22),(ex+.10,ey,2.16),(ex+.102,ey,1.89)],.009,rubber)
  # Vestibule wall washbasin with genuine bowl and drain, folding tap and mirror.
  bx=e*10.31;by=.66
  ob=lathe('VESTIBULE_washbasin',(bx,by,2.03),[(.025,-.13),(.16,-.075),(.21,0),(.208,.028),(.183,.03),(.161,-.04),(.028,-.108)],ceramic,48);ob.scale.y=.70
  rod('WASHBASIN_drain',(bx,by,1.928),(bx,by,1.934),.023,steel,20,coll=inter)
  tube('WASHBASIN_tap',[(bx,by+.15,2.057),(bx,by+.15,2.24),(bx,by+.07,2.24),(bx,by+.07,2.20)],.011)
  tube('WASHBASIN_trap',[(bx,by,1.926),(bx,by,1.83),(bx+.085,by,1.80),(bx+.085,by,1.90),(bx+.16,by,1.90)],.023)
  box('WASHBASIN_mirror_frame',(e*10.525,.90,2.68),(.023,.50,.65),steel,.014,coll=inter)
  box('WASHBASIN_mirror',(e*10.509,.90,2.68),(.008,.45,.60),mirror,.008,coll=inter)
  for s in [-1,1]:
   tx=e*11.13;ty=s*1.06;linen_room=k=='1A' and e<0 and s<0
   box('SERVICE_floor_pan',(tx,ty,1.343),(1.01,.89,.035),grey,.024,coll=inter)
   if linen_room:
    for z in [1.72,2.16,2.60,3.04]:
     box('LINEN_shelf',(tx,ty,z),(.90,.70,.03),ivory,.008,coll=inter)
     for n in range(3):box('LINEN_folded_stack',(tx-.27+n*.27,ty,z+.07),(.24,.43,.10),linen,.023,coll=inter)
    continue
   # Selected generic modular lavatory fittings; service geometry not a manufacturer installation drawing.
   if e*s>0:
    # Western pedestal with hollow rim and recessed water surface.
    ob=lathe('WC_pedestal',(tx,ty,1.36),[(.145,0),(.13,.18),(.20,.30),(.225,.36),(.23,.40),(.20,.42),(.16,.37),(.10,.31)],ceramic,48);ob.scale.x=1.30;ob.scale.y=.83
    loop('WC_seat_ring',(tx,ty,1.79),.52,.37,.135,'XY',white,.029)
    box('WC_cistern',(tx+e*.33,ty,1.92),(.19,.44,.59),ceramic,.065,coll=inter)
    box('WC_flush_button',(tx+e*.332,ty,2.221),(.055,.083,.01),steel,.017,coll=inter)
   else:
    # Squat stainless tray with a true recessed bowl and raised ribbed foot pads.
    ob=lathe('WC_squat_bowl',(tx,ty,1.385),[(.055,-.11),(.08,-.08),(.16,-.01),(.19,.014),(.195,.028),(.17,.031),(.07,-.066),(.035,-.092)],steel,48);ob.scale.x=1.5;ob.scale.y=.62
    for ss in [-1,1]:
     box('WC_squat_footpad',(tx,ty+ss*.225,1.397),(.40,.14,.024),steel,.025,coll=inter)
     for j in range(9):box('WC_footpad_rib',(tx-.17+j*.042,ty+ss*.225,1.411),(.012,.10,.008),rubber,.003,coll=inter)
    tube('WC_flush_pipe',[(tx+e*.25,ty,1.40),(tx+e*.35,ty,1.45),(tx+e*.35,ty,2.20)],.018)
    box('WC_flush_valve',(tx+e*.35,ty,2.18),(.072,.062,.08),steel,.014,coll=inter)
   # Toilet grabrail, wash jet, tissue, mirror, shelf, exhaust and covered bin.
   tube('WC_grab_rail',[(tx-e*.30,s*1.479,2.08),(tx-e*.30,s*1.437,2.08),(tx+e*.24,s*1.437,2.08),(tx+e*.24,s*1.479,2.08)],.015)
   bx=tx-e*.34;by=ty+s*.25
   tube('WC_bidet_hose',[(bx,by,2.0),(bx-.04,by,1.59),(bx+.04,by,1.49),(bx+.11,by,1.61),(bx+.09,by,1.95)],.008,rubber)
   rod('WC_bidet_handle',(bx+.09,by,1.95),(bx+.09,by,2.045),.017,steel,16,coll=inter)
   box('WC_paper_holder',(tx-e*.31,ty-s*.20,2.23),(.20,.085,.135),steel,.027,coll=inter)
   rod('WC_tissue_roll',(tx-e*.36,ty-s*.20,2.23),(tx-e*.26,ty-s*.20,2.23),.051,linen,24,coll=inter)
   box('WC_waste_bin',(tx+e*.30,ty-s*.25,1.60),(.23,.21,.46),grey,.03,coll=inter)
   box('WC_bin_lid',(tx+e*.30,ty-s*.25,1.84),(.25,.23,.038),steel,.025,coll=inter)
   box('WC_exhaust_grille',(e*11.591,ty,3.21),(.024,.33,.24),grey,.022,coll=inter)
   for j in range(9):box('WC_exhaust_slot',(e*11.575,ty,3.115+j*.023),(.009,.27,.008),rubber,.002,coll=inter)
   box('WC_soap_dispenser',(e*10.607,ty+s*.22,2.55),(.083,.11,.18),white,.03,coll=inter)
   box('WC_door_latch',(e*10.603,ty-s*.26,2.28),(.033,.09,.045),steel,.005,coll=inter)
   text('WC_cleanliness_notice','KEEP CLEAN',(e*10.601,ty,2.89),.047,rot=(math.pi/2,0,e*math.pi/2),m=rubber,coll=inter)
 # Per-variant labels and saloon partition treatment complete the change of accommodation.
 for e in [-1,1]:
  if k!='1A':
   for sy in [-1,1]:box('SALOON_end_partition',(e*8.99,sy*1.04,2.46),(.045,.92,2.26),ivory,.008,coll=inter)
   # True central saloon doorway opening, transom overhead; doors shown recessed open.
   box('SALOON_partition_transom',(e*8.99,0,3.39),(.045,1.16,.37),ivory,.008,coll=inter)
   text('SALOON_class_plaque',c['label'],(e*8.963,0,3.32),.063,rot=(math.pi/2,0,e*math.pi/2),m=rubber,coll=inter)
 root['detail_revision']='02';root['research_basis']='CAMTECH LHB manual class plates plus FIAT monograph, representative fabrication and furnishings'
 root['native_TF3_conversion']=False;root['runtime_tested']=False
