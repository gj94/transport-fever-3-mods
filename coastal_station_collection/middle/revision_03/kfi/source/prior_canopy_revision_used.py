"""Make the photo-guided KFI rose veranda canopy structurally coherent and visible."""
import bpy,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'kfi';P=ROOT/'revision_02/kfi';P.mkdir(parents=True,exist_ok=True)
for f in('source','renders','export'):(P/f).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'KFI_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='bf51dc2fc200fe084f5d6f11e64fc5b9b65b70406fed7a5eae83d9a5e73b1844'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene;roof=bpy.data.objects['Kappil rose sloping veranda roof'];mat=roof.data.materials[0];col=roof.users_collection[0];oldcoords=[list(v.co)for v in roof.data.vertices]
# Original upper/lower edge positions are retained. A solid fascia makes the rose
# plane legible from low platform views; its support piers terminate below it.
top=[(.8,-5,4.818),(22.2,-5,4.818),(22.2,-8.2,4.118),(.8,-8.2,4.118)];vs=top+[(x,y,z-.12)for x,y,z in top];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new('Kappil rose canopy solid sheet and eaves');me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);roof.data=me
changes=[{'object':roof.name,'old_vertices':oldcoords,'new_vertices':vs,'reason':'Give the source-shaped sloping plane a visible physical edge and correct upper/lower normals.'}]
def box(n,p,d,usemat=None):
 x,y,z=[a/2 for a in d];v=[(p[0]+a,p[1]+b,p[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)];m=bpy.data.meshes.new(n);m.from_pydata(v,[],f);m.update();m.materials.append(usemat or mat);o=bpy.data.objects.new(n,m);col.objects.link(o);changes.append({'object':n,'centre_m':p,'dimensions_m':d})
# The source's blue rectangles are on a peach parapet facing the platforms.
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Low blue parapet'):
  o.data.materials[0]=bpy.data.materials['Kappil salmon plaster'];changes.append({'object':o.name,'material':'Kappil salmon plaster','reason':'Peach parapet backdrop with separate blue accents, as photographed.'})
for x in range(2,22,3):box('Kappil platform-facing blue parapet accent',(x,-5.14,4.698),(1.15,.05,.30),bpy.data.materials['Kappil turquoise accents'])
box('Kappil deep rose front fascia',(11.5,-8.19,4.066),(21.4,.15,.22));box('Kappil rose support beam over peach piers',(11.5,-7.9,4.10),(20.6,.26,.20))
for o in bpy.data.collections['05_STATION_ARCHITECTURE_PHOTO_GUIDED'].objects:
 if o.type=='MESH' and o.name=='Veranda column':
  count=0
  for v in o.data.vertices:
   if v.co.z>4.3:v.co.z=4.0;count+=1
  o.data.update();changes.append({'object':o.name,'top_vertices_lowered':count,'new_top_z_m':4.0})
cam=bpy.data.objects['04_FACADE_AND_APPROACH'];oldcam={'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens};cam.location=(-2.5,-33,8.3);cam.rotation_euler=(Vector((11.5,-5,2.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45
S['canopy_revision']='KFIv02: source-observed rose sloping platform veranda gets visible thickness/fascia and corrected peach-pier tops. Facade camera04 now faces the photographed platform side.';S['base_blend_sha256']=basehash
out=P/'KFI_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'revision':'rose veranda canopy revision02','base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changes,'camera04_before':oldcam,'camera04_after':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens},'observed_source':'KFI_facade_2017-10.png: peach block, blue parapet accents and prominent deep rose sloping veranda canopy.','uncertainty':'Roof thickness, fascia, dimensions and pier height are reconstructed from the distant photograph.','unchanged':'Track/platform/body/room/furniture geometry and all cameras except04. Existing canopy plan extent and pitch retained; support tops corrected under it; peach parapet and blue platform-facing accents follow the source.','retained_views':['05_ticket_interior.png'],'rerender_views':['01_full_mapped_layout.png','03_platform_track_details.png','04_facade_and_approach.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
rp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());oldrp=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['retained_from_immutable_base']=True;rr['retention_reason']='Only the external platform-side canopy and facade camera04 changed; the interior subject/camera/illumination is unchanged.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Rose veranda canopy revision02\nThe existing thin sloping roof plane was made solid with a visible deep rose fascia and support beam, and the peach pier tops were lowered beneath it. The photographed peach parapet with blue rectangular accents is also shown on the platform-facing side. Camera04 now looks at the photographed platform facade rather than the less-documented road side. The distant2017 photograph supports the colour and canopy form; exact roof thickness and support dimensions remain reconstructed. Exterior01/03/04 are refreshed; unchanged interior05 retains its explicit base-scene lineage.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print(json.dumps(rev),flush=True)
