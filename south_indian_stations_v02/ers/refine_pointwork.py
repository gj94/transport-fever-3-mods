# Physical visual turnout refinement: intersections of offset rail-head centrelines,
# flangeway breaks, actual derived crossing noses and opposite check rails.
# Not an interlocking/safety-certified trackwork design.
collection('20 | PHYSICAL POINTWORK • crossing gaps and derived frogs')
for ob in list(scene.objects):
 if ob.name.startswith(('Tapered switch blade','Turnout check rail','Cast manganese crossing nose','Rail foot ','Rail web ','Rail crown exact gauge ')):
  oldmesh=ob.data
  bpy.data.objects.remove(ob,do_unlink=True)
  if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
R=[]
for rid,pts,tags in paths:
 for side in [-1,1]:
  pp=[]
  for i,p in enumerate(pts):
   d=(Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])).normalized();pp.append(Vector((p[0]-d.y*.868*side,p[1]+d.x*.868*side)))
  chain=[0.0]
  for a,b in zip(pp,pp[1:]):chain.append(chain[-1]+(b-a).length)
  R.append({'id':rid,'side':side,'p':pp,'s':chain,'cuts':[],'blades':[]})
def cross(a,b):return a.x*b.y-a.y*b.x
grid={};events=[];eventpoints=[]
for ri,r in enumerate(R):
 for j,(a,b) in enumerate(zip(r['p'],r['p'][1:])):
  d=b-a;l=d.length
  if l<1e-5:continue
  keys=[(gx,gy) for gx in range(math.floor(min(a.x,b.x)/5),math.floor(max(a.x,b.x)/5)+1) for gy in range(math.floor(min(a.y,b.y)/5),math.floor(max(a.y,b.y)/5)+1)]
  seen=set()
  for key in keys:
   for rj,k,c,e in grid.get(key,[]):
    if ri==rj or R[ri]['id']==R[rj]['id'] or (rj,k) in seen:continue
    seen.add((rj,k));v=e-c;den=cross(d,v)
    if abs(den)<.005*l*v.length:continue
    t=cross(c-a,v)/den;u=cross(c-a,d)/den
    if not (.0001<t<.9999 and .0001<u<.9999):continue
    p=a+d*t
    # Near a shared toe, offset stock rails merge; this is not a crossing frog.
    if any(len(cc)>=3 and (p-Vector(np)).length<2.0 for np,cc in nodes.items()):continue
    if any((p-q).length<.12 for q in eventpoints):continue
    si=r['s'][j]+l*t;sj=R[rj]['s'][k]+v.length*u
    # A real crossing needs flange space on BOTH intersecting rail heads.
    half=(.060/2+.045)/max(abs(den)/(l*v.length),.015)
    r['cuts'].append((si-half,si+half));R[rj]['cuts'].append((sj-half,sj+half))
    events.append((p,ri,rj,d.normalized(),v.normalized(),si,sj));eventpoints.append(p)
   grid.setdefault(key,[]).append((ri,j,a,b))
def sample(r,s):
 s=max(0,min(r['s'][-1],s))
 for i in range(len(r['s'])-1):
  if r['s'][i+1]>=s:
   den=r['s'][i+1]-r['s'][i];t=(s-r['s'][i])/max(den,1e-8);return r['p'][i].lerp(r['p'][i+1],t)
 return r['p'][-1]
def interval(r,a,b):return [sample(r,a)]+[p for p,s in zip(r['p'],r['s']) if a<s<b]+[sample(r,b)]
# Identify the diverging route at each simple3-leg branch; replace first8m with
# variable-width switch blades, so there is no duplicate full-width rail underneath.
blade_count=0
for p,cs in nodes.items():
 if len(cs)!=3:continue
 dirs=[(Vector(c[0][1])-Vector(p)).normalized() for c in cs]
 pair=min([(dirs[i].dot(dirs[j]),i,j) for i in range(3) for j in range(i+1,3)])
 branch=next(k for k in range(3) if k not in pair[1:]);rid=cs[branch][1];d=dirs[branch]
 candidates=[r for r in R if r['id']==rid]
 for r in candidates:
  idx=min(range(len(r['p'])),key=lambda i:(r['p'][i]-Vector(p)).length)
  start=r['s'][idx];sgn=1 if idx==0 or (idx<len(r['p'])-1 and (r['p'][idx+1]-r['p'][idx]).dot(d)>0) else -1
  end=max(0,min(r['s'][-1],start+sgn*8.0));a,b=sorted([start,end])
  if b-a<1:continue
  r['cuts'].append((a,b));r['blades'].append((start,end));blade_count+=1
