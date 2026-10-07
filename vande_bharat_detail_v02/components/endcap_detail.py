"""Close the actual curved roof/end-wall crescent without blocking the gangway."""
import bpy
from common import mesh,box,remove_prefix,tube
P='VB02_END_'
def apply(ctx):
 remove_prefix(P);M=ctx['materials'];body=ctx['body'];C=ctx['collection'];kind=ctx['kind']
 for obj in list(bpy.data.objects):
  if obj.type=='MESH' and obj.name.split('.')[0] in ['End_wall','End_wall_top']:bpy.data.objects.remove(obj,do_unlink=True)
 profile=[(-1.62,3.13),(-1.59,3.36),(-1.46,3.58),(-1.23,3.73),(-.82,3.8),(0,3.82),(.82,3.8),(1.23,3.73),(1.46,3.58),(1.59,3.36),(1.62,3.13)]
 def top(y):
  for (a,z),(b,zz) in zip(profile,profile[1:]):
   if a<=y<=b:return z+(zz-z)*(y-a)/(b-a)
 ys=sorted(set([y for y,z in profile]+[-.55,.55]));ends=[-1] if kind=='DTC' else [-1,1]
 for sg in ends:
  x=sg*11.55
  for side in [-1,1]:box(P+'full_width_end_sidewall',(x,side*1.085,2.24),(.09,1.07,2.06),M['white'],body,C,b=.006)
  vv=[];ff=[]
  for a,b in zip(ys,ys[1:]):
   za,zb=top(a),top(b);low=3.38 if abs((a+b)/2)<.55 else min(3.20,za-.005,zb-.005)
   n=len(vv);vv.extend([(xx,y,z) for xx in [x-.03,x+.03] for y,z in [(a,low),(b,low),(b,zb),(a,za)]])
   ff.extend(tuple(n+i for i in face) for face in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
  mesh(P+'continuous_curved_roof_closure',vv,ff,M['white'],body,C)
  tube(P+'roof_end_seam',[(x-sg*.034,y,z+.001) for y,z in profile],.003,M['alloy'],body,C,N=8)
 return {'ends_closed':len(ends),'gangway_clear_width_m':1.10,'central_cap_bottom_z_m':3.38,'scope':'Curved roof crown and end-wall shell closure; no full opaque plate across passenger opening'}
