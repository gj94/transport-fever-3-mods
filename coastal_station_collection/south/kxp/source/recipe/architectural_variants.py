"""Station-specific photograph-informed geometry; imported into build_station namespace.
Sources are separately recorded in each station's evidence file. Hidden spaces remain reconstructed.
"""
def clear_groups(names):
 for key in list(batches):
  if key[0] in names:del batches[key]
 for cn in names:
  if cn in collections:
   for o in list(collections[cn].objects):bpy.data.objects.remove(o,do_unlink=True)
def flat_slab(n,x,y,z,w,d,m='ivory',h=.16):b_box(n,(x,y,z),(w,d,h),m)
def sheet_wall(n,x0,x1,y,z0,z1,m):
 for i in range(max(1,int((x1-x0)/.15))):
  x=x0+(i+.5)*(x1-x0)/max(1,int((x1-x0)/.15));b_box(n,(x,y+(.025 if i%2 else -.025),(z0+z1)/2),((x1-x0)/max(1,int((x1-x0)/.15)),.055,z1-z0),m)
def broadleaf_tree(x,y,h=8,r=5):
 group('40_FORECOURT_AND_LANDSCAPE');beam('Spreading shade tree trunk',(x,y,-.3),(x+.25,y,h*.60),.23,'trunk')
 for j in range(8):
  a=j*math.tau/8;dx,dy=math.cos(a),math.sin(a);end=(x+dx*r*.8,y+dy*r*.8,h*.80+random.uniform(-.5,.5));beam('Branching shade tree limb',(x+.2,y,h*.44),end,.07,'trunk')
  # Airy individual leaves keep a real foliage silhouette rather than low-poly green solids.
  for k in range(3):
   cx=end[0]+random.uniform(-1.2,1.2);cy=end[1]+random.uniform(-1.2,1.2);cz=end[2]+random.uniform(-.5,1.1);rr=random.uniform(1.2,2.1);vs=[];fs=[]
   for j0 in range(100):
    a0=random.random()*math.tau;r0=rr*math.sqrt(random.random());px=cx+math.cos(a0)*r0;py=cy+math.sin(a0)*r0;pz=cz+random.uniform(-.7,.7);ang=random.random()*math.tau;le=random.uniform(.13,.32);wi=le*.35;dx,dy=math.cos(ang),math.sin(ang);nx,ny=-dy,dx;k0=len(vs)
    vs.extend([(px-dx*le,py-dy*le,pz),(px+nx*wi,py+ny*wi,pz+.05),(px+dx*le,py+dy*le,pz-.03),(px-nx*wi,py-ny*wi,pz+.04)]);fs.append((k0,k0+1,k0+2,k0+3))
   mesh('Individual spreading-tree leaves',vs,fs,M['green'])
arch=C.get('architecture')
if arch=='pgz_hut':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');ht=3.05
 b_box('PGZ small hut plinth',(0,H/2,Z-.16),(W+.25,H+.2,.32),'concrete');b_box('PGZ hut floor',(0,H/2,Z+.025),(W,H,.10),'tile')
 # Street side has an open door, window and three high ventilators; platform facade has the source stepped asymmetry.
 for a,b in [(-W/2,-.7),(.7,W/2)]:b_box('PGZ street wall portal',((a+b)/2,0,Z+ht/2),(b-a,.22,ht),'cream')
 b_box('PGZ street door lintel',(0,0,Z+2.65),(1.4,.22,.8),'cream')
 for x in [-W/2,W/2]:b_box('PGZ short end wall',(x,H/2,Z+ht/2),(.22,H,ht),'cream')
 # Platform front: left feature bay, central open accordion-gate entrance, right double-door booking bay.
 split=-.25;door0=.1;door1=2.05
 b_box('PGZ tall left feature wall',(-W*.28,H,Z+2.12),(W*.43,.22,4.24),'cream')
 b_box('PGZ right lower wall',(W*.40,H,Z+ht/2),(W*.20,.22,ht),'cream')
 b_box('PGZ central portal header',(1.02,H,Z+2.84),(2.05,.24,.42),'cream')
 for x in [-W*.49,-W*.065]:b_box('PGZ projecting feature pier',(x,H+.16,Z+2.14),(.25,.50,4.28),'ivory')
 # Shallow gabled feature profile, not a full hipped heritage roof.
 apex=Z+4.68;left=-W/2;right=-W*.055
 mesh('PGZ raised gable face',[bp(left,H,Z+4.17),bp(right,H,Z+4.17),bp((left+right)/2,H,apex)],[(0,1,2)],M['cream'])
 b_beam('PGZ gable projecting trim',(left-.2,H+.24,Z+4.22),((left+right)/2,H+.24,apex+.05),.105,'ivory');b_beam('PGZ gable projecting trim',((left+right)/2,H+.24,apex+.05),(right+.18,H+.24,Z+4.22),.105,'ivory')
 b_box('PGZ lower lintel shade',(-W*.28,H+.25,Z+2.99),(W*.49,.66,.15),'ivory')
 for x in [-W*.375,-W*.195]:
  b_box('PGZ lattice window recess',(x,H+.135,Z+1.95),(.67,.03,1.48),'dark')
  # Clearly visible staggered perforated concrete grille, reconstructed pattern from the photograph.
  for j in range(6):
   for k in range(4):
    xx=x-.275+k*.18;zz=Z+1.32+j*.24;b_box('PGZ lattice horizontal',(xx,H+.19,zz),(.18,.07,.035),'ivory');b_box('PGZ lattice upright',(xx+(.075 if j%2 else -.075),H+.19,zz+.11),(.035,.07,.24),'ivory')
 b_box('PGZ built-in external bench',(-W*.28,H+.27,Z+.40),(W*.38,.54,.16),'concrete')
 # Open folded gate leaves keep real threshold clear; red/brown double leaf at right bay.
 for x in [.12,1.95]:
  for j in range(5):b_box('PGZ folded gate bars',(x+(j-2)*.028,H+.02,Z+1.1),(.018,.08,2.2),'red')
 b_box('PGZ booking double door',(W*.397,H+.13,Z+1.04),(1.35,.06,2.08),'red')
 b_box('PGZ door centre seam',(W*.397,H+.17,Z+1.04),(.025,.022,2.08),'dark')
 for x in [W*.35,W*.435]:b_box('PGZ brass door handle',(x,H+.20,Z+1.01),(.04,.035,.17),'steel')
 # Real photographed low yellow fascia on right; local/English text is geometry.
 group('32_ARCHITECTURAL_SIGNS');b_box('PGZ yellow name fascia',(W*.21,H+.17,Z+3.16),(W*.57,.13,.35),'yellow');text('PGZ fascia English','PERUNGUZHI',bp(W*.21,H+.25,Z+3.16),.20,'dark',W*.52,rot=(math.pi/2,0,0) if side>0 else (math.pi/2,0,math.pi))
 group('31_ROOFS_REMOVABLE');flat_slab('PGZ left flat roof',-W*.27,H/2,Z+3.50,W*.46,H+.45);flat_slab('PGZ right low roof',W*.24,H/2,Z+3.05,W*.56,H+.4);b_box('PGZ stepped roof vertical closure',(-W*.04,H/2,Z+3.275),(.12,H,.45),'cream')
 # Side elevation high vents and ochre pilasters.
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for yy in [H*.22,H*.48,H*.72]:
  b_box('PGZ three end-wall high vents',(-W/2-.125,yy,Z+2.48),(.02,.44,.19),'dark')
 for x in [-W/2+.15,W*.44]:b_box('PGZ ochre wall pilaster',(x,-.14,Z+ht/2),(.16,.08,ht),'yellow')
 b_box('PGZ yellow flat roof edge',(0,-.15,Z+3.09),(W+.26,.16,.17),'yellow')
 # Additional switchback-like approach runs and double rails documented in2020 image.
 group('35_BUILDING_ACCESS');b_box('PGZ rear approach landing',(0,-1.8,Z-.015),(W,3.6,.14),'tile');b_box('PGZ doorway right jamb',(2.27,H+.03,Z+1.50),(.44,.20,3.0),'cream');startx=bx-W/2-8;endy=build_front+side*9.0
 box('PGZ red-grid ramp landing',(startx+9,endy,-.055),(18,2.2,.18),'terracotta')
 for yy in [endy-1.0,endy+1.0]:
  for xx in [startx+j*2.5 for j in range(8)]:
   if abs(xx-(bx-W*.35))>1.2:beam('PGZ red ramp posts',(xx,yy,.03),(xx,yy,1.08),.03,'red')
  for z in [.60,1.05]:
   for a,b in [(startx,bx-W*.35-1.2),(bx-W*.35+1.2,startx+17.5)]:
    if b>a:beam('PGZ double ramp handrail with passage',(a,yy,z),(b,yy,z),.025,'red')
 # The long photographed path is extra context; main ramp has continuous sloping access.
 for sx in [-1,1]:beam('PGZ main ramp handrail',(bx-W*.35+sx,build_front+side*3.6,Z+1.02),(bx-W*.35+sx,build_front+side*15.6,.84),.03,'red')
 for xx,yy in [(bx-W*.70,by+side*3),(bx+W*.75,by+side*5)]:broadleaf_tree(xx,yy,8.5,4.6)
 # Ground-floor ticket counter and furnishings are explicitly hidden-interior reconstruction.
