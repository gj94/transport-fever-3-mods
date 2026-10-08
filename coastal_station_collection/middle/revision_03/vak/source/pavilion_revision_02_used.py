"""Localized VAK photo-fidelity repair. Immutable original/source geometry retained."""
import bpy,json,hashlib,shutil,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'vak';P=ROOT/'revision_02/vak';P.mkdir(parents=True,exist_ok=True)
for folder in ('source','renders','export'):(P/folder).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'VAK_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='2e21f937d21776b41e913393ebb948cc37ac2d3a29215aff7fa63cc94992e5d1'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene
oldcol=bpy.data.collections['06C_VARKALA_SIVAGIRI_CENTRAL_PAVILION'];removed=[o.name for o in oldcol.objects]
for o in list(oldcol.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(oldcol)
col=bpy.data.collections.new('06C_VARKALA_PHOTO_BASED_SQUARE_PAVILION');S.collection.children.link(col)
cream=bpy.data.materials['Faded cream limewash'];ochre=bpy.data.materials['Warm station ochre'];dark=bpy.data.materials['Dark iron and rubber']
roof=bpy.data.materials.new('Varkala pavilion warm yellow ochre cap');roof.diffuse_color=(.74,.50,.16,1);roof.use_nodes=True;roof.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=roof.diffuse_color;roof.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
created=[]
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);col.objects.link(o);me.materials.append(m);created.append(n);return o
def box(n,p,d,m):
 x,y,z=[q/2 for q in d];v=[(p[0]+a,p[1]+b,p[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];return mesh(n,v,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],m)
bx,by=34.1,-2.3
# Source is Oct2019 built facade. Dimensions and hidden rear detailing reconstructed.
box('Varkala pavilion broad lower cornice',(bx,by,6.55),(9.5,7.8,.28),ochre)
box('Varkala pavilion stepped upper plinth',(bx,by,6.80),(8.6,6.9,.24),roof)
box('Varkala square cream upper chamber',(bx,by,7.57),(5.2,5.2,1.35),cream)
for x in (-2.65,2.65):
 for y in (-2.65,2.65):box('Varkala ochre chamber corner pilaster',(bx+x,by+y,7.56),(.22,.22,1.43),ochre)
box('Varkala upper chamber cornice',(bx,by,8.29),(5.65,5.65,.16),roof)
# Square hip-cap with a shallow upward curl only at its broad eaves/corners.
vs=[];rings=[(.14,9.02,0),(.90,8.81,.0),(2.70,8.30,.035),(3.55,8.20,.09),(3.76,8.31,.14)]
for r,z,curl in rings:
 for x,y in [(-r,-r),(0,-r),(r,-r),(r,0),(r,r),(0,r),(-r,r),(-r,0)]:vs.append((bx+x,by+y,z+(curl if x and y else 0)))
fs=[]
for j in range(len(rings)-1):
 for k in range(8):fs.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
fs.append(tuple(reversed(range(8))))
start=len(vs)
for v in vs[-8:]:vs.append((v[0],v[1],v[2]-.14))
for k in range(8):fs.append((32+k,32+(k+1)%8,start+(k+1)%8,start+k))
fs.append(tuple(range(start,start+8)))
mesh('Varkala yellow ochre upturned square hip cap',vs,fs,roof)
# Small axial ornamental finial, shown in the 2019 photograph.
rings=[(.13,9.02),(.16,9.11),(.08,9.30),(.04,9.50),(0.005,9.66)];vs=[]
for r,z in rings:
 for k in range(12):vs.append((bx+r*math.cos(k*math.tau/12),by+r*math.sin(k*math.tau/12),z))
fs=[(j*12+k,j*12+(k+1)%12,(j+1)*12+(k+1)%12,(j+1)*12+k)for j in range(4)for k in range(12)];mesh('Varkala central cap finial',vs,fs,roof)
cam=bpy.data.objects['03_PLATFORM_TRACK_DETAILS'];oldcam={'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens};cam.location=(-30,-6.9,3.218);cam.rotation_euler=(Vector((-110,-4.8,2.55))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=32
S['architecture_revision']='VAKv02: source-observed square cream chamber, stepped yellow-ochre upturned hip cap and finial; clear platform camera03. Reference: Google Maps Oct2019.';S['base_blend_sha256']=basehash
out=P/'VAK_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'blend':out.name,'revision':'photo-based pavilion and camera revision02','base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'removed_objects':removed,'created_objects':created,'camera03_before':oldcam,'camera03_after':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens},'observed_source':'Google Maps Oct2019 platform facade screenshot VAK_platform_facade_2019-10.png. Cream square upper chamber, broad stepped ochre cap with uplifted eaves/corners and small finial. Rear dimensions reconstructed.','unchanged':'Track, platforms, wings, rooms, furnishings, footbridge and all cameras except03.','retained_views':['05_ticket_interior.png'],'rerender_views':['01_full_mapped_layout.png','02_station_and_platforms.png','03_platform_track_details.png','04_facade_and_approach.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
oldrp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());rp=dict(oldrp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['source_blend_sha256']=basehash;rr['retained_from_immutable_base']=True;rr['retention_reason']='Interior subject/camera/lighting is unchanged; pavilion is outside the view and enclosed above the roof.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Architecture revision02\nThe central pavilion now follows the actual October2019 photograph: a raised square cream chamber on a stepped cornice, broad yellow-ochre hip cap with upturned corners, and axial finial. Exact chamber dimensions and its hidden rear faces are reconstructed. Camera03 was moved clear of footbridge obstructions. All original track/platform/room geometry remains unchanged. Views01–04 were rerendered; unaffected interior05 retains its original source hash explicitly. See ARCHITECTURE_REVISION.json and the exact repair script.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print('REVISED',json.dumps(rev),flush=True)
