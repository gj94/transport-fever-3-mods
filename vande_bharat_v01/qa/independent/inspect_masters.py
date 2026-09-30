"""Independent read-only modelling inspection; no TF3 conversion or source edits."""
import bpy, json, sys, re, math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [str(p) for p in sorted((Path(__file__).resolve().parents[2]/'cars').glob('*.blend')) if '_baked' not in p.stem]
reports=[]
for source in args:
 bpy.ops.wm.open_mainfile(filepath=source)
 objs=list(bpy.data.objects)
 roots=[o for o in objs if o.type=='EMPTY' and 'ROOT' in o.name.upper() and not o.parent]
 meshes=[o for r in roots for o in r.children_recursive if o.type=='MESH']
 seen=set();meshes=[o for o in meshes if not(o.name in seen or seen.add(o.name))]
 points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 def xyz(v):return [round(float(x),7) for x in v]
 normalized={}
 for o in objs:
  key=re.sub(r'[^a-z0-9_]','_',o.name.lower());normalized.setdefault(key,[]).append(o.name)
 r={'file':source,'units':{'system':bpy.context.scene.unit_settings.system,'scale':bpy.context.scene.unit_settings.scale_length},'root_names':[o.name for o in roots],'mesh_count':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'bounds':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]} if points else None,'materials':sorted({m.name for o in meshes for m in o.data.materials if m}),'normalized_name_collisions':{k:v for k,v in normalized.items() if len(v)>1},'markers':{},'pivots':{},'unparented_meshes':[o.name for o in objs if o.type=='MESH' and not o.parent]}
 for o in objs:
  if o.type=='EMPTY' and any(t in o.name.upper() for t in ('COUPLING','DRIVER','PAX_','PASSENGER','AXLE','BOGIE','DOOR','PANTO','LIGHT')):
   data={'parent':o.parent.name if o.parent else None,'world_position':xyz(o.matrix_world.translation),'local_position':xyz(o.matrix_local.translation),'world_euler':xyz(o.matrix_world.to_euler()),'custom_properties':{k:str(v) for k,v in o.items()}}
   (r['markers'] if any(t in o.name.upper() for t in ('COUPLING','DRIVER','PAX_','PASSENGER')) else r['pivots'])[o.name]=data
 r['seat_count']=sum(o.type=='EMPTY' and o.name.startswith(('PAX_','PASSENGER_SEATED_')) for o in objs)
 r['finite_vertices']=all(math.isfinite(x) for p in points for x in p)
 reports.append(r)
out=(Path(__file__).resolve().parent/'independent_inventory.json');out.write_text(json.dumps(reports,indent=2));print('INDEPENDENT_INVENTORY',str(out),len(reports))
