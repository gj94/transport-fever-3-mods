"""WAP7 visual interior pass, Blender 4.3.2. Relative source path optional -- source.blend.
No TF3 gameplay integration. Original exterior master preserved separately.
"""
import bpy, math, os, sys, json
from pathlib import Path
from mathutils import Vector
from math import pi,sin,cos
OUT=Path(__file__).resolve().parent
SOURCE=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else OUT/'source/WAP7_prototype.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;asset=bpy.data.collections['WAP7_ASSET'];stage=bpy.data.collections['PRESENTATION_ONLY'];body=bpy.data.objects['BODY']
inter=bpy.data.collections.new('CAB_INTERIORS_V02');scene.collection.children.link(inter)
new=[]
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
wall=mat('Cab warm light grey enamel',(.49,.51,.47),.1,.48);console=mat('Cab grey formed desk',(.30,.34,.33),.25,.42);panel=mat('Charcoal control plates',(.025,.034,.032),.25,.42);rubber=mat('Cab soft rubber',(.018,.022,.023),0,.85);seatmat=mat('Blue vinyl upholstery',(.022,.09,.17),0,.52);metal=mat('Brushed cab metal',(.35,.40,.4),.8,.3);floor=mat('Anti-slip cab floor',(.075,.089,.086),.1,.85);red=mat('Red controls',(.48,.022,.016),0,.4);amber=mat('Amber controls',(.8,.39,.015),.1,.35);green=mat('Green controls',(.025,.25,.08),.1,.4);blue=mat('Blue controls',(.014,.17,.37),.1,.4);ivory=mat('Instrument tick colour',(.65,.72,.65),0,.45)
white=bpy.data.materials['Signal white | RAL9003 approximation']
# Fine procedural roughness on the metal floor, no simulated dirt decals.
p=floor.node_tree.nodes.get('Principled BSDF');noise=floor.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=170;bump=floor.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.006;floor.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);floor.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
def obj(n,v,f,m,loc=(0,0,0),coll=None,parent=None,bevel=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);(coll or inter).objects.link(o);o.location=loc;o.parent=parent if parent else body
 if m:me.materials.append(m)
 if bevel:
  md=o.modifiers.new('Soft manufactured edges','BEVEL');md.width=bevel;md.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 new.append(o);return o
def box(n,c,d,m,bevel=.008,coll=None,parent=None):
 x,y,z=[a/2 for a in d];v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)];return obj(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,c,coll,parent,bevel)
def cyl(n,c,r,h,m,axis='Z',verts=16,parent=None):
 v=[(r*cos(2*pi*j/verts),r*sin(2*pi*j/verts),z) for z in [-h/2,h/2] for j in range(verts)];f=[tuple(reversed(range(verts))),tuple(range(verts,verts*2))]+[(j,(j+1)%verts,(j+1)%verts+verts,j+verts) for j in range(verts)];o=obj(n,v,f,m,c,parent=parent)
 if axis=='X':o.rotation_euler[1]=pi/2
 if axis=='Y':o.rotation_euler[0]=pi/2
 for p in o.data.polygons:
  if len(p.vertices)==4:p.use_smooth=True
 return o
def rod(n,a,b,r,m,parent=None):
 a=Vector(a);b=Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,parent=parent);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
