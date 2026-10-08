"""Photo-guided PVU wooden window leaves; blue remains in the upper transoms."""
import bpy,json,hashlib,shutil,sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R/'revision_02/pvu';p=R/'revision_03/pvu';p.mkdir(parents=True,exist_ok=True)
for n in('source','renders','export'):(p/n).mkdir(exist_ok=True)
for f in(old/'source').glob('*'):
 if f.is_file():shutil.copy2(f,p/'source'/f.name)
shutil.copy2(old/'ARCHITECTURE_REVISION.json',p/'source/prior_facade_revision.json');shutil.copy2(old/'source/repair_architecture_used.py',p/'source/prior_facade_revision_used.py')
source=old/'PVU_coastal_station_v01.blend';basehash=hashlib.sha256(source.read_bytes()).hexdigest();assert basehash=='2a5a0b12dafabbed96c539f52b195f04f5d8186fcfe17ce4daa8089fdfac9844';bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;changes=[];fronty=30.15;F=1.018
for o in S.objects:
 if o.type!='MESH' or not o.name.startswith('Window glass pane'):continue
 me=o.data;keep=[v.index for v in me.vertices if abs(v.co.y-fronty)>.1];idx={old:i for i,old in enumerate(keep)};vs=[tuple(me.vertices[i].co)for i in keep];faces=[tuple(idx[i]for i in f.vertices)for f in me.polygons if all(i in idx for i in f.vertices)];new=bpy.data.meshes.new(o.name+' retained non-front glazing');new.from_pydata(vs,[],faces);new.update()
 for m in me.materials:new.materials.append(m)
 changes.append({'object':o.name,'front_glazing_vertices_replaced':len(me.vertices)-len(keep)});o.data=new
col=bpy.data.collections.new('06M_PARAVUR_SOURCE_WOODEN_WINDOW_LEAVES');S.collection.children.link(col);batch={}
def box(name,point,dim,material):
 key=(name,material);vs,fs=batch.setdefault(key,[[],[]]);off=len(vs);x,y,z=[a/2 for a in dim];vs.extend((point[0]+a,point[1]+b,point[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]);fs.extend(tuple(off+i for i in f)for f in[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)])
for i in range(11):
 if i==5 or i%4==0:continue
 x=-.3-21+(i+.5)*42/11
 for dx in(-.37,0,.37):
  box('Paravur reddish-brown divided wooden window leaf',(x+dx,fronty+.12,F+1.60),(.33,.07,1.04),'Weathered timber')
  for k in range(7):box('Paravur brown louvred leaf slat',(x+dx,fronty+.18,F+1.16+k*.135),(.31,.055,.040),'Weathered timber')
 box('Paravur retained blue upper transom pane',(x,fronty+.04,F+2.275),(1.10,.028,.29),'Blue tinted glazing')
for (name,mat),(vs,fs)in batch.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials[mat]);o=bpy.data.objects.new(name,me);col.objects.link(o);changes.append({'object':name,'material':mat,'vertices':len(vs)})
S['facade_revision']='PVU revision03: photographed lower window leaves are divided/louvred reddish-brown timber; blue is limited to the upper transoms. Walls, openings and public circulation unchanged.';S['base_blend_sha256']=basehash;out=p/'PVU_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),p/'source/repair_architecture_used.py');qa=json.loads((old/'BUILD_QA.json').read_text());qa.update({'revision':S['facade_revision'],'base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(p/'BUILD_QA.json').write_text(json.dumps(qa,indent=2));rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changes,'unchanged':'All walls/openings, doors/ramps, room furniture, tracks, platforms, roofs and cameras. Only front window infill changed below existing blue transoms.','retained_views':[],'rerender_views':['01_full_mapped_layout.png','03_platform_track_details.png','04_facade_and_approach.png','05_ticket_interior.png']};(p/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2));rp=json.loads((old/'RENDER_PROVENANCE.json').read_text());rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[];(p/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2));report=(old/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Photographed wooden window leaves revision03\nThe lower street-facing window infill now consists of divided/louvred reddish-brown wooden leaves, with blue limited to the upper transoms as in the May2023 photograph. Existing walls/openings, central entry, ramp, room layouts and the rest of the station are unchanged. Exact leaf/slat dimensions remain reconstructed. All four final views are refreshed.\n';(p/'SOURCES_AND_UNCERTAINTIES.md').write_text(report);print('PVU_WOODEN_LEAVES_SAVED',rev['repaired_blend_sha256'],flush=True)
j=R/'portable_colour_revision_02/pvu_final_palette_job.json';j.write_text(json.dumps([{'station_code':'PVU','blend_path':str(out.resolve()),'output_path':str((R/'portable_colour_revision_02/palettes/PVU.json').resolve())}],indent=2));sys.argv=['extract_blend_palettes.py','--',str(j)];runpy.run_path(str(R/'scripts/extract_blend_palettes.py'),run_name='__main__');sys.argv=['export_source_cohort.py','--','revision_03:PVU'];runpy.run_path(str(R/'scripts/export_source_cohort.py'),run_name='__main__')
