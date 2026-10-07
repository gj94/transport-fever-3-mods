"""Conventional vestibules and four end lavatories, original representative layout.
Two Indian-style pans and two Western-style pans are a modelling choice, not a
claim that every numbered coach uses this allocation. No imported assets.
"""
import math

def basin(g,n,c,rx,ry,depth,mat,parent):
 x,y,z=c;N=48
 rings=[(rx,ry,z),(rx*.83,ry*.81,z+.006),(rx*.69,ry*.66,z-depth*.46),(rx*.18,ry*.18,z-depth)]
 vs=[(x+a*math.cos(i*2*math.pi/N),y+b*math.sin(i*2*math.pi/N),h) for a,b,h in rings for i in range(N)]
 fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(3) for i in range(N)]
 ob=g.mesh(n,vs,fs,mat,parent)
 for p in ob.data.polygons:p.use_smooth=True
 # Drain grille is at the actual well bottom, never an opaque face at the rim.
 g.rod(n+' drain',(x,y,z-depth-.003),(x,y,z-depth+.002),min(rx,ry)*.15,g.STEEL,parent,N=24)
 for dx in [-.013,0,.013]:g.box(n+' drain slot',(x+dx,y,z-depth+.003),(.005,.035,.002),g.DARK,parent)
 return ob

