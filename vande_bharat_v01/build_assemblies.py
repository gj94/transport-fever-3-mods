"""Build linked-source review formations; never export these as one vehicle."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;pitch=19.375
specs={8:['DTC','MC','TC_EC','MC2','MC2','TC_CC','MC','DTC'],16:['DTC','MC','TC_CC','MC2','MC','TC_CC','MC2','NDTC_EC','NDTC_EC2','MC2','TC_CC','MC','MC2','TC_CC','MC','DTC']}
formation_source='https://digitalscr.in/bzadiv/circulars/misc_circulars/uploads/Vandebharat_GMsanction.pdf'
mini_source='https://st.indiarailinfo.com/kjfdsuiemjvcya24/0/6/9/2/5769692/0/commhq1764176322411285603.pdf'

def make(n,y=0):
 group=bpy.data.collections.new(f'RAKE_{n}');bpy.context.scene.collection.children.link(group);rows=[];cache={}
 for i,kind in enumerate(specs[n]):
  if kind not in cache:
   with bpy.data.libraries.load(str(P/'cars'/('VB_'+kind+'.blend')),link=True) as(src,dst):dst.collections=['VB_'+kind+'_ASSET']
   cache[kind]=dst.collections[0]
  o=bpy.data.objects.new(f'CAR_{i+1:02d}_{kind}',None);group.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=cache[kind];x=(i-(n-1)/2)*pitch;sign=-1 if i<n/2 else 1;o.location=(x,y,0);o.rotation_euler.z=math.pi if sign<0 else 0
  qa=json.loads((P/'qa'/('VB_'+kind+'.json')).read_text());amin=qa['bounds_lowered_m']['min'][0];amax=qa['bounds_lowered_m']['max'][0]
  rows.append({'index':i+1,'type':kind,'source_blend':'../cars/VB_'+kind+'.blend','source_fbx':'../cars/VB_'+kind+'.fbx','origin_m':[x,y,0],'rotation_z_deg':180 if sign<0 else 0,'facing_sign':sign,'coupling_front_world_m':[x+sign*pitch/2,y,1.02],'coupling_rear_world_m':[x-sign*pitch/2,y,1.02],'left_spacing_datum_world_m':[x-pitch/2,y,1.02],'right_spacing_datum_world_m':[x+pitch/2,y,1.02],'visual_x_min_m':x+(amin if sign>0 else-amax),'visual_x_max_m':x+(amax if sign>0 else-amin),'compact_passenger_seats':qa['passenger_seats'],'pantograph':kind.startswith('TC')})
 joins=[]
 for a,b in zip(rows,rows[1:]):
  error=abs(a['right_spacing_datum_world_m'][0]-b['left_spacing_datum_world_m'][0]);assert error<1e-8
  joins.append({'cars':[a['index'],b['index']],'anchor_error_m':error,'main_body_end_clearance_m':pitch-2*9.33,'bellows_lip_clearance_m':pitch-2*9.675,'floor_bridge_gap_m':pitch-2*9.67,'passage_clear_width_m':1.06,'note':'straight authored pose only; no runtime curve/compression claim'})
 report={'formation_cars':n,'prototype_formation_source':formation_source if n==16 else mini_source,'source_scope':'16-car ordering is official. 8-car inventory is official; two end-BU order and selected TC_EC placement are supported interpretation. Handed orientations mirror units for this model, not factory drawing certification.','coupling_pitch_m':pitch,'total_outer_anchor_span_m':n*pitch,'actual_visual_x_min_m':min(r['visual_x_min_m'] for r in rows),'actual_visual_x_max_m':max(r['visual_x_max_m'] for r in rows),'passenger_seats_compact_total':sum(r['compact_passenger_seats'] for r in rows),'cab_indices':[1,n],'pantograph_indices':[r['index'] for r in rows if r['pantograph']],'cars':rows,'joins':joins,'outer_datum_note':'DTC outward anchor is a stowed rescue-coupler/formation-spacing datum behind the closed nose fairing. Whole trainset coupling is unsupported.','assembly_scene_note':'Collection instances link reusable source cars. Per-type shared rig control in this review scene; conversion must instantiate each per-car rig independently.'}
 report['actual_visible_length_m']=report['actual_visual_x_max_m']-report['actual_visual_x_min_m'];report['platform_320_margin_m']=320-report['actual_visible_length_m'];assert report['actual_visible_length_m']<320
 return report

allreports={}
for n in specs:
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;report=make(n)
 # Evaluate actual mesh instances independently rather than trusting an anchor length.
 bpy.context.view_layer.update();points=[]
 for inst in bpy.context.evaluated_depsgraph_get().object_instances:
  if inst.object.type=='MESH':points.extend([inst.matrix_world@v.co for v in inst.object.data.vertices])
 report['evaluated_instance_bounds_m']={'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]};report['evaluated_length_m']=report['evaluated_instance_bounds_m']['max'][0]-report['evaluated_instance_bounds_m']['min'][0];assert abs(report['evaluated_length_m']-report['actual_visible_length_m'])<.0001
 for lib in bpy.data.libraries:lib.filepath='//../cars/'+Path(lib.filepath).name
 sc.name=f'VB_{n}_LINKED_ASSEMBLY';bpy.ops.wm.save_as_mainfile(filepath=str(P/'assemblies'/f'VB_{n}_car.blend'),compress=True);(P/'assemblies'/f'VB_{n}_formation.json').write_text(json.dumps(report,indent=2));allreports[n]=report
# Single legible orthographic proof, with both rakes parked parallel.
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';make(16,-4);make(8,5)
def linebox(n,c,d,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=n;o.dimensions=d;m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);o.data.materials.append(m)
linebox('Platform_320m',(0,-9,.35),(320,3,.7),(.18,.24,.28))
for y in [-4,5]:
 for yy in [y-.838,y+.838]:linebox('Proof_rail',(0,yy,-.05),(320,.08,.10),(.35,.4,.45))
for x in [-160,160]:linebox('Platform_limit',(x,-9,.80),(.15,3,.10),(.94,.52,.08))
# Label with mesh typography only in review scene.
for txt,x,y in [(f'16 CARS  |  {allreports[16]["evaluated_length_m"]:.3f} m visible  |  310.000 m spacing span',0,-16),(f'8 CARS  |  {allreports[8]["evaluated_length_m"]:.3f} m visible  |  155.000 m spacing span',0,9),('320 m PLATFORM LIMIT',0,-24)]:
 cu=bpy.data.curves.new('Proof_label','FONT');cu.body=txt;cu.align_x='CENTER';cu.size=3.0;o=bpy.data.objects.new('Proof_label',cu);sc.collection.objects.link(o);o.location=(x,y,.9);o.rotation_euler=(0,0,0);m=bpy.data.materials.new(txt);m.diffuse_color=(.012,.025,.04,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.025,.04,1);cu.materials.append(m)
world=bpy.data.worlds.new('Proof_world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.7,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8
sun=bpy.data.lights.new('Proof_sun','SUN');sun.energy=3;ob=bpy.data.objects.new('Proof_sun',sun);sc.collection.objects.link(ob);ob.rotation_euler=(.3,-.4,-.3)
c=bpy.data.cameras.new('Proof_camera');ob=bpy.data.objects.new('Proof_camera',c);sc.collection.objects.link(ob);ob.location=(0,-85,145);ob.rotation_euler=(Vector((0,-1,0))-ob.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=337;sc.camera=ob
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=2400;sc.render.resolution_y=500;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'renders'/'formation_length_proof.png')
for lib in bpy.data.libraries:lib.filepath='//../cars/'+Path(lib.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(P/'assemblies'/'VB_formation_length_proof.blend'),compress=True);bpy.ops.render.render(write_still=True)
