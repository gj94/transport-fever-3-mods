"""Nagercoil detailed full-size station. Metres. Original geometry; source-backed and reconstructed parts labelled."""
import bpy, math, json, random, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
exec(compile((ROOT/'scripts/facade_heritage.py').read_text(),str(ROOT/'scripts/facade_heritage.py'),'exec'))
random.seed(74)
# Faster direct meshes: architectural baseline alone retains bevel modifiers.
oldcube=cube
cube=lambda n,p,s,m,bev=0:oldcube(n,p,s,m,0)
for n in ['10_HALL_INTERIOR_RECONSTRUCTED','11_WAITING_AND_OFFICES_RECONSTRUCTED','12_TOILETS_AND_SERVICE_RECONSTRUCTED','13_UPPER_FLOOR_RECONSTRUCTED','20_PLATFORMS_MAP_DERIVED','21_PLATFORM_FURNITURE','22_FOOTBRIDGE_RECONSTRUCTED','30_RAILS_OSM_1676mm','31_TURNOUT_COMPONENTS_RECONSTRUCTED','32_SLEEPERS_FASTENERS','33_BALLAST_DRAINAGE','34_OHE_SIGNALS_RECONSTRUCTED','35_DEPOT_PITS_AND_GOODS','40_SURROUNDINGS','90_REVIEW_CAMERAS']:
 cols[n]=collection(n)
for o in list(bpy.data.objects):
 if o.name.split('.')[0] in ['Rear wall','Lower wing building','Annex block','Ground slab','Annex ground doorway']:bpy.data.objects.remove(o,do_unlink=True)
# Fully resolved physically modelled station palette.
tile=mat('Speckled warm terrazzo',(.58,.55,.44),noise=.19);tile2=mat('Darker replacement terrazzo',(.44,.45,.39),noise=.25);grout=mat('Grouted joints',(.20,.21,.19));cream=mat('Interior washable cream',(.79,.75,.60),noise=.08);skirt=mat('Maroon enamel skirting',(.29,.07,.045),.4);ceramic=mat('Glazed sanitary ceramic',(.87,.89,.85),.23);steel=mat('Polished stainless fixtures',(.51,.55,.54),.25,.85);wood=mat('Worn hardwood slats',(.24,.12,.055),noise=.32);bluepaint=mat('Railway blue painted steel',(.025,.17,.33),.52,.25,noise=.16);warning=mat('Safety yellow',(.92,.64,.025),.61);trackrust=mat('Rusty rail sides',(.22,.095,.045),.53,.68,noise=.28);railhead=mat('Polished running rail',(.34,.39,.41),.28,.9);ballast=mat('Angular granite ballast',(.26,.28,.27),noise=.5);sleepermat=mat('Prestressed concrete sleeper',(.46,.46,.41),noise=.25);moss=mat('Drain algae',(.15,.19,.07),noise=.4);water=mat('Water basin',(.08,.22,.24),.15,.5)
def emissive(n,col,power):
 m=mat(n,col,.35);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=power;return m
