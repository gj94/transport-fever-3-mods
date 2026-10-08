"""Remove inferred outdoor shelter/amenity components from the mapped VAK building envelope."""
import bpy,json,hashlib,shutil,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'revision_02/vak';P=ROOT/'revision_03/vak';P.mkdir(parents=True,exist_ok=True)
for folder in ('source','renders','export'):(P/folder).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
shutil.copy2(OLD/'ARCHITECTURE_REVISION.json',P/'source/pavilion_revision_02.json');shutil.copy2(OLD/'source/repair_architecture_used.py',P/'source/pavilion_revision_02_used.py')
base=OLD/'VAK_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='9bdbda1968e9105290c4520a693c5d2d737571064dd76de6628552098e501d56'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene;changes=[];bounds=[5.45,-6.45,62.75,1.85];margin=.30
D=json.loads((P/'source/adopted_geometry.json').read_text());platform=D['platforms'][0]
def widthat(x):
 yy=[];ps=platform['outline']
 for a,b in zip(ps,ps[1:]):
  if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>1e-8:yy.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
 return(min(yy),max(yy))if yy else None
def overlaps(bb):return bb[2]>=bounds[0]-margin and bb[0]<=bounds[2]+margin and bb[3]>=bounds[1]-margin and bb[1]<=bounds[3]+margin
collection=bpy.data.collections['04_PLATFORM_SHELTERS_AND_AMENITIES']
for o in list(collection.objects):
 if o.type!='MESH':
  if overlaps([o.location.x,o.location.y,o.location.x,o.location.y]):changes.append({'object':o.name,'removed':'non-mesh platform sign inside building'});bpy.data.objects.remove(o,do_unlink=True)
  continue
 me=o.data;parents=list(range(len(me.vertices)))
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 def union(a,b):
  a=find(a);b=find(b)
  if a!=b:parents[b]=a
 for face in me.polygons:
  a=face.vertices[0]
  for b in face.vertices[1:]:union(a,b)
 comps={}
 for v in me.vertices:comps.setdefault(find(v.index),[]).append(v.index)
 discard=set();removed_components=0
 canopy=any(o.name.startswith(n)for n in ['Canopy','Corrugated shelter','Shelter','Ceiling fan','Fluorescent'])
 for ids in comps.values():
  vv=[me.vertices[i].co for i in ids];bb=[min(v.x for v in vv),min(v.y for v in vv),max(v.x for v in vv),max(v.y for v in vv)];remove=overlaps(bb)
  if canopy:
   anchor=round((bb[0]+bb[2])/16)*8;yy=widthat(anchor)
   if yy:
    cy=sum(yy)/2;w=min(yy[1]-yy[0]-.75,9.0);row_intersects=anchor+4>=bounds[0]-margin and anchor-4<=bounds[2]+margin and cy+w/2>=bounds[1]-margin and cy-w/2<=bounds[3]+margin
    on_this_platform=abs((bb[1]+bb[3])/2-cy)<=w/2+.7
    remove=remove or(row_intersects and on_this_platform)
  if remove:discard.update(ids);removed_components+=1
 if not discard:continue
 if len(discard)==len(me.vertices):changes.append({'object':o.name,'components_removed':removed_components,'vertices_removed':len(discard),'whole_object':True});bpy.data.objects.remove(o,do_unlink=True);continue
 keep=[i for i in range(len(me.vertices))if i not in discard];idx={old:new for new,old in enumerate(keep)};vs=[tuple(me.vertices[i].co)for i in keep];faces=[tuple(idx[i]for i in f.vertices)for f in me.polygons if all(i in idx for i in f.vertices)];new=bpy.data.meshes.new(me.name+' clear of mapped building');new.from_pydata(vs,[],faces);new.update()
 for m in me.materials:new.materials.append(m)
 o.data=new;changes.append({'object':o.name,'components_removed':removed_components,'vertices_removed':len(discard),'whole_object':False})
assert changes and any('Bench' in c['object'] or 'bench' in c['object']for c in changes) and any('wayfinding' in c['object'].lower()for c in changes),changes
# Preserve clear walking width at the narrow station edge: replace standing veranda
# piers with high wall-mounted metal brackets; their load-bearing design is reconstructed.
arch=bpy.data.collections['05_STATION_ARCHITECTURE_PHOTO_GUIDED']
for o in list(arch.objects):
 if o.name.startswith('Veranda column'):
  changes.append({'object':o.name,'removed':'standing pier replaced by high wall bracket at narrow station edge'});bpy.data.objects.remove(o,do_unlink=True)
