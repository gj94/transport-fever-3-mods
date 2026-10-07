"""Small fabricated fittings and upholstered interior refinement."""
import math
import bpy
from mathutils import Vector

def tube(g,name,points,radius,material,parent=None,N=12):
 pts=[Vector(p) for p in points];vs=[];frames=[]
 for j,p in enumerate(pts):
  tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
  normal=tangent.cross(Vector((0,0,1)))
  if normal.length<.05:normal=tangent.cross(Vector((0,1,0)))
  normal.normalize();binormal=tangent.cross(normal).normalized()
  if frames and normal.dot(frames[-1])<0:normal=-normal;binormal=-binormal
  frames.append(normal)
  for k in range(N):
   a=k*2*math.pi/N;vs.append(tuple(p+radius*(normal*math.cos(a)+binormal*math.sin(a))))
 fs=[(j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k) for j in range(len(pts)-1) for k in range(N)]
 fs.extend([tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))])
 ob=g.mesh(name,vs,fs,material,parent or g.BODY)
 for p in ob.data.polygons[:-2]:p.use_smooth=True
 return ob

def circle(g,name,center,radius,material,parent=None,plane='XY',tube_radius=.004,N=48):
 pts=[]
 for k in range(N+1):
  a=k*2*math.pi/N;x=radius*math.cos(a);y=radius*math.sin(a)
  d={'XY':(x,y,0),'XZ':(x,0,y),'YZ':(0,x,y)}[plane]
  pts.append(tuple(center[i]+d[i] for i in range(3)))
 return tube(g,name,pts,tube_radius,material,parent,8)

def fan(g,x,y,z):
 parent=g.INTERIOR
 g.rod('Fan ceiling stem',(x,y,z+.25),(x,y,z+.085),.018,g.STEEL,parent,N=20)
 g.rod('Fan pressed ceiling flange',(x,y,z+.237),(x,y,z+.255),.065,g.TRIM,parent,N=32)
 g.rod('Fan round motor housing',(x,y,z-.007),(x,y,z+.112),.060,g.TRIM,parent,N=32)
 for dz,r in [(-.056,.063),(-.048,.112),(-.029,.166),(0,.205),(.052,.205),(.072,.16)]:circle(g,'Fan concentric safety grille',(x,y,z+dz),r,g.STEEL,parent,tube_radius=.0025)
 for j in range(24):
  a=j*2*math.pi/24
  tube(g,'Fan radial cage wire',[(x+.040*math.cos(a),y+.040*math.sin(a),z-.057),(x+.112*math.cos(a),y+.112*math.sin(a),z-.048),(x+.183*math.cos(a),y+.183*math.sin(a),z-.019),(x+.205*math.cos(a),y+.205*math.sin(a),z+.026),(x+.19*math.cos(a),y+.19*math.sin(a),z+.068),(x+.085*math.cos(a),y+.085*math.sin(a),z+.094)],.0025,g.STEEL,parent,6)
 for j in range(3):
  a=j*2*math.pi/3;xy=[(.032,-.02),(.085,-.054),(.181,-.040),(.190,.018),(.121,.059),(.059,.040)]
  vs=[(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a),z+.020+.045*v) for u,v in xy]
  ob=g.mesh('Fan swept three blade rotor',vs,[tuple(range(6))],g.DARK,parent);m=ob.modifiers.new('Blade plate thickness','SOLIDIFY');m.thickness=.004
 g.rod('Fan centre decorative cap',(x,y,z-.064),(x,y,z-.048),.038,g.TRIM,parent,N=32)
 for j in range(4):
  a=j*math.pi/2;g.box('Fan grille locking clip',(x+.205*math.cos(a),y+.205*math.sin(a),z+.026),(.019,.019,.014),g.DARK,parent,.004)

def upholstery(g,name,center,size):
 o=g.box(name,center,size,g.UPHOL,g.INTERIOR,.027)
 for m in o.modifiers:
  if m.type=='BEVEL':m.segments=4
 o.modifiers.new('Upholstery weighted corner normals','WEIGHTED_NORMAL')
 o['component']='seat_cushion';g.CUSHIONS.append(o)
 x,y,z=center;dx,dy,dz=[v/2 for v in size]
 # A restrained tailored welt on horizontal cushions and around upright backs.
 if size[2]<.20:
  rr=min(.032,size[0]/8,size[1]/8);points=[]
  for cx,cy,a in [(dx-rr,dy-rr,0),(-dx+rr,dy-rr,90),(-dx+rr,-dy+rr,180),(dx-rr,-dy+rr,270)]:
   for k in range(7):
    t=math.radians(a+k*15);points.append((x+cx+rr*math.cos(t),y+cy+rr*math.sin(t),z+dz-.016))
  points.append(points[0]);tube(g,name+'_stitched_edge_welt',points,.0027,g.SEAM,g.INTERIOR,6)
  if size[1]>1.1:
   for xx in [-.16,.16]:g.rod(name+'_subtle_cover_stitch',(x+xx,y-dy+.04,z+dz+.0005),(x+xx,y+dy-.04,z+dz+.0005),.0008,g.SEAM,g.INTERIOR,N=6)
 return o