lampmat=emissive('Warm fluorescent diffuser',(.9,.87,.66),3);redlight=emissive('Red signal lens',(.75,.009,.002),2)
# Bulk immutable batches keep the editable scene tractable.
batches={}
def boxb(n,p,s,m,ang=0):
 key=(active.name,n,m.name);v,f=batches.setdefault(key,([],[]));k=len(v);c,si=math.cos(ang),math.sin(ang)
 for xx,yy,zz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
  x,y=xx*s[0]/2,yy*s[1]/2;v.append((p[0]+x*c-y*si,p[1]+x*si+y*c,p[2]+zz*s[2]/2))
 f.extend(tuple(k+j for j in a) for a in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
def flush():
 global active
 for (cn,n,mn),(v,f) in batches.items():active=bpy.data.collections[cn];mesh(n,v,f,bpy.data.materials[mn])
 batches.clear()
def polycurve(n,pts,r,m):
 d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=0;s=d.splines.new('POLY');s.points.add(len(pts)-1)
 for p,q in zip(s.points,pts):p.co=(*q,1)
 o=bpy.data.objects.new(n,d);active.objects.link(o);d.materials.append(m);return o
def area(n,p,power,size=5):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=p;return o
def plaque(n,body,p,w=2.5,h=.5):
 cube(n+' sign',p,(w,.08,h),bluepaint);text(n,body,(p[0],p[1]-.055,p[2]),h*.35,ivory,width=w-.15)
def bench(x,y,z=.7):
 for xx in [x-1,x+1]:
  for yy in [y-.24,y+.24]:boxb('Bench cast legs',(xx,yy,z+.21),(.07,.07,.42),metal)
 for j in range(4):boxb('Bench seat hardwood',(x,y-.24+j*.16,z+.46),(2.4,.13,.065),wood)
 for j in range(3):boxb('Bench back slats',(x,y+.30,z+.69+j*.15),(2.4,.05,.12),wood)
 for xx in [x-1.1,x+1.1]:beam('Bench armrest',(xx,y-.3,z+.71),(xx,y+.32,z+.71),.025,metal)
def fan(x,y,z):
 beam('Ceiling fan drop',(x,y,z+.4),(x,y,z),.016,ivory);cyl('Fan motor',(x,y,z),.13,.12,ivory)
 for a in [0,2.094,4.188]:o=cube('Fan paddle',(x+.33*math.cos(a),y+.33*math.sin(a),z-.07),(.63,.14,.015),ivory);o.rotation_euler.z=a

def room_shell(n,x0,x1,y0,y1,z=.68,height=3.35,doorx=None):
 cube(n+' floor',((x0+x1)/2,(y0+y1)/2,z-.08),(x1-x0,y1-y0,.16),tile)
 for x in [x0,x1]:cube(n+' sidewall',(x,(y0+y1)/2,z+height/2),(.22,y1-y0,height),cream)
 cube(n+' back wall',((x0+x1)/2,y1,z+height/2),(x1-x0,.22,height),cream)
 dx=doorx if doorx is not None else (x0+x1)/2
 for a,b in [(x0,dx-.65),(dx+.65,x1)]:
  if b>a:cube(n+' doorway flank',((a+b)/2,y0,z+height/2),(b-a,.22,height),cream)
 cube(n+' door lintel',(dx,y0,z+2.85),(1.3,.22,1),cream)
 plaque(n,n,(dx,y0-.16,z+2.6),min(3,x1-x0-.3),.38)
 for x in [x0+.13,x1-.13]:cube(n+' skirting',(x,(y0+y1)/2,z+.10),(.035,y1-y0,.2),skirt)
 return dx

print('NCJ_INTERIORS',flush=True)
group('10_HALL_INTERIOR_RECONSTRUCTED')
# Rear openings connect directly from hall to platform; no sealed facade shell.
for a,b in [(-18,-7),(-4,4),(7,18)]:
 if (a,b)==(-4,4):continue
 cube('Rear masonry portal side',((a+b)/2,10,2.35),(b-a,.25,3.4),cream)
cube('Rear portal header',(0,10,3.9),(36,.25,.45),cream)
for x in [-6,6]:cube('Rear portal jamb',(x,10,2.25),(.22,.3,3.15),ivory)
# Raised landings, 150 mm steps and edge bands onto higher platform.
for i in range(4):cube('Hall platform step',(0,10.4+i*.28,.75+i*.14),(7,1.2-i*.23,.16),tile)
for x in range(-17,18):
 for y in range(1,10):boxb('Hall individually jointed floor tile',(x,y,.69),(.985,.985,.035),tile if (x+y)%7 else tile2)
# Public counters face hall, offices behind. Counter portals remain open.
for side in [-1,1]:
 x=side*12
 cube('Booking office lower wall',(x,7.05,1.2),(9,.18,1.0),cream);cube('Booking office upper lintel',(x,7.05,3.55),(9,.18,1.15),cream)
 for j in range(3):
  xx=x+(j-1)*2.7
  cube('Granite ticket counter',(xx,6.85,1.52),(2.4,.65,.10),grey)
  for q in range(9):boxb('Counter security grill',(xx-1+q*.25,7,2.19),(.025,.025,1.24),metal)
  for z in [1.8,2.5,2.8]:boxb('Counter grille rail',(xx,7,z),(2.1,.028,.022),metal)
  cube('Ticket pass opening lower shelf',(xx,6.78,1.68),(.5,.3,.045),steel)
  plaque('Booking counter',f'{j+1 if side<0 else j+4}   TICKETS',(xx,6.9,3.08),2.2,.4)
  cube('Booking computer monitor',(xx,8,1.85),(.53,.16,.37),black);cube('Booking keyboard',(xx,7.8,1.6),(.45,.18,.04),black)
  cube('Clerk desk',(xx,8.2,1.49),(2.1,.75,.09),wood)
  for dx in [-.8,.8]:boxb('Desk steel legs',(xx+dx,8.3,1.1),(.04,.04,.75),metal)
  cube('Clerk chair seat',(xx,8.8,1.16),(.42,.42,.09),bluepaint);cube('Clerk chair back',(xx,9,1.48),(.43,.05,.5),bluepaint)
  for yy in [2.6,4,5.4]:
   for dx in [-.65,.65]:beam('Queue rail post',(xx+dx,yy,.72),(xx+dx,yy,1.6),.027,steel)
  for dx in [-.65,.65]:beam('Queue rail',(xx+dx,2.6,1.6),(xx+dx,5.4,1.6),.028,steel)
for x in [-9,0,9]:
 fan(x,4.5,3.55);cube('Ceiling tube fitting',(x,2.6,3.92),(1.3,.25,.12),ivory);cube('Fluorescent tube diffuser',(x,2.6,3.85),(1.2,.16,.025),lampmat);area('Hall ceiling light',(x,4.4,3.92),420,4)
plaque('Wayfinding','PLATFORMS 1 / 1A / 2 / 3   →',(0,9.7,3.12),6,.55)
# Timetable case and clock with hands.
cube('Timetable glass case',(-5.9,6.2,2.2),(.14,2.2,1.3),wood)
for j in range(15):boxb('Timetable rows',(-5.81,5.3+j*.12,2.2),(.015,.006,1.03),black)
cyl('Hall wall clock',(0,9.76,3.72),.30,.04,ivory,32,(math.pi/2,0,0))
beam('Clock minute hand',(0,9.70,3.72),(0,9.70,3.95),.009,black);beam('Clock hour hand',(0,9.70,3.72),(.16,9.70,3.69),.013,black)
for x in [-4,4]:
 cyl('Waste bin',(x,8.8,.99),.22,.60,bluepaint);cyl('Bin lid',(x,8.8,1.3),.245,.05,metal)
# Wing: habitable waiting room with washbasin and luggage racks.
group('11_WAITING_AND_OFFICES_RECONSTRUCTED')
room_shell('WAITING HALL',-35.8,-18.2,-.7,9.1,doorx=-25)
for x in [-32,-28,-23]:
 for y in [2,5.5]:bench(x,y)
for x in [-32,-25]:fan(x,4.5,3.45);area('Waiting ceiling light',(x,4.5,3.8),360,4)
for y in [2,5.5,7.8]:
 cube('Luggage rack shelf',(-35.4,y,2.1),(.65,2,.08),steel)
 for yy in [y-.8,y+.8]:beam('Luggage rack support',(-35.6,yy,.8),(-35.6,yy,2.8),.025,steel)
plaque('Waiting room notice','PLEASE KEEP THE STATION CLEAN',(-27,8.93,2.65),5,.45)
# Offices behind annex with real doors and external corridor.
for i,(name,x0,x1) in enumerate([('STATION MANAGER',-56.3,-48.5),('PARCEL OFFICE',-48.5,-39)]):
 room_shell(name,x0,x1,3.1,12.3,doorx=(x0+x1)/2)
 cube(name+' desk',((x0+x1)/2,8.7,1.49),(2.3,1,.10),wood)
 for xx in [x0+.8,x1-.8]:cube('Office metal cabinet',(xx,11.75,1.8),(.75,.55,2.15),grey)
 for z in [1.3,1.8,2.3]:cube('Cupboard handle',((x0+x1)/2,11.43,z),(.15,.04,.025),steel)
 bench((x0+x1)/2,5)
 cube('Office map frame',((x0+x1)/2,12.15,2.4),(3,.07,1.3),wood);cube('Office map paper',((x0+x1)/2,12.10,2.4),(2.85,.01,1.15),ivory)
 for j in range(6):boxb('Schematic operating board lines',((x0+x1)/2,12.08,1.98+j*.15),(2.55,.012,.01),bluepaint)
 area('Office light',((x0+x1)/2,7.5,3.8),160,4)
# Toilet block with open cubicle doors, drains, plumbing, wash points.
group('12_TOILETS_AND_SERVICE_RECONSTRUCTED')
room_shell('TOILETS',-77,-59,1,12.3,doorx=-68)
for side in [-1,1]:
 for j in range(3):
  x=-68+side*(2.1+j*2.3);y=9.8
  for dx in [-1.03,1.03]:cube('WC cubicle partition',(x+dx,y,1.86),(.08,3.6,2.35),ceramic)
  cube('WC cistern',(x,11.45,1.5),(.53,.18,.63),ceramic);cyl('WC pedestal',(x,10.95,.98),.2,.4,ceramic)
  o=cyl('Toilet bowl rim',(x,10.8,1.22),.32,.10,ceramic,24);o.scale.y=1.25
  o=cyl('Toilet bowl opening',(x,10.8,1.28),.225,.01,black,24);o.scale.y=1.2
  o=cube('Open cubicle door',(x+.6,8,1.79),(.82,.06,2.1),bluepaint);o.rotation_euler.z=.7
  cube('WC flush button',(x,11.32,1.78),(.1,.02,.07),steel)
for x in [-75,-72,-64,-61]:
 cube('Washbasin wall support',(x,4.5,1.35),(.7,.52,.12),ceramic);cyl('Washbasin well',(x,4.4,1.42),.21,.02,water)
 beam('Basin tap riser',(x,4.66,1.4),(x,4.66,1.65),.018,steel);beam('Basin tap spout',(x,4.66,1.65),(x,4.46,1.65),.019,steel)
 cube('Mirror',(x,4.84,2.07),(.66,.02,.8),glass);polycurve('Waste pipe',[(x,4.5,1.3),(x,4.5,.83),(x,4.83,.83)],.033,ivory)
for x in range(-76,-59):
 for y in range(2,12):boxb('Bathroom square ceramic tile',(x,y,.705),(.98,.98,.035),ceramic if (x+y)%2 else tile2)
for x in [-74,-62]:area('Washroom light',(x,6,3.8),360,4)
# Utility/service room east of station, electrical cabinets and pump pipes.
room_shell('ELECTRICAL / STAFF',22,34,1,10,doorx=27)
for x in [24,27,30,32]:
 cube('Electrical distribution cabinet',(x,9.5,1.65),(1.25,.6,1.9),grey)
 for z in [1.2,1.6,2.0]:cube('Cabinet meter',(x,9.17,z),(.27,.02,.18),black)
 text('Electrical caution','DANGER  415 V',(x,9.15,2.35),.105,warning,width=1.1)
for x in [24,30]:fan(x,5,3.45)
area('Electrical room light',(27,5,3.8),160,5)
# Habitable roofs are separate editable slabs.
for p,sz in [((-27,4.2,4.05),(18,10,.18)),((-47.5,7.7,4.1),(18,9.5,.18)),((-68,6.65,4.15),(18.4,11.7,.2)),((28,5.5,4.15),(12.4,9.4,.2))]:cube('Interior roof ceiling slab',p,sz,cream)
# First floor: corridor, staff rooms, beds and station office; navigable internal stairs.
group('13_UPPER_FLOOR_RECONSTRUCTED')
for x0,x1,name in [(-17,-7,'STAFF REST'),(-7,4,'OPERATIONS'),(4,12,'RECORDS')]:
 room_shell(name,x0,x1,4.0,9.7,z=4.35,height=4.6)
 for x in [x0+1.4,x1-1.4]:
  cube('Staff bed frame',(x,7.4,4.8),(1,2.1,.35),wood);cube('Staff mattress',(x,7.4,5.03),(.96,2.02,.16),ivory);cube('Pillow',(x,8.1,5.16),(.65,.4,.12),cream)
 area('Upper room light',((x0+x1)/2,6.3,8.4),160,4)
for i in range(22):
 z=.7+(i+1)*.165;y=1+i*.30;cube('Internal stair tread',(15.4,y,z-.09),(2.25,.32,.18),tile)
beam('Stair handrail',(14.25,.8,1.6),(14.25,7.4,5.25),.029,steel)
# Cut stairwell from pre-existing mezzanine by replace with three slabs.
for o in list(bpy.data.objects):
 if o.name.startswith('Interior mezzanine floor'):bpy.data.objects.remove(o,do_unlink=True)
for p,s in [((-1.8,5.3,4.2),(31.6,9.1,.24)),((15.3,9,4.2),(4.5,1.7,.24))]:cube('Upper floor around real stairwell',p,s,grey)
# Rich service fixtures, individually grouted waiting room floor and legible notices.
group('11_WAITING_AND_OFFICES_RECONSTRUCTED')
for x in range(-35,-18):
 for y in range(0,9):boxb('Waiting room jointed terrazzo',(x+.5,y+.5,.72),(.985,.985,.025),tile if (x+y)%5 else tile2)
for x,y in [(-34,8.9),(-21,8.9),(-52,12.1),(-43,12.1)]:
 cube('Passenger information frame',(x,y,2.2),(2.1,.10,1.15),wood);cube('Notice paper backing',(x,y-.061,2.2),(1.97,.02,1.02),ivory)
 for j,body in enumerate(['SOUTHERN RAILWAY','PASSENGER INFORMATION','Keep your luggage with you','Use the foot overbridge','No smoking on station premises']):text('Passenger information text',body,(x,y-.08,2.58-j*.17),.09 if j else .12,black,width=1.85)
for x,y in [(-34,1),(-20,7.8),(-54,4.5),(-41,4.5),(-76,2),(-60,2)]:
 cube('Surface electrical switch plate',(x,y,1.65),(.15,.04,.23),ceramic)
 for j in range(3):cube('Switch rocker',(x-.04+j*.04,y-.027,1.69),(.027,.01,.045),ivory)
 polycurve('Surface conduit',[(x,y,1.78),(x,y,3.65),(x+1,y,3.65)],.012,grey)
for x in [-32,-25]:
 cube('Waiting fluorescent fitting',(x,4.5,3.90),(1.45,.22,.10),ivory);cube('Waiting fluorescent diffuser',(x,4.5,3.84),(1.35,.15,.025),lampmat)
for x in [-33,-20]:
 cyl('Waiting room waste bin',(x,7.8,1.05),.23,.64,bluepaint);cyl('Waiting fire extinguisher',(x,8.83,1.65),.12,.68,red)
plaque('Waiting exit','EXIT  →',(-25,-.86,3.30),1.7,.32)
# Upper wing and annex are enclosed occupied volumes, not floating facade windows.
group('13_UPPER_FLOOR_RECONSTRUCTED')
for x0,x1,y0,y1,z,h,title in [(-35.8,-18.2,-.7,9.1,4.2,3.12,'STAFF LOUNGE'),(-56.3,-39,3.1,12.3,4.22,2.55,'ADMINISTRATION')]:
 room_shell(title,x0,x1,y0,y1,z=z,height=h)
 cube('Upper wing roof',((x0+x1)/2,(y0+y1)/2,z+h+.08),(x1-x0+.3,y1-y0+.3,.16),grey)
 for x in [x0+2,x1-2]:
  cube('Upper staff table',(x,(y0+y1)/2,z+.77),(2,1,.12),wood);cube('Upper office cabinet',(x,y1-.4,z+1.0),(1.1,.55,1.95),grey)
 area('Upper wing light',((x0+x1)/2,(y0+y1)/2,z+h-.12),180,5)
# Open upper circulation portals and a small link walkway between inherited wings.
def open_side_portal(name,x,ya,yb,z0,z1,door_y):
 for o in list(bpy.data.objects):
  if o.name.startswith(name) and abs(o.location.x-x)<.04:bpy.data.objects.remove(o,do_unlink=True)
 for lo,hi in [(ya,door_y-.75),(door_y+.75,yb)]:
  if hi>lo:cube('Upper passage side masonry',(x,(lo+hi)/2,(z0+z1)/2),(.22,hi-lo,z1-z0),cream)
 cube('Upper passage door lintel',(x,door_y,(z0+2.35+z1)/2),(.22,1.5,z1-z0-2.35),cream)
open_side_portal('STAFF LOUNGE sidewall',-18.2,-.7,9.1,4.2,7.32,2)
open_side_portal('STAFF LOUNGE sidewall',-35.8,-.7,9.1,4.2,7.32,6)
open_side_portal('ADMINISTRATION sidewall',-39,3.1,12.3,4.22,6.77,6)
for o in list(bpy.data.objects):
 if o.name.startswith('End wall') and o.location.x<0:bpy.data.objects.remove(o,do_unlink=True)
cube('Main sidewall below upper portal',(-17.9,5,2.37),(.42,10,3.74),peach)
for ya,yb in [(0,1.25),(2.75,10)]:cube('Main sidewall upper portal jamb',(-17.9,(ya+yb)/2,6.8),(.42,yb-ya,4.85),peach)
cube('Main sidewall upper portal lintel',(-17.9,2,7.95),(.42,1.5,2.6),peach)
cube('Upper annex link walk',(-37.4,6,4.16),(3.4,1.8,.16),grey)
for yy in [5.1,6.9]:beam('Upper link handrail',(-39.1,yy,5.25),(-35.7,yy,5.25),.025,metal)
print('NCJ_MAP_RAILWAY',flush=True)
raw=json.loads((ROOT/'references/local_geometry.json').read_text())
# Coordinate transform preserves source metre dimensions and site orientation.
def local(p):return Vector((p[0]+45,p[1],0))
paths=[];platforms=[]
for w in raw:
 pts=[local(p) for p in w['local']]
 if w['tags'].get('railway')=='platform':platforms.append((w['id'],pts));continue
 if w['tags'].get('railway')!='rail':continue
 # Keep full yard and a generous approach envelope, not the entire adjoining towns.
 runs=[];run=[]
 for a,b in zip(pts,pts[1:]):
  N=max(1,int((b-a).length/5))
  for j in range(N):
   p=a.lerp(b,j/N)
   if -1220<p.x<1150 and -180<p.y<610:run.append(p)
   elif run:
    if len(run)>1:runs.append(run)
    run=[]
 if run:
  if -1220<pts[-1].x<1150 and -180<pts[-1].y<610:run.append(pts[-1])
  if len(run)>1:runs.append(run)
 for q in runs:paths.append({'id':w['id'],'pts':q,'tags':w['tags'],'basis':'OSM mapped centreline, 2021–2025 edits'})
# Disconnected mapped pit/siding pairs need approach connections; preserve their surveyed-like
# parallel runs, add clearly tagged reconstructed ladder only where endpoint graph is absent.
def distance_seg(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/max(1e-8,v.dot(v))));q=a+t*v;return (p-q).length,q
original_count=len(paths);inferred=[]
for pi in range(original_count):
 w=paths[pi]
 if w['tags'].get('service') not in ['yard','siding','spur']:continue
 # Is either endpoint actually joined to another mapped centreline?
 connections=[]
 for end in [w['pts'][0],w['pts'][-1]]:
  best=(1e9,None,None)
  for j,v in enumerate(paths[:original_count]):
   if j==pi:continue
   for a,b in zip(v['pts'],v['pts'][1:]):
    dd,q=distance_seg(end,a,b)
    if dd<best[0]:best=(dd,q,j)
  connections.append(best)
 if min(c[0] for c in connections)<.2:continue
 # Source shows an isolated pit road. Connect its south end to an adjacent mapped road
 # over an eased 1:12-or-gentler transition, rather than leave floating rails.
 ei=0 if w['pts'][0].x>w['pts'][-1].x else 1;p=w['pts'][0 if ei==0 else -1];candidate=None
 for j,v in enumerate(paths[:original_count]):
  if j==pi:continue
  for a,b in zip(v['pts'],v['pts'][1:]):
   if max(a.x,b.x)<p.x+45 or min(a.x,b.x)>p.x+160:continue
   dd,q=distance_seg(p+Vector((90,0,0)),a,b)
   if 0<q.x-p.x<170 and abs(q.y-p.y)<30 and (candidate is None or dd<candidate[0]):candidate=(dd,q)
 if candidate:
  q=candidate[1];pp=[]
  for j in range(61):
   t=j/60;s=t*t*(3-2*t);pp.append(Vector((p.x+(q.x-p.x)*t,p.y+(q.y-p.y)*s,0)))
  paths.append({'id':'reconstructed_link_'+w['id'],'pts':pp,'tags':{'service':'yard'},'basis':'Inferred connection because mapped pit road is disconnected'});inferred.append(w['id'])
