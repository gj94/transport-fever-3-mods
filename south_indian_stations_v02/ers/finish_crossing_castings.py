# Construct one local cast crossing top from a convex envelope, then subtract
# the two45mm flange channels. This retains supporting metal between channels,
# instead of leaving full-width long gaps in both intersecting running heads.
collection('21 | CROSSING CASTINGS • clipped flange channels')
for ob in list(scene.objects):
 if ob.name.startswith('Derived manganese frog nose '):bpy.data.objects.remove(ob,do_unlink=True)
def hull(pp):
 pp=sorted(set((float(p.x),float(p.y)) for p in pp))
 def c(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pp:
  while len(lo)>=2 and c(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pp):
  while len(hi)>=2 and c(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return [Vector(p) for p in lo[:-1]+hi[:-1]]
def halfclip(poly,n,bound,lower):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa=a.dot(n)-bound;fb=b.dot(n)-bound;ina=fa<=1e-9 if lower else fa>=-1e-9;inb=fb<=1e-9 if lower else fb>=-1e-9
  if ina:out.append(a)
  if ina!=inb:out.append(a+(b-a)*(fa/(fa-fb)))
 return out
polys_count=0
for idx,(p,ri,rj,da,db,sa,sb) in enumerate(events):
 # Use original orientation for each rail's inside-gauge side.
 dirs=[]
 for rr,ss in [(R[ri],sa),(R[rj],sb)]:dirs.append((sample(rr,ss+.10)-sample(rr,ss-.10)).normalized())
 da,db=dirs;st=abs(cross(da,db));extent=(.030+.045)/max(st,.015)
 corners=[]
 for d in dirs:
  n=Vector((-d.y,d.x))
  for sg in [-1,1]:
   for side in [-1,1]:corners.append(p+d*extent*sg+n*.062*side)
 pieces=[hull(corners)]
 for rr,d in [(R[ri],da),(R[rj],db)]:
  n=Vector((-d.y,d.x));offset=-rr['side']*(.030+.045/2);center=p.dot(n)+offset
  remaining=[]
  for poly in pieces:
   for lower,bound in [(True,center-.045/2),(False,center+.045/2)]:
    q=halfclip(poly,n,bound,lower)
    if len(q)>=3:remaining.append(q)
  pieces=remaining
 for part,poly in enumerate(pieces):
  prism('Cast crossing '+str(idx)+' flange-separated part '+str(part),[(q.x,q.y) for q in poly],.515,.643,railhead);polys_count+=1
 # Low mounting casting stays well below flanges, not at running-head height.
 prism('Crossing sole casting '+str(idx),[(q.x,q.y) for q in hull(corners)],.46,.485,railmat)
q=json.loads((P/'physical_pointwork.json').read_text());q['flange_separated_casting_parts']=polys_count;q['crossing_surface']='Convex local crossing casting clipped by both45mm normal flange channels; supporting nose/wing pieces retained.';(P/'physical_pointwork.json').write_text(json.dumps(q,indent=2))
# Dark granular ballast, no pale concrete-looking base.
bs=ballast.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.065,.073,.065,1)
for node in ballast.node_tree.nodes:
 if node.type=='VALTORGB':
  node.color_ramp.elements[0].color=(.035,.042,.035,1);node.color_ramp.elements[1].color=(.14,.15,.13,1)
 if node.type=='BUMP':node.inputs['Strength'].default_value=.45;node.inputs['Distance'].default_value=.06
# Continuous shared ballast underneath the common turnout bearer envelopes.
beds=Batch('Shared turnout granular formation',ballast)
for k in range(math.floor(-510/.65),math.ceil(850/.65)):
 x=k*.65
 for ya,yb in bands_at(x):beds.box((x,(ya+yb)/2,.18),(.65,yb-ya+.5,.28))
beds.finish()
# Trapezoidal outer shoulders instead of vertical blocks, where running beds remain.
for ob in scene.objects:
 if not ob.name.startswith('Ballast formation '):continue
 vv=ob.data.vertices
 for i in range(0,len(vv),4):
  if i+3>=len(vv):break
  center=(vv[i+2].co+vv[i+3].co)/2
  for j in [i+2,i+3]:vv[j].co=center+(vv[j].co-center)*.84
