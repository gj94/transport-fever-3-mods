"""Detailed ICF conventional shell. Metres, rail zero, true apertures.
Prototype visual interpretation, not a manufacturing/clearance model.
"""
import math
import bpy
from mathutils import Matrix

def rounded(x,y,z,w,h,r,N=8):
 pts=[]
 for cx,cz,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for k in range(N+1):
   t=math.radians(a+k*90/N);pts.append((x+cx+r*math.cos(t),y,z+cz+r*math.sin(t)))
 return pts

def panel(g,name,x,y,z,w,h,r,depth,mat,parent):
 a=rounded(x,y-depth/2,z,w,h,r);b=rounded(x,y+depth/2,z,w,h,r);n=len(a)
 return g.mesh(name,a+b,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],mat,parent)

def surround(g,name,x,y,z,w,h,r,border,mat,parent,depth=.013):
 a=rounded(x,y,z,w,h,r);b=rounded(x,y,z,w-2*border,h-2*border,max(.008,r-border));n=len(a)
 ob=g.mesh(name,a+b,[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],mat,parent)
 mod=ob.modifiers.new('Fabricated section thickness','SOLIDIFY');mod.thickness=depth
 return ob

def text(g,name,string,loc,size,mat,side,parent):
 ob=g.text(name,string,loc,size,mat,side,parent)
 ob.data.space_character=1.04
 return ob

