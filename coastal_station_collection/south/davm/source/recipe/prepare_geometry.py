"""Source-preserving metric geometry, conservative visual reconstruction, not a railway survey."""
from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1]; WORK=R.parents[1]
sys.path.insert(0,str(WORK/'south_indian_stations_v02/tvc/.builddeps'))
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import unary_union,substring
from shapely.geometry.polygon import orient
from shapely import make_valid,constrained_delaunay_triangles
STATIONS=json.loads((R/'stations.json').read_text())
CONFIG={
 'PGZ':dict(length=320,building=[10,5],halt=True,roof='tile',color=[.70,.63,.40],pfwidth=4.5,bridge=False),
 'MQU':dict(length=510,building=[29,9],roof='tile',color=[.77,.68,.46],pfwidth=6,bridge=True),
 'KXP':dict(length=420,building=[17,7],roof='flat',color=[.75,.73,.56],pfwidth=5.5,bridge=True),
 'KZK':dict(length=550,building=[43,13],roof='flat',color=[.82,.72,.54],pfwidth=7,bridge=True,envelope=1350),
 'VELI':dict(length=350,building=[12,6],halt=True,roof='tile',color=[.72,.67,.46],pfwidth=4.5,bridge=False),
 'TVCN':dict(length=610,building=[73,17],roof='terminal',color=[.77,.79,.66],pfwidth=8,bridge=True,envelope=1400),
 'TVP':dict(length=500,building=[29,9],roof='tile',color=[.74,.66,.52],pfwidth=6,bridge=True),
 'TVCS':dict(length=530,building=[28,10],roof='tile',color=[.71,.65,.50],pfwidth=6,bridge=True,envelope=1100),
 'BRAM':dict(length=380,building=[16,7],roof='tile',color=[.77,.65,.44],pfwidth=5,bridge=False),
 'NYY':dict(length=520,building=[40,11],roof='flat',color=[.80,.75,.64],pfwidth=6,bridge=True),
 'AMVA':dict(length=310,building=[9,5],halt=True,roof='tile',color=[.74,.62,.44],pfwidth=4.5,bridge=False),
 'DAVM':dict(length=470,building=[16,7],roof='flat',color=[.77,.70,.48],pfwidth=5,bridge=True),
 'PASA':dict(length=530,building=[31,10],roof='tile',color=[.74,.68,.53],pfwidth=6,bridge=True),
 'KZTW':dict(length=350,building=[10,5],halt=True,roof='tile',color=[.78,.71,.56],pfwidth=4.5,bridge=False),
 'KZT':dict(length=540,building=[40,11],roof='flat',color=[.76,.65,.47],pfwidth=6.5,bridge=True),
 'PYD':dict(length=380,building=[12,6],halt=True,roof='tile',color=[.76,.72,.60],pfwidth=4.8,bridge=False),
 'ERL':dict(length=600,building=[36,10],roof='tile',color=[.80,.70,.51],pfwidth=6,bridge=True,envelope=1100),
 'VRLR':dict(length=560,building=[16,7],roof='flat',color=[.74,.73,.59],pfwidth=5.5,bridge=True),
 'NJT':dict(length=620,building=[29,9],roof='flat',color=[.78,.72,.56],pfwidth=6.5,bridge=True,envelope=1100),
}
def polygons(g):
 if g.geom_type=='Polygon':return [g]
 return [p for gg in getattr(g,'geoms',[]) for p in polygons(gg)]
def lines(g):
 if g.geom_type=='LineString':return [g]
 return [p for gg in getattr(g,'geoms',[]) for p in lines(gg)]
def meshdata(g,z0,z1):
 v=[];f=[];index={}
 def idx(x,y,z):
  k=(round(x,6),round(y,6),z)
  if k not in index:index[k]=len(v);v.append(k)
  return index[k]
 for p in polygons(g):
  p=orient(p,sign=1)
  if p.area<1e-7:continue
  for t in constrained_delaunay_triangles(p).geoms:
   if not p.covers(t.representative_point()):continue
   xy=list(t.exterior.coords)[:-1]
   if sum(xy[i][0]*xy[(i+1)%3][1]-xy[(i+1)%3][0]*xy[i][1] for i in range(3))<0:xy.reverse()
   f.append([idx(x,y,z1) for x,y in xy]);f.append([idx(x,y,z0) for x,y in reversed(xy)])
  for ring in [p.exterior,*p.interiors]:
   xy=list(ring.coords)
   for (a,b),(c,d) in zip(xy,xy[1:]):f.append([idx(a,b,z0),idx(c,d,z0),idx(c,d,z1),idx(a,b,z1)])
 return dict(vertices=v,faces=f,parts=len(polygons(g)))
