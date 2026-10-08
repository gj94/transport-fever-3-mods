"""Keep the mapped dogleg; move only the reconstructed third flight within its narrowing island footprint."""
import bpy,json,sys,hashlib,math,ast
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));sc=bpy.context.scene;D=json.load(open(P/'references/plan.json'));CODE='KYJ';BATCH={};COL=None;CAT=None;metrics={};M={n:bpy.data.materials[n]for n in ['steel','roofblue']};platform_info=[]
for record,pf in zip(q['platform_parameters'],D['platforms']):r=record.copy();r['poly']=pf['xy'];platform_info.append(r)
master=P/'BUILD_SOURCE.py';source=master.read_text();tree=ast.parse(source);names={'coll','mesh','batchgeom','box','beam','polyplate','platform_span'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(master),'exec'))
old=bpy.data.collections.get('07 | Pedestrian footbridge reconstructed geometry');assert old
for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(old)
chunk=source[source.index('# Kayamkulam has a mapped dogleg pedestrian bridge.'):source.index('# Station context uses actual mapped road centerlines')]
needle="fx=max(sp[0]+1.30,min(sp[1]-1.30,fx));syend=deck_front_at(fx)"
rep="fx=max(sp[0]+1.30,min(sp[1]-1.30,fx))\n  if p['ref']=='4;5':fx=44.06621618210055\n  syend=deck_front_at(fx)";assert needle in chunk;chunk=chunk.replace(needle,rep);exec(compile(chunk,str(Path(__file__)),'exec'))
for(cat,mn),g in BATCH.items():COL=g['col'];mesh(cat+' / '+mn,g['v'],g['f'],g['m'])
assert len(metrics['bridge_flights'])==3
out=P/'KYJ_coastal_station_v03.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update(metrics);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'object_count':len(sc.objects),'mesh_objects':sum(o.type=='MESH'for o in sc.objects),'mesh_vertices':sum(len(o.data.vertices)for o in sc.objects if o.type=='MESH'),'mesh_faces':sum(len(o.data.polygons)for o in sc.objects if o.type=='MESH'),'bridge_patch':{'source_blend_sha256':sha,'source_blend_file':src.name,'changed_collection':'07 | Pedestrian footbridge reconstructed geometry','reason':'Move reconstructed platform4/5 flight inward to x44.066216 and update its deck-mouth railing. Its whole run now lies inside the common source-platform interval, including the narrowed toe.','common_center_interval_with_1_30m_margins':[43.229130837679186,44.903301526521915],'mapped_platform_and_bridge_route_unchanged':True,'all_nonbridge_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('KYJ_THIRD_FLIGHT_CORRECTED',q['blend_sha256'],q['bridge_flights'])
