"""Independently validate a source-palette-only GLB revision.
Expected palette JSON: {source_blend_sha256: str, colors: {material_name: [r,g,b,a]}}.
Only RGB fallback additions are permitted; all geometry, textures and alpha semantics stay unchanged.
"""
import argparse,json,struct,zipfile,hashlib,copy,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('--palette',required=True);p.add_argument('--source-sha256',required=True);p.add_argument('--out',required=True);a=p.parse_args()
def load(path):
 f=Path(path);container=f.read_bytes();raw=container;member=None
 if f.suffix=='.zip':
  with zipfile.ZipFile(f)as z:
   names=[n for n in z.namelist()if n.lower().endswith('.glb')];assert len(names)==1;member=names[0];raw=z.read(member)
 assert raw[:4]==b'glTF'and struct.unpack_from('<I',raw,4)[0]==2 and struct.unpack_from('<I',raw,8)[0]==len(raw)
 chunks=[];doc=None;off=12
 while off<len(raw):
  size,kind=struct.unpack_from('<II',raw,off);off+=8;data=raw[off:off+size];assert len(data)==size and size%4==0;off+=size
  if kind==0x4e4f534a:assert doc is None;doc=json.loads(data)
  else:chunks.append({'type':kind,'bytes':size,'sha256':hashlib.sha256(data).hexdigest()})
 assert off==len(raw)and doc is not None
 return doc,{'path':str(f),'glb_sha256':hashlib.sha256(raw).hexdigest(),'container_sha256':hashlib.sha256(container).hexdigest(),'member':member,'non_json_chunks':chunks}
old,oi=load(a.before);new,ni=load(a.after);palette=json.loads(Path(a.palette).read_text());assert palette['source_blend_sha256']==a.source_sha256;colors=palette['colors'];errors=[];changes=[]
if oi['non_json_chunks']!=ni['non_json_chunks']:errors.append('Non-JSON chunks differ.')
def without_rgb(doc):
 d=copy.deepcopy(doc)
 for m in d.get('materials',[]):
  pbr=m.get('pbrMetallicRoughness',{});pbr.pop('baseColorFactor',None)
  if not pbr:m.pop('pbrMetallicRoughness',None)
 return d
if without_rgb(old)!=without_rgb(new):errors.append('JSON outside baseColorFactor changed.')
om=old.get('materials',[]);nm=new.get('materials',[])
if len(om)!=len(nm):errors.append('Material count changed.')
for i,(before,after)in enumerate(zip(om,nm)):
 name=before.get('name',str(i));bp=before.get('pbrMetallicRoughness',{});ap=after.get('pbrMetallicRoughness',{});bv=bp.get('baseColorFactor',[1,1,1,1]);av=ap.get('baseColorFactor',[1,1,1,1]);textured='baseColorTexture'in bp;explicit='baseColorFactor'in bp
 if len(av)!=4 or not all(isinstance(v,(int,float))and math.isfinite(v)and 0<=v<=1 for v in av):errors.append(f'{name}: invalid RGBA factor.');continue
 if abs(av[3]-bv[3])>1e-7:errors.append(f'{name}: alpha factor changed.')
 modified=bv!=av or ('baseColorFactor'in bp)!=('baseColorFactor'in ap)
 if (textured or explicit)and modified:errors.append(f'{name}: existing textured/explicit colour was modified.')
 if not textured and not explicit:
  if name not in colors:errors.append(f'{name}: source palette has no exact material match.');continue
  expected=colors[name][:3]
  if len(expected)!=3 or any(abs(x-y)>2e-6 for x,y in zip(av[:3],expected)):errors.append(f'{name}: RGB does not match authored source palette.')
 if modified:changes.append({'index':i,'name':name,'before_factor':bv,'before_factor_explicit':explicit,'after_factor':av,'source_rgba':colors.get(name)})
r={'status':'pass'if not errors else'fail','source_blend_sha256':a.source_sha256,'palette_path':a.palette,'palette_sha256':hashlib.sha256(Path(a.palette).read_bytes()).hexdigest(),'before':oi,'after':ni,'non_json_chunks_identical':oi['non_json_chunks']==ni['non_json_chunks'],'all_non_colour_json_identical':without_rgb(old)==without_rgb(new),'material_count':len(nm),'changed_materials':changes,'changed_count':len(changes),'errors':errors,'method':'Only absent untextured base-color fallbacks may be filled from the exact packed-source palette. Existing explicit colors, textures, alpha, alphaMode, extensions, node transforms, mesh/accessor/buffer tables and binary data are preserved. Original geometry QA remains applicable.'};Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'changed':len(changes),'errors':errors,'out':a.out}));raise SystemExit(bool(errors))