# Source platform meshes are extruded full footprint, not shortened modules.
group('20_PLATFORMS_MAP_DERIVED')
for ident,pts in platforms:
 if (pts[-1]-pts[0]).length<.1:pts=pts[:-1]
 N=len(pts);v=[(p.x,p.y,z) for z in [.05,1.26] for p in pts];f=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];mesh('Mapped platform '+ident,v,f,grey)
 # Full-length top and edge strip follows polygon segments exactly.
 mesh('Terrazzo platform surface '+ident,[(p.x,p.y,1.265) for p in pts],[tuple(range(N))],tile)
 for a,b in zip(pts,pts[1:]+pts[:1]):
  if (b-a).length<20:continue
  polycurve('Platform yellow safety edge',[(a.x,a.y,1.282),(b.x,b.y,1.282)],.065,warning)
  length=(b-a).length
  for j in range(int(length/1.5)):
   p=a.lerp(b,(j+.5)*1.5/length);boxb('Edge weathered fascia coping',(p.x,p.y,1.13),(1.46,.12,.24),ivory if j%5 else tile2,math.atan2(b.y-a.y,b.x-a.x))
# Tile grid clipped at all four corners to the actual mapped platform polygons.
def inside_poly(x,y,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
for ident,pts in platforms:
 poly=pts[:-1] if (pts[-1]-pts[0]).length<.1 else pts
 for x in range(math.floor(min(p.x for p in poly)),math.ceil(max(p.x for p in poly))):
  for y in range(math.floor(min(p.y for p in poly)),math.ceil(max(p.y for p in poly))):
   if all(inside_poly(x+.5+dx,y+.5+dy,poly) for dx in [-.495,.495] for dy in [-.495,.495]):
    boxb('Platform paving jointed tiles',(x+.5,y+.5,1.285),(.99,.99,.028),tile if random.random()>.10 else tile2)
def pfmid(ix,x):
 ps=platforms[ix][1];ys=[]
 for a,b in zip(ps,ps[1:]):
  if min(a.x,b.x)<=x<max(a.x,b.x):ys.append(a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y))
 return (min(ys)+max(ys))/2 if ys else (16 if ix==0 else 36)
