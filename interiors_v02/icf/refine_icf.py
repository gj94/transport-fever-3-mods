"""Blender 4.3.2: refine a preserved ICF prototype, no third-party geometry."""
import bpy, math, json, os, sys, hashlib
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SRC=Path(args[0]) if args else OUT/'source'/'icf_sleeper_prototype.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene=bpy.context.scene
asset=bpy.data.collections.get('ICF Sleeper | original dimensioned prototype')
body=bpy.data.objects['BODY'];root=bpy.data.objects['ICF_ROOT_metres_X_forward']
def tris(obs):return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs if o.type=='MESH')
def signature(o):
 return hashlib.sha256((str([tuple(round(v,6) for v in x.co) for x in o.data.vertices])+str([tuple(p.vertices) for p in o.data.polygons])+str([list(row) for row in o.matrix_world])+str(o.parent.name if o.parent else '')).encode()).hexdigest() if o.type=='MESH' else str([list(row) for row in o.matrix_world])
base_tris=tris(asset.objects)
remove=['Transverse sleeper berth','Side sleeper berth','Compartment partition','Berth ladder','Aisle ceiling lamp','Vestibule compartment bulkhead']
protected={o.name:signature(o) for o in asset.objects if not any(o.name.startswith(n) for n in remove)}
for o in list(asset.objects):
 if any(o.name.startswith(n) for n in remove):bpy.data.objects.remove(o,do_unlink=True)