def build(g,cfg):
 floor=g.FLOORZ;ac=cfg['ac'];V=g.V
 g.box('Floor steel undertray',(0,0,floor-.079),(21.337,3.08,.115),g.DARK)
 g.box('Interior floor seamless vinyl',(0,0,floor+.008),(21.13,3.10,.016),g.FLOOR,g.INTERIOR)
 for y in [-1.43,1.43]:g.box('Welded solebar channel',(0,y,1.125),(21.12,.15,.24),g.DARK,bevel=.01)
 for x in [-10+i*.8 for i in range(26)]:g.box('Body floor transverse bearer',(x,0,1.145),(.062,2.91,.14),g.DARK)
 n=cfg['windows'];pitch=15.12/n;wins=[-7.56+pitch*(i+.5) for i in range(n)]
 ww=min(1.22,pitch*.74) if ac else .65;wh=.64 if V in ['3A','CC'] else .75
 if V=='1A':wins=[-6.92,-5.40,-3.92,-2.40,-.50,1.50,3.50,5.08,6.59];ww=.98
 g.WINDOW_APERTURES=[]
 # Smooth mild tumblehome under the window sill, maximum bodyside width 3245 mm.
 def yy(z):return 1.6225 if z>=1.98 else 1.5525+.07*max(0,min(1,(z-floor)/(1.98-floor)))
 for s in [-1,1]:
  side=g.empty('SHELL_SIDE_'+('R' if s>0 else 'L'),(0,0,0),g.BODY)
  apertures=[dict(x=x,w=ww,z=2.385,h=wh,kind='saloon') for x in wins]
  apertures += [dict(x=x,w=.91,z=(floor+3.255)/2,h=3.255-floor,kind='door') for x in [-9.12,9.12]]
  apertures += [dict(x=x,w=.44,z=2.53,h=.68,kind='toilet') for x in [-10.12,10.12]]
  xs=sorted(set([-10.5685,10.5685]+[round(a['x']+k*a['w']/2,6) for a in apertures for k in [-1,1]]))
  zs=sorted(set([floor,1.98,2.80,3.39]+[round(a['z']+k*a['h']/2,6) for a in apertures for k in [-1,1]]))
  for xa,xb in zip(xs,xs[1:]):
   for za,zb in zip(zs,zs[1:]):
    x=(xa+xb)/2;z=(za+zb)/2
    if any(abs(x-a['x'])<a['w']/2-.00001 and abs(z-a['z'])<a['h']/2-.00001 for a in apertures):continue
    m=g.CYAN if 1.98<z<2.80 else g.BLUE
    vs=[(xa,s*yy(za),za),(xb,s*yy(za),za),(xb,s*yy(zb),zb),(xa,s*yy(zb),zb)]
    ob=g.mesh('Pressed bodyside skin',vs,[(0,1,2,3)] if s<0 else [(3,2,1,0)],m,side)
    mod=ob.modifiers.new('Steel skin thickness','SOLIDIFY');mod.thickness=.032
    # Independent matching lining, no hidden full-length wall over window/door apertures.
    vs=[(xx,s*(yy(zz)-.052),zz) for xx,_,zz in vs]
    ob=g.mesh('Lined bodyside aperture panel',vs,[(0,1,2,3)],g.CREAM,side);mod=ob.modifiers.new('Lining thickness','SOLIDIFY');mod.thickness=.012
  # Continuous drip rail and lower joint; tiny actual fabricated details, not heavy ribs.
  g.path('Bodyside roof rain gutter',[(-10.45,s*1.633,3.388),(10.45,s*1.633,3.388)],.011,g.ROOF,side,10)
  g.path('Floor skin rolled seam',[(-10.5,s*1.57,floor+.025),(10.5,s*1.57,floor+.025)],.005,g.BLUE,side,8)
  for i,x in enumerate(wins):
   g.WINDOW_APERTURES.append(dict(x=x,y=s*1.6225,z=2.385,width=ww,height=wh,rounded_radius=.10))
   surround(g,'Rounded body aperture corner',x,s*1.624,2.385,ww,wh,.005,.001,g.CYAN,side)
   # Corner infill connects the squared skin grid to the radiused window, with no backing pane.
   outer=rounded(x,s*1.624,2.385,ww,wh,.0001);inner=rounded(x,s*1.625,2.385,ww,wh,.10);N=len(outer)
   g.mesh('Pressed window aperture corner infill',outer+inner,[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)],g.CYAN,side)
   surround(g,'Continuous EPDM glazing gasket',x,s*1.638,2.385,ww+.024,wh+.024,.115,.026,g.RUBBER,side,.019)
   surround(g,'Anodised window frame extrusion',x,s*1.651,2.385,ww-.018,wh-.018,.094,.018,g.STEEL,side,.018)
   pane=panel(g,'Sealed tinted passenger pane' if ac else 'Clear raised sliding window pane',x,s*1.610,2.385,ww-.057,wh-.057,.080,.008,g.GLASS,side)
   pane['window_index']=i;pane['side']=s
   g.box('Interior rounded window sill',(x,s*1.50,2.006),(ww+.035,.13,.032),g.TRIM,side,.01)
   if not ac:
    for j in range(5):g.rod('Window stainless security bar',(x-ww/2+.012,s*1.674,2.103+j*.14),(x+ww/2-.012,s*1.674,2.103+j*.14),.009,g.STEEL,side,N=12)
    # Shutters are rolled metal louvres, parked above glazing, not opaque inserts over the aperture.
    for dx in [-ww/2+.026,ww/2-.026]:
     g.box('Sliding shutter guide channel',(x+dx,s*1.577,2.415),(.028,.026,.89),g.STEEL,side,.004)
    g.box('Raised twin shutter head',(x,s*1.578,2.878),(ww-.05,.038,.18),g.CYAN,side,.012)
    for dx in [-ww/4,ww/4]:
     for j in range(4):g.box('Shutter visible folded louvre',(x+dx,s*1.602,2.821+j*.033),(ww/2-.039,.015,.019),g.CYAN,side,.004)
     g.box('Shutter lift recessed grip',(x+dx,s*1.611,2.797),(.12,.018,.018),g.STEEL,side,.004)
    g.box('Window lower lock thumb tab',(x,s*1.664,2.055),(.066,.022,.021),g.STEEL,side,.004)
   elif V in ['1A','2A','CC']:
    # Wavy mesh curtains; no rectangular bars posing as cloth.
    for sign in [-1,1]:
     cx=x+sign*(ww/2-.06);v=[];NX=16;NZ=5
     for iz in range(NZ+1):
      z=2.045+iz*.70/NZ
      for j in range(NX+1):
       xx=cx+(j/NX-.5)*.12;v.append((xx,s*(1.491+.018*math.cos(j*math.pi/2)),z))
     f=[(iz*(NX+1)+j,iz*(NX+1)+j+1,(iz+1)*(NX+1)+j+1,(iz+1)*(NX+1)+j) for iz in range(NZ) for j in range(NX)]
     g.mesh('Gathered window curtain folds',v,f,g.CURTAIN,side)
     g.box('Window curtain fabric tie',(cx,s*1.471,2.30),(.122,.014,.03),g.TRIM,side,.004)
   if i in [1,len(wins)-2]:
    text(g,'Emergency window stencil','EMERGENCY WINDOW',(x,s*1.643,1.891),.040,g.RED,s,side)
    for dx in [-ww/2-.02,ww/2+.02]:g.box('Emergency red release indicator',(x+dx,s*1.66,2.16),(.018,.018,.10),g.RED,side,.004)
   if V in ['SL','3A','2A']:
    bay=i//2 if V in ['SL','2A'] else i
    if i%2==0 or V=='3A':text(g,'Berth range stencil',f'{bay*(8 if V!="2A" else 6)+1}-{min(cfg["capacity"],(bay+1)*(8 if V!="2A" else 6))}',(x,s*1.639,2.835),.044,g.WHITE,s,side)
  for x in [-9.12,9.12]:
   door=g.empty('DOOR_'+('A' if x<0 else 'B')+('_R' if s>0 else '_L')+'_PIVOT',(x-.398,s*1.57,floor+.035),g.BODY)
   g.box('Door peripheral reveal',(x,s*1.582,(floor+3.255)/2),(.845,.027,3.255-floor-.025),g.RUBBER,door,.02)
   # Remove the backing reveal and replace by an open rectangular ring.
   bpy.data.objects.remove(bpy.data.objects.get('Door peripheral reveal'),do_unlink=True)
   z=(floor+3.255)/2;h=3.255-floor-.035
   surround(g,'Entrance door weatherseal',x,s*1.594,z,.872,h,.030,.025,g.RUBBER,side)
   for z0,hh in [((floor+2.025)/2,2.025-floor-.045),(3.000,.465)]:
    panel(g,'Entrance pressed steel door panel',x,s*1.580,z0,.790,hh,.022,.041,g.BLUE,door)
   for dx in [-.349,.349]:g.box('Entrance glazed opening side rail',(x+dx,s*1.58,2.401),(.092,.041,.752),g.BLUE,door,.008)
   surround(g,'Entrance window gasket',x,s*1.610,2.401,.622,.758,.06,.028,g.RUBBER,door)
   panel(g,'Entrance clear door glazing',x,s*1.589,2.401,.564,.700,.033,.008,g.GLASS,door)
   if not ac:
    for j in range(5):g.rod('Entrance window protection bar',(x-.29,s*1.631,2.139+j*.131),(x+.29,s*1.631,2.139+j*.131),.008,g.STEEL,door,N=12)
   for z0 in [floor+.19,floor+.49]:surround(g,'Pressed door lower panel bead',x,s*1.607,z0,.62,.24,.018,.009,g.BLUE,door)
   for z0 in [floor+.24,2.27,3.10]:
    g.rod('Door hinge knuckle',(x-.398,s*1.617,z0-.047),(x-.398,s*1.617,z0+.047),.017,g.STEEL,door,N=16)
    for dx in [-.025,.025]:g.box('Door hinge plate',(x-.398+dx,s*1.599,z0),(.042,.018,.086),g.STEEL,door,.004)
   g.rod('Door polished pull',(x+.275,s*1.637,1.868),(x+.275,s*1.637,2.074),.012,g.STEEL,door,N=16)
   for z0 in [1.868,2.074]:g.rod('Door handle mounting boss',(x+.275,s*1.588,z0),(x+.275,s*1.637,z0),.016,g.STEEL,door,N=12)
   g.box('Door lock escutcheon',(x+.273,s*1.611,1.815),(.052,.012,.068),g.STEEL,door,.008)
   g.box('Door key slot',(x+.273,s*1.619,1.815),(.009,.007,.027),g.DARK,door)
   for dx in [-.487,.487]:
    g.path('Bent entrance stainless grabrail',[(x+dx,s*1.615,1.455),(x+dx,s*1.723,1.53),(x+dx,s*1.723,2.948),(x+dx,s*1.615,3.013)],.018,g.STEEL,side,16)
    for z0 in [1.455,3.013]:
     g.box('Grabrail mounting pad',(x+dx,s*1.625,z0),(.064,.018,.09),g.STEEL,side,.009)
   for z0 in [.463,.726,.989,1.252]:
    g.box('Entrance ladder perforated tread',(x,s*1.619,z0),(.802,.262,.032),g.DARK,side,.004)
    for dx in [-.35+k*.05 for k in range(15)]:g.box('Entry tread raised antislip ridge',(x+dx,s*1.619,z0+.019),(.016,.247,.007),g.STEEL,side,.002)
   for dx in [-.37,.37]:g.box('Entrance ladder angle stringer',(x+dx,s*1.58,.865),(.042,.06,.84),g.DARK,side,.006)
   text(g,'Door instruction','PULL',(x+.27,s*1.635,2.105),.037,g.WHITE,s,door)
   text(g,'Entry lettering','ENTRY',(x,s*1.639,3.288),.055,g.WHITE,s,side)
  for x in [-10.12,10.12]:
   surround(g,'Toilet window black gasket',x,s*1.639,2.53,.46,.70,.075,.027,g.RUBBER,side)
   panel(g,'Obscure toilet glass',x,s*1.617,2.53,.409,.649,.052,.008,g.FROST,side)
   for zz in [2.33,2.48,2.63,2.78]:g.rod('Toilet window external bar',(x-.19,s*1.669,zz),(x+.19,s*1.669,zz),.007,g.STEEL,side,N=10)
  # Service era markings are illustrative, not a forged numbered photograph reconstruction.
  text(g,'English class legend',cfg['label'].replace('  ',' '),(2.7*s,s*1.642,3.035),.13,g.CYAN,s,side)
  text(g,'Coach number illustrative',{'1A':'991801','2A':'984602','3A':'016403','CC':'047304','2S':'031805','SL':'027206','GS':'041807'}[V],(-6.1*s,s*1.642,3.047),.17,g.CYAN,s,side)
  text(g,'Zone initials','IR',(-7.49*s,s*1.642,3.04),.16,g.CYAN,s,side)
  # Raised routeboard with top and bottom rolled clip retainers.
  g.box('Yellow destination board',(0,s*1.649,3.137),(1.92,.022,.218),g.YELLOW,side,.007)
  text(g,'Route destination legend','INDIAN RAILWAYS',(0,s*1.666,3.100),.073,g.DARK,s,side)
  for xx in [-.98,.98]:g.box('Destination board mounting bracket',(xx,s*1.654,3.137),(.040,.030,.255),g.DARK,side,.004)
  for xx in [-.92,.92]:
   for zz in [3.056,3.218]:g.rod('Destination board fixing screw',(xx,s*1.66,zz),(xx,s*1.68,zz),.009,g.STEEL,side,N=8)
  g.box('Coach position plate',(-1.54*s,s*1.65,2.971),(.25,.022,.27),g.YELLOW,side,.008)
  text(g,'Coach position character',{'SL':'S1','3A':'B1','2A':'A1','1A':'H1','CC':'C1','2S':'D1','GS':'GS'}[V],(-1.54*s,s*1.669,2.91),.086,g.DARK,s,side)
  for xx in [-8.16,8.16]:
   text(g,'Technical maintenance stencil',f'{cfg["code"].split()[0]}  {cfg["capacity"]}  TARE', (xx,s*1.59,1.518),.039,g.WHITE,s,side)
  text(g,'Pneumatic release stencil','RELEASE',(0,s*1.585,1.40),.039,g.WHITE,s,side)
  # Rounded ICF body/end corner: quarter cylindrical bend, not LHB tapered end.
  for end in [-1,1]:
   pts=[]
   for z in [floor,1.98,2.80,3.39]:
    for j in range(9):
     a=j*math.pi/16;pts.append((end*(10.5685+.10*math.sin(a)),s*(yy(z)-.10+.10*math.cos(a)),z))
   for iz in range(3):g.mesh('Rounded end corner pressed skin',pts,[(iz*9+j,iz*9+j+1,(iz+1)*9+j+1,(iz+1)*9+j) for j in range(8)],g.CYAN if iz==1 else g.BLUE,side)
 roof=g.empty('ROOF_ASSEMBLY',(0,0,0),g.BODY)
 N=64;xs=[-10.6685,-10.60,-10.48,-10.30,10.30,10.48,10.60,10.6685];vs=[]
 for x in xs:
  # Slight downturn at curved end cap, with exact central crown retained.
  drop=max(0,(abs(x)-10.30)/.3685)*.038
  for j in range(N+1):
   a=j*math.pi/N;vs.append((x,1.6225*math.cos(a),3.39+(.635-drop)*math.sin(a)))
 fs=[(ix*(N+1)+j,ix*(N+1)+j+1,(ix+1)*(N+1)+j+1,(ix+1)*(N+1)+j) for ix in range(len(xs)-1) for j in range(N)]
 ob=g.mesh('Curved steel roof continuous skin',vs,fs,g.ROOF,roof)
 for p in ob.data.polygons:p.use_smooth=True
 mod=ob.modifiers.new('Pressed steel roof thickness','SOLIDIFY');mod.thickness=.024
 vs=[(x,1.556*math.cos(j*math.pi/N),3.356+.587*math.sin(j*math.pi/N)) for x in [-10.52,10.52] for j in range(N+1)]
 ob=g.mesh('Arched interior ceiling laminate',vs,[(j,j+1,N+j+2,N+j+1) for j in range(N)],g.CREAM,roof)
 for p in ob.data.polygons:p.use_smooth=True
 for x in [-9.6,-7.2,-4.8,-2.4,0,2.4,4.8,7.2,9.6]:
  g.path('Roof sheet flush weld',[(x,1.6235*math.cos(j*math.pi/32),3.393+.635*math.sin(j*math.pi/32)) for j in range(33)],.0028,g.ROOF,roof,6)
 if ac:
  g.box('Conventional underslung AC internal trunk',(0,0,3.72),(15.95,.65,.18),g.CREAM,roof,.025)
  for x in [-7.2+i*1.8 for i in range(9)]:
   for s in [-1,1]:
    g.box('AC louvre diffuser backing',(x,s*.332,3.688),(.39,.018,.095),g.DARK,roof,.004)
    for dx in [-.165+j*.047 for j in range(8)]:g.box('AC diffuser directional vane',(x+dx,s*.346,3.688),(.017,.028,.086),g.TRIM,roof,.003)
 else:
  for x in [-7.12+i*1.78 for i in range(9)]:
   g.box('Torpedo vent mounting flange',(x,0,4.013),(.49,.32,.032),g.ROOF,roof,.012)
   # Low cowl with sloped ends, central rain cap and actual dark intake slot.
   v=[(x+dx,y,z) for dx,y,z in [(-.22,-.125,4.024),(.22,-.125,4.024),(.16,-.125,4.079),(-.16,-.125,4.079),(-.22,.125,4.024),(.22,.125,4.024),(.16,.125,4.079),(-.16,.125,4.079)]]
   g.mesh('Pressed roof ventilator rain cowl',v,[(0,1,2,3),(4,7,6,5),(3,2,6,7),(0,4,5,1)],g.ROOF,roof)
   for s in [-1,1]:g.box('Ventilator airway mouth',(x,s*.126,4.048),(.30,.008,.025),g.DARK,roof)
 ends(g)
 return wins

