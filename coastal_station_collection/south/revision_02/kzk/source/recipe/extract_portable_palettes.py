"""Read exact authored base palette; never save or alter source scenes."""
import bpy,json,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parents[1];codes=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [r['station_code'] for r in json.loads((B/'stations.json').read_text())]
for code in codes:
 R=B/code.lower();rev=B/'revision_02'/code.lower()
 if (rev/f'{code}_station_v01.blend').exists():R=rev
 src=R/f'{code}_station_v01.blend';h=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));colors={};materials={}
 for m in bpy.data.materials:
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
  rgba=list(p.inputs['Base Color'].default_value) if p else list(m.diffuse_color);colors[m.name]=rgba
  materials[m.name]={'authored_base_default_rgba':rgba,'diffuse_rgba':list(m.diffuse_color),'base_colour_links':[{'name':l.from_node.name,'node_type':l.from_node.bl_idname} for l in p.inputs['Base Color'].links] if p else [],'choice':'Explicit authored Principled base default; procedural variation remains in native scene'}
 assert hashlib.sha256(src.read_bytes()).hexdigest()==h
 out=B/'portable_colour_revision_02'/code;out.mkdir(parents=True,exist_ok=True);path=out/'SOURCE_PALETTE.json';assert not path.exists(),'Palette already written; preserve immutable evidence'
 path.write_text(json.dumps({'station':code,'source_blend':str(src),'source_blend_sha256':h,'source_blend_unchanged':True,'colors':colors,'materials':materials},indent=2));print('PALETTE',code,h,flush=True)