elif arch=='davm_ticket_shelter':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS','33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED','34_STAFF_TOILET_SERVICE_RECONSTRUCTED']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');ht=2.85
 b_box('DAVM small waiting shelter floor',(0,H/2,Z+.02),(W,H,.12),'tile')
 # Corrugated end wall with cream lower zone and turquoise upper triangle.
 sheet_wall('DAVM cream corrugated end wall',-W/2,W/2,H,Z,Z+1.30,'ivory');sheet_wall('DAVM turquoise corrugated end wall',-W/2,W/2,H,Z+1.30,Z+ht,'teal')
 for x in [-W/2,W/2]:
  for j in range(int(H/.15)):
   yy=(j+.5)*H/int(H/.15);b_box('DAVM corrugated open half side',(x+(.025 if j%2 else -.025),yy,Z+.60),(.055,H/int(H/.15),1.20),'ivory')
  for yy in [0,H/2,H]:b_box('DAVM steel angle column',(x,yy,Z+1.45),(.075,.075,2.9),'concrete')
  b_beam('DAVM open side horizontal member',(x,0,Z+2.05),(x,H,Z+2.05),.025,'concrete')
 group('31_ROOFS_REMOVABLE');ridge=Z+3.70;roofz=Z+2.80;v=[bp(-W/2-.30,-.3,roofz),bp(W/2+.30,-.3,roofz),bp(-W/2-.30,H+.3,roofz),bp(W/2+.30,H+.3,roofz),bp(0,-.3,ridge),bp(0,H+.3,ridge)];mesh('DAVM corrugated metal gable roof',v,[(0,2,5,4),(4,5,3,1)],M['roof'])
 for y in [0,H/2,H]:
  b_beam('DAVM roof triangular tie',(-W/2,y,roofz),(W/2,y,roofz),.035,'concrete')
  for sg in [-1,1]:b_beam('DAVM exposed roof angle',(0,y,ridge),(sg*W/2,y,roofz),.035,'concrete')
 for j in range(int(H/.14)):
  yy=-.3+j*.14
  for sg in [-1,1]:b_beam('DAVM roof corrugation',(0,yy,ridge+.018),(sg*(W/2+.3),yy,roofz+.018),.02,'roof')
 # Gabled turquoise end infill follows slope.
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for j in range(int(W/.15)):
  xx=-W/2+(j+.5)*W/int(W/.15);zh=ridge-abs(xx)/(W/2)*(ridge-roofz);b_box('DAVM teal gable sheet',(xx,H,Z+ht+(zh-(Z+ht))/2),(.145,.055,max(.02,zh-(Z+ht))),'teal')
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED')
 # Two inward-facing yellow slatted benches, shaped turquoise concrete feet.
 for sg in [-1,1]:
  xx=sg*(W/2-.58)
  for yy in [1.2,3.7]:b_box('DAVM turquoise bench pedestal',(xx,yy,Z+.26),(.66,.22,.52),'teal')
  for j in range(4):b_box('DAVM yellow bench seat',(xx+(j-1.5)*.14,2.45,Z+.53),(.12,3.2,.065),'yellow')
  for j in range(3):b_box('DAVM yellow slat back',(xx+sg*.34,2.45,Z+.77+j*.16),(.05,3.2,.13),'yellow')
 # Tiny actual back-wall ticket hatch, round speaking aperture and black plaque.
 b_box('DAVM ticket hatch shadow',(1.25,H-.055,Z+1.03),(.76,.07,.66),'dark');b_box('DAVM brown ticket shutter',(1.25,H-.105,Z+1.03),(.73,.045,.61),'red')
 for xx in [.95,1.10,1.25,1.40,1.55]:b_box('DAVM ticket hatch vertical bar',(xx,H-.14,Z+1.03),(.018,.024,.61),'steel')
 for zz in [Z+.83,Z+1.23]:b_box('DAVM ticket hatch horizontal bar',(1.25,H-.15,zz),(.72,.024,.018),'steel')
 b_box('DAVM speaking panel',(1.25,H-.065,Z+1.75),(.44,.05,.47),'wood');o=cyl('DAVM round speaking aperture',bp(1.25,H-.10,Z+1.75),.085,.015,'dark',20);o.rotation_euler.x=math.pi/2
 b_box('DAVM ticket sign',(1.25,H-.09,Z+2.20),(.88,.07,.33),'dark');b_text('DAVM ticket sign type','TICKET COUNTER',(1.25,H-.14,Z+2.2),.115,'white',.8)
 b_box('DAVM timetable blue board',(-1.0,H-.095,Z+1.89),(2.5,.09,1.03),'blue')
 for j in range(10):b_box('DAVM timetable printed entries',(-1,H-.15,Z+2.30-j*.08),(2.3,.01,.016),'white')
 xx,yy,_=bp(0,H/2,0);light(xx,yy,ridge-.20);area('DAVM shelter light',(xx,yy,ridge-.20),180,2)
 # Physical doubled corridor is graded earth, never falsely represented as commissioned second track.
 group('40_FORECOURT_AND_LANDSCAPE');rail_y=D['cross_section_y'][0];box('DAVM uncompleted graded corridor',(0,rail_y-7,-.31),(500,8,.07),'soil')
elif arch=='tvcs_teal':
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for x in [-W/2,-W*.28,0,W*.28,W/2]:
  for yy in [0,H]:b_box('TVCS teal facade pier',(x,yy-.16,Z+1.70),(.25,.075,3.4),'teal')
 for yy in [0,H]:
  for z in [Z+2.70,Z+3.65]:b_box('TVCS teal continuous facade band',(0,yy-.16,z),(W+.2,.11,.23),'teal')
  for x in [-W*.39,-W*.15,W*.15,W*.39]:b_box('TVCS upper small vent',(x,yy-.18,Z+3.21),(.62,.03,.36),'red')
 group('32_ARCHITECTURAL_SIGNS');b_text('TVCS current name','THIRUVANANTHAPURAM SOUTH',(0,-.25,Z+3.13),.28,'blue',W*.82)