# Railway paths: actual gauge head inner-face separation 1.676 m.
group('30_RAILS_OSM_1676mm')
rail_segments=[];track_lengths={};ends=[]
for w in paths:
 pts=w['pts'];length=sum((b-a).length for a,b in zip(pts,pts[1:]));track_lengths[w['id']]=length
 for side in [-1,1]:
  rp=[]
  for i,p in enumerate(pts):
   t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();normal=Vector((-t.y,t.x,0));rp.append(p+normal*side*.8705)
  for i,(a,b) in enumerate(zip(rp,rp[1:])):rail_segments.append((w['id'],side,a,b,[]))
# Physical frog flangeway gaps at rail-head intersections. Spatial bucket search.
def intersect(a,b,c,d):
 u=b-a;v=d-c;det=u.x*v.y-u.y*v.x
 if abs(det)<1e-8:return None
 z=c-a;t=(z.x*v.y-z.y*v.x)/det;s=(z.x*u.y-z.y*u.x)/det
 return (t,s) if .0001<t<.9999 and .0001<s<.9999 else None
buckets={};frogpoints=[]
for i,(wid,side,a,b,gaps) in enumerate(rail_segments):
 xmin,xmax=math.floor(min(a.x,b.x)/8),math.floor(max(a.x,b.x)/8);ymin,ymax=math.floor(min(a.y,b.y)/8),math.floor(max(a.y,b.y)/8);candidates=set()
 for xx in range(xmin,xmax+1):
  for yy in range(ymin,ymax+1):candidates.update(buckets.get((xx,yy),[]))
 for j in candidates:
  wj,sj,c,d,gj=rail_segments[j]
  if wid==wj:continue
  hit=intersect(a,b,c,d)
  if hit:
   t,s=hit;gaps.append(t);gj.append(s);p=a.lerp(b,t)
   if all((p-q).length>2 for q in frogpoints):frogpoints.append(p)
 for xx in range(xmin,xmax+1):
  for yy in range(ymin,ymax+1):buckets.setdefault((xx,yy),[]).append(i)
for wid,side,a,b,gaps in rail_segments:
 vec=b-a;L=vec.length
 if L<1e-5:continue
 ranges=[(0,1)]
 for t in gaps:
  a0,b0=max(0,t-.08/L),min(1,t+.08/L);ranges=[z for lo,hi in ranges for z in [(lo,min(hi,a0)),(max(lo,b0),hi)] if z[1]-z[0]>1e-5]
 angle=math.atan2(vec.y,vec.x)
 for lo,hi in ranges:
  p=a.lerp(b,(lo+hi)/2);l=L*(hi-lo)
  for z,width,height,m in [(.365,.15,.025,trackrust),(.422,.016,.10,trackrust),(.480,.065,.04,railhead)]:boxb('Rail '+wid,(p.x,p.y,z),(l,width,height),m,angle)
