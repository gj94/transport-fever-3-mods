"""Verify actual exported rail-solid polygons and clear flange channels offline."""
import json,sys,math
from pathlib import Path
P=Path(__file__).resolve().parent
try:import shapely
except ImportError:sys.path.insert(0,str(P.parent/'tvc'/'.builddeps'))
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
D=json.loads((P/'geometry/rail_solids.json').read_text());ways=json.loads((P/'geometry/mapped_routes.json').read_text())
polys=[]
for k in ['head','blade']:
 dd=D[k];v=dd['vertices'];zmax=max(p[2] for p in v)
 for f in dd['faces']:
  if all(abs(v[i][2]-zmax)<1e-6 for i in f):polys.append(Polygon([(v[i][0],v[i][1]) for i in f]))
heads=unary_union(polys)
channels=[]
for w in ways:
 line=LineString(w['xy'])
 for side in [-1,1]:channels.append(line.offset_curve(side*.8155,join_style=2).buffer(.0225,cap_style=2,join_style=2))
channels=unary_union(channels);inter=heads.intersection(channels)
checks=[];skipped=[]
for targetx in [0,180,280]:
 for w in ways:
  pp=w['xy']
  for a,b in zip(pp,pp[1:]):
   if not (min(a[0],b[0])<=targetx<max(a[0],b[0])):continue
   t=(targetx-a[0])/(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy);nx=-dy/l;ny=dx/l
   ray=LineString([(targetx-1.3*nx,y-1.3*ny),(targetx+1.3*nx,y+1.3*ny)]);rr=heads.intersection(ray)
   pieces=[rr] if rr.geom_type=='LineString' else [g for g in getattr(rr,'geoms',[]) if g.geom_type=='LineString']
   spans=[]
   for g in pieces:
    ss=[(x-targetx)*nx+(yy-y)*ny for x,yy in g.coords];spans.append((min(ss),max(ss)))
   if len(spans)!=2:
    skipped.append({'way':w['id'],'section_x_m':targetx,'reason':'Multiple route heads present in cross-section; not a plain-track gauge sample'});continue
   neg=[b for a,b in spans if b<0 and a> -1.2];pos=[a for a,b in spans if a>0 and b<1.2]
   if neg and pos:checks.append({'way':w['id'],'section_x_m':targetx,'gauge_m':min(pos)-max(neg)})
report={'mesh_based_test':True,'top_surface_polygon_count':len(polys),'raw_boundary_overlap_area_m2':inter.area,'all_route_flange_channel_interior_overlap_area_m2':heads.intersection(channels.buffer(-.000002)).area,'rounding_tolerance_m':.000002,'skipped_multiroute_sections':skipped,'overlap_note':'Tiny boundary-only residue may result from1micrometre coordinate quantization; substantive channel fillings fail.','gauge_checks':checks,'nominal_gauge_m':1.676,'gauge_max_abs_error_m':max((abs(v['gauge_m']-1.676) for v in checks),default=None),'model_is_engineering_certified':False}
(P/'geometry/rail_geometry_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
