import bpy, math, os,json
from mathutils import Vector
P=os.path.dirname(os.path.abspath(__file__))
SOURCE=os.environ.get('LHB_SOURCE',os.path.join(P,'..','..','lhb','LHB_3A_prototype.blend'))
bpy.ops.wm.open_mainfile(filepath=SOURCE)
sc=bpy.context.scene; asset=bpy.data.collections['LHB_3A_PROTOTYPE']; body=bpy.data.objects['BODY_PIVOT']; root=bpy.data.objects['LHB_3A_ROOT_metres']; studio=bpy.data.collections['PRESENTATION_ONLY']
for o in list(asset.objects):
 if o.name.startswith(('Main_berth','Side_berth','Berth_frame','Berth_ladder','Bay_partition','Interior_floor')):bpy.data.objects.remove(o,do_unlink=True)
inter=bpy.data.collections.new('INTERIOR_V02_DAY_CONFIGURATION');sc.collection.children.link(inter)
locators=bpy.data.collections.new('PASSENGER_LOCATORS_REFERENCE_ONLY');sc.collection.children.link(locators)
def mat(n,c,rough=.5,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
ivory=mat('V02 warm FRP panels',(.62,.64,.61));blue=mat('V02 blue vinyl upholstery',(.028,.115,.23),.47);edge=mat('V02 vinyl seam',(.017,.049,.105));floor=mat('V02 blue grey nonslip floor',(.115,.18,.22),.8);steel=mat('V02 satin stainless',(.44,.49,.52),.3,.8);rubber=mat('V02 dark gaskets',(.025,.035,.04));white=mat('V02 light diffuser',(.8,.84,.81),.4);wood=mat('V02 pale table laminate',(.49,.52,.49));vent=mat('V02 vent shadow',(.035,.045,.05))
# Subtle procedural nonslip flooring, no photographic textures.
p=floor.node_tree.nodes.get('Principled BSDF');n=floor.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=180;b=floor.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.002;floor.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);floor.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);inter.objects.link(o);o.parent=body;d.materials.append(m);return o
def box(n,loc,dim,m,bevel=0):
 x,y,z=[q/2 for q in dim];v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)];o=mesh(n,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m);o.location=loc
 if bevel:md=o.modifiers.new('Small fabricated edge','BEVEL');md.width=bevel;md.segments=2
 return o
def rod(n,a,b,r=.012,m=steel,N=8):
 a=Vector(a);b=Vector(b);d=b-a;u=d.normalized().cross(Vector((0,0,1)))
 if u.length<.1:u=d.normalized().cross(Vector((0,1,0)))
 u.normalize();v=d.normalized().cross(u);vs=[tuple(c+r*(u*math.cos(i*2*math.pi/N)+v*math.sin(i*2*math.pi/N))) for c in [a,b] for i in range(N)];return mesh(n,vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m)
def label(n,s,loc,rot,size=.055):
 d=bpy.data.curves.new(n,'FONT');d.body=s;d.size=size;d.align_x='CENTER';d.extrude=0;o=bpy.data.objects.new(n,d);inter.objects.link(o);o.parent=body;o.location=loc;o.rotation_euler=rot;d.materials.append(rubber)
def seat(n,loc,yaw):
 o=bpy.data.objects.new(n,None);locators.objects.link(o);o.parent=body;o.location=loc;o.rotation_euler.z=yaw;o.empty_display_type='ARROWS';o.empty_display_size=.12;o['purpose']='Seated pelvis reference above cushion; +X facing. Not an engine seat configuration.';return o
box('V02_Floor',(0,0,1.329),(23.25,3.08,.022),floor)
# Window reveals leave actual light/visibility paths; wall panels never cross apertures.
for s in [-1,1]:
 box('V02_Wall_sill',(0,s*1.537,1.707),(19.0,.035,.71),ivory)
 box('V02_Wall_header',(0,s*1.537,3.265),(19.0,.035,.69),ivory)
 for i,x in enumerate([-7.4+j*1.85 for j in range(9)]):
  for dx in [-.615,.615]:box('V02_Window_vertical_reveal',(x+dx,s*1.56,2.5),(.042,.115,.855),ivory,.015)
  for z in [2.075,2.925]:box('V02_Window_horizontal_reveal',(x,s*1.56,z),(1.25,.115,.035),ivory,.012)
  box('V02_Window_pillar',(x+.925,s*1.537,2.5),(.60,.035,.84),ivory)
  rod('V02_Curtain_track',(x-.60,s*1.48,2.94),(x+.60,s*1.48,2.94),.009)
  # narrow gathered curtain at edge does not cover pane
  for q in range(4):box('V02_Gathered_window_curtain',(x-.54+q*.025,s*(1.485+(.014 if q%2 else 0)),2.52),(.03,.035,.75),blue,.007)
 box('V02_Skirting',(0,s*1.511,1.40),(19,.018,.11),steel)
