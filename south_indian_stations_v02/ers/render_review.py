import bpy,sys,json,time,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_full_station_v02.blend'))
s=bpy.context.scene
changed=False
# Idempotent final QA fix also present in the builder: east yard fence clears mapped tracks.
for o in s.objects:
 if o.name.startswith(('Boundary concrete post','Boundary wire')) and abs(o.location.y-121)<.1:o.location.y=160;changed=True
# Formation footing QA: ground meets ballast, preventing a floating-bed underside.
base=bpy.data.objects.get('Full railway site base')
if base and abs(base.location.z+.325)>.000001:base.location.z=-.325;changed=True
for ob in s.objects:
 if ob.type=='MESH' and ob.name.startswith(('Ballast formation ','Shared turnout granular formation')):
  for v in ob.data.vertices:
   if v.co.z<.20 and abs(v.co.z+.02)>.000001:v.co.z=-.02;changed=True
# Correct original swept-strip face orientation only if its top is inverted.
for ob in s.objects:
 if ob.type!='MESH' or not (ob.name.startswith(('Ballast formation ','Derived opposite checkrail ')) or 'pale perimeter coping' in ob.name):continue
 top=max(v.co.z for v in ob.data.vertices);polys=[f for f in ob.data.polygons if all(abs(ob.data.vertices[i].co.z-top)<.001 for i in f.vertices)]
 if polys and sum(f.normal.z for f in polys)<0:
  old=ob.data;me=bpy.data.meshes.new(ob.name+' outward normals');me.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(reversed(f.vertices)) for f in old.polygons]);me.update()
  for ma in old.materials:me.materials.append(ma)
  ob.data=me;changed=True
from mathutils import Vector
if '13_Turnout_frog_detail' not in bpy.data.objects:
 changed=True
 cd=bpy.data.cameras.new('13_Turnout_frog_detail');o=bpy.data.objects.new('13_Turnout_frog_detail',cd);s.collection.objects.link(o);o.location=(557,33,3.6);o.rotation_euler=(Vector((549.85,39.75,.62))-o.location).to_track_quat('-Z','Y').to_euler();cd.lens=46;cd.clip_end=4000
if changed:bpy.ops.wm.save_as_mainfile(filepath=str(P/'ERS_full_station_v02.blend'),compress=True)
source_hash=hashlib.sha256((P/'ERS_full_station_v02.blend').read_bytes()).hexdigest()
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=96;s.render.resolution_x=1200;s.render.resolution_y=750
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
(P/'render_idle.flag').unlink(missing_ok=True)
completed=[]
(P/'render_progress.json').write_text(json.dumps({'state':'running','requested':args,'completed':completed}))
order={'13':0,'05':1,'02':2} if args else {}
for c in sorted([o for o in s.objects if o.type=='CAMERA'],key=lambda x:(order.get(x.name[:2],9),x.name)):
 if args and not any(c.name.startswith(a) for a in args):continue
 s.cycles.samples=128 if c.name[:2] in ['02','03','08','09','11'] else 64
 s.camera=c;s.render.filepath=str(P/'renders'/(c.name+'.png'));bpy.ops.render.render(write_still=True)
 proof={'image':c.name+'.png','image_sha256':hashlib.sha256((P/'renders'/(c.name+'.png')).read_bytes()).hexdigest(),'source_blend':'ERS_full_station_v02.blend','source_blend_sha256':source_hash,'samples':s.cycles.samples,'threads':4,'engine':'Cycles CPU','denoising':False,'status':'Rendered from frozen scene; visual review recorded separately in QA.md'}
 (P/'renders'/(c.name+'.proof.json')).write_text(json.dumps(proof,indent=2))
 completed.append(c.name);(P/'render_progress.json').write_text(json.dumps({'state':'at_frame_boundary','completed':completed,'last_frame':c.name,'unix_time':time.time()}))
 print('ERS_FRAME_BOUNDARY',c.name,flush=True)
 if (P/'STOP_AFTER_FRAME').exists():break
(P/'render_idle.flag').write_text('Renderer idle after: '+', '.join(completed))
(P/'render_progress.json').write_text(json.dumps({'state':'idle','completed':completed,'unix_time':time.time()}))
