"""Contoured cushions and original upholstery details for later refinement pass."""
import math

def back(g,name,c,size,mat,parent,high=True,face=1):
 """Closed quiltless chair back; sloped ergonomic face, rounded shoulders."""
 x,y,z=c;thick,width,height=size;NY=16;NZ=24;vs=[]
 for rear in [False,True]:
  for iz in range(NZ+1):
   v=iz/NZ
   # Rounded shoulders/corners retain a broad head-support area.
   shoulder=1-.18*max(0,(v-.83)/.17)**2-.10*max(0,(.09-v)/.09)**2
   for iy in range(NY+1):
    u=iy/NY*2-1
    yy=y+u*width/2*shoulder
    zz=z+(v-.5)*height
    recline=-.105*(v-.5) if high else -.048*(v-.5)
    contour=.025*(1-u*u)+.018*math.sin(math.pi*v) if not rear else -.008*(1-u*u)
    xx=x+face*(recline+(-thick/2 if rear else thick/2)+contour)
    vs.append((xx,yy,zz))
 K=(NY+1)*(NZ+1);fs=[]
 for rear in [0,1]:
  for iz in range(NZ):
   for iy in range(NY):
    q=rear*K+iz*(NY+1)+iy;f=(q,q+1,q+NY+2,q+NY+1);fs.append(tuple(reversed(f)) if rear else f)
 for iz in range(NZ):
  for iy in [0,NY]:
   a=iz*(NY+1)+iy;b=(iz+1)*(NY+1)+iy;fs.append((a,b,b+K,a+K))
 for iz in [0,NZ]:
  for iy in range(NY):
   a=iz*(NY+1)+iy;fs.append((a,a+K,a+K+1,a+1))
 ob=g.mesh(name+' shaped upholstery',vs,fs,mat,parent)
 for p in ob.data.polygons:p.use_smooth=True
 if mat!=g.UPHOL:return ob
 # Surface seams run down the contoured face; small enough to read only close up.
 for u in [-.62,.62]:
  pts=[]
  for j in range(25):
   v=.09+j*.80/24;shoulder=1-.18*max(0,(v-.83)/.17)**2
   yy=y+u*width/2*shoulder;zz=z+(v-.5)*height
   xx=x+face*(-(.105 if high else .048)*(v-.5)+thick/2+.025*(1-u*u)+.018*math.sin(math.pi*v)+.001)
   pts.append((xx,yy,zz))
  g.path('Chair upholstered face tailored seam',pts,.0013,g.SEAM,parent,6)
 ob['component']='contoured_chair_back';return ob

def first_class_details(g):
 start=-7.5;spec=[('A',3,4),('B',3,4),('C',2,2),('D',2,2),('E',2,2),('F',3,4)];floor=g.FLOORZ
 for label,length,n in spec:
  end=start+length;xs=[start+.41,end-.41] if n==4 else [start+.42]
  for j,x in enumerate(xs):
   face=1 if j==0 else -1
   wx=start+.044 if j==0 else end-.044
   for lamp_z in [2.65,3.44]:
    g.box('First AC individual reading light mount',(wx,-1.17,lamp_z),(.026,.16,.18),g.TRIM,g.INTERIOR,.007)
    g.box('First AC shielded reading lamp',(wx+face*.047,-1.17,lamp_z),(.075,.135,.10),g.TRIM,g.INTERIOR,.018)
    g.box('First AC reading lamp diffuser',(wx+face*.086,-1.17,lamp_z-.018),(.003,.099,.047),g.LAMP,g.INTERIOR,.003)
    g.box('First AC personal lamp switch',(wx+face*.020,-1.17,lamp_z-.118),(.014,.043,.055),g.DARK,g.INTERIOR,.005)
   for y in [-1.385,.405]:
    # Upholstered hinged armrests, as seen in conventional first-AC cabins.
    g.box('First AC upholstered arm pad',(x+face*.025,y,floor+.67),(.56,.075,.069),g.UPHOL,g.INTERIOR,.026)
    g.rod('First AC armrest pivot',(x-face*.26,y-.049,floor+.655),(x-face*.26,y+.049,floor+.655),.021,g.STEEL,g.INTERIOR,N=24)
    g.box('First AC armrest support',(x-face*.20,y,floor+.56),(.044,.045,.19),g.TRIM,g.INTERIOR,.01)
   # Three rails above the aisle edge create a proper upper-berth guard.
   for dz in [.05,.23]:g.rod('First AC upper guard rail',(x-.29,.435,3.01+dz),(x+.29,.435,3.01+dz),.014,g.DARK,g.INTERIOR,N=16)
   for dx in [-.29,0,.29]:g.rod('First AC upper guard upright',(x+dx,.435,3.05),(x+dx,.435,3.24),.012,g.DARK,g.INTERIOR,N=16)
  start=end

def headrest_cloth(g,name,c,size,mat,parent):
 """Thin antimacassar follows the seat curvature; no hovering foam rectangle."""
 x,y,z=c;back_x=x-.068;back_z=z-.275;NY=16;NZ=12;vs=[]
 for j in range(NZ+1):
  t=j/NZ
  for i in range(NY+1):
   q=i/NY*2-1;yy=y+q*size[1]/2;zz=z+(t-.5)*size[2]-.003*math.cos(q*math.pi)*(1-t)**4
   v=(zz-back_z)/.76+.5;u=(yy-y)/.205
   xx=back_x-.105*(v-.5)+.105/2+.025*(1-u*u)+.018*math.sin(math.pi*v)+.0028
   vs.append((xx,yy,zz))
 fs=[(j*(NY+1)+i,j*(NY+1)+i+1,(j+1)*(NY+1)+i+1,(j+1)*(NY+1)+i) for j in range(NZ) for i in range(NY)]
 ob=g.mesh(name+' draped linen',vs,fs,mat,parent)
 for p in ob.data.polygons:p.use_smooth=True
 mod=ob.modifiers.new('Linen thickness','SOLIDIFY');mod.thickness=.0011
 g.path('Headrest cloth stitched lower hem',vs[:NY+1],.001,mat,parent,6)
 return ob