def build(g,ac):
 floor=g.FLOORZ
 for end in [-1,1]:
  aisle=1.06 if g.V=='1A' else (.62 if g.V in ['2A','3A','SL'] else 0);clear=.68 if aisle else .62
  le=aisle-clear/2;ri=aisle+clear/2
  for ya,yb in [(-1.53,le),(ri,1.53)]:g.box('Saloon end bulkhead',(end*8.1,(ya+yb)/2,2.35),(.045,yb-ya,2.08),g.CREAM,g.INTERIOR)
  g.box('Saloon doorway header',(end*8.1,aisle,3.34),(.05,clear,.15),g.TRIM,g.INTERIOR)
  if ac:
   parked=le-.25 if ri+.5>1.5 else ri+.25
   g.box('Saloon sliding door parked panel',(end*8.152,parked,2.36),(.033,.49,1.90),g.CREAM,g.INTERIOR,.008)
   g.rod('Saloon door handle',(end*8.174,parked-.12,2.10),(end*8.174,parked-.12,2.33),.013,g.STEEL,g.INTERIOR)
  for side in [-1,1]:
   x=end*10.13;y=side*1.01
   g.box('Lavatory cross partition',(end*9.66,y,2.30),(.045,1.07,1.99),g.CREAM,g.INTERIOR)
   # Split doorway stiles/header: no full backing wall through the door leaf.
   for dx in [-.403,.403]:g.box('Lavatory door jamb',(x+dx,side*.485,2.31),(.095,.045,2.02),g.CREAM,g.INTERIOR)
   g.box('Lavatory door head',(x,side*.485,3.286),(.71,.045,.11),g.CREAM,g.INTERIOR)
   g.box('Lavatory door leaf',(x,side*.462,2.28),(.703,.036,1.87),g.TRIM,g.INTERIOR,.008)
   for z in [1.53,2.31,3.07]:g.rod('Lavatory hinge knuckle',(x-.352,side*.437,z-.025),(x-.352,side*.437,z+.025),.014,g.STEEL,g.INTERIOR,N=16)
   g.rod('Lavatory inside pull',(x+.20,side*.433,2.10),(x+.20,side*.433,2.27),.011,g.STEEL,g.INTERIOR)
   g.box('Lavatory rotary latch plate',(x+.23,side*.438,2.03),(.10,.013,.065),g.STEEL,g.INTERIOR,.006)
   g.box('Lavatory occupied indicator',(x+.23,side*.430,2.03),(.043,.003,.018),g.RED,g.INTERIOR,.003)
   g.text('Lavatory style label','INDIAN' if side<0 else 'WESTERN',(x,side*.439,2.84),.05,g.DARK,-side,g.INTERIOR)
   g.box('Lavatory nonslip tray',(x,y,floor+.032),(.83,.95,.045),g.TRIM,g.INTERIOR,.007)
   if side<0:
    # Raised stainless squat pan with actual dished opening and two ribbed foot pads.
    basin(g,'Indian stainless squatting pan',(x,y,floor+.155),.245,.17,.095,g.STEEL,g.INTERIOR)
    for dy in [-.28,.28]:
     g.box('Indian pan foot pad',(x,y+dy,floor+.094),(.49,.145,.076),g.STEEL,g.INTERIOR,.032)
     for dx in [-.18,-.12,-.06,0,.06,.12,.18]:g.box('Squat footpad antislip ridge',(x+dx,y+dy,floor+.135),(.012,.122,.008),g.DARK,g.INTERIOR,.003)
   else:
    g.box('Western toilet ceramic pedestal',(x,y,floor+.25),(.26,.29,.39),g.WHITE,g.INTERIOR,.065)
    basin(g,'Western toilet hollow bowl',(x,y,floor+.52),.24,.22,.17,g.WHITE,g.INTERIOR)
    for dx in [-.12,.12]:g.box('Toilet seat hinge',(x+dx,y+.19,floor+.53),(.043,.07,.033),g.STEEL,g.INTERIOR,.008)
    # Elliptical open seat ring, separately surfaced above the bowl.
    N=64;vs=[]
    for rx,ry,z in [(.245,.225,floor+.54),(.185,.164,floor+.54),(.245,.225,floor+.515),(.185,.164,floor+.515)]:
     vs.extend((x+rx*math.cos(i*2*math.pi/N),y+ry*math.sin(i*2*math.pi/N),z) for i in range(N))
    fs=[]
    for a,b in [(0,1),(2,0),(1,3),(3,2)]:fs.extend((a*N+i,a*N+(i+1)%N,b*N+(i+1)%N,b*N+i) for i in range(N))
    g.mesh('Western toilet open seat ring',vs,fs,g.TRIM,g.INTERIOR)
    g.rod('Toilet tissue roll',(x-.33,y-.07,2.04),(x-.33,y+.07,2.04),.055,g.WHITE,g.INTERIOR,N=32)
   g.box('Lavatory flush valve mount',(end*10.45,y,2.03),(.028,.12,.13),g.STEEL,g.INTERIOR,.009)
   g.rod('Lavatory flush pushbutton',(end*10.43,y,2.03),(end*10.412,y,2.03),.027,g.TRIM,g.INTERIOR,N=24)
   g.path('Lavatory flush pipe',[(end*10.445,y,2.03),(end*10.445,y,1.54),(x,y,1.54)],.017,g.STEEL,g.INTERIOR,14)
   g.rod('Lavatory grab handle',(end*9.72,y-.25,2.08),(end*9.72,y+.25,2.08),.012,g.STEEL,g.INTERIOR)
   g.path('Lavatory wash spray hose',[(end*10.43,y-.27,1.85),(end*10.35,y-.27,1.60),(end*10.30,y-.27,1.45),(end*10.20,y-.27,1.51)],.009,g.STEEL,g.INTERIOR,12)
   g.box('Lavatory stainless floor drain',(end*9.82,y,floor+.060),(.18,.18,.008),g.STEEL,g.INTERIOR,.006)
   for dx in [-.06,-.03,0,.03,.06]:g.box('Lavatory drain perforation',(end*9.82+dx,y,floor+.065),(.008,.13,.002),g.DARK,g.INTERIOR,.002)
   # End vestibule washbasin: a true hollow bowl replaces the old dark inset.
   xx=end*9.40;yy=side*1.12
   g.box('Washbasin undercounter cabinet',(xx,yy,floor+.45),(.35,.55,.62),g.CREAM,g.INTERIOR,.025)
   basin(g,'Vestibule handwash bowl',(xx,yy,floor+.88),.195,.265,.11,g.WHITE,g.INTERIOR)
   g.path('Washbasin bent tap',[(end*9.54,yy,floor+.89),(end*9.54,yy,floor+1.045),(end*9.43,yy,floor+1.045)],.011,g.STEEL,g.INTERIOR,16)
   g.box('Washbasin mirror',(end*9.632,yy,2.62),(.012,.50,.58),g.MIRROR,g.INTERIOR,.008)
   for zz in [2.32,2.92]:g.box('Washbasin mirror horizontal trim',(end*9.620,yy,zz),(.020,.525,.025),g.STEEL,g.INTERIOR,.005)
  for yy in [-1.34,1.34]:g.rod('Vestibule interior grab pole',(end*8.60,yy,floor+.12),(end*8.60,yy,3.18),.021,g.STEEL,g.INTERIOR)
  g.text('Interior emergency instructions','EMERGENCY',(end*8.48,-1.468,2.48),.065,g.RED,-1,g.INTERIOR)
  g.box('Electrical distribution cupboard',(end*8.50,1.28,2.34),(.40,.45,1.91),g.CREAM,g.INTERIOR,.01)
  for z in [1.65,2.1,2.55,3.0]:
   g.box('Distribution cupboard access panel',(end*8.50,1.04,z),(.34,.018,.35),g.TRIM,g.INTERIOR,.004)
   g.box('Distribution panel quarter turn latch',(end*8.60,1.025,z),(.018,.010,.06),g.STEEL,g.INTERIOR,.003)
