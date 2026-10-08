"""Apply accepted physical turnout reconstruction algorithm to all spatially independent cases.
See references/physical_turnout_cases.json for exact corrected/excluded node IDs and reasons.
Run after build_ncj_full.py and add_review_labels.py. Re-running is idempotent for physical groups.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
cases=json.loads((R/'references/physical_turnout_cases.json').read_text());reports=[]
for o in list(s.objects):
 if o.name.startswith(('Tapering switch blade','Turnout check rail','Long crossing bearers','Point machine enclosure','Point drive rod','Point identification board','Points number')):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if c.name.startswith('36_PHYSICAL_TURNOUT_'):
  for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(c)
for case in cases['accepted']:
 nodeid=case['node'];P=Vector((*case['position'],0));U=Vector((*case['U'],0));V=Vector((*case['V'],0));Q=Vector((*case['closure_endpoint'],0));L=case['L'];Y=case['Y'];LO=case['LO'];HI=L
 # Source branch reaches Y at L; cubic closure is tangent to the stock at the toe.
 end_slope=Y/L;aa=(3*Y-end_slope*L)/L**2;bb=(end_slope*L-2*Y)/L**3
 A=1.741/2;HW=.065;gap=.046
 C=bpy.data.collections.new(f'36_PHYSICAL_TURNOUT_{nodeid}_RECONSTRUCTED');s.collection.children.link(C)
 C['scope']='Physical reconstructed toe/closure/frog/bearers fitted to OSM node6045464001 and source endpoints; type and layout not surveyed.'
 M={n:bpy.data.materials[n] for n in ['Rusty rail sides','Polished running rail','Prestressed concrete sleeper','Painted charcoal steel','Weathered concrete','Safety yellow','Warm white painted concrete']}
 RUST=M['Rusty rail sides'];HEAD=M['Polished running rail'];CON=M['Prestressed concrete sleeper'];DARK=M['Painted charcoal steel'];GREY=M['Weathered concrete'];WHITE=M['Warm white painted concrete']
 def uv(p):p=Vector(p)-P;return p.dot(U),p.dot(V)
 def world(u,v,z):return P+U*u+V*v+Vector((0,0,z))
 def mesh(n,vs,fs,m):
  d=bpy.data.meshes.new(n);d.from_pydata(vs,[],[tuple(reversed(f)) for f in fs] if U.cross(V).z<0 else fs);d.update();o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m);return o
 F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 def box(n,p,sz,m,u=U,v=V):
  p=Vector(p);vs=[p+u*(i*sz[0]/2)+v*(j*sz[1]/2)+Vector((0,0,k*sz[2]/2)) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];return mesh(n,vs,F,m)
 def inpatch(p,wide=False):
  u,v=uv(p);return LO-.01<u<HI+.01 and (Y-1.7 if not wide else Y-2.3)<v<2.3
 removed={};clipped={}
 # Batched direct boxes use8 vertices and6 faces. Clip original rail cross-sections at patch planes,
 # avoiding accidental gaps or duplicated coincident rails at the patch boundaries.
 for o in list(s.objects):
  if o.type!='MESH':continue
  name=o.name
  israil=name.startswith('Rail ') and any(w in name for w in case['ways'])
  isbatch=(name.startswith('Concrete sleepers') and any(w in name for w in case['ways'])) or name.startswith(('Rail seat pads','Elastic rail clips'))
  if not israil and not isbatch:continue
  vs0=[o.matrix_world@v.co for v in o.data.vertices]
  if len(vs0)%8:continue
  vs=[];fs=[];count=0
  for i in range(0,len(vs0),8):
   vv=vs0[i:i+8];center=sum(vv,Vector())/8
   if israil:
    a=sum(vv[:4],Vector())/4;b=sum(vv[4:],Vector())/4;ua,va=uv(a);ub,vb=uv(b)
    if max(ua,ub)<=LO or min(ua,ub)>=HI or max(va,vb)<Y-1.7 or min(va,vb)>2.3:ranges=[(0,1)]
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
    uu,vv0=uv(center);old_branch=Y*max(0,uu)/L
    on_target=min(abs(vv0),abs(vv0-old_branch))<1.30
    if inpatch(center) and on_target:count+=1;continue
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
 def main_y(u):return case['common_y_slope']*u if u<0 else 0.0
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
  cy=branch_y(u) if branch else main_y(u);dy=dydx(u) if branch else (case['common_y_slope'] if u<0 else 0);nn=Vector((-dy,1,0)).normalized();return Vector((u+nn.x*side*A,cy+nn.y*side*A,0))
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
 rail(f'{nodeid} fixed straight outer stock',[wr(offsets(False,1,u)) for u in us])
 # Straight and divergent closure rails end before the wing/nose assembly; no oblique
 #45mm slit masquerades as a normal flangeway. The frog is assembled explicitly below.
 for a,b in [(LO,frog_u-2.0),(frog_u+2.5,HI)]:rail(f'{nodeid} straight closure and stock',[wr(offsets(False,-1,a+(b-a)*i/150)) for i in range(151)])
 start=.55;b_us=[start+(L-start)*i/220 for i in range(221)];scales=[max(.025,min(1,(u-start)/5.5)) for u in b_us]
 rail(f'{nodeid} diverging outer tapered blade',[wr(offsets(True,-1,u)) for u in b_us],widthscale=scales)
 for a,b in [(start,fu-2.0),(fu+2.5,L)]:
  bu=[a+(b-a)*i/160 for i in range(161)];scale=[max(.025,min(1,(u-start)/5.5)) for u in bu];qs=[]
  for u in bu:
   q=offsets(True,1,u)
   # Open switch tongue:115mm tip-face gap, eased to the closure line at heel.
   q.y-=(.115+.0325)*(max(0,1-(u-start)/7.0)**2);qs.append(wr(q))
  rail(f'{nodeid} open inner blade closure',qs,widthscale=scale)
 # Check rails on opposing running rails, with flared entry mouths and46mm flangeway.
 check_offset=.065+gap
 for branch,side in [(False,1),(True,-1)]:
  pts=[]
  for i in range(41):
   u=fu-2.2+i*.11;u=min(L-.1,max(.1,u));q=offsets(branch,side,u);dy=dydx(u) if branch else 0;nn=Vector((-dy,1,0)).normalized();flare=.10*(1-min(1,i/5,(40-i)/5));q-=nn*side*(check_offset+flare);pts.append(wr(q))
  # Check rails have a narrow head profile; guard function, no unintended full running rail.
  rail(f'{nodeid} opposite checkrail',pts)
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
  rail(f'{nodeid} '+('upper' if upper else 'lower')+' frog wing',pts)
 # The tapered V-nose is one mesh, avoiding two overlaid intersecting rail heads.
 e=frog_u+2.5;be=offsets(True,1,fu+2.5);tip=Vector((frog_u+.10,-A-.006,0));neck=Vector((frog_u+.72,-A-.040,0))
 outline=[tip,Vector((e,-A+.0325,0)),Vector((e,-A-.0325,0)),neck,Vector((be.x,be.y+.0325,0)),Vector((be.x,be.y-.0325,0))]
 vs=[wr(q)+Vector((0,0,z)) for z in [.3775,.500] for q in outline];N=len(outline);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 mesh(f'{nodeid} one-piece manganese V crossing nose',vs,fs,HEAD)
 frog=world(frog_u,frog_v,0)
 # Continuous granite formation beneath the complete eased turnout fan.
 ballastmat=bpy.data.materials['Angular granite ballast'];outline=[]
 for i in range(81):
  u=LO+(HI-LO)*i/80;by=branch_y(max(0,u));outline.append(world(u,min(0,by)-1.73,0))
 for i in range(80,-1,-1):
  u=LO+(HI-LO)*i/80;outline.append(world(u,1.73,0))
 N=len(outline);vs=[p+Vector((0,0,z)) for z in [-.06,.212] for p in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh(f'{nodeid} continuous turnout ballast fan',vs,fs,ballastmat)
 # One bearer array, aligned to stock direction and long enough to support both routes.
 for j in range(int((HI-LO)/.6)+1):
  u=LO+j*.6;by=branch_y(max(0,u));ymn=min(-A,by-A)-.52;ymx=A+.52;center=(ymn+ymx)/2
  box(f'{nodeid} long single bearer',world(u,center,.285),(.27,ymx-ymn,.15),CON)
  # No duplicate ties. Rail fastenings align with both routes beyond the blade heel.
  rails=[offsets(False,-1,u),offsets(False,1,u)]
  if u>6:rails.extend([offsets(True,-1,u),offsets(True,1,u)])
  for q in rails:
   p=world(q.x,q.y,.383);box(f'{nodeid} baseplate',p,(.24,.23,.026),DARK)
   for z in [-1,1]:box(f'{nodeid} elastic clip',p+V*z*.092+Vector((0,0,.025)),(.11,.037,.035),RUST)
 # Point machine at the actual toe, linked stretcher bars and visible hardware.
 box(f'{nodeid} toe point machine',world(2,2.0,.51),(.8,.5,.34),GREY)
 for u in [1.9,3.3]:box(f'{nodeid} stretcher bar',world(u,0,.391),(.06,1.72,.055),DARK)
 box(f'{nodeid} machine linkage',world(2,1.35,.39),(.075,1.4,.04),DARK)

 reports.append({'node':nodeid,'source_ways':case['ways'],'toe_m':list(P),'end_m':list(Q),'length_m':L,'lateral_m':Y,'flangeway_target_m':gap,'frog_m':list(frog),'removed_components':removed,'scope':'Reconstructed physical simple turnout, not surveyed NCJ switch type'})
 print('CORRECTED_NODE',nodeid,flush=True)
 if nodeid=='6045464001':
  for old in list(bpy.data.objects):
   if old.name.startswith('17_PHYSICAL_TURNOUT'):bpy.data.objects.remove(old,do_unlink=True)
  d=bpy.data.cameras.new('17_PHYSICAL_TURNOUT_6045464001');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=world(17,31,35);target=world(15,-1.7,.4);o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.lens=42;d.clip_end=5000
s['physical_turnout_corrected_count']=len(reports);s['physical_turnout_approximate_count']=len(cases['excluded']);s['turnout_scope']='All20 applicable isolated simple nodes physically reconstructed;14 short/compound/degree4 nodes retain explicitly approximate map-derived geometry. Not operational engineering.'
(R/'QA_ALL_TURNOUTS.json').write_text(json.dumps({'corrected':reports,'approximate_or_compound':cases['excluded'],'standard_reference':'IRISET Signalling General section4.6.4:44–48mm BG check/wing flangeways; reconstructed target46mm, not certified profile.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('ALL_PHYSICAL_TURNOUTS_SAVED',len(reports),flush=True)
