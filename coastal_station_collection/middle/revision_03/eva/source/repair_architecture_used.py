"""Correct the photographed Edava platform-face tall grilles; other facades and public doors retained."""
import bpy,json,hashlib,shutil,math,sys,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];old=R/'revision_02/eva';p=R/'revision_03/eva';p.mkdir(parents=True,exist_ok=True)
for n in('source','renders','export'):(p/n).mkdir(exist_ok=True)
for f in(old/'source').glob('*'):
 if f.is_file():shutil.copy2(f,p/'source'/f.name)
shutil.copy2(old/'ARCHITECTURE_REVISION.json',p/'source/prior_camera_revision.json');shutil.copy2(old/'source/repair_architecture_used.py',p/'source/prior_camera_revision_used.py')
source=old/'EVA_coastal_station_v01.blend';basehash=hashlib.sha256(source.read_bytes()).hexdigest();assert basehash=='8b0a142156a678db6d69ed522e0633dd2adc76ebcfd8344858a01f550508b48f';bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;F=1.018;backy=9;changes=[];blue=bpy.data.materials['Institutional cobalt lower band']
def comps(me):
 par=list(range(len(me.vertices)))
 def find(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for f in me.polygons:
  a=find(f.vertices[0])
  for i in f.vertices[1:]:par[find(i)]=a
 out={}
 for v in me.vertices:out.setdefault(find(v.index),[]).append(v.index)
 return list(out.values())
def filter_components(o,predicate):
 discard=set()
 for ids in comps(o.data):
  if predicate(ids,o.data):discard.update(ids)
 if not discard:return
 me=o.data;keep=[i for i in range(len(me.vertices))if i not in discard];idx={old:i for i,old in enumerate(keep)};vs=[tuple(me.vertices[i].co)for i in keep];fs=[];mi=[]
 for f in me.polygons:
  if all(i in idx for i in f.vertices):fs.append(tuple(idx[i]for i in f.vertices));mi.append(f.material_index)
 mats=list(me.materials);new=bpy.data.meshes.new(o.name+' platform opening corrected');new.from_pydata(vs,[],fs);new.update()
 for m in mats:new.materials.append(m)
 for f,m in zip(new.polygons,mi):f.material_index=m
 o.data=new;changes.append({'object':o.name,'platform_vertices_removed':len(discard)})
platform=lambda ids,me:abs(sum(me.vertices[i].co.y for i in ids)/len(ids)-backy)<.4
for o in list(S.objects):
 if o.type!='MESH':continue
 if o.name.startswith('Platform facade window sill wall'):
  for v in o.data.vertices:v.co.z=F+(v.co.z-F)*(.10/1.02)
  o.data.update();changes.append({'object':o.name,'new_sill_wall_height_m':.10})
 elif o.name.startswith('Platform facade lintel'):
  moved=0
  for v in o.data.vertices:
   if abs(v.co.z-(F+2.48))<.02:v.co.z+=.10;moved+=1
  o.data.update();changes.append({'object':o.name,'window_lintel_lower_vertices_raised':moved,'new_window_top_above_platform_m':2.58})
 elif any(o.name.startswith(n)for n in['Timber window sill','Timber window jamb','Window header']):
  chosen=set()
  for ids in comps(o.data):
   if not platform(ids,o.data):continue
   chosen.update(ids)
   for i in ids:
    v=o.data.vertices[i]
    if o.name.startswith('Timber window sill'):v.co.z-=.92
    elif o.name.startswith('Timber window jamb'):v.co.z=F+.10+(v.co.z-F-1.02)*(2.48/1.46)
    else:v.co.z+=.10
  if chosen:
   slot=len(o.data.materials);o.data.materials.append(blue)
   for f in o.data.polygons:
    if all(i in chosen for i in f.vertices):f.material_index=slot
   o.data.update();changes.append({'object':o.name,'platform_frame_vertices_adjusted':len(chosen),'finish':'source-observed blue'})
 elif any(o.name.startswith(n)for n in['Window glass pane','Window security bars','Outward timber window awning shutter','Masonry lower plinth']):filter_components(o,platform)
for o in list(S.objects):
 if o.name.startswith('Edavai grille upright')or o.name.startswith('Edavai diamond grille'):changes.append({'object':o.name,'replaced':'full-height source-facing grille'});bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.new('06M_EDAVAI_PHOTOGRAPHED_TALL_OPENINGS');S.collection.children.link(col);vs=[];fs=[]
def box(point,dim):
 x,y,z=[q/2 for q in dim];off=len(vs);vv=[(point[0]+a,point[1]+b,point[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];vs.extend(vv);fs.extend(tuple(off+i for i in f)for f in[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)])
def rod(aa,bb,r=.019):
 a=Vector(aa);b=Vector(bb);d=(b-a).normalized();u=d.cross(Vector((0,0,1)));u=Vector((1,0,0))if u.length<.01 else u.normalized();v=d.cross(u);off=len(vs);N=8;vs.extend(tuple(q+r*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))for q in(a,b)for k in range(N));fs.extend([tuple(off+i for i in reversed(range(N))),tuple(off+N+i for i in range(N))]+[(off+k,off+(k+1)%N,off+(k+1)%N+N,off+k+N)for k in range(N)])
bx=-25;bw=32;bay=bw/9
for i in range(9):
 if i in(0,4,8):continue
 x=bx-bw/2+(i+.5)*bay
 for sg in(-1,1):box((x+sg*(.61+(bay-1.22)/4),backy+.01,F+.36),((bay-1.22)/2,.28,.65))
 box((x,backy+.01,F+.0675),(1.22,.28,.065))
 for dx in(-.35,0,.35):box((x+dx,backy-.20,F+1.335),(.035,.05,2.43))
 for k in range(5):
  z=F+.32+k*.44;points=[(x-.34,8.79,z),(x,8.79,z+.20),(x+.34,8.79,z),(x,8.79,z-.20)]
  for a,b in zip(points,points[1:]+points[:1]):rod(a,b)
 for z in(2.32,2.42,2.52):box((x,8.78,F+z),(1.10,.06,.035))
me=bpy.data.meshes.new('Edavai tall blue geometric grilles and clear low sill');me.from_pydata(vs,[],fs);me.update();me.materials.append(blue);o=bpy.data.objects.new(me.name,me);col.objects.link(o);changes.append({'object':o.name,'six_platform_windows':'near-floor sill0.10m, top2.58m; full-height blue grilles; separate high vents retained'})
S['facade_revision']='EVA revision03: photographed platform-face tall near-floor rectangular grille openings below high vents; generic sill-height windows removed only on this face.';S['base_blend_sha256']=basehash;out=p/'EVA_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),p/'source/repair_architecture_used.py');qa=json.loads((old/'BUILD_QA.json').read_text());qa.update({'revision':S['facade_revision'],'base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(p/'BUILD_QA.json').write_text(json.dumps(qa,indent=2));rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changes,'unchanged':'All track/platform/ramp/doorway and room-furniture geometry, high vents, roof/canopy and cameras. Street facade remains unchanged.','retained_views':[],'rerender_views':['01_full_mapped_layout.png','03_platform_track_details.png','04_facade_and_approach.png','05_ticket_interior.png']};(p/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2));rp=json.loads((old/'RENDER_PROVENANCE.json').read_text());rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[];(p/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2));report=(old/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Photographed tall platform openings revision03\nThe platform-face generic sill-height windows were corrected to the source-observed tall rectangular near-floor openings with blue geometric grilles below the separate high vents. Only non-door bays on that face changed; public doors, ramps, room layouts, tracks and platforms remain intact. Heights and grille-cell dimensions are reconstructed. All four final views are refreshed from this scene.\n';(p/'SOURCES_AND_UNCERTAINTIES.md').write_text(report);print('EVA_TALL_OPENINGS_SAVED',rev['repaired_blend_sha256'],flush=True)
j=R/'portable_colour_revision_02/eva_final_palette_job.json';j.write_text(json.dumps([{'station_code':'EVA','blend_path':str(out.resolve()),'output_path':str((R/'portable_colour_revision_02/palettes/EVA.json').resolve())}],indent=2));sys.argv=['extract_blend_palettes.py','--',str(j)];runpy.run_path(str(R/'scripts/extract_blend_palettes.py'),run_name='__main__');sys.argv=['export_source_cohort.py','--','revision_03:EVA'];runpy.run_path(str(R/'scripts/export_source_cohort.py'),run_name='__main__')
