"""Immutable portable RGB fallback revision; native scenes, galleries and original exports are never changed."""
from pathlib import Path
import json,hashlib,zipfile,sys,subprocess,math,shutil
B=Path(__file__).resolve().parents[1];ROOT=B.parents[1]
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
for code in sys.argv[1:]:
 p=B/'revision_02/KUMM'if code=='KUMM'else B/'revision_03/TNU'if code=='TNU'else B/code
 out=B/'portable_colour_revision_02'/code;manifest=out/'MANIFEST.json'
 if manifest.exists():
  old=json.load(open(manifest))
  assert all(digest(ROOT/f['path'])==f['sha256']for f in old['files']);print('COLOUR_ALREADY_FROZEN',code,flush=True);continue
 if not(p/'MANIFEST.json').exists():print('WAITING_FOR_SOURCE_FREEZE',code,flush=True);continue
 q=json.load(open(p/'QA_BUILD.json'));eq=json.load(open(p/'QA_EXPORT.json'));native=p/q['blend_file'];assert digest(native)==q['blend_sha256']==eq['source_blend_sha256']
 palette_path=B/'export_colour_revision_01'/(code+'_packed_palette.json');pal=json.load(open(palette_path));assert pal['source_blend_sha256']==q['blend_sha256']and pal['source_unchanged'];colors={}
 for name,m in pal['materials'].items():
  a=m['principled_base_color_default'];b=m['diffuse_color'];assert len(a)==4 and all(math.isfinite(x)and 0<=x<=1 for x in a)
  assert all(abs(x-y)<1e-7 for x,y in zip(a,b)),('Authored palette properties disagree',code,name,a,b)
  colors[name]=a
 out.mkdir(parents=True,exist_ok=True);shutil.copyfile(palette_path,out/'SOURCE_MATERIALS.json');shutil.copyfile(p/'QA_EXPORT.json',out/'ORIGINAL_EXPORT_QA.json');shutil.copyfile(Path(__file__),out/'REVISION_BUILDER.py')
 helper=(B.parent/'south/scripts/portable_colors.py').read_bytes();(out/'PATCH_SOURCE.py').write_bytes(helper);ns={};exec(compile(helper,str(out/'PATCH_SOURCE.py'),'exec'),ns)
 vp={'source_blend_sha256':q['blend_sha256'],'colors':colors,'source_material_palette_sha256':digest(out/'SOURCE_MATERIALS.json'),'source_choice':'Exact Principled Base Color defaults and material diffuse RGB values agree; linked procedural textures remain native Blender features.'};(out/'VALIDATION_PALETTE.json').write_text(json.dumps(vp,indent=2))
 exports=[eq]+eq.get('additional_exports',[]);revisions=[]
 for e in exports:
  raw_path=p/e['export'];assert digest(raw_path)==e['export_sha256'];raw=raw_path.read_bytes();patched,proof=ns['patch'](raw,colors)
  member=raw_path.stem+'_colour_v02.glb';zp=out/(member+'.zip')
  with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.writestr(member,patched)
  with zipfile.ZipFile(zp)as z:
   assert z.testzip()is None;check=z.read(member);assert hashlib.sha256(check).hexdigest()==proof['new_glb_sha256'];assert len(check)==len(patched)
  proof.update({'station_code':code,'source_scene':e.get('scene'),'source_blend_sha256':q['blend_sha256'],'source_glb':str(raw_path.relative_to(ROOT)),'source_glb_bytes':len(raw),'corrected_glb_bytes':len(patched),'zip_file':str(zp.relative_to(ROOT)),'zip_member':member,'zip_sha256':digest(zp),'zip_bytes':zp.stat().st_size,'zip_lossless_verified':True,'source_palette_sha256':digest(out/'SOURCE_MATERIALS.json'),'patch_source_sha256':digest(out/'PATCH_SOURCE.py')});proof_path=out/(raw_path.stem+'_COLOUR_QA.json');proof_path.write_text(json.dumps(proof,indent=2))
  validation=out/(raw_path.stem+'_INDEPENDENT_VALIDATION.json');r=subprocess.run([sys.executable,str(B.parent/'qa/validate_material_revision.py'),str(raw_path),str(zp),'--palette',str(out/'VALIDATION_PALETTE.json'),'--source-sha256',q['blend_sha256'],'--out',str(validation)],capture_output=True,text=True);print(r.stdout.strip(),flush=True);assert r.returncode==0,r.stderr
  assert digest(raw_path)==e['export_sha256'];revisions.append({**proof,'proof_file':str(proof_path.relative_to(ROOT)),'independent_validation_file':str(validation.relative_to(ROOT))});del raw,patched,check
 assert digest(native)==q['blend_sha256'];original=json.load(open(p/'MANIFEST.json'))
 names='\n'.join('- '+Path(x['zip_file']).name+' → '+x['zip_member'] for x in revisions)
 text=f'''# {code} portable colour revision02

Use the archives below for the portable model. Unzip to obtain the GLB; no geometry simplification was applied.

{names}

This revision fills only missing, untextured RGB base-colour factors from the exact packed Blender material palette. Existing explicit colours, alpha/transmission semantics, image textures, all binary chunks, mesh/accessor/buffer tables, node transforms and scenes remain unchanged. The independent validator checks those properties. The original exported GLB remains preserved as historical provenance and is superseded for portable colour viewing by these archives.

The authoritative packed Blender file and every reviewed rendered image are unchanged. Procedural noise and bump patterns remain native Blender features; this portable correction restores the base palette without claiming to bake those patterns.

Source Blender SHA256: {q['blend_sha256']}
Original source/gallery manifest: {str((p/'MANIFEST.json').relative_to(ROOT))}
'''
 if code=='TNU':text+='\nTNU remains closed from10 July2017. Keep the historical2016 unplaced building and the mapped corridor exports separate; each archive contains only its original intended scene. The historical study does not establish current survival or exact remnant location.\n'
 (out/'README.md').write_text(text)
 files=[]
 for f in sorted(out.rglob('*')):
  if f.is_file()and f.name not in ['MANIFEST.json','SHA256SUMS.txt']:files.append({'path':str(f.relative_to(ROOT)),'sha256':digest(f),'size':f.stat().st_size})
 retained=[f for f in original['files']if f['relative_station_path'].endswith('.blend')or f['relative_station_path'].startswith('renders/')]
 man={'station':code,'status':'frozen_for_independent_material_gate','revision':'portable_colour_revision_02','source_blend_sha256':q['blend_sha256'],'original_source_gallery_manifest':str((p/'MANIFEST.json').relative_to(ROOT)),'original_source_gallery_manifest_sha256':digest(p/'MANIFEST.json'),'native_scene_and_render_bytes_unchanged':True,'retained_assets':retained,'portable_replacements':revisions,'files':files,'file_count':len(files),'total_bytes':sum(f['size']for f in files),'opening_instructions':'Unzip the new archive(s) and open the contained GLB. Retain the original packed Blend/gallery; this addendum supersedes only portable RGB fallback factors.','photo_redistribution':'No third-party photographs included; embedded original sign images unchanged.'};manifest.write_text(json.dumps(man,indent=2));(out/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {Path(f['path']).relative_to(out.relative_to(ROOT))}\n"for f in files));print('COLOUR_REVISION_FROZEN',code,str(manifest),digest(manifest),len(files),man['total_bytes'],flush=True)