# Rear doors swing into rooms so their open leaves do not cross the narrow veranda.
for o in arch.objects:
 if o.type!='MESH':continue
 dy=1.02 if o.name.startswith('Open door panel') else (1.76 if o.name.startswith('Door lever handle') else 0)
 if not dy:continue
 moved=0
 for v in o.data.vertices:
  if v.co.y < -6.3:v.co.y+=dy;moved+=1
 if moved:o.data.update();changes.append({'object':o.name,'rear_leaf_vertices_moved':moved,'dy_m':dy})
vs=[];fs=[]
def rod(a,b,r):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u);off=len(vs);N=8
 vs.extend(tuple(p+r*(u*math.cos(i*math.tau/N)+v*math.sin(i*math.tau/N)))for p in(a,b)for i in range(N))
 fs.extend([tuple(off+i for i in reversed(range(N))),tuple(off+N+i for i in range(N))]+[(off+i,off+(i+1)%N,off+(i+1)%N+N,off+i+N)for i in range(N)])
for x in range(8,63,4):
 rod((x,-6.50,4.018),(x,-7.40,4.558),.055);rod((x,-6.50,4.558),(x,-7.40,4.558),.05)
me=bpy.data.meshes.new('Narrow veranda high wall brackets reconstructed');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);arch.objects.link(o);me.materials.append(bpy.data.materials['Galvanised structural steel']);changes.append({'object':o.name,'added':'high wall brackets leave ground passage clear','minimum_z_m':3.97})
walk=[]
for k in range(61):
 x=bounds[0]+(bounds[2]-bounds[0])*k/60;yy=widthat(x)
 if yy:walk.append(bounds[1]-yy[0])
S['platform_building_overlap']='The inferred raised platform body continues beneath the mapped building as station-edge foundation. It is not six metres of unobstructed passenger width. Outdoor amenities and canopy bays inside the mapped building have been removed.';S['base_blend_sha256']=basehash
out=P/'VAK_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'revision':'platform/building overlap clearance revision03','base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH'),'station_edge_clear_width_before_veranda_posts_m':{'min':min(walk),'max':max(walk)},'platform_body_width_note':'Nominal six-metre raised-body width includes the building overlap; it is not unobstructed pedestrian width.'});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changes,'building_envelope_m':bounds,'body_building_overlap_area_m2':259.68,'station_edge_width_before_veranda_posts_m':[min(walk),max(walk)],'candidate_rear_walking_line_y_m':-7.05,'uncertainty':'Narrow reconstructed station-edge treatment follows the axis-aligned mapped building envelope and inferred platform boundary; not a surveyed accessibility-compliance claim.','unchanged':'Mapped tracks, platform bodies, building, furnished interiors, revised pavilion, cameras and bridge; erroneously colocated outdoor components removed and narrow-edge standing veranda piers replaced by high reconstructed wall brackets; rear door leaves swing inward instead of crossing the narrow veranda.','retained_views':['03_platform_track_details.png'],'rerender_views':['01_full_mapped_layout.png','02_station_and_platforms.png','04_facade_and_approach.png','05_ticket_interior.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
rp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());oldrp=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['retained_from_immutable_base']=True;rr['retention_reason']='Camera03 looks away from the corrected building area, from x−30 toward x−110; outdoor subjects in this view are unchanged.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Station-edge clearance revision03\nThe inferred six-metre side-platform body includes259.68m² beneath the axis-aligned mapped station building and is treated as continuous raised foundation there. It does not imply six metres of clear passenger space. Between the rear building wall and track-side platform edge, the reconstructed clear strip is %.2f–%.2fm between the masonry envelope and platform edge. Standing veranda piers were replaced by high reconstructed wall brackets to leave that ground passage clear, and rear doors swing inward rather than across it. Outdoor canopy bays, benches, water/notice/sign fixtures accidentally placed inside the building envelope have been removed. Actual platform widths and building alignment remain survey uncertainties; accessibility compliance is not claimed. The revised source preserves the original mapped tracks, building and bridge. See ARCHITECTURE_REVISION.json for exact removed components and the proposed y−7.05m walking line for independent checking.\n'%(min(walk),max(walk));(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print(json.dumps(rev),flush=True)
