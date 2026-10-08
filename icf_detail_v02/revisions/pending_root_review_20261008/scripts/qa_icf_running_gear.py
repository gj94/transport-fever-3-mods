"""Focused source-component regression; no full-coach assets are changed.

blender -b -t 1 --python scripts/qa_icf_running_gear.py -- [--ac] [--render]
"""
import bpy, bmesh, sys, json, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core as c
import icf_running_gear as g
OUT=HERE.parent/'qa'
OUT.mkdir(exist_ok=True)
AC='--ac' in sys.argv
VAR='AC' if AC else 'nonAC'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
c.C=bpy.data.collections.new('QA_ICF_RUNNING_GEAR');bpy.context.scene.collection.children.link(c.C)
c.ROOT=c.empty('ROOT',(0,0,0));c.BODY=c.empty('BODY',(0,0,0),c.ROOT)
def cyl(n,p,r,d,m,axis='Z',parent=None,vertices=32):
 a=Vector(p);b=Vector(p);ix='XYZ'.index(axis);a[ix]-=d/2;b[ix]+=d/2
 return c.rod(n,a,b,r,m,parent,N=vertices)
M={k:c.material(k,v,.6,.5) for k,v in {'steel':(.30,.33,.35),'dark':(.015,.018,.02),'rubber':(.011,.012,.014),'rust':(.14,.065,.025),'brass':(.39,.28,.11),'paint_blue':(.03,.12,.29)}.items()}
api=SimpleNamespace(root=c.ROOT,body=c.BODY,collection=c.C,materials=M,cube=lambda n,p,d,m,bevel=0,parent=None:c.box(n,p,d,m,parent,bevel),cylinder=cyl,pipe=c.path,mesh=c.mesh,empty=c.empty)
result=g.build(api,ac=AC)
objects=[o for o in c.C.objects if o.get('icf_component')]
meshes=[o for o in objects if o.type=='MESH']
def named(prefix):return [o for o in objects if o.get('icf_component','').startswith(prefix)]
def coords(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(o):
 vv=coords(o);return [[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)]
def centroid(o):return sum(coords(o),Vector())/len(o.data.vertices)
def ancestor(o,p):
 while o.parent:
  o=o.parent
  if o==p:return True
 return False
checks={}
def check(name,test,detail=None):checks[name]={'pass':bool(test),'detail':detail}
counts={'primary_springs':len(named('Primary 33.5mm helical spring')),'secondary_springs':len(named('Secondary 42mm bolster coil')),'brake_blocks':len(named('Curved K-type composition tread brake block')),'wheels':len(named('ICF monobloc 915mm dished wheel')),'axles':len(named('Turned stepped solid ICF axle')),'belts':len(named('Matched alternator V belt'))}
# Spring colour dabs have the same prefix; count the parent coil only.
counts['primary_springs']=len([o for o in named('Primary 33.5mm helical spring') if 'wire_diameter_m' in o])
counts['secondary_springs']=len([o for o in named('Secondary 42mm bolster coil') if 'wire_diameter_m' in o])
check('component_counts',counts==dict(primary_springs=16,secondary_springs=8,brake_blocks=16,wheels=8,axles=4,belts=24 if AC else 4),counts)
bogies=[bpy.data.objects[n] for n in result['bogie_names']]
axles=[bpy.data.objects[n] for n in result['axle_names']]
check('pivot_spacing',abs(bogies[1].matrix_world.translation.x-bogies[0].matrix_world.translation.x-14.783)<2e-6)
check('wheelbase',all(abs(axles[i+1].matrix_world.translation.x-axles[i].matrix_world.translation.x-2.896)<2e-6 for i in [0,2]))
check('axle_height',all(abs(o.matrix_world.translation.z-.4575)<2e-6 for o in axles))
wheel_measurements=[]
for o in named('ICF monobloc'):
 axle=o.parent.matrix_world.translation
 radii=[math.hypot(v.x-axle.x,v.z-axle.z) for v in coords(o) if abs(abs(v.y)-.873)<1e-6]
 wheel_measurements.append([o.name,len(radii),2*sum(radii)/len(radii) if radii else 0])
check('wheel_tread_diameter',all(n==96 and abs(d-.915)<2e-6 for _,n,d in wheel_measurements),wheel_measurements)
check('side_bearer_pitch',all(abs(abs(centroid(named('Side bearer lubricating oil bath')[i]).y-centroid(named('Side bearer lubricating oil bath')[i+1]).y)-1.6)<2e-6 for i in [0,2]))
# Transform actual sample vertices. A root-only metadata assertion cannot prove isolation.
wheel=next(o for o in meshes if o.get('icf_component')=='ICF monobloc 915mm dished wheel' and o.parent==axles[0])
box=next(o for o in named('Axlebox bolted front cover') if o.parent==bogies[0])
wp=coords(wheel)[15];bp=coords(box)[0]
axles[0].rotation_euler.y=.413;bpy.context.view_layer.update()
check('wheel_responds_to_axle_rotation',(coords(wheel)[15]-wp).length>.025)
check('axlebox_does_not_rotate_with_axle',(coords(box)[0]-bp).length<1e-7)
axles[0].rotation_euler.y=0;bpy.context.view_layer.update()
fixed_prefixes=('Axlebox','Wing-type axlebox','Primary ','Brake ','Curved K-type','Bogie mounted','Alternator bolted','Alternator longitudinal')
wrong=[o.name for o in meshes if o.get('icf_component','').startswith(fixed_prefixes) and any(ancestor(o,a) for a in axles)]
check('fixed_gear_not_parented_to_axles',not wrong,wrong)
eq=bpy.data.objects[result['equipment_root']]
ep=coords(named('Battery box enclosure')[0])[0]
wp=coords(wheel)[15];bogies[0].rotation_euler.z=.12;bpy.context.view_layer.update()
check('wheel_responds_to_bogie_yaw',(coords(wheel)[15]-wp).length>.05)
check('body_equipment_ignores_bogie_yaw',(coords(named('Battery box enclosure')[0])[0]-ep).length<1e-7)
bogies[0].rotation_euler.z=0;bpy.context.view_layer.update()
# Independent rotor leaves the stationary alternator casing and belt in place.
rotors=named('ALTERNATOR_')
rotor=rotors[0];driven=next(o for o in named('Alternator V-belt driven pulley') if o.parent==rotor)
barrel=next(o for o in meshes if 'self-generating alternator barrel' in o.name and o.parent==bogies[0])
rp=coords(driven)[17];cp=coords(barrel)[0];rotor.rotation_euler.y=.31;bpy.context.view_layer.update()
check('alternator_rotor_independent',(coords(driven)[17]-rp).length>.01 and (coords(barrel)[0]-cp).length<1e-7)
rotor.rotation_euler.y=0;bpy.context.view_layer.update()
check('alternator_drive_ratio',all(abs(o['drive_ratio']-2.863)<1e-8 for o in rotors))
check('pulley_face_width',all(abs(o['face_width_m']-(.200 if AC else .1365))<1e-8 for o in named('Split axle V-belt drive pulley')))
check('pulley_groove_count',all(o['groove_count']==(6 if AC else 4) for o in named('Split axle V-belt drive pulley')))
# Coils meet upper/lower seats; allow the faceted wire's 1.5 mm extremum error.
contacts=[]
for spring_prefix,low,high in [('Primary 33.5mm',.586,.859),('Secondary 42mm',.5555,.839)]:
 for o in named(spring_prefix):
  if 'wire_diameter_m' not in o:continue
  zz=bounds(o)[2];contacts.append([o.name,zz[0]-low,high-zz[1]])
check('spring_seat_contact',all(-.0015<=a<=.0015 and -.0015<=b<=.0015 for _,a,b in contacts),contacts)
# Alternator end-shields previously intersected the lower transverse plank.
clearances=[]
for o in named('Alternator bolted end shield'):
 ob=bounds(o)
 for plank in named('Lower spring cradle transverse channel'):
  pb=bounds(plank)
  if abs(centroid(o).x-centroid(plank).x)<1:
   gap=max(pb[0][0]-ob[0][1],ob[0][0]-pb[0][1]);clearances.append(gap)
check('alternator_lower_plank_clearance',min(clearances)>.020,clearances)
# Verify nominal frame section bounds independently of displayed metadata.
webs=named('Fabricated sideframe vertical web')
check('frame_length',all(abs(bounds(o)[0][1]-bounds(o)[0][0]-3.95)<2e-6 for o in webs))
# Brake blocks now avoid the flange-root transition at y=0.843.
check('brake_block_flange_root_clearance',all(min(abs(v.y) for v in coords(o))>.8529 for o in named('Curved K-type composition tread brake block')))
issues={'nonmanifold':[],'degenerate_faces':[],'zero_length_edges':[],'inward_volume':[],'nonfinite':[]}
vertices=faces=0
for o in meshes:
 bm=bmesh.new();bm.from_mesh(o.data)
 boundary=sum(not e.is_manifold for e in bm.edges)
 degenerate=sum(f.calc_area()<1e-12 for f in bm.faces)
 volume=bm.calc_volume(signed=True)
 if boundary:issues['nonmanifold'].append([o.name,boundary])
 if degenerate:issues['degenerate_faces'].append([o.name,degenerate])
 zero_edges=sum(e.calc_length()<1e-8 for e in bm.edges)
 if zero_edges:issues['zero_length_edges'].append([o.name,zero_edges])
 if volume< -1e-12:issues['inward_volume'].append([o.name,volume])
 if any(not math.isfinite(x) for v in bm.verts for x in v.co):issues['nonfinite'].append(o.name)
 vertices+=len(bm.verts);faces+=len(bm.faces);bm.free()
for k,v in issues.items():check(k,not v,v)
report={'component_version':result['version'],'mode':VAR,'source_sha256':hashlib.sha256((HERE/'icf_running_gear.py').read_bytes()).hexdigest(),'passed':all(v['pass'] for v in checks.values()),'checks':checks,'mesh_count':len(meshes),'vertices':vertices,'polygons':faces,'scope':'Procedural component source geometry and parenting only. Not full-coach collision, production drawing certification, native game conversion, or suspension animation.'}
path=OUT/f'gear_audit_{VAR}.json';path.write_text(json.dumps(report,indent=2))
print('GEAR_AUDIT',str(path),json.dumps({'passed':report['passed'],'mesh_count':len(meshes),'failed_checks':[k for k,v in checks.items() if not v['pass']]}),flush=True)
if '--render' in sys.argv:
 for o in meshes:
  if not ancestor(o,bogies[0]):o.hide_render=True
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
 scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100
 scene.world.color=(.22,.22,.22);scene.view_settings.view_transform='AgX'
 for p,energy,size in [((-7,-4,6),1400,5),((-5,3,4),1100,4),((-10,0,5),700,3)]:
  ld=bpy.data.lights.new('QA area','AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;lo=bpy.data.objects.new('QA area',ld);scene.collection.objects.link(lo);lo.location=p;lo.rotation_euler=(Vector((-7.3915,0,.65))-lo.location).to_track_quat('-Z','Y').to_euler()
 cd=bpy.data.cameras.new('QA cam');ca=bpy.data.objects.new('QA cam',cd);scene.collection.objects.link(ca);ca.location=(-10.8,-5.5,2.5);ca.rotation_euler=(Vector((-7.3915,0,.55))-ca.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=5.1;scene.camera=ca
 scene.render.filepath=str(OUT/f'gear_audit_{VAR}.png');bpy.ops.render.render(write_still=True)
if not report['passed']:raise RuntimeError('Running gear QA failed; see JSON')