def bottle_holder(g,x,y,z,parent=None):
 parent=parent or g.INTERIOR
 for dz in [0,.17]:circle(g,'Bottle holder rolled hoop',(x,y,z+dz),.059,g.STEEL,parent,tube_radius=.0035,N=24)
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:g.rod('Bottle holder wire upright',(x+.059*math.cos(a),y+.059*math.sin(a),z),(x+.059*math.cos(a),y+.059*math.sin(a),z+.17),.0035,g.STEEL,parent,N=8)
 for dx in [-.035,.035]:g.rod('Bottle basket bottom wire',(x+dx,y-.045,z),(x+dx,y+.045,z),.0035,g.STEEL,parent,N=8)
 g.box('Bottle holder wall mounting plate',(x,y-.07,z+.1),(.12,.015,.18),g.TRIM,parent,.012)

def finish(g):
 V=g.V;floor=g.FLOORZ
 # Lining panel joints, lower kick strips and compact seat control/bottle fittings.
 for s in [-1,1]:
  g.box('Interior stainless kick strip',(0,s*1.514,floor+.07),(15.99,.018,.14),g.STEEL,g.INTERIOR,.004)
  for x in [-7.6+i*.84 for i in range(19)]:
   g.box('Lining panel vertical joint',(x,s*1.551,3.108),(.006,.010,.40),g.TRIM,g.INTERIOR)
 if V in ['SL','3A','2A']:
  bays=9 if V=='SL' else 8;pitch=15.2/bays
  for b in range(bays):
   cx=-7.6+(b+.5)*pitch
   bottle_holder(g,cx-.28,-1.425,1.87)
   bottle_holder(g,cx+.28,-1.425,1.87)
   for face in [-1,1]:
    xx=cx+face*(pitch/2-.055)
    # Strong perforated divider crown and slender stainless upper safety guard.
    for y in [-1.29,-.92,-.55,-.18,.18]:
     g.rod('Upper berth guard mesh horizontal',(cx+face*(pitch/2-.67),y,3.08),(cx+face*(pitch/2-.67),y,3.26),.004,g.STEEL,g.INTERIOR,N=8)
    for z in [3.08,3.17,3.26]:g.rod('Upper berth safety rail',(cx+face*(pitch/2-.67),-1.34,z),(cx+face*(pitch/2-.67),.20,z),.009 if z!=3.17 else .004,g.STEEL,g.INTERIOR,N=12)
    if V!='2A':
     for y in [-1.28,.10]:
      g.rod('Middle berth folding hinge axle',(xx-face*.025,y-.07,1.82),(xx-face*.025,y+.07,1.82),.018,g.STEEL,g.INTERIOR,N=16)
      g.box('Middle berth retention latch',(xx-face*.055,y,2.388),(.022,.055,.068),g.STEEL,g.INTERIOR,.007)
      # Chain parks beside the folded berth and carries visible individual small links.
      for j in range(9):
       c=(xx-face*.054,y,2.51+j*.031)
       circle(g,'Parked berth support chain link',c,.015,g.STEEL,g.INTERIOR,plane='XZ' if j%2 else 'YZ',tube_radius=.003,N=16)
    g.box('Berth individual moulded control plate',(xx-face*.05,-1.19,2.64),(.018,.21,.105),g.TRIM,g.INTERIOR,.005)
    for y in [-1.24,-1.14]:g.box('Berth toggle switch',(xx-face*.064,y,2.64),(.010,.038,.039),g.DARK,g.INTERIOR,.003)
   # A wall-mounted coathook and mesh-paper pocket are deliberately small relative to the berth.
   g.path('Bay coat hook',[(cx,-1.515,2.94),(cx,-1.46,2.94),(cx,-1.43,2.98)],.008,g.STEEL,g.INTERIOR,10)
   g.box('Window table wall hinge',(cx,-1.476,1.957),(.27,.029,.022),g.STEEL,g.INTERIOR,.004)
 if V=='1A':
  for x in [-6,-3,-.5,1.5,3.5,6]:
   # Private compartment fittings: robe hooks, mirror frame, timber grain accent, reading controls.
   bottle_holder(g,x,-1.40,1.68)
   for dx in [-.16,.16]:g.path('First AC polished coat hook',[(x+dx,-1.52,2.81),(x+dx,-1.46,2.81),(x+dx,-1.44,2.86)],.008,g.BRASS,g.INTERIOR,12)
   g.box('First AC compartment call plate',(x,.544,2.09),(.085,.018,.11),g.TRIM,g.INTERIOR,.008)
   g.rod('Compartment call pushbutton',(x,.524,2.09),(x,.532,2.09),.018,g.RED,g.INTERIOR,N=20)
 if V in ['CC','2S','GS']:
  rows=15 if V=='CC' else 18;pitch=1 if V=='CC' else .84;start=-7 if V=='CC' else -7.14
  for row in range(rows):
   x=start+row*pitch;face=1 if V=='CC' or row%2==0 else -1
   ys=[-1.27,-.81,-.35,.50,1.05] if V=='CC' else [-1.28,-.84,-.40,.40,.84,1.28]
   if V=='CC' and row==14:ys=ys[:3]
   for i,y in enumerate(ys):
    if V=='CC':
     # Padded chair shape is supplemented with injection-moulded shell, recline button and footrest.
     g.box('Chair rear moulded shell',(x-.325,y,2.13),(.045,.425,.68),g.TRIM,g.INTERIOR,.03)
     for dy in [-.185,.185]:g.rod('Seat footrest suspended link',(x-.22,y+dy,floor+.35),(x-.37,y+dy,floor+.17),.010,g.STEEL,g.INTERIOR,N=12)
     g.rod('Seat fluted footrest bar',(x-.37,y-.18,floor+.17),(x-.37,y+.18,floor+.17),.023,g.DARK,g.INTERIOR,N=16)
     for dy in [-.14,-.07,0,.07,.14]:g.rod('Footrest grip ring',(x-.37,y+dy-.009,floor+.17),(x-.37,y+dy+.009,floor+.17),.026,g.RUBBER,g.INTERIOR,N=16)
     g.box('Chair tray pivot',(x-.351,y,2.22),(.022,.27,.027),g.STEEL,g.INTERIOR,.005)
     # Seat-back mesh pocket below the tray.
     for dy in [-.14,-.07,0,.07,.14]:g.rod('Chair seatback pocket vertical mesh',(x-.361,y+dy,1.90),(x-.361,y+dy,2.07),.0025,g.DARK,g.INTERIOR,N=6)
     for z in [1.90,1.95,2.00,2.05]:g.rod('Chair seatback pocket horizontal mesh',(x-.361,y-.16,z),(x-.361,y+.16,z),.0025,g.DARK,g.INTERIOR,N=6)
    # Raised enamel seat number tabs, facing the central aisle.
   if row%2==0:
    for s in [-1,1]:
     g.box('Second seating rack seat-number tab',(x,s*.956,3.055),(.17,.018,.085),g.TRIM,g.INTERIOR,.005)
 for end in [-1,1]:
  # Practical vestibule finish and extinguisher, with cage, handle and hose.
  x=end*8.51;y=-1.27
  g.rod('Vestibule fire extinguisher steel bottle',(x,y,1.64),(x,y,2.04),.079,g.RED,g.INTERIOR,N=32)
  g.rod('Extinguisher valve neck',(x,y,2.04),(x,y,2.112),.025,g.BRASS,g.INTERIOR,N=16)
  g.box('Extinguisher squeeze handle',(x,y,2.123),(.12,.036,.024),g.DARK,g.INTERIOR,.006)
  g.path('Extinguisher black hose',[(x+.04,y,2.09),(x+.11,y,2.04),(x+.12,y,1.80)],.010,g.RUBBER,g.INTERIOR,12)
  for z in [1.71,1.94]:circle(g,'Extinguisher mounting strap',(x,y,z),.083,g.DARK,g.INTERIOR,tube_radius=.006)
  g.box('Extinguisher instruction label',(x,y-.080,1.855),(.082,.009,.17),g.WHITE,g.INTERIOR,.007)
  for z in [1.81,1.83,1.85,1.87,1.89]:g.box('Extinguisher fine print line',(x,y-.086,z),(.06,.001,.005),g.DARK,g.INTERIOR)
  for sy in [-1,1]:
   # Toilet fittings are improved as actual shallow bowl meshes, not dark rectangles.
   xx=end*10.23;yy=sy*1.01;z=floor+.50
   rings=[(.22,.21,z),(.18,.17,z+.012),(.13,.12,z-.055),(.065,.055,z-.125)];vs=[];N=48
   for rx,ry,zz in rings:
    for j in range(N):a=j*2*math.pi/N;vs.append((xx+rx*math.cos(a),yy+ry*math.sin(a),zz))
   ob=g.mesh('Ceramic toilet bowl curved hollow rim',vs,[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(len(rings)-1) for j in range(N)],g.WHITE,g.INTERIOR)
   for p in ob.data.polygons:p.use_smooth=True
   circle(g,'Toilet stainless tissue holder axle',(end*9.725,yy,2.04),.045,g.STEEL,g.INTERIOR,plane='YZ',tube_radius=.006)
   g.rod('Toilet tissue roll',(end*9.74,yy-.07,2.04),(end*9.74,yy+.07,2.04),.055,g.WHITE,g.INTERIOR,N=24)
   g.path('Toilet wash spray flexible hose',[(end*10.45,yy-.27,1.85),(end*10.35,yy-.27,1.60),(end*10.30,yy-.27,1.45),(end*10.20,yy-.27,1.51)],.009,g.STEEL,g.INTERIOR,12)
   g.box('Toilet stainless floor drain',(end*9.82,yy,floor+.057),(.18,.18,.008),g.STEEL,g.INTERIOR,.006)
   for dx in [-.06,-.03,0,.03,.06]:g.box('Toilet drain perforation',(end*9.82+dx,yy,floor+.062),(.008,.13,.002),g.DARK,g.INTERIOR,.002)