# Open the existing shell. Boolean cavities leave actual wall/roof thickness.
shell=bpy.data.objects['Chamfered welded body shell']
def difference(target,c,d):
 cutter=box('TEMP_CUT',c,d,None,bevel=0,coll=asset);bpy.context.view_layer.update();md=target.modifiers.new('Actual opening','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=cutter;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=md.name);new.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
for s in [-1,1]:
 difference(shell,(s*8.12,0,2.60),(1.92,2.86,2.04))
 for y in [-.67,.67]:difference(shell,(s*9.33,y,3.015),(.8,1.045,.89))
 for y in [-1.58,1.58]:
  difference(shell,(s*8.55,y,3.03),(.51,.5,.74));difference(shell,(s*7.8,y,3.02),(.395,.5,.755))
# Existing opaque seals become outline frames; glazing becomes optically clear.
for o in list(asset.objects):
 if o.name.startswith(('Windscreen rubber seal','Cab side window surround','Door window seal')):
  # Preserve exact transform, replace solid occluding slab with inset border.
  ds=o.dimensions.copy();loc=o.location.copy();rot=o.rotation_euler.copy();ma=o.data.materials[0];isfront=o.name.startswith('Windscreen');name=o.name
  w,h=(ds.y,ds.z) if isfront else (ds.x,ds.z);dep=ds.x if isfront else ds.y;t=.047
  for k in range(4):
   if isfront:
    off=(0,(-1 if k==0 else 1)*(w-t)/2,0) if k<2 else (0,0,(-1 if k==2 else 1)*(h-t)/2);dim=(.036,t,h) if k<2 else (.036,w,t)
   else:
    off=((-1 if k==0 else 1)*(w-t)/2,0,0) if k<2 else (0,0,(-1 if k==2 else 1)*(h-t)/2);dim=(t,.034,h) if k<2 else (w,.034,t)
   ob=box(name+' hollow edge',loc,dim,ma,.012,asset);ob.rotation_euler=rot;ob.location+=rot.to_matrix()@Vector(off)
  bpy.data.objects.remove(o,do_unlink=True)
  continue
 if o.name.startswith('Cab door leaf'):
  difference(o,(o.location.x,o.location.y,3.02),(.395,.4,.755))
glass=bpy.data.materials['Smoked blue cab glazing'];bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.87,.95,.97,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.07;bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45;glass.diffuse_color=(.7,.85,.89,.18)
nt=glass.node_tree;transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.12;nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(bs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
# Texture materials for generic unlabelled analogue instruments and display.
def texmat(n,file):
 m=mat(n,(.3,.4,.3),0,.48);nt=m.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(OUT/'textures'/file));t.image.pack();t.image.filepath='//textures/'+file;nt.links.new(t.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);return m
gaugetex=texmat('Original gauge atlas','cab_gauges.png');screen=texmat('Original generic display','cab_display.png')
def face(n,center,w,h,ma,uv=(0,0,1,1),parent=None):
 # Plane faces aft, slanted upwards 0.35 m per 1 m height.
 x,y,z=center;slope=.35*h if 'removable instrument face' in n else 0;o=obj(n,[(0,-w/2,-h/2),(0,w/2,-h/2),(slope,w/2,h/2),(slope,-w/2,h/2)],[(0,3,2,1)],ma,(x,y,z),parent=parent);layer=o.data.uv_layers.new();u,v,U,V=uv
 for li,coord in zip(o.data.polygons[0].loop_indices,[(u,v),(u,V),(U,V),(U,v)]):layer.data[li].uv=coord
 return o
for end in [1,-1]:
 prefix='CAB_A' if end==1 else 'CAB_B';cab=bpy.data.objects.new(prefix+'_INTERIOR',None);inter.objects.link(cab);cab.parent=body;cab.rotation_euler.z=0 if end==1 else pi
 # All internal local values are for +X; second complete cab rotated as a unit.
 def B(n,c,d,m,bev=.008):return box(prefix+' '+n,c,d,m,bev,parent=cab)
 def C(n,c,r,h,m,axis='Z',verts=16):return cyl(prefix+' '+n,c,r,h,m,axis,verts,cab)
 def R(n,a,b,r,m):return rod(prefix+' '+n,a,b,r,m,cab)
 def F(n,c,w,h,m,uv=(0,0,1,1)):return face(prefix+' '+n,c,w,h,m,uv,cab)
 B('floor liner',(8.17,0,1.595),(2.04,2.94,.075),floor)
 B('rear bulkhead',(7.22,0,2.59),(.085,2.96,2.00),wall)
 B('gangway door gasket',(7.275,0,2.48),(.022,.71,1.73),rubber)
 B('gangway door',(7.299,0,2.48),(.04,.65,1.66),wall,.02)
 B('gangway inspection pane',(7.325,0,2.8),(.018,.38,.43),panel,.025)
 R('gangway door handle',(7.36,-.24,2.36),(7.36,-.24,2.49),.017,metal)
 for y in [-1.45,1.45]:
  B('side interior lower lining',(8.16,y,2.1),(1.87,.04,.9),wall)
  B('door inner kickplate',(7.8,y*.982,1.85),(.58,.022,.33),metal)
  B('door upper lining',(7.8,y,3.55),(.7,.04,.13),wall)
  B('door rear pillar',(7.41,y,2.86),(.10,.055,1.35),wall)
  R('door interior handle',(7.59,y*.965,2.32),(7.72,y*.965,2.32),.015,metal)
 B('ceiling liner',(8.13,0,3.605),(1.93,2.86,.045),wall)
 B('center roof duct',(8.13,0,3.545),(1.93,.27,.08),console)
 # Desk: continuous top, central service pedestal, broad driver foot recess.
 B('continuous desk',(8.83,0,2.385),(.70,2.86,.10),console,.035)
 B('front desk toe fascia',(8.475,0,2.35),(.06,2.86,.15),console,.02)
 B('central equipment pedestal',(8.8,-.13,1.98),(.58,.60,.72),console,.025)
 B('central service access',(8.493,-.13,2.02),(.013,.49,.42),panel)
 for z in [1.89+i*.031 for i in range(5)]:B('service cabinet louvre',(8.482,-.13,z),(.01,.39,.012),metal,.002)
 for y in [-1.33,1.33]:B('desk end pedestal',(8.88,y,1.99),(.56,.18,.75),console)
 # Angular upper housings match the continuous grey sheet-metal desk photograph.
 for y,w,h in [(.72,1.21,.43),(-.17,.58,.42),(-1.10,.50,.31)]:
  housing=B('sloping console housing',(8.98,y,2.625),(.29,w,h),console,.018);housing.rotation_euler[1]=.30
  F('removable instrument face',(8.72,y,2.625),w-.045,h-.045,panel)
 # Three slender analogue rectangular meters and a square gauge in driver plate.
 for i,y in enumerate([1.17,1.00,.85,.70]):
  B('meter bezel',(8.785,y,2.737),(.02,.125 if i==0 else .09,.154),metal,.006)
  F('meter dark scale',(8.768,y,2.737),.10 if i==0 else .067,.13,panel)
  for j in range(5):B('meter scale tick',(8.755,y-.023+j*.011,2.769),(.01,.004,.026),ivory,.001)
  R('meter needle',(8.748,y-.016,2.695),(8.748,y+.02,2.76),.0025,ivory)
 # Subtle three groups of operating switchgear, no unverified safety labels.
 for i in range(4):
  C('indicator chrome collar',(8.81,.50-i*.12,2.76),.027,.018,metal,'X',20);C('indicator lens',(8.796,.50-i*.12,2.76),.022,.02,[red,amber,amber,red][i],'X',20)
 for row in range(3):
  for col in range(9):
   y=1.24-col*.112;z=2.47+row*.063;x=8.72+(z-2.44)*.35
   C('rotary switch bezel',(x,y,z),.016,.02,metal,'X',12);B('toggle stem',(x-.024,y,z+.006),(.041,.010,.016),rubber,.002)
 for y,m in [(.44,blue),(.28,red),(.12,green)]:C('large push button',(8.755,y,2.61),.034,.027,m,'X',20)
 C('emergency stop collar',(8.766,-.025,2.63),.053,.020,amber,'X',24);C('emergency stop mushroom',(8.735,-.025,2.63),.036,.041,red,'X',20)
 # Small LCD with keypad, dark sounder grill.
 B('display bezel',(8.769,-.18,2.69),(.025,.31,.092),metal,.004)
 F('green diagnostic display',(8.746,-.18,2.69),.275,.061,screen)
 for iy in range(4):
  for iz in range(2):B('keypad key',(8.721,-.06-iy*.062,2.58-iz*.05),(.027,.034,.027),ivory,.003)
 # Pressure-gauge side console beside driver's elbow.
 side=B('left pressure console',(8.77,1.30,2.57),(.49,.28,.33),console,.02)
 for i in range(4):
  z=2.55+(i//2)*.12;y=1.20+(i%2)*.115
  C('pressure gauge rim',(8.507,y,z),.052,.023,metal,'X',24)
  uv=((i%2)*.5,(i//2)*.5,(i%2+1)*.5,(i//2+1)*.5);F('pressure gauge face',(8.487,y,z),.087,.087,gaugetex,uv)
 # Assistant desk has its own compact switches.
 for i in range(3):C('assistant switch',(8.764,-.94-i*.11,2.61),.025,.028,[green,blue,rubber][i],'X')
 for y in [-1.20,-1.08,-.96]:
  for z in [2.50,2.70]:B('assistant toggle',(8.75,y,z),(.037,.014,.02),metal,.002)
 # Master controller, brake handle and horn control visible on desk.
 for y,m in [(1.03,rubber),(.26,red),(-.77,rubber)]:
  B('controller mounting boot',(8.59,y,2.455),(.20,.14,.045),rubber,.022)
  R('controller lever',(8.59,y,2.47),(8.57,y,2.63),.013,metal)
  R('controller grip',(8.57,y-.052,2.63),(8.57,y+.052,2.63),.025,m)
 # Three pedals on inclined driver's footboard visible in reference.
 fp=B('driver slanted footboard',(8.76,.79,1.78),(.45,1.01,.055),console);fp.rotation_euler[1]=-.45
 for y in [.48,.78,1.08]:
  ped=B('pedal face',(8.60,y,1.86),(.17,.11,.032),rubber,.011);ped.rotation_euler[1]=-.45
  for k in range(3):B('pedal rib',(8.55+k*.035,y,1.894),(.008,.092,.007),metal,.001)
 # Both crew seats: modeled blue vinyl cushions and separate suspension pedestal.
 for y in [.78,-.90]:
  C('seat pedestal foot',(7.98,y,1.68),.20,.09,metal);C('seat hydraulic column',(7.98,y,1.88),.066,.37,metal)
  B('seat suspension bellows',(7.98,y,1.975),(.24,.24,.18),rubber,.025)
  for z in [1.91,1.945,1.98,2.015]:B('seat bellows rib',(7.98,y,z),(.252,.25,.012),panel,.007)
  B('seat pan',(8.0,y,2.095),(.49,.52,.075),panel,.035)
  B('seat cushion',(8.03,y,2.16),(.49,.51,.11),seatmat,.065)
  back=B('seat back cushion',(7.76,y,2.46),(.12,.50,.56),seatmat,.06);back.rotation_euler[1]=-.09
  B('seat piping',(7.696,y,2.46),(.011,.45,.49),panel,.035)
  for side in [-1,1]:
   R('seat arm upright',(7.82,y+side*.29,2.11),(7.82,y+side*.29,2.38),.021,metal)
   B('seat armrest',(7.99,y+side*.29,2.40),(.37,.067,.054),rubber,.025)
  R('seat adjustment lever',(7.96,y+.2,2.02),(8.12,y+.28,2.02),.011,metal)
 # Front window trim from cabin side, roller-blind cylinders and pulled-up cloth.
 for y in [-.67,.67]:
  R('roller blind spindle',(9.08,y-.53,3.50),(9.08,y+.53,3.50),.039,metal)
  B('raised roller blind',(9.10,y,3.45),(.019,1.06,.15),rubber,.004)
  R('blind bottom weight',(9.087,y-.53,3.37),(9.087,y+.53,3.37),.011,metal)
 # Ceiling fluorescent housing and two inspection lamps (preview emitters).
 B('fluorescent fitting',(8.06,.65,3.554),(.67,.16,.043),console,.013)
 lightmat=mat(prefix+' lamp diffuser',(.77,.8,.7),0,.3);p=lightmat.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.8,.85,.73,1);p.inputs['Emission Strength'].default_value=1.5
 B('lamp diffuser',(8.06,.65,3.524),(.59,.10,.014),lightmat,.006)
 # Small roof ventilation enclosure, guarded fan treated as visual approximation.
 B('overhead equipment cover',(8.65,-.74,3.5),(.36,.32,.18),console,.035)
 for y in [-.84,-.79,-.74,-.69,-.64]:B('overhead grille slot',(8.46,y,3.48),(.01,.019,.08),panel,.002)
 # Fasteners on back bulkhead and service panels.
 for y in [-1.30,-.83,.83,1.30]:
  for z in [1.8,3.38]:C('bulkhead screw',(7.27,y,z),.012,.012,metal,'X',8)
 # Preview cameras and lights belong only to presentation collection.
 def camera(n,loc,target,lens):
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);stage.objects.link(o);o.location=(end*loc[0],end*loc[1],loc[2]);tar=Vector((end*target[0],end*target[1],target[2]));o.rotation_euler=(tar-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.025;o['purpose']='Preview only; TF3 camera configuration not integrated';return o
 camera(prefix+'_ONBOARD_PREVIEW',(7.89,.62,3.00),(9.14,.28,2.74),19)
 camera(prefix+'_CAB_REVIEW',(7.34,0,3.05),(8.85,0,2.50),17)
 for y in [-.65,.65]:
  d=bpy.data.lights.new(prefix+' interior fill','AREA');d.energy=40;d.shape='RECTANGLE';d.size=.6;d.size_y=.25;o=bpy.data.objects.new(d.name,d);stage.objects.link(o);o.location=(end*8.12,end*y,3.5)
print('Interiors and actual openings built',flush=True)
# Export only renderable asset and hierarchy, no preview cameras or studio.
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1120;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.context.view_layer.update()
# Validate non-finite verts and count evaluated triangles, plus exterior envelope.
dg=bpy.context.evaluated_depsgraph_get()
def tri(obs):
 result=0
 for o in obs:
  if o.type=='MESH':
   me=o.evaluated_get(dg).to_mesh();me.calc_loop_triangles();result+=len(me.loop_triangles);o.evaluated_get(dg).to_mesh_clear()
 return result
report={'source_master_triangles':117220,'interior_triangles':tri(inter.objects),'asset_triangles':tri(list(asset.objects)+list(inter.objects)),'interior_objects':len(inter.objects),'axles':[o.name for o in asset.objects if o.name.startswith('AXLE_')],'bogies':[o.name for o in asset.objects if o.name.startswith('BOGIE_')],'cab_roots':[o.name for o in inter.objects if o.type=='EMPTY'],'camera_objects':[o.name for o in stage.objects if o.type=='CAMERA'],'denoising':False,'render_device':'CPU','threads':2,'tf3_camera_config_integrated':False}
report['added_net_triangles']=report['asset_triangles']-117220
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
scene.camera=bpy.data.objects['CAB_A_CAB_REVIEW'];scene.render.filepath='//WAP7_cab_review.png';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAP7_interiors_v02.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in list(asset.objects)+list(inter.objects):o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'WAP7_interiors_v02.fbx'),use_selection=True,object_types={'MESH','EMPTY','OTHER'},apply_unit_scale=True,axis_forward='X',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,add_leaf_bones=False,path_mode='COPY',embed_textures=True)
for name,cam in [('WAP7_onboard_A','CAB_A_ONBOARD_PREVIEW'),('WAP7_cab_review','CAB_A_CAB_REVIEW'),('WAP7_onboard_B','CAB_B_ONBOARD_PREVIEW')]:
 scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['Three quarter camera'];scene.render.filepath=str(OUT/'WAP7_exterior_regression.png');bpy.ops.render.render(write_still=True)
# A separate deliberate presentation cutaway, hidden walls/roof only during render.
hidden=[]
for o in list(asset.objects)+list(inter.objects):
 if o in asset.objects.values() or (o.parent and o.parent.name.startswith('CAB_A') and any(t in o.name for t in ['ceiling','center roof','bulkhead','gangway','side interior','door','blind','lamp','fluorescent','overhead'])):
  if not o.hide_render:hidden.append(o);o.hide_render=True
cam=bpy.data.objects['CAB_A_CAB_REVIEW'];cam.location=(6.9,-3.1,4.65);cam.rotation_euler=(Vector((8.35,0,2.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.5;scene.camera=cam;scene.render.filepath=str(OUT/'WAP7_cab_cutaway.png');bpy.ops.render.render(write_still=True)
for o in hidden:o.hide_render=False
print(json.dumps(report),flush=True)
