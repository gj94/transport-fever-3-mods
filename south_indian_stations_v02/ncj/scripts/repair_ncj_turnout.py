"""Physical reconstruction of mapped turnout node6045464001; source endpoints fixed.
Replaces all prior track and bearer components inside the correction envelope.
Not a railway fabrication drawing or verified NCJ turnout type.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'))
s=bpy.context.scene;src=json.loads((R/'references/turnout_source_nodes.json').read_text());node=next(n for n in src if n['node']=='6045464001');P=Vector((*node['position'],0));U=(Vector((191.2185802010538,54.162975051962874,0))-P).normalized();V=Vector((-U.y,U.x,0));Q=Vector((274.48543319312125,60.359559236272254,0));L=(Q-P).dot(U);Y=(Q-P).dot(V);LO=-8.0;HI=L
# Source branch reaches Y at L; cubic closure is tangent to the stock at the toe.
end_slope=Y/L;aa=(3*Y-end_slope*L)/L**2;bb=(end_slope*L-2*Y)/L**3
A=1.741/2;HW=.065;gap=.046
C=bpy.data.collections.new('36_PHYSICAL_TURNOUT_6045464001_RECONSTRUCTED');s.collection.children.link(C)
C['scope']='Physical reconstructed toe/closure/frog/bearers fitted to OSM node6045464001 and source endpoints; type and layout not surveyed.'
M={n:bpy.data.materials[n] for n in ['Rusty rail sides','Polished running rail','Prestressed concrete sleeper','Painted charcoal steel','Weathered concrete','Safety yellow','Warm white painted concrete']}
RUST=M['Rusty rail sides'];HEAD=M['Polished running rail'];CON=M['Prestressed concrete sleeper'];DARK=M['Painted charcoal steel'];GREY=M['Weathered concrete'];WHITE=M['Warm white painted concrete']
def uv(p):p=Vector(p)-P;return p.dot(U),p.dot(V)
def world(u,v,z):return P+U*u+V*v+Vector((0,0,z))
def mesh(n,vs,fs,m):
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m);return o
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def box(n,p,sz,m,u=U,v=V):
 p=Vector(p);vs=[p+u*(i*sz[0]/2)+v*(j*sz[1]/2)+Vector((0,0,k*sz[2]/2)) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];return mesh(n,vs,F,m)
def inpatch(p,wide=False):
 u,v=uv(p);return LO-.01<u<HI+.01 and (-6.2 if not wide else -7.5)<v<2.3
removed={};clipped={}
# Batched direct boxes use8 vertices and6 faces. Clip original rail cross-sections at patch planes,
# avoiding accidental gaps or duplicated coincident rails at the patch boundaries.
for o in list(s.objects):
 if o.type!='MESH':continue
 name=o.name
 israil=name.startswith('Rail ') and any(w in name for w in ['642061244','96236046'])
 isbatch=any(name.startswith(t) for t in ['Concrete sleepers','Rail seat pads','Elastic rail clips','Long crossing bearers','Turnout check rail','Point machine enclosure'])
 if not israil and not isbatch:continue
 vs0=[o.matrix_world@v.co for v in o.data.vertices]
 if len(vs0)%8:continue
 vs=[];fs=[];count=0
 for i in range(0,len(vs0),8):
  vv=vs0[i:i+8];center=sum(vv,Vector())/8
  if israil:
   a=sum(vv[:4],Vector())/4;b=sum(vv[4:],Vector())/4;ua,va=uv(a);ub,vb=uv(b)
   if max(ua,ub)<=LO or min(ua,ub)>=HI or max(va,vb)<-6.2 or min(va,vb)>2.3:ranges=[(0,1)]
   else:
    den=ub-ua
    if abs(den)<1e-8:ranges=[] if inpatch(center) else [(0,1)]
    else:
     t0,t1=sorted([(LO-ua)/den,(HI-ua)/den]);t0=max(0,t0);t1=min(1,t1);ranges=[]
     if t0>0:ranges.append((0,t0))
     if t1<1:ranges.append((t1,1))
    count+=1
   for t0,t1 in ranges:
    if t1-t0<1e-6:continue
    verts=[vv[k].lerp(vv[k+4],t0) for k in range(4)]+[vv[k].lerp(vv[k+4],t1) for k in range(4)];k=len(vs);vs.extend(verts);fs.extend(tuple(k+j for j in f) for f in F)
  else:
   if inpatch(center):count+=1;continue
   k=len(vs);vs.extend(vv);fs.extend(tuple(k+j for j in f) for f in F)
 if count:
  d=bpy.data.meshes.new(name+' corrected');d.from_pydata(vs,[],fs);d.update()
  for m in o.data.materials:d.materials.append(m)
  o.data=d;o.matrix_world.identity();removed[name]=count
# Remove old loose decorative blade curves, drive rods and ID markers from this envelope.
for o in list(s.objects):
 if o.type=='CURVE' and any(n in o.name for n in ['Tapering switch blade','Point drive rod']):
  pts=[o.matrix_world@Vector(p.co[:3]) for sp in o.data.splines for p in sp.points]
  if any(inpatch(p,True) for p in pts):bpy.data.objects.remove(o,do_unlink=True);continue
 if o.name.startswith(('Point identification board','Points number')) and inpatch(o.location,True):bpy.data.objects.remove(o,do_unlink=True)
def main_y(u):return -.01476*u if u<0 else 0.0
def branch_y(u):return aa*u*u+bb*u*u*u
def dydx(u):return 2*aa*u+3*bb*u*u
# Rail profile sweep. Sections have real foot/web/head shape; tapers reduce only blade head width.
def rail(n,points,material=RUST,widthscale=None):
 # three separate profile strips keep editable materials and avoid intersecting head envelopes.
 for part,zlo,zhi,width,m in [('foot',.3525,.3775,.15,RUST),('web',.372,.472,.016,RUST),('head',.460,.500,.065,HEAD)]:
  verts=[];faces=[]
  for i,p in enumerate(points):
   p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();normal=Vector((-t.y,t.x,0));ww=width*(widthscale[i] if widthscale is not None and part=='head' else 1)
   verts.extend([p+normal*ww/2+Vector((0,0,zlo)),p-normal*ww/2+Vector((0,0,zlo)),p+normal*ww/2+Vector((0,0,zhi)),p-normal*ww/2+Vector((0,0,zhi))])
  for i in range(len(points)-1):
   a=i*4;b=a+4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
  faces.extend([(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)]);mesh(n+' '+part,verts,faces,m)
def offsets(branch,side,u):
 cy=branch_y(u) if branch else main_y(u);dy=dydx(u) if branch else (-.01476 if u<0 else 0);nn=Vector((-dy,1,0)).normalized();return Vector((u+nn.x*side*A,cy+nn.y*side*A,0))
def wr(q):return world(q.x,q.y,0)
# Numerically find actual branch-upper/main-lower crossing, accounting for normal offsets.
lo,hi=0,L
for _ in range(60):
 mid=(lo+hi)/2
 if offsets(True,1,mid).y>-A:lo=mid
 else:hi=mid
fu=(lo+hi)/2;fq=offsets(True,1,fu);frog_u=fq.x;frog_v=-A
# Stock and closure paths. Only one stock pair before the toe. The diverging outside blade
# tapers from a tip after separation; no duplicate full-width common rail pair.
N=250
us=[LO+(HI-LO)*i/N for i in range(N+1)]
rail('6045464001 fixed straight outer stock',[wr(offsets(False,1,u)) for u in us])
# Straight and divergent closure rails end before the wing/nose assembly; no oblique
#45mm slit masquerades as a normal flangeway. The frog is assembled explicitly below.
for a,b in [(LO,frog_u-2.0),(frog_u+2.5,HI)]:rail('6045464001 straight closure and stock',[wr(offsets(False,-1,a+(b-a)*i/150)) for i in range(151)])
start=.55;b_us=[start+(L-start)*i/220 for i in range(221)];scales=[max(.025,min(1,(u-start)/5.5)) for u in b_us]
rail('6045464001 diverging outer tapered blade',[wr(offsets(True,-1,u)) for u in b_us],widthscale=scales)
for a,b in [(start,fu-2.0),(fu+2.5,L)]:
 bu=[a+(b-a)*i/160 for i in range(161)];scale=[max(.025,min(1,(u-start)/5.5)) for u in bu];qs=[]
 for u in bu:
  q=offsets(True,1,u)
  # Open switch tongue:115mm tip-face gap, eased to the closure line at heel.
  q.y-=(.115+.0325)*(max(0,1-(u-start)/7.0)**2);qs.append(wr(q))
 rail('6045464001 open inner blade closure',qs,widthscale=scale)
# Check rails on opposing running rails, with flared entry mouths and46mm flangeway.
check_offset=.065+gap
for branch,side in [(False,1),(True,-1)]:
 pts=[]
 for i in range(41):
  u=fu-2.2+i*.11;u=min(L-.1,max(.1,u));q=offsets(branch,side,u);dy=dydx(u) if branch else 0;nn=Vector((-dy,1,0)).normalized();flare=.10*(1-min(1,i/5,(40-i)/5));q-=nn*side*(check_offset+flare);pts.append(wr(q))
 # Check rails have a narrow head profile; guard function, no unintended full running rail.
 rail('6045464001 opposite checkrail',pts)
# Wing rails splay round a solid V-nose. Faces in the parallel guard section are
#46mm apart. The lower wing follows the divergent rail; the upper follows straight.
for upper in [False,True]:
 pts=[]
 for i in range(91):
  delta=-2+i*4.5/90;u=frog_u+delta
  branchq=offsets(True,1,fu+delta);straightq=Vector((u,-A,0))
  t=max(0,min(1,(delta+1.2)/1.6));t=t*t*(3-2*t)
  if upper:q=branchq.lerp(straightq+Vector((0,.111,0)),t)
  else:q=straightq.lerp(branchq-Vector((0,.111,0)),t)
  pts.append(wr(q))
 rail('6045464001 '+('upper' if upper else 'lower')+' frog wing',pts)
# The tapered V-nose is one mesh, avoiding two overlaid intersecting rail heads.
e=frog_u+2.5;be=offsets(True,1,fu+2.5);tip=Vector((frog_u+.10,-A-.006,0));neck=Vector((frog_u+.72,-A-.040,0))
outline=[tip,Vector((e,-A+.0325,0)),Vector((e,-A-.0325,0)),neck,Vector((be.x,be.y+.0325,0)),Vector((be.x,be.y-.0325,0))]
vs=[wr(q)+Vector((0,0,z)) for z in [.3775,.500] for q in outline];N=len(outline);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('6045464001 one-piece manganese V crossing nose',vs,fs,HEAD)
frog=world(frog_u,frog_v,0)
# One bearer array, aligned to stock direction and long enough to support both routes.
for j in range(int((HI-LO)/.6)+1):
 u=LO+j*.6;by=branch_y(max(0,u));ymn=min(-A,by-A)-.52;ymx=A+.52;center=(ymn+ymx)/2
 box('6045464001 long single bearer',world(u,center,.285),(.27,ymx-ymn,.15),CON)
 # No duplicate ties. Rail fastenings align with both routes beyond the blade heel.
 rails=[offsets(False,-1,u),offsets(False,1,u)]
 if u>6:rails.extend([offsets(True,-1,u),offsets(True,1,u)])
 for q in rails:
  p=world(q.x,q.y,.383);box('6045464001 baseplate',p,(.24,.23,.026),DARK)
  for z in [-1,1]:box('6045464001 elastic clip',p+V*z*.092+Vector((0,0,.025)),(.11,.037,.035),RUST)
# Point machine at the actual toe, linked stretcher bars and visible hardware.
box('6045464001 toe point machine',world(2,2.0,.51),(.8,.5,.34),GREY)
for u in [1.9,3.3]:box('6045464001 stretcher bar',world(u,0,.391),(.06,1.72,.055),DARK)
box('6045464001 machine linkage',world(2,1.35,.39),(.075,1.4,.04),DARK)
# Clearance audit: shift portal mast components if they occupy this rail patch (none expected).
# Review camera follows actual source-backed location and shows toe-to-frog all together.
for old in list(bpy.data.objects):
 if old.name.startswith('17_PHYSICAL_TURNOUT'):bpy.data.objects.remove(old,do_unlink=True)
d=bpy.data.cameras.new('17_PHYSICAL_TURNOUT_6045464001');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=world(18,19,21);target=world(19,-1.7,.4);o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.lens=42;d.clip_end=5000
s['physical_turnout_review']='Node6045464001: source-connected correction envelope, continuous stock, eased closure, tapered blades, computed frog, opposite checkrails, one bearer array; reconstructed not as-built.'
report={'node':'6045464001','source_ways':['642061244','96236046'],'source_toe_world_m':list(P),'closure_endpoint_world_m':list(Q),'local_extent_m':[LO,HI],'branch_cubic_coefficients':[aa,bb],'frog_branch_u_m':fu,'frog_world_m':list(frog),'target_flangeway_m':gap,'removed_original_components':removed,'common_stock_pair_count':1,'bearer_arrays_in_envelope':1,'historical_status':'Locally reconstructed physical turnout fitted to map endpoints, not certified NCJ type'}
(R/'QA_TURNOUT_6045464001.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('TURNOUT_REPAIR_SAVED',json.dumps(report),flush=True)
