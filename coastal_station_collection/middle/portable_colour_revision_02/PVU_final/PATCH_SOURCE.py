"""Additive GLB base-colour revision: retain all binary chunks and non-colour JSON exactly."""
import argparse,copy,hashlib,json,math,struct,zipfile,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--export-zip',required=True);p.add_argument('--export-qa',required=True);p.add_argument('--palette',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--station',required=True);a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda d:json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
source=Path(a.export_zip);eqp=Path(a.export_qa);pp=Path(a.palette);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
if (out/'COLOUR_QA.json').exists():raise RuntimeError('Existing colour revision is immutable; use a fresh output directory')
archive=source.read_bytes();eq=json.loads(eqp.read_text());palette=json.loads(pp.read_text());assert sha(archive)==eq['zip_sha256'];assert palette['source_blend_sha256']==eq['authoritative_blend_sha256'];assert palette['source_blend_unchanged']
with zipfile.ZipFile(source)as z:
 assert z.testzip()is None;names=[n for n in z.namelist()if n.endswith('.glb')];assert len(names)==1;raw=z.read(names[0])
assert sha(raw)==eq['glb_sha256'];magic,version,total=struct.unpack_from('<4sII',raw);assert magic==b'glTF'and version==2 and total==len(raw)
chunks=[];offset=12
while offset<len(raw):
 size,kind=struct.unpack_from('<II',raw,offset);payload=raw[offset+8:offset+8+size];assert len(payload)==size;chunks.append((kind,payload));offset+=8+size
assert offset==len(raw)and chunks[0][0]==0x4e4f534a;old=json.loads(chunks[0][1]);new=copy.deepcopy(old);changes=[];textures=[]
for i,m in enumerate(new.get('materials',[])):
 name=m.get('name');assert name in palette['materials'],('Missing exact source material',name);s=palette['materials'][name];pbr=m.get('pbrMetallicRoughness',{})
 if 'baseColorTexture'in pbr:textures.append({'index':i,'name':name,'reason':'Image texture and factor preserved'});continue
 if 'baseColorFactor'in pbr:textures.append({'index':i,'name':name,'reason':'Existing explicit base colour factor preserved'});continue
 assert not any(x['node_type']=='ShaderNodeTexImage'for x in s['base_colour_link_source']),('Image source missing from GLB material',name)
 assert s['intended_verified'],('Source palette requires explicit review',name);colour=s['intended_base_rgba'];assert len(colour)==4 and all(math.isfinite(x)and 0<=x<=1 for x in colour);before=pbr.get('baseColorFactor',[1.,1.,1.,1.]);colour=[*colour[:3],before[3]]
 if all(abs(x-y)<1e-7 for x,y in zip(before,colour)):continue
 changes.append({'material_index':i,'material_name':name,'before_rgba':before,'before_was_implicit_white':'baseColorFactor'not in pbr,'after_rgba':colour,'source_choice':s['source_choice'],'existing_alpha_preserved':True,'source_palette_rgba':s['intended_base_rgba'],'base_colour_link_source':s['base_colour_link_source']});m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=colour
assert changes,'No base-colour differences found'
def without_colours(d):
 d=copy.deepcopy(d)
 for m in d.get('materials',[]):
  q=m.get('pbrMetallicRoughness')
  if q is not None:
   q.pop('baseColorFactor',None)
   if not q:m.pop('pbrMetallicRoughness',None)
 return d
noncolour_before=sha(canon(without_colours(old)));noncolour_after=sha(canon(without_colours(new)));assert noncolour_before==noncolour_after
geometry_keys=['accessors','bufferViews','buffers','meshes','nodes','scenes','scene','skins','animations','images','textures','samplers'];structure_before=sha(canon({k:old.get(k)for k in geometry_keys}));structure_after=sha(canon({k:new.get(k)for k in geometry_keys}));assert structure_before==structure_after
js=json.dumps(new,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);newchunks=[(chunks[0][0],js),*chunks[1:]];body=b''.join(struct.pack('<II',len(data),kind)+data for kind,data in newchunks);fixed=struct.pack('<4sII',b'glTF',2,12+len(body))+body
binary=[{'type':kind,'bytes':len(data),'before_sha256':sha(data),'after_sha256':sha(newchunks[i][1])}for i,(kind,data)in enumerate(chunks)if i>0];assert binary and all(x['before_sha256']==x['after_sha256']for x in binary)
name=a.station+'_coastal_station_colour_v02.glb';zp=out/(name+'.zip')
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.writestr(name,fixed)
with zipfile.ZipFile(zp)as z:assert z.testzip()is None and sha(z.read(name))==sha(fixed)
assert sha(source.read_bytes())==eq['zip_sha256'];assert sha(Path(palette['source_blend']).read_bytes())==palette['source_blend_sha256']
shutil.copy2(pp,out/'SOURCE_MATERIALS.json');shutil.copy2(eqp,out/'ORIGINAL_EXPORT_QA.json');shutil.copy2(Path(__file__),out/'PATCH_SOURCE.py')
report={'schema_version':1,'station_code':a.station,'status':'Material-only portable correction; independent acceptance pending','source_blend_sha256':palette['source_blend_sha256'],'source_export_zip':str(source),'source_export_zip_sha256':eq['zip_sha256'],'source_glb_sha256':sha(raw),'corrected_glb_sha256':sha(fixed),'corrected_glb_bytes':len(fixed),'zip_file':zp.name,'zip_bytes':zp.stat().st_size,'zip_sha256':sha(zp.read_bytes()),'palette_sha256':sha(pp.read_bytes()),'patch_script_sha256':sha(Path(__file__).read_bytes()),'material_changes':changes,'texture_materials_preserved':textures,'before_materials_sha256':sha(canon(old.get('materials',[]))),'after_materials_sha256':sha(canon(new.get('materials',[]))),'non_colour_json_before_sha256':noncolour_before,'non_colour_json_after_sha256':noncolour_after,'geometry_node_texture_structure_before_sha256':structure_before,'geometry_node_texture_structure_after_sha256':structure_after,'binary_chunks':binary,'source_blend_and_old_export_unchanged':True,'zip_lossless_verified':True,'limitation':'Base colours are restored from exact Blend material settings. Procedural noise, paving and bump patterns remain native Blend features; geometry and embedded sign images are unchanged.'};(out/'COLOUR_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps({'station':a.station,'changed_materials':len(changes),'zip':str(zp),'zip_sha256':report['zip_sha256'],'binary_identical':True,'all_non_colour_json_identical':True}),flush=True)