# Sleepers and fastenings at true 0.60 m pitch, plus slab/ballast per route.
group('32_SLEEPERS_FASTENERS')
for w in paths:
 pts=w['pts'];carry=0
 for a,b in zip(pts,pts[1:]):
  d=b-a;L=d.length
  if L<.001:continue
  t=d/L;normal=Vector((-t.y,t.x,0));angle=math.atan2(d.y,d.x)
  while carry<L:
   p=a+t*carry;
   if w['id'] in ['514385386','514385387','514385388','1302623382','1302623383']:
    for ss in [-1,1]:
     qq=p+normal*ss*.96;boxb('Pit line discrete rail supports '+w['id'],(qq.x,qq.y,.285),(.25,.8,.15),sleepermat,angle)
   else:boxb('Concrete sleepers '+w['id'],(p.x,p.y,.285),(.25,2.75,.15),sleepermat,angle)
   for side in [-1,1]:
    q=p+normal*side*.8705;boxb('Rail seat pads',(q.x,q.y,.37),(.22,.22,.026),black,angle)
    for off in [-.09,.09]:
     qq=q+normal*off;boxb('Elastic rail clips',(qq.x,qq.y,.398),(.105,.045,.037),trackrust,angle)
   carry+=.6
  carry-=L
 group('33_BALLAST_DRAINAGE')
 # Batched rectangular ballast segments preserve full mapped curvature.
 for a,b in zip(pts,pts[1:]):
  d=b-a;p=(a+b)/2;boxb('Granite ballast formation',(p.x,p.y,.08),(d.length+0.1,3.35,.24),ballast,math.atan2(d.y,d.x))
 group('32_SLEEPERS_FASTENERS')
# Individual angular ballast stones at close-view scale, seeded along the full network.
group('33_BALLAST_DRAINAGE')
rockv=[];rockf=[]
for w in paths:
 for a,b in zip(w['pts'],w['pts'][1:]):
  L=(b-a).length;t=(b-a).normalized();n=Vector((-t.y,t.x,0))
  for j in range(max(1,int(L*.6))):
   p=a.lerp(b,random.random())+n*random.choice([-1,1])*random.uniform(1.15,1.65);r=random.uniform(.025,.075);k=len(rockv)
   rockv.extend([(p.x-r,p.y-r,.20),(p.x+r,p.y-r,.205),(p.x+r,p.y+r,.21),(p.x-r,p.y+r,.205),(p.x+r*.3,p.y-r*.2,.20+r)])
   rockf.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
mesh('Individual angular granite aggregate',rockv,rockf,ballast)
# Turnout anatomy at crossings: guard rails, switch motors, linkage rods, extended bearers.
group('31_TURNOUT_COMPONENTS_RECONSTRUCTED')
for k,p in enumerate(frogpoints):
 # Align with nearest route tangent.
 best=min([(distance_seg(p,a,b)[0],a,b) for w in paths for a,b in zip(w['pts'],w['pts'][1:])],key=lambda z:z[0]);t=(best[2]-best[1]).normalized();n=Vector((-t.y,t.x,0));ang=math.atan2(t.y,t.x)
 for side in [-1,1]:
  q=p+n*side*.64
  boxb('Turnout check rail',(q.x,q.y,.474),(3.4,.048,.05),trackrust,ang)
  for j in range(7):
   q=p+t*(j*.6-1.8);boxb('Long crossing bearers',(q.x,q.y,.27),(.27,3.65,.17),sleepermat,ang)
 q=p+n*2.1-t*6;boxb('Point machine enclosure',(q.x,q.y,.49),(.8,.45,.3),grey,ang)
 polycurve('Point drive rod',[(q.x,q.y,.38),(q.x-n.x*1.8,q.y-n.y*1.8,.38)],.025,steel)
 # Thin tapered blade strips converge toward stock rail over twelve metres.
 for side in [-1,1]:
  seq=[]
  for j in range(13):
   q=p-t*(18-j)+n*(side*(.8705-.30*j/12));seq.append((q.x,q.y,.485))
  polycurve('Tapering switch blade',seq,.018,railhead)
 cube('Point identification board',(p.x+1,p.y+2.9,.85),(.45,.1,.32),ivory);text('Points number',str(101+k),(p.x+1,p.y+2.84,.85),.17,black,width=.4)
# Detect true free line ends and add buffer stops, except cropped main approaches.
group('35_DEPOT_PITS_AND_GOODS')
buffer_positions=[]
for w in paths:
 if w['tags'].get('service') not in ['yard','siding','spur']:continue
 for ix in [0,-1]:
  p=w['pts'][ix];near=False
  for v in paths:
   if v is w:continue
   if any(distance_seg(p,a,b)[0]<.18 for a,b in zip(v['pts'],v['pts'][1:])):near=True;break
  if near or abs(p.x)>1100 or p.y>580:continue
  t=(w['pts'][1]-p).normalized() if ix==0 else (w['pts'][-2]-p).normalized();n=Vector((-t.y,t.x,0));buffer_positions.append([p.x,p.y])
  for s in [-1,1]:
   q=p+n*s*.87;beam('Buffer A-frame brace',(q.x+t.x*1.5,q.y+t.y*1.5,.45),(q.x,q.y,1.35),.09,trackrust)
  o=cube('Red white buffer beam',(p.x,p.y,1.35),(2.45,.25,.34),ivory);o.rotation_euler.z=math.atan2(t.y,t.x)+math.pi/2
  for s in [-1,1]:q=p+n*s*.5;cyl('Buffer stop discs',(q.x,q.y,1.35),.16,.11,red,16,(math.pi/2,0,0))
# Five full-length inspection pit facilities aligned to mapped yard runs; no rolling stock.
for wid in ['514385386','514385387','514385388','1302623382','1302623383']:
 ws=[w for w in paths if w['id']==wid]
 if not ws:continue
 pts=ws[0]['pts'];a,b=pts[0],pts[-1];t=(b-a).normalized();n=Vector((-t.y,t.x,0));L=min((b-a).length-35,550);c=(a+b)/2;ang=math.atan2(t.y,t.x)
 boxb('Inspection pit dark invert',(c.x,c.y,.21),(L,1.1,.12),dark,ang)
 for s in [-1,1]:
  q=c+n*s*.66;boxb('Pit reinforced concrete retaining wall',(q.x,q.y,.26),(L,.18,.42),grey,ang)
  q=c+n*s*1.75;boxb('Maintenance side walkway',(q.x,q.y,.40),(L,.65,.20),grey,ang)
  for j in range(int(L/12)):
   q=c+t*(j*12-L/2)+n*s*1.8
   beam('Depot water riser',(q.x,q.y,.35),(q.x,q.y,1.0),.025,bluepaint)
   polycurve('Depot watering hose',[(q.x,q.y,1),(q.x+.25,q.y,1.05),(q.x+.45,q.y,.4),(q.x+.65,q.y,.32)],.025,black)
