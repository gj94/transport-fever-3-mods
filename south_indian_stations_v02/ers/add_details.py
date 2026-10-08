# Representative researched-style details, not claimed room-by-room survey.
collection('16 | CLOSE RANGE • ticketing equipment notices and safety')
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.30
glass.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.12
def notice(name,title,lines,x,y,z,w=1.5,h=1.9):
 cube(name+' frame',(x,y,z),(w+.07,.055,h+.07),blue)
 cube(name+' paper',(x,y-.035,z),(w,.015,h),cream)
 text(name+' heading',title,(x,y-.05,z+h*.35),w*.095,red)
 for j,line in enumerate(lines):text(name+' notice text',line,(x,y-.054,z+h*.19-j*h*.105),w*.064,black)
def extinguisher(x,y,z=.4):
 cyl('Fire extinguisher cylinder',(x,y,z+.52),.115,.70,red,16)
 cyl('Extinguisher shoulder',(x,y,z+.9),.08,.08,red,16)
 cube('Extinguisher valve lever',(x,y,z+1.01),(.20,.055,.055),black)
 cube('Extinguisher inspection label',(x,y-.117,z+.58),(.13,.015,.26),cream)
 tube('Extinguisher black hose',[(x+.1,y,z+.96),(x+.2,y,z+.9),(x+.21,y,z+.35)],.018,black)
 cube('Fire extinguisher wall sign',(x,y+.15,z+1.6),(.38,.055,.43),red)
 text('Fire extinguisher sign','FIRE',(x,y+.112,z+1.53),.12,cream)
def clockface(x,y,z,r=.40):
 o=cyl('Analog clock casing',(x,y,z),r,.12,black,40);o.rotation_euler[0]=math.pi/2
 o=cyl('Analog clock dial',(x,y-.075,z),r*.92,.02,cream,40);o.rotation_euler[0]=math.pi/2
 for j in range(12):
  a=j*math.tau/12;beam('Clock tick',(x+math.sin(a)*r*.77,y-.09,z+math.cos(a)*r*.77),(x+math.sin(a)*r*.86,y-.09,z+math.cos(a)*r*.86),.014,black)
 beam('Clock minute hand',(x,y-.105,z),(x+r*.65,y-.105,z+.1),.018,black);beam('Clock hour hand',(x,y-.105,z),(x-.09,y-.105,z+r*.42),.025,black)
def printer(x,y,z):
 cube('Ticket printer body',(x,y,z),(.37,.34,.23),cream,.018)
 cube('Ticket printer slot',(x,y-.176,z+.02),(.25,.018,.028),black)
 cube('Printed ticket emerging',(x,y-.23,z+.02),(.17,.16,.007),white)
 cube('Printer status panel',(x+.12,y-.182,z+.075),(.035,.012,.035),green)
# Physical secure grilles, ticket speech ports and equipment behind transactions.
for i in range(5):
 x=-12.3+i*3.1
 for dx in [-.27,-.18,-.09,0,.09,.18,.27]:cube('Ticket grille vertical bars',(x+dx,4.73,2.45),(.018,.035,.70),steel)
 for z in [2.13,2.4,2.72]:cube('Ticket grille horizontal bars',(x,4.72,z),(.65,.035,.018),steel)
 cyl('Counter intercom base',(x+.7,4.45,1.76),.08,.04,black,12)
 tube('Counter intercom microphone',[(x+.7,4.45,1.77),(x+.7,4.45,1.98),(x+.64,4.40,2.04)],.015,black)
 printer(x+.60,6.0,1.23)
 cube('Ticket stamp pad',(x-.6,4.49,1.71),(.24,.18,.035),blue)
 cube('Counter acrylic instruction plate',(x-1.0,4.42,1.94),(.35,.035,.42),cream)
 text('Counter instruction','QUEUE',(x-1,4.39,1.99),.085,blue)
 text('Counter instruction lower','HERE',(x-1,4.39,1.85),.085,blue)
 # privacy side partition behind each counter
 cube('Clerk desk partition',(x+1.40,5.70,1.65),(.045,1.7,1.3),cream)
 for z in [1.03,1.18,1.33]:cube('Ticket form tray',(x-.5,6.3,z),(.35,.26,.045),steel)
