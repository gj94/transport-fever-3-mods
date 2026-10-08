"""Bounded source-identifying facade additions. Rail, bridge, interiors and other scene objects unchanged."""
import bpy,sys,json,math,hashlib,ast
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));CODE=q['station_code'];assert CODE in ['AMPA','SRTL','HAD'];src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));sc=bpy.context.scene;D=json.load(open(P/'references/plan.json'));bx,by=D['main_building']['center'];DEP=max(7,D['main_building']['width']);LEN=max(12,D['main_building']['length']);SIDE=D['main_building']['public_side'];H=4.05 if LEN>25 else 3.65;eave=1.45+H;porchwidth=min(LEN+1,16 if LEN<30 else 25);COL=None;CAT=None;BATCH={};M={n:(bpy.data.materials.get(n) or bpy.data.materials['red'])for n in ['cream','red','dark','glass','wood','tile']}
master=P/'BUILD_SOURCE.py';tree=ast.parse(master.read_text());names={'coll','mesh','batchgeom','box','beam','loc','b0','be0','rooflocal'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];exec(compile(ast.Module(body=defs,type_ignores=[]),str(master),'exec'));M['white']=bpy.data.materials['white'];changed=[]
if CODE=='AMPA':
 # Remove only old shallow clerestory components, detected as disconnected upper mesh islands.
 cw=min(16,LEN*.65)
 for col in bpy.data.collections:
  if not col.name.startswith('04 |'):continue
  for ob in list(col.objects):
   if ob.type!='MESH':continue
   me=ob.data;parent=list(range(len(me.vertices)))
   def find(a):
    while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
    return a
   for e in me.edges:
    a,b=e.vertices;ra,rb=find(a),find(b)
    if ra!=rb:parent[rb]=ra
   groups={}
   for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
   remove=set()
   for ids in groups.values():
    vs=[me.vertices[i].co for i in ids];us=[v.y-by for v in vs];vvs=[(v.x-bx)*SIDE for v in vs]
    if min(v.z for v in vs)>eave+.14 and max(abs(u)for u in us)<cw/2+.85 and max(abs(v)for v in vvs)<DEP*.34+.9:remove.update(ids)
    if any(ob.name.endswith('/ '+m)for m in ['glass','wood','dark']) and min(vvs)>DEP/2-.10 and max(vvs)<DEP/2+.25 and min(us)>3.9 and max(us)<8.2 and min(v.z for v in vs)>2.70 and max(v.z for v in vs)<4.25:remove.update(ids)
   if remove:
    keep=[v for v in me.vertices if v.index not in remove];imap={v.index:i for i,v in enumerate(keep)};verts=[tuple(v.co)for v in keep];faces=[tuple(imap[i]for i in f.vertices)for f in me.polygons if not any(i in remove for i in f.vertices)];new=bpy.data.meshes.new(me.name+' source-fidelity patch');new.from_pydata(verts,[],faces);new.update()
    for m in me.materials:new.materials.append(m)
    ob.data=new;changed.append({'object':ob.name,'removed_old_clerestory_vertices':len(remove)})
