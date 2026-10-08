"""Bounded photo-facing facade corrections, retaining original route and room layouts."""
import bpy,json,hashlib,shutil,math,sys,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
jobs=[('AMY','6ca7129c71dcab56374a6118c920259fb214601901fcd74268c76969f08e8d07'),('PVU','44677066bc27cfb41f74e15cb49d55714313d6ae8c34e39f1cde23dab51fc380')]
def components(me):
 parents=list(range(len(me.vertices)))
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for f in me.polygons:
  a=find(f.vertices[0])
  for i in f.vertices[1:]:parents[find(i)]=a
 out={}
 for v in me.vertices:out.setdefault(find(v.index),[]).append(v.index)
 return list(out.values())
def install_mesh(o,vs,fs):
 mats=list(o.data.materials);me=bpy.data.meshes.new(o.name+' corrected');me.from_pydata(vs,[],fs);me.update()
 for m in mats:me.materials.append(m)
 o.data=me
boxfaces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
def boxverts(p,d):
 x,y,z=[a/2 for a in d];return[(p[0]+a,p[1]+b,p[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]]
for code,expected in jobs:
 old=R/code.lower();p=R/'revision_02'/code.lower();p.mkdir(parents=True,exist_ok=True)
 for n in('source','renders','export'):(p/n).mkdir(exist_ok=True)
 for f in (old/'source').glob('*'):
  if f.is_file():shutil.copy2(f,p/'source'/f.name)
 source=old/f'{code}_coastal_station_v01.blend';basehash=hashlib.sha256(source.read_bytes()).hexdigest();assert basehash==expected;bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;arch=bpy.data.collections['05_STATION_ARCHITECTURE_PHOTO_GUIDED'];changes=[];F=1.018
 def material(n):return bpy.data.materials[n]
 if code=='AMY':
  bx=-20;fronty=3.5
  # Reflect positions of individual symmetric facade primitives, preserving normals.
  names=['Street facade','Timber window','Window header','Window security bars','Window glass pane','Masonry lower plinth']
  for o in arch.objects:
   if o.type!='MESH' or not any(o.name.startswith(n)for n in names):continue
   moved=0
   for ids in components(o.data):
    cy=sum(o.data.vertices[i].co.y for i in ids)/len(ids)
    if cy<fronty-.25:continue
    cx=sum(o.data.vertices[i].co.x for i in ids)/len(ids);dx=2*(bx-cx)
    for i in ids:o.data.vertices[i].co.x+=dx;moved+=1
   if moved:o.data.update();changes.append({'object':o.name,'front_vertices_mirrored_by_component':moved})
   if o.name.startswith('Window glass pane'):
    mi=len(o.data.materials);o.data.materials.append(material('Weathered timber'))
    for f in o.data.polygons:
     if sum(o.data.vertices[i].co.y for i in f.vertices)/len(f.vertices)>fronty-.25:f.material_index=mi
  detail=bpy.data.collections['06E_AKATHUMURI_YELLOW_ENTRY_AND_BREEZE_BLOCKS']
  for o in detail.objects:
   if o.type!='MESH':continue
   for ids in components(o.data):
    cx=sum(o.data.vertices[i].co.x for i in ids)/len(ids);dx=2*(bx-cx)
    for i in ids:o.data.vertices[i].co.x+=dx
   o.data.update();changes.append({'object':o.name,'facade_detail_reflected_about_x_m':bx})
  for o in arch.objects:
   if o.type=='MESH' and o.name.startswith('Enamel wayfinding panel'):
    o.data.materials[0]=material('Railway enamel yellow')
    for v in o.data.vertices:v.co.z+=.70
    changes.append({'object':o.name,'name_panel':'yellow raised above sunshade'})
   if o.type=='FONT' and o.name.startswith('Wayfinding AKATHUMURI'):
    o.location.z+=.70;o.data.materials[0]=material('Dark iron and rubber')
  # A facade-parallel 14m ramp joins a full-width upper landing beside the doorway.
  landing=bpy.data.objects['Continuous front entrance landing'];install_mesh(landing,boxverts((-22.5,4.4,F-.12),(7,1.8,.24)),boxfaces)
  ramp=bpy.data.objects['Accessible ramp from forecourt'];vs=[(-5,3.7,.05),(-5,5.3,.05),(-19,5.3,F),(-19,3.7,F),(-5,3.7,-.1),(-5,5.3,-.1),(-19,5.3,F-.18),(-19,3.7,F-.18)];install_mesh(ramp,vs,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
  def rods_mesh(o,segments,radius):
   vs=[];fs=[];N=8
   for aa,bb in segments:
    a=Vector(aa);b=Vector(bb);d=(b-a).normalized();u=d.cross(Vector((0,0,1)));u=Vector((1,0,0))if u.length<.01 else u.normalized();v=d.cross(u);off=len(vs);vs.extend(tuple(q+radius*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))for q in(a,b)for k in range(N));fs.extend([tuple(off+i for i in reversed(range(N))),tuple(off+N+i for i in range(N))]+[(off+k,off+(k+1)%N,off+(k+1)%N+N,off+k+N)for k in range(N)])
   install_mesh(o,vs,fs)
  rods_mesh(bpy.data.objects['Accessible ramp handrail'],[((-5,y,.97),(-19,y,F+.92))for y in(3.75,5.25)],.032)
  upr=[]
  for y in(3.75,5.25):
   for k in range(7):
    t=k/6;x=-5-14*t;z=.05+(F-.05)*t;upr.append(((x,y,z),(x,y,z+.92)))
  rods_mesh(bpy.data.objects['Ramp rail upright'],upr,.026)
  steps=bpy.data.objects['Front approach granite step']
  for v in steps.data.vertices:v.co.x=-20.5+(v.co.x+20)*.625;v.co.y+=.2
  steps.data.update();changes.append({'access_ramp':'Runs parallel to facade from lower(-5,4.5,.05) to upper(-19,4.5,1.018); joins landing x[-26,-19],y[3.5,5.3]. Steps width3m centrex-20.5; central doorway unchanged.'})
  for o in bpy.data.collections['07_FURNISHED_INTERIORS_RECONSTRUCTED'].objects:
   if o.type!='MESH' or not any(o.name.startswith(n)for n in['Station noticeboard timber frame','Noticeboard felt','Notice sheet','Notice printed line']):continue
   moved=0
   for v in o.data.vertices:
    if abs(v.co.x+22)<.85 and abs(v.co.y-3.35)<.18:v.co.x+=.34;moved+=1
   if moved:o.data.update();changes.append({'object':o.name,'notice_vertices_moved':moved,'dx_m':.34,'reason':'Keep board on solid pier beside the mirrored wide screen.'})
  location=(-20,24,3.0);target=(-20,3.5,2.6);lens=30;reason='AMY front now matches the photographed brown window left / perforated screen right, yellow header and shade, with a functional facade-parallel ramp. Room layout and central doorway remain unchanged.';retain=['03_platform_track_details.png'];rerender=['01_full_mapped_layout.png','04_facade_and_approach.png','05_ticket_interior.png']
 else:
  bx=-.3;by=25.8;bw=42;bd=8.7;fronty=30.15;col=bpy.data.collections.new('06L_PARAVUR_2023_FACADE_DETAILS');S.collection.children.link(col)
  def box(n,point,dim,matname):
   me=bpy.data.meshes.new(n);me.from_pydata(boxverts(point,dim),[],boxfaces);me.update();me.materials.append(material(matname));o=bpy.data.objects.new(n,me);col.objects.link(o)
  n=11;bay=bw/n
  for i in range(n):
   if i==n//2 or i%4==0:continue
   x=bx-bw/2+(i+.5)*bay
   for dx in(-.20,.20):box('Paravur paired timber window mullion',(x+dx,fronty+.18,F+1.62),(.065,.13,1.10),'Weathered timber')
   box('Paravur blue transom lower bar',(x,fronty+.18,F+2.16),(1.14,.12,.075),'Institutional cobalt lower band')
   for z in(2.25,2.35,2.45):box('Paravur blue upper window louvre',(x,fronty+.19,F+z),(1.12,.14,.04),'Institutional cobalt lower band')
  box('Paravur long off-white projecting sunshade',(bx,fronty+.65,F+2.80),(42.4,1.5,.14),'Chalk white masonry');box('Paravur blue sunshade edge',(bx,fronty+1.43,F+2.79),(42.4,.10,.16),'Institutional cobalt lower band')
  for y in(by-5.1,by+5.1):box('Paravur dark red roof fascia',(bx,y,5.08),(43.6,.14,.20),'Oxide red masonry and tile')
  for o in arch.objects:
   if o.type=='MESH' and o.name.startswith('Enamel wayfinding panel'):o.data.materials[0]=material('Railway enamel yellow')
   if o.type=='FONT' and o.name.startswith('Wayfinding PARAVUR'):o.data.materials[0]=material('Dark iron and rubber')
  changes.append({'facade_additions':'Brown paired window mullions, blue transom/louvre bars, long off-white sunshade with blue edge, yellow name panel and dark-red roof fascia. Existing walls/openings/room layout/ramp unchanged.'});location=(-14,65,5.8);target=(-.3,30.15,3.4);lens=32;reason='PVU revision02 explicitly models the observed May2023 front window/transom, continuous blue-edged shade, yellow name panel and dark-red roof fascia. Building envelope, doors, rooms, tracks and platforms stay unchanged.';retain=[];rerender=['01_full_mapped_layout.png','03_platform_track_details.png','04_facade_and_approach.png','05_ticket_interior.png']
 cam=bpy.data.objects['04_FACADE_AND_APPROACH'];beforecam={'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens};cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;S['facade_revision']=reason;S['base_blend_sha256']=basehash
 out=p/f'{code}_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),p/'source/repair_architecture_used.py');qa=json.loads((old/'BUILD_QA.json').read_text());qa.update({'revision':reason,'base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(p/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
 rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'reason':reason,'changes':changes,'camera04_before':beforecam,'camera04_after':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens},'retained_views':retain,'rerender_views':rerender,'uncertainty':'Visible facade arrangement is photo-guided; dimensions and hidden room details remain reconstructed.'};(p/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2));rp=json.loads((old/'RENDER_PROVENANCE.json').read_text());prior=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
 for v in prior['renders']:
  if Path(v['file']).name in retain:
   vv=dict(v);vv['retained_from_immutable_base']=True;vv['retention_reason']='Track-detail camera looks away from the changed facade/ramp region; its subject geometry and lighting are unchanged.';shutil.copy2(old/v['file'],p/v['file']);rp['renders'].append(vv)
 (p/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2));text=(old/'SOURCES_AND_UNCERTAINTIES.md').read_text();text+='\n\n## Final photographed facade revision02\n'+reason+' Exact component and camera changes are recorded in ARCHITECTURE_REVISION.json. Revised views are source-bound; any retained view keeps its original source hash and unchanged-subject reason.\n';(p/'SOURCES_AND_UNCERTAINTIES.md').write_text(text);print('FACADE_REVISION_SAVED',code,rev['repaired_blend_sha256'],flush=True)
palette_jobs=[{'station_code':c,'blend_path':str((R/'revision_02'/c.lower()/f'{c}_coastal_station_v01.blend').resolve()),'output_path':str((R/'portable_colour_revision_02/palettes'/f'{c}.json').resolve())}for c,_ in jobs];jfile=R/'portable_colour_revision_02/facade_palette_jobs.json';jfile.write_text(json.dumps(palette_jobs,indent=2));sys.argv=['extract_blend_palettes.py','--',str(jfile)];runpy.run_path(str(R/'scripts/extract_blend_palettes.py'),run_name='__main__');sys.argv=['export_source_cohort.py','--','revision_02:AMY','revision_02:PVU'];runpy.run_path(str(R/'scripts/export_source_cohort.py'),run_name='__main__')
