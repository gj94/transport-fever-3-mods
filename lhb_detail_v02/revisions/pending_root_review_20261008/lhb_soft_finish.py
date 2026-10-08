"""Soft-surface geometry and source-informed cabin fittings.
All upholstery and textile meshes are original. This is representative finishing,
not a scan or manufacturer seat CAD. Existing physical seating datums are retained.
"""
import bpy,math
from mathutils import Vector

def apply(g,k,c):
 box,mesh,rod,text,material=[g[n] for n in ['box','mesh','rod','text','material']]
 inter=g['inter'];body=g['body'];blue=g['blue'];ivory=g['ivory'];steel=g['steel'];rubber=g['rubber'];white=g['white'];wood=g['wood']
 trim=material('Soft_upholstery_seam_'+k,(.048,.013,.018) if k=='1A' else (.012,.028,.045),0,.75)
 cloth=material('Curtain_woven_cloth_'+k,(.16,.029,.025) if k=='1A' else (.023,.075,.13),0,.83)
 cp=cloth.node_tree.nodes.get('Principled BSDF');cp.inputs['Sheen Weight'].default_value=.25
 vp=blue.node_tree.nodes.get('Principled BSDF')
 if k=='1A':vp.inputs['Base Color'].default_value=(.17,.022,.028,1);blue.diffuse_color=(.17,.022,.028,1);vp.inputs['Roughness'].default_value=.62
 elif k=='GS':vp.inputs['Roughness'].default_value=.67;vp.inputs['Sheen Weight'].default_value=.04
 for n in blue.node_tree.nodes:
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=1450 if k!='GS' else 2100
  elif n.type=='BUMP':n.inputs['Distance'].default_value=.00019;n.inputs['Strength'].default_value=.15
 sp=steel.node_tree.nodes.get('Principled BSDF');sp.inputs['Base Color'].default_value=(.235,.275,.29,1);sp.inputs['Roughness'].default_value=.34
 def outline(w,h,r,n=10):
  points=[]
  for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for j in range(n+1):
    a=math.radians(start+90*j/n);points.append((cx+r*math.cos(a),cy+r*math.sin(a)))
  return points
 def soft_mesh(ob,axis='Z',thickness=None):
  # Rounded rectangular contour rings produce a rolled shoulder and crown,
  # rather than merely beveling a thin flat board. The maximum top stays fixed.
  old=ob.data;dims=[max(v.co[i] for v in old.vertices)-min(v.co[i] for v in old.vertices) for i in range(3)];ax={'X':0,'Z':2}[axis];plane=[i for i in range(3) if i!=ax]
  olddepth=dims[ax];depth=thickness or olddepth
  if axis=='Z':ob.location.z+=(olddepth-depth)/2
  w,h=dims[plane[0]],dims[plane[1]];radius=min(.055 if k=='1A' else .042,w*.13,h*.13)
  steps=[(-.50,.034),(-.39,.012),(-.12,0),(.19,0),(.36,.006),(.46,.019),(.50,.037)]
  # CC shoulders receive bounded cubic profile refinement: preserve each
  # control ring and all maximum dimensions while removing seven-ring faceting.
  if k=='CC' and ob.name.startswith('CHAIR_back'):
   refined=[]
   for i in range(len(steps)-1):
    p0=steps[max(0,i-1)];p1=steps[i];p2=steps[i+1];p3=steps[min(len(steps)-1,i+2)]
    for j in range(4):
     u=j/4; t=p1[0]+u*(p2[0]-p1[0])
     m1=(p2[1]-p0[1])/(p2[0]-p0[0]);m2=(p3[1]-p1[1])/(p3[0]-p1[0]);dt=p2[0]-p1[0]
     v=(2*u**3-3*u*u+1)*p1[1]+(u**3-2*u*u+u)*dt*m1+(-2*u**3+3*u*u)*p2[1]+(u**3-u*u)*dt*m2
     refined.append((t,max(min(p1[1],p2[1]),min(max(p1[1],p2[1]),v))))
   steps=refined+[steps[-1]]
  vs=[];ring_count=0
  for t,inset in steps:
   inset=min(inset,w*.14,h*.14);points=outline(w-2*inset,h-2*inset,max(.014,radius-inset*.48));ring_count=len(points)
   for a,b in points:
    q=[0.,0.,0.];q[plane[0]]=a;q[plane[1]]=b;q[ax]=t*depth;vs.append(tuple(q))
  fs=[tuple(range(ring_count-1,-1,-1))]
  for row in range(len(steps)-1):
   fs.extend([(row*ring_count+j,row*ring_count+(j+1)%ring_count,(row+1)*ring_count+(j+1)%ring_count,(row+1)*ring_count+j) for j in range(ring_count)])
  fs.append(tuple(range((len(steps)-1)*ring_count,len(steps)*ring_count)))
  data=bpy.data.meshes.new(ob.name+'_soft_surface');data.from_pydata(vs,[],fs);data.update()
  import bmesh
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
  for m in old.materials:data.materials.append(m)
  for p in data.polygons:p.use_smooth=True
  ob.data=data
  for mod in list(ob.modifiers):ob.modifiers.remove(mod)
  if old.users==0:bpy.data.meshes.remove(old)
  ob['surface_detail']='Closed contour-ring cushion with rolled shoulder; original geometry'
  return w,h,depth
 def closed_cord(name,points,r,mat,normal=(0,0,1),normals=None):
  vs=[];N=8;count=len(points)
  for i,p in enumerate(points):
   p=Vector(p);t=(Vector(points[(i+1)%count])-Vector(points[i-1])).normalized();u=Vector(normals[i] if normals is not None else normal).normalized();v=t.cross(u).normalized()
   for j in range(N):vs.append(tuple(p+r*(u*math.cos(j*math.tau/N)+v*math.sin(j*math.tau/N))))
  fs=[(i*N+j,i*N+(j+1)%N,((i+1)%count)*N+(j+1)%N,((i+1)%count)*N+j) for i in range(count) for j in range(N)]
  ob=mesh(name,vs,fs,mat,coll=inter)
  for p in ob.data.polygons:p.use_smooth=True
  return ob
 for ob in list(inter.objects):
  if ob.name.startswith(('UPHOLSTERY_edge_piping','UPHOLSTERY_back_seam')):bpy.data.objects.remove(ob,do_unlink=True)
 cushions=[ob for ob in list(inter.objects) if ob.name.startswith(('FIRST_LOWER','FIRST_UPPER','MAIN_LOWER','MAIN_UPPER','SIDE_LOWER','SIDE_UPPER','GS_main_bench','GS_side_bench','CHAIR_cushion'))]
 for ob in cushions:
  w,h,depth=soft_mesh(ob,'Z',.155 if k=='1A' else (.128 if k=='GS' else None))
  bpy.context.view_layer.update();pts=[tuple(ob.matrix_world@Vector((x,y,depth*.40))) for x,y in outline(w-.025,h-.025,min(.049,w*.12,h*.12),12)]
  closed_cord('UPHOLSTERY_edge_piping_soft',pts,.0017,trim)
 for ob in list(inter.objects):
  if ob.name.startswith(('FIRST_backrest','LOWER_BACKREST','MIDDLE_FOLDED','GS_bench_back','CHAIR_back')):
   w,h,depth=soft_mesh(ob,'X');bpy.context.view_layer.update()
   normal=ob.matrix_world.to_3x3()@Vector((1,0,0))
   for face in [-1,1]:
    points=[tuple(ob.matrix_world@Vector((face*depth*.40,y,z))) for y,z in outline(w-.025,h-.025,min(.045,w*.12,h*.12),12)]
    closed_cord('UPHOLSTERY_back_seam_soft',points,.0015,trim,normal)
 # The chair-car antimacassar is woven cloth draped over the crown, never
 # a second foam headrest. Closed 1.2 mm textile and a sewn perimeter hem.
 if k=='CC':
  cotton=bpy.data.materials.get('Cotton_linen') or white
  for head in [o for o in list(inter.objects) if o.name.startswith('HEADREST_')]:
   sid=head.name[len('HEADREST_'):];bpy.data.objects.remove(head,do_unlink=True)
   back=bpy.data.objects['CHAIR_back_'+sid];bpy.context.view_layer.update()
   path=[]
   for j in range(13):path.append((-.060,.158+(.285-.158)*j/12))
   for j in range(1,25):
    a=math.pi-j*math.pi/24;path.append((.060*math.cos(a),.285+.043*math.sin(a)))
   for j in range(1,16):path.append((.060,.285-(.285-.125)*j/15))
   nx=28;ny=len(path);vs=[];mid=[]
   for layer in (-1,1):
    for row,(xx,zz) in enumerate(path):
     prev=Vector(path[max(0,row-1)]);nxt=Vector(path[min(ny-1,row+1)])
     tangent=(nxt-prev).normalized();normal=Vector((-tangent.y,tangent.x))
     for col in range(nx+1):
      u=col/nx;hang=max(0,(.285-zz)/.16);wrinkle=(.0012+.0013*math.sin(u*math.tau*3+.4))*hang
      px=xx+normal.x*(wrinkle+layer*.0006);pz=zz+normal.y*(wrinkle+layer*.0006)
      pz+=.003*math.sin(u*math.tau*2+.2)*hang**3
      vs.append((px,(u-.5)*.302,pz))
   stride=nx+1;N=ny*stride;fs=[]
   for row in range(ny-1):
    for col in range(nx):
     a=row*stride+col;fs += [(a,a+1,a+1+stride,a+stride),(N+a+stride,N+a+1+stride,N+a+1,N+a)]
   boundary=list(range(stride))+[r*stride+nx for r in range(1,ny)]+list(range(N-2,N-stride-1,-1))+[r*stride for r in range(ny-2,0,-1)]
   for a,b in zip(boundary,boundary[1:]+boundary[:1]):fs.append((a,N+a,N+b,b))
   ob=mesh('HEADREST_'+sid,vs,fs,cotton,coll=inter);ob.matrix_local=back.matrix_local.copy()
   for poly in ob.data.polygons:poly.use_smooth=True
   ob['textile_thickness_m']=.0012;ob['construction']='Thin draped cotton antimacassar with sewn perimeter hem; original mesh'
   hem=[tuple(back.matrix_local@Vector(tuple((vs[i][j]+vs[N+i][j])/2 for j in range(3)))) for i in boundary]
   normals=[back.matrix_local.to_3x3()@(Vector(vs[N+i])-Vector(vs[i])).normalized() for i in boundary]
   closed_cord('CC_ANTIMACASSAR_sewn_hem_'+sid,hem,.0009,cotton,normals=normals)
 # Replace accordion-like rectangular curtain strips with gravity-shaped folds,
 # a gathered waist, uneven soft hem and a small cloth tieback.
 if k in ['1A','2A','3A']:
  for ob in list(inter.objects):
   if ob.name.startswith('WINDOW_pleated_curtain'):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.context.view_layer.update()
  for rail in [o for o in bpy.data.objects if o.name.startswith('CURTAIN_rail')]:
   ps=[rail.matrix_world@v.co for v in rail.data.vertices];xc=(min(p.x for p in ps)+max(p.x for p in ps))/2;yc=sum(p.y for p in ps)/len(ps);width=max(p.x for p in ps)-min(p.x for p in ps);sy=1 if yc>0 else -1
   for side in [-1,1]:
    cx=xc+side*(width/2-.075);nx=40;nz=18;vs=[]
    for iz in range(nz+1):
     v=iz/nz;w=.17+.045*(1-v)-.065*math.exp(-((v-.43)/.16)**2)
     for ix in range(nx+1):
      u=ix/nx;fold=math.sin(u*8*math.pi+.16*math.cos(v*math.pi));vs.append((cx+(u-.5)*w,yc+.020*fold*(.62+.38*math.sin(v*math.pi)),2.095+v*.81+.009*math.cos(u*math.tau*4)*(1-v)))
    fs=[(iz*(nx+1)+ix,iz*(nx+1)+ix+1,(iz+1)*(nx+1)+ix+1,(iz+1)*(nx+1)+ix) for iz in range(nz) for ix in range(nx)]
    ob=mesh('WINDOW_soft_gathered_curtain',vs,fs,cloth,coll=inter);md=ob.modifiers.new('Cloth thickness','SOLIDIFY');md.thickness=.0016
    for f in ob.data.polygons:f.use_smooth=True
    box('CURTAIN_cloth_tieback',(cx,yc-sy*.026,2.442),(.124,.009,.025),cloth,.004,coll=inter)
 g['soft_finish_trim']=trim;g['soft_finish_cloth']=cloth
 if k=='1A':first_class(g)


