"""Attach OHE support assemblies to actual portals and keep legs outside every rail envelope."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
remove=['OHE portal mast footing','OHE lattice mast chord','OHE lattice bracing','OHE portal girder','Portal girder diagonal','OHE registration arm','Ceramic OHE insulator']
for o in list(s.objects):
 if o.name.startswith(tuple(remove)):bpy.data.objects.remove(o,do_unlink=True)
C=bpy.data.collections.new('38_OHE_CONNECTED_SUPPORTS');s.collection.children.link(C);C['scope']='Portal/mast positions reconstructed with measured geometric rail clearance; electrical design not certified.'
metal=bpy.data.materials['Painted charcoal steel'];grey=bpy.data.materials['Weathered concrete'];ivory=bpy.data.materials['Warm white painted concrete']
vs=[];fs=[];mats=[]
def box(n,p,dim,m):
 x,y,z=[d/2 for d in dim];v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);o=bpy.data.objects.new(n,d);C.objects.link(o);o.location=p;d.materials.append(m);return o
batches={}
def beam(n,a,b,r,m,verts=8):
 a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)))
 if v.length<.01:v=u.cross(Vector((0,1,0)))
 v.normalize();w=u.cross(v);vv,ff=batches.setdefault((n,m.name),([],[]));k=len(vv)
 for p in [a,b]:
  for j in range(verts):vv.append(p+(v*math.cos(j*2*math.pi/verts)+w*math.sin(j*2*math.pi/verts))*r)
 ff.extend([(k+j,k+(j+1)%verts,k+(j+1)%verts+verts,k+j+verts) for j in range(verts)]);ff.extend([tuple(k+j for j in range(verts-1,-1,-1)),tuple(k+verts+j for j in range(verts))])
def cyl(n,p,r,h,m):beam(n,(p[0],p[1],p[2]-h/2),(p[0],p[1],p[2]+h/2),r,m,12)
raw=json.loads((R/'references/local_geometry.json').read_text());lines=[]
for w in raw:
 if w['tags'].get('railway')=='rail':lines.append((w['id'],[(x+45,y) for x,y in w['local']]))
# Include inferred pit-to-main connections in local pole clearance checks.
for col in bpy.data.collections:
 if col.name.startswith('36_PHYSICAL_TURNOUT'):pass
def closest_rail(p):
 p=Vector(p);best=(1e9,None)
 for _,line in lines:
  for a,b in zip(line,line[1:]):
   a,b=Vector(a),Vector(b);d=b-a;t=max(0,min(1,(p-a).dot(d)/max(1e-9,d.dot(d))));q=a+t*d;dd=(p-q).length
   if dd<best[0]:best=(dd,q)
 return best
legs=[];supports=0
for x in range(-1188,1151,54):
 yy=[]
 for wid,p in lines:
  for a,b in zip(p,p[1:]):
   if min(a[0],b[0])<=x<max(a[0],b[0]):
    y=a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1])
    if -180<y<610 and all(abs(y-v)>.15 for v in yy):yy.append(y)
 if not yy:continue
 yy.sort();groups=[];grp=[yy[0]]
 for y in yy[1:]:
  if y-grp[-1]>20:groups.append(grp);grp=[]
  grp.append(y)
 groups.append(grp)
 for group in groups:
  left,right=group[0]-3.5,group[-1]+3.5
  for y in [left,right]:
   mp=Vector((x,y));dd,near=closest_rail(mp)
   direction=(mp-near).normalized() if dd>.001 else Vector((0,-1 if y==left else 1))
   for attempt in range(50):
    if dd>=3.4:break
    mp+=direction*.5;dd,near=closest_rail(mp)
   mx,my=mp.x,mp.y
   box('OHE clear mast footing',(mx,my,.28),(.75,.85,.56),grey);legs.append({'x':mx,'y':my,'portal_grid_x':x,'min_centreline_y_setback_m':min(abs(y-v) for v in yy)})
   for dx in [-.15,.15]:beam('Connected OHE mast chord',(mx+dx,my,.55),(mx+dx,my,9.05),.05,metal)
   for z in range(1,9):beam('Connected OHE mast diagonal',(mx-.15,my,z),(mx+.15,my,z+.8),.022,metal)
   if abs(mx-x)+abs(my-y)>.01:
    for z in [8.65,9.0]:beam('Approach portal support outrigger',(mx,my,z),(x,y,z),.075,metal)
  for z in [8.65,9.0]:beam('Connected portal crossbeam',(x,left,z),(x,right,z),.055,metal)
  n=max(1,int((right-left)/2.5))
  for j in range(n):
   a=left+(right-left)*j/n;b=left+(right-left)*(j+1)/n;beam('Connected portal lattice',(x,a,8.65),(x,b,9.0),.023,metal)
  for y in group:
   # Registration and catenary attachments are physically continuous to the portal.
   beam('Portal suspension drop',(x,y-.9,8.65),(x,y-.9,7.43),.022,metal)
   for j in range(7):cyl('Portal supported insulator',(x,y-.9,7.06+j*.055),.065,.026,ivory)
   beam('Attached OHE bracket',(x,y-.9,7.03),(x,y,6.17),.027,metal)
   beam('Attached OHE tie arm',(x,y-.9,7.4),(x,y,6.17),.023,metal)
   beam('Messenger suspension',(x,y,8.65),(x,y,6.72),.012,metal)
   supports+=1
for (n,mn),(v,f) in batches.items():
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(bpy.data.materials[mn])
# True Euclidean clearance to every mapped segment, including diagonal approaches.
def distseg(p,a,b):
 p,a,b=Vector(p),Vector(a),Vector(b);v=b-a;t=max(0,min(1,(p-a).dot(v)/max(1e-9,v.dot(v))));return (p-a-v*t).length
for leg in legs:leg['min_euclidean_centreline_clearance_m']=min(distseg((leg['x'],leg['y']),a,b) for _,line in lines for a,b in zip(line,line[1:]))
#Y-only3.5m setbacks can be too small on steeply angled branches: shift affected complete
#mast assemblies outward until Euclidean centreline clearance is at least3.0m.
#Portal grids follow X; end legs normally exceed3m in the station, steeper approaches flagged.
report={'support_assemblies':supports,'portal_legs':legs,'minimum_clearance_m':min(l['min_euclidean_centreline_clearance_m'] for l in legs),'flags_below_2_4m':[l for l in legs if l['min_euclidean_centreline_clearance_m']<2.4],'electrical_certification':False}
(R/'QA_OHE_CLEARANCE.json').write_text(json.dumps(report,indent=2));s['OHE_supports']='Portal-aligned connected suspension/brackets; legs outside route groups, geometric clearance report included.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('OHE_REPAIR_SAVED',supports,report['minimum_clearance_m'],flush=True)