elif arch=='kzk_entry':
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 # Taller centre facade, broad shade and distinctive triple ventilation above the open portal.
 b_box('KZK horizontal concrete rain shade',(0,-.5,Z+2.85),(W,.88,.18),'ivory')
 for x in [-W*.36,0,W*.36]:
  b_box('KZK high clerestory recess',(x,-.15,Z+3.29),(1.8,.06,.32),'dark')
  for dx in [-.60,0,.60]:b_box('KZK clerestory mullion',(x+dx,-.19,Z+3.29),(.045,.035,.31),'red')
 for x in [-.8,0,.8]:
  for j in range(5):b_box('KZK triple louvered vent',(x,-.18,Z+2.42+j*.075),(.71,.11,.031),'ivory')
 # Dated facade panel dimensions reconstructed; visible checker entry represented geometrically.
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED')
 for ix in range(-8,9):
  for iy in range(1,10):b_box('KZK red cream checker floor',(ix*.42,iy*.42,Z+.114),(.415,.415,.023),'red' if (ix+iy)%2 else 'ivory')
 group('32_ARCHITECTURAL_SIGNS');b_box('KZK high yellow trilingual sign band',(0,-.19,Z+3.76),(min(W,22),.10,.50),'yellow');b_text('KZK English identity','KAZHAKUTTAM',(6.8,-.25,Z+3.76),.34,'dark',6.5)
 for x in [-3.3,3.3]:b_box('KZK sign panel divider',(x,-.253,Z+3.76),(.035,.015,.50),'dark')
 # Project verified Malayalam native outlines onto one fascia panel (other panel retains source font metadata).
 if native_names:
  native_letters(native_names[0][0],bp(-6.8,-.27,Z+3.76),6.3,.32)
elif arch=='tvcn_two_storey':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');h1=3.8;h2=3.25;upper=Z+h1
 b_box('TVCN full building ground slab',(0,H/2,Z-.10),(W,H,.30),'concrete')
 for yy in [0,H]:
  for a,b in [(-W/2,-2.3),(2.3,W/2)]:b_box('TVCN ground open-portal masonry',((a+b)/2,yy,Z+h1/2),(b-a,.26,h1),'cream')
  b_box('TVCN main portal header',(0,yy,Z+h1-.45),(4.6,.26,.9),'cream');b_box('TVCN full upper wall',(0,yy,upper+h2/2),(W,.25,h2),'cream')
 for x in [-W/2,W/2]:b_box('TVCN building endwall',(x,H/2,Z+(h1+h2)/2),(.26,H,h1+h2),'cream')
 for x in [-W/2+4+j*8 for j in range(int((W-8)/8)+1)]:
  for dx in [-1.0,1.0]:b_window(x+dx,-.16,upper+1.35,1.35,1.60)
  # Small red tiled awnings over each upper window pair.
  mesh('TVCN upper window tiled awning',[bp(x-2.35,-.16,upper+2.35),bp(x+2.35,-.16,upper+2.35),bp(x-2.55,-1.05,upper+2.04),bp(x+2.55,-1.05,upper+2.04)],[(0,1,3,2)],M['terracotta'])
 for j in range(int(W/4)+1):
  x=-W/2+j*W/int(W/4);b_box('TVCN slender verandah dark post',(x,-3.3,Z+1.73),(.09,.11,3.46),'dark')
 group('31_ROOFS_REMOVABLE');v=[bp(-W/2-.4,-.1,Z+3.84),bp(W/2+.4,-.1,Z+3.84),bp(-W/2-.4,-3.8,Z+3.42),bp(W/2+.4,-3.8,Z+3.42)];mesh('TVCN continuous tiled verandah',v,[(0,1,3,2)],M['terracotta'])
 for j in range(int(W/.27)):
  x=-W/2+j*.27;b_beam('TVCN verandah tile ridges',(x,-.1,Z+3.86),(x,-3.8,Z+3.44),.024,'terracotta')
 b_box('TVCN yellow upper band',(0,-.16,upper+h2),(W+.3,.17,.30),'yellow')
 # Huge dark elevated weather roof separate from occupied concrete building.
 top=upper+h2+1.2;ridge=top+H*.22
 for x in [-W/2+j*8 for j in range(int(W/8)+1)]:
  for yy in [-.1,H+.1]:b_box('TVCN elevated overroof stanchion',(x,yy,upper+h2+.6),(.11,.11,1.2),'steel')
 v=[bp(-W/2-.9,-1,top),bp(W/2+.9,-1,top),bp(-W/2-.9,H/2,ridge),bp(W/2+.9,H/2,ridge),bp(-W/2-.9,H+1,top),bp(W/2+.9,H+1,top)];mesh('TVCN large dark metal over-roof',v,[(0,1,3,2),(2,3,5,4)],M['dark'])
 # Projecting tall triangular entrance canopy clearly visible in2024 photograph.
 cx=W*.24;cw=11;projection=15;canbase=Z+6.30;canridge=Z+10.10
 v=[bp(cx-cw/2,-1,canbase),bp(cx+cw/2,-1,canbase),bp(cx-cw/2,-projection,canbase),bp(cx+cw/2,-projection,canbase),bp(cx,-1,canridge),bp(cx,-projection,canridge)];mesh('TVCN monumental entrance canopy',v,[(0,2,5,4),(4,5,3,1)],M['dark'])
 for yy in [-1,-projection]:
  b_beam('TVCN entrance canopy triangle',(cx-cw/2,yy,canbase),(cx,yy,canridge),.07,'steel');b_beam('TVCN entrance canopy triangle',(cx,yy,canridge),(cx+cw/2,yy,canbase),.07,'steel');b_beam('TVCN entrance canopy lower tie',(cx-cw/2,yy,canbase),(cx+cw/2,yy,canbase),.065,'steel')
 for xx in [cx-cw/2,cx+cw/2]:b_box('TVCN entrance canopy post',(xx,-projection,Z+3.1),(.18,.18,6.2),'steel')
 # Navigable upper floor with a genuine stairwell in the far wing.
 group('36_TVCN_UPPER_INTERIOR_RECONSTRUCTED');sx=W*.39;sy=1.8;stairlen=7.0;holelo=sx-1.2;holehi=sx+1.2
 for a,b in [(-W/2,holelo),(holehi,W/2)]:b_box('TVCN upper floor around stairwell',((a+b)/2,H/2,upper-.10),(b-a,H,.20),'concrete')
 b_box('TVCN upper floor beyond stairwell',(sx,(sy+stairlen+H)/2,upper-.10),(2.4,H-sy-stairlen,.20),'concrete')
 for j in range(23):b_box('TVCN internal stair tread',(sx,sy+j*.30,Z+(j+1)*h1/23-.06),(2.15,.31,.12),'tile')
 for dx in [-1.07,1.07]:b_beam('TVCN internal stair handrail',(sx+dx,sy,Z+1),(sx+dx,sy+22*.30,upper+1),.03,'steel')
 for x in [-W*.35,-W*.16,W*.04,W*.22]:
  b_box('TVCN upper staff desk',(x,H*.55,upper+.78),(2.0,.85,.10),'wood');b_box('TVCN upper cabinet',(x,H-.45,upper+1.0),(1.1,.65,2),'concrete');xx,yy,_=bp(x,H*.35,0);bench(xx,yy,upper,0 if side>0 else math.pi);area('TVCN upper room light',bp(x,H*.5,upper+h2-.2),280,4)
 group('32_ARCHITECTURAL_SIGNS');b_box('TVCN front name panel',(0,-.20,upper-.4),(25,.14,.55),'yellow');b_text('TVCN main-entry current name','THIRUVANANTHAPURAM NORTH',(0,-.30,upper-.4),.34,'dark',24)
 # Planted forecourt islands and ramp rails are geometry, not the reference image.
 group('40_FORECOURT_AND_LANDSCAPE')
 for x in [bx-W*.40,bx+W*.42]:
  yy=build_front+side*12;box('TVCN raised forecourt planter',(x,yy,.14),(4.3,2,.70),'ivory');box('TVCN planter earth',(x,yy,.50),(3.95,1.7,.10),'soil');broadleaf_tree(x,yy,7,3.2)
