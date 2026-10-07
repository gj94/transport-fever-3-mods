"""Photo-informed VB2 shell finishes and nose assemblies, full-size prototype datums."""
import bpy,bmesh,math
from mathutils import Vector
from common import *
from materials import make
P='VB02_EXT_'
def apply(ctx):
 remove_prefix(P);M=ctx['materials'];body=ctx['body'];C=ctx['collection'];kind=ctx['kind'];dtc=kind=='DTC';L=ctx['layout'];nose_dx=L['nose_dx'];M['unlit_tail']=make('unlit_tail_lens',(.065,.0015,.002),.06,.19,.025,300)
 def B(n,c,d,ma='white',b=.004,parent=body):return box(P+n,c,d,M[ma],parent,C,b)
 def R(n,a,z,r,ma='steel',parent=body):return rod(P+n,a,z,r,M[ma],parent,C,N=16)
 def T(n,points,r,ma='rubber',parent=body):return tube(P+n,points,r,M[ma],parent,C,N=10)
 def V(n,v,f,ma='white',bevel=0,smooth=False):return mesh(P+n,v,f,M[ma],body,C,bevel,smooth)
 def remove(names):
  for o in list(bpy.data.objects):
   if o.type=='MESH' and any(o.name==n or o.name.startswith(n+'.') for n in names):bpy.data.objects.remove(o,do_unlink=True)
 def label(n,s,loc,size,rot,ma='black'):
  cu=bpy.data.curves.new(P+n,'FONT');cu.body=s;cu.size=size;cu.align_x='CENTER';cu.extrude=.00015;cu.resolution_u=3;o=bpy.data.objects.new(P+n,cu);C.objects.link(o);o.parent=body;o.location=loc;o.rotation_euler=rot;cu.materials.append(M[ma]);return o
 # Rounded manufacturing seals and recessed window sightlines, with the original open apertures retained.
 wins=L['windows']
 remove(['Window_seals','Window_inner_trim','Window_roller_blinds','Flag_orange','Flag_white','Flag_green','Side_identity','Side_railway','Door_leaf','Door_glass','Door_seals','Door_blue_footer','Door_handles'])
 for s in [-1,1]:
  rot=(math.pi/2,0,0) if s<0 else (math.pi/2,0,math.pi)
  for wi,window in enumerate(wins):
   if s not in window.get('sides',[-1,1]):continue
   x=window['x'];w=window['width'];h=window['height'];zc=window['center_z'];emergency=window.get('emergency',False)
   lower=zc-h/2;upper=zc+h/2
   for zz in [lower,upper]:B('window_inner_moulding',(x,s*1.508,zz),(w+.045,.035,.045),'ivory',.010)
   for xx in [x-w/2,x+w/2]:B('window_inner_jamb',(xx,s*1.508,zc),(.045,.035,h),'ivory',.010)
   if emergency:label('emergency_window_marking','EMERGENCY WINDOW',(x,s*1.639,lower-.11),.025,rot,'blue')
   if emergency:
    outer=rounded_rect(w,h,.105,10);inner=rounded_rect(1.50,.88,.10,10);nn=len(outer);vv=[(x+u,s*1.632,zc+z) for u,z in outer+inner];ff=[(j,(j+1)%nn,nn+(j+1)%nn,nn+j) for j in range(nn)];V('emergency_window_retaining_frame',vv,ff,'brushed')
   pts=rounded_rect(w,h,.105,10);T(f'window_{s}_{wi}_moulded_gasket',[(x+u,s*1.627,zc+z) for u,z in pts]+[(x+pts[0][0],s*1.627,zc+pts[0][1])],.022)
   # White quarter corners mask the square base opening, keeping a truly transparent center.
   for sx in [-1,1]:
    for sz in [-1,1]:
     a=x+sx*(w/2-.105);z=zc+sz*(h/2-.105)
     corner=(x+sx*w/2,s*1.631,zc+sz*h/2)
     vv=[corner]+[(a+sx*.105*math.cos(t*math.pi/2/12),s*1.631,z+sz*.105*math.sin(t*math.pi/2/12)) for t in range(13)]
     V('window_corner_fillet',vv,[tuple(range(len(vv)))])
   B('window_bottom_drain',(x,s*1.640,lower-.036),(.085,.008,.008),'black',.002)
   # Narrow blind cassette with end caps, on interior side rather than glazing plane.
   B('blind_cassette',(x,s*1.485,upper-.015),(w+.03,.074,.072),'ivory',.018)
  doors=L['passenger_door_x']
  for j,x in enumerate(doors):
   pivot=bpy.data.objects[f'DOOR_{"L" if s>0 else "R"}_{j+1}_SLIDE']
   outer=rounded_rect(.99,1.86,.050,12);inner=rounded_rect(.42,.90,.075,12);N=len(outer);vv=[]
   for yy in [-.0375,.0375]:
    vv.extend((u,yy,.93+z) for u,z in outer);vv.extend((u,yy,1.16+z) for u,z in inner)
   ff=[]
   for k in range(N):
    q=(k+1)%N
    ff += [(k,q,N+q,N+k),(2*N+k,3*N+k,3*N+q,2*N+q),(k,2*N+k,2*N+q,q),(N+k,N+q,3*N+q,3*N+k)]
   leaf=mesh(P+'continuous_passenger_door_leaf',vv,ff,M['white'],pivot,C,bevel=.004,local=True)
   bm=bmesh.new();bm.from_mesh(leaf.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(leaf.data);bm.free()
   tube(P+'door_window_moulding',[(u,s*.041,1.16+z) for u,z in inner]+[(inner[0][0],s*.041,1.16+inner[0][1])],.012,M['rubber'],pivot,C,N=10,local=True)
   glass=mesh(P+'door_laminated_glass',[(u,s*.040,1.16+z) for u,z in inner],[tuple(range(N))],M['glass'],pivot,C,local=True);mod=glass.modifiers.new('Closed door glass','SOLIDIFY');mod.thickness=.006;mod.offset=-s
   box(P+'door_blue_belt',(0,s*.041,.19),(.98,.004,.07),M['blue'],pivot,C,b=.003,local=True)
   rod(P+'door_handle',(.36,s*.080,.78),(.36,s*.080,1.12),.014,M['brushed'],pivot,C,N=20,local=True)
   for zz in [.78,1.12]:rod(P+'door_handle_mount',(.36,s*.040,zz),(.36,s*.080,zz),.019,M['steel'],pivot,C,N=20,local=True)
   pts=rounded_rect(1.04,1.91,.07,8);T('door_aperture_seal',[(x+u,s*1.626,2.255+z) for u,z in pts]+[(x+pts[0][0],s*1.626,2.255+pts[0][1])],.012)
   B('door_running_rail_cover',(x+.04,s*1.631,3.225),(1.24,.032,.065),'alloy',.012)
   for dz in [-.048,0,.048]:B('step_anti_slip_groove',(x,s*(1.64+dz),1.331),(.98,.010,.006),'dark_metal',.001)
   B('door_pushbutton_mount',(x+.62,s*1.642,2.10),(.115,.026,.15),'brushed',.017)
   cyl(P+'door_pushbutton_green_ring',(x+.62,s*1.663,2.10),.044,.018,M['green'],body,C,axis='Y',N=32)
   cyl(P+'door_pushbutton_centre',(x+.62,s*1.675,2.10),.027,.014,M['black'],body,C,axis='Y',N=32)
   label('door_instruction','OPEN',(x+.62,s*1.682,2.02),.026,rot)
   # Tricolour with geometric Ashoka Chakra, rather than three detached bars.
   for k,ma in enumerate(['amber','white','green']):B('tricolour',(x+.68,s*1.631,2.88-k*.043),(.255,.004,.042),ma,.0006)
   ring(P+'chakra_outer_ring',(x+.68,s*1.635,2.837),.016,.0143,.002,M['blue'],body,C,'Y',48);cyl(P+'chakra_hub',(x+.68,s*1.637,2.837),.0027,.002,M['blue'],body,C,'Y',24)
   for k in range(24):
    a=k*math.tau/24;R('chakra_spoke',(x+.68,s*1.639,2.837),(x+.68+.015*math.cos(a),s*1.639,2.837+.015*math.sin(a)),.00040,'blue')
   label('access_symbol','DOOR '+str(j+1),(x-.64,s*1.636,2.93),.036,rot,'blue')
   label('coach_class','EXECUTIVE CHAIR CAR' if 'EC' in kind else 'AC CHAIR CAR',(x-.60,s*1.636,3.13),.037,rot,'blue')
  label('identity','VANDE BHARAT',(0,s*1.637,1.685),.127,rot,'blue')
  label('railway','INDIAN RAILWAYS',(0,s*1.638,3.252),.075,rot,'white')
  label('technical',kind+'  |  1676 mm  |  ICF',(-5.6,s*1.638,1.39),.040,rot,'dark_metal')
  for x in [-5.3,-2.65,0,2.65,5.3]:
   # Panel-defined lower skirt with protected catches and drainage slots.
   B('skirt_panel',(x,s*1.501,.959),(2.08,.021,.365),'white',.012)
   for dx in [-.93,.93]:
    B('skirt_recess_latch',(x+dx,s*1.517,1.04),(.053,.007,.045),'dark_metal',.006)
    cyl(P+'skirt_latch',(x+dx,s*1.526,1.04),.012,.008,M['steel'],body,C,'Y',20)
   for dx in [-.65,0,.65]:B('skirt_drain',(x+dx,s*1.517,.794),(.095,.008,.009),'black',.003)
  for x in [-10.9,-7.2,7.2,10.9]:
   if dtc and x>L['cab_shell_rear_x']:continue
   B('body_vertical_panel_joint',(x,s*1.624,1.65),(.005,.003,.85),'alloy',.0005)
   B('lifting_point',(x,s*1.51,1.04),(.13,.035,.07),'dark_metal',.006)
  # Soft rain channel at shoulder; does not alter body envelope materially.
  R('roof_rain_gutter',(-11.52,s*1.613,3.185),(L['cab_shell_rear_x']-.03 if dtc else 11.52,s*1.613,3.185),.009,'blue')
 if dtc:
  before_nose=set(bpy.data.objects)
  remove(['Sculpted_nose_skin','Nose_windscreen','Nose_lamp_pods','Marker_lamp_bezel','Marker_lamp_lens','Upper_headlamps','Front_headcode','Front_headcode_text','Front_wipers','ICF_nose_marking','Nose_cover_seam','Roof_horns','Roof_horn_bells','Nose_side_cheeks','Cab_side_glass','Cab_inner_nose_lining','Cab_inner_side_lining','Cab_crown','Nose_underlip'])
  zs=[.78,1.04,1.30,1.62,1.94,2.18,2.30,2.64,3.02,3.22,3.48,3.72,3.91,4.00]
  xs=[9.74,9.98,10.05,10.043,10.005,9.92,9.80,9.38,8.90,8.65,8.30,7.96,7.58,7.30]
  ws=[1.15,1.36,1.43,1.48,1.52,1.55,1.55,1.53,1.49,1.44,1.34,1.19,.94,.65]
  def val(arr,z):
   i=max(0,min(len(zs)-2,next((i for i in range(len(zs)-1) if zs[i]<=z<=zs[i+1]),len(zs)-2)));t=(z-zs[i])/(zs[i+1]-zs[i]);a=arr[max(0,i-1)];b=arr[i];c=arr[i+1];d=arr[min(len(arr)-1,i+2)];return .5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
  def paint_u(z,u):
   t=max(0,min(1,(z-1.92)/.38));t=t*t*(3-2*t);inner=.68+.16*t;a=abs(u)
   mapped=a*inner/.84 if a<=.84 else inner+(a-.84)*(1-inner)/.16
   return math.copysign(mapped,u)
  def pt(z,u,off=0):
   u=paint_u(z,u);return(val(xs,z)-.24*u*u+off,val(ws,z)*u,z)
  def surface(z,y,off=.012):return(val(xs,z)-.24*(y/val(ws,z))**2+off,y,z)
  levels=sorted(set([z+(zs[i+1]-z)*j/5 for i,z in enumerate(zs[:-1]) for j in range(5)]+[zs[-1],2.375,2.40,2.925,3.18]));us=sorted(set([i/60 for i in range(-60,61)]+[-.84,-.81,-.7333333333,.7333333333,.81,.84]))
  verts=[];faces=[];mis=[]
  for z in levels:
   verts.extend(pt(z,u) for u in us)
  for i in range(len(levels)-1):
   for j in range(len(us)-1):
    z=(levels[i]+levels[i+1])/2;u=(us[j]+us[j+1])/2;glass=2.30<z<3.22 and abs(u)<.73
    if glass:continue
    black=z>=2.18 and abs(u)<.81
    blue=abs(u)>.84
    ma=2 if black else 1 if blue else 0
    faces.append((i*len(us)+j,i*len(us)+j+1,(i+1)*len(us)+j+1,(i+1)*len(us)+j));mis.append(ma)
  o=mesh(P+'continuous_formed_nose',verts,faces,[M['white'],M['blue'],M['black']],body,C,smooth=True)
  for f,mi in zip(o.data.polygons,mis):f.material_index=mi
  # Continuous rear-to-front side loft using the exact inherited roof cross-section.
  # Unlike the baseline linear shoulder approximation, every rear edge meets the roof.
  cross=[(1.62,3.13),(1.59,3.36),(1.46,3.58),(1.23,3.73),(.82,3.8),(0,3.82)]
  def rear(z):
   if z<=3.13:return 1.62,z
   if z>=3.82:return 0,3.82
   for (y0,z0),(y1,z1) in zip(cross,cross[1:]):
    if z0<=z<=z1:return y0+(y1-y0)*(z-z0)/(z1-z0),z
  def sidept(z,t,sgn,inside=0):
   yy,zz=rear(z);a=Vector((5.65,sgn*yy,zz));b=Vector(pt(z,sgn));q=a.lerp(b,t);q.y-=sgn*inside;return tuple(q)
  def side_x_knots(z):
   front=pt(z,1)[0];door=L['cab_door_x']-nose_dx
   rear_window=8.95-nose_dx;front_window=10.93-nose_dx+(z-2.40)*(9.98-10.93)/.78
   knots=[5.65,min(door-.14,front-.04),min(door+.14,front-.03),min(rear_window,front-.02),min(max(rear_window+.01,front_window),front-.01),front]
   values=[]
   for a,b in zip(knots,knots[1:]):values.extend(a+(b-a)*i/4 for i in range(4))
   values.append(front);return values
  def side_at_x(z,x,sg):return sidept(z,(x-5.65)/(pt(z,sg)[0]-5.65),sg)
  ts=list(range(21))
  for sg in [-1,1]:
   vs=[];fs=[];inner=[];gvs=[];gfs=[];colours=[]
   for z in levels:
    vs.extend(side_at_x(z,x,sg) for x in side_x_knots(z))
   for ii in range(len(levels)-1):
    for jj in range(len(ts)-1):
     zm=(levels[ii]+levels[ii+1])/2;tm=jj/20
     ids=(ii*len(ts)+jj,ii*len(ts)+jj+1,(ii+1)*len(ts)+jj+1,(ii+1)*len(ts)+jj)
     if (2.40<zm<3.18 and 12<=jj<16) or (2.375<zm<2.925 and 4<=jj<8):
      k=len(gvs);gvs.extend(vs[v] for v in ids);gfs.append(tuple(range(k,k+4)));continue
     fs.append(ids if sg<0 else tuple(reversed(ids)));colours.append(1 if tm>.945 else 0)
   side=mesh(P+'continuous_cab_side',vs,fs,[M['white'],M['blue']],body,C,smooth=True)
   for f,mi in zip(side.data.polygons,colours):f.material_index=mi
   bm=bmesh.new();bm.from_mesh(side.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(side.data);bm.free()
   window=mesh(P+'cab_side_laminated_glass',gvs,gfs,M['glass'],body,C,smooth=True);bm=bmesh.new();bm.from_mesh(window.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(window.data);bm.free();mod=window.modifiers.new('Closed cabin side glass','SOLIDIFY');mod.thickness=.006;mod.offset=-1
   edge=[side_at_x(2.40,8.95-nose_dx+k*(10.93-8.95)/18,sg) for k in range(19)]+[side_at_x(2.40+k*.78/18,10.93-nose_dx+k*(9.98-10.93)/18,sg) for k in range(1,19)]+[side_at_x(3.18,9.98-nose_dx-k*(9.98-8.95)/18,sg) for k in range(1,19)]+[side_at_x(3.18-k*.78/18,8.95-nose_dx,sg) for k in range(1,19)]
   T('cab_side_window_seal',edge+[edge[0]],.019,'rubber')
   # Inner lining follows only solid skin panels, with no opaque window backing.
   lining=[(x,y-sg*.047,z) for x,y,z in vs];mesh(P+'cab_side_inner_lining',lining,[tuple(reversed(f)) for f in fs],M['ivory'],body,C,smooth=True)
   # Independent narrow cab access door behind side window, drawn closed.
   doorpts=rounded_rect(.57,1.83,.07,10);T('cab_entry_door_seal',[(L['cab_door_x']-nose_dx+x,sg*1.624,2.29+z) for x,z in doorpts]+[(L['cab_door_x']-nose_dx+doorpts[0][0],sg*1.624,2.29+doorpts[0][1])],.0075,'rubber')
   d=L['cab_door_x']-nose_dx;frame=[side_at_x(z,x,sg) for x,z in [(d-.14,2.375),(d+.14,2.375),(d+.14,2.925),(d-.14,2.925),(d-.14,2.375)]];T('cab_entry_glass_seal',frame,.012,'rubber')
   R('cab_entry_handle',(L['cab_door_x']-nose_dx+.185,sg*1.65,1.97),(L['cab_door_x']-nose_dx+.185,sg*1.65,2.20),.011,'brushed')
   for z in [1.0,1.14]:B('cab_entry_recess_step',(L['cab_door_x']-nose_dx-.01,sg*1.60,z),(.57,.11,.032),'brushed',.009)
  # Crown closes the top of both side patches and meets the front upper edge exactly.
  crown=mesh(P+'smooth_cab_crown',[(5.65,0,3.82)]+[pt(4,u) for u in us],[(0,j+1,j+2) for j in range(len(us)-1)],M['white'],body,C,smooth=True)
  # Nose lining is offset behind solid front panels only.
  lining=[(x-.048,y*.99,z) for x,y,z in verts];mesh(P+'nose_inner_lining',lining,[tuple(reversed(f)) for f in faces],M['ivory'],body,C,smooth=True)
  # Slim lower return replaces the inherited deep protruding front slab.
  for sg in [-1,1]:
   R('cab_lower_sill',(5.69,sg*1.58,1.11),(8.82,sg*1.43,1.11),.030,'alloy')
  for slab in bpy.data.objects:
   if slab.type=='MESH' and slab.name.startswith('Body_sill'):
    for v in slab.data.vertices:
     if v.co.x>L['cab_shell_rear_x']:v.co.x=L['cab_shell_rear_x']
  # One closed laminated, smoothly curved windscreen; topology continues to omitted skin region.
  glz=[z for z in levels if 2.30<=z<=3.22];glu=[u for u in us if -.733334<=u<=.733334];vv=[pt(z,u,.0005) for z in glz for u in glu];ff=[(i*len(glu)+j,i*len(glu)+j+1,(i+1)*len(glu)+j+1,(i+1)*len(glu)+j) for i in range(len(glz)-1) for j in range(len(glu)-1)];o=V('laminated_windscreen',vv,ff,'glass',smooth=True);sol=o.modifiers.new('Closed six millimetre laminated pane','SOLIDIFY');sol.thickness=.006;sol.offset=-1
  perimeter=[pt(2.3,-.7333+i*1.4666/40,.004) for i in range(41)]+[pt(2.3+i*.92/28,.7333,.004) for i in range(1,29)]+[pt(3.22,.7333-i*1.4666/40,.004) for i in range(1,41)]+[pt(3.22-i*.92/28,-.7333,.004) for i in range(1,29)]
  T('windscreen_extruded_seal',perimeter+[perimeter[0]],.024)
  # Tear-drop black pods are surface-conforming mouldings with a bright narrow perimeter.
  for s in [-1,1]:
   yz=[(1.11,1.63),(1.34,1.80),(1.42,2.01),(1.35,2.19),(1.30,2.43),(1.26,2.48),(1.22,2.19),(1.08,1.91)]
   pts=[surface(z,s*y,.020) for y,z in yz];o=V('teardrop_light_moulding',pts,[tuple(range(len(pts)))],'black');so=o.modifiers.new('Moulded lamp pod depth','SOLIDIFY');so.thickness=.019
   T('teardrop_bright_edge',pts+[pts[0]],.009,'brushed')
   for j,(y,z,r) in enumerate([(1.25,1.91,.073),(1.30,2.095,.099)]):
    c=surface(z,s*y,.044);ring(P+'marker_recess',c,r*1.20,r,.025,M['rubber'],body,C,'X',48);ring(P+'marker_chrome',c,r,r*.83,.032,M['steel'],body,C,'X',48);cyl(P+'marker_lens',(c[0]+.021,c[1],c[2]),r*.80,.017,M['emissive'] if j else M['unlit_tail'],body,C,'X',48)
    for k in range(8 if j else 0):
     a=k*math.tau/8;cyl(P+'marker_optical_facet',(c[0]+.032,c[1]+r*.50*math.cos(a),c[2]+r*.50*math.sin(a)),r*.11,.004,M['emissive'],body,C,'X',12)
   # Pantograph-form wipers: two links, paired rods, blade and pivot boots.
   p0=surface(2.25,s*.79,.034);p1=surface(2.72,s*.65,.045);p2=surface(3.04,s*.90,.043)
   for off in [-.016,.016]:T('wiper_parallel_arm',[(p0[0],p0[1]+off,p0[2]),(p1[0],p1[1]+off,p1[2])],.0075,'dark_metal')
   T('wiper_carrier',[p1,p2],.013,'dark_metal');T('wiper_rubber_blade',[surface(2.77,s*.64,.060),surface(3.08,s*.98,.060)],.013,'rubber');cyl(P+'wiper_spindle',p0,.037,.043,M['black'],body,C,'X',32)
  # Upper twin LED capsule, amber destination box and lens barrels, conforming to sloped mask.
  z=3.55;cx=val(xs,z)+.015
  pts=rounded_rect(.58,.27,.115,12);o=V('upper_headlamp_capsule',[(val(xs,z+v)+.015,u,z+v) for u,v in pts],[tuple(range(len(pts)))],'black');so=o.modifiers.new('Headlamp housing depth','SOLIDIFY');so.thickness=.055
  T('upper_capsule_trim',[(val(xs,z+v)+.020,u,z+v) for u,v in pts]+[(val(xs,z+pts[0][1])+.020,pts[0][0],z+pts[0][1])],.007,'brushed')
  # Continuous sealed curved cover; LED cups remain behind this lens.
  cap=V('sealed_upper_lamp_cover',[(val(xs,z+v)+.035,u,z+v) for u,v in pts],[tuple(range(len(pts)))],'glass');solid=cap.modifiers.new('Sealed capsule lens','SOLIDIFY');solid.thickness=.004
  # All optical layers share a plane normal to the sloping mask, avoiding protruding cages.
  normal=Vector((1,0,-(val(xs,z+.01)-val(xs,z-.01))/.02)).normalized();q=Vector((1,0,0)).rotation_difference(normal)
  def optic(n,center,r,depth,ma,ro=None):
   obj=ring(P+n,(0,0,0),ro,r,depth,M[ma],body,C,'X',64) if ro else cyl(P+n,(0,0,0),r,depth,M[ma],body,C,'X',64)
   for v in obj.data.vertices:v.co=q@v.co+Vector(center)
   return obj
  for y in [-.135,.135]:
   center=Vector(surface(z,y,.025));optic('headlamp_reflector',center,.088,.009,'alloy')
   optic('headlamp_sealed_rim',center+normal*.010,.091,.009,'steel',.101)
   optic('headlamp_clear_cover',center+normal*.016,.088,.005,'glass')
   for iy in range(-2,3):
    for iz in range(-2,3):
     if iy*iy+iz*iz<=5:
      c=center+q@Vector((.008,iy*.029,iz*.029));optic('individual_LED_emitter',c,.010,.002,'emissive')
  B('destination_housing',(val(xs,3.315)+.012,0,3.315),(.025,1.16,.21),'black',.025)
  label('destination_text','VANDE BHARAT',(val(xs,3.287)+.031,0,3.287),.096,(math.pi/2,0,math.pi/2),'amber')
  for y in [-.78,.78]:cyl(P+'camera_sensor',surface(3.34,y,.025),.037,.028,M['black'],body,C,'X',32);ring(P+'camera_sensor_trim',surface(3.34,y,.045),.024,.019,.005,M['brushed'],body,C,'X',32)
  # Closed rescue fairing seams and shallow upper badge panel; geometry stays inside prior nose envelope.
  T('lower_skirt_shadow_joint',[surface(1.045,y,.004) for y in [-1.21,-.95,-.65,-.3,0,.3,.65,.95,1.21]],.009,'black')
  T('central_split_seam',[surface(z,0,.003) for z in [1.04,1.3,1.62,1.94]],.0035,'dark_metal')
  T('rescue_fairing_upper_seam',[surface(1.945,y,.004) for y in [-1.03,-.8,-.4,0,.4,.8,1.03]],.004,'alloy')
  label('ICF_identity','ICF',(val(xs,1.505)+.004,0,1.505),.225,(math.pi/2,0,math.pi/2),'blue')
  # Horns with hollow flared bell interiors, hose and genuine bracket feet.
  for s in [-1,1]:
   B('horn_mount',(6.20,s*.39,3.905),(.28,.18,.05),'dark_metal',.006)
   lathe(P+'horn_flared_body',(6.19,s*.39,3.985),[(-.10,.034),(.07,.039),(.21,.065),(.31,.10),(.31,.080),(.21,.046),(.07,.025),(-.10,.025)],M['dark_metal'],body,C,'X',48)
   T('horn_airline',[(6.10,s*.39,3.97),(5.99,s*.39,3.93),(5.98,s*.63,3.87)],.010,'rubber')
  for obj in list(bpy.data.objects):
   if obj not in before_nose and obj.name.startswith(P):
    if obj.type=='MESH':
     for vertex in obj.data.vertices:vertex.co.x+=nose_dx+(1.05 if 'horn_' in obj.name else 0)
     obj.data.update()
    else:obj.location.x+=nose_dx
  for s in [-1,1]:
   for j,(y,z) in enumerate([(1.25,1.91),(1.30,2.095)]):
    anchor=bpy.data.objects.get(f'LIGHT_{"L" if s>0 else "R"}_{j}_ANCHOR')
    if anchor:anchor.location=tuple(Vector(surface(z,s*y,.065))+Vector((nose_dx,0,0)))
 return {'kind':kind,'pitch_m':24.0,'nose_profile':'Photo-informed smooth loft uses23.328m nose-to-rear body envelope; not dimension-certified','window_seals':'Rounded exterior masks retain open base apertures','reference':'PIB VB2 launch photograph 2022-09-30; all meshes original','lamp_preview_state':'White front optics illuminated; red tail lenses unlit. Runtime directional light switching not supplied','objects':sum(o.name.startswith(P) for o in bpy.data.objects)}
