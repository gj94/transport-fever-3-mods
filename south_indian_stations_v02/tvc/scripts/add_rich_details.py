# Executed inside build_full_tvc.py namespace; every feature is editable geometry.
col('18_INTERIOR_OPERATIONAL_DETAIL_AND_WEATHERING')
# Individually varying terrazzo tiles, narrow grout, wear around circulation lines.
for cx,cy,w,d in [(-48,5.6,22.7,9.7),(-68,5.6,14.7,9.7),(41,5.6,14.7,9.7),(54,5.6,8.7,9.7),(113,3,45.7,19.7),(0,4,13.1,7.2)]:
 for i in range(int(w/.75)):
  for j in range(int(d/.75)):
   x=cx-w/2+(i+.5)*.75;y=cy-d/2+(j+.5)*.75
   box('Terrazzo floor tile variation',(x,y,.857),(.741,.741,.016),tile if random.random()>.2 else tile2)
 for x in [cx-w/2+.3,cx+w/2-.3]:
  box('Room wall skirting',(x,cy,1.03),(.12,d,.34),red)
 # Clock on rear wall. Dial + hands + ticks are actual geometry.
 x=cx+w*.31;y=cy+d/2-.19;z=3.65
 rod('Station wall clock rim',(x,y+.04,z),(x,y-.035,z),.34,dark,48);rod('Clock cream dial',(x,y-.038,z),(x,y-.045,z),.307,white,48)
 for k in range(12):
  a=k*math.tau/12;rod('Clock hour marks',(x+.255*math.sin(a),y-.049,z+.255*math.cos(a)),(x+.287*math.sin(a),y-.049,z+.287*math.cos(a)),.009,dark,6)
 rod('Clock minute hand',(x,y-.060,z),(x+.12,y-.060,z+.21),.010,dark,6);rod('Clock hour hand',(x,y-.065,z),(x-.15,y-.065,z+.03),.013,dark,6)
 # Surface conduits follow top of wall and drop only beside door jambs.
 rod('Interior surface electrical conduit',(cx-w/2+.2,cy+d/2-.20,4.35),(cx+w/2-.2,cy+d/2-.20,4.35),.020,steel)
 for xx in (cx-1.1,cx+1.1):
  rod('Switch drop conduit',(xx,cy-d/2+.19,4.3),(xx,cy-d/2+.19,1.8),.017,steel);box('Light switchboard',(xx,cy-d/2+.15,1.85),(.24,.07,.35),white)
  for k in range(3):box('Switch rocker',(xx-.07+k*.07,cy-d/2+.10,1.86),(.045,.018,.12),dark)
 box('Fire extinguisher wall bracket',(cx-w/2+.4,cy+1,1.3),(.10,.35,.65),dark)
 rod('Red fire extinguisher cylinder',(cx-w/2+.55,cy+1,1.05),(cx-w/2+.55,cy+1,1.65),.12,red,16)
 rod('Extinguisher neck',(cx-w/2+.55,cy+1,1.65),(cx-w/2+.55,cy+1,1.74),.045,steel,12)
 box('Extinguisher instruction label',(cx-w/2+.55,cy+.87,1.37),(.15,.022,.24),white)
 for k in range(5):box('Extinguisher printed lines',(cx-w/2+.55,cy+.854,1.31+k*.027),(.11,.009,.005),dark)
 # Noticeboard with individual clipped forms; original text, no commercial image reuse.
 nx=cx-w*.3;ny=cy+d/2-.20
 box('Framed passenger noticeboard',(nx,ny,3.05),(2.2,.12,1.35),wood);box('Noticeboard backing',(nx,ny-.07,3.05),(2.04,.04,1.20),teal)
 for ix in range(3):
  for iz in range(2):
   xx=nx-.65+ix*.65;zz=2.75+iz*.55;box('Pinned notice sheet',(xx,ny-.095,zz),(.52,.012,.44),paper)
   for k in range(6):box('Notice text strokes',(xx,ny-.105,zz+.12-k*.045),(.40,.004,.006),dark)
   rod('Notice pin',(xx,ny-.10,zz+.18),(xx,ny-.115,zz+.18),.013,red,8)
 # Frosted high-level vent and operating AC grille above rear room openings.
 box('Wall-mounted air conditioner',(cx,cy+d/2-.35,4.52),(1.8,.42,.35),white)
 for k in range(7):box('AC outlet louvres',(cx,cy+d/2-.58,4.40+k*.023),(1.5,.045,.012),dark)
# Platform P1 wall carries functional posters and passenger displays.
for x in range(-65,60,17):
 sign('EXIT  /  WAY OUT',(x,14.25,3.55),2.6,.6,size=.24)
 box('Electrical distribution locker',(x,13.8,1.70),(.65,.25,1.55),steel)
 for z in (1.3,1.6,1.9,2.2):box('Locker vent slit',(x,13.65,z),(.4,.015,.025),dark)
 rod('Locker earth wire',(x+.23,13.68,.86),(x+.23,13.68,2.40),.009,green,6)