wall_door('Clerks secure rear wall',-5,7.4,20,5.5,1.4,z=.4)
notice('Fare enquiry notice','FARES / ENQUIRY',['ERNAKULAM JUNCTION','Ask at the enquiry counter','Keep your ticket ready','Check platform display','Enquiry: 139'],3.5,4.48,2.5,1.35,1.8)
notice('Rail passenger notice','PASSENGER INFORMATION',['Use the footbridge','Do not cross the tracks','Keep platforms clean','Drinking water on platforms','Emergency assistance:139'],-14.65,2.0,2.1,1.8,2.1)
notice('Waiting hall route notice','DESTINATIONS',['SHORANUR / THRISSUR','KOTTAYAM / KOLLAM','ALAPPUZHA / KAYAMKULAM','Check departure displays','Platform changes announced'],-29,6.46,2.2,2.2,2.25)
clockface(-19,6.3,2.85,.43)
for x,y in [(-15,-3),(4,4.4),(-17,5.9),(34,6),(42,-4.6),(24,103)]:extinguisher(x,y)
# Modern-in-era vending / enquiry enclosure, detailed controls instead of blank box.
for x in [-13.4,2.8]:
 cube('Ticket vending cabinet',(x,-.7,1.32),(.85,.72,1.85),blue,.035)
 cube('Vending touchscreen bezel',(x,-1.08,1.66),(.66,.04,.57),black)
 cube('Vending touchscreen',(x,-1.108,1.66),(.57,.01,.46),roofblue)
 text('Vending touchscreen legend','TICKETS',(x,-1.12,1.74),.095,cream)
 cube('Vending ticket output',(x,-1.09,.91),(.36,.045,.10),black)
 for i in range(4):cube('Vending buttons',(x-.20+i*.13,-1.10,1.24),(.08,.02,.08),cream)
# Visible ceiling luminaires, conduits, speakers, camera mounts and junction boxes.
for x,y,z in [(-12,-2,5.6),(-5,-2,5.6),(2,-2,5.6),(-28,2,3.42),(-21,2,3.42),(10,1,3.34),(30,1,3.34)]:
 cube('Fluorescent fixture enamel body',(x,y,z),(1.35,.22,.07),white)
 for dy in [-.055,.055]:beam('Fluorescent lamp tube',(x-.60,y+dy,z-.06),(x+.60,y+dy,z-.06),.035,cream)
 for dx in [-.62,.62]:cube('Lamp end connector',(x+dx,y,z-.035),(.06,.20,.075),steel)
 tube('Electrical surface conduit',[(x,y,z+.03),(x,y+2,z+.03),(x+2,y+2,z+.03)],.02,white)
for x,y,z in [(-14,4,3.4),(4,4,3.4),(-31,5,3),(30,6,3)]:
 cube('Electrical junction box',(x,y,z),(.22,.1,.30),cream)
 for dz in [-.07,.07]:cube('Switch face',(x,y-.06,z+dz),(.075,.025,.09),white)
 cube('Public-address loudspeaker',(x,y-.25,z+.35),(.40,.30,.22),black)
 beam('CCTV mounting arm',(x,y,z+.6),(x,y-.45,z+.6),.04,steel)
 cube('CCTV camera housing',(x,y-.50,z+.6),(.15,.26,.13),white)
 cube('CCTV black lens face',(x,y-.64,z+.6),(.12,.015,.095),black)
# Arrival enquiry writing ledge and form rack.
cube('Passenger writing ledge',(-8,-3.8,1.39),(4.5,.55,.10),wood)
for x in [-10,-6]:cube('Writing ledge steel bracket',(x,-3.72,.92),(.10,.33,.9),steel)
for x in [-9.5,-8,-6.5]:
 cube('Reservation blank form',(x,-3.78,1.45),(.45,.32,.006),cream)
 beam('Chained writing pen',(x,-3.9,1.47),(x+.15,-3.7,1.47),.012,black)
# Notice boards and concrete-floor wear at operational platform viewpoints.
collection('17 | PLATFORM DETAIL • safety notices lights and surface wear')
for x,y in [(18,48),(260,48),(30,68),(-105,98),(45,19)]:
 for xx in [x-.95,x+.95]:beam('Notice board support',(xx,y,1.16),(xx,y,3.45),.07,steel)
 notice('Platform passenger notice','PASSENGER NOTICE',['USE FOOTBRIDGE','DO NOT CROSS TRACKS','KEEP THE STATION CLEAN','Enquiry and assistance:139'],x,y,2.7,1.9,1.45)
 clockface(x+3,y,3.75,.38)
 extinguisher(x-2,y,1.18)
 cube('Platform digital display',(x+8,y,4.05),(3,.20,.60),black)
 text('Platform digital display text','ERNAKULAM JN',(x+8,y-.115,3.95),.23,yellow)
for x,y in [(6,48),(250,48),(15,68),(245,68),(-96,98),(75,19)]:
 notice('Kiosk menu','REFRESHMENTS',['TEA / COFFEE','BOTTLED WATER','PACKAGED SNACKS','PLEASE USE THE BIN'],x+1.45,y-1.62,3.05,.55,.88)
 cube('Kiosk serving kettle',(x-.8,y-1.1,2.83),(.30,.25,.38),steel,.04)
 for j in range(5):cyl('Stacked paper cups',(x-.15+j*.15,y-1.15,2.65),.055,.20,cream,10)
 printer(x+.7,y-.8,2.67)
# Fastened bench frames and foot pads augment individual seats.
for o in list(bpy.data.objects):
 if o.name.startswith('Seat steel legs'):
  x,y,z=o.location;cube('Bench bolted soleplate',(x,y,z-.235),(.18,.60,.025),steel)
  for dx in [-.055,.055]:
   for dy in [-.22,.22]:cyl('Bench anchor bolt',(x+dx,y+dy,z-.21),.014,.028,black,6)