# Drain/cable trough continuous station lengths and access chambers.
group('33_BALLAST_DRAINAGE')
for yy in [7,24.7,45.5,114]:
 for x in range(-670,500,4):
  boxb('Cable trough concrete lids',(x,yy,.16),(3.95,.40,.12),grey)
  if x%40==10:cube('Cable inspection chamber',(x,yy,.23),(1.2,.85,.12),metal)
for yy in [9,117]:
 cube('Open longitudinal drain invert',(-85,yy,-.02),(1180,.65,.08),moss)
 for dy in [-.4,.4]:cube('Drain side wall',(-85,yy+dy,.08),(1180,.15,.32),grey)
 for x in range(-670,500,15):
  for j in range(6):boxb('Drain crossing grate',(x+j*.09,yy,.28),(.035,.8,.035),metal)
print('NCJ_PLATFORM_DETAILS',flush=True)
group('21_PLATFORM_FURNITURE')
# Two shelters, with actual corrugated meshes, trusses, purlins and gutters.
def shelter(x0,x1,y,w,slope=.013):
 for x in range(int(x0),int(x1)+1,8):
  for yy in [y+x*slope-w*.32,y+x*slope+w*.32]:
   cube('Shelter steel stanchion',(x,yy,3.0),(.16,.18,3.48),bluepaint);cube('Shelter concrete base',(x,yy,1.55),(.42,.45,.57),grey)
  beam('Roof transverse tie',(x,y+x*slope-w/2,4.86),(x,y+x*slope+w/2,4.86),.045,bluepaint)
  for s in [-1,1]:
   beam('Roof sloped top chord',(x,y+x*slope,5.6),(x,y+x*slope+s*w/2,4.87),.048,bluepaint)
   beam('Roof diagonal web',(x,y+x*slope,4.85),(x,y+x*slope+s*w*.25,5.23),.026,bluepaint)
  cube('Shelter light fitting',(x,y,4.61),(1.4,.22,.12),ivory);cube('Shelter tube lamp',(x,y,4.54),(1.3,.13,.025),lampmat)
  if x%24==0:fan(x,y,4.25)
 for off in [-w*.48,-w*.24,0,w*.24,w*.48]:
  h=5.6-abs(off)/w*1.46;beam('Roof longitudinal purlin',(x0,y+x0*slope+off,h-.12),(x1,y+x1*slope+off,h-.12),.06,metal)
 verts=[];faces=[];n=int((x1-x0)/.16)
 for i in range(n+1):
  x=x0+i*(x1-x0)/n;zoff=.035 if i%2 else -.035
  verts.extend([(x,y+x*slope-w/2,4.9+zoff),(x,y+x*slope,5.62+zoff),(x,y+x*slope+w/2,4.9+zoff)])
 for i in range(n):
  for j in range(2):faces.append((i*3+j,i*3+j+1,(i+1)*3+j+1,(i+1)*3+j))
 mesh('Corrugated zinc canopy sheets',verts,faces,roof)
 for yy in [y-w/2,y+w/2]:
  polycurve('Shelter gutter',[(x0,yy+x0*slope,4.87),(x1,yy+x1*slope,4.87)],.07,grey)
  for x in range(int(x0)+8,int(x1),24):polycurve('Downpipe',[(x,yy+x*slope,4.87),(x,yy+x*slope,1.3)],.045,grey)
shelter(-205,70,17.2,6.5);shelter(-242,116,36.6,7.7)
# Repeating canopies stop before points; open full-length platform ends remain.
for pfidx in [0,1]:
 for x in range(-360,155,24):bench(x,pfmid(pfidx,x),1.27)
 for x in range(-350,150,60):
  y=pfmid(pfidx,x)
  for dx,m in [(-.45,bluepaint),(.45,teal)]:
   cyl('Platform segregation bin',(x+dx,y+1,1.7),.26,.78,m);cyl('Bin rim',(x+dx,y+1,2.1),.275,.06,metal)
  cube('Bin bilingual category label',(x-.45,y+.73,1.75),(.35,.03,.21),ivory)
 for x in [-340,-125,110]:
  y=pfmid(pfidx,x)
  for dx in [-2.3,2.3]:cube('Station nameboard leg',(x+dx,y,2.45),(.14,.16,2.4),black)
  cube('Yellow station board',(x,y,3.28),(5.2,.13,1.5),warning)
  text('Station English name','NAGERCOIL JUNCTION',(x,y-.083,2.91),.29,black,width=4.9)
  # Re-use correctly shaped Tamil and Hindi lettering rather than unshaped fonts.
  outlined_sign('Platform Tamil','tamil_outlined.svg',(x,y-.085,3.78),4.8,black)
  outlined_sign('Platform Hindi','hindi_outlined.svg',(x,y-.088,3.35),4.7,black)
 for x in [-270,-80,64]:
  y=pfmid(pfidx,x)
  cube('Drinking water tiled back',(x,y+1.65,2.0),(3.0,.25,1.45),ceramic);cube('Water trough',(x,y+1.28,1.59),(3.0,.75,.20),grey)
  for dx in [-1,-.5,0,.5,1]:
   polycurve('Individual chrome drinking tap',[(x+dx,y+1.48,2),(x+dx,y+1.21,2),(x+dx,y+1.21,1.94)],.018,steel)
   cyl('Tap cross handle',(x+dx,y+1.40,2.05),.06,.025,steel,12,(math.pi/2,0,0))
  plaque('Drinking water','DRINKING WATER',(x,y+1.46,2.71),2.8,.35)
  for dx in [-1.2,-.6,0,.6,1.2]:boxb('Water trough drainage slots',(x+dx,y+1.24,1.702),(.025,.45,.01),black)
 for x in range(-370,160,45):
  y=pfmid(pfidx,x)
  cyl('Platform lamp post',(x,y,4.5),.055,6.5,grey);beam('Twin light crossarm',(x,y-1,7.65),(x,y+1,7.65),.035,grey)
  for yy in [y-1,y+1]:cube('Lamp head',(x,yy,7.67),(.55,.29,.12),ivory)
# Signs, PA speakers, clock, fire extinguishers, benches and snack kiosk.
for y,label in [(17.6,'1'),(34.4,'2 / 3')]:
 for x in [-160,-60,40]:
  plaque('Platform number','PLATFORM '+label,(x,y,4.1),2.7,.55)
  cube('PA loudspeaker',(x+2,y,4.05),(.25,.35,.35),ivory)
  for k in range(6):boxb('Speaker grille',(x+2,y-.18,3.91+k*.055),(.2,.02,.018),metal)
plaque('Bay platform','1A  TERMINAL BAY',(-530,16,2.9),4,.6)
for x in [-112,45]:
 cube('Snack kiosk counter',(x,14.2,1.83),(5,2,1.15),bluepaint);cube('Kiosk worktop',(x,13.14,2.45),(5.2,.3,.10),steel)
 cube('Kiosk canopy',(x,14.2,3.8),(5.5,2.6,.15),roof);plaque('Refreshment stall','TEA  •  COFFEE  •  REFRESHMENTS',(x,12.91,3.45),5,.55)
 for dx in [-2.3,2.3]:cube('Kiosk post',(x+dx,13.3,3.15),(.08,.08,1.3),steel)
 for j in range(12):cyl('Tea glasses',(x-1.8+j*.3,13.15,2.57),.055,.14,ceramic,12)
 cyl('Tea urn',(x+1.6,14,2.87),.30,.73,steel,20);cyl('Tea urn lid',(x+1.6,14,3.25),.32,.05,steel)
