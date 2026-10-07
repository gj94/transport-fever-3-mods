"""Conventional screw couplings with side buffers. Illustrative static uncoupled pose."""
import math

def build(g):
 for s in [-1,1]:
  label='FRONT' if s>0 else 'REAR'
  anchor=g.empty('COUPLING_'+label,(s*11.1485,0,1.105),g.ROOT,0 if s>0 else math.pi)
  anchor['datum']='side-buffer contact plane, not an AAR CBC knuckle mating datum'
  anchor['hardware']='conventional screw coupling with side buffers'
  group=g.empty('SCREW_'+label+'_ASSEMBLY',(0,0,0),g.BODY)
  g.box('Headstock buffer beam',(s*10.530,0,1.088),(.192,2.99,.298),g.DARK,group,.014)
  g.box('Headstock steel upper flange',(s*10.525,0,1.248),(.236,2.99,.025),g.DARK,group,.004)
  for y in [-.978,.978]:
   g.box('Buffer housing square baseplate',(s*10.644,y,1.105),(.056,.372,.386),g.DARK,group,.012)
   g.rod('Buffer spring case',(s*10.65,y,1.105),(s*10.941,y,1.105),.143,g.DARK,group,N=48)
   g.rod('Buffer sliding ram',(s*10.85,y,1.105),(s*11.104,y,1.105),.089,g.STEEL,group,N=40)
   g.rod('Buffer dust collar',(s*10.911,y,1.105),(s*10.956,y,1.105),.155,g.DARK,group,N=48)
   g.rod('Buffer face forged dish',(s*11.0945,y,1.105),(s*11.1485,y,1.105),.213,g.DARK,group,N=64)
   # A gently dished machined centre is flush with, never beyond, the contact plane.
   g.rod('Buffer face contact wear',(s*11.1460,y,1.105),(s*11.1484,y,1.105),.159,g.STEEL,group,N=64)
   for dy in [-.141,.141]:
    for dz in [-.15,.15]:
     g.rod('Buffer mounting hex nut',(s*10.672,y+dy,1.105+dz),(s*10.696,y+dy,1.105+dz),.021,g.STEEL,group,N=6)
     g.rod('Buffer mounting stud',(s*10.688,y+dy,1.105+dz),(s*10.708,y+dy,1.105+dz),.009,g.DARK,group,N=12)
   g.rod('Buffer grease nipple',(s*10.855,y,1.248),(s*10.855,y,1.271),.009,g.BRASS,group,N=10)
  # Forged drawhook silhouette, modelled as a true concave outline rather than a block.
  outline=[(10.54,1.025),(10.86,1.025),(10.915,.992),(11.025,1.005),(11.104,1.09),(11.104,1.224),(11.058,1.268),(11.035,1.19),(11.047,1.125),(11.005,1.087),(10.945,1.103),(10.88,1.182),(10.54,1.182)]
  vs=[(s*x,y,z) for y in [-.049,.049] for x,z in outline];N=len(outline)
  ob=g.mesh('Forged central drawhook',vs,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)],g.STEEL,group,bevel=.008)
  g.box('Drawhook pocket opening',(s*10.665,0,1.11),(.05,.24,.24),g.RUBBER,group,.015)
  # Trunnion pin, twin forged links and oppositely threaded turnbuckle hang clear of track.
  g.rod('Drawhook trunnion pin',(s*10.88,-.125,1.060),(s*10.88,.125,1.060),.031,g.STEEL,group,N=28)
  for sy in [-1,1]:
   y=sy*.10
   for dx in [-.020,.020]:g.rod('Coupling shackle cheek',(s*(10.89+dx),y,1.055),(s*(10.952+dx),y,.82),.017,g.STEEL,group,N=14)
   g.rod('Coupling trunnion retaining nut',(s*10.88,sy*.13,1.060),(s*10.88,sy*.15,1.060),.039,g.DARK,group,N=6)
  g.rod('Screw coupling upper trunnion',(s*10.95,-.126,.820),(s*10.95,.126,.820),.032,g.STEEL,group,N=24)
  g.rod('Screw coupling turnbuckle barrel',(s*10.955,0,.84),(s*10.996,0,.555),.030,g.STEEL,group,N=32)
  for j in range(19):
   z=.584+j*.012
   # Visible helical thread on the lower spindle, with restrained depth.
   pts=[]
   for k in range(13):
    a=k*2*math.pi/12;pts.append((s*(10.992+.029*math.cos(a)),.029*math.sin(a),z+.012*k/12))
   g.path('Turnbuckle screw thread',pts,.0027,g.DARK,group,N=6)
  g.rod('Turnbuckle cross handle',(s*10.979,-.15,.714),(s*10.979,.15,.714),.011,g.STEEL,group,N=16)
  for y in [-.153,.153]:g.rod('Turnbuckle handle end stop',(s*10.979,y-.009,.714),(s*10.979,y+.009,.714),.018,g.DARK,group,N=16)
  # Oblong final coupling bow, free hanging; no claim of a tensioned paired pose.
  pts=[]
  for j in range(49):
   a=j*2*math.pi/48;pts.append((s*(10.997+.014*math.sin(a)),.090*math.cos(a),.473+.105*math.sin(a)))
  g.path('Screw coupling forged lower bow',pts,.018,g.STEEL,group,N=12)
  for y in [-.36,.36]:
   g.rod('Brake pipe end feed',(s*10.48,y,1.028),(s*10.71,y,1.028),.022,g.STEEL,group,N=16)
   g.rod('Brake pipe cock body',(s*10.70,y,1.028),(s*10.79,y,1.028),.041,g.BRASS,group,N=16)
   g.box('Brake isolation cock lever',(s*10.745,y+.044,1.082),(.14,.024,.019),g.RED,group,.004)
   g.path('Rubber pneumatic end hose',[(s*10.79,y,1.02),(s*10.88,y,.95),(s*10.90,y,.80),(s*10.88,y,.65),(s*10.80,y,.571)],.025,g.RUBBER,group,16)
   g.rod('Pneumatic hose gladhand',(s*10.80,y,.572),(s*10.754,y,.526),.043,g.STEEL,group,N=16)
   for z in [.80,.94]:g.rod('Hose moulded collar',(s*10.886,y,z-.02),(s*10.886,y,z+.02),.029,g.RUBBER,group,N=16)
  # Corner safety chains and equipment shelf remain inside the buffer face.
  for y in [-1.29,1.29]:g.path('Buffer beam corner handhold',[(s*10.65,y-.12,1.18),(s*10.73,y-.12,1.18),(s*10.73,y+.12,1.18),(s*10.65,y+.12,1.18)],.012,g.STEEL,group,N=12)
