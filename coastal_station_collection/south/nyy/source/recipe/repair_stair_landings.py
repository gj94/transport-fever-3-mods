"""Narrow, documented stair-surface correction, preserving unrelated geometry/materials."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent));from access_geometry import approach_end,link_clearance
args=sys.argv[sys.argv.index('--')+1:];code=args[0].upper();src=Path(args[1]).resolve();R=Path(args[2]).resolve();R.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;oldsha=hashlib.sha256(src.read_bytes()).hexdigest();Q=json.loads((R/'QA_BUILD.json').read_text());col=bpy.data.collections['23_FOOTBRIDGE_RECONSTRUCTED'];prefixes=['Stair non-slip tread','Stair yellow nosing','Stair structural stringer','Stair handrail','Stair baluster'];M={};oldbounds=[]
for o in list(S.objects):
 if any(o.name.startswith(n) for n in prefixes):
  for n in prefixes:
   if o.name.startswith(n) and o.data.materials:M.setdefault(n,o.data.materials[0])
  oldbounds.extend([o.matrix_world@Vector(v) for v in o.bound_box]);bpy.data.objects.remove(o,do_unlink=True)
batch={};F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def box(n,p,sz):
 vs,fs=batch.setdefault(n,([],[]));k=len(vs);vs.extend([(p[0]+i*sz[0]/2,p[1]+j*sz[1]/2,p[2]+h*sz[2]/2) for i,j,h in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]);fs.extend(tuple(k+i for i in f) for f in F)
def beam(n,a,b,r):
 a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)))
 if v.length<.001:v=u.cross(Vector((0,1,0)))
 v.normalize();w=u.cross(v);vs,fs=batch.setdefault(n,([],[]));k=len(vs)
 for p in [a,b]:
  for i in range(8):vs.append(tuple(p+r*(v*math.cos(i*math.tau/8)+w*math.sin(i*math.tau/8))))
 fs.extend([tuple(k+i for i in range(7,-1,-1)),tuple(k+i for i in range(8,16))]+[(k+i,k+(i+1)%8,k+(i+1)%8+8,k+i+8) for i in range(8)])
checks=[];newbounds=[]
for f in Q['footbridges']:
 fx,y=f['x'],f['y'];deck=f['deck_height'];top=deck+.11;low=.964;steps=42;rise=(top-low)/steps;edge=fx+2.275;first=edge+.15;end=edge+steps*.30
 for j in range(steps):
  x=first+j*.30;z=top-(j+1)*rise;box('Stair non-slip tread',(x,y,z-.065),(.30,2.1,.13));box('Stair yellow nosing',(x+.137,y,z+.002),(.023,2.1,.004))
 for sg in [-1,1]:
  yy=y+sg*1.06;beam('Stair structural stringer',(edge,yy,top-.18),(end,yy,low-.12),.065);beam('Stair handrail',(edge,yy,top+1),(end,yy,low+1),.030)
  for j in range(0,steps,3):x=first+j*.30;z=top-(j+1)*rise;beam('Stair baluster',(x,yy,z),(x,yy,z+1),.018)
 f.update(landing_start_x=first,landing_end_x=end,landing_top_z=top,first_tread_top_z=top-rise,nominal_rise_m=rise,stair_transition_version=2)
 newbounds.extend([Vector((edge,y-1.1,low-.2)),Vector((end,y+1.1,top+1.1))]);checks.append({'y':y,'landing_edge_x':edge,'landing_top_expected':top,'nominal_rise_m':rise})
for n,(vs,fs) in batch.items():
 me=bpy.data.meshes.new(n+' repaired mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);col.objects.link(o);me.materials.append(M.get(n,bpy.data.materials['concrete']))
if any(o.name.startswith('Toilet annex floor') for o in S.objects) and not Q['building'].get('sanitary_annex_approach'):
 b=Q['building'];bx,by=b['center'];side=b['side'];px=bx+b['width']/2+5;ya=by-side*1.95;D=json.loads((R/'source/layout.json').read_text());yb=approach_end(D,px,by,side)[0];clearance=link_clearance(D,px,ya,yb,1.6);vv=[(px-.8,ya,-.2),(px+.8,ya,-.2),(px+.8,yb,-.2),(px-.8,yb,-.2),(px-.8,ya,1.005),(px+.8,ya,1.005),(px+.8,yb,.964),(px-.8,yb,.964)];ff=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new('Reconstructed sanitary annex approach mesh');me.from_pydata(vv,[],ff);me.materials.append(bpy.data.materials['concrete']);o=bpy.data.objects.new('Reconstructed sanitary annex approach',me);bpy.data.collections['35_BUILDING_ACCESS'].objects.link(o);newbounds.extend(Vector(v) for v in vv);Q['building']['sanitary_annex_approach']={'center_x':px,'width_m':1.6,'endpoints':[[px,ya,1.005],[px,yb,.964]],'basis':'Explicitly reconstructed continuous sanitary-annex connection','clearance':clearance}
if code=='NYY':
 # Independent photo review requested a readable name on the photographed pale fascia.
 b=Q['building'];bx=b['center'][0];side=b['side'];front=b['front_y'];o=S.objects.get('NYY portico name')
 if o:
  oldbounds.extend([o.matrix_world@Vector(v) for v in o.bound_box]);o.data.size=.40;o.data.materials.clear();o.data.materials.append(bpy.data.materials['dark']);o.location=(bx,front+side*4.32,.95+3.94)
 p=(bx,front+side*4.28,.95+3.94);sz=(8.4,.055,.44);vs=[(p[0]+i*sz[0]/2,p[1]+j*sz[1]/2,p[2]+h*sz[2]/2) for i,j,h in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 me=bpy.data.meshes.new('NYY pale fascia panel mesh');me.from_pydata(vs,[],F);me.materials.append(bpy.data.materials['ivory']);ob=bpy.data.objects.new('NYY pale fascia name panel',me);bpy.data.collections['32_ARCHITECTURAL_SIGNS'].objects.link(ob);newbounds.extend(Vector(v) for v in vs)
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();errors=[]
for q in checks:
 def floor(x):
  hit=S.ray_cast(dep,Vector((x,q['y'],8.12)),Vector((0,0,-1)),distance=8)
  return {'z':float(hit[1].z),'object':hit[4].name} if hit[0] else None
 q['landing_actual']=floor(q['landing_edge_x']-.01);q['first_tread_actual']=floor(q['landing_edge_x']+.01)
 if not q['landing_actual'] or not q['first_tread_actual']:errors.append('missing floor')
 else:
  q['actual_transition_rise_m']=q['landing_actual']['z']-q['first_tread_actual']['z']
  if not .12<q['actual_transition_rise_m']<.19:errors.append('excessive top rise')
 q['surface_samples']=[floor(q['landing_edge_x']+.15+j*.30) for j in range(42)]
 if any(x is None for x in q['surface_samples']):errors.append('unsupported tread')
assert not errors,errors
Q.update(stair_transition_version=2,objects=len(S.objects),meshes=sum(o.type=='MESH' for o in S.objects),vertices=sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),polygons=sum(len(o.data.polygons) for o in S.objects if o.type=='MESH'),stair_repair_input_sha256=oldsha)
(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));S['stair_transition_version']=2;S['stair_repair_input_sha256']=oldsha;dest=R/f'{code}_station_v01.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);newsha=hashlib.sha256(dest.read_bytes()).hexdigest()
report={'station':code,'input_source_sha256':oldsha,'output_source_sha256':newsha,'scope':'Only tread/nosing/stringer/handrail/baluster mesh assemblies and repair metadata changed. Original upper landing retained; first tread begins immediately beyond its outer edge, ordinary equal rise. Where a detached sanitary annex exists, its short reconstructed platform access link is added. NYY additionally receives its explicitly requested pale fascia and contrasting name-text repair.','geometry_surface_checks':checks,'errors':errors,'status':'Actual Blender floor rays passed ordinary upper transition and42supported tread centers'};(R/'QA_STAIR_REPAIR.json').write_text(json.dumps(report,indent=2))
# Conservatively retain only views whose camera frustum excludes the entire changed envelope.
pts=oldbounds+newbounds;lo=Vector((min(v.x for v in pts),min(v.y for v in pts),min(v.z for v in pts)));hi=Vector((max(v.x for v in pts),max(v.y for v in pts),max(v.z for v in pts)));corners=[Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]];prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());rerender=[];retained=[]
for name,r in prov['views'].items():
 cam=S.objects.get(r.get('camera',''))
 if cam is None:rerender.append(name[:2]);continue
 oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldlens=cam.data.lens
 ov=r.get('camera_override')
 if ov:
  cam.location=ov['location'];cam.rotation_euler=(Vector(ov['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=ov['lens_mm']
 vv=[world_to_camera_view(S,cam,p) for p in corners];out=(max(v.z for v in vv)<=0 or max(v.x for v in vv)<0 or min(v.x for v in vv)>1 or max(v.y for v in vv)<0 or min(v.y for v in vv)>1)
 cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.lens=oldlens
 if out:
  r['unchanged_view_verified']=True;r['current_source_scene_sha256']=newsha;r['inheritance_basis']='Changed stair AABB entirely outside recorded camera frustum; no other geometry or material edits';retained.append(name)
 else:rerender.append(name[:2])
prov['current_source_scene_sha256']=newsha;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));lineage={'station':code,'input_source_sha256':oldsha,'output_source_sha256':newsha,'changed_bounds':[list(lo),list(hi)],'retained_views':retained,'rerender_prefixes':sorted(set(rerender))};(R/'REPAIR_LINEAGE.json').write_text(json.dumps(lineage,indent=2));print(json.dumps(lineage,indent=2),flush=True)