interior=bpy.data.collections.new('ICF_INTERIOR_V02');scene.collection.children.link(interior)
def mat(n,c,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
cream=mat('Interior warm pale seafoam laminate',(.47,.62,.57));edge=mat('Pale grey edge trims',(.61,.67,.63),.25);blue=mat('Blue padded vinyl with subtle grain',(.025,.12,.24),0,.48);steel=mat('Brushed interior stainless',(.44,.49,.51),.75,.32);dark=mat('Interior dark enamel',(.065,.085,.09),.35);floor=mat('Grey speckled coach flooring',(.19,.23,.23),0,.85);light=mat('Warm diffused fluorescent lens',(.95,.89,.70),0,.4,2)
# Procedural texture only; no photos used as textures.
for m,scale,strength in [(blue,180,.12),(floor,130,.22)]:
 nt=m.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.006;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.materials.append(m);me.update();o=bpy.data.objects.new(n,me);interior.objects.link(o);o.parent=body;return o
def box(n,c,s,m,bev=0):
 x,y,z=c;a,b,d=[v/2 for v in s];v=[(x+i*a,y+j*b,z+k*d) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];o=mesh(n,v,f,m)
 if bev:mod=o.modifiers.new('Small manufactured radius','BEVEL');mod.width=bev;mod.segments=2
 return o
def rod(n,a,b,r,m,N=8):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.01:u=d.cross(Vector((1,0,0)))
 u.normalize();w=d.cross(u);v=[tuple(p+r*(math.cos(i*2*math.pi/N)*u+math.sin(i*2*math.pi/N)*w)) for p in [a,b] for i in range(N)];f=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[tuple(reversed(range(N))),tuple(range(N,2*N))];return mesh(n,v,f,m)
def ring(n,c,r,m,axis='Z',tube=.007,N=20):
 pts=[]
 for i in range(N+1):
  a=i*2*math.pi/N;q=(r*math.cos(a),r*math.sin(a));pts.append((c[0]+q[0],c[1]+q[1],c[2]) if axis=='Z' else (c[0],c[1]+q[0],c[2]+q[1]))
 for a,b in zip(pts,pts[1:]):rod(n,a,b,tube,m,6)
def loc(n,c,props=None):
 o=bpy.data.objects.new(n,None);interior.objects.link(o);o.parent=body;o.location=c;o.empty_display_size=.12
 if props:
  for k,v in props.items():o[k]=v
 return o
berths=[]
def cushion(n,c,s):
 o=box(n,c,s,blue,.035);o['component']='berth_cushion';berths.append(o)
 # thin piping on all horizontal long visible edges
 return o
box('Interior finished floor',(0,0,1.337),(21.10,3.06,.024),floor)
# Lining uses the exact existing aperture grid, without covering apertures.
windows=[-7.2675+i*.855 for i in range(18)]
for sign in [-1,1]:
 y=sign*1.552
 for n,z,h in [('Lower wall lining',1.70,.70),('Upper wall lining',3.11,.66)]:box(n,(0,y,z),(21.12,.02,h),cream)
 for z in [2.01,2.735]:box('Window horizontal interior trim',(0,y,z),(21.10,.035,.09),edge)
 openings=sorted([(x,.66) for x in windows]+[(-9.13,.78),(9.13,.78),(-10.12,.43),(10.12,.43)])
 e=-10.56
 for x,w in openings:
  if x-w/2>e:box('Window interior pier',((e+x-w/2)/2,y,2.37),(x-w/2-e,.021,.64),cream)
  e=x+w/2
 if e<10.56:box('Window interior end pier',((e+10.56)/2,y,2.37),(10.56-e,.021,.64),cream)
 for x in windows:
  for xx in [x-.337,x+.337]:box('Window shutter inner guide',(xx,sign*1.532,2.37),(.023,.045,.68),steel)
  box('Window sill',(x,sign*1.51,2.04),(.70,.10,.035),edge,.007)
  box('Shutter lift handle',(x,sign*1.526,2.61),(.13,.034,.024),dark,.008)
# Curved inner ceiling, normals down/in, closed thickness by solidify.
N=32;v=[]
for x in [-10.55,10.55]:
 for j in range(N+1):
  a=j*math.pi/N;v.append((x,1.55*math.cos(a),3.37+.54*math.sin(a)))
f=[(j+1,j,N+1+j,N+2+j) for j in range(N)];ceil=mesh('Interior curved ceiling lining',v,f,cream);mod=ceil.modifiers.new('Ceiling panel thickness','SOLIDIFY');mod.thickness=.015
for x in [-8.1,-6.0,-4,-2,0,2,4,6,8.1]:
 for j in range(16):
  a=j*math.pi/16;b=(j+1)*math.pi/16;rod('Ceiling panel joint',(x,1.55*math.cos(a),3.363+.54*math.sin(a)),(x,1.55*math.cos(b),3.363+.54*math.sin(b)),.005,edge,6)
# Nine bays, retain exterior grid. Daytime middle berths folded vertically against partitions.
for bay in range(9):
 cx=-6.84+bay*1.71;prefix=f'Bay_{bay+1:02d}'
 for side in [-1,1]:
  xx=cx+side*.53
  cushion(prefix+'_lower', (xx,-.60,1.755),(.59,1.77,.12))
  cushion(prefix+'_upper', (xx,-.60,2.96),(.59,1.77,.10))
  cushion(prefix+'_middle_folded_backrest',(cx+side*.765,-.60,2.10),(.085,1.77,.56))
  box(prefix+'_lower_steel_pan',(xx,-.60,1.676),(.61,1.79,.035),dark,.009)
  box(prefix+'_upper_steel_pan',(xx,-.60,2.893),(.61,1.79,.03),dark,.009)
  for yy in [-1.31,.15]:
   rod(prefix+'_seat_leg',(xx,yy,1.36),(xx,yy,1.67),.022,steel)
   rod(prefix+'_fold_hinge',(cx+side*.754,yy-.06,1.81),(cx+side*.754,yy+.06,1.81),.019,steel)
   # upper tie supports, straight steel supports rather than millions of chain links
   anchor_z=3.37+.54*math.sqrt(1-(yy/1.55)**2)-.018
   rod(prefix+'_upper_support',(cx+side*.22,yy,2.91),(cx+side*.22,yy,anchor_z),.012,dark)
   box(prefix+'_support_anchor',(cx+side*.22,yy,anchor_z),(.07,.055,.04),steel)
  # luggage rack under lower berth: six transverse bars, accessible from bay aisle
  for xx2 in [xx-.25+i*.10 for i in range(6)]:rod(prefix+'_luggage_rack',(xx2,-1.40,1.49),(xx2,.18,1.49),.009,steel)
  for yy in [-1.38,.17]:rod(prefix+'_rack_rail',(xx-.28,yy,1.49),(xx+.28,yy,1.49),.015,steel)
  # ladder at end of cushion, leaves longitudinal side aisle free
  lx=cx+side*.59
  for dx in [-.115,.115]:rod(prefix+'_ladder_upright',(lx+dx,.315,1.36),(lx+dx,.315,3.02),.017,steel)
  for z in [1.56,1.87,2.18,2.49,2.80]:rod(prefix+'_ladder_rung',(lx-.115,.315,z),(lx+.115,.315,z),.014,steel)
  for yy in [-1.19,-.60,-.01]:
   k=bay*8+(1 if side==-1 else 4)+int(round((yy+1.19)/.59))
   loc(f'PASSENGER_SEATED_{k:02d}',(xx,yy,1.82),{'purpose':'Authoring reference only; not a game/runtime binding','bay':bay+1})
  for tier,z in enumerate([1.83,2.16,3.02]):
   num=bay*8+(1 if side==-1 else 4)+tier;loc(f'BERTH_{num:02d}_'+['LOWER','MIDDLE_FOLDED','UPPER'][tier],(xx,-.60,z),{'folded':tier==1})
 # Single shared partitions at boundaries avoid coincident duplicate solids
 if bay==0:box(prefix+'_partition_start',(cx-.855,-.61,2.38),(.028,1.83,2.02),cream,.005)
 box(prefix+'_partition_end',(cx+.855,-.61,2.38),(.028,1.83,2.02),cream,.005)
 # Number plates on aisle-facing partition edges
 for side in [-1,1]:
  cu=bpy.data.curves.new(prefix+'_berth_number_plate','FONT');cu.body=f'{bay*8+(1 if side==-1 else 4)} / {bay*8+(2 if side==-1 else 5)} / {bay*8+(3 if side==-1 else 6)}';cu.size=.043;cu.align_x='CENTER';cu.extrude=0;cu.resolution_u=1;ob=bpy.data.objects.new(cu.name,cu);interior.objects.link(ob);ob.parent=body;ob.location=(cx+side*.55,.335,3.17);ob.rotation_euler=(math.pi/2,0,math.pi);cu.materials.append(dark)
 # two longitudinal side berths, a 0.59m clear aisle at y=.30..87
 for label,z in [('lower',1.765),('upper',2.96)]:
  cushion(prefix+'_side_'+label,(cx,1.18,z),(1.57,.57,.115))
  box(prefix+'_side_'+label+'_pan',(cx,1.18,z-.075),(1.59,.59,.029),dark,.01)
 rod(prefix+'_side_lower_cushion_division',(cx,.913,1.825),(cx,1.447,1.825),.003,dark,6)
 for xx in [cx-.76,cx+.76]:
  rod(prefix+'_side_support',(xx,.89,1.38),(xx,.89,3.27),.018,steel)
  box(prefix+'_side_end_trim',(xx,1.20,2.39),(.035,.60,.96),cream,.012)
 # realistic small fold-down table between main windows
 box(prefix+'_window_table',(cx,-1.285,1.94),(.34,.42,.028),edge,.018)
 rod(prefix+'_table_bracket',(cx,-1.49,1.72),(cx,-1.14,1.92),.013,steel)
 for j in [7,8]:loc(f'BERTH_{bay*8+j:02d}_SIDE_'+('LOWER' if j==7 else 'UPPER'),(cx,1.18,1.84 if j==7 else 3.02))
 loc(f'PASSENGER_SEATED_{bay*8+7:02d}',(cx-.49,1.18,1.83));loc(f'PASSENGER_SEATED_{bay*8+8:02d}',(cx+.49,1.18,1.83))
 # caged three-blade fan, not a generic propeller without guard
 fy=-.58;fz=3.48
 rod(prefix+'_fan_stem',(cx,fy,3.88),(cx,fy,3.55),.025,cream)
 rod(prefix+'_fan_motor',(cx,fy,3.47),(cx,fy,3.57),.072,dark,16)
 for radius in [.10,.18,.235]:ring(prefix+'_fan_guard',(cx,fy,fz),radius,steel)
 for a in range(0,360,45):
  a=math.radians(a);rod(prefix+'_fan_guard_spoke',(cx,fy,fz-.026),(cx+.235*math.cos(a),fy+.235*math.sin(a),fz),.0045,steel,6)
 for angle in [0,120,240]:
  a=math.radians(angle);points=[(.04,-.025),(.20,-.06),(.215,.025),(.06,.035)];vs=[(cx+u*math.cos(a)-v*math.sin(a),fy+u*math.sin(a)+v*math.cos(a),fz+.036) for u,v in points];mesh(prefix+'_fan_blade',vs,[(0,1,2,3)],dark)
 box(prefix+'_fluorescent_fixture',(cx,.59,3.62),(.65,.18,.06),edge,.015)
 box(prefix+'_fluorescent_diffuser',(cx,.59,3.58),(.59,.14,.018),light,.007)
# End compartment portals with side aisle openings; sealed toilets simplified.
for sign in [-1,1]:
 x=sign*8.12
 box('End saloon bulkhead main',(x,-.64,2.37),(.04,1.83,2.05),cream)
 box('End saloon bulkhead side',(x,1.255,2.37),(.04,.60,2.05),cream)
 box('End saloon portal lintel',(x,.59,3.29),(.045,.68,.22),edge)
 for yy in [.27,.93]:rod('End portal grab rail',(x-sign*.08,yy,1.56),(x-sign*.08,yy,2.65),.020,steel)
 for yy in [-1.02,1.02]:
  box('Simplified sealed toilet end bulkhead',(sign*9.68,yy,2.37),(.04,1.02,2.02),cream)
  box('Simplified sealed toilet corridor wall',(sign*10.11,yy*.51,2.37),(.84,.035,2.02),cream)
  box('Toilet door inset',(sign*10.1,yy*.49,2.33),(.66,.035,1.81),edge,.012)
  rod('Toilet door pull',(sign*10.2,yy*.46,2.08),(sign*10.2,yy*.46,2.25),.016,steel)
 for yy in [-1.49,1.49]:
  box('Entry door inner lower panel',(sign*9.13,yy,1.705),(.73,.045,.73),cream,.01)
  box('Entry door inner upper panel',(sign*9.13,yy,3.035),(.73,.045,.61),cream,.01)
  for dx in [-.325,.325]:box('Entry door inner window stile',(sign*9.13+dx,yy,2.40),(.08,.045,.66),cream,.005)
  for xx in [sign*9.13-.43,sign*9.13+.43]:rod('Entry inner grab rail',(xx,yy*.93,1.49),(xx,yy*.93,2.83),.023,steel)
 box('Vestibule inner end header',(sign*10.39,0,3.34),(.05,1.02,.17),edge)
 for yy in [-.42,.42]:rod('Vestibule door handrail',(sign*10.36,yy,1.62),(sign*10.36,yy,2.61),.019,steel)
# Explicit checks on cushion AABBs; intentional support contacts excluded.
def aabb(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)]
bpy.context.view_layer.update();collisions=[]
for i,a in enumerate(berths):
 aa=aabb(a)
 for b in berths[i+1:]:
  bb=aabb(b)
  if all(min(aa[k][1],bb[k][1])-max(aa[k][0],bb[k][0])>.002 for k in range(3)):collisions.append([a.name,b.name])
