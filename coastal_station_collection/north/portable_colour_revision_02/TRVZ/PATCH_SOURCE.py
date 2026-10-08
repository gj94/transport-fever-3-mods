"""Fill only absent untextured GLB RGB factors; retain all other data exactly."""
import json,struct,hashlib,copy,math
sha=lambda b:hashlib.sha256(b).hexdigest()
def patch(raw,colors):
 assert raw[:4]==b'glTF' and struct.unpack_from('<I',raw,8)[0]==len(raw);chunks=[];i=12
 while i<len(raw):
  n,t=struct.unpack_from('<II',raw,i);chunks.append((t,raw[i+8:i+8+n]));i+=8+n
 assert i==len(raw) and chunks[0][0]==0x4e4f534a
 old=json.loads(chunks[0][1]);new=copy.deepcopy(old);changes=[]
 for i,m in enumerate(new.get('materials',[])):
  p=m.get('pbrMetallicRoughness',{})
  if 'baseColorFactor' in p or 'baseColorTexture' in p:continue
  name=m['name'];rgb=colors[name][:3];assert len(rgb)==3 and all(math.isfinite(v) and 0<=v<=1 for v in rgb);rgba=[*rgb,1.0];m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=rgba;changes.append({'index':i,'name':name,'old_implicit_factor':[1,1,1,1],'new_factor':rgba})
 def strip(doc):
  d=copy.deepcopy(doc)
  for m in d.get('materials',[]):
   q=m.get('pbrMetallicRoughness',{});q.pop('baseColorFactor',None)
   if not q:m.pop('pbrMetallicRoughness',None)
  return d
 assert strip(old)==strip(new)
 js=json.dumps(new,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);outchunks=[(chunks[0][0],js),*chunks[1:]];body=b''.join(struct.pack('<II',len(b),t)+b for t,b in outchunks);out=struct.pack('<4sII',b'glTF',2,12+len(body))+body
 return out,{'old_glb_sha256':sha(raw),'new_glb_sha256':sha(out),'changed_materials':changes,'binary_chunks':[{'type':t,'bytes':len(b),'unchanged_sha256':sha(b)} for t,b in chunks[1:]],'binary_identical':True,'all_non_colour_json_identical':True,'alpha_semantics_unchanged':True,'existing_factors_and_textures_unchanged':True}
