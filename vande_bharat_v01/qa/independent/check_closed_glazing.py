import bpy,bmesh,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[2];reports=[]
for path in sorted((base/'cars').glob('*.blend')):
 if '_baked' in path.stem:continue
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not any(o.name.startswith(n) for n in ['Window_clear_glazing','Door_glass','Saloon_door_glass','Nose_windscreen','Cab_side_glass']):continue
  bm=bmesh.new();bm.from_mesh(o.data)
  rows.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'unapplied_modifiers':len(o.modifiers)})
  bm.free()
 assert rows and all(r['boundary_edges']==0 and r['nonmanifold_edges']==0 and r['signed_volume_m3']>0 and r['unapplied_modifiers']==0 for r in rows),str(rows)
 reports.append({'file':path.name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'panes':rows})
(Path(__file__).resolve().parent/'independent_closed_glazing.json').write_text(json.dumps(reports,indent=2));print('GLASS_PASS',len(reports),sum(len(r['panes']) for r in reports))