# side aisle runs along +Y, main berths across coach at -Y.
xs=[-7.4+j*1.85 for j in range(9)]
for i,x in enumerate(xs):
 for e in [-1,1]:
  xx=x+e*.61
  box('V02_Main_lower_%02d_%s'%(i,e),(xx,-.56,1.84),(.61,1.83,.105),blue,.044)
  box('V02_Main_upper_%02d_%s'%(i,e),(xx,-.56,3.22),(.61,1.83,.105),blue,.044)
  # Middle berth stowed upright as lower-seat backrest in daytime configuration.
  box('V02_Main_middle_FOLDED_%02d_%s'%(i,e),(x+e*.86,-.56,2.213),(.105,1.83,.635),blue,.04)
  for zz in [1.765,3.145]:box('V02_Transverse_berth_pan',(xx,-.56,zz),(.64,1.85,.032),steel,.008)
  rod('V02_Middle_berth_hinge',(x+e*.86,-1.45,1.88),(x+e*.86,.33,1.88),.018)
  # Upholstery piping along visible aisle edge.
  for zz in [1.84,3.22]:rod('V02_Padded_seam',(xx-.25,.363,zz),(xx+.25,.363,zz),.005,edge)
  for yy in [-1.29,.22]:box('V02_Lower_berth_support',(xx,yy,1.565),(.055,.055,.43),steel,.009)
  for yy in [-.99,-.43,.13]:seat('PAX_B%02d_MAIN_%s_%s'%(i+1,'A' if e<0 else 'B',round((yy+.99)/.56)+1),(x+e*.54,yy,1.915),0 if e<0 else math.pi)
  # Protective upper aisle lip and one ladder per berth stack, away from main circulation.
  rod('V02_Upper_guardrail',(xx-.24,.385,3.38),(xx+.24,.385,3.38),.014)
  for dx in [-.17,.17]:
   rod('V02_Ladder_rail',(xx+dx,.383,1.40),(xx+dx,.383,3.40),.014)
   rod('V02_Guard_post',(xx+dx,.385,3.23),(xx+dx,.385,3.38),.013)
  for zz in [1.72,2.04,2.36,2.68,3.0]:rod('V02_Ladder_rung',(xx-.17,.383,zz),(xx+.17,.383,zz),.013)
  # Reading lamp and outlet are restrained generic batch-dependent fixtures.
  box('V02_Reading_light_base',(x+e*.882,-1.13,2.72),(.027,.16,.12),ivory,.012)
  box('V02_Reading_light_diffuser',(x+e*.858,-1.13,2.72),(.018,.11,.038),white,.009)
  box('V02_Outlet_plate',(x+e*.881,-.28,2.65),(.026,.09,.13),ivory,.008)
  for z in [2.63,2.67]:box('V02_Outlet_slots',(x+e*.864,-.28,z),(.005,.023,.009),rubber)
 # Full bay dividers, with cap; no solid walls through side aisle.
 box('V02_Bay_partition',(x+.925,-.56,2.46),(.035,1.84,2.24),ivory,.008)
 box('V02_Partition_edge',(x+.925,.375,2.46),(.041,.027,2.24),steel,.009)
 label('V02_Bay_number','%02d - %02d'%(i*8+1,i*8+8),(x+.925,.395,3.43),(math.pi/2,0,0),.06)
 # Side lower day seating: two cushions face inward along X, central bed section remains flat.
 for z in [1.84,3.18]:
  box('V02_Side_%s_%02d'%('lower' if z<2 else 'upper',i),(x,1.235,z),(1.72,.57,.105),blue,.045)
  box('V02_Side_pan',(x,1.235,z-.073),(1.75,.59,.029),steel,.008)
 for e in [-1,1]:
  box('V02_Side_backrest',(x+e*.82,1.235,2.16),(.10,.57,.53),blue,.032)
  seat('PAX_B%02d_SIDE_%s'%(i+1,'A' if e<0 else 'B'),(x+e*.59,1.23,1.915),0 if e<0 else math.pi)
  rod('V02_Side_upper_post',(x+e*.69,.925,3.21),(x+e*.69,.925,3.43),.013)
  rod('V02_Side_support',(x+e*.80,.936,1.39),(x+e*.80,.936,3.39),.018)
 rod('V02_Side_upper_rail',(x-.69,.925,3.43),(x+.69,.925,3.43),.013)
 box('V02_Side_divider',(x+.925,1.24,2.47),(.035,.56,2.25),ivory,.009)
 # small table under main window, out of seat leg zones
 box('V02_Window_table',(x,-1.275,2.015),(.40,.44,.038),wood,.015)
 # Luggage storage under lower transverse berth: flat barred shelf; no invented aisle racks.
 for off in [-.61,.61]:
  for yy in [-1.25,-.9,-.55,-.2,.15]:rod('V02_Underseat_luggage_shelf',(x+off-.26,yy,1.50),(x+off+.26,yy,1.50),.008)
 # Ceiling lights and AC slots.
 box('V02_Ceiling_light_housing',(x,.67,3.675),(.69,.19,.028),ivory,.018)
 box('V02_Ceiling_light_diffuser',(x,.67,3.653),(.61,.13,.016),white,.015)
 for s in [-1,1]:
  box('V02_AC_vent',(x,s*1.16,3.615),(.63,.13,.02),vent,.008)
  for k in range(7):box('V02_AC_louvre',(x-.26+k*.086,s*1.16,3.596),(.025,.12,.008),ivory)
 # Lighting separated from exported asset.
 d=bpy.data.lights.new('INTERIOR_LIGHT_%02d'%i,'AREA');d.energy=38;d.shape='RECTANGLE';d.size=1.5;d.size_y=1.1;o=bpy.data.objects.new(d.name,d);studio.objects.link(o);o.location=(x,.3,3.57)
