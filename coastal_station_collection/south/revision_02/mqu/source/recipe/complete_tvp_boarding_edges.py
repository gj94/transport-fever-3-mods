"""Complete observed boarding edges; preserve raw mapped footprints and outer boundaries."""
import json,sys,math
from pathlib import Path
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from prepare_geometry import meshdata,Polygon,LineString,unary_union
R=B/'tvp';p=R/'source/layout.json';D=json.loads(p.read_text());allrails=unary_union([LineString(w['xy']) for w in D['ways']]);records=[]
for pid,wid,side in [('1081587507','385040650',-1),('1081587508','608428979',1)]:
 pf=next(p for p in D['platforms'] if p['id']==pid);old=Polygon(pf['xy']);raw=next(p for p in D['raw_platforms'] if p['id']==pid);coords=raw['xy'][:-1];w=next(w for w in D['ways'] if w['id']==wid);road=sorted(w['xy']);outer=sorted(coords,key=lambda p:p[1])[:2] if side<0 else sorted(coords,key=lambda p:p[1])[-2:];outer=sorted(outer);x0,x1=outer[0][0],outer[1][0]
 def ry(x):
  for a,b in zip(road,road[1:]):
   if a[0]<=x<=b[0]:return a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
  raise ValueError(x)
 # Both local rail segments are effectively straight across this observed platform extent.
 edge=[[x,ry(x)+side*1.8*math.sqrt(1+((ry(x1)-ry(x0))/(x1-x0))**2)] for x in [x0,x1]]
 poly=Polygon([outer[0],outer[1],edge[1],edge[0]]);assert poly.is_valid and poly.area>old.area;assert poly.distance(allrails)>1.79999
 pf['xy']=list(poly.exterior.coords);pf['basis']+='; hospital/opposite boarding edge completed parallel to its adjacent mapped road at1.8m model centreline clearance, preserving outer mapped boundary and length; Google satellite shows developed boarding surfaces, exact offset reconstructed and not surveyed'
 rec={'platform_id':pid,'adjacent_road_id':wid,'reason':'Mapped polygon does not reach the observed boarding face. Complete only railward edge; retain outer boundary and source length. Satellite supports adjacency, not exact dimensions.','raw_polygon_preserved':True,'prior_adopted_polygon':list(old.exterior.coords),'adopted_polygon':list(poly.exterior.coords),'previous_minimum_rail_centre_distance_m':old.distance(allrails),'minimum_rail_centre_distance_m':poly.distance(allrails),'adopted_area_m2':poly.area,'basis_screenshot':'TVP_satellite_undated.png','image_acquisition_date':'not exposed','accessed_date':'2026-10-08'};D['platform_corrections'].append(rec);records.append(rec)
p.write_text(json.dumps(D,indent=2));(R/'source/platform_mesh.json').write_text(json.dumps([dict(id=p['id'],**meshdata(Polygon(p['xy']),-.20,.95)) for p in D['platforms']]));(R/'source/evidence').mkdir(exist_ok=True);(R/'source/evidence/TVP_boarding_edge_adoption.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
