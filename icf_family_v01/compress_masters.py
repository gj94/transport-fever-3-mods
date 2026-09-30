"""Lossless native Blender compression with full mesh/hierarchy reopen signature check."""
import bpy,json,hashlib,array
from pathlib import Path
P=Path(__file__).resolve().parent
paths=[P/v/f'ICF_{v}_master.blend' for v in ['1A','2A','3A','2S','CC','SL','GS']]+[P/'qa'/'two_coach_straight_fixture.blend']
def signature():
 bpy.context.view_layer.update();h=hashlib.sha256();counts={'mesh_objects':0,'vertices':0,'polygons':0,'empties':0}
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  h.update(json.dumps({'name':o.name,'parent':o.parent.name if o.parent else None,'type':o.type,'world':[list(r) for r in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []},sort_keys=True).encode())
  if o.type=='MESH':
   me=o.data;co=array.array('f',[0])* (len(me.vertices)*3);me.vertices.foreach_get('co',co);h.update(co.tobytes());ind=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',ind);h.update(ind.tobytes());counts['mesh_objects']+=1;counts['vertices']+=len(me.vertices);counts['polygons']+=len(me.polygons)
  elif o.type=='EMPTY':counts['empties']+=1
 return h.hexdigest(),counts
reports=[]
for path in paths:
 bpy.ops.wm.open_mainfile(filepath=str(path));before,counts=signature();old=path.stat().st_size;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));after,newcounts=signature();assert before==after and counts==newcounts,path
 reports.append({'file':str(path.relative_to(P)),'passed':True,'before_bytes':old,'compressed_bytes':path.stat().st_size,'scene_geometry_hierarchy_sha256':after,**counts});print('LOSSLESS_COMPRESSED',reports[-1],flush=True)
(P/'qa'/'compressed_master_roundtrip.json').write_text(json.dumps(reports,indent=2))