box('V02_Ceiling',(0,0,3.725),(19,3.05,.04),ivory)
for yy in [-1.37,-.98,.96,1.37]:box('V02_Ceiling_panel_joint',(0,yy,3.696),(19,.009,.008),rubber)
# End saloon bulkhead and glazed sliding door opening, offset with aisle.
for e in [-1,1]:
 xx=e*8.58
 box('V02_Saloon_bulkhead_main',(xx,-.66,2.51),(.07,1.71,2.33),ivory,.012)
 box('V02_Saloon_bulkhead_side',(xx,1.31,2.51),(.07,.43,2.33),ivory,.012)
 box('V02_Saloon_bulkhead_header',(xx,.65,3.54),(.07,.91,.27),ivory,.012)
 # Door stowed in pocket left of clear .88m aperture, visible handle/frame.
 box('V02_Saloon_sliding_door_STOWED',(xx-e*.06,-.21,2.45),(.035,.82,2.15),wood,.015)
 box('V02_Saloon_door_pane',(xx-e*.081,-.21,2.64),(.006,.51,1.18),rubber,.08)
 rod('V02_Saloon_door_handle',(xx-e*.10,.12,2.10),(xx-e*.10,.12,2.40),.012)
 box('V02_Vestibule_ceiling',(e*10.10,0,3.62),(2.95,3.05,.04),ivory)
 for s in [-1,1]:
  box('V02_Toilet_closed_compartment',(e*11.1,s*1.12,2.47),(1.16,.70,2.23),ivory,.01)
  box('V02_Toilet_closed_door',(e*10.51,s*1.11,2.38),(.025,.65,2.03),wood,.009)
  rod('V02_Toilet_handle',(e*10.488,s*.88,2.18),(e*10.488,s*.88,2.32),.011)
  box('V02_Entry_inner_liner',(e*10.05,s*1.566,2.39),(.86,.025,1.91),ivory,.025)
 # central gangway recess gets actual visible door frame, not nonexistent machinery
 for yy in [-.50,.50]:box('V02_Vestibule_door_frame',(e*11.64,yy,2.37),(.07,.06,2.08),steel,.01)
 box('V02_Vestibule_door_top',(e*11.64,0,3.4),(.07,1.06,.06),steel,.01)
 label('V02_Exit_label','EXIT',(e*8.528,.66,3.52),(math.pi/2,0,e*math.pi/2),.085)
# Correct glazed window transmission; exterior size, window locations and undercarriage untouched.
g=bpy.data.materials.get('Sealed smoked green glazing');p=g.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.59,.72,.73,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.09;p.inputs['Transmission Weight'].default_value=.97;p.inputs['IOR'].default_value=1.45
# Door attachment repair: related details follow existing pivots preserving world transform.
bpy.context.view_layer.update()
for dp in [o for o in asset.objects if o.name.startswith('DOOR_')]:
 xx=dp.matrix_world.translation.x+.45;ss=1 if dp.matrix_world.translation.y>0 else -1
 for o in list(asset.objects)+list(inter.objects):
  if o.name.startswith(('Door_window','Door_handle','V02_Entry_inner_liner')) and abs(o.matrix_world.translation.x-xx)<.5 and o.matrix_world.translation.y*ss>1.5:
   mw=o.matrix_world.copy();o.parent=dp;o.matrix_world=mw
