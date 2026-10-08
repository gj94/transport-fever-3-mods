"""Explicitly simplified fixed crossing geometry for compound mapped junctions.
Planar unions eliminate duplicate stock rails;46mm route-normal flange channels are subtracted.
These are visual reconstructions preserving source routes, not certified movable-point/interlocking designs.
Requires Shapely2.2 in Blender Python, or set NCJ_SHAPELY_PATH to its compatible installation.
"""
import bpy,sys,os,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,os.environ.get('NCJ_SHAPELY_PATH','/tmp/ncj_shapely313'))
import shapely
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union,substring
from shapely.affinity import rotate,translate
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
cases=json.loads((R/'references/physical_turnout_cases.json').read_text());source=json.loads((R/'references/local_geometry.json').read_text());nodes=json.loads((R/'references/turnout_source_nodes.json').read_text())
# Node coordinates derive directly from source XML, including compound nodes outside proof subset.
nodepos=json.loads((R/'references/junction_node_positions.json').read_text())
excluded=[n for n in cases['excluded'] if n['node'] in nodepos]
simplemask=unary_union([Polygon(c['poly']).buffer(.03) for c in cases['accepted']]);region=unary_union([Point(nodepos[n['node']]).buffer(23,quad_segs=8) for n in excluded]).difference(simplemask)
# Saved domain geometry is evidence of exact corrected extent.
(R/'references/compound_domains.geojson').write_text(json.dumps(shapely.geometry.mapping(region)))
for c in list(bpy.data.collections):
 if c.name.startswith('37_COMPOUND_CROSSINGS'):
  for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(c)
C=bpy.data.collections.new('37_COMPOUND_CROSSINGS_SIMPLIFIED');s.collection.children.link(C);C['scope']='14 compound/short junctions: unioned mapped rail profiles and normal flange channels; fixed visual approximation, no interlocking claim.'
RUST=bpy.data.materials['Rusty rail sides'];HEAD=bpy.data.materials['Polished running rail'];BALL=bpy.data.materials['Angular granite ballast'];CON=bpy.data.materials['Prestressed concrete sleeper'];DARK=bpy.data.materials['Painted charcoal steel']
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in g.geoms for p in polys(x)] if hasattr(g,'geoms') else []
def append_poly(g,z0,z1,vs,fs):
 # Constrained triangulation respects flangeway holes. Exterior/interior walls close the solid.
 for p in polys(g):
  if p.area<1e-8:continue
  triangles=shapely.constrained_delaunay_triangles(p)
  for tri in triangles.geoms:
   xy=list(tri.exterior.coords)[:3];k=len(vs);vs.extend([(x,y,z) for z in [z0,z1] for x,y in xy]);fs.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
  for ring in [p.exterior]+list(p.interiors):
   coords=list(ring.coords)
   for a,b in zip(coords,coords[1:]):
    k=len(vs);vs.extend([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)]);fs.append((k,k+1,k+2,k+3))
def make(n,g,z0,z1,m):
 vs=[];fs=[];append_poly(g,z0,z1,vs,fs)
 if not vs:return None
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m);return o
# Build source-centreline offsets; no copies of common stock rails survive the planar union.
records=[];centres=[];channels=[]
for w in source:
 if w['tags'].get('railway')!='rail':continue
 line=LineString([(x+45,y) for x,y in w['local']]);clip=line.intersection(region.buffer(4))
 if clip.is_empty:continue
 pieces=list(clip.geoms) if hasattr(clip,'geoms') else [clip]
 for linepart in pieces:
  if linepart.geom_type!='LineString' or linepart.length<.1:continue
  centres.append(linepart)
  for side in [-1,1]:
   rail=linepart.offset_curve(side*.8705,join_style='mitre');records.append({'id':w['id'],'side':side,'rail':rail,'centre':linepart})
   channels.append(linepart.offset_curve(side*.815,join_style='mitre').buffer(.023,cap_style='flat',join_style='mitre'))
channel=unary_union(channels);beds=unary_union([l.buffer(1.73,cap_style='flat',join_style='mitre') for l in centres]).intersection(region)
# Clip original rail, sleeper, fastening and ballast boxes exactly at domain boundary.
clipped={}
for o in list(s.objects):
 if o.type!='MESH':continue
 israil=o.name.startswith('Rail ');istie=o.name.startswith(('Concrete sleepers','Pit line discrete rail supports'));isfast=o.name.startswith(('Rail seat pads','Elastic rail clips'));isball=o.name.startswith('Granite ballast formation')
 if not (israil or istie or isfast or isball):continue
 vs0=[o.matrix_world@v.co for v in o.data.vertices]
 if len(vs0)%8:continue
 vs=[];fs=[];count=0
 for i in range(0,len(vs0),8):
  vv=vs0[i:i+8];xy=[(vv[j].x,vv[j].y) for j in [0,4,6,2]];p=Polygon(xy)
  if not p.is_valid:p=p.buffer(0)
  if not region.intersects(p):
   k=len(vs);vs.extend(vv);fs.extend(tuple(k+j for j in f) for f in F);continue
  count+=1;left=p.difference(region);append_poly(left,min(v.z for v in vv),max(v.z for v in vv),vs,fs)
 if count:
  d=bpy.data.meshes.new(o.name+' compound corrected');d.from_pydata(vs,[],fs);d.update()
  for m in o.data.materials:d.materials.append(m)
  o.data=d;o.matrix_world.identity();clipped[o.name]=count
