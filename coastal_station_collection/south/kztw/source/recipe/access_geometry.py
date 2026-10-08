"""Pure geometry helpers for source-aware reconstructed approach links."""
import math

def approach_end(D,x,building_y,side,overlap=.30):
 candidates=[]
 for pf in D['platforms']:
  ys=[]
  for a,b in zip(pf['xy'],pf['xy'][1:]):
   if min(a[0],b[0])<=x<max(a[0],b[0]) and abs(a[0]-b[0])>1e-8:ys.append(a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1]))
  if len(ys)>=2:
   edge=max(ys) if side>0 else min(ys);candidates.append((abs(edge-building_y),edge,pf['id']))
 if not candidates:raise ValueError('No platform section at approach longitude')
 _,edge,pfid=min(candidates);return edge-side*overlap,pfid,edge

def _dist(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def _cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def _segments(a,b,c,d):
 if max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])) and _cross(a,b,c)*_cross(a,b,d)<=0 and _cross(c,d,a)*_cross(c,d,b)<=0:return 0
 return min(_dist(a,c,d),_dist(b,c,d),_dist(c,a,b),_dist(d,a,b))
def link_clearance(D,x,ya,yb,width):
 lo,hi=sorted([ya,yb]);vs=[(x-width/2,lo),(x+width/2,lo),(x+width/2,hi),(x-width/2,hi)];best=(float('inf'),None)
 for way in D['ways']:
  for a,b in zip(way['xy'],way['xy'][1:]):
   v=0 if any(x-width/2<=p[0]<=x+width/2 and lo<=p[1]<=hi for p in [a,b]) else min(_segments(a,b,vs[i],vs[(i+1)%4]) for i in range(4))
   if v<best[0]:best=(v,way['id'])
 assert best[0]>=1.80,('Approach conflicts with rail clearance',best)
 return {'minimum_adopted_rail_centerline_distance_m':best[0],'nearest_rail_way':best[1],'required_model_clearance_m':1.8,'platform_contact':'Endpoint is0.30m inside a source platform cross-section, not extrapolated from the main-building origin'}
