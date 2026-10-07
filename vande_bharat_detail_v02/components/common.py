"""Deterministic editable mesh construction, metres, world-coordinate input by default."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from math import pi, sin, cos

def collection(name):
 c=bpy.data.collections.get(name)
 if not c:c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
 return c

def remove_prefix(prefix):
 for o in list(bpy.data.objects):
  if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)

def hide_prefix(prefixes):
 for o in bpy.data.objects:
  if o.name.startswith(tuple(prefixes)):
   o.hide_render=True;o.hide_viewport=True;o['v02_replaced']=True

def mesh(n,verts,faces,m=None,parent=None,coll=None,bevel=0,smooth=False,local=False):
 me=bpy.data.meshes.new(n+'_mesh');me.from_pydata(verts,[],faces);me.update()
 # Reflection-built closed parts must retain outward surface normals for real refraction.
 bm=bmesh.new();bm.from_mesh(me)
 if bm.faces and all(ed.is_manifold for ed in bm.edges) and bm.calc_volume(signed=True)<0:
  bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(me);me.update()
 bm.free();o=bpy.data.objects.new(n,me)
 (coll or bpy.context.scene.collection).objects.link(o)
 if parent:
  o.parent=parent
  if not local:o.matrix_parent_inverse=parent.matrix_world.inverted()
 if m:
  if isinstance(m,(list,tuple)):
   for mm in m:me.materials.append(mm)
  else:me.materials.append(m)
 if smooth:
  for f in me.polygons:f.use_smooth=True
 if bevel:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=3;mod.affect='EDGES'
  mod=o.modifiers.new('Weighted hard surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return o

def box(n,c,d,m=None,parent=None,coll=None,b=.003,local=False):
 x,y,z=[v/2 for v in d];X,Y,Z=c;v=[(X+a,Y+bb,Z+cc) for a,bb,cc in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
 return mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,parent,coll,b,local=local)

def cyl(n,c,r,d,m=None,parent=None,coll=None,axis='Z',N=32,bevel=0,local=False):
 v=[(r*cos(2*pi*i/N),r*sin(2*pi*i/N),z) for z in [-d/2,d/2] for i in range(N)]
 f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 if axis=='Y':v=[(a,cc,-bb) for a,bb,cc in v]
 if axis=='X':v=[(cc,bb,-a) for a,bb,cc in v]
 v=[(a+c[0],bb+c[1],cc+c[2]) for a,bb,cc in v];o=mesh(n,v,f,m,parent,coll,bevel,local=local)
 for p in o.data.polygons:
  if len(p.vertices)==4:p.use_smooth=True
 return o

def lathe(n,c,profile,m=None,parent=None,coll=None,axis='Z',N=64,local=False):
 """Profile list (axis_position,radius); welded real poles and closed-profile seam."""
 vs=[];fs=[];rings=[]
 for k,(z,r) in enumerate(profile):
  if k==len(profile)-1 and abs(z-profile[0][0])<1e-10 and abs(r-profile[0][1])<1e-10:
   rings.append(rings[0]);continue
  ids=[]
  for j in range(1 if abs(r)<1e-10 else N):
   a,b=r*cos(2*pi*j/N),r*sin(2*pi*j/N);q=(z,a,b) if axis=='X' else (a,z,b) if axis=='Y' else (a,b,z)
   ids.append(len(vs));vs.append(tuple(q[t]+c[t] for t in range(3)))
  rings.append(ids)
 for lo,hi in zip(rings[:-1],rings[1:]):
  if len(lo)==1 and len(hi)==1:continue
  for j in range(N):
   k=(j+1)%N
   if len(lo)==1:fs.append((lo[0],hi[k],hi[j]))
   elif len(hi)==1:fs.append((lo[j],lo[k],hi[0]))
   else:fs.append((lo[j],lo[k],hi[k],hi[j]))
 return mesh(n,vs,fs,m,parent,coll,smooth=True,local=local)

def ring(n,c,ro,ri,d,m=None,parent=None,coll=None,axis='Y',N=48,local=False):
 return lathe(n,c,[(-d/2,ri),(-d/2,ro),(d/2,ro),(d/2,ri),(-d/2,ri)],m,parent,coll,axis,N,local)

def tube(n,points,r,m=None,parent=None,coll=None,N=12,local=False,closed=False):
 pts=[Vector(p) for p in points];vs=[]
 if len(pts)>2 and (pts[0]-pts[-1]).length<1e-7:closed=True;pts=pts[:-1]
 for i,p in enumerate(pts):
  prev=pts[(i-1)%len(pts)] if closed else pts[max(0,i-1)];next=pts[(i+1)%len(pts)] if closed else pts[min(i+1,len(pts)-1)]
  tangent=(next-prev).normalized();q=tangent.to_track_quat('Z','Y')
  vs += [tuple(p+q@Vector((r*cos(2*pi*j/N),r*sin(2*pi*j/N),0))) for j in range(N)]
 fs=[] if closed else [tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))]
 for i in range(len(pts) if closed else len(pts)-1):
  k=(i+1)%len(pts)
  fs += [(i*N+j,i*N+(j+1)%N,k*N+(j+1)%N,k*N+j) for j in range(N)]
 return mesh(n,vs,fs,m,parent,coll,smooth=True,local=local)

def rod(n,a,b,r,m=None,parent=None,coll=None,N=16,local=False):return tube(n,[a,b],r,m,parent,coll,N,local)

def beam(n,a,endpoint,width,height,m=None,parent=None,coll=None,local=False,b=.002):
 a,bp=Vector(a),Vector(endpoint);d=bp-a;q=d.to_track_quat('X','Z');c=(a+bp)/2
 vs=[c+q@Vector((xx*d.length/2,yy*width/2,zz*height/2)) for xx,yy,zz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(n,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,parent,coll,b,local=local)

def rounded_rect(w,h,r,N=8):
 pts=[]
 for x,z,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for i in range(N+1):
   a=math.radians(start+i*90/N);pts.append((x+r*cos(a),z+r*sin(a)))
 return pts

def extrude_xy(n,poly,z0,z1,m=None,parent=None,coll=None,bevel=.005):
 N=len(poly);vs=[(x,y,z) for z in [z0,z1] for x,y in poly];fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(n,vs,fs,m,parent,coll,bevel)

def bolt(n,c,r=.01,d=.009,m=None,parent=None,coll=None,axis='Z',washer=True,local=False):
 o=cyl(n+' hex head',c,r,d,m,parent,coll,axis,6,.0007,local)
 if washer:
  cc=list(c);idx='XYZ'.index(axis);cc[idx]-=d*.50
  ring(n+' washer',cc,r*1.32,r*.52,d*.20,m,parent,coll,axis,24,local)
 return o

def slotted_screw(n,c,r=.007,m=None,dark=None,parent=None,coll=None,axis='X'):
 o=cyl(n+' domed screw',c,r,.004,m,parent,coll,axis,20,.0009)
 cc=list(c);cc['XYZ'.index(axis)]+=.0025
 if axis=='X':dim=(.0005,r*1.05,.0013)
 elif axis=='Y':dim=(r*1.05,.0005,.0013)
 else:dim=(r*1.05,.0013,.0005)
 box(n+' screw slot',cc,dim,dark or m,parent,coll,b=.0002)
 return o

def sphere(n,c,r,m=None,parent=None,coll=None,N=24,R=12,scale=(1,1,1)):
 vs=[(c[0],c[1],c[2]+r*scale[2])];fs=[]
 for j in range(1,R):
  a=pi*j/R
  for i in range(N):
   t=2*pi*i/N;vs.append((c[0]+r*sin(a)*cos(t)*scale[0],c[1]+r*sin(a)*sin(t)*scale[1],c[2]+r*cos(a)*scale[2]))
 last=len(vs);vs.append((c[0],c[1],c[2]-r*scale[2]))
 for i in range(N):fs.append((0,1+i,1+(i+1)%N));fs.append((1+(R-2)*N+i,last,1+(R-2)*N+(i+1)%N))
 for j in range(R-2):
  for i in range(N):fs.append((1+j*N+i,1+(j+1)*N+i,1+(j+1)*N+(i+1)%N,1+j*N+(i+1)%N))
 return mesh(n,vs,fs,m,parent,coll,smooth=True)

def bezier_points(points,steps=12):
 # Catmull-Rom path with repeated end points, for physically continuous hose curvature.
 p=[Vector(points[0])]+[Vector(x) for x in points]+[Vector(points[-1])];out=[]
 for j in range(1,len(p)-2):
  a,b,c,d=p[j-1:j+3]
  for i in range(steps):
   t=i/steps;out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
 out.append(tuple(p[-2]));return out
