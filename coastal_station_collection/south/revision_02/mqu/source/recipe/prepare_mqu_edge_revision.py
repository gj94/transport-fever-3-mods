"""Prepare an immutable, source-documented boarding-edge completion."""
import json,sys,shutil,math
from pathlib import Path
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'));from prepare_geometry import Polygon,LineString,meshdata
src=B/'mqu';R=B/'revision_02/mqu';R.mkdir(parents=True,exist_ok=True)
for f in src.rglob('*'):
 if not f.is_file() or f.suffix in ['.blend','.blend1','.glb','.zip','.log'] or f.name in ['DELIVERY_MANIFEST.json','SHA256SUMS.txt']:continue
 p=R/f.relative_to(src);p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,p)
D=json.loads((R/'source/layout.json').read_text());pf=next(p for p in D['platforms'] if p['id']=='1409282832');old=list(pf['xy']);outer=old[:10];oldinner=old[10:18];road=next(w for w in D['ways'] if w['id']=='90772767');line=LineString(road['xy']);offset=line.offset_curve(2.0,join_style=2);coords=sorted(offset.coords);x0=oldinner[-1][0];x1=oldinner[0][0]
def at(x):
 for a,b in zip(coords,coords[1:]):
  if a[0]<=x<=b[0]:return [x,a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])]
 raise ValueError(x)
newinner=[at(x1),*reversed([list(p) for p in coords if x0<p[0]<x1]),at(x0)];oldpoly=Polygon(old);poly=oldpoly.union(Polygon(outer+newinner));assert poly.is_valid and poly.area>oldpoly.area and poly.distance(line)>1.99999
# It is an additive surface completion, with no loss of existing usable platform.
assert oldpoly.difference(poly).area<.01
pf['xy']=list(poly.exterior.coords);pf['basis']+='; northeast railward edge completed parallel to road90772767 at2.0m model clearance; original outer boundary/extent retained, satellite establishes adjacency but exact dimensions estimated'
record={'platform_id':pf['id'],'adjacent_road_id':'90772767','raw_polygon_preserved':True,'previous_adopted_polygon':old,'adopted_polygon':pf['xy'],'previous_rail_distance_m':oldpoly.distance(line),'adopted_rail_distance_m':poly.distance(line),'added_surface_area_m2':poly.area-oldpoly.area,'old_inner_edge':oldinner,'new_inner_edge':newinner,'basis':'MQU_satellite_undated.png shows two developed outer bodies around three rail alignments, with northeast boarding edge alongside outer road; exact edge dimension reconstructed','accessed_date':'2026-10-08','image_capture_date':'not exposed','scope':'Only additive boarding surface, coping, safety edge and paving joints. Existing furniture, bridge, building and rails remain unchanged.'};D['platform_corrections'].append(record);(R/'source/layout.json').write_text(json.dumps(D,indent=2));(R/'source/evidence').mkdir(exist_ok=True);(R/'source/evidence/MQU_boarding_edge_adoption.json').write_text(json.dumps(record,indent=2));(R/'source/platform_mesh.json').write_text(json.dumps([dict(id=p['id'],**meshdata(Polygon(p['xy']),-.20,.95)) for p in D['platforms']]));print('ADOPTED',record['previous_rail_distance_m'],record['adopted_rail_distance_m'],record['added_surface_area_m2'])