elif arch=='kxp_bungalow':
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 # Photographed white projecting front gable above the entrance.
 gwidth=5.3;eave=Z+height;ridge=eave+1.6
 mesh('KXP front triangular white gable',[bp(-gwidth/2,-.27,eave),bp(gwidth/2,-.27,eave),bp(0,-.27,ridge)],[(0,1,2)],M['ivory'])
 b_box('KXP dark gable vent',(0,-.30,eave+.61),(.75,.045,.46),'dark')
 group('31_ROOFS_REMOVABLE');vs=[bp(-gwidth/2-.2,-.65,eave),bp(gwidth/2+.2,-.65,eave),bp(-gwidth/2-.2,H*.45,eave+1),bp(gwidth/2+.2,H*.45,eave+1),bp(0,-.65,ridge+.10),bp(0,H*.45,ridge+.8)];mesh('KXP crossing tiled gable roof',vs,[(0,2,5,4),(4,5,3,1)],M['terracotta'])
 group('37_KXP_ANNEX_RECONSTRUCTED');ax=-W/2-3;aw=6;ad=7;ah=4.4
 b_box('KXP flat annex floor',(ax,ad/2,Z+.01),(aw,ad,.13),'tile')
 for x in [ax-aw/2,ax+aw/2]:b_box('KXP annex sidewall',(x,ad/2,Z+ah/2),(.2,ad,ah),'ivory')
 b_box('KXP annex backwall',(ax,ad,Z+ah/2),(aw,.2,ah),'ivory')
 for a,b in [(ax-aw/2,ax-.7),(ax+.7,ax+aw/2)]:b_box('KXP annex door flank',((a+b)/2,0,Z+ah/2),(b-a,.2,ah),'ivory')
 b_box('KXP annex door header',(ax,0,Z+(2.35+ah)/2),(1.4,.2,ah-2.35),'ivory');b_box('KXP annex flat roof',(ax,ad/2,Z+ah),(aw+.3,ad+.3,.2),'ivory')
 b_box('KXP annex office desk',(ax,ad*.60,Z+.76),(1.9,.8,.09),'wood');b_box('KXP annex cabinet',(ax+1.7,ad-.4,Z+1),(.8,.6,2),'concrete');area('KXP annex room light',bp(ax,ad/2,Z+ah-.2),200,3)
 # Distinctive pale fabricated bridge with red feet and deep under-deck girders.
 for key in list(batches):
  if key[0]=='23_FOOTBRIDGE_RECONSTRUCTED' and key[2]=='blue':batches[(key[0],key[1],'ivory')]=batches.pop(key)
 if bridge_x is not None:
  group('23_FOOTBRIDGE_RECONSTRUCTED');pys=[pfmid(p,bridge_x) for p in D['platforms']];ya,yb=min(pys)-1,max(pys)+1
  for xx in [bridge_x-1.15,bridge_x+1.15]:box('KXP deep rectangular bridge girder',(xx,(ya+yb)/2,7.48),(.25,yb-ya,.64),'ivory')
  for yy in pys:
   for xx in [bridge_x-.95,bridge_x+.95]:
    box('KXP bridge red foot',(xx,yy,Z+.17),(.45,.47,.34),'red')
    # Paired members and diagonal ties leave the characteristic long open cut-outs.
    for dx in [-.17,.17]:box('KXP fabricated pier chord',(xx+dx,yy,4.30),(.09,.18,6.65),'ivory')
    for z in [1.7,3.6,5.5]:beam('KXP pier diagonal',(xx-.17,yy,z),(xx+.17,yy,z+1.6),.034,'ivory')
 broadleaf_tree(bx-W*.70,build_front+side*9,9,4.6)
elif arch=='tvp_long_red':
 # Long, low platform veranda and bright-red metal roof distinguish Pettah from generic station kits.
 for key in list(batches):
  if key[0]=='30_BUILDING_ENVELOPE_PHOTO_INFORMED' and key[1].startswith('Verandah column'):batches[(key[0],key[1],'yellow')]=batches.pop(key)
 group('38_TVP_PLATFORM_VERANDA')
 for x in [-W/2+j*4 for j in range(int(W/4)+1)]:
  b_box('TVP golden platform column',(x,H+2.6,Z+height/2),(.20,.22,height),'yellow');b_box('TVP platform column base',(x,H+2.6,Z+.16),(.27,.28,.32),'ivory')
 b_box('TVP continuous platform veranda floor',(0,H+1.5,Z-.015),(W,3.0,.14),'tile')
 # Roof surface rises from the platform eave to the existing ridge; side hips soften both ends.
 roofz=Z+height+.10;ridge=roofz+H*.25;v=[bp(-W/2-.5,H+3.1,roofz),bp(W/2+.5,H+3.1,roofz),bp(-W/2+3,H/2,ridge),bp(W/2-3,H/2,ridge)];mesh('TVP long red platform roof',v,[(0,1,3,2)],M['red'])
 for x in [-W/2+j*.18 for j in range(int(W/.18))]:b_beam('TVP red corrugated roof seam',(x,H+3.1,roofz+.018),(x,H/2,ridge+.018),.020,'red')
 # Recolour the inherited main roof surface, but retain architectural roof geometry.
 for o in list(collections.get('31_ROOFS_REMOVABLE',[]).objects if '31_ROOFS_REMOVABLE' in collections else []):
  if o.name.startswith('Pitched traditional station roof'):o.data.materials.clear();o.data.materials.append(M['red'])
 for key in list(batches):
  if key[0]=='31_ROOFS_REMOVABLE' and key[1]=='Terracotta tile course relief':batches[(key[0],key[1],'red')]=batches.pop(key)
 for xx in [-30,-18,18,30]:
  b_box('TVP passenger wing partition',(xx,H*.64,Z+1.4),(.12,H*.70,2.8),'cream');xw,yw,_=bp(xx+5,H*.55,0);bench(xw,yw,Z,0 if side>0 else math.pi)
  b_box('TVP room luggage rack',(xx+3,H-.5,Z+1.7),(3,.6,.07),'steel')
 broadleaf_tree(bx+5,build_back-side*3,6.2,3.7)