# Apply only new bevels, keeps originals bit-for-bit unchanged.
bpy.ops.object.select_all(action='DESELECT')
for o in interior.objects:
 if o.type in {'MESH','FONT'}:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in interior.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH')
allasset=list(asset.objects)+list(interior.objects)
regress=[n for n,s in protected.items() if signature(bpy.data.objects[n])!=s]
qa={'source_baseline_triangles':base_tris,'final_asset_triangles':tris(allasset),'interior_triangles':tris(interior.objects),'growth_triangles':tris(allasset)-base_tris,'protected_original_objects':len(protected),'protected_geometry_transform_hierarchy_changes':regress,'cushions':len(berths),'cushion_intersections':collisions,'berth_locators':sum(o.name.startswith('BERTH_') for o in interior.objects),'passenger_seated_locators':sum(o.name.startswith('PASSENGER_SEATED_') for o in interior.objects),'nominal_capacity':72,'middle_configuration':'18 upright folded daytime backrests','clear_main_aisle_m':.53,'longitudinal_berth_length_m':1.57,'main_berth_length_m':1.77,'bay_pitch_m':1.71,'dimensions_from_original':{k:root[k] for k in root.keys()},'status':'Detailed visual prototype; no TF3 integration or runtime passenger binding tested'}
(OUT/'qa.json').write_text(json.dumps(qa,indent=2))
assert not collisions,collisions
assert not regress,regress
root['interior_version']='v02 daytime folded middle';root['interior_runtime_binding']='not implemented'
# Render setup is honest: passenger view all full asset geometry visible; cutaway explicitly identified.
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.9
scene.view_settings.exposure=.65
studio=bpy.data.collections['STUDIO_render_only']
for x in [-6,-3,0,3,6]:
 data=bpy.data.lights.new('Interior practical illumination','AREA');data.energy=90;data.shape='RECTANGLE';data.size=1.1;data.size_y=.30;ob=bpy.data.objects.new(data.name,data);studio.objects.link(ob);ob.location=(x,.57,3.48)
