import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];oldhash=hashlib.sha256(src.read_bytes()).hexdigest();assert oldhash==q['blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));d=json.load(open(P/'references/plan.json'));by=d['main_building']['center'][1];yy=by+65
old=bpy.data.collections.get('07 | Pedestrian footbridge reconstructed geometry')
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
C=bpy.data.collections.new('07 | Pedestrian footbridge reconstructed geometry');bpy.context.scene.collection.children.link(C);geo={}
def add(v,f,mat):
 g=geo.setdefault(mat,{'v':[],'f':[]});n=len(g['v']);g['v'].extend(v);g['f'].extend([tuple(n+i for i in ff)for ff in f])
def box(loc,di,m):
 x,y,z=loc;a,b,c=[v/2 for v in di];v=[(x+u*a,y+w*b,z+t*c)for u,w,t in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];add(v,[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)],m)
def beam(a,b,w,m):
 a,b=Vector(a),Vector(b);q0=(b-a).to_track_quat('Z','Y');ce=(a+b)/2;l=(b-a).length/2;h=w/2;v=[tuple(q0@Vector((u*h,v*h,t*l))+ce)for u,v,t in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];add(v,[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)],m)
def span(pp,y):
 xx=[]
 for a,b in zip(pp,pp[1:]+pp[:1]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-5:xx.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return(min(xx),max(xx))if len(xx)>1 else None
px=[]
for p in d['platforms']:
 sp=span(p['xy'],yy)
 if sp and sp[1]-sp[0]>4:px.append((sum(sp)/2,sp[1]-sp[0]))
assert len(px)>1
x0=min(x for x,w in px);x1=max(x for x,w in px);deck=8.55;steel='steel';roof='roof';box(((x0+x1)/2,yy,deck),(x1-x0+3,2.5,.30),steel)
for ys in [-1.17,1.17]:
 segs=[(x0-1.4,x1+1.4)]
 if ys<0:
  for xx,ww in px:
   out=[]
   for a,b in segs:
    if a<xx-1.15:out.append((a,min(b,xx-1.15)))
    if b>xx+1.15:out.append((max(a,xx+1.15),b))
   segs=[(a,b)for a,b in out if b>a]
 for a,b in segs:
  beam((a,yy+ys,deck+1.2),(b,yy+ys,deck+1.2),.065,steel);beam((a,yy+ys,deck+.35),(b,yy+ys,deck+.35),.05,steel)
 for xx in range(int(x0),int(x1)+2):
  if ys<0 and any(abs(xx-x)<1.15 for x,w in px):continue
  beam((xx,yy+ys,deck),(xx,yy+ys,deck+1.2),.035,steel)
run=15.2;rise=deck+.15-1.45;steps=44;syend=yy-1.25
for x,w in px:
 for xx in[x-1.15,x+1.15]:beam((xx,yy,1.45),(xx,yy,deck),.18,steel)
 for j in range(steps):
  zz=1.45+(j+1)*rise/steps-.05;sy=syend-run+(j+.5)*run/steps;box((x,sy,zz),(2.2,run/steps+.025,.10),steel)
 for sg in[-1,1]:
  beam((x+sg*1.05,syend-run,1.35),(x+sg*1.05,syend,deck+.05),.14,steel);beam((x+sg*1.02,syend-run,2.45),(x+sg*1.02,syend,deck+1.15),.055,steel)
  for j in range(0,steps,4):beam((x+sg*1.02,syend-run+j*run/steps,1.45+j*rise/steps),(x+sg*1.02,syend-run+j*run/steps,2.45+j*rise/steps),.035,steel)
box(((x0+x1)/2,yy,deck+2.4),(x1-x0+4,3.2,.1),roof)
for m,g in geo.items():
 me=bpy.data.meshes.new('Repaired bridge '+m);me.from_pydata(g['v'],[],g['f']);me.update();o=bpy.data.objects.new('07 | Pedestrian footbridge reconstructed geometry / '+m,me);C.objects.link(o);me.materials.append(bpy.data.materials[m])
# Flush original checker-color tile patches to floor; remove an8mm unintended air gap.
tile_vertices=0
for col in bpy.data.collections:
 if not col.name.startswith('05 |'):continue
 for obj in col.objects:
  if obj.type!='MESH':continue
  for v in obj.data.vertices:
   if abs(v.co.z-1.508)<.00001:v.co.z=1.500;tile_vertices+=1
   elif abs(v.co.z-1.520)<.00001:v.co.z=1.502;tile_vertices+=1
new=P/(q['station_code']+'_coastal_station_v02.blend');bpy.ops.wm.save_as_mainfile(filepath=str(new),compress=True);newhash=hashlib.sha256(new.read_bytes()).hexdigest();(P/'QA_BUILD_before_bridge_patch.json').write_text(json.dumps(q,indent=2));q.update({'blend_file':new.name,'blend_sha256':newhash,'blend_bytes':new.stat().st_size,'bridge_deck_top_m':deck+.15,'bridge_deck_underside_m':deck-.15,'stair_end_y':syend,'stair_landing_method':'Last tread ends at deck leading edge; tread top and deck top both8.70m. No treads run below deck.','bridge_patch':{'original_blend_file':src.name,'original_blend_sha256':oldhash,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'changed_collections':['07 | Pedestrian footbridge reconstructed geometry','05 | Furnished reconstructed interiors: flush floor color tiles only'],'flushed_tile_vertices':tile_vertices,'other_scene_geometry_unchanged':True}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('BRIDGE_PATCH_COMPLETE',q['station_code'],newhash)
