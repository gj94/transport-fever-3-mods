import bpy, math, os, json
from mathutils import Vector, Matrix
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
asset=bpy.data.collections.new('LHB_3A_PROTOTYPE'); scene.collection.children.link(asset)
studio=bpy.data.collections.new('PRESENTATION_ONLY'); scene.collection.children.link(studio)
def move(o,col=asset):
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o)
 return o
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
red=mat('LHB vermilion red enamel',(.48,.027,.018),.28,.34);grey=mat('Warm grey lower band',(.43,.46,.47),.35,.43);roofmat=mat('Aluminium roof',(.49,.52,.54),.65,.36);black=mat('Rubber and gangway',(.023,.027,.03),0,.64);frame=mat('FIAT bogie grey',(.19,.23,.24),.65,.43);steel=mat('Machined stainless steel',(.49,.54,.57),.85,.25);dark=mat('Undercarriage charcoal',(.058,.07,.075),.6,.5);yellow=mat('Spring inspection yellow',(.64,.43,.03),.3,.5);label=mat('Warm yellow lettering',(.95,.8,.32),.2,.36);cream=mat('Interior laminate',(.64,.61,.51),.1,.65);blue=mat('Blue vinyl berths',(.055,.15,.25),.02,.48);glass=mat('Sealed smoked green glazing',(.025,.09,.11),.35,.15);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.35
root=bpy.data.objects.new('LHB_3A_ROOT_metres',None);asset.objects.link(root)
root['asset_status']='Measured visual prototype; not game-ready';root['body_length_m']=23.54;root['gauge_m']=1.676;root['height_assumption_m']=4.25
body=bpy.data.objects.new('BODY_PIVOT',None);asset.objects.link(body);body.parent=root
parent=body

def finish(o,n,m,par=None):
 o.name=n;move(o);o.parent=par if par else parent
 if m:o.data.materials.append(m)
 return o
def cube(n,loc,dim,m,bevel=.0,par=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m,par)
 if bevel: mod=o.modifiers.new('Fabricated edge radius','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,depth,m,axis='Z',par=None,vertices=40):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 if axis=='X':o.rotation_euler[1]=math.pi/2
 finish(o,n,m,par)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('Metal edge','BEVEL');mod.width=.009;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def mesh(n,v,f,m,par=None):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);asset.objects.link(o);o.parent=par if par else parent;d.materials.append(m);return o