def camera(n,location,target,lens=22,ortho=None):
 data=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,data);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.035
 if ortho:data.type='ORTHO';data.ortho_scale=ortho
 return o
passenger=camera('Passenger aisle full shell',(-7.8,.60,2.46),(5,.60,2.46),19)
baycam=camera('Passenger daytime bay',(-6.84,-1.29,2.37),(-6.84,1.35,2.27),18)
cut=camera('Cutaway overview',(15,21,19),(0,0,2.1),ortho=25)
exterior=camera('Exterior regression',(22,-30,13),(0,0,1.55),ortho=27)
scene.camera=passenger
bpy.ops.object.select_all(action='DESELECT')
for o in allasset:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'icf_sleeper_interior_v02.fbx'),use_selection=True,object_types={'EMPTY','MESH'},apply_unit_scale=True,axis_forward='X',axis_up='Z',add_leaf_bones=False,bake_anim=False)
scene.render.filepath='//passenger_aisle.png';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'icf_sleeper_interior_v02.blend'))
for cam,name in [(passenger,'passenger_aisle'),(baycam,'passenger_bay'),(exterior,'exterior_regression')]:
 scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
# Cutaway hides ceiling/roof and positive side walls only, fully restored after render.
hidden=[]
for o in allasset:
 if o.type!='MESH':continue
 bb=aabb(o);name=o.name
 rooflike=any(s in name for s in ['roof shell','Roof welded','Roof torpedo','ceiling lining','Ceiling panel','Curved roof end'])
 sidewall=bb[1][0]>1.48 and bb[2][1]>1.95 and not name.startswith('Bay_')
 if rooflike or sidewall:hidden.append(o);o.hide_render=True
scene.camera=cut;scene.render.filepath=str(OUT/'cutaway_overview.png');bpy.ops.render.render(write_still=True)
for o in hidden:o.hide_render=False
scene.camera=passenger;scene.render.filepath='//passenger_aisle.png';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'icf_sleeper_interior_v02.blend'))
print('QA',json.dumps(qa))
