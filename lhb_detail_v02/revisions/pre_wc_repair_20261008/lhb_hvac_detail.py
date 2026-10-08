"""Reference-informed LHB roof-mounted package unit.
CAMTECH chapter6, figs6.9–6.11: offset twin condenser fans, adjacent four-panel
intake bank, six maintenance covers, mounting brackets, conduits and two junction
boxes. Fine dimensions and fan blade profiles are representative, not OEM CAD.
"""
import bpy,math

def build(g,e):
 box,mesh,rod,text,material=[g[n] for n in ['box','mesh','rod','text','material']]
 body,roof=g['body'],g['roof'];rubber=g['rubber'];steel=g['steel']
 cover=material('RMPU_satin_galvanised_cover',(.245,.267,.278),.62,.43)
 blade=material('RMPU_fan_dark_alloy',(.095,.112,.120),.64,.39)
 grille=material('RMPU_stainless_wire_grille',(.25,.28,.30),.78,.32)
 shadow=material('RMPU_recess_and_coil_shadow',(.012,.016,.018),.15,.73)
 panel=material('RMPU_service_panel',(.26,.28,.29),.57,.45)
 copper=material('RMPU_copper_bond',(.24,.12,.047),.70,.38)
 junction=material('RMPU_electrical_junction_blue',(.027,.085,.19),.15,.43)
 plate=material('RMPU_identification_plate',(.46,.49,.50),.70,.29)
 for mat in [cover,panel]:
  nt=mat.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=145;tex.inputs['Detail'].default_value=2
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00008;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 def B(n,loc,dim,m,bevel=0):return box(n,(e*loc[0],e*loc[1],loc[2]),dim,m,bevel,coll=roof)
 def R(n,a,b,r,m=grille,N=12):return rod(n,(e*a[0],e*a[1],a[2]),(e*b[0],e*b[1],b[2]),r,m,N,coll=roof)
 TOP=3.950;BOTTOM=3.715;WELL=3.8075;fan_y=-.50
 package=B('AC_ROOF_end_package',(9.82,0,(TOP+BOTTOM)/2),(2.55,2.44,TOP-BOTTOM),cover,.025)
 bpy.context.view_layer.objects.active=package
 for modifier in list(package.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
 # One disconnected but closed cutter combines the two circular fan wells and
 # four rectangular intake wells. Cover geometry remains a closed solid.
 cv=[];cf=[];N=64
 for xx in [9.30,10.17]:
  base=len(cv)
  cv.extend([(e*(xx+.394*math.cos(j*math.tau/N)),e*(fan_y+.394*math.sin(j*math.tau/N)),z) for z in [WELL,4.06] for j in range(N)])
  cf.extend([tuple(base+j for j in range(N-1,-1,-1)),tuple(base+j for j in range(N,2*N))])
  cf.extend([(base+j,base+(j+1)%N,base+(j+1)%N+N,base+j+N) for j in range(N)])
 for xx in [9.08+j*.43 for j in range(4)]:
  base=len(cv);cv.extend([(e*(xx+dx),e*(.62+dy),z) for z in [WELL,4.06] for dx,dy in [(-.183,-.315),(.183,-.315),(.183,.315),(-.183,.315)]])
  cf.extend([tuple(base+j for j in face) for face in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 cutter=mesh('TEMP_RMPU_six_apertures',cv,cf,shadow,coll=roof)
 modifier=package.modifiers.new('Actual condenser and intake recesses','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
 bpy.context.view_layer.objects.active=package;bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
 # Six individually readable maintenance covers: two banks of three, without
 # an invented blanket bolt pattern. Fine seams are flush with the top casing.
 for xx in [9.735,10.605]:R('RMPU_maintenance_cover_joint',(xx,-1.188,TOP+.001),(xx,1.188,TOP+.001),.0016,shadow,8)
 R('RMPU_maintenance_cover_joint',(8.575,.10,TOP+.001),(11.065,.10,TOP+.001),.0016,shadow,8)
 for sy in [-1,1]:
  R('RMPU_casing_fold',(8.575,sy*1.19,TOP-.003),(11.065,sy*1.19,TOP-.003),.0035,grille,10)
  B('RMPU_service_end_cover',(10.845,sy*.59,TOP+.001),(.448,1.10,.003),panel)
 for xx in [9.30,10.17]:
  R('AC_condenser_well',(xx,fan_y,WELL+.002),(xx,fan_y,WELL+.006),.389,shadow,64)
  R('AC_condenser_motor',(xx,fan_y,WELL+.012),(xx,fan_y,TOP-.018),.074,blade,32)
  for j in range(6):
   a=j*math.tau/6;ca,sa=math.cos(a),math.sin(a)
   profile=[(.075,-.027),(.15,-.047),(.30,-.027),(.354,.018),(.327,.060),(.17,.048),(.075,.028)]
   vs=[]
   for dz in [-.004,.004]:
    for u,v in profile:
     z=TOP-.030+v*.30+dz;vs.append((e*(xx+u*ca-v*sa),e*(fan_y+u*sa+v*ca),z))
   n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(q,(q+1)%n,(q+1)%n+n,q+n) for q in range(n)]
   mesh('AC_fan_blade',vs,fs,blade,coll=roof)
  for rad in [.11,.19,.27,.385]:
   for j in range(64):
    a=j*math.tau/64;b=(j+1)*math.tau/64;R('AC_condenser_grille_ring',(xx+rad*math.cos(a),fan_y+rad*math.sin(a),TOP+.034),(xx+rad*math.cos(b),fan_y+rad*math.sin(b),TOP+.034),.0024,grille,8)
  for j in range(12):
   a=j*math.tau/12;R('AC_condenser_guard_spoke',(xx+.075*math.cos(a),fan_y+.075*math.sin(a),TOP+.035),(xx+.385*math.cos(a),fan_y+.385*math.sin(a),TOP+.035),.0030,grille,10)
 # The reference has a conspicuous wire-mesh bank adjacent to the fans, not
 # tiny black decorative squares around the side of an otherwise solid box.
 for xx in [9.08+j*.43 for j in range(4)]:
  B('RMPU_condenser_intake_shadow',(xx,.62,WELL+.006),(.359,.622,.008),shadow)
  for dx in [-.197,.197]:B('RMPU_intake_frame',(xx+dx,.62,TOP+.005),(.018,.706,.010),grille,.002)
  for dy in [-.344,.344]:B('RMPU_intake_frame',(xx,.62+dy,TOP+.005),(.412,.018,.010),grille,.002)
  for j in range(15):
   x=xx-.177+j*.354/14;R('RMPU_intake_mesh_wire',(x,.304,TOP+.008),(x,.936,TOP+.008),.0017,grille,6)
  for j in range(25):
   y=.307+j*.626/24;R('RMPU_intake_mesh_wire',(xx-.179,y,TOP+.011),(xx+.179,y,TOP+.011),.0017,grille,6)
  # A dark fin core is visible below the grille, at a distinct physical depth.
  for j in range(16):B('RMPU_condenser_fin',(xx-.165+j*.022,.62,WELL+.047),(.003,.59,.064),blade)
 # Support channels and paired electrical boxes follow Fig6.10's component
 # relationships. Bracket, gland and conduit dimensions remain representative.
 for sy in [-1,1]:
  B('RMPU_mounting_channel',(9.82,sy*1.245,3.730),(2.43,.080,.030),steel,.004)
  for xx in [8.70,10.94]:
   B('RMPU_mounting_bracket',(xx,sy*1.240,3.711),(.15,.15,.012),steel,.003)
   B('RMPU_vibration_isolator',(xx,sy*1.200,3.710),(.095,.055,.010),rubber,.004)
  B('RMPU_electrical_junction_box',(10.86,sy*1.285,3.786),(.20,.13,.142),junction,.011)
  B('RMPU_junction_box_lid',(10.86,sy*1.285,3.860),(.208,.139,.009),cover,.002)
  pts=[(10.77,sy*1.285,3.799),(10.62,sy*1.307,3.781),(10.42,sy*1.307,3.763),(10.32,sy*1.185,3.752)]
  for a,b in zip(pts,pts[1:]):R('RMPU_flexible_electrical_conduit',a,b,.015,rubber,16)
  R('RMPU_conduit_gland',(10.755,sy*1.285,3.799),(10.79,sy*1.285,3.799),.026,steel,12)
  R('RMPU_casing_gland',(10.32,sy*1.185,3.752),(10.32,sy*1.245,3.752),.024,steel,12)
  R('RMPU_roof_feed_gland',(10.86,sy*1.285,3.685),(10.86,sy*1.285,3.728),.018,steel,12)
  R('RMPU_earthing_bond',(10.86,sy*1.20,3.740),(10.64,sy*1.205,3.715),.004,copper,10)
 B('RMPU_editable_identification_plate',(10.845,-.59,TOP+.006),(.29,.15,.006),plate,.001)
 text('RMPU_unit_identification','RMPU  '+('1' if e>0 else '2'),(e*10.845,e*(-.625),TOP+.011),.041,rot=(0,0,0 if e>0 else math.pi),m=shadow,coll=roof)
 package['reference']='CAMTECH LHB manual chapter6 figs6.9–6.11; offset twin fans, four mesh intakes, six maintenance covers, mounting and electrical components'
 package['fan_bank_y_m']=e*fan_y;package['condenser_well_floor_z_m']=WELL;package['cover_top_z_m']=TOP;package['maintenance_cover_count']=6
 package['interpretation']='Fine dimensions, fastener omission, fan blade profile and bracket positions are representative, not certified OEM data'
 return package