elif arch=='bram_corbel':
 clear_groups(['31_ROOFS_REMOVABLE']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 h=Z+height
 b_box('BRAM projecting deep eave slab',(0,H/2,h+.15),(W+1.3,H+1.3,.25),'ivory')
 for yy in [-.62,H+.62]:
  b_box('BRAM red brick-pattern fascia',(0,yy,h+.58),(W+1.3,.12,.68),'red')
  for z in [h+.19,h+.97]:b_box('BRAM turquoise fascia border',(0,yy-.05,z),(W+1.4,.10,.16),'teal')
  for j in range(int(W/.50)):
   x=-W/2+j*.5
   for k in range(3):b_box('BRAM fascia brick mortar',(x+(k%2)*.25,yy-.075,h+.34+k*.20),(.46,.01,.010),'ivory')
 for x in [-W/2+.2,W/2-.2]:
  for yy in [0,H]:
   for j in range(5):
    # Stepped corbel silhouette supported from wall, with yellow square end faces.
    dep=.34+(4-j)*.22;zz=h-.16-j*.25;b_box('BRAM stepped white corbel',(x,yy-side*dep*.5,zz),(.30,dep,.25),'ivory');b_box('BRAM corbel yellow end',(x,yy-side*dep,zz),(.30,.027,.25),'yellow')
 b_box('BRAM turquoise entrance hood',(0,-.64,Z+2.7),(3.7,1.5,.22),'teal')
 for j in range(6):b_box('BRAM yellow entrance louvers',(1.5,-.1,Z+1.0+j*.25),(.62,.22,.065),'yellow')
 group('31_ROOFS_REMOVABLE');b_box('BRAM flat occupied roof',(0,H/2,h+.10),(W,H,.20),'concrete');roofz=h+2.0
 for x in [-W/2+.4,W/2-.4]:
  for yy in [0,H]:b_box('BRAM outer overroof steel support',(x,yy,h+1.15),(.10,.10,1.8),'dark')
 mesh('BRAM large independent grey over-roof',[bp(-W/2-1,-1,roofz),bp(W/2+1,-1,roofz),bp(-W/2-1,H/2,roofz+1.3),bp(W/2+1,H/2,roofz+1.3),bp(-W/2-1,H+1,roofz),bp(W/2+1,H+1,roofz)],[(0,1,3,2),(2,3,5,4)],M['roof'])
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED');x=counter_x;y=counter_y-.18
 b_box('BRAM maroon double ticket surround',(x,y,Z+1.76),(2.3,.08,1.75),'red')
 for xx in [x-.58,x+.58]:
  b_box('BRAM pale ticket grille backing',(xx,y-.07,Z+1.34),(.99,.03,.93),'dark')
  for k in range(10):b_box('BRAM fine pale wire grid',(xx-.45+k*.10,y-.09,Z+1.35),(.016,.014,.92),'ivory')
  for k in range(9):b_box('BRAM fine pale wire grid',(xx,y-.10,Z+.93+k*.10),(.94,.014,.014),'ivory')
  for j in range(13):
   a=j*math.pi/12;b_beam('BRAM arched ticket cutout trim',(xx+.16*math.cos(a),y-.13,Z+1.0+.18*math.sin(a)),(xx+.16*math.cos(min(math.pi,a+math.pi/12)),y-.13,Z+1.0+.18*math.sin(min(math.pi,a+math.pi/12))),.023,'red')
 b_box('BRAM navy ticket counter sign',(x-.50,y-.10,Z+2.23),(1.15,.08,.40),'blue');b_text('BRAM ticket sign','TICKET COUNTER',(x-.50,y-.16,Z+2.23),.14,'white',1.05)
elif arch=='veli_service':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS','33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED','21_PLATFORM_SHELTERS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');h=2.9
 b_box('VELI modest service block floor',(0,H/2,Z+.03),(W,H,.12),'tile')
 for yy in [0,H]:
  for a,b in [(-W/2,-.65),(.65,W/2)]:b_box('VELI white wall with door',((a+b)/2,yy,Z+1.2),(b-a,.18,2.4),'ivory')
  b_box('VELI low door lintel',(0,yy,Z+2.32),(1.3,.18,.22),'ivory')
  for x in [-W/2+j*W/6 for j in range(7)]:b_box('VELI high vent pier',(x,yy,Z+2.65),(.15,.20,.50),'ivory')
 for x in [-W/2,W/2]:b_box('VELI solid short service wall',(x,H/2,Z+1.45),(.18,H,2.9),'ivory')
 group('31_ROOFS_REMOVABLE');b_box('VELI flat projecting weathered roof',(0,H/2,Z+3.0),(W+.70,H+.75,.20),'concrete')
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED');b_box('VELI service storage shelf',(W*.28,H-.40,Z+1.20),(2.0,.65,.08),'wood');b_box('VELI closed utility cabinet',(-W*.28,H-.42,Z+1),(.9,.64,2.0),'concrete')
 for z in [Z+.6,Z+1.1,Z+1.6]:b_box('VELI cabinet pull',(-W*.28,H-.75,z),(.16,.03,.025),'steel')
 b_box('VELI small work bench',(W*.20,H*.58,Z+.78),(1.7,.7,.08),'wood');b_box('VELI service ledger',(W*.20,H*.58,Z+.84),(.35,.27,.025),'ivory')
 xx,yy,_=bp(-W*.20,H*.30,0);bench(xx,yy,Z);light(xx,yy,Z+2.70);area('VELI service room lamp',bp(0,H/2,Z+2.7),150,2)
 # Verified existing butterfly canopy: central V trough and outer high eaves, one central row.
 group('21_PLATFORM_SHELTERS');pf=D['platforms'][0];cx=-100;x0=cx-22;x1=cx+22;width=4.0
 for x in range(x0,x1+1,6):
  y=pfmid(pf,x);box('VELI blue central canopy column',(x,y,Z+1.65),(.18,.22,3.3),'blue');box('VELI flared canopy column footing',(x,y,Z+.22),(.42,.48,.44),'concrete')
  for sg in [-1,1]:beam('VELI butterfly cantilever',(x,y,Z+3.24),(x,y+sg*width/2,Z+3.93),.050,'blue');beam('VELI canopy knee brace',(x,y,Z+2.55),(x,y+sg*width*.35,Z+3.73),.035,'blue')
 for j in range(int((x1-x0)/.16)):
  x=x0+j*.16;y=pfmid(pf,x);yn=pfmid(pf,x+.16);off=.022 if j%2 else -.022;vs=[(x,y-width/2,Z+3.96+off),(x,y,Z+3.28+off),(x,y+width/2,Z+3.96+off),(x+.16,yn-width/2,Z+3.96-off),(x+.16,yn,Z+3.28-off),(x+.16,yn+width/2,Z+3.96-off)];key=(active.name,'VELI actual V-profile canopy sheets','roof');v,f=batches.setdefault(key,([],[]));k=len(v);v.extend(vs);f.extend([(k,k+1,k+4,k+3),(k+1,k+2,k+5,k+4)])
 # September2026 opposite strip is visible geometry with explicitly unverified use.
 group('24_VELI_OPPOSITE_RAISED_STRIP_STATUS_UNVERIFIED');far=max(D['ways'],key=lambda w:sample(w['xy'],-110))
 for x in range(-245,25,5):
  y0=sample(far['xy'],x)+3.0;y1=sample(far['xy'],x+5)+3.0;ang=math.atan2(y1-y0,5);le=math.hypot(5,y1-y0);box('Opposite raised strip uncertain construction status',(x+2.5,(y0+y1)/2,.32),(le,2.3,1.0),'concrete',ang);box('Opposite strip flat tan top',(x+2.5,(y0+y1)/2,.833),(le,2.3,.035),'soil',ang)
 group('40_FORECOURT_AND_LANDSCAPE');bb=pfbounds(pf)
 for x in range(math.ceil(bb[0]),math.floor(bb[2]),1):
  if abs(x-bx)<W/2+2:continue
  sec=pfsect(pf,x)
  if sec:
   yy=sec[0]-.65;box('VELI cream rear picket',(x,yy,Z+.60),(.055,.055,1.2),'ivory')
   if x%5==0:box('VELI red rear fence pier',(x,yy,Z+.66),(.15,.15,1.32),'red')
 broadleaf_tree(bx-7,by+side*6,8.4,4.5)
elif arch=='amva_corrugated':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS','33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');ht=2.8
 b_box('AMVA modest hut floor',(0,H/2,Z+.02),(W,H,.12),'tile')
 for yy in [0,H]:
  for a,b in [(-W/2,-.60),(.60,W/2)]:
   sheet_wall('AMVA ochre corrugated base',a,b,yy,Z,Z+.35,'yellow');sheet_wall('AMVA weathered white corrugated band',a,b,yy,Z+.35,Z+1.75,'ivory');sheet_wall('AMVA ochre corrugated upper wall',a,b,yy,Z+1.75,Z+ht,'yellow')
  sheet_wall('AMVA doorway sheet header',-.60,.60,yy,Z+2.20,Z+ht,'yellow')
 for x in [-W/2,W/2]:
  b_box('AMVA cream endwall',(x,H/2,Z+ht/2),(.08,H,ht),'ivory');b_box('AMVA ochre endwall top',(x,H/2,Z+2.3),(.09,H,1.0),'yellow')
 # Source-facing hatch, sign and concrete bench on the platform side.
 b_box('AMVA maroon closed hatch',(W*.30,H+.055,Z+1.50),(1.3,.08,1.20),'red');b_box('AMVA front cast concrete bench',(-W*.25,H+.38,Z+.39),(3.15,.65,.13),'concrete')
 for x in [-W*.39,-W*.1]:b_box('AMVA concrete bench legs',(x,H+.38,Z+.18),(.21,.45,.36),'ivory')
 group('31_ROOFS_REMOVABLE');roofz=Z+ht+.08
 for j in range(int((W+.7)/.15)):
  x=-W/2-.35+j*.15;zoff=.025 if j%2 else -.025;mesh('AMVA shallow corrugated roof strip',[bp(x,-.50,roofz+.32+zoff),bp(x+.15,-.50,roofz+.32-zoff),bp(x+.15,H+.55,roofz-zoff),bp(x,H+.55,roofz+zoff)],[(0,1,2,3)],M['dark'])
 group('32_ARCHITECTURAL_SIGNS');b_box('AMVA yellow wall sign',(-W*.25,H+.08,Z+2.27),(3.05,.08,.70),'yellow');text('AMVA English fascia','AMARAVILA',bp(-W*.25,H+.13,Z+2.14),.26,'dark',2.9,rot=(math.pi/2,0,0) if side>0 else (math.pi/2,0,math.pi));b_box('AMVA paper train timetable',(0,H+.08,Z+2.54),(1.12,.055,.65),'ivory')
 for j in range(9):b_box('AMVA timetable printed rows',(0,H+.12,Z+2.79-j*.057),(.95,.009,.010),'dark')
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED');b_box('AMVA clerk desk',(-1.9,H*.67,Z+.77),(2.25,.85,.10),'wood');b_box('AMVA ticket cash box',(-2.3,H*.65,Z+.94),(.45,.35,.26),'dark');b_box('AMVA paper ledger',(-1.45,H*.62,Z+.85),(.40,.30,.035),'ivory')
 for x in [-2.85,-.95]:b_box('AMVA desk legs',(x,H*.67,Z+.38),(.06,.06,.76),'steel')
 xx,yy,_=bp(1.9,H*.55,0);bench(xx,yy,Z);xx,yy,_=bp(0,H*.5,0);fan(xx,yy,Z+2.45);light(xx,yy,Z+2.65);area('AMVA ticket hut light',(xx,yy,Z+2.6),140,2)
 # Small photographed detached sanitary block, with reconstructed single cubicle inside.
 group('34_STAFF_TOILET_SERVICE_RECONSTRUCTED');tx=bx+W/2+3.0;ty=by;tw=2.4;td=2.2
 box('AMVA toilet floor',(tx,ty,Z+.015),(tw,td,.15),'concrete')
 for x in [tx-tw/2,tx+tw/2]:box('AMVA toilet sidewall',(x,ty,Z+1.35),(.15,td,2.7),'ivory')
 box('AMVA toilet rear wall',(tx,ty+side*td/2,Z+1.35),(tw,.15,2.7),'ivory');box('AMVA toilet front right',(tx+.45,ty-side*td/2,Z+1.35),(1.5,.15,2.7),'ivory');box('AMVA toilet door lintel',(tx-.74,ty-side*td/2,Z+2.52),(.85,.15,.36),'ivory');box('AMVA toilet flat roof',(tx,ty,Z+2.80),(tw+.4,td+.4,.18),'ivory');box('AMVA ochre roof edge',(tx,ty-side*(td/2+.2),Z+2.87),(tw+.4,.13,.20),'yellow');cyl('AMVA black rooftop water tank',(tx+.5,ty,Z+3.20),.43,.65,'dark',24)
 cyl('AMVA WC pedestal',(tx+.5,ty+.3,Z+.22),.17,.42,'white');cyl('AMVA WC bowl',(tx+.5,ty+.25,Z+.48),.28,.12,'white',20);box('AMVA WC cistern',(tx+.5,ty+.75,Z+.87),(.45,.18,.58),'white');area('AMVA toilet light',(tx,ty,Z+2.60),100,1.2)
 broadleaf_tree(bx-W*.65,by+side*5,7.5,3.7)
elif arch=='pyd_lattice':
 clear_groups(['31_ROOFS_REMOVABLE','21_PLATFORM_SHELTERS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for key in list(batches):
  if key[0]=='30_BUILDING_ENVELOPE_PHOTO_INFORMED' and key[1].startswith(('Verandah column','Verandah fascia')):del batches[key]
 b_box('PYD turquoise projecting fascia',(0,-.4,Z+3.15),(W+.8,.78,.35),'teal')
 for x in [-W/2+.12,W/2-.12]:
  for yy in [0,H]:
   for j in range(3):b_box('PYD stepped turquoise corner corbel',(x,yy-.1-j*.10,Z+2.86-j*.20),(.25,.65-j*.15,.20),'teal')
 group('31_ROOFS_REMOVABLE');b_box('PYD small flat hut roof',(0,H/2,Z+3.14),(W+.7,H+.6,.18),'ivory')
 group('21_PLATFORM_SHELTERS');pf=D['platforms'][0];cx=bx;x0=cx-18;x1=cx+18;wy=pfmid(pf,cx)
 for x in range(int(x0),int(x1)+1,8):
  y=pfmid(pf,x);box('PYD turquoise heavy canopy pedestal',(x,y,Z+.20),(.95,.85,.40),'teal');box('PYD galvanized bolted footplate',(x,y,Z+.46),(.70,.65,.13),'steel')
  for dx in [-.22,.22]:
   box('PYD open lattice upright',(x+dx,y,Z+2.68),(.10,.18,4.35),'steel')
   for dy in [-.21,.21]:cyl('PYD footplate bolt',(x+dx,y+dy,Z+.56),.034,.08,'steel',10)
  for z in [Z+.8,Z+1.7,Z+2.6,Z+3.5]:beam('PYD lattice diagonal',(x-.22,y,z),(x+.22,y,z+.84),.037,'steel')
  for sg in [-1,1]:beam('PYD canopy long knee brace',(x,y,Z+3.0),(x,y+sg*3.3,Z+4.75),.055,'steel')
 for j in range(int((x1-x0)/.17)):
  x=x0+j*.17;y=pfmid(pf,x);yn=pfmid(pf,x+.17);off=.025 if j%2 else -.025;mesh('PYD high corrugated canopy sheet',[(x,y-3.6,Z+4.8+off),(x+.17,yn-3.6,Z+4.8-off),(x+.17,yn+3.6,Z+5.0-off),(x,y+3.6,Z+5.0+off)],[(0,1,2,3)],M['roof'])
 # Dated2026 footbridge is physical; its opposite landing is not an operational platform claim.
 if bridge_x is not None:
  group('23_FOOTBRIDGE_RECONSTRUCTED');pys=[f['y'] for f in bridge_data];ya,yb=min(pys)-1,max(pys)+1
  for key in list(batches):
   if key[0]=='23_FOOTBRIDGE_RECONSTRUCTED' and key[1]=='Bridge truss web':del batches[key]
   elif key[0]=='23_FOOTBRIDGE_RECONSTRUCTED' and key[2]=='blue':batches[(key[0],key[1],'ivory')]=batches.pop(key)
  box('PYD bridge red tile walkway',(bridge_x,(ya+yb)/2,8.025),(2.57,yb-ya,.025),'red')
  for dx in [-.84,.84]:box('PYD bridge cream longitudinal border',(bridge_x+dx,(ya+yb)/2,8.043),(.21,yb-ya,.01),'ivory')
  group('24_PYD_OPPOSITE_LANDING_STATUS_UNVERIFIED');far=pys[-1];box('PYD opposite constructed landing',(bridge_x+8,far,.73),(21,4.2,.44),'concrete')
 group('40_FORECOURT_AND_LANDSCAPE');broadleaf_tree(bx-W*.8,by+side*6,7.5,3.5)
elif arch=='kztw_three_bay':
 clear_groups(['30_BUILDING_ENVELOPE_PHOTO_INFORMED','31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS','33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED');ht=2.95
 b_box('KZTW compact block floor',(0,H/2,Z+.025),(W,H,.12),'tile')
 for x in [-W/2,W/2]:b_box('KZTW short cream side wall',(x,H/2,Z+ht/2),(.18,H,ht),'ivory')
 # Three real door bays on platform side, middle left open for the reconstructed circulation.
 for a,b in [(-W/2,-3.55),(-2.45,-.55),(.55,2.45),(3.55,W/2)]:b_box('KZTW three-bay facade pier',((a+b)/2,H,Z+ht/2),(b-a,.18,ht),'ivory')
 for x in [-3,0,3]:
  b_box('KZTW doorway lintel',(x,H,Z+2.52),(1.1,.18,.85),'ivory');b_box('KZTW high vent recess',(x,H+.10,Z+2.64),(.60,.025,.28),'dark')
  for dx in [-.20,0,.20]:b_box('KZTW high vent bars',(x+dx,H+.13,Z+2.64),(.028,.025,.28),'ivory')
  if x: b_box('KZTW closed side-bay door',(x,H+.04,Z+1.10),(1.06,.06,2.2),'blue' if x<0 else 'red')
 for a,b in [(-W/2,-.6),(.6,W/2)]:b_box('KZTW rear wall opening',((a+b)/2,0,Z+ht/2),(b-a,.18,ht),'ivory')
 b_box('KZTW rear lintel',(0,0,Z+2.57),(1.2,.18,.76),'ivory')
 group('31_ROOFS_REMOVABLE');b_box('KZTW flat roof slab',(0,H/2,Z+3.03),(W+.60,H+.55,.18),'ivory')
 for yy in [-.27,H+.27]:
  b_box('KZTW broad yellow roof fascia',(0,yy,Z+3.19),(W+.6,.10,.26),'yellow');b_box('KZTW yellow projecting low eave',(0,yy,Z+2.26),(W+.65,.50,.13),'yellow')
 cyl('KZTW black water tank',bp(W*.25,H*.60,Z+3.58),.43,.67,'dark',24)
 group('33_FURNISHED_PUBLIC_INTERIOR_RECONSTRUCTED')
 for xx in [-1.5,1.5]:
  for a,b in [(0,1.3),(2.8,H)]:b_box('KZTW interior room partition',(xx,(a+b)/2,Z+1.4),(.10,b-a,2.8),'cream')
  b_box('KZTW internal doorway lintel',(xx,2.05,Z+2.50),(.10,1.5,.60),'cream')
 b_box('KZTW inferred staff desk',(-3,H*.65,Z+.75),(1.7,.70,.10),'wood');b_box('KZTW inferred storage cabinet',(3,H-.40,Z+1),(.95,.60,2),'concrete')
 for xx in [-3,3]:
  area('KZTW modest room light',bp(xx,H/2,Z+2.7),120,2);b_box('KZTW simple external bench',(xx,H+.55,Z+.39),(2.3,.6,.13),'yellow')
  for dx in [-.80,.80]:b_box('KZTW bench concrete leg',(xx+dx,H+.55,Z+.18),(.17,.45,.36),'ivory')
 group('35_BUILDING_ACCESS');b_box('KZTW rear landing',(0,-1.8,Z-.015),(W,3.6,.14),'tile')
 group('40_FORECOURT_AND_LANDSCAPE');pf=D['platforms'][0];pb=pfbounds(pf)
 for x in range(math.ceil(pb[0]+8),math.floor(pb[2]-8)):
  if abs(x-bx)<W/2+2:continue
  sec=pfsect(pf,x)
  if not sec:continue
  y=sec[0]-.65;box('KZTW white picket',(x,y,Z+.56),(.055,.055,1.12),'ivory')
  if x%5==0:box('KZTW red fence pier',(x,y,Z+.60),(.14,.14,1.2),'red')
 broadleaf_tree(bx+W*.9,by+side*5.5,7,3.5)
elif arch=='mqu_louvers':
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 # Source-specific golden facade, low parapet, tall shutters and striped waist course.
 for yy in [0,H]:
  for zz,hh in [(Z+1.15,.22),(Z+1.45,.10)]:b_box('MQU orange horizontal wall band',(0,yy-.15,zz),(W,.07,hh),'terracotta')
 for x in [-W*.39,-W*.24,-W*.10,W*.10,W*.24,W*.39]:
  b_box('MQU tall louver window recess',(x,-.18,Z+1.73),(1.8,.08,2.2),'dark')
  for j in range(14):b_box('MQU yellow long louver',(x,-.24,Z+.74+j*.145),(1.76,.15,.046),'yellow')
  for dx in [-.88,0,.88]:b_box('MQU louver vertical frame',(x+dx,-.25,Z+1.72),(.065,.08,2.24),'ivory')
 for x in [-W/2,-W*.3,-W*.1,W*.1,W*.3,W/2]:b_box('MQU square frontage pilaster',(x,-.22,Z+1.85),(.27,.24,3.7),'cream')
 # Dark-red shutters on platform side, detailed as wood panels and louvered transoms.
 for x in [-W*.35,W*.35]:
  b_box('MQU maroon platform shutter',(x,H+.10,Z+1.65),(1.7,.08,2.05),'red')
  for dx in [-.48,.48]:
   for zz in [Z+1.15,Z+1.80]:b_box('MQU raised shutter panel',(x+dx,H+.15,zz),(.65,.035,.45),'wood')
  for j in range(7):b_box('MQU shutter upper louver',(x,H+.15,Z+2.43+j*.045),(1.65,.07,.022),'dark')
 group('31_ROOFS_REMOVABLE');roofz=Z+4.12;ridge=roofz+1.15
 mesh('MQU red rear weather roof',[bp(-W/2,1.0,roofz),bp(W/2,1.0,roofz),bp(-W/2,H*.55,ridge),bp(W/2,H*.55,ridge),bp(-W/2,H+.45,roofz),bp(W/2,H+.45,roofz)],[(0,1,3,2),(2,3,5,4)],M['red'])
 group('39_MQU_POTTED_PLATFORM_VERANDA');b_box('MQU red-grid platform veranda',(0,H+.65,Z+.03),(W,1.3,.10),'red')
 for x in [-W/2+1+j*2.0 for j in range(int((W-2)/2))]:
  if abs(x)<2:continue
  px,py,_=bp(x,H+.60,0);mt=random.choice(['teal','blue','red','yellow']);cyl('MQU colored flowerpot',(px,py,Z+.29),.22,.50,mt,14);cyl('MQU pot rim',(px,py,Z+.55),.245,.06,mt,14);cyl('MQU planter earth',(px,py,Z+.56),.205,.025,'soil',14)
  for j in range(6):
   a=j*math.tau/6;tip=(px+math.cos(a)*.36,py+math.sin(a)*.36,Z+random.uniform(.9,1.35));beam('MQU leafy plant stem',(px,py,Z+.58),tip,.010,'green');mesh('MQU plant leaves',[(tip[0],tip[1],tip[2]),(tip[0]+.12,tip[1]+.08,tip[2]-.13),(px,py,Z+.68),(tip[0]-.08,tip[1]-.08,tip[2]-.16)],[(0,1,2),(0,2,3)],M['green'])
 # Additional small stationmaster operating rack visible in the dated reference; exact fitout inferred.
 group('34_STAFF_TOILET_SERVICE_RECONSTRUCTED');x=-W*.35;b_box('MQU operations equipment rack',(x,H-.48,Z+1.10),(1.6,.65,2.15),'dark')
 for j in range(6):
  b_box('MQU rack panel',(x,H-.84,Z+.34+j*.27),(1.5,.025,.22),'concrete')
  for dx in [-.45,0,.45]:b_box('MQU green status indicator',(x+dx,H-.86,Z+.35+j*.27),(.09,.013,.04),'green')
 group('32_ARCHITECTURAL_SIGNS');b_text('MQU high street identity','MURUKKAMPUZHA',(0,-.30,Z+4.11),.32,'dark',W*.6)
elif arch=='nyy_yellow_portico':
 clear_groups(['32_ARCHITECTURAL_SIGNS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for key in list(batches):
  if key[0]=='30_BUILDING_ENVELOPE_PHOTO_INFORMED' and key[1].startswith(('Verandah column','Verandah fascia')):del batches[key]
 # Broad portico with the photographed yellow stair-stepped brackets and slender round columns.
 b_box('NYY broad portico concrete canopy',(0,-2.0,Z+3.75),(10.7,4.3,.28),'ivory')
 b_box('NYY weathered turquoise fascia',(0,-4.15,Z+3.95),(10.7,.22,.34),'teal')
 mesh('NYY shallow sloped portico cap',[bp(-5.35,-4.28,Z+4.04),bp(5.35,-4.28,Z+4.04),bp(-5.35,-1.0,Z+4.48),bp(5.35,-1.0,Z+4.48)],[(0,1,3,2)],M['teal'])
 for sg in [-1,1]:
  for j in range(6):
   ww=(6-j)*.32;x=sg*(4.72-ww/2);b_box('NYY yellow stepped corbel',(x,-3.10,Z+3.51-j*.24),(ww,.72,.24),'yellow')
  b_box('NYY yellow slender pilaster',(sg*4.55,-.18,Z+1.65),(.25,.24,3.30),'yellow');cyl('NYY white round entrance column',bp(sg*3.8,-3.0,Z+1.80),.11,3.60,'ivory',18)
  # Tiny turquoise pyramid hood over the side window.
  xx=sg*10;zz=Z+3.06;v=[bp(xx-1,-.25,zz),bp(xx+1,-.25,zz),bp(xx+1,-1.35,zz),bp(xx-1,-1.35,zz),bp(xx,-.65,zz+.45)];mesh('NYY small pyramidal window hood',v,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],M['teal'])
 group('32_ARCHITECTURAL_SIGNS');b_text('NYY portico name','NEYYATTINKARA',(0,-4.29,Z+3.88),.31,'blue',8.2)
 group('40_FORECOURT_AND_LANDSCAPE');broadleaf_tree(bx-W*.68,build_front+side*8,8.5,4.5)
elif arch=='pasa_pink_gable':
 clear_groups(['31_ROOFS_REMOVABLE','32_ARCHITECTURAL_SIGNS']);group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for key in list(batches):
  if key[0]=='30_BUILDING_ENVELOPE_PHOTO_INFORMED' and key[1].startswith(('Verandah column','Verandah fascia')):del batches[key]
 # Pink pilasters and long dark clerestory band identify the low right wing.
 for x in [-W/2,-W*.33,-W*.16,W*.16,W*.33,W/2]:b_box('PASA pale pink facade pilaster',(x,-.16,Z+1.7),(.27,.20,3.4),'cream')
 for x in [-W*.32,W*.32]:b_box('PASA long upper dark ventilation band',(x,-.15,Z+2.97),(W*.29,.04,.36),'dark')
 b_box('PASA raised central name wall',(0,-.15,Z+4.04),(14.0,.23,1.3),'ivory')
 group('31_ROOFS_REMOVABLE');eave=Z+3.50;ridge=eave+.72
 mesh('PASA shallow tiled wing roof',[bp(-W/2-.6,-.45,eave),bp(W/2+.6,-.45,eave),bp(-W/2-.6,H/2,ridge),bp(W/2+.6,H/2,ridge),bp(-W/2-.6,H+.4,eave),bp(W/2+.6,H+.4,eave)],[(0,1,3,2),(2,3,5,4)],M['terracotta'])
 for x in [-W/2+j*.26 for j in range(int(W/.26))]:
  b_beam('PASA wing tile ridge',(x,-.45,eave+.02),(x,H/2,ridge+.02),.022,'terracotta');b_beam('PASA wing tile ridge',(x,H/2,ridge+.02),(x,H+.4,eave+.02),.022,'terracotta')
 mesh('PASA small raised rear gable',[bp(-3.6,2,Z+4.40),bp(3.6,2,Z+4.40),bp(0,2,Z+5.05)],[(0,1,2)],M['ivory'])
 # Low projecting entrance gable covers only the actual central doorway zone.
 v=[bp(-4.2,-4.0,Z+2.93),bp(4.2,-4.0,Z+2.93),bp(-4.2,.15,Z+3.3),bp(4.2,.15,Z+3.3),bp(0,-4.0,Z+3.77),bp(0,.15,Z+4.15)];mesh('PASA tiled entrance portico roof',v,[(0,2,5,4),(4,5,3,1)],M['terracotta'])
 mesh('PASA portico cream triangular fascia',[bp(-4.2,-4.02,Z+2.93),bp(4.2,-4.02,Z+2.93),bp(0,-4.02,Z+3.77)],[(0,1,2)],M['ivory'])
 group('30_BUILDING_ENVELOPE_PHOTO_INFORMED')
 for x in [-3.7,3.7]:b_box('PASA portico square column',(x,-3.25,Z+1.48),(.33,.36,2.96),'ivory')
 group('32_ARCHITECTURAL_SIGNS');b_text('PASA raised name identity','PARASSALA',(0,-.30,Z+4.22),.51,'dark',12);b_box('PASA right-wing yellow station board',(W*.30,-.20,Z+2.05),(2.5,.07,.65),'yellow');b_text('PASA right-wing name','PARASSALA',(W*.30,-.25,Z+2.04),.22,'dark',2.35)
 for key in list(batches):
  if key[0]=='40_FORECOURT_AND_LANDSCAPE' and key[1]=='Station forecourt':batches[(key[0],key[1],'ballast')]=batches.pop(key)
 broadleaf_tree(bx-W*.66,build_front+side*9,9.5,5);broadleaf_tree(bx+W*.66,build_front+side*12,8.7,4.5)
# Bespoke replacements retain a continuous landing where the generic approach ramp/stairs end.
if arch in ['davm_ticket_shelter','veli_service','tvcn_two_storey','amva_corrugated']:
 group('35_BUILDING_ACCESS');b_box('Continuous bespoke approach landing',(0,-1.8,Z-.015),(W,3.6,.14),'tile')
