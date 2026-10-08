# Derive safe above-rail utilities from actual mapped alignments; don't draw
# arbitrary straight pipes through the fan of curved service roads.
col('16B_MAP_FOLLOWING_RAILSIDE_SERVICES')
segments=[(Vector(a),Vector(b)) for pp in route_paths.values() for a,b in zip(pp,pp[1:])]
def pointdist(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/max(v.length_squared,1e-12)));return (p-(a+v*t)).length
def clear(p,minimum=1.65):return all(pointdist(p,a,b)>=minimum for a,b in segments)
for wi,wid in enumerate(['641863870','641863872','641863874','641863876','641863878','641863880','641863882','641863884','641863886','641863888']):
 pts=route_paths.get(wid,[])
 sampleslist=list(samples(pts,2));previous=None
 for x,y,a in sampleslist:
  n=Vector((-math.sin(a),math.cos(a)));p=Vector((x,y))+n*2.2
  if not clear(p):previous=None;continue
  if previous is not None and (p-previous).length<3 and clear((p+previous)/2):
   rod('Map-following carriage water main',(*previous,.25),(*p,.25),.04,steel)
   d=p-previous;aa=math.atan2(d.y,d.x);mid=(p+previous)/2;box('Rail-clear inspection walkway',(*mid,-.02),(d.length,.55,.18),concrete,aa)
  previous=p
 for i,(x,y,a) in enumerate(samples(pts,24)):
  n=Vector((-math.sin(a),math.cos(a)));p=Vector((x,y))+n*2.2
  if not clear(p):continue
  rod('Map-following water riser',(*p,.25),(*p,.88),.034,steel);rod('Service water tap',(*p,.81),(p.x+.2,p.y,.81),.022,steel);box('Service tap handle',(p.x+.2,p.y,.84),(.14,.05,.04),red)
  if i%3==0:
   rod('Service pathway lamp',(*p,.1),(*p,3.2),.045,steel);box('Service pathway lamp hood',(*p,3.2),(.55,.22,.13),lit)
flush()
