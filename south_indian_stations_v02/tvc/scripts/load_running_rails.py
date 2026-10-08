col('10B_UNIONED_RUNNING_RAILS_WITH_FLANGEWAYS')
railmesh=json.loads((R/'source/running_rails_mesh.json').read_text())
for part,ma in [('foot',rust),('web',rust),('head',rail),('blade',rail)]:
 g=railmesh[part];o=mesh('Connected running rail '+part+' with genuine flangeways',g['vertices'],g['faces'],ma);o['construction']='Planar union of profile footprints, flange-channel subtraction; constrained triangulation';o['gauge_m']=1.676;o['flangeway_m']=.045
# Check rails next to actual crossing noses, aligned to their parent routes.
col('11B_CROSSING_CHECKRAILS_AND_FROG_FASTENINGS')
def nearpath(c,pts):
 best=None
 for a,b in zip(pts,pts[1:]):
  a=Vector(a);b=Vector(b);d=b-a;t=max(0,min(1,(c-a).dot(d)/max(d.length_squared,1e-9)));p=a+t*d;dist=(c-p).length
  if best is None or dist<best[0]:best=(dist,p,d.normalized())
 return best
frog_count=0
for item in railmesh['crossing_points']:
 c=Vector(item['xy'])
 if any((c-Vector(nodepos[nd])).length<4 for nd in turnouts):continue
 frog_count+=1
 for wid in item['ways']:
  pp=route_paths.get(wid)
  if not pp:continue
  dist,p,d=nearpath(c,pp);n=Vector((-d.y,d.x));sg=1 if (c-p).dot(n)>0 else -1
  # Opposite stockrail's inner check rail guides the flange past the common crossing.
  check=p-n*sg*.762
  q=[check-d*2+n*sg*.10,check-d*1.65,check+d*1.65,check+d*2+n*sg*.10]
  pathmesh('Frog opposite check-rail',q,[(-.031,.07),(.031,.07),(.031,.175),(-.031,.175)],rail)
  for tt in (-1.5,-.9,-.3,.3,.9,1.5):
   b=check+d*tt;box('Check rail bolted mounting',(*b,.035),(.22,.28,.06),rust,math.atan2(d.y,d.x))
   for ss in (-1,1):rod('Check rail bolt',(b.x+n.x*ss*.10,b.y+n.y*ss*.10,.06),(b.x+n.x*ss*.10,b.y+n.y*ss*.10,.08),.025,steel,6)
flush()