# Rebuild rail sections outside all gap/blade intervals.
for r in R:
 cuts=sorted((max(0,a),min(r['s'][-1],b)) for a,b in r['cuts']);merged=[]
 for a,b in cuts:
  if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
  else:merged.append((a,b))
 intervals=[];last=0
 for a,b in merged:
  if a>last+.002:intervals.append((last,a))
  last=max(last,b)
 if last<r['s'][-1]:intervals.append((last,r['s'][-1]))
 for n,(a,b) in enumerate(intervals):
  pp=interval(r,a,b)
  for kind,w,z,dep,m in [('foot',.15,.475,.03,railmat),('web',.018,.548,.12,railmat),('crown',.060,.620,.045,railhead)]:strip('Physical rail '+kind+' '+r['id']+' '+str(r['side'])+' '+str(n),pp,w,z,dep,m)
 for n,(a,b) in enumerate(r['blades']):
  pp=[sample(r,a+(b-a)*i/24) for i in range(25)];vv=[]
  for i,p in enumerate(pp):
   d=(pp[min(i+1,24)]-pp[max(i-1,0)]).normalized();per=Vector((-d.y,d.x));w=.005+.055*i/24
   for z in [.548,.643]:
    for side in [-1,1]:q=p+per*w*.5*side;vv.append((q.x,q.y,z))
  ff=[]
  for i in range(24):
   q=4*i;ff.extend([(q,q+4,q+5,q+1),(q+2,q+3,q+7,q+6),(q,q+2,q+6,q+4),(q+1,q+5,q+7,q+3)])
  mesh('Tapered physical switch blade '+r['id']+' '+str(r['side']),vv,ff,railhead)
# Derived frog geometry lies at an ACTUAL intersection, not in all three node rays.
for n,(p,ri,rj,da,db,sa,sb) in enumerate(events):
 if da.dot(db)<0:db=-db
 axis=(da+db).normalized()
 toes=[Vector(k) for k,v in nodes.items() if len(v)==3 and (Vector(k)-p).length<100]
 if toes:
  toe=min(toes,key=lambda q:(q-p).length)
  if axis.dot(p-toe)<0:axis=-axis
 per=Vector((-axis.y,axis.x));angle=math.acos(max(-1,min(1,da.dot(db))))
 # V nose immediately beyond crossing throat; the angle-derived rail gaps remain open.
 tipdist=(.030+.045)/max(math.sin(angle/2),.01);length=tipdist+1.5
 tip=p+axis*tipdist;base=p+axis*length;halfwidth=max(.005,length*math.sin(angle/2)-.030-.045)
 prism('Derived manganese frog nose '+str(n),[(tip.x,tip.y),(base.x+per.x*halfwidth,base.y+per.y*halfwidth),(base.x-per.x*halfwidth,base.y-per.y*halfwidth)],.548,.643,railhead)
 # Check rails have0.045m face clearance (0.100m centres) from opposite stock rails, with flared ends.
 for rr,ss in [(R[ri],sa),(R[rj],sb)]:
  pos=sample(rr,ss);d=(sample(rr,ss+.2)-sample(rr,ss-.2)).normalized();normal=Vector((-d.y,d.x));side=rr['side'];cp=pos-normal*side*(1.736-.100)
  pp=[cp-d*2.0+normal*side*.055,cp-d*1.65,cp+d*1.65,cp+d*2.0+normal*side*.055]
  strip('Derived opposite checkrail '+str(n),pp,.05,.62,.065,railhead)
  for t in [-1.5,-.5,.5,1.5]:
   q=cp+d*t;cube('Checkrail fastening chair',(q.x,q.y,.48),(.26,.26,.03),railmat)
