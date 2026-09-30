"""Lossless Blender-native compression with full asset-structure signature verification."""
import bpy,json,hashlib,os
from pathlib import Path
P=Path(__file__).resolve().parent

def signature(k):
 root=bpy.data.objects['LHB_'+k+'_ROOT_metres'];bpy.context.view_layer.update();records=[]
 for o in sorted([root]+list(root.children_recursive),key=lambda o:o.name):
  r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_local':[x for row in o.matrix_local for x in row],'properties':{key:str(o[key]) for key in o.keys()},'modifiers':[{'type':m.type,'width':getattr(m,'width',None),'segments':getattr(m,'segments',None)} for m in o.modifiers]}
  if o.type=='MESH':r.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons],face_materials=[f.material_index for f in o.data.polygons],materials=[m.name if m else None for m in o.data.materials])
  if o.type=='FONT':r.update(text=o.data.body,size=o.data.size,extrude=o.data.extrude)
  records.append(r)
 mats=[]
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  mats.append({'name':m.name,'diffuse':list(m.diffuse_color),'principled':{n:list(p.inputs[n].default_value) if n=='Base Color' else p.inputs[n].default_value for n in ['Base Color','Metallic','Roughness','Transmission Weight','Alpha','IOR']} if p else None})
 return hashlib.sha256(json.dumps({'objects':records,'materials':mats},sort_keys=True).encode()).hexdigest()
results=[]
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 path=P/'models'/('LHB_'+k+'.blend');before=path.stat().st_size;bpy.ops.wm.open_mainfile(filepath=str(path));sig=signature(k);temp=P/'models'/('LHB_'+k+'_compressed_tmp.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);bpy.ops.wm.open_mainfile(filepath=str(temp));after_sig=signature(k);assert sig==after_sig,(k,sig,after_sig);os.replace(temp,path);results.append({'variant':k,'passed':True,'asset_structure_signature_sha256':sig,'bytes_before':before,'bytes_after':path.stat().st_size,'master_sha256':hashlib.sha256(path.read_bytes()).hexdigest()});print(k,'compression verified',before,path.stat().st_size,flush=True)
(P/'qa/native_compression_verification.json').write_text(json.dumps(results,indent=2))