# Original multilingual station boards, reused packed graphic, at both ends of each body.
col('19_TRILINGUAL_BOARDS_AND_PLATFORM_SIGNAGE')
im=bpy.data.images.load(str(R/'textures/TVC_trilingual_board.png'),check_existing=True);im.pack();m=bpy.data.materials.new('Original trilingual station name graphic');m.use_nodes=True;n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
for x,y in [(-237,19.5),(150,19.5),(-198,40.0),(202,40.0),(-181,59.0),(226,59.0)]:
 for xx in (x-2.85,x+2.85):box('Station board yellow leg',(xx,y,2.1),(.19,.21,2.5),yellow);box('Nameboard leg black base',(xx,y,1.13),(.21,.23,.6),dark)
 box('Thick yellow nameboard',(x,y,3.8),(6.0,.24,2.10),yellow)
 v=[(x-2.9,y-.132,2.82),(x+2.9,y-.132,2.82),(x+2.9,y-.132,4.78),(x-2.9,y-.132,4.78)];o=mesh('Trilingual TVC nameboard graphic',v,[(0,1,2,3)],m);uv=o.data.uv_layers.new(name='UVMap')
 for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=co
# Track-side telephone cabinets, cable loops, route markers and tool detail.
col('20_YARD_SMALL_OPERATIONAL_DETAILS')
for i,(nd,neighbours) in enumerate(adj.items()):
 if len(neighbours)<3:continue
 x,y=nodepos[nd]
 if abs(x)>700:continue
 box('Point identification plate',(x+1.6,y+2.5,.72),(.65,.05,.32),yellow)
 txt('Reconstructed point asset marker','P%02d'%(i%100),(x+1.6,y+2.46,.65),.14,dark)
 box('Junction cable box',(x-1.5,y+2.4,.31),(.45,.50,.60),steel)
 for k in range(3):rod('Cable ground run',(x-1.5+k*.06,y+2.4,.03),(x-.4+k*.06,y+1,.03),.015,dark,6)
for x,y in [(-360,110),(-420,85),(302,128),(450,90)]:
 box('Trackside telecom cabinet',(x,y,1.10),(1.2,.55,1.9),steel);box('Telecom door seam',(x,y-.285,1.12),(.013,.014,1.72),dark)
 for z in (.65,.8,.95,1.1):box('Telecom vent',(x,y-.288,z),(.8,.016,.025),dark)
 for k in range(9):box('Stacked replacement sleeper',(x+3,y, k*.19),(.26,2.7,.18),concrete)
# Yard track labels are carried by documentation; operational numbers are explicitly synthetic.
flush()
col('21_PLATFORM_PAVING_AND_FORECOURT_FINISHES')
def inside(p,poly):
 x,y=p;odd=False;j=len(poly)-1
 for i in range(len(poly)):
  a,b=poly[i],poly[j]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:odd=not odd
  j=i
 return odd
for w in platforms:
 poly=w['xy'];xs=[p[0] for p in poly];ys=[p[1] for p in poly]
 for i in range(math.ceil((max(xs)-min(xs))/.9)):
  x=min(xs)+(i+.5)*.9
  for j in range(math.ceil((max(ys)-min(ys))/.9)):
   y=min(ys)+(j+.5)*.9
   if all(inside((x+dx,y+dy),poly) for dx in(-.44,.44) for dy in(-.44,.44)):
    box('Individual platform paving slabs',(x,y,.855),(.888,.888,.01),tile2 if random.random()<.13 else tile)
# Marked passenger pick-up bays and autos from previous editable source.
for x in range(-50,56,7):
 for xx in (x-2.9,x+2.9):box('Auto rank bay markings',(xx,-24,.052),(.10,5,.015),yellow)
 box('Auto rank end markings',(x,-26.5,.052),(5.9,.10,.015),yellow)
for x in (-62,64):sign('AUTO / TAXI',(x,-22,2.8),3,.75,size=.28)
with bpy.data.libraries.load(str(R/'source/TVC_heritage_source.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Auto ')]
for o in dst.objects:
 if o:current.objects.link(o);o.location.y-=15;o.location.x*=1.9
# Dense tropical foliage clusters with individual low-poly lobes; no image billboards.
leafmats=[material('Tropical foliage variation %d'%i,(.045+i*.015,.12+i*.035,.027+i*.007),noise=7) for i in range(4)]
def lobe(p,s,ma):
 v=[(p[0],p[1],p[2]+s[2]),(p[0],p[1],p[2]-s[2])]
 for i in range(10):
  a=i*math.tau/10;v.append((p[0]+s[0]*math.cos(a),p[1]+s[1]*math.sin(a),p[2]+random.uniform(-.2,.2)))
 f=[]
 for i in range(10):f.extend([(0,2+i,2+(i+1)%10),(1,2+(i+1)%10,2+i)])
 add('Broadleaf tree crown clusters',v,f,ma)
for x,y in [(-143,-19),(-86,-20),(84,-19),(149,-18),(-235,215),(245,131),(317,140),(475,128)]:
 h=random.uniform(5,8);rod('Shade tree trunk',(x,y,0),(x,y,h),.24,wood,12)
 for k in range(22):
  a=random.random()*math.tau;r=random.uniform(.1,3.2);p=(x+math.cos(a)*r,y+math.sin(a)*r,h+random.uniform(-.4,1.6));rod('Shade tree branch',(x,y,h-1),p,.05,wood);lobe(p,(random.uniform(.9,1.7),random.uniform(.8,1.5),random.uniform(.6,1.0)),random.choice(leafmats))
 for sg in(-1,1):box('Planter brick edging',(x+sg*2.3,y,.25),(.18,4.6,.5),red);box('Planter brick edging',(x,y+sg*2.3,.25),(4.6,.18,.5),red)
 box('Raised planting bed',(x,y,.10),(4.5,4.5,.2),soil)
flush()