# Discrete stains/patch repairs: separate low thin irregular polygons, not photo projection.
weather=mat('Dark damp concrete edge staining',(.20,.225,.205),noise=31)
for label,y,lo,hi,width in platform_specs:
 for x in range(lo+5,hi-5,9):
  yy=y+random.choice([-1,1])*(width*.34);r=random.uniform(.15,.55)
  v=[(x+r*math.cos(j*math.tau/7)*random.uniform(.65,1.2),yy+r*.5*math.sin(j*math.tau/7),1.168) for j in range(7)]
  mesh('Platform irregular weather patch',v,[tuple(range(7))],weather)
# Real angular gravel chips cover the formerly flat ballast top with varied tones.
collection('18 | BALLAST SURFACE • explicit angular stone geometry')
for wid,pts,t in paths:
 vv=[];ff=[];mi=[];dist=0
 for a,b in zip(pts,pts[1:]):
  va=Vector(a);v=Vector(b)-va;l=v.length
  if l<.01:continue
  d=v/l;per=Vector((-d.y,d.x))
  for k in range(math.ceil(dist/.6),math.floor((dist+l)/.6)+1):
   c=va+d*(k*.6-dist)
   for side in [-1,1,-1,1,-1,1]:
    q=c+d*random.uniform(-.28,.28)+per*random.uniform(1.1,1.80)*side;r=random.uniform(.025,.06);n=len(vv);z=.31
    vv.extend([(q.x-r,q.y-r*.6,z),(q.x+r,q.y-r*.4,z),(q.x+r*.5,q.y+r,z),(q.x-r*.7,q.y+r*.5,z),(q.x,q.y,z+r)])
    ff.extend([(n,n+1,n+4),(n+1,n+2,n+4),(n+2,n+3,n+4),(n+3,n,n+4)])
  dist+=l
 mesh('Angular ballast shoulder stones '+wid,vv,ff,ballast)
collection('19 | EAST HALL AND SANITARY FINISHING')
for j,o in enumerate(sorted([o for o in scene.objects if o.name.startswith('Toilet cubicle door')],key=lambda x:x.name)):
 if j%2==0:o.rotation_euler[2]=-.9;o.location.y+=.45
for x in [6,14,23]:
 before=set(scene.objects)
 notice('East passenger notice','PASSENGER INFORMATION',['UNRESERVED TICKETS','WAITING HALL','PLATFORM 6 / FOOTBRIDGE','Enquiry and assistance139'],x,102.19,2.8,2.0,1.7)
 rot=Matrix.Translation(Vector((x,102.19,0)))@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(Vector((-x,-102.19,0)))
 for o in set(scene.objects)-before:
  o.location.x=2*x-o.location.x;o.location.y=2*102.19-o.location.y;o.rotation_euler[2]+=math.pi
for x in [-24,-12,0,12,24]:
 cube('East hall ceiling lamp',(x,111,4.95),(1.5,.24,.09),cream)
 tube('East hall electrical conduit',[(x,102.3,4.6),(x,111,4.6)],.02,white)
for x in [-23,-17,-11]:printer(x+.7,107,2.03)
# Thin tile courses on washroom walls and floor, towel/soap dispensers at basins.
for x in range(40,59):cube('Washroom floor tile joint',(x,1,.433),(.009,11.8,.006),white)
for y in range(-4,8):cube('Washroom transverse tile joint',(49,y,.433),(17.8,.009,.006),white)
for x in [43,46,49,52,55]:
 cube('Wall soap dispenser',(x+.58,-4.79,1.6),(.18,.16,.32),cream,.025)
 cube('Soap dispenser push button',(x+.58,-4.88,1.48),(.10,.04,.07),black)
 cube('Basin plumbing trap',(x,-3,.90),(.07,.07,.60),steel)
for x in [41.5,46.7,51.9]:
 cube('Cubicle paper dispenser',(x-1.05,4.5,1.25),(.15,.28,.28),steel)
 for z in [.8,1.4,2.0]:cube('Sanitary rear wall tile grout',(x,6.89,z),(2.3,.012,.009),white)

# Idempotent frog-nose orientation QA: the nose points away from its nearest toe.
for event_id,e in enumerate(json.loads((P/'physical_pointwork.json').read_text())['crossings']):
 ob=bpy.data.objects.get('Derived manganese frog nose '+str(event_id))
 if ob is None:continue
 p=Vector((e['x'],e['y']));toes=[Vector(k) for k,v in nodes.items() if len(v)==3 and (Vector(k)-p).length<100]
 if not toes:continue
 toe=min(toes,key=lambda q:(q-p).length);center=sum((v.co.xy for v in ob.data.vertices),Vector((0,0)))/len(ob.data.vertices)
 if (center-p).dot(p-toe)<0:
  for v in ob.data.vertices:v.co.x=2*p.x-v.co.x;v.co.y=2*p.y-v.co.y