def compact(path,d):path.write_text(json.dumps(d,separators=(',',':')))
def prepare(code):
 st=next(s for s in STATIONS if s['station_code']==code);cfg=CONFIG[code].copy();cfg.setdefault('halt',False);cfg.setdefault('envelope',850)
 overrides=json.loads((R/'research/config_overrides.json').read_text()) if (R/'research/config_overrides.json').exists() else {};cfg.update(overrides.get(code,{}))
 raw=json.loads((WORK/f'coastal_route_research/osm_plots/{code}_geometry.json').read_text());lon,lat=raw['locator'];fac=111320*math.cos(math.radians(lat))
 def en(p):return[(p[0]-lon)*fac,(p[1]-lat)*110540]
 main=[w for w in raw['ways'] if w['tags'].get('railway')=='rail' and w['tags'].get('usage')=='main']
 if not main:main=[w for w in raw['ways'] if w['tags'].get('railway')=='rail']
 seg=[]
 for w in main:
  pp=[en(p) for p in w['coords']]
  for a,b in zip(pp,pp[1:]):
   ln=LineString([a,b]);seg.append((ln.distance(Point(0,0)),a,b))
 _,a,b=min(seg);dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy);u=[dx/le,dy/le]
 if u[1]>.1:u=[-v for v in u]
 n=[-u[1],u[0]]
 def xy(p):e,no=en(p);return[e*u[0]+no*u[1],e*n[0]+no*n[1]]
 # Include the raw station's full yard envelope across track. Do not include proposed lines.
 clip=box(-cfg['envelope'],-400,cfg['envelope'],400)
 ww=[];platforms=[];excluded=[]
 for w in raw['ways']:
  tag=w['tags'];kind=tag.get('railway');pp=[xy(p) for p in w['coords']]
  if kind=='platform' and len(pp)>3 and pp[0]==pp[-1]:
   p=make_valid(Polygon(pp)).intersection(clip)
   for p0 in polygons(p):
    if p0.area>15:platforms.append(dict(id=w['id'],xy=list(p0.exterior.coords),basis='OSM footprint; mixed edit date, not operational certification',tags=tag,timestamp=w['timestamp']))
   continue
  if kind not in ['rail','construction','proposed']:continue
  if kind=='construction' and code in ['ERL','VRLR','NJT']:
   basis='Mapped construction alignment represented physically after 2026 doubled-section reporting; exact commissioning and station-road role unverified'
  elif kind!='rail':excluded.append(dict(id=w['id'],reason=kind,tags=tag));continue
  else:basis='OSM mapped railway centreline; operating classification and edit date are not commissioning evidence'
  for j,ln in enumerate(lines(LineString(pp).intersection(clip))):
   if ln.length<.05:continue
   # Reject duplicate geometric ways rather than model two superimposed roads.
   if any(ln.hausdorff_distance(LineString(q['xy']))<.03 for q in ww):continue
   ww.append(dict(id=w['id']+(':'+str(j) if j else ''),source_id=w['id'],xy=list(ln.coords),tags=tag,timestamp=w['timestamp'],basis=basis))
 rail_ln=unary_union([LineString(w['xy']) for w in ww]);cross=rail_ln.intersection(LineString([(0,-400),(0,400)]));ys=sorted(set(round(p.y,2) for p in getattr(cross,'geoms',[cross]) if p.geom_type=='Point'))
 # Parallel road inferred only when platform evidence requires it and mapping is explicitly incomplete.
 # NJT current3-face side+island satellite requires third platform road beyond old construction line.
 if code=='NJT':
  # The island's mapped exterior gives a better physical road placement than an arbitrary offset.
  island=min(platforms,key=lambda p:Polygon(p['xy']).centroid.y)
  sec=Polygon(island['xy']).intersection(LineString([(0,-400),(0,400)]))
  target=min(p[1] for p in sec.coords)-1.9
  base=next(w for w in ww if w['tags'].get('railway')=='rail');ln=LineString(base['xy'])
  coords=sorted(ln.coords)
  def ly(x):
   for a,b in zip(coords,coords[1:]):
    if a[0]<=x<=b[0]:return a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1])
   return coords[0][1] if x<coords[0][0] else coords[-1][1]
  delta=target-ly(0);pb=Polygon(island['xy']).bounds;x0=pb[0]-160;x1=pb[2]+160;pp=[]
  for i in range(201):
   x=x0+(x1-x0)*i/200;t=min(1,(x-x0)/150,(x1-x)/150);t=max(0,t);s=t*t*(3-2*t);pp.append([x,ly(x)+delta*s])
  ww.append(dict(id='NJT_satellite_third_platform_road',source_id='Google satellite 2026-10-08',xy=pp,tags={'railway':'rail','service':'yard'},timestamp='imagery date not exposed',basis='Physically visible third platform road fitted beyond mapped island; throat curves reconstructed, not surveyed'))
  ys.append(target)
 # Missing platform polygons are reconstructed parallel to mapped roads with taper ends.
 # Existing polygons remain source-specific. VRLR override2physical bodies despite reported1.
 wanted={'VRLR':2}.get(code, int(st['iri_reported_platforms']))
 bodies=wanted if wanted<=2 else (2 if wanted==3 else 4)
 if code=='TVCN':bodies=4
 if cfg.get('physical_platform_bodies'):bodies=cfg['physical_platform_bodies']
 def parallel_platform(line,side,length,width,index):
  near=line.project(Point(0,0));a=max(0,near-length/2);b=min(line.length,near+length/2)
  cut=substring(line,a,b);sg=side
  edge=cut.offset_curve(sg*2.0,join_style=2);outer=cut.offset_curve(sg*(2+width),join_style=2)
  pp=list(edge.coords)+list(reversed(outer.coords));p=make_valid(Polygon(pp))
  return dict(id=f'RECONSTRUCTED_PLATFORM_{index}',xy=list(max(polygons(p),key=lambda p:p.area).exterior.coords),basis='Inferred platform footprint because source mapping lacks polygons; length/width approximate; reported count corroborates count only',tags={'railway':'platform','ref':str(index)})
 if len(platforms)<bodies:
  # Select near-station source line and orient x increasing for consistent side.
  nearways=[]
  for w in ww:
   ln=LineString(w['xy']);hit=ln.intersection(LineString([(0,-400),(0,400)]))
   if hit.geom_type=='Point':nearways.append((hit.y,w,ln))
  nearways.sort(key=lambda q:q[0])
  if code=='KZK':nearways=[q for q in nearways if q[1]['tags'].get('service')!='spur']
  if not nearways:raise ValueError('No station roads '+code)
  if not platforms:
   if bodies==1:selection=[nearways[0]]
   elif bodies==2:selection=[nearways[0],nearways[-1]]
   else:selection=[nearways[0],nearways[-1]]
   for j,(y,w,ln) in enumerate(selection):
    side=(-1 if y>0 else 1) if bodies==1 else (-1 if j==0 else 1)
    if list(ln.coords)[-1][0]<list(ln.coords)[0][0]:side=-side
    platforms.append(parallel_platform(ln,side,cfg['length'],cfg['pfwidth'],j+1))
  else:
   for j in range(bodies-len(platforms)):
    y,w,ln=nearways[-1];side=1 if list(ln.coords)[-1][0]>list(ln.coords)[0][0] else -1;platforms.append(parallel_platform(ln,side,cfg['length'],cfg['pfwidth'],len(platforms)+1))
 if code=='NJT':
  # Keep mapped bodies; current satellite shows island arrangement. Do not mislabel OSM as current proof.
  for pf in platforms:
   pf['basis']+='; interpreted using 2026-10-08 Google satellite southernside+northernisland evidence'
   pf['tags']['ref']='2 / 3' if pf['id']=='383031394' else '1'
 if code=='KZK':
  east=next(w for w in ww if w['source_id']=='641627329');westmain=next(w for w in ww if w['source_id']=='608428982')
  def xline(w):
   pp=w['xy'];return LineString(pp if pp[-1][0]>pp[0][0] else list(reversed(pp)))
  platforms=[parallel_platform(xline(east),1,cfg['length'],cfg['pfwidth'],1),parallel_platform(xline(westmain),-1,cfg['length'],10.1,2)]
  for p in platforms:p['basis']='2026-10-08 Google satellite east side+western island organization; aligned to OSM easternloop and westernmain, dimensional reconstruction; industrialspurs excluded from passengerplatform placement'
  # 3 faces: two bodies, one island. Exact body placement refined after Google imagery.
  for pf in platforms:pf['tags']['ref']='1' if pf is platforms[0] else '2 / 3'
 if code=='VRLR':
  for pf in platforms:pf['basis']='Google satellite confirms2built opposing platform bodies and footbridge; footprint dimensions reconstructed; operation of both unverified'
 # Preserve every input polygon before explicitly documented clearance reconstruction.
 raw_platforms=json.loads(json.dumps(platforms));corrections=[] 
 if code=='MQU':
  old=next(p for p in platforms if p['id']=='1409282833');original=Polygon(old['xy']);near=sorted([(LineString(w['xy']).distance(Point(0,0)),w) for w in ww],key=lambda x:x[0])[0][1];pp=near['xy'];ln=LineString(pp if pp[-1][0]>pp[0][0] else list(reversed(pp)));new=parallel_platform(ln,-1,580,5.5,1);old['xy']=new['xy'];old['basis']='Google satellite visually confirms normal-width southwest outer platform beside red-roof station and silver canopy. Imprecise OSM footprint realigned parallel to source western loop with approximate5.5m width; original preserved in raw_platforms.';corrections.append({'platform_id':old['id'],'reason':'Satellite rejects sub1m clipped ribbon. Reconstructed a connected normal-width platform parallel to western loop; width approximate, not surveyed.','original_area_m2':original.area,'adopted_area_m2':Polygon(old['xy']).area,'width_m':5.5})
 if code=='BRAM':
  original=platforms[0];src=Polygon(original['xy']);base=min(ww,key=lambda w:LineString(w['xy']).distance(Point(0,0)));pp=base['xy'];ln=LineString(pp if pp[-1][0]>pp[0][0] else list(reversed(pp)));pf=parallel_platform(ln,-1,min(390,src.bounds[2]-src.bounds[0]),5.5,1);pf['id']='BRAM_SINGLE_PLATFORM_RECONSTRUCTED';pf['basis']='One reported/mapped platform and one definitely visible satellite road. Original OSM polygon crosses road and is retained in raw_platforms. Physical side inferred toward station-marker/access side southwest; approximate parallel footprint, not independently verified satellite width or current survey.';platforms=[pf];corrections.append({'platform_id':pf['id'],'reason':'Original mapped polygon straddles running centreline; do not trim into narrow disconnected pieces. Reconstruct a single usable southwest-side body parallel to the road, preserve source extent approximately, and explicitly retain uncertain side/width.','original_id':original['id'],'original_area_m2':src.area,'adopted_area_m2':Polygon(pf['xy']).area,'side_status':'inferred from marker/access-side context; not visually precise'})

 if code in ['MQU','TVP','NYY','KZT','TVCN','NJT','KZK']:
  rb=unary_union([LineString(w['xy']) for w in ww]).buffer(1.8,cap_style=2,join_style=2)
  for pf in platforms:
   p=Polygon(pf['xy']);cut=make_valid(p.difference(rb));pp=polygons(cut)
   if not pp:raise ValueError('Platform erased by rail envelope '+code+' '+pf['id'])
   largest=max(pp,key=lambda q:q.area)
   if largest.area<p.area-.01:
    pf['xy']=list(largest.exterior.coords);pf['basis']+='; mapped/inferred edge locally adjusted to1.8m visual rail-centre envelope, originalpolygon retained separately; notsurveyed'
    corrections.append({'platform_id':pf['id'],'reason':'Original geometry crossed adopted route envelope or source registration left less than1.8m rail-centre clearance; preserve connected largest body and source extent, omit tiny detached fragments. Dimensions remain visual reconstruction.','original_area_m2':p.area,'adopted_area_m2':largest.area,'retained_fraction':largest.area/p.area,'minimum_rail_centre_distance_m':largest.distance(unary_union([LineString(w['xy']) for w in ww])),'adopted_bounds':list(largest.bounds),'original_bounds':list(p.bounds),'discarded_fragment_area_m2':cut.area-largest.area})
 # Preserve current source metadata and metric transform, portable source citations only.
 out=R/code.lower();(out/'source').mkdir(parents=True,exist_ok=True);(out/'renders').mkdir(exist_ok=True)
 d=dict(code=code,name=st['station_name'],metadata=st,config=cfg,transform={'origin_lonlat':[lon,lat],'x_axis_east_north':u,'y_axis_east_north':n,'units':'metres','geodetic':'Local equirectangular, appropriate short model extent'},ways=ww,platforms=platforms,raw_platforms=raw_platforms,platform_corrections=corrections,excluded=excluded,cross_section_y=ys)
 compact(out/'source/layout.json',d)
 # Full geometric union removes superimposed duplicate rail heads at source connections.
 heads=[];webs=[];feet=[];flanges=[];ballast=[];offsets=[]
 for w in ww:
  ln=LineString(w['xy']);ballast.append(ln.buffer(1.75,cap_style=2,join_style=2))
  for sg in [-1,1]:
   run=ln.offset_curve(sg*.872,join_style=2);flange=ln.offset_curve(sg*.8155,join_style=2)
   heads.append(run.buffer(.034,cap_style=2,join_style=2));webs.append(run.buffer(.012,cap_style=2,join_style=2));feet.append(run.buffer(.075,cap_style=2,join_style=2));flanges.append(flange.buffer(.0225,cap_style=2,join_style=2));offsets.append((w['id'],sg,run))
 ch=unary_union(flanges);head=make_valid(unary_union(heads).difference(ch));web=make_valid(unary_union(webs).difference(ch));foot=make_valid(unary_union(feet))
 frogs=[]
 for i,(wid,sg,a) in enumerate(offsets):
  for wid2,sg2,b in offsets[i+1:]:
   if wid==wid2:continue
   hit=a.intersection(b)
   ps=[hit] if hit.geom_type=='Point' else [p for p in getattr(hit,'geoms',[]) if p.geom_type=='Point']
   for p in ps:
    if all(math.hypot(p.x-q['xy'][0],p.y-q['xy'][1])>.3 for q in frogs):frogs.append(dict(xy=[p.x,p.y],ways=[wid,wid2]))
 if code=='KZTW':frogs=[] # Three mapped main/bridge pieces are one physical road, not two turnouts.
 # Extract tapered tongues from the union itself, avoiding duplicate overlaid blade rails.
 nodes={};adj={};waynodes={}
 for w in ww:
  nn=[]
  for xy0 in w['xy']:
   key=(round(xy0[0],3),round(xy0[1],3));nodes[key]=xy0;nn.append(key)
  waynodes[w['id']]=nn
  for a,b in zip(nn,nn[1:]):
   if a!=b:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
 def unit2(p):
  ll=math.hypot(*p);return (p[0]/ll,p[1]/ll) if ll>.00001 else (1,0)
 def dot(a,b):return a[0]*b[0]+a[1]*b[1]
 blade_shapes=[];blade_sites=[]
 for nd,neighbors in adj.items():
  if len(neighbors)!=3:continue
  ns=list(neighbors);q=nodes[nd];vv=[unit2((nodes[n][0]-q[0],nodes[n][1]-q[1])) for n in ns];_,i,j=max((dot(vv[i],vv[j]),i,j) for i in range(3) for j in range(i+1,3));k=next(z for z in range(3) if z not in (i,j));branch=i if dot(vv[i],vv[k])>dot(vv[j],vv[k]) else j;bn=ns[branch];route=None;routeid=None
  for w in ww:
   nn=waynodes[w['id']]
   for ii,(a,b) in enumerate(zip(nn,nn[1:])):
    if a==nd and b==bn:route=w['xy'][ii:];routeid=w['id'];break
    if b==nd and a==bn:route=list(reversed(w['xy'][:ii+2]));routeid=w['id'];break
   if route:break
  if not route or len(route)<2:continue
  ln=substring(LineString(route),0,min(12,LineString(route).length))
  for sg in [-1,1]:
   run=ln.offset_curve(sg*.872,join_style=2);ll=run.length
   if ll<.5 or run.geom_type!='LineString':continue
   left=[];right=[]
   for jj in range(25):
    t=jj/24;di=t*ll;p0=run.interpolate(di);aa=run.interpolate(max(0,di-.02));bb=run.interpolate(min(ll,di+.02));du=unit2((bb.x-aa.x,bb.y-aa.y));nv=(-du[1],du[0]);hw=.003+.031*t;shift=-sg*.006*(1-t);left.append((p0.x+nv[0]*(shift+hw),p0.y+nv[1]*(shift+hw)));right.append((p0.x+nv[0]*(shift-hw),p0.y+nv[1]*(shift-hw)))
   blade_shapes.append(Polygon(left+list(reversed(right))))
  u=unit2((vv[i][0]+vv[j][0],vv[i][1]+vv[j][1]));blade_sites.append({'xy':q,'direction':u,'node_key':list(nd),'branch_way':routeid,'basis':'Degree3 mapped junction; tongue geometry reconstructed from source branch, not surveyed turnout type'})
 blades=make_valid(unary_union(blade_shapes).intersection(head)) if blade_shapes else Polygon();head=make_valid(head.difference(blades))
 guards=[]
 for f in frogs:
  p=Point(f['xy'])
  for wid in f['ways']:
   w=next(w for w in ww if w['id']==wid);ln=LineString(w['xy']);dist=ln.project(p);q=ln.interpolate(dist);aa=ln.interpolate(max(0,dist-.1));bb=ln.interpolate(min(ln.length,dist+.1));dx,dy=bb.x-aa.x,bb.y-aa.y;L=math.hypot(dx,dy)
   if L<.001:continue
   nx,ny=-dy/L,dx/L;sg=-1 if (p.x-q.x)*nx+(p.y-q.y)*ny>0 else 1;cut=substring(ln,max(0,dist-1.6),min(ln.length,dist+1.6));g=cut.offset_curve(sg*.768,join_style=2).buffer(.025,cap_style=2,join_style=2);guards.append(g)
 guard=make_valid(unary_union(guards).difference(ch).difference(head).difference(blades)) if guards else Polygon()
 bearer_sites=[]
 for f in frogs:
  fp=Point(f['xy'])
  if any(math.dist(f['xy'],q['center'])<8 for q in bearer_sites):continue
  w=next(w for w in ww if w['id']==f['ways'][0]);ln=LineString(w['xy']);di=ln.project(fp);q=ln.interpolate(di);aa=ln.interpolate(max(0,di-.1));bb=ln.interpolate(min(ln.length,di+.1));u=unit2((bb.x-aa.x,bb.y-aa.y));nv=(-u[1],u[0]);sg=1 if (fp.x-q.x)*nv[0]+(fp.y-q.y)*nv[1]>0 else -1;center=[q.x+nv[0]*sg*.45,q.y+nv[1]*sg*.45];bearer_sites.append({'center':center,'u':u,'half_length':3.25,'half_width':2.4,'basis':'Approximate extended crossing bearers replacing overlapping ordinary sleepers around physical frog; not exact turnout schedule'})
 pits=unary_union([LineString(w['xy']).buffer(.60,cap_style=2,join_style=2) for w in ww if code=='TVCN' and w['tags'].get('layer')=='-1'])
 ball=unary_union(ballast).difference(pits)
 xs=[p[0] for w in ww for p in w['xy']];ysall=[p[1] for w in ww for p in w['xy']];gh=max(140,max(ysall)-min(ysall)+140);yc=(max(ysall)+min(ysall))/2;terrain=box(min(xs)-45,yc-gh/2,max(xs)+45,yc+gh/2).difference(pits)
 rail=dict(method='Mapped running-rail polygon union with real45mm flange-channel subtraction. Nominal gauge1.676m at inner head faces. Visual crossing reconstruction, not a surveyed turnout design.',head=meshdata(head,.125,.178),blade=meshdata(blades,.125,.179),blade_sites=blade_sites,web=meshdata(web,.012,.135),guard=meshdata(guard,.125,.178),foot=meshdata(foot,-.015,.012),ballast=meshdata(ball,-.32,-.105),terrain=meshdata(terrain,-.55,-.34),pit_void_area_m2=pits.area,bearer_sites=bearer_sites,crossings=frogs,flangeway_width_m=.045,gauge_m=1.676,qa={'head_channel_intersection_area_m2':head.intersection(ch).area,'blade_channel_intersection_area_m2':blades.intersection(ch).area,'blade_head_overlap_area_m2':blades.intersection(head).area,'head_valid':head.is_valid,'web_valid':web.is_valid,'guard_channel_intersection_area_m2':guard.intersection(ch).area,'guard_running_head_overlap_m2':guard.intersection(head).area})
 compact(out/'source/rail_mesh.json',rail)
 compact(out/'source/platform_mesh.json',[dict(id=p['id'],**meshdata(Polygon(p['xy']),-.20,.95)) for p in platforms])
 print(code,len(ww),'source road pieces',len(platforms),'platform bodies',len(frogs),'crossings','centreYs',ys,flush=True)
 return d
if __name__=='__main__':
 for code in sys.argv[1:] or CONFIG:prepare(code)
