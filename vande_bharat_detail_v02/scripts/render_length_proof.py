"""Both actual linked formations beside a400m reference datum, using final measured envelopes."""
import os,bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'));from common import box,collection
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;cache={};reports={}
for n,y in [(8,8),(16,-3)]:
 r=json.loads((OUT/'assemblies'/f'VB_{n}_formation.json').read_text());reports[n]=r
 for row in r['cars']:
  kind=row['type']
  if kind not in cache:
   with bpy.data.libraries.load(str(OUT/'cars'/f'VB_{kind}.blend'),link=True) as(src,dst):dst.collections=[f'VB_{kind}_ASSET']
   cache[kind]=dst.collections[0]
  o=bpy.data.objects.new(f'PROOF_{n}_CAR_{row["index"]}',None);sc.collection.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=cache[kind];o.location=(row['origin_m'][0],y,0);o.rotation_euler.z=math.radians(row['rotation_z_deg'])
source_hashes={f'cars/VB_{kind}.blend':hashlib.sha256((OUT/'cars'/f'VB_{kind}.blend').read_bytes()).hexdigest() for kind in cache}
C=collection('PRESENTATION_NOT_EXPORTED')
def mat(n,c):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);return m
white=mat('Proof ground',(.70,.73,.74));ink=mat('Proof ink',(.018,.045,.07));gold=mat('Proof limits',(.75,.33,.035));rail=mat('Proof rail',(.20,.24,.26))
box('Proof ground',(0,0,-.22),(430,70,.22),white,coll=C,b=.03)
box('400 metre reference',(0,-12,.10),(400,.35,.20),ink,coll=C,b=.03)
for x in [-200,200]:
 box('400 metre limit',(x,-1,.05),(.18,29,.02),gold,coll=C,b=.003)
for y in [-3,8]:
 for yy in [y-.838,y+.838]:box('Proof rail',(0,yy,-.03),(406,.073,.05),rail,coll=C,b=.001)
def label(body,loc,size,ma=ink):
 cu=bpy.data.curves.new('Proof label','FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.materials.append(ma);o=bpy.data.objects.new('Proof label',cu);C.objects.link(o);o.location=loc
label(f'8 CARS  |  {reports[8]["visible_length_m"]:.3f} m VISIBLE  |  192.000 m COUPLING SPAN',(0,13,.1),2.25)
label(f'16 CARS  |  {reports[16]["visible_length_m"]:.3f} m VISIBLE  |  384.000 m COUPLING SPAN',(0,-8.8,.1),2.25)
label('FULL-SIZE 24m CAR SOURCES  |  400m REFERENCE DATUM',(0,-17.5,.1),2.4)
label('MEASURED CLOSED-FAIRING ENVELOPES SHOWN SEPARATELY FROM NOMINAL COUPLER SPANS',(0,-22,.1),1.7)
world=bpy.data.worlds.new('Proof world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.87,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
sun=bpy.data.lights.new('Proof sunlight','SUN');sun.energy=2.4;sun.angle=.15;o=bpy.data.objects.new('Proof sunlight',sun);C.objects.link(o);o.rotation_euler=(.15,-.3,-.4)
cam=bpy.data.cameras.new('Proof camera');o=bpy.data.objects.new('Proof camera',cam);C.objects.link(o);o.location=(0,-35,220);o.rotation_euler=(Vector((0,-1,0))-o.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=418;sc.camera=o
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=False;sc.cycles.adaptive_threshold=.04;sc.render.threads_mode='FIXED';sc.render.threads=int(os.environ.get("VB_RENDER_THREADS","6"));sc.render.resolution_x=3000;sc.render.resolution_y=580;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.filepath=str(OUT/'previews/formation_length_proof.png');sc.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True)
(OUT/'qa/render_formation_length_proof.json').write_text(json.dumps({'library_source_sha256':source_hashes,'image_sha256':hashlib.sha256((OUT/'previews/formation_length_proof.png').read_bytes()).hexdigest(),'source_formation_reports':{str(n):hashlib.sha256((OUT/'assemblies'/f'VB_{n}_formation.json').read_bytes()).hexdigest() for n in reports},'renderer':'Cycles','samples':48,'resolution':[3000,580],'rake_geometry':'Actual linked seven-car source family; not symbolic boxes'},indent=2))

assert all(hashlib.sha256((OUT/p).read_bytes()).hexdigest()==h for p,h in source_hashes.items()), 'Source changed during render'