# Profile unions with route-normal open flange corridors. All crossings have one geometric head surface.
heads=unary_union([r['rail'].buffer(.0325,cap_style='flat',join_style='mitre') for r in records]).difference(channel).intersection(region)
webs=unary_union([r['rail'].buffer(.008,cap_style='flat',join_style='mitre') for r in records]).difference(channel).intersection(region)
feet=unary_union([r['rail'].buffer(.075,cap_style='flat',join_style='mitre') for r in records]).intersection(region)
assert heads.is_valid and not heads.is_empty, 'Compound rail union failed'
make('Compound unioned running rail heads with46mm channels',heads,.46,.5,HEAD);make('Compound unioned rail webs',webs,.372,.472,RUST);make('Compound unioned rail feet',feet,.3525,.3775,RUST)
# Opposite guard rails around actual intersection points, separate from the running lines.
guards=[];intersections=[]
for i,a in enumerate(records):
 for b in records[i+1:]:
  if a['id']==b['id']:continue
  hit=a['rail'].intersection(b['rail'])
  points=[hit] if hit.geom_type=='Point' else list(hit.geoms) if hit.geom_type=='MultiPoint' else []
  for p in points:
   if not region.contains(p):continue
   if all(p.distance(q)>.25 for q in intersections):intersections.append(p)
   for r in [a,b]:
    d=r['centre'].project(p);part=substring(r['centre'],max(0,d-2),min(r['centre'].length,d+2))
    if part.geom_type!='LineString':continue
    guard=part.offset_curve(-r['side']*.7595,join_style='mitre').buffer(.0325,cap_style='flat',join_style='mitre');guards.append(guard)
if guards:make('Compound opposite checkrail heads',unary_union(guards).difference(channel).difference(heads.buffer(.002)).intersection(region),.3775,.498,RUST)
make('Compound continuous granite ballast support',beds,-.06,.211,BALL)
# A single aligned bearer field per connected fan. Intersections produce no overlapping old ties.
newties=[];tieaxes=[]
for p in polys(beds):
 rr=list(p.minimum_rotated_rectangle.exterior.coords);edges=[(math.dist(a,b),a,b) for a,b in zip(rr,rr[1:])];_,a,b=max(edges);theta=math.atan2(b[1]-a[1],b[0]-a[0]);angle=math.degrees(theta);rot=rotate(p,-angle,origin=(0,0));x0,y0,x1,y1=rot.bounds
 for j in range(math.ceil((x1-x0)/.6)):
  x=x0+j*.6;bar=rotate(box(x-.135,y0-.1,x+.135,y1+.1),angle,origin=(0,0));g=bar.intersection(p)
  if not g.is_empty:newties.append(g)
  tieaxes.append(rotate(LineString([(x,y0-1),(x,y1+1)]),angle,origin=(0,0)))
make('Compound single clipped bearer array',unary_union(newties),.21,.36,CON)
# Fresh rail-seat plates at actual bearer/rail intersections.
plates=[]
for axis in tieaxes:
 for r in records:
  if not axis.intersects(r['rail']):continue
  hit=axis.intersection(r['rail']);pp=[hit] if hit.geom_type=='Point' else list(hit.geoms) if hit.geom_type=='MultiPoint' else []
  for p in pp:
   if beds.contains(p):plates.append(box(p.x-.10,p.y-.10,p.x+.10,p.y+.10))
if plates:make('Compound rail seat pads',unary_union(plates),.36,.384,DARK)
report={'compound_node_count':len(excluded),'nodes':excluded,'profile_method':'Boolean union of all mapped rail ribbons, subtract46mm normal inner flange channels, constrained triangulation with holes. Simple physical switch domains excluded.','crossing_locations':[[p.x,p.y] for p in intersections],'replacement_head_area_m2':heads.area,'normal_flangeway_m':.046,'old_components_clipped':clipped,'fixed_visual_approximation':True,'interlocking_or_fabrication_certified':False}
(R/'QA_COMPOUND_CROSSINGS.json').write_text(json.dumps(report,indent=2));s['compound_crossing_treatment']='14nodes: source-route rail unions +46mm flange channels +one clipped bearer field; simplified fixed visual crossings, not movable pointwork/interlocking.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('COMPOUND_CROSSINGS_SAVED',len(excluded),len(intersections),flush=True)