(P/'physical_pointwork.json').write_text(json.dumps({'rail_intersections_with_flangeway_gaps':len(events),'tapered_replacement_blades':blade_count,'clear_flange_gap_target_m':.045,'longitudinal_cut':'(rail_head_width+2*clear_gap)/sin(crossing_angle)','checkrail_center_inset_m':.100,'crossings':[{'x':float(p.x),'y':float(p.y),'route_a':R[a]['id'],'route_b':R[b]['id']} for p,a,b,*_ in events],'limitations':'Visual physical crossing reconstruction; route topology map-derived. Not certified interlocking or exact turnout manufacturer geometry.'},indent=2))
print('PHYSICAL POINTWORK',len(events),'crossings',blade_count,'replacement blades',flush=True)
# Replace coincident individual-track sleepers within simple turnout envelopes with
# common extended bearers. Global0.65m stations prevent duplicate bearer layers.
regions=[]
for p,cs in nodes.items():
 if len(cs)!=3:continue
 dd=[(Vector(c[0][1])-Vector(p)).normalized() for c in cs]
 pair=min([(dd[i].dot(dd[j]),i,j) for i in range(3) for j in range(i+1,3)])
 bi=next(k for k in range(3) if k not in pair[1:]);mi=max(pair[1:],key=lambda k:dd[k].dot(dd[bi]));dm=dd[mi];db=dd[bi]
 angle=math.acos(max(-1,min(1,dm.dot(db))))
 if angle<.008 or angle>.65 or abs(dm.x)<.6 or abs(db.x)<.6:continue
 extent=min(85,max(25,1.736/max(math.tan(angle),.02)+12));regions.append((Vector(p),dm,db,extent))
def bands_at(x):
 bands=[]
 for p,dm,db,extent in regions:
  sm=(x-p.x)/dm.x;sb=(x-p.x)/db.x
  if -2<=sm<=extent and -2<=sb<=extent:
   ya=p.y+dm.y*sm;yb=p.y+db.y*sb;bands.append((min(ya,yb)-1.50,max(ya,yb)+1.50))
 bands.sort();merged=[]
 for a,b in bands:
  if merged and a<merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
  else:merged.append((a,b))
 return merged
def inside(x,y):return any(a<=y<=b for a,b in bands_at(x))
removed_boxes=0
for ob in list(scene.objects):
 if not ob.name.startswith(('Concrete sleepers ','Fastening baseplates ','Pandrol clips ')):continue
 old=ob.data;verts=[];faces=[];oldv=list(old.vertices)
 # The Batch constructor uses8 vertices and6 faces per physically distinct box.
 for k in range(0,len(old.vertices),8):
  chunk=oldv[k:k+8]
  if len(chunk)!=8:continue
  center=sum((v.co for v in chunk),Vector())/8
  if inside(center.x,center.y):removed_boxes+=1;continue
  n=len(verts);verts.extend(tuple(v.co) for v in chunk)
  faces.extend([tuple(n+i for i in face) for face in [(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)]])
 me=bpy.data.meshes.new(ob.name+' trimmed');me.from_pydata(verts,[],faces);me.update()
 for ma in old.materials:me.materials.append(ma)
 ob.data=me
 if old.users==0:bpy.data.meshes.remove(old)
bearers=Batch('Common turnout long bearers',stone);chairs=Batch('Common turnout fastening plates',railmat);newclips=Batch('Common turnout elastic clips',black)
bearer_count=0
# x interval contains only the station model; no extra routes are introduced.
for k in range(math.floor(-510/.65),math.ceil(850/.65)):
 x=k*.65;bands=bands_at(x)
 for ya,yb in bands:
  bearers.box((x,(ya+yb)/2,.36),(.25,yb-ya,.18));bearer_count+=1
  ys=[]
  for r in R:
   for a,b in zip(r['p'],r['p'][1:]):
    if min(a.x,b.x)<=x<max(a.x,b.x) and abs(b.x-a.x)>1e-7:
     t=(x-a.x)/(b.x-a.x);y=a.y+(b.y-a.y)*t
     if ya+.12<y<yb-.12 and not any(abs(y-z)<.09 for z in ys):ys.append(y)
  for y in ys:
   chairs.box((x,y,.465),(.30,.23,.025))
   for dy in [-.085,.085]:newclips.box((x,y+dy,.50),(.12,.045,.055))
bearers.finish();chairs.finish();newclips.finish()
# Operationally neutral review camera targets a documented simple branch.
pointwork_review_target=(552,39,.62)
q=json.loads((P/'physical_pointwork.json').read_text());q.update({'common_bearers':bearer_count,'removed_duplicate_sleeper_fastener_boxes':removed_boxes,'representative_node':'1008213472','representative_local_xy_m':[563.817,37.329],'representative_routes':['1453154556','285881585','49015817'],'bearer_note':'Unified0.65m stationing in local station-X direction; long bearers reconstructed, not a manufacturer tie schedule.'});(P/'physical_pointwork.json').write_text(json.dumps(q,indent=2))
print('COMMON BEARERS',bearer_count,'removed old boxes',removed_boxes,flush=True)
