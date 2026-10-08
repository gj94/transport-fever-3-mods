"""Inspect saved source-file external dependencies without modifying masters."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent.parent
rows=[]
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 p=P/'models'/f'LHB_{k}.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
 images=[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
 fonts=[{'name':f.name,'filepath':f.filepath,'packed':bool(f.packed_file)} for f in bpy.data.fonts if f.filepath and f.filepath!='<builtin>']
 libraries=[l.filepath for l in bpy.data.libraries]
 assert all(i['packed'] for i in images),images;assert all(f['packed'] for f in fonts),fonts;assert not libraries,libraries
 assert hashlib.sha256(p.read_bytes()).hexdigest()==before
 rows.append({'variant':k,'source_sha256':before,'external_images':images,'external_fonts':fonts,'linked_libraries':libraries,'status':'pass'})
(P/'qa/portable_dependencies.json').write_text(json.dumps({'status':'pass','scope':'Saved source masters only; render environment dependencies listed separately in external_dependency_audit.json','classes':rows},indent=2));print('PORTABLE_SOURCE_PASS',flush=True)