def first_class(g):
 # Fittings are corroborated by CAMTECH's first-AC layout/maintenance inventory
 # and the original 2023 1AC coupe photo linked in the reference ledger.
 box,mesh,rod,text,material=[g[n] for n in ['box','mesh','rod','text','material']]
 inter=g['inter'];body=g['body'];steel=g['steel'];ivory=g['ivory'];rubber=g['rubber'];white=g['white'];wood=g['wood']
 mirror=material('Cabin_mirror_silver',(.84,.88,.89),1,.055)
 dark=material('Cabin_control_engraving',(.025,.031,.036),0,.46)
 lamp=material('Cabin_reading_light_diffuser',(.78,.73,.57),0,.4);p=lamp.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.83,.61,1);p.inputs['Emission Strength'].default_value=1.7
 # The old low luggage ledges conflicted with the above-window mirror position.
 for ob in list(inter.objects):
  if ob.name.startswith('LUGGAGE_RACK_'):
   for v in ob.data.vertices:v.co.z+=.50
  if ob.name.startswith('FIRST_upper_guard'):bpy.data.objects.remove(ob,do_unlink=True)
  elif ob.name.startswith('FIRST_upper_access_step'):ob.location.z-=.10
 lengths=[2.50,1.73,2.50,1.73,1.73,2.50,1.73,2.50];cur=-sum(lengths)/2
 for i,L in enumerate(lengths):
  x=cur+L/2;ends=[-1,1] if L>2 else [-1]
  g['detail_rounded_slab']('CABIN_mirror_frame',x,-1.484,3.195,.43,.405,.021,.06,steel,inter)
  g['detail_rounded_slab']('CABIN_mirror',x,-1.469,3.195,.382,.357,.008,.047,mirror,inter)
  for side in [-1,1]:
   xx=x+side*.333
   box('CABIN_upper_control_panel',(xx,-1.484,3.193),(.175,.018,.168),ivory,.012,coll=inter)
   for dx,dz in [(-.020,-.019),(.020,-.019),(0,.023)]:rod('CABIN_socket_hole',(xx+dx,-1.473,3.193+dz),(xx+dx,-1.468,3.193+dz),.005,dark,10,coll=inter)
   box('CABIN_light_switch',(xx+side*.051,-1.465,3.189),(.019,.012,.045),white,.004,coll=inter)
  text('CABIN_control_legend','LIGHT  /  SOCKET',(x,-1.462,2.961),.025,m=dark,coll=inter)
  # Sliding door has a pull and a real latch/strike at the visible corridor edge.
  dx=x+.28
  box('CABIN_lock_escutcheon',(dx,.568,2.10),(.063,.014,.18),steel,.012,coll=inter)
  rod('CABIN_lock_thumbturn',(dx-.023,.584,2.10),(dx+.023,.584,2.10),.009,steel,12,coll=inter)
  box('CABIN_lock_strike',(x-.37,.520,2.10),(.032,.029,.12),steel,.004,coll=inter)
  box('CABIN_inner_lock_plate',(dx,.520,2.10),(.063,.018,.18),steel,.005,coll=inter)
  rod('CABIN_inner_thumbturn',(dx-.023,.503,2.10),(dx+.023,.503,2.10),.009,steel,12,coll=inter)
  rod('CABIN_inner_door_pull',(dx+.10,.495,2.04),(dx+.10,.495,2.28),.010,steel,16,coll=inter)
  for zz in [2.04,2.28]:rod('CABIN_inner_pull_mount',(dx+.10,.495,zz),(dx+.10,.528,zz),.009,steel,12,coll=inter)
  box('CABIN_ceiling_lamp_frame',(x,-.55,3.583),(.55,.18,.025),steel,.008,coll=inter)
  box('CABIN_ceiling_lamp_diffuser',(x,-.55,3.564),(.51,.145,.016),lamp,.007,coll=inter)
  ax=cur+L-.22
  box('CABIN_alarm_plate',(ax,.470,3.13),(.105,.016,.155),ivory,.007,coll=inter)
  rod('CABIN_alarm_pull',(ax-.03,.452,3.115),(ax+.03,.452,3.115),.009,g['paint'],12,coll=inter)
  text('CABIN_alarm_label','ALARM',(ax,.458,3.175),.024,m=dark,coll=inter)
  for e in ends:
   xx=x+e*(L/2-.40)
   # Guard is a supported U-shaped rail with a centre brace, matching the
   # functional form in the photo rather than a floating horizontal rod.
   for gx in [xx-.27,xx+.27]:rod('FIRST_upper_guard_upright',(gx,.462,3.065),(gx,.462,3.295),.014,steel,16,coll=inter)
   rod('FIRST_upper_guard_top',(xx-.27,.462,3.295),(xx+.27,.462,3.295),.014,steel,20,coll=inter)
   rod('FIRST_upper_guard_centre',(xx,.462,3.065),(xx,.462,3.295),.011,steel,16,coll=inter)
   stairx=xx-e*.30
   for yy in [.185,.435]:
    rod('FIRST_access_ladder_stile',(stairx-e*.10,yy,1.313),(stairx+e*.08,yy,3.14),.014,steel,20,coll=inter)
    box('FIRST_ladder_floor_foot',(stairx-e*.10,yy,1.314),(.07,.06,.020),steel,.004,coll=inter)
   # One magazine net below each upper berth and one above its pillow area.
   for zz in [2.72,3.35]:
    wallx=xx+e*.3725
    for yy in [-1.14,-.58]:rod('CABIN_magazine_frame',(wallx,yy,zz-.13),(wallx,yy,zz+.13),.006,steel,10,coll=inter)
    for z in [zz-.13,zz+.13]:rod('CABIN_magazine_frame',(wallx,-1.14,z),(wallx,-.58,z),.006,steel,10,coll=inter)
    for j in range(12):
     yy=-1.12+j*.047;rod('CABIN_magazine_net',(wallx-e*.014,yy,zz-.12),(wallx-e*.014,min(-.59,yy+.19),zz+.12),.0016,rubber,6,coll=inter)
    for j in range(12):
     yy=-1.12+j*.047;rod('CABIN_magazine_net',(wallx-e*.013,yy,zz+.12),(wallx-e*.013,min(-.59,yy+.19),zz-.12),.0016,rubber,6,coll=inter)
   # Per-berth upper reading lamp and small coat-hook fittings.
   box('CABIN_upper_reading_mount',(xx,-1.478,3.438),(.105,.021,.075),steel,.012,coll=inter)
   rod('CABIN_upper_reading_stem',(xx,-1.465,3.438),(xx,-1.387,3.408),.009,steel,14,coll=inter)
   box('CABIN_upper_reading_head',(xx,-1.369,3.392),(.095,.065,.032),ivory,.012,coll=inter)
   box('CABIN_upper_reading_lens',(xx,-1.367,3.373),(.073,.047,.007),lamp,.003,coll=inter)
   hx=xx+e*.3725;hy=.23
   box('CABIN_coat_hook_base',(hx,hy,2.77),(.013,.090,.040),steel,.004,coll=inter)
   rod('CABIN_coat_hook',(hx-e*.009,hy,2.77),(hx-e*.065,hy,2.75),.009,steel,12,coll=inter)
   rod('CABIN_coat_hook_tip',(hx-e*.065,hy,2.75),(hx-e*.065,hy,2.795),.009,steel,12,coll=inter)
  cur+=L