# Real through-openings in original solid entry leaves and added interior liners.
# Keep the same object, pivot and material; replace only its mesh with a hollow frame.
def door_aperture(o,width,height,depth,holewidth,holeheight,hole_z):
 loops=[]
 for yy in [-depth/2,depth/2]:
  loops.extend([(-width/2,yy,-height/2),(width/2,yy,-height/2),(width/2,yy,height/2),(-width/2,yy,height/2)])
  loops.extend([(-holewidth/2,yy,hole_z-holeheight/2),(holewidth/2,yy,hole_z-holeheight/2),(holewidth/2,yy,hole_z+holeheight/2),(-holewidth/2,yy,hole_z+holeheight/2)])
 fs=[]
 for j in range(4):
  k=(j+1)%4;fs.extend([(j,k,k+4,j+4),(j+8,j+12,k+12,k+8),(j,j+8,k+8,k),(j+4,k+4,k+12,j+12)])
 d=bpy.data.meshes.new(o.name+'_real_aperture');d.from_pydata(loops,[],fs);d.update()
 for m in o.data.materials:d.materials.append(m)
 o.data=d
 for md in list(o.modifiers):o.modifiers.remove(md)
 md=o.modifiers.new('Door frame edges','BEVEL');md.width=.012;md.segments=2
for o in asset.objects:
 if o.name.startswith('Door_leaf'):door_aperture(o,.91,1.98,.055,.34,.90,.29)
 if o.name.startswith('Door_recess'):door_aperture(o,1.05,2.10,.08,.34,.90,.28)
for o in inter.objects:
 if o.name.startswith('V02_Entry_inner_liner'):door_aperture(o,.86,1.91,.025,.34,.90,.29)

root['interior_version']='v02 ordinary 72 berth 3A; middle berths folded for seated daytime use';root['aisle_clear_width_m']=.51;root['seat_locators']='72 reference empties; +X forward; no TF3 runtime config'
sc.render.engine='CYCLES';sc.cycles.samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
def camera(n,loc,target,lens=24,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.025;d.clip_end=1000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
ext=camera('V02_EXTERIOR_REGRESSION',(22,-29,12),(0,0,1.75),ortho=28)
cut=camera('V02_LAYOUT_CUTAWAY',(13,20,20),(0,0,2),ortho=26)
pax=camera('V02_PASSENGER_AISLE',(-7.87,.66,2.80),(3,.65,2.68),lens=20)
bay=camera('V02_PASSENGER_BAY',(-.15,.71,2.6),(0,-1.42,2.5),lens=18)
sc.camera=ext;bpy.ops.wm.save_as_mainfile(filepath=P+'/LHB_3A_interior_v02.blend')
bpy.ops.object.select_all(action='DESELECT')
for c in [asset,inter,locators]:
 for o in c.objects:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=P+'/LHB_3A_interior_v02.fbx',use_selection=True,object_types={'EMPTY','MESH','OTHER'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False)
# Full assembled exterior and actual in-model perspective first.
sc.render.resolution_x=1280;sc.render.resolution_y=720
for cam,filename in [(ext,'LHB_v02_exterior.png'),(pax,'LHB_v02_passenger.png'),(bay,'LHB_v02_bay.png')]:
 sc.camera=cam;sc.render.filepath=P+'/'+filename;bpy.ops.render.render(write_still=True)
# Genuine cutaway render only: hide removable roof and near-side bodyside/upper berth layers.
hidden=[]
for o in list(asset.objects)+list(inter.objects):
 n=o.name;hide=n.startswith(('Arched_LHB_roof','Roof_','AC_','Condenser_','End_roof_cap','V02_Ceiling','V02_AC_','V02_Side_upper','V02_Side_pan','V02_Side_divider'))
 if o.type in {'MESH','CURVE','FONT'} and sum((o.matrix_world @ Vector(v)).y for v in o.bound_box)/8>1.48 and not n.startswith(('Door_','V02_Entry')):hide=True
 if n.startswith(('Grey_lower_body','Red_upper_fascia','Red_sill_band','Window_band_pillar')) and o.location.y>0:hide=True
 if hide and not o.hide_render:o.hide_render=True;hidden.append(o)
sc.cycles.samples=256;sc.camera=cut;sc.render.resolution_y=800;sc.render.filepath=P+'/LHB_v02_cutaway.png';bpy.ops.render.render(write_still=True)
for o in hidden:o.hide_render=False
sc.camera=ext
print('V02_COMPLETE')