coll('04A | '+CODE+' source-identifying facade refinement')
if CODE=='AMPA':
 cw=min(16,LEN*.65);v=DEP*.34+.11
 b0('Raised window-tier lower band',0,v,eave+.24,cw,.28,.35,M['cream']);b0('Raised window-tier upper band',0,v,eave+2.03,cw,.28,.42,M['cream'])
 for u in[-cw/2,cw/2]:b0('Window-tier side wall',u,0,eave+1.20,.24,DEP*.68,2.4,M['cream'])
 b0('Upper tier rear wall',0,-DEP*.34,eave+1.20,cw,.24,2.4,M['cream'])
 for j in range(4):
  u=(j-1.5)*cw/4;ww=cw/4-.35;b0('Paired dark upper glazing',u,v+.02,eave+1.10,ww,.045,1.40,M['glass'])
  for du in[-ww/2,0,ww/2]:b0('Upper glazing pale mullion',u+du,v+.06,eave+1.10,.045,.065,1.45,M['cream'])
  for zz in[eave+.40,eave+1.80]:b0('Upper glazing horizontal frame',u,v+.07,zz,ww,.075,.05,M['cream'])
 for j in range(5):b0('Upper tier masonry pier',-cw/2+j*cw/4,v,eave+1.16,.26,.32,2.35,M['cream'])
 b0('Photographed upper-tier projecting roof',0,0,eave+2.38,cw+1,DEP*.68+1.5,.20,M['cream'])
 for u in[-cw/2+.8,-cw/4,0,cw/4,cw/2-.8]:
  for j in range(3):b0('Upper coral stepped corbel',u,v+.14+j*.13,eave+1.80+j*.16,.33,.36+j*.14,.17,M['red'])
 # Central pier is offset from the through-entry axis so the modeled passage stays open.
 b0('Observed middle black portico pier',2.30,DEP/2+2.8,1.45+(H-.45)/2,.66,.72,H-.45,M['dark'])
 # Prominent perforated screen, cream flower/diamond cells, to right of the entry.
 pu=6.0;pv=DEP/2+.22
 for du in[-1.50,1.50]:b0('Cream screen side border',pu+du,pv,3.0,.16,.16,1.94,M['cream'])
 for z in[2.02,3.98]:b0('Cream screen horizontal border',pu,pv,z,3.16,.16,.16,M['cream'])
 for a in range(6):
  for b in range(4):
   u=pu+(a-2.5)*.48;z=2.25+b*.48
   for da,db in[((-.22,0),(0,.22)),((0,.22),(.22,0)),((.22,0),(0,-.22)),((0,-.22),(-.22,0))]:be0('Perforated breeze-block diamond',(u+da[0],pv,z+da[1]),(u+db[0],pv,z+db[1]),.085,M['cream'])
 detail='Raised2.4m central upper window tier; cream patterned breeze-block screen and offset middle black portico pier from the actual frontage source.'
elif CODE=='SRTL':
 # Broad stepped cream brackets read below the portico beam, as in the inspected photo.
 for center in[-6,6]:
  for sg in[-1,1]:
   for j in range(4):
    u=center+sg*(1.0+j*.65);bottom=eave-.55-j*.20;top=eave-.49;b0('Stepped cream portico corbel',u,DEP/2+2.78,(bottom+top)/2,.68,.56,max(.10,top-bottom),M['cream'])
 detail='Stepped cream underside corbels added beneath the photographed twin-gable portico; existing wings remain reconstructed.'
else:
 cw=18;pv=DEP/2+.30
 b0('Raised Haripad cream ventilator band',0,pv,eave+.72,cw,.34,1.40,M['cream'])
 for u in[-7.5,-5.4,-3.3,-1.2,1.2,3.3,5.4,7.5]:
  b0('Small recessed upper ventilation opening',u,pv+.19,eave+.72,.76,.06,.80,M['dark'])
  for du in[-.29,0,.29]:b0('Vent pale bars',u+du,pv+.235,eave+.72,.035,.04,.80,M['cream'])
 b0('Red upper projecting lintel',0,pv+.10,eave+1.46,cw+1,1.35,.23,M['red'])
 for u in[-8,-6,-4,-2,0,2,4,6,8]:
  for j in range(3):b0('Photographed red stepped ventilator corbel',u,pv+.28+j*.1,eave+.97+j*.16,.30,.45+j*.12,.17,M['red'])
 rooflocal(0,0,cw+1,DEP+1,eave+1.56,.80,M['tile'])
 detail='Raised central cream ventilator band with small dark openings, red stepped corbels and a tile cap; actual frontage source basis.'
for(cat,mn),g in BATCH.items():COL=g['col'];mesh(cat+' / '+mn,g['v'],g['f'],g['m'])
version={'AMPA':'v02','SRTL':'v03','HAD':'v03'}[CODE];out=P/(CODE+'_coastal_station_'+version+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'object_count':len(sc.objects),'mesh_objects':sum(o.type=='MESH' for o in sc.objects),'mesh_vertices':sum(len(o.data.vertices) for o in sc.objects if o.type=='MESH'),'mesh_faces':sum(len(o.data.polygons)for o in sc.objects if o.type=='MESH'),'facade_refinement':{'source_blend_sha256':sha,'source_blend_file':src.name,'details':detail,'changed_existing_objects':changed,'added_collection':'04A | '+CODE+' source-identifying facade refinement','all_other_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('SOURCE_FACADE_PATCH_DONE',CODE,q['blend_sha256'],detail)