def pipe(n,points,r,m,par=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for a,b in zip(sp.points,points):a.co=(*b,1)
 o=bpy.data.objects.new(n,cu);asset.objects.link(o);o.parent=par if par else parent;cu.materials.append(m);return o
def ring(n,x,y,z,w,h,r,border,m,par=None):
 def loop(w,h,r):
  pts=[]
  for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for i in range(9):
    a=math.radians(start+i*90/8);pts.append((x+cx+r*math.cos(a),y,z+cz+r*math.sin(a)))
  return pts
 a=loop(w,h,r);b=loop(w-2*border,h-2*border,max(.02,r-border));N=len(a);return mesh(n,a+b,[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m,par)
def text(n,s,loc,size,m,side=-1):
 cu=bpy.data.curves.new(n,'FONT');cu.body=s;cu.size=size;cu.align_x='CENTER';cu.extrude=.0008
 o=bpy.data.objects.new(n,cu);asset.objects.link(o);o.parent=body;o.location=loc;o.rotation_euler=(math.pi/2,0,0) if side==-1 else (math.pi/2,0,math.pi);cu.materials.append(m);return o
# structural solebars and interior floor
cube('Floor_sandwich',(0,0,1.255),(23.54,3.12,.096),dark,.02)
cube('Interior_floor',(0,0,1.31),(23.25,3.04,.035),cream)
for s in [-1,1]:
 cube('Continuous_solebar',(0,s*1.42,1.11),(23.5,.13,.25),dark,.025)
 cube('Grey_lower_body',(0,s*1.585,1.555),(23.54,.07,.55),grey,.025)
 cube('Red_sill_band',(0,s*1.585,1.955),(19.0,.07,.25),red)
 cube('Red_upper_fascia',(0,s*1.585,3.265),(23.54,.07,.69),red)
 # Actual open window bay walls; no opaque block behind glass
 windows=[-7.4+i*1.85 for i in range(9)]
 edges=[-9.5]+[a for x in windows for a in [x-.62,x+.62]]+[9.5]
 for i in range(0,len(edges)-1,2):
  a,b=edges[i:i+2];cube('Window_band_pillar',((a+b)/2,s*1.585,2.50),(b-a,.07,.84),red)
 for i,x in enumerate(windows):
  ring('Window_Rubber_Seal_%s_%02d'%(s,i),x,s*1.627,2.5,1.29,.93,.16,.065,black)
  ring('Window_Aluminium_Rebate',x,s*1.63,2.5,1.205,.845,.115,.018,steel)
  cube('Window_glass_%s_%02d'%(s,i),(x,s*1.603,2.5),(1.16,.018,.80),glass,.10)
  text('Berth_range',str(i*8+1)+'-'+str(i*8+8),(x,s*1.632,3.055),.068,label,s)
  if i in [1,7]:text('Emergency_window','EMERGENCY WINDOW',(x,s*1.631,1.995),.052,label,s)
 # vestibule doors and toilet side spaces
 for end in [-1,1]:
  x=end*10.05
  cube('Door_recess',(x,s*1.575,2.40),(1.05,.08,2.10),black,.025)
  dp=bpy.data.objects.new('DOOR_%s_%s_PIVOT'%(end,s),None);asset.objects.link(dp);dp.parent=body;dp.location=(x-.45,s*1.61,1.39)
  ob=cube('Door_leaf',(x,s*1.616,2.39),(.91,.055,1.98),red,.035);ob.parent=dp;ob.matrix_parent_inverse=Matrix.Identity(4) # corrected below by preserving world at update
  # parent transform use explicit local placement
  ob.location=(.45,0,1.0)
  # small sealed door pane black backing and green pane, parented with matrix world preserve later unnecessary
  ring('Door_window_seal',x,s*1.652,2.68,.42,.98,.16,.052,black)
  cube('Door_window',(x,s*1.646,2.68),(.32,.014,.88),glass,.12)
  for dx in [-.60,.60]:
   pipe('Door_stainless_grab',[(x+dx,s*1.64,1.66),(x+dx,s*1.66,1.74),(x+dx,s*1.66,3.11),(x+dx,s*1.64,3.17)],.021,steel)
  cube('Door_handle',(x+.32,s*1.665,2.18),(.13,.035,.028),steel,.015)
  for zz,yy in [(.48,1.43),(.75,1.40),(1.03,1.37)]:
   cube('Serrated_entry_tread',(x,s*yy,zz),(.98,.39,.047),steel,.009)
   for k in range(5):cube('Tread_antislip',(x,s*(yy-.16+k*.065),zz+.028),(.96,.014,.009),dark)
  for dx in [-.48,.48]:pipe('Step_stringer',[(x+dx,s*1.64,.44),(x+dx,s*1.64,.76),(x+dx,s*1.61,1.06),(x+dx,s*1.55,1.36)],.023,steel)
  cube('Toilet_end_side',(end*11.16,s*1.594,2.40),(1.22,.07,2.38),grey,.022)
  ring('Toilet_frosted_window_seal',end*11.08,s*1.629,2.95,.47,.56,.09,.035,black)
  cube('Toilet_frosted_glass',(end*11.08,s*1.631,2.95),(.40,.015,.49),mat('ObscureGlass_%s%s'%(s,end),(.46,.55,.55),.1,.4),.06)
  text('Entry_sign','ENTRY',(x,s*1.64,3.49),.07,label,s)
 text('Class_label','AC THREE TIER',(4.0 if s==-1 else -4.0,s*1.634,3.35),.19,label,s)
 text('Class_identifier','3A',(-8.55 if s==-1 else 8.55,s*1.634,3.31),.18,label,s)
 cube('Blank_route_board',(0,s*1.636,3.37),(1.62,.03,.17),label,.008)
 text('Route_board_text','INDIAN RAILWAYS',(0,s*1.657,3.325),.075,dark,s)
 cube('Destination_clip',(1.1,s*1.645,2.9),(.16,.025,.21),label,.006)
 text('Capacity_stencil','72 BERTHS',(8.7,s*1.635,1.55),.065,dark,s)
# arched roof, end taper, fluted central aluminium
N=48;v=[]
for x,h in [(-11.77,.37),(-11.45,.42),(-9.,.42),(-8.7,.69),(8.7,.69),(9.,.42),(11.45,.42),(11.77,.37)]:
 for i in range(N+1):
  t=math.pi*i/N;v.append((x,1.62*math.cos(t),3.56+h*math.sin(t)))
f=[]
for j in range(7):
 for i in range(N):a=j*(N+1)+i;f.append((a,a+1,a+1+N+1,a+N+1))
o=mesh('Arched_LHB_roof_4250mm',v,f,roofmat)
for p in o.data.polygons:p.use_smooth=True
for end in [-1,1]:
 vv=[(end*11.773,0,3.56)]+[(end*11.773,1.62*math.cos(math.pi*i/N),3.56+.37*math.sin(math.pi*i/N)) for i in range(N+1)]
 mesh('End_roof_cap',vv,[(0,i,i+1) for i in range(1,N+1)],grey)
for yy in [-.96,-.84,-.72,-.60,-.48,-.36,-.24,-.12,0,.12,.24,.36,.48,.60,.72,.84,.96]:
 zz=3.56+.69*math.sqrt(1-(yy/1.62)**2);pipe('Roof_longitudinal_fluting',[(-8.9,yy,zz+.009),(8.9,yy,zz+.009)],.008,roofmat)
# roof packaged AC units low-profile at both ends
for end in [-1,1]:
 cube('Roof_AC_housing',(end*9.68,0,3.99),(2.00,1.42,.37),roofmat,.10)
 cube('AC_service_cover',(end*9.68,0,4.18),(1.62,1.22,.045),grey,.06)
 for side in [-1,1]:
  cube('Condenser_dark_grille',(end*9.68,side*.722,4.00),(1.5,.025,.19),dark,.01)
  for i in range(24):cube('AC_vertical_louvre',(end*9.68-.71+i*.061,side*.741,4.0),(.025,.025,.21),steel,.005)
# end walls, gangway bellows and CBC couplers
for end in [-1,1]:
 for yy in [-1.10,1.10]:cube('Endwall_outer',(end*11.72,yy,2.45),(.10,1.03,2.39),grey,.04)
 cube('Endwall_header',(end*11.72,0,3.51),(.1,1.25,.29),grey,.02)
 cube('Vestibule_dark_recess',(end*11.78,0,2.40),(.04,1.18,2.12),black,.04)
 for i in range(6):
  xx=end*(11.79+i*.025)
  for yy in [-.66,.66]:cube('Gangway_accordion_rib',(xx,yy,2.38),(.021,.095,2.28),black,.025)
  cube('Gangway_top_rib',(xx,0,3.50),(.021,1.4,.095),black,.025)
 cube('Gangway_threshold',(end*11.86,0,1.31),(.27,1.3,.06),steel,.01)
 cube('CBC_draft_shank',(end*11.64,0,.99),(.56,.18,.19),dark,.02)
 cube('CBC_knuckle_head',(end*11.91,0,.99),(.18,.37,.30),frame,.055)
 cube('CBC_knuckle_jaw',(end*11.99,.12,1.00),(.02,.16,.19),dark,.015)
 for side in [-1,1]:
  pipe('Brake_hose',[(end*11.78,side*.38,1.13),(end*11.89,side*.4,.88),(end*11.9,side*.56,.74),(end*11.80,side*.68,.84)],.029,black)
  cyl('Brake_pipe_cock',(end*11.8,side*.38,1.13),.05,.11,steel,'Y')
  cyl('Tail_lamp_mount',(end*11.785,side*1.15,2.18),.065,.018,dark,'X')
# underframe equipment with opening doors, louvres, mounts
for x,w in [(-4.18,1.7),(-1.8,1.45),(2.0,2.5),(4.55,1.35)]:
 for s in [-1,1]:
  cube('Underframe_electrical_cabinet',(x,s*.85,.85),(w,.75,.64),dark,.035)
  cube('Cabinet_front',(x,s*1.24,.85),(w-.06,.035,.56),grey,.012)
  for z in [.65,1.05]:
   for dx in [-w*.36,w*.36]:cube('Cabinet_hinge',(x+dx,s*1.265,z),(.06,.025,.045),steel,.006)
  for j in range(8):cube('Cabinet_vent',(x,s*1.267,.70+j*.038),(w*.62,.016,.012),dark)
for x in [-.3,.60]:
 cyl('Underfloor_air_reservoir',(x,0,.76),.31,1.86,frame,'Y')
 for y in [-.58,.58]:
  cyl('Reservoir_strap',(x,y,.76),.323,.05,steel,'Y')
for x in [-10.9,10.9]:
 cube('Bio_toilet_tank',(x,0,.80),(1.25,1.34,.60),dark,.12)
 pipe('Wastewater_pipe',[(x,.6,1.25),(x,.6,.83),(x+.48,.6,.61)],.041,steel)
for y in [-.28,.28]:pipe('Continuous_brake_pipe',[(-11.72,y,1.09),(11.72,y,1.09)],.016,steel)
# FIAT bogies with correct pivots and wheelbase
for b,bx in enumerate([-7.45,7.45]):
 bog=bpy.data.objects.new('BOGIE_%d_PIVOT_Z'%b,None);asset.objects.link(bog);bog.parent=root;bog.location=(bx,0,.4575);bog['wheelbase_m']=2.56
 def pb(o):
  # created in world coordinates -> children relative to bogie
  o.parent=bog;o.location-=Vector((bx,0,.4575));return o
 for s in [-1,1]:
  # silhouette FIAT fabricated dropped side frame
  pts=[(bx-1.54,s*1.11,.69),(bx-1.24,s*1.11,.82),(bx-.66,s*1.11,.57),(bx+.66,s*1.11,.57),(bx+1.24,s*1.11,.82),(bx+1.54,s*1.11,.69)]
  pb(pipe('FIAT_swept_sideframe',pts,.12,frame))
  pb(cube('FIAT_centre_beam',(bx,s*1.11,.68),(1.65,.18,.25),frame,.06))
  for dx in [-.50,.50]:
   pb(cyl('Secondary_spring_base',(bx+dx,s*1.04,.91),.22,.065,steel))
   coil=[]
   for i in range(121):
    t=i/120;coil.append((bx+dx+.175*math.cos(t*10*math.pi),s*1.04+.175*math.sin(t*10*math.pi),.94+t*.29))
   pb(pipe('Secondary_coil_spring',coil,.031,dark));pb(cyl('Spring_yellow_mark',(bx+dx,s*1.04,1.08),.182,.038,yellow))
  pb(pipe('Yaw_damper',[(bx-.94,s*1.32,.64),(bx-.37,s*1.32,.94)],.055,steel))
  pb(pipe('Damper_piston',[(bx-.37,s*1.32,.94),(bx-.13,s*1.32,1.05)],.029,steel))
 for ax,dx in enumerate([-1.28,1.28]):
  xp=bx+dx
  axle=bpy.data.objects.new('AXLE_%d_%d_ROTATE_Y'%(b,ax),None);asset.objects.link(axle);axle.parent=bog;axle.location=(dx,0,0);axle['rotation_axis']='Y'
  def pa(o):o.parent=axle;o.location-=Vector((xp,0,.4575));return o
  pa(cyl('Axle_shaft',(xp,0,.4575),.09,2.20,steel,'Y'))
  for s in [-1,1]:
   pa(cyl('Wheel_tread_915mm',(xp,s*.893,.4575),.4575,.132,steel,'Y',vertices=64))
   pa(cyl('Wheel_web',(xp,s*.967,.4575),.365,.025,dark,'Y',vertices=64))
   pa(cyl('Wheel_hub',(xp,s*.993,.4575),.15,.10,steel,'Y'))
   pa(cyl('Inner_flange',(xp,s*.820,.4575),.482,.025,dark,'Y',vertices=64))
   pb(cube('Axlebox',(xp,s*1.13,.49),(.29,.24,.28),frame,.075));pb(cyl('Bearing_cap',(xp,s*1.27,.49),.10,.04,steel,'Y'))
   for dd in [-.16,.16]:
    coil=[]
    for i in range(65):
     t=i/64;coil.append((xp+dd+.083*math.cos(t*8*math.pi),s*1.04+.083*math.sin(t*8*math.pi),.66+t*.22))
    pb(pipe('Primary_coil',coil,.016,dark))
  for yy in [-.53,0,.53]:
   pa(cyl('Axle_brake_disc',(xp,yy,.4575),.30,.075,steel,'Y'))
   pb(cube('Disc_brake_caliper',(xp+.23,yy,.61),(.20,.15,.23),frame,.04))
 for dx in [-.5,.5]:pb(cube('Bogie_crossmember',(bx+dx,0,.69),(.17,2.15,.18),frame,.025))
# simplified 72 berth interior: nine bays each six transverse plus two longitudinal
for i,x in enumerate([-7.4+j*1.85 for j in range(9)]):
 for off in [-.60,.60]:
  for z in [1.79,2.50,3.21]:
   cube('Main_berth_%d'%i,(x+off,-.45,z),(.60,1.84,.105),blue,.055)
   cube('Berth_frame',(x+off,-.45,z-.067),(.64,1.89,.028),steel,.009)
 for z in [1.79,3.13]:cube('Side_berth_%d'%i,(x,1.18,z),(1.70,.62,.12),blue,.055)
 for zz in [2.02,2.29,2.58,2.87,3.15]:pipe('Berth_ladder_rung',[(x-.70,.48,zz),(x-.36,.48,zz)],.013,steel)
 for dx in [-.70,-.36]:pipe('Berth_ladder_upright',[(x+dx,.48,1.37),(x+dx,.48,3.37)],.014,steel)
 cube('Bay_partition',(x+.89,-.40,2.45),(.035,1.89,2.25),cream,.01)
# display studio with broad gauge track, not exported
parent=None
for y in [-.873,.873]:
 o=cube('DISPLAY_rail',(0,y,-.052),(29,.07,.104),steel,.006);move(o,studio);o.parent=None
 o=cube('DISPLAY_rail_web',(0,y,-.12),(29,.025,.09),dark);move(o,studio);o.parent=None
for x in [i*.65 for i in range(-22,23)]:
 o=cube('DISPLAY_sleeper',(x,0,-.24),(.25,2.65,.15),mat('Sleeper_%s'%x,(.23,.24,.23),0,.8),.03);move(o,studio);o.parent=None
floor=mat('Studio_floor',(.11,.14,.17),0,.78)
o=cube('DISPLAY_ground',(0,0,-.37),(2000,2000,.1),floor);move(o,studio);o.parent=None
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.40,.50,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,loc,power,size in [('Large_softbox',(-4,-8,14),2600,11),('Roof_rim',(6,7,10),3000,9),('End_fill',(-15,-1,6),1000,7)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.8))-o.location).to_track_quat('-Z','Y').to_euler();move(o,studio)
bpy.ops.object.camera_add(location=(22,-29,12));cam=bpy.context.object;cam.name='Three_quarter_camera';cam.rotation_euler=(Vector((0,0,1.75))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=28;cam.data.clip_end=10000;scene.camera=cam;move(cam,studio)
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
# ensure export geometry is meshes with preserved hierarchy, retain editable bevels in blend
bpy.ops.object.select_all(action='DESELECT')
for o in asset.objects:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=P+'/LHB_3A_prototype.blend')
bpy.ops.export_scene.fbx(filepath=P+'/LHB_3A_prototype.fbx',use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False)
scene.render.filepath=P+'/LHB_3A_preview.png';bpy.ops.render.render(write_still=True)
cam.location=(0,-32,3.8);cam.rotation_euler=(Vector((0,0,2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=26
scene.render.resolution_y=520;scene.render.filepath=P+'/LHB_3A_side.png';bpy.ops.render.render(write_still=True)
print('LHB_COMPLETE',len(asset.objects))