# Luggage trolley, pallet stacks and fire equipment, all no rolling stock.
for x in [-44,-32]:
 cube('Parcel trolley frame',(x,16.1,1.64),(2.6,1.3,.15),bluepaint)
 for dx in [-1,1]:
  for yy in [15.5,16.7]:cyl('Trolley wheel',(x+dx,yy,1.45),.18,.07,black,16,(math.pi/2,0,0))
 beam('Trolley handle',(x-1.3,15.6,1.7),(x-1.3,15.6,2.5),.025,bluepaint);beam('Trolley handle',(x-1.3,16.6,1.7),(x-1.3,16.6,2.5),.025,bluepaint);beam('Trolley crossgrip',(x-1.3,15.6,2.5),(x-1.3,16.6,2.5),.025,bluepaint)
for x in [-22,22]:
 cyl('Fire extinguisher',(x,11,2.0),.115,.65,red);beam('Extinguisher nozzle',(x,11,2.37),(x+.18,11,2.15),.018,black)
# Footbridge at one mapped station central span; exact siting reconstructed.
group('22_FOOTBRIDGE_RECONSTRUCTED')
fx=-90
cube('Footbridge deck',(fx,24.7,7.7),(3.2,33,.28),grey)
for xx in [fx-1.6,fx+1.6]:
 openings=[(14.2,16.8),(33.2,35.8)] if xx>fx else []
 def clear(y):return not any(lo-.1<y<hi+.1 for lo,hi in openings)
 for yy in range(9,42,3):
  if clear(yy):beam('Footbridge truss upright',(xx,yy,7.8),(xx,yy,10.0),.055,bluepaint)
  if clear(yy) and clear(min(yy+3,41)) and not any(yy<lo<yy+3 for lo,hi in openings):beam('Footbridge truss diagonal',(xx,yy,7.8),(xx,min(yy+3,41),10.0),.04,bluepaint)
 for z in [7.85,8.8,10]:
  spans=[(8.3,41.2)] if z==10 or not openings else [(8.3,14.2),(16.8,33.2),(35.8,41.2)]
  for ya,yb in spans:beam('Footbridge truss chord with stair opening',(xx,ya,z),(xx,yb,z),.055,bluepaint)
 for yy in range(9,42):
  if clear(yy):beam('Bridge infill railing',(xx,yy,7.9),(xx,yy,8.95),.018,metal)
cube('Covered footbridge roof',(fx,24.7,10.25),(3.7,34,.14),roof)
for yy in [15.5,34.5]:
 for xx in [fx-1.1,fx+1.1]:cube('Footbridge support column',(xx,yy,4.38),(.32,.32,6.4),grey)
 # Straight flights run along platform, with midlanding and physical treads.
 for i in range(38):
  xx=fx+3.3+i*.30;z=1.26+(38-i)*.168;cube('Footbridge stair tread',(xx,yy,z-.07),(.31,2.2,.14),grey)
 for sy in [-1.1,1.1]:
  beam('Stair upper handrail',(fx+3.1,yy+sy,8.6),(fx+14.7,yy+sy,2.3),.035,bluepaint)
  for i in range(0,38,3):
   xx=fx+3.3+i*.30;z=1.26+(38-i)*.168;beam('Stair baluster',(xx,yy+sy,z),(xx,yy+sy,z+1.0),.02,bluepaint)
 cube('Stair top landing',(fx+2.35,yy,7.65),(1.8,2.3,.2),grey)
# OHE portal geometry and contact/messenger wires along every electrified station road.
group('34_OHE_SIGNALS_RECONSTRUCTED')
for x in range(-720,661,54):
 maxy=112 if -620<x<270 else 75
 for yy in [-4,maxy]:
  cube('OHE portal mast footing',(x,yy,.3),(.85,.9,.6),grey)
  for dx in [-.15,.15]:cube('OHE lattice mast chord',(x+dx,yy,4.55),(.065,.12,8.6),metal)
  for z in range(1,9):
   beam('OHE lattice bracing',(x-.15,yy,z),(x+.15,yy,z+.8),.024,metal)
 for z in [8.65,9.0]:beam('OHE portal girder',(x,-4,z),(x,maxy,z),.055,metal)
 for yy in range(-3,maxy,3):beam('Portal girder diagonal',(x,yy,8.65),(x,yy+3,9.0),.025,metal)
# Every path carries geometrically continuous contact and catenary; supports repeated at 54m.
for w in paths:
 pts=w['pts'];contact=[(p.x,p.y,6.15) for p in pts];polycurve('Contact wire '+w['id'],contact,.009,trackrust)
 messenger=[];travel=0
 for i,p in enumerate(pts):
  if i:travel+=(p-pts[i-1]).length
  sag=.3*(1-math.cos(2*math.pi*(travel%54)/54))/2;messenger.append((p.x,p.y,7.0-sag))
  if i%5==0:polycurve('OHE dropper',[(p.x,p.y,6.15),(p.x,p.y,7.0-sag)],.006,metal)
 polycurve('Messenger cable '+w['id'],messenger,.010,trackrust)
 # Cantilever equipment at route points every ~54m.
 dist=0
 for a,b in zip(pts,pts[1:]):
  dist+=(b-a).length
  if dist<54:continue
  dist=0
  beam('OHE registration arm',(b.x,b.y-1.4,7.0),(b.x,b.y,6.18),.03,metal)
  for j in range(7):cyl('Ceramic OHE insulator',(b.x,b.y-.9,7+j*.065),.07,.035,ivory,10)
# Signals at platform ends, stop boards and trackside equipment cabinets.
for x in [-400,190,350,-700]:
 for yy in [25,43,51,60]:
  cube('Signal concrete footing',(x,yy+1.9,.27),(.65,.65,.55),grey);cyl('Signal post',(x,yy+1.9,2.25),.075,4.0,metal)
  cube('Signal hood back',(x,yy+1.9,4.35),(.35,.19,1.3),black)
  for z in [3.95,4.35,4.75]:
   cyl('Signal lens',(x,yy+1.78,z),.12,.04,redlight if z==4.75 else glass,16,(math.pi/2,0,0));cube('Signal rain visor',(x,yy+1.65,z+.15),(.30,.37,.04),black)
  for zz in range(1,8):boxb('Signal ladder rung',(x+.3,yy+1.91,.5+zz*.48),(.3,.04,.035),metal)
  beam('Signal ladder stile',(x+.45,yy+1.91,.6),(x+.45,yy+1.91,4.3),.022,metal)
  cube('Signal relay location cabinet',(x+3,yy+2.3,.75),(.8,.55,1.3),grey)
# Depot workshop, goods shed, loading apron, tanks and service circulation.
group('35_DEPOT_PITS_AND_GOODS')
room_shell('COACH MAINTENANCE',-350,-280,119,138,z=.35,height=5,doorx=-314)
cube('Depot workshop roof',(-315,128.5,5.55),(73,22,.2),roof)
for x in range(-345,-281,6):
 cube('Workshop bench',(x,135,1.3),(3.3,1,.15),metal)
 for yy in [123,126,129]:cube('Workshop tool rack',(x,yy,1.5),(1.8,.45,2.3),bluepaint)
 for j in range(4):cyl('Tool oil drum',(x+j*.65,136,.76),.28,.84,trackrust)
room_shell('GOODS SHED',-570,-455,-20,-4,z=.4,height=4.5,doorx=-510)
cube('Goods shed corrugated roof',(-512.5,-12,5.0),(118,18,.18),roof)
for x in range(-562,-457,5):
 for j in range(3):cube('Stacked parcel crate',(x,-9+j*1.3,.9),(2.2,1.1,1),wood)
