"""Apply the reviewed EC-only fabric refinement to existing source masters."""
import bpy,sys,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'));from ec_upholstery_refine import apply_to_mesh
reports={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def controls():return {o.name:(o.parent.name if o.parent else None,tuple(v for row in o.matrix_world for v in row)) for o in bpy.data.objects if o.type=='EMPTY'}
def seat_bounds(objects):return {o.name:([min((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)],[max((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)]) for o in objects}
for kind in ['TC_EC','NDTC_EC','NDTC_EC2']:
 path=OUT/'cars'/f'VB_{kind}.blend';before_sha=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 seats=[o for o in bpy.data.objects if o.type=='MESH' and o.get('detail_role')=='passenger_seat_instance'];assert len(seats)==52 and len({o.data.as_pointer() for o in seats})==1
 me=seats[0].data
 if me.get('ec_fabric_refinement')=='bounded_catmull_clark_2':raise RuntimeError(f'{kind} is already refined; do not patch twice')
 ctl=controls();bb=seat_bounds(seats);r=apply_to_mesh(me);me['ec_fabric_refinement_report']=json.dumps(r);bpy.context.view_layer.update();aa=seat_bounds(seats)
 err=max(abs(bb[n][a][k]-aa[n][a][k]) for n in bb for a in range(2) for k in range(3));assert err<1e-6 and controls()==ctl
 pairs=[]
 for i,a in enumerate(seats):
  for b in seats[i+1:]:
   if abs(a.parent.location.x-b.parent.location.x)>.0001:continue
   gap=max(aa[a.name][0][1]-aa[b.name][1][1],aa[b.name][0][1]-aa[a.name][1][1]);assert gap>=-.00001;pairs.append(gap)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 report={'source_before_sha256':before_sha,'source_after_sha256':sha(path),'passenger_mesh_instances':len(seats),'protected_controls_unchanged':True,'all_seat_envelopes_max_error_m':err,'minimum_adjacent_seat_gap_m':min(pairs),'refinement':r}
 reports[kind]=report
 q=OUT/'qa'/f'VB_{kind}.json';d=json.loads(q.read_text());d['post_build_ec_refinement']=report;d['component_sha256']['interiors.py']=sha(OUT/'components/interiors.py');d['component_sha256']['ec_upholstery_refine.py']=sha(OUT/'components/ec_upholstery_refine.py');d['components']['interiors']['ec_fabric_refinement']=r
 obs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('VB02_INT_')];d['components']['interiors']['mesh_vertices_instanced']=sum(len(o.data.vertices) for o in obs);d['components']['interiors']['mesh_triangles_instanced']=sum(len(p.vertices)-2 for o in obs for p in o.data.polygons);q.write_text(json.dumps(d,indent=2));print('EC_REFINED',kind,err,min(pairs),flush=True)
(OUT/'qa/ec_upholstery_refinement.json').write_text(json.dumps(reports,indent=2))
