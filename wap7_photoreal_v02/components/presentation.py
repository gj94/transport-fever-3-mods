"""Rebuildable outdoor photographic presentation, excluded from the vehicle source envelope.
Original railway scenery + CC0 Poly Haven pure-sky lighting; no vehicle/photo backplates."""
import bpy,bmesh,math,random,json
from mathutils import Vector,Matrix
from math import pi,sin,cos
from pathlib import Path
import common as C
OUT=Path(__file__).resolve().parents[1]

def mat(n,c,rough=.7,metal=0,variation=.0,scale=150,micro=0):
 m=bpy.data.materials.get('ENV02_'+n) or bpy.data.materials.new('ENV02_'+n);m.use_nodes=True;m.diffuse_color=(*c,1);nt=m.node_tree;nt.nodes.clear();p=nt.nodes.new('ShaderNodeBsdfPrincipled');o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs[0],o.inputs[0]);p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if variation or micro:
  t=nt.nodes.new('ShaderNodeTexCoord');no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=scale;no.inputs['Detail'].default_value=3;nt.links.new(t.outputs['Object'],no.inputs[0])
  if variation:
   r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*(1-variation) for v in c),1);r.color_ramp.elements[-1].color=(*(v*(1+variation) for v in c),1);nt.links.new(no.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
  if micro:
   b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=micro;b.inputs['Strength'].default_value=.30;nt.links.new(no.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
 return m

def apply(context=None):
 random.seed(390027);sc=bpy.context.scene
 for name in ['V02_PRESENTATION_ONLY','ENV02_PHOTOGRAPHIC_RAILWAY']:
  co=bpy.data.collections.get(name)
  if co:
   for o in list(co.objects):bpy.data.objects.remove(o,do_unlink=True)
 col=C.collection('ENV02_PHOTOGRAPHIC_RAILWAY');col['purpose']='Presentation only; exclude from vehicle export and source dimension audit'
 earth=mat('Dry railway formation',(.126,.105,.073),.92,0,.24,2.5,.006)
 # CC0 scanned soil material gives fine aggregate/footprint variation at a documented2m scale.
 nt=earth.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tc=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.5;nt.links.new(tc.outputs['Object'],scale.inputs[0])
 maps={}
 for key,file,colorspace in [('diff','dirt_diff_2k.jpg','sRGB'),('rough','dirt_rough_2k.jpg','Non-Color'),('normal','dirt_nor_gl_2k.jpg','Non-Color'),('height','dirt_disp_2k.exr','Non-Color')]:
  t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(OUT/'environment'/file),check_existing=True);t.image.colorspace_settings.name=colorspace;t.extension='REPEAT';nt.links.new(scale.outputs[0],t.inputs['Vector']);maps[key]=t
 nt.links.new(maps['diff'].outputs['Color'],bs.inputs['Base Color']);nt.links.new(maps['rough'].outputs['Color'],bs.inputs['Roughness'])
 normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.75;nt.links.new(maps['normal'].outputs['Color'],normal.inputs['Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.015;bump.inputs['Strength'].default_value=.30;nt.links.new(maps['height'].outputs['Color'],bump.inputs['Height']);nt.links.new(normal.outputs[0],bump.inputs['Normal']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
 sleepermat=mat('Aged concrete sleeper',(.30,.294,.270),.83,0,.13,440,.00075)
 railweb=mat('Weathered rail web',(.125,.061,.028),.68,.48,.15,65,.00022)
 railhead=mat('Steel running crown',(.34,.36,.37),.24,.96,.04,950,.000025)
 rubber=mat('Rail seat EPDM pads',(.013,.017,.015),.68,0,.05,550,.00008)
 clipmat=mat('Spring steel rail clips',(.055,.043,.028),.48,.72,.09,190,.00008)
 insulator=mat('Rail foot insulator nylon',(.255,.217,.137),.65,0,.09,330,.00008)
 ballast=[mat('Granite ballast '+str(i),c,.87,0,.10,1400,.00032) for i,c in enumerate([(.125,.121,.110),(.159,.153,.140),(.086,.091,.087),(.181,.174,.158),(.059,.064,.061),(.134,.131,.120)])]
 grasses=[mat('Grass '+str(i),c,.90,0,.10,60,.0001) for i,c in enumerate([(.056,.083,.018),(.089,.11,.022),(.16,.139,.060),(.10,.086,.034)])]
 wiremat=mat('OHE copper contact line',(.095,.065,.024),.48,.79,.03,300,.000025)
 galv=mat('Galvanised steel mast',(.29,.32,.315),.49,.72,.035,480,.000045)
 ceramics=mat('Brown glazed line insulators',(.060,.022,.009),.21,0,.02,500,.000012)
 # Ground is an undulating real surface; terrain horizon is not a flat giant slab.
 vs=[];fs=[];N=151
 for j in range(N):
  y=-450+j*6
  for i in range(N):
   x=-450+i*6;z=-.43+.043*sin(.12*x+.6)*cos(.15*y)+.015*sin(.47*x)*sin(.33*y);vs.append((x,y,z))
 for j in range(N-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+N+1,a+N))
 ground=C.mesh('ENV02 undulating ground',vs,fs,earth,None,col,smooth=True)
 uv=ground.data.uv_layers.new(name='Metric2m soil UV')
 for poly in ground.data.polygons:
  for li in poly.loop_indices:
   v=ground.data.vertices[ground.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.5,v.y*.5)
 # Correct broad-gauge rails use the head's inner running gauge faces, not rail centres.
 railprofile=[(-.075,-.172),(.075,-.172),(.075,-.157),(.052,-.148),(.012,-.134),(.007,-.117),(.007,-.051),(.020,-.043),(.030,-.034),(.035,-.021),(.0345,-.009),(.029,-.0028),(.018,-.0008),(0,0),(-.018,-.0008),(-.029,-.0028),(-.0345,-.009),(-.035,-.021),(-.030,-.034),(-.020,-.043),(-.007,-.051),(-.007,-.117),(-.012,-.134),(-.052,-.148),(-.075,-.157)]
 for yc in [0,5.40]:
  # Granular ballast bank cross-section with irregular shoulder edges.
  vs=[];fs=[]
  for k in range(241):
   x=-72+k*.60
   vs += [(x,yc-2.22+random.uniform(-.045,.045),-.435),(x,yc-1.52,-.248),(x,yc+1.52,-.248),(x,yc+2.22+random.uniform(-.045,.045),-.435)]
  fs=[(k*4+j,(k+1)*4+j,(k+1)*4+j+1,k*4+j+1) for k in range(240) for j in range(3)]
  C.mesh('ENV02 compacted ballast formation',vs,fs,ballast[0],None,col)
  for sy in [-1,1]:
   yy=yc+sy*.8725;N=len(railprofile);v=[(x,yy+y,z) for x in [-100,100] for y,z in railprofile];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
   o=C.mesh('ENV02 60kg rail section',v,f,[railweb,railhead],None,col,bevel=.0008)
   for p in o.data.polygons:
    if p.center.z>-.02:p.material_index=1
  # Prestressed sleepers have real tapered plan width and a lower central waist.
  for i in range(-113,114):
   x=i*.60;prof=[(-1.37,.131,-.215),(-1.24,.135,-.199),(-1.02,.140,-.187),(-.73,.132,-.188),(-.45,.112,-.230),(0,.108,-.241),(.45,.112,-.230),(.73,.132,-.188),(1.02,.140,-.187),(1.24,.135,-.199),(1.37,.131,-.215)]
   v=[]
   for y,w,z in prof:v += [(x-w,yc+y,z),(x+w,yc+y,z),(x+w+.022,yc+y,-.354),(x-w-.022,yc+y,-.354)]
   f=[(3,2,1,0),tuple(range((len(prof)-1)*4,len(prof)*4))]+[(k*4+j,k*4+(j+1)%4,(k+1)*4+(j+1)%4,(k+1)*4+j) for k in range(len(prof)-1) for j in range(4)]
   C.mesh('ENV02 prestressed broad gauge sleeper',v,f,sleepermat,None,col,bevel=.006)
   if abs(x)<32:
    for sy in [-1,1]:
     y=yc+sy*.8725
     C.box('ENV02 elastic rail seat',(x,y,-.180),(.246,.212,.015),rubber,None,col,b=.002)
     for ss in [-1,1]:
      yy=y+ss*.102
      C.box('ENV02 rail clip shoulder casting',(x,yy,-.145),(.071,.032,.057),railweb,None,col,b=.008)
      C.box('ENV02 rail foot insulating key',(x,y+ss*.078,-.156),(.088,.033,.026),insulator,None,col,b=.003)
      pts=[(x-.053,yy,-.129),(x-.057,yy+ss*.057,-.136),(x+.034,yy+ss*.071,-.133),(x+.076,yy+ss*.029,-.128),(x+.044,yy-ss*.022,-.138),(x-.012,yy-ss*.019,-.142)]
      C.tube('ENV02 elastic spring rail clip',C.bezier_points(pts,5),.0105,clipmat,None,col,N=12)
 # Four dense ballast tiles share real angular rock meshes across distance, never flat photo cards.
 shapes=[]
 for k in range(19):
  bm=bmesh.new();pts=[]
  for j in range(random.randint(11,17)):
   a=random.random()*2*pi;z=random.uniform(-1,1);r=math.sqrt(1-z*z)*random.uniform(.83,1.15);pts.append(bm.verts.new((r*cos(a),r*sin(a),z*random.uniform(.55,.95))))
  bmesh.ops.convex_hull(bm,input=pts,use_existing_faces=False);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();idx={v:i for i,v in enumerate(bm.verts)}
  shapes.append(([tuple(v.co) for v in bm.verts],[tuple(idx[v] for v in f.verts) for f in bm.faces]));bm.free()
 for tile in range(4):
  vs=[];fs=[];mis=[]
  for k in range(10300):
   x=random.uniform(-3.0,3.0);y=random.uniform(-2.205,2.205);r=random.uniform(.021,.047)
   z=-.246 if abs(y)<1.52 else -.246-(abs(y)-1.52)*.272
   z+=random.uniform(-.010,.017);sx=r*random.uniform(.78,1.42);sy=r*random.uniform(.73,1.27);sz=r*random.uniform(.49,.85);a=random.random()*2*pi
   vv,ff=random.choice(shapes);base=len(vs)
   for xx,yy,zz in vv:vs.append((x+xx*sx*cos(a)-yy*sy*sin(a),y+xx*sx*sin(a)+yy*sy*cos(a),z+zz*sz))
   fs.extend(tuple(base+j for j in f) for f in ff);mi=random.choices(range(6),[24,17,17,9,11,22])[0];mis.extend([mi]*len(ff))
  me=bpy.data.meshes.new('ENV02 angular ballast tile '+str(tile));me.from_pydata(vs,[],fs);me.update()
  for m in ballast:me.materials.append(m)
  for p,mi in zip(me.polygons,mis):p.material_index=mi
  for yc in [0,5.40]:
   for j in range(-11,12):
    if (j+11)%4!=tile:continue
    o=bpy.data.objects.new('ENV02 dense ballast instances',me);col.objects.link(o);o.location=(j*6,yc,0)
    if j%2:o.rotation_euler.z=pi
 # Grass tufts and dry grasses root in soil outside the ballast shoulder.
 vs=[];fs=[];mi=[]
 for k in range(1400):
  x=random.choice([-63,-42,-23,-7,8,19,36,53,72])+random.gauss(0,1.5);y=random.choice([-1,1])*(2.5+abs(random.gauss(0,.42)))
  if random.random()<.25:y+=5.4
  z=-.43+.043*sin(.12*x+.6)*cos(.15*y)+.015*sin(.47*x)*sin(.33*y)-.012;h=random.uniform(.045,.16)
  for j in range(random.randint(5,10)):
   a=random.random()*2*pi;hh=h*random.uniform(.5,1.2);w=random.uniform(.0017,.004);lean=random.uniform(.05,.16);b=len(vs)
   for t in [0,.45,1]:
    xx=x+cos(a)*lean*t*t;yy=y+sin(a)*lean*t*t;ww=w*(1-t*.83);vs.extend([(xx-sin(a)*ww,yy+cos(a)*ww,z+hh*t),(xx+sin(a)*ww,yy-cos(a)*ww,z+hh*t)])
   fs.extend([(b,b+1,b+3,b+2),(b+2,b+3,b+5,b+4)]);idx=random.randrange(4);mi.extend([idx,idx])
 o=C.mesh('ENV02 rooted ballast edge grasses',vs,fs,grasses,None,col)
 for p,i in zip(o.data.polygons,mi):p.material_index=i
 # Restrained industrial mass replaces the artificial empty horizon and sparse fake trees.
 import depot
 depot.apply(col,mat)
 # Single railway electrification run; raised rear collector meets actual5.53m wire plane.
 for x in [-62,-18,26,70]:
  y=3.2
  C.box('ENV02 catenary concrete foundation',(x,y,-.03),(.65,.63,.74),sleepermat,None,col,b=.016)
  for dx in [-.085,.085]:C.box('ENV02 H-mast steel flange',(x+dx,y,3.28),(.018,.240,6.82),galv,None,col,b=.002)
  C.box('ENV02 H-mast web',(x,y,3.28),(.171,.015,6.82),galv,None,col,b=.002)
  for z in [.17,.32]:
   for dx in [-.11,.11]:C.cyl('ENV02 foundation anchor bolt',(x+dx,y-.18,z),.014,.08,clipmat,None,col,N=6)
  C.rod('ENV02 OHE cantilever stay',(x,y,6.60),(x,-.18,6.11),.024,galv,None,col,N=16)
  C.rod('ENV02 OHE compression stay',(x,y,5.12),(x,.15,6.16),.026,galv,None,col,N=16)
  C.rod('ENV02 OHE registration arm',(x,1.02,5.61),(x,0,5.53),.019,galv,None,col,N=14)
  C.rod('ENV02 adjacent-track cantilever',(x,y,6.55),(x,5.58,6.11),.024,galv,None,col,N=16)
  C.rod('ENV02 adjacent-track compression stay',(x,y,5.19),(x,5.25,6.16),.026,galv,None,col,N=16)
  C.rod('ENV02 adjacent-track registration arm',(x,4.48,5.61),(x,5.4,5.53),.019,galv,None,col,N=14)
  for yy,zz in [(2.62,6.516),(2.65,5.26)]:
   profile=[]
   for k in range(7):
    a=k*.043;profile.extend([(a,.024),(a+.011,.078),(a+.021,.078),(a+.028,.030),(a+.043,.024)])
   C.lathe('ENV02 OHE porcelain stay insulator',(x,yy,zz),profile,ceramics,None,col,'Y',32)
 for yc in [0,5.4]:
  C.rod('ENV02 contact copper wire',(-105,yc,5.53),(105,yc,5.53),.0058,wiremat,None,col,N=10)
  pts=[]
  for j in range(141):
   x=-105+j*1.5;phase=((x+18)%44)/44;pts.append((x,yc,6.17-.24*sin(pi*phase)))
  C.tube('ENV02 messenger catenary',pts,.0065,wiremat,None,col,N=10)
  for x in range(-102,103,6):
   phase=((x+18)%44)/44;C.rod('ENV02 catenary droppers',(x,yc,5.536),(x,yc,6.17-.24*sin(pi*phase)),.0026,wiremat,None,col,N=8)
 # Scene lighting uses actual unclipped HDR radiance. Stage transforms/report record orientation.
 w=bpy.data.worlds.new('ENV02 Poly Haven CC0 pure sky');sc.world=w;w.use_nodes=True;nt=w.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputWorld');bg=nt.nodes.new('ShaderNodeBackground');tex=nt.nodes.new('ShaderNodeTexEnvironment');im=bpy.data.images.load(str(OUT/'environment/kloofendal_48d_partly_cloudy_puresky_2k.hdr'),check_existing=True);tex.image=im
 tc=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=math.radians(11);nt.links.new(tc.outputs['Generated'],mapping.inputs['Vector']);nt.links.new(mapping.outputs[0],tex.inputs[0]);nt.links.new(tex.outputs[0],bg.inputs[0]);bg.inputs['Strength'].default_value=.95;nt.links.new(bg.outputs[0],out.inputs['Surface'])
 def camera(n,loc,target,lens=60):
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.03;d.clip_end=500;d.dof.use_dof=False;return o
 hero=camera('V02_CAM_HERO',(30.7,-12.8,1.85),(1.0,0,2.36),89)
 hero.data.dof.use_dof=True;hero.data.dof.focus_distance=(hero.location-Vector((1.0,0,2.36))).length;hero.data.dof.aperture_fstop=6.3
 camera('V02_CAM_CAB',(16.5,-9.0,3.5),(8.25,-.1,2.6),74)
 camera('V02_CAM_FRONT',(24,-.7,2.7),(9.45,0,2.40),104)
 camera('V02_CAM_BOGIE',(8.0,-8.5,1.45),(6,-.05,1.03),65)
 camera('V02_CAM_COUPLER',(13.1,-2.8,1.65),(9.94,-.05,1.15),67)
 camera('V02_CAM_COUPLER_TOP',(12.8,-2.2,2.85),(10.0,0,1.15),74)
 camera('V02_CAM_ROOF',(.5,-9.2,8.2),(-3.1,0,4.34),58)
 camera('V02_CAM_PANTOGRAPH',(-1.7,-5.5,5.8),(-4.8,0,4.7),64)
 camera('V02_CAM_SIDE',(0,-36,2.9),(0,0,2.65),57)
 # A broad weak reflected-light fill represents open pale ground outside the frame.
 d=bpy.data.lights.new('ENV02 soft trackside ground bounce','AREA');d.energy=280;d.shape='RECTANGLE';d.size=18;d.size_y=3
 o=bpy.data.objects.new(d.name,d);col.objects.link(o);o.location=(1,-8,2.2);o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
 sc.camera=bpy.data.objects['V02_CAM_HERO']
 return {'collection':col.name,'source':'Original geometry, CC0 Poly Haven pure sky for lighting only','sky':'https://polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky','sky_rotation_degrees':11,'world_strength':.95,'render_only':True,'ballast_unique_tiles':4,'rocks_per_tile':10300}