cube('Goods loading apron',(-512,-.8,.52),(120,5,.8),grey)
for x,y in [(-246,124),(-230,125)]:
 for xx in [-2,2]:
  for yy in [-2,2]:cube('Water tower support',(x+xx,y+yy,4.3),(.35,.35,8.3),grey)
 cyl('Depot elevated water tank',(x,y,9.6),3.2,3,grey,24)
 polycurve('Water tower downpipe',[(x+2,y,10),(x+2,y,.3),(x+7,y,.3)],.1,bluepaint)
# Full site ground, boundaries, road, footpaths and vegetation.
group('40_SURROUNDINGS')
cube('Full metre-scale site ground',(-35,110,-.28),(2600,1050,.35),sand)
cube('Station approach road',(-15,-28,-.06),(360,15,.15),asphalt)
for x in range(-195,165,8):boxb('Road centre paint dash',(x,-28,.024),(4,.14,.008),ivory)
for yy in [-45,150]:
 for x in range(-710,570,5):
  cube('Boundary fence post',(x,yy,1.1),(.13,.13,2.2),grey)
 for z in [.35,1.1,1.85]:polycurve('Boundary wire',[(x,yy,z) for x in range(-710,571,5)],.012,metal)
# Coastal vegetation clusters: irregular branching foliage geometry, no billboard planes.
for i in range(65):
 x=random.uniform(-700,550);y=random.choice([-55,165])+random.uniform(-10,10);h=random.uniform(4,8)
 cyl('Tree trunk',(x,y,h/2),.14,h,trunk,9)
 for j in range(5):
  a=j*1.26;end=Vector((x+math.cos(a)*1.5,y+math.sin(a)*1.5,h+random.uniform(-.5,1)));beam('Tree branch',(x,y,h*.65),end,.055,trunk)
  # Low-poly leaf clusters retain volumetric silhouette.
  v=[(end.x+math.cos(k*math.pi/4)*2,end.y+math.sin(k*math.pi/4)*2,end.z) for k in range(8)]+[(end.x,end.y,end.z+1.6),(end.x,end.y,end.z-1.4)]
  mesh('Tree foliage crown',v,[(k,(k+1)%8,8) for k in range(8)]+[((k+1)%8,k,9) for k in range(8)],leaf)
# Fine world-metre-scale material texture, independent of the enormous batched mesh bounds.
for m,scale,strength in [(ballast,32,.55),(sleepermat,10,.20),(sand,6,.23),(tile,18,.11),(tile2,16,.15),(grey,8,.25)]:
 nt=m.node_tree;tex=next((n for n in nt.nodes if n.bl_idname=='ShaderNodeTexNoise'),None)
 if tex:
  tc=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tc.outputs['Object'],tex.inputs['Vector']);tex.inputs['Scale'].default_value=scale
  for n in nt.nodes:
   if n.bl_idname=='ShaderNodeBump':n.inputs['Strength'].default_value=strength
# Scene-level metadata and purpose-built review cameras.
flush();group('90_REVIEW_CAMERAS')
def camera(n,p,target,lens=42,ortho=None):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);active.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=8000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
cams=[camera('01_FACADE_AND_STATION',(-65,-92,24),(-8,3,5),43),camera('02_TICKET_HALL',(0,.85,2.25),(9,7,2.1),20),camera('03_WAITING_HALL',(-20,0.1,2.1),(-30,6,1.6),23),camera('04_TOILETS',(-68,2.2,2.5),(-71,9.5,1.55),21),camera('05_PLATFORM_DETAIL',(64,18.8,2.9),(-90,16.4,2.8),37),camera('06_FOOTBRIDGE',(fx+34,58,15),(fx,25,6),44),camera('07_YARD_POINTS',(280,114,26),(210,66,1.2),44),camera('08_DEPOT_PITS',(-50,157,32),(-265,80,1),43),camera('09_FULL_YARD_AERIAL',(-250,-330,960),(-50,100,0),42,1900),camera('10_FULL_YARD_TOP',(-70,100,1550),(-70,100,0),42,2350),camera('11_BAY_1A',(-200,-32,8),(-420,8,1.5),40),camera('12_UPPER_OFFICES',(15,1.9,5.8),(-4,6,5.5),23),camera('13_RAIL_FASTENINGS',(227,59,2.1),(216,58,.40),39),camera('14_SERVICE_WORKSHOP',(-289,120,2),(-323,130,1.5),24)]
d=bpy.data.lights.new('Coastal late-morning sun','SUN');o=bpy.data.objects.new('Coastal late-morning sun',d);active.objects.link(o);o.rotation_euler=(.5,-.4,-.5);d.energy=2.8;d.angle=.12
world=bpy.data.worlds.new('Coastal bright sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.67,.83,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
scene=bpy.context.scene;scene.world=world;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.4;scene.camera=cams[0]
scene['title']='NCJ detailed full-size pre-final-remodelling reconstruction';scene['era']='Mixed dated evidence: heritage facade2010; platform outlines2021/2023; mapped rail approaches through2025. Not an as-built survey.';scene['gauge_inner_faces_m']=1.676;scene['rolling_stock']='NONE';scene['interiors']='Original inferred furnished interiors; no measured room plan available';scene['source_topology']='OSM mapped centreline graph, supplemented with explicitly named reconstructed links for unmapped pit-road connections';scene['inferred_connections']=','.join(inferred)
for cn,c in cols.items():
 c['evidence']='Reconstructed detail' if 'RECONSTRUCTED' in cn else ('Mapped physical footprint/centreline' if 'MAP' in cn or 'OSM' in cn else 'Photo-informed architecture or original contextual geometry')
for f in bpy.data.fonts:
 if f.filepath and f.filepath!='<builtin>':f.pack()
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.clip_end=10000;ar.spaces.active.shading.color_type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'NCJ_full_station_v02.blend'),compress=True)
qa={'stage':'Base build before final physical and circulation finishing; see QA_VALIDATION.json for shipped geometry.','objects':len(scene.objects),'meshes':sum(o.type=='MESH' for o in scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'track_route_lengths_m':track_lengths,'total_route_metres':sum(track_lengths.values()),'mapped_route_count':original_count,'inferred_connected_pit_roads':inferred,'crossing_frog_locations':len(frogpoints),'buffer_stops':buffer_positions,'platforms':[{'osm_id':i,'extent_x_m':max(p.x for p in ps)-min(p.x for p in ps)} for i,ps in platforms],'rail_gauge_inner_faces_m':1.676,'rolling_stock_count':0,'interiors':['six ticket windows and clerk spaces','waiting hall','station manager','parcel office','six toilet cubicles and four washbasins','electrical/service room','three upper staff rooms','maintenance workshop','goods shed'],'cameras':[c.name for c in cams],'render_threads':4,'denoise':False}
(ROOT/'QA_BUILD.json').write_text(json.dumps(qa,indent=2));print('NCJ_FULL_SAVED',json.dumps({k:v for k,v in qa.items() if k in ['objects','vertices','total_route_metres','crossing_frog_locations']}),flush=True)
if '--export' in sys.argv:
 for o in scene.objects:o.select_set(o.type in {'MESH','FONT','CURVE'})
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/NCJ_full_station_v02.glb'),export_format='GLB',use_selection=True,export_apply=True)
if '--render' in sys.argv:
 for c in cams:
  scene.camera=c;scene.render.filepath=str(ROOT/'renders'/f'{c.name}.png');bpy.ops.render.render(write_still=True)