def ends(g):
 for s in [-1,1]:
  end=g.empty('END_'+('A' if s<0 else 'B'),(0,0,0),g.BODY)
  for yy in [-1.08,1.08]:g.box('Formed end wall',(s*10.647,yy,2.32),(.042,.87,2.10),g.BLUE,end,.02)
  g.box('End wall door header',(s*10.647,0,3.323),(.042,3.04,.17),g.BLUE,end)
  vs=[(s*10.647,1.52*math.cos(j*math.pi/48),3.39+.597*math.sin(j*math.pi/48)) for j in range(49)]
  g.mesh('Domed end cap skin',vs,[tuple(range(49))],g.BLUE,end)
  for yy in [-1.49,1.49]:g.box('Yellow end visibility stripe',(s*10.674,yy,2.31),(.009,.045,1.92),g.YELLOW,end)
  for j in range(9):
   xx=s*(10.680+j*.030)
   for yy in [-.605,.605]:g.box('Concertina gangway upright fold',(xx,yy,2.274),(.020,.110,1.925),g.RUBBER,end,.008)
   g.box('Concertina gangway roof fold',(xx,0,3.233),(.020,1.27,.112),g.RUBBER,end,.012)
  for yy in [-.607,.607]:g.box('Gangway sprung face frame',(s*10.937,yy,2.274),(.026,.13,1.935),g.DARK,end,.009)
  g.box('Gangway sprung top frame',(s*10.937,0,3.237),(.026,1.28,.128),g.DARK,end,.009)
  g.box('Vestibule bridge plate',(s*10.81,0,g.FLOORZ-.005),(.38,1.12,.045),g.STEEL,end,.004)
  for y in [-.48+i*.08 for i in range(13)]:g.box('Bridge plate grip rib',(s*10.82,y,g.FLOORZ+.022),(.34,.012,.008),g.DARK,end)
  for yy in [-.368,.368]:g.box('End sliding door stile',(s*10.467,yy,2.282),(.037,.133,1.953),g.TRIM,end,.008)
  for z,h in [(1.78,.94),(3.072,.375)]:g.box('End sliding door panel',(s*10.467,0,z),(.037,.74,h),g.CREAM,end,.01)
  g.box('End door clear window',(s*10.467,0,2.61),(.008,.594,.712),g.GLASS,end,.015)
  for yy in [-.301,.301]:g.rod('End glazed door vertical gasket',(s*10.491,yy,2.25),(s*10.491,yy,2.98),.009,g.RUBBER,end,N=10)
  for zz in [2.25,2.98]:g.rod('End glazed door horizontal gasket',(s*10.491,-.30,zz),(s*10.491,.30,zz),.009,g.RUBBER,end,N=10)
  for yy in [-.276,.276]:g.rod('Vestibule door grab pull',(s*10.433,yy,1.938),(s*10.433,yy,2.20),.013,g.STEEL,end,N=14)
  for yy in [-1.20,1.20]:
   g.box('End marker lamp socket',(s*10.697,yy,2.855),(.040,.14,.18),g.DARK,end,.02)
   g.box('End red marker reflector',(s*10.723,yy,2.855),(.012,.105,.13),g.RED,end,.025)
  # Roof water-filling pipe descends outside the gangway, accompanied by handle and unions.
  g.path('End water fill pipe',[(s*10.70,1.11,3.69),(s*10.72,1.11,3.05),(s*10.72,1.11,1.46),(s*10.64,1.11,1.15)],.021,g.STEEL,end,14)
  for zz in [1.65,2.4,3.22]:g.box('Water pipe end wall retaining strap',(s*10.701,1.11,zz),(.040,.091,.023),g.DARK,end,.003)
  for yy in [-.86,.86]:g.path('End maintenance grab handle',[(s*10.69,yy-.12,2.53),(s*10.75,yy-.12,2.53),(s*10.75,yy+.12,2.53),(s*10.69,yy+.12,2.53)],.014,g.STEEL,end,12)
