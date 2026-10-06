"""Refine the accepted WAP7 live-rig master. Blender 4.3.2; metres; X forward.
Creates editable geometry and procedural/packed-image PBR materials, never photographic projections.
The caller supplies the accepted baseline path; no game resources are modified.
"""
import bpy, math, random, json, sys, os, hashlib, time
from pathlib import Path
from mathutils import Vector, Matrix
from math import pi, sin, cos
random.seed(19002)
OUT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else OUT.parent/'pantograph_v04/WAP7_pantograph_v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene; root=bpy.data.objects['WAP7_ROOT']; body=bpy.data.objects['BODY']
# Presentation is replaced, not mixed with the old studio.
for o in list(bpy.data.collections['PRESENTATION_ONLY'].objects): bpy.data.objects.remove(o,do_unlink=True)
asset=bpy.data.collections.new('PHOTOREAL_REFINEMENT');scene.collection.children.link(asset)
stage=bpy.data.collections['PRESENTATION_ONLY'];stage['purpose']='Render environment only; exclude from vehicle export'
created=[]
def material(n,col,metal=0,rough=.5,noise=0,bump=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*col,1);nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if noise:
  tc=nt.nodes.new('ShaderNodeTexCoord');no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=22;no.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['Object'],no.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*(max(.002,c*(1-noise)) for c in col),1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(min(1,c*(1+noise)) for c in col),1);nt.links.new(no.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
  mr=nt.nodes.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=max(.03,rough-.08);mr.inputs['To Max'].default_value=min(.98,rough+.10);nt.links.new(no.outputs['Fac'],mr.inputs[0]);nt.links.new(mr.outputs[0],p.inputs['Roughness'])
  if bump:
   fine=nt.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=230;fine.inputs['Detail'].default_value=2;nt.links.new(tc.outputs['Object'],fine.inputs[0]);bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.23;bn.inputs['Distance'].default_value=bump;nt.links.new(fine.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs['Normal'],p.inputs['Normal'])
 return m
def setmat(o,m):
 if hasattr(o.data,'materials'):o.data.materials.clear();o.data.materials.append(m)
paint=material('PBR • aged signal-white enamel',(.78,.77,.72),.12,.35)
# World-position planar projection gives coherent body wear across the shell and separate doors.
nt=paint.node_tree;p=nt.nodes.get('Principled BSDF');g=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],sep.inputs[0]);comb=nt.nodes.new('ShaderNodeCombineXYZ')
for axis,ofs,div in [('X',9.6,19.2),('Z',-1.44,2.38)]:
 ad=nt.nodes.new('ShaderNodeMath');ad.operation='ADD';ad.inputs[1].default_value=ofs;nt.links.new(sep.outputs[axis],ad.inputs[0]);dv=nt.nodes.new('ShaderNodeMath');dv.operation='DIVIDE';dv.inputs[1].default_value=div;nt.links.new(ad.outputs[0],dv.inputs[0]);nt.links.new(dv.outputs[0],comb.inputs[0 if axis=='X' else 1])
for filename,inputname in [('body_enamel_albedo.png','Base Color'),('body_enamel_roughness.png','Roughness')]:
 tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'textures'/filename));tex.image.pack();tex.extension='EXTEND';nt.links.new(comb.outputs[0],tex.inputs[0]);nt.links.new(tex.outputs['Color'],p.inputs[inputname]);
 if inputname=='Roughness':tex.image.colorspace_settings.name='Non-Color'
no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=320;no.inputs['Detail'].default_value=2;nt.links.new(g.outputs['Position'],no.inputs[0]);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.11;bump.inputs['Distance'].default_value=.00038;nt.links.new(no.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal']);p.inputs['Coat Weight'].default_value=.13;p.inputs['Coat Roughness'].default_value=.3
red=material('PBR • vermilion oxide stripe',(.49,.068,.022),.08,.39,.06,.0005)
roof=material('PBR • soot-grey roof enamel',(.082,.081,.070),.33,.46,.15,.00018)
frame=material('PBR • dusty cast bogie steel',(.070,.057,.039),.42,.62,.28,.0006)
edge=material('PBR • rubbed black metal',(.024,.024,.020),.50,.42,.4,.0006)
buffermat=material('PBR • rubbed buffer-face steel',(.047,.042,.034),.65,.49,.18,.00025)
steel=material('PBR • polished steel contact edges',(.36,.37,.35),.88,.25,.12,.00018)
rust=material('PBR • aged iron oxide',(.14,.059,.020),.38,.71,.48,.0013)
dust=material('PBR • deposited ochre dust',(.20,.16,.105),.1,.86,.30,.001)
rubber=material('PBR • weathered EPDM',(.012,.014,.013),0,.68,.15,.0004)
ceramic=material('PBR • glazed brown porcelain',(.075,.032,.012),.05,.20,.13,.0001)
copper=material('PBR • dark oxidised copper bus',(.23,.095,.025),.78,.42,.3,.0004)
panto=material('PBR • worn ochre pantograph paint',(.32,.22,.080),.12,.52,.20,.0004)
navy=material('PBR • charcoal markings',(.014,.020,.021),0,.5)
white=material('PBR • cream stencil paint',(.65,.62,.49),0,.57)
# Thick, genuinely transmissive glass with restrained tint. Interior remains visible.
glass=material('PBR • laminated cab glazing',(.82,.91,.91),0,.065)
gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=1;gp.inputs['IOR'].default_value=1.46
lampglass=material('PBR • clear prismatic lamp lens',(.89,.93,.91),0,.12);lampglass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.75
redlens=material('PBR • dark ruby marker lens',(.30,.009,.004),.1,.2);redlens.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.65
# All source interior meshes are left untouched. Their material assets are left untouched too.
oldmap={'Signal white | RAL9003 approximation':paint,'Oxide red belt':red,'Graphite underframe':frame,'Rubber and cavities':rubber,'Machined wheel rims':steel,'Smoked blue cab glazing':glass,'Roof grey':roof,'Copper HV conductor':copper,'Pantograph ochre':panto,'Brown ceramic insulators':ceramic,'Headlamp lenses':lampglass,'Handrail silver':edge,'Railway lettering':navy,'CBC cast steel v03':frame}
for o in list(bpy.data.objects):
 if o.name in bpy.data.collections['CAB_INTERIORS_V02'].objects:continue
 if hasattr(o.data,'materials'):
  for i,m in enumerate(o.data.materials):
   if m and m.name in oldmap:o.data.materials[i]=oldmap[m.name]
# Exact preserved root/pivot transforms; added meshes use world coordinates with inverse parent matrices.
def mesh(n,verts,faces,m,parent=body,coll=asset,bevel=0,smooth=False):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);coll.objects.link(o)
 if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
 if m:me.materials.append(m)
 if bevel:mod=o.modifiers.new('True manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Face-weighted normals','WEIGHTED_NORMAL')
 if smooth:
  for f in me.polygons:f.use_smooth=True
 created.append(o);return o
def box(n,c,d,m,parent=body,coll=asset,b=.006):
 x,y,z=[v/2 for v in d];X,Y,Z=c;v=[(X+a,Y+bb,Z+cc) for a,bb,cc in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]];return mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,parent,coll,b)
def cyl(n,c,r,d,m,parent=body,axis='Z',N=32,coll=asset):
 v=[(r*cos(2*pi*i/N),r*sin(2*pi*i/N),z) for z in [-d/2,d/2] for i in range(N)];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 if axis=='Y':v=[(a,cc,-bb) for a,bb,cc in v]
 if axis=='X':v=[(cc,bb,-a) for a,bb,cc in v]
 v=[(a+c[0],bb+c[1],cc+c[2]) for a,bb,cc in v];o=mesh(n,v,f,m,parent,coll)
 for p in o.data.polygons:
  if len(p.vertices)==4:p.use_smooth=True
 return o
def tube(n,points,r,m,parent=body,coll=asset,N=10):
 pts=[Vector(p) for p in points];vs=[]
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();q=tangent.to_track_quat('Z','Y')
  vs += [tuple(p+q@Vector((r*cos(2*pi*j/N),r*sin(2*pi*j/N),0))) for j in range(N)]
 fs=[tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))]+[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
 return mesh(n,vs,fs,m,parent,coll,smooth=True)
def rod(n,a,b,r,m,parent=body,coll=asset,N=12):return tube(n,[a,b],r,m,parent,coll,N)
def ring(n,c,ro,ri,d,m,parent=body,axis='Y',N=48):
 v=[]
 for z,r in [(-d/2,ro),(d/2,ro),(-d/2,ri),(d/2,ri)]:
  for i in range(N):
   a,b=r*cos(2*pi*i/N),r*sin(2*pi*i/N);pt=(a,z,b) if axis=='Y' else (z,a,b) if axis=='X' else (a,b,z);v.append(tuple(pt[k]+c[k] for k in range(3)))
 f=[]
 for i in range(N):
  j=(i+1)%N;f += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)]
 return mesh(n,v,f,m,parent,bevel=.001,smooth=True)
def bolt(n,c,r=.017,d=.016,parent=body,axis='Y',m=steel):return cyl(n,c,r,d,m,parent,axis,6)
def remove_prefixes(prefixes):
 for o in list(bpy.data.objects):
  if o.name.startswith(tuple(prefixes)):bpy.data.objects.remove(o,do_unlink=True)
def textmat(file):
 name='DECAL • '+file
 if name in bpy.data.materials:return bpy.data.materials[name]
 m=material(name,(1,1,1),0,.53);nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'textures'/file));tex.image.pack();nt.links.new(tex.outputs['Color'],p.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);return m
def decal(n,file,c,w,h,side=-1,end=None):
 # Quad is almost flush paint, not a raised sign. Correct reading on both sides.
 x,y,z=c
 if end is None:
  sx=1 if side==-1 else -1;v=[(x-sx*w/2,y,z-h/2),(x+sx*w/2,y,z-h/2),(x+sx*w/2,y,z+h/2),(x-sx*w/2,y,z+h/2)]
 else:
  sy=end;v=[(x,y-sy*w/2,z-h/2),(x,y+sy*w/2,z-h/2),(x,y+sy*w/2,z+h/2),(x,y-sy*w/2,z+h/2)]
 o=mesh(n,v,[(0,1,2,3)],textmat(file));uv=o.data.uv_layers.new()
 for j,co in zip(o.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=co
 return o
# Cab roofs have dark curved shoulders rather than white flat caps.
shell=bpy.data.objects['Chamfered welded body shell'];shell.data.materials.append(roof)
for p in shell.data.polygons:
 if p.center.z>3.555:p.material_index=len(shell.data.materials)-1
for o in bpy.data.objects:
 if o.name.startswith(('Cab roof horn enclosure','Horn trumpet stem','Horn flared bell','Horn mouth')):o.location.z+=.11
# Curved cab roof crown over the preserved aperture shell: rounded shoulders and a falling front brow.
for end in [-1,1]:
 vs=[];sections=[(7.18,1.448,3.842),(7.70,1.448,3.948),(8.30,1.448,3.988),(8.65,1.430,3.934),(8.88,1.380,3.805),(9.05,1.293,3.658),(9.166,1.192,3.557)]
 for x,w,top in sections:
  for j in range(25):
   yn=-1+j/12;z=3.553+(top-3.553)*max(0,cos(yn*pi/2))**.43;vs.append((end*x,w*yn,z))
 fs=[(i*25+j,i*25+j+1,(i+1)*25+j+1,(i+1)*25+j) for i in range(len(sections)-1) for j in range(24)]
 if end==1:fs=[tuple(reversed(f)) for f in fs]
 mesh('Formed curved cab roof crown',vs,fs,roof,smooth=True)
# Exterior welded corner patches close old cavity-cut slivers without editing either cab interior.
for end in [-1,1]:
 for sy in [-1,1]:
  vv=[]
  for zz in [2.350,3.552]:
   L=9.52-max(zz-2.35,0)*.35/1.2
   vv += [(end*(L+.0018),sy*(1.296*body.scale.y+.0018),zz),(end*(L-.36+.0018),sy*(1.576*body.scale.y+.0018),zz)]
  mesh('Continuous welded cab-corner skin',vv,[(0,1,3,2)] if end*sy>0 else [(2,3,1,0)],paint)
# Cast roof searchlight housing replaces a generic featureless box.
remove_prefixes(['Cab roof horn enclosure'])
for end in [-1,1]:
 box('Cab central roof lamp housing',(end*8.58,0,4.105),(.39,.35,.25),roof,b=.035)
 box('Cab roof lamp face recess',(end*8.782,0,4.108),(.012,.281,.188),rubber,b=.027)
 ring('Cab roof lamp bezel',(end*8.793,0,4.108),.087,.072,.014,edge,axis='X')
 cyl('Cab roof lamp lens',(end*8.804,0,4.108),.070,.016,lampglass,axis='X',N=48)
# Replace incorrectly repeating louvres and grey panel bars with asymmetric screened filters.
remove_prefixes(['Air intake rim','Recessed intake screen','Intake horizontal slat','Intake screen mullion','Shell vertical joint','Indian Railways bodyside','Class designation','Windscreen protection','Wiper arm','Wiper blade','Marker lamp body','Marker lamp red lens','Tricolour marking','Nose safety railing','Pilot vertical strut','Pilot transverse bar'])
# Recess shadow, sheet-metal frame, fine wire mesh and mullions; distinct both side arrangements.
for s in [-1,1]:
 y=s*1.486
 layouts=[(4.78,.78,1.43,2.91),(-3.92,.52,1.20,3.02),(-6.2,.40,.47,3.10),(-6.72,.40,.47,3.10)] if s==-1 else [(-4.80,1.43,1.30,2.94),(3.85,.52,1.30,2.96),(6.22,.38,.47,3.10),(6.70,.38,.47,3.10)]
 for gi,(x,w,h,z) in enumerate(layouts):
  box('Filter perimeter gasket',(x,y,z),(w+.11,.019,h+.10),rubber,b=.018)
  box('Filter recessed cavity',(x,y+s*.013,z),(w,.012,h),edge,b=.009)
  for dx in [-w/2,w/2]:box('Filter formed vertical rim',(x+dx,y+s*.030,z),(.026,.038,h+.06),roof,b=.006)
  for dz in [-h/2,h/2]:box('Filter formed end rim',(x,y+s*.030,z+dz),(w+.046,.041,.031),roof,b=.006)
  # Individual fine screens are dimensional geometry and shade as actual mesh.
  for i in range(int(w/.026)):
   xx=x-w/2+.019+i*.026;rod('Intake vertical screen wire',(xx,y+s*.036,z-h/2+.014),(xx,y+s*.036,z+h/2-.014),.0024,frame,N=6)
  for i in range(int(h/.025)):
   zz=z-h/2+.014+i*.025;rod('Intake horizontal screen wire',(x-w/2+.012,y+s*.038,zz),(x+w/2-.012,y+s*.038,zz),.0022,frame,N=6)
  if w>1:
   for dx in [0]:box('Filter central mullion',(x+dx,y+s*.047,z),(.017,.025,h),roof,b=.002)
   box('Filter horizontal mullion',(x,y+s*.047,z),(w,.025,.019),roof,b=.002)
  for dx in [-w/2,w/2]:
   for zz in [-h/2+.07,0,h/2-.07]:bolt('Filter frame screw',(x+dx,y+s*.058,z+zz),.009,.010,axis='Y',m=edge)
 # Correct large, condensed class railway lettering and running number.
 decal('Railway painted lettering','railway_english.png' if s==-1 else 'railway_hindi.png',(.15,s*1.459,2.94),5.4 if s==-1 else 3.9,.58,side=s)
 decal('Large running number','number_red.png',(.05,s*1.459,1.715),1.67,.32,side=s)
 # Flush sheet joints, seam beads, roof rain gutter, subtle lower edge break.
 for x in [-7.28,-5.78,-2.95,0,2.95,5.78,7.28]:
  rod('Body welded seam',(x,s*1.456,2.23),(x,s*1.456,3.54),.0018,roof,N=6)
 tube('Continuous eaves rain gutter',[(-8.92,s*1.328,3.66),(-7.25,s*1.405,3.66),(7.25,s*1.405,3.66),(8.93,s*1.328,3.66)],.022,roof,N=12)
 for x in [-7.38,7.38]:
  tube('Cab rain downpipe',[(x,s*1.470,3.63),(x,s*1.486,3.33),(x,s*1.486,1.66)],.015,roof,N=8)
 for x in [-2.8,2.8]:decal('Jacking stencil','lift.png',(x,s*1.459,1.395),.27,.055,side=s)
 for end in [-1,1]:
  decal('Cab identification stencil','cab1.png' if end==1 else 'cab2.png',(end*7.78,s*1.513,2.52),.34,.075,side=s)
  decal('Locomotive technical stencil','technical.png',(end*6.98,s*1.459,2.48),.31,.19,side=s)
  # Door kick plate and real tread grating; source aperture/door retained.
  box('Brushed cab door kickplate',(end*7.80,s*1.511,1.735),(.51,.009,.235),steel,b=.005)
  for dx in [-.22,.22]:
   for zz in [1.64,1.82]:bolt('Kickplate fastener',(end*7.8+dx,s*1.519,zz),.007,.005,axis='Y',m=edge)
  for zz in [1.0,1.22,1.44]:
   for i in range(10):box('Cab tread serration',(end*7.8-.26+i*.057,s*1.43,zz+.026),(.012,.24,.01),edge,b=.001)
# Front stripe widened very slightly and continues around chamfered cab corners.
for o in bpy.data.objects:
 if o.name.startswith(('Continuous red bodyside band','Front red band')):
  o.scale.z=1.23
for end in [-1,1]:
 for s in [-1,1]:
  v=[(end*x,s*y,z) for z in [1.892,2.188] for x,y in [(9.075,1.460),(9.163,1.460),(9.523,1.198)]];mesh('Continuous red stripe across cab bevel',v,[(0,1,4,3),(1,2,5,4)],red)
 # Dark rounded roof brow and sunshade lip follow existing openings.
 for sy in [-1,1]:
  y=sy*.618
  def fx(z):return end*(9.52-max(z-2.35,0)*.35/1.2+.055)
  # rounded rectangular protection cage with bent corners, spaced from glass
  w,h,r=1.062,.933,.084;zc=3.015
  pts=[]
  for cy,cz,start in [(y+w/2-r,zc+h/2-r,0),(y-w/2+r,zc+h/2-r,90),(y-w/2+r,zc-h/2+r,180),(y+w/2-r,zc-h/2+r,270)]:
   for i in range(8):
    a=math.radians(start+i*90/7);yy=cy+r*cos(a);zz=cz+r*sin(a);pts.append((fx(zz)+end*.055,yy,zz))
  # start corners formulation fixed with standard four quarter arcs around Y/Z
  pts=[]
  for cy,cz,start in [(y+w/2-r,zc+h/2-r,0),(y-w/2+r,zc+h/2-r,90),(y-w/2+r,zc-h/2+r,180),(y+w/2-r,zc-h/2+r,270)]:
   for i in range(9):
    a=math.radians(start+i*90/8);yy=cy+r*cos(a);zz=cz+r*sin(a);pts.append((fx(zz)+end*.071,yy,zz))
  pts.append(pts[0]);tube('Rounded windshield protection cage',pts,.019,edge,N=10)
  for j in range(13):
   yy=y-.46+j*.077;rod('Fine windshield guard bar',(fx(2.62)+end*.066,yy,2.62),(fx(3.40)+end*.066,yy,3.40),.0065,edge,N=8)
  for zz in [2.59,2.67,3.36,3.44]:rod('Guard horizontal frame',(fx(zz)+end*.076,y-.49,zz),(fx(zz)+end*.076,y+.49,zz),.011,edge,N=10)
  for yy in [y-.55,y+.55]:
   for zz in [2.68,3.33]:box('Cage mounting hinge',(fx(zz)+end*.015,yy,zz),(.09,.05,.075),frame,b=.007);bolt('Cage mounting bolt',(fx(zz)+end*.066,yy,zz),.012,.016,axis='X',m=edge)
  # Wiper sits behind protective cage, with a pivot and articulated blade.
  rod('Wiper swept arm',(fx(2.54)-end*.014,y+.18,2.54),(fx(2.92)-end*.014,y-.08,2.92),.011,edge)
  rod('Wiper rubber blade',(fx(2.85)-end*.007,y-.12,2.85),(fx(3.20)-end*.007,y-.19,3.20),.014,rubber)
  cyl('Wiper spindle',(fx(2.53),y+.18,2.53),.031,.043,edge,axis='X')
 # Stacked paired corner markers; glass behind machined rings.
 for y in [-1.02,1.02]:
  box('Marker lamps pressed housing',(end*9.555,y,2.00),(.058,.231,.400),roof,b=.025)
  box('Marker lamps inset',(end*9.589,y,2.00),(.010,.188,.354),rubber,b=.018)
  for z,m in [(2.085,lampglass),(1.916,redlens)]:
   ring('Marker lamp circular bezel',(end*9.602,y,z),.080,.064,.018,steel,axis='X');cyl('Marker lens',(end*9.612,y,z),.062,.019,m,axis='X',N=48)
   for j in range(-4,5):rod('Marker lens fluting',(end*9.627,y+j*.011,z-.048),(end*9.627,y+j*.011,z+.048),.0015,m,N=6)
 # A restrained realistic two-lamp reflector assembly instead of flat luminous disks.
 for y in [-.143,.143]:
  ring('Headlight polished inner ring',(end*9.710,y,1.99),.100,.079,.016,steel,axis='X')
  cyl('Headlight reflector',(end*9.708,y,1.99),.078,.010,steel,axis='X',N=48)
  cyl('Halogen bulb cap',(end*9.721,y,1.99),.020,.032,lampglass,axis='X',N=20)
  for j in range(-6,7):
   yy=y+j*.012;hh=math.sqrt(max(.00001,.09*.09-(j*.012)**2));rod('Headlight lens refractive rib',(end*9.728,yy,1.99-hh),(end*9.728,yy,1.99+hh),.0013,lampglass,N=6)
 # Nose safety handrail bends and bracketry in the real lamp plane.
 tube('Nose bent grab rail',[(end*9.625,-1.14,1.54),(end*9.625,-1.14,2.31),(end*9.625,-1.10,2.35),(end*9.625,1.10,2.35),(end*9.625,1.14,2.31),(end*9.625,1.14,1.54)],.017,edge,N=12)
 for y in [-1.14,1.14]:
  for z in [1.57,2.30]:bolt('Front grabrail bracket',(end*9.630,y,z),.019,.018,axis='X',m=steel)
 decal('National tricolour','indian_flag.png',(end*9.563,-.61*end,2.01),.49,.292,end=end)
 decal('Front railway zone','sr.png',(end*9.552,-.54*end,2.253),.22,.118,end=end)
 decal('Front shed code','rpm.png',(end*9.552,.54*end,2.253),.32,.118,end=end)
 decal('Front class','class.png',(end*9.555,-.84*end,1.585),.46,.128,end=end)
 decal('Front running number','number_black.png',(end*9.555,.83*end,1.585),.53,.128,end=end)
 decal('Front shed name','shed.png',(end*9.555,0,1.586),.78,.124,end=end)
 decal('Front HOG equipment designation','hog.png',(end*9.554,0,1.756),.55,.077,end=end)
 decal('Shed crest','shed_emblem.png',(end*9.560,0,2.401),.27,.27,end=end)
 # HOG connectors and drooping air lines use multi-segment real tubular geometry.
 for sy in [-1,1]:
  y=sy*.53
  box('Jumper socket square mount',(end*9.61,y,1.77),(.12,.19,.20),frame,b=.015)
  ring('Jumper socket circular flange',(end*9.70,y,1.77),.067,.045,.020,steel,axis='X')
  tube('HOG flexible jumper',[(end*9.70,y,1.75),(end*9.80,y,1.45),(end*9.84,y*.9,.96),(end*9.71,y*.75,.76),(end*9.52,y*.7,.83)],.036,rubber,N=14)
  for zz in [1.43,1.38,1.33]:ring('Jumper corrugated sleeve',(end*9.74,y,zz),.040,.034,.014,edge,axis='Z',N=16)
 # More faithful boxed lattice pilot with a high number of light bars, open to track behind.
 corners=[(-1.30,.38),(-1.43,.53),(-1.37,.95),(1.37,.95),(1.43,.53),(1.30,.38),(-1.30,.38)]
 tube('Pilot perimeter',[(end*(9.53+(z-.6)*.2),y,z) for y,z in corners],.038,frame,N=12)
 for y in [-1.16,-.93,-.70,-.47,-.235,0,.235,.47,.70,.93,1.16]:rod('Pilot vertical lattice',(end*9.49,y,.42),(end*9.58,y,.93),.012,frame,N=8)
 for zz in [.48,.62,.77,.91]:rod('Pilot horizontal lattice',(end*(9.53+(zz-.6)*.2),-1.34,zz),(end*(9.53+(zz-.6)*.2),1.34,zz),.014,frame,N=8)
 box('Pilot lower sacrificial edge',(end*9.505,0,.384),(.085,2.60,.088),frame,b=.012)
# Visible source wheels/frame receive differentiated service finishes, not chrome coils.
for o in bpy.data.objects:
 if o.name.startswith(('Primary coil spring','Secondary suspension coil','Axlebox bearing cover','Brake rigging','Lateral suspension link','Wheel disc','Wheel outer web','Buffer plate','Buffer shank')):setmat(o,frame)
 if o.name.startswith('Wheel tyre'):setmat(o,steel)
 if o.name.startswith('Buffer plate'):setmat(o,buffermat)
 if o.name.startswith('Bogie fabricated side beam'):o.hide_render=True;o.hide_viewport=True;o['replaced_by']='Detailed cast bogie cheek below'
# Cast bogie plates, ribs, axlebox covers, dampers, pneumatic lines, fasteners and brake rigging.
for bi,bx in enumerate([-6,6]):
 bog=bpy.data.objects['BOGIE_%s_YAW_Z'%('A' if bi==0 else 'B')]
 for s in [-1,1]:
  # Top frame has deep cast profiles around the primary spring pockets.
  profile=[(-2.84,.99),(-2.77,1.20),(-2.27,1.22),(-2.10,1.07),(-1.60,1.07),(-1.47,1.18),(-.47,1.18),(-.31,1.08),(.31,1.08),(.47,1.18),(1.47,1.18),(1.60,1.07),(2.10,1.07),(2.27,1.22),(2.77,1.20),(2.84,.99),(2.62,.72),(2.22,.69),(2.08,.84),(1.59,.84),(1.40,.76),(.42,.76),(.27,.83),(-.27,.83),(-.42,.76),(-1.40,.76),(-1.59,.84),(-2.08,.84),(-2.22,.69),(-2.62,.72)]
  verts=[(bx+x,s*(1.15+yy),z) for yy in [-.12,.12] for x,z in profile];n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh('Cast three-axle bogie cheek',verts,faces,frame,bog,bevel=.024)
  for dx in [-2.45,-1.05,1.05,2.45]:
   box('Bogie cast stiffening rib',(bx+dx,s*1.286,.984),(.057,.070,.39),frame,bog,b=.008)
   bolt('Bogie structural hex fastener',(bx+dx,s*1.332,1.145),.024,.026,bog,m=edge)
  for ai,dx in enumerate([-1.85,0,1.85]):
   ax=bpy.data.objects['AXLE_%s_%d_ROLL_Y'%('A' if bi==0 else 'B',ai+1)]
   ring('Wheel forged web ring',(bx+dx,s*1.035,.546),.428,.365,.019,frame,ax)
   ring('Wheel oxidised inner tyre',(bx+dx,s*1.007,.546),.522,.45,.008,rust,ax)
   ring('Wheel polished tread lip',(bx+dx,s*1.015,.546),.545,.527,.025,steel,ax)
   # Axleboxes are fixed to bogie; wheels and hubs follow axle roll.
   box('Axlebox cast lower jaw',(bx+dx,s*1.28,.57),(.39,.26,.285),frame,bog,b=.049)
   cyl('Axlebox end cap',(bx+dx,s*1.423,.584),.113,.034,edge,bog,axis='Y',N=40)
   ring('Axlebox machined cap rim',(bx+dx,s*1.444,.584),.121,.112,.010,frame,bog)
   for k in range(6):
    t=k*pi/3;bolt('Axlebox cover bolt',(bx+dx+.089*cos(t),s*1.45,.584+.089*sin(t)),.012,.016,bog,m=steel)
   for off in [-.37,.37]:
    # Heavy spring retainers seat the inherited coil springs into the casting.
    cyl('Primary spring lower cup',(bx+dx+off,s*1.13,.727),.123,.033,frame,bog)
    cyl('Primary spring upper cup',(bx+dx+off,s*1.13,1.058),.130,.030,frame,bog)
   # Outboard brake pull rod and double clevis ends.
   for dd in [-.53,.53]:
    rod('Brake actuator vertical lever',(bx+dx+dd,s*1.22,.92),(bx+dx+dd*.90,s*1.23,.40),.026,frame,bog)
    for zz in [.44,.88]:cyl('Brake clevis pin',(bx+dx+dd,s*1.265,zz),.037,.050,edge,bog,axis='Y',N=20)
   rod('Brake connecting pull rod',(bx+dx-.46,s*1.30,.435),(bx+dx+.46,s*1.30,.435),.017,rust,bog)
   # Sand pipe terminates ahead of tyre with a clamp.
   xx=bx+dx+.59;tube('Sand delivery pipe',[(xx+.10,s*1.19,1.12),(xx+.05,s*1.14,.70),(xx,s*.96,.25),(xx-.03,s*.94,.12)],.018,frame,bog,N=10)
   for z in [.60,.96]:ring('Pipe clamp',(xx+.045,s*1.14,z),.026,.019,.023,steel,bog,axis='Z',N=16)
  # Diagonal hydraulic dampers have a dark body and partly polished piston rod.
  for dd in [-1.05,1.05]:
   a=Vector((bx+dd,s*1.30,.87));b=Vector((bx+dd+.30,s*1.30,1.40));mid=a.lerp(b,.65);rod('Secondary hydraulic damper body',a,mid,.058,frame,bog);rod('Secondary damper polished piston',mid,b,.021,steel,bog)
   for pt in [a,b]:cyl('Damper eye pin',pt,.055,.080,edge,bog,axis='Y',N=24)
  # Four brake-cylinder bodies per bogie, conventional converted rigging representation.
  for dd in [-2.4,2.4]:
   cyl('Pneumatic brake cylinder',(bx+dd,s*.92,1.18),.116,.40,frame,bog,axis='X',N=32)
   rod('Brake cylinder piston',(bx+dd-.26,s*.92,1.18),(bx+dd-.48,s*.92,1.18),.022,steel,bog)
  tube('Bogie brake air piping',[(bx-2.65,s*1.31,1.245),(bx-1.50,s*1.32,1.27),(bx+1.55,s*1.32,1.27),(bx+2.65,s*1.31,1.245)],.012,edge,bog,N=8)
  for dd in [-2,-1,0,1,2]:box('Air-line retaining clip',(bx+dd,s*1.33,1.262),(.028,.023,.05),steel,bog,b=.003)
  # Four lugs and edge scrapes provide scale without indiscriminate rust coverage.
  for dd in [-1.34,-.66,.66,1.34]:box('Bogie casting pad',(bx+dd,s*1.29,1.105),(.14,.045,.17),frame,bog,b=.010)
# Coupler casting radii, knuckle boss, release linkage and restrained contact scuffing.
for end,label in [(1,'FRONT'),(-1,'REAR')]:
 head=bpy.data.objects['CBC_'+label+'_closed_knuckle_head']
 for mod in head.modifiers:
  if mod.type=='BEVEL':mod.width=.021;mod.segments=5
 cp=bpy.data.objects['CBC_'+label+'_PIVOT']
 cyl('CBC knuckle boss',(end*10.05,end*.105,1.105),.047,.28,frame,cp,N=32)
 ring('CBC pin washer',(end*10.05,end*.105,1.251),.037,.020,.010,steel,cp,axis='Z',N=24)
 box('CBC knuckle cast top rib',(end*10.087,end*.12,1.225),(.21,.036,.026),frame,cp,b=.012)
 tube('CBC mechanical release handle',[(end*9.61,-.85,1.38),(end*9.65,-.61,1.38),(end*9.72,-.27,1.36),(end*10.03,-.09,1.27)],.012,edge,cp,N=10)
 # Dark throat behind the projecting closed knuckle, with a distinct lip.
 box('CBC throat cavity',(end*10.155,-end*.058,1.105),(.015,.074,.133),rubber,cp,b=.020)
 rod('CBC top casting seam',(end*9.97,-end*.15,1.231),(end*10.16,end*.028,1.231),.006,edge,cp,N=8)
 for sy in [-1,1]:
  ring('Buffer polished peripheral contact',(end*10.111,sy*.978,1.105),.231,.207,.003,steel,axis='X',N=64)
  cyl('Buffer central greased contact',(end*10.113,sy*.978,1.105),.138,.003,edge,axis='X',N=64)
# Underbody interstitial apparatus: cabinet seams, closures and electrical raceways.
for s in [-1,1]:
 for x in [-2.30,2.30]:
  box('Underfloor service-panel seam',(x,s*1.15,1.045),(.62,.022,.45),edge,b=.018)
  for dx in [-.25,.25]:
   for zz in [.88,1.22]:bolt('Service cover fastener',(x+dx,s*1.173,zz),.015,.018,m=steel)
  box('Cabinet latch handle',(x,s*1.185,1.05),(.09,.032,.025),steel,b=.004)
 tube('Underframe cable trunking',[(-3.15,s*1.42,1.27),(-2.65,s*1.43,1.25),(2.75,s*1.43,1.25),(3.12,s*1.41,1.30)],.031,edge,N=12)
 for x in [-2.7,-1.8,-.9,0,.9,1.8,2.7]:box('Cable-trunk clamp',(x,s*1.444,1.256),(.032,.05,.087),frame,b=.004)
# Roof fittings: added vented equipment covers, lifting eyes, high-voltage porcelain and clamps.
for x in [-6,-3,0,3,6]:
 for y in [-.99,.99]:
  for dx in [-1.28,1.28]:
   bolt('Roof panel washer bolt',(x+dx,y,3.887),.016,.015,axis='Z',m=edge)
 for y in [-1.07,1.07]:
  tube('Roof-panel lifting eye',[(x-.065,y,3.885),(x-.06,y,3.95),(x+.06,y,3.95),(x+.065,y,3.885)],.010,edge,N=8)
# Photo-visible hood behind each cab, with perforated side faces and framed louvre outlet.
for end in [-1,1]:
 x=end*7.75
 box('Roof ventilation module',(x,0,3.97),(.82,1.17,.28),roof,b=.028)
 for sy in [-1,1]:
  box('Roof-module intake darkness',(x,sy*.592,3.978),(.69,.012,.190),edge,b=.009)
  for i in range(17):rod('Roof-module grille',(x-.33+i*.041,sy*.605,3.895),(x-.33+i*.041,sy*.605,4.065),.005,frame,N=6)
 for zz in [3.9,3.97,4.04]:box('Roof-module end louvre',(x-end*.427,0,zz),(.016,.88,.022),frame,b=.003)
 # flexible corrugated ventilation hose to cab roof module
 pts=[(x+end*.21,-.47,4.03),(x+end*.38,-.54,4.07),(x+end*.62,-.54,4.08)];tube('Cab roof cooling hose',pts,.052,rubber,N=16)
 for j in range(8):ring('Roof hose convolution',(x+end*(.32+j*.045),-.54,4.072),.055,.047,.014,edge,axis='X',N=20)
# Conductor lead path, multiple taller porcelain stacks and switchgear fittings.
for x,y in [(-2.15,-.57),(-.95,-.57),(1.30,-.57),(2.36,-.57)]:
 cyl('HV porcelain pedestal',(x,y,3.97),.095,.22,ceramic)
 for j in range(9):
  z=3.89+j*.032;cyl('HV porcelain shed',(x,y,z),.145-j*.002,.018,ceramic,N=40)
 cyl('Porcelain top terminal',(x,y,4.20),.060,.072,copper)
 bolt('Busbar terminal stud',(x,y,4.235),.021,.027,axis='Z',m=steel)
for x,y in [(-2.15,-.57),(-.95,-.57),(1.30,-.57),(2.36,-.57)]:
 box('Ceramic base mounting plate',(x,y,3.86),(.31,.30,.022),frame,b=.005)
 for dx in [-.11,.11]:
  for dy in [-.11,.11]:bolt('Ceramic flange fixing',(x+dx,y+dy,3.88),.014,.018,axis='Z',m=edge)
tube('Formed high-voltage busbar',[(-4.0,.57,4.15),(-2.70,.57,4.15),(-2.45,.30,4.24),(-2.15,-.57,4.235),(-.95,-.57,4.235),(-.65,-.35,4.20),(.72,-.35,4.20),(1.30,-.57,4.235),(2.36,-.57,4.235),(2.70,.57,4.15),(4.0,.57,4.15)],.017,copper,N=12)
# The prototype's solid pantograph plinth becomes a fabricated open mounting frame.
remove_prefixes(['Pantograph base'])
for px in [-5,5]:
 for sy in [-1,1]:box('Open pantograph mounting frame side',(px,sy*.610,4.105),(1.98,.075,.072),edge,b=.008)
 for dx in [-.925,.925,-.750,.650]:box('Open pantograph mounting frame crossmember',(px+dx,0,4.105),(.07,1.25,.072),edge,b=.006)
 for dx in [-.80,.80]:
  for sy in [-1,1]:bolt('Pantograph frame fixing',(px+dx,sy*.55,4.152),.017,.020,axis='Z',m=steel)
# Panto refinements attach to existing rigid controls so source animation is retained.
for name in ['FRONT','REAR']:
 ctrl=bpy.data.objects['PANTO_'+name+'_CTRL'];x=ctrl.matrix_world.translation.x
 for sy in [-1,1]:
  # Fixed spring box and air lines do not obstruct the arm sweep.
  box('Pantograph fixed spring housing',(x+.42,sy*.70,4.154),(.35,.22,.10),frame,parent=ctrl,b=.010)
  tube('Pantograph pneumatic air feed',[(x+.57,sy*.70,4.18),(x+.68,sy*.73,4.15),(x+.90,sy*.73,4.14)],.007,copper,parent=ctrl,N=8)
  bolt('Pantograph base pivot end',(x,sy*.491,4.18),.029,.021,parent=ctrl,axis='Y',m=edge)
for node in roof.node_tree.nodes:
 if node.type=='TEX_NOISE' and node.inputs['Scale'].default_value<100:node.inputs['Scale'].default_value=2.5
# Perimeter gasket is a real seal, not an opaque slab behind the door aperture.
remove_prefixes(['Cab door gasket'])
for end in [-1,1]:
 for sy in [-1,1]:
  for dx in [-.331,.331]:box('Cab door perimeter gasket',(end*7.8+dx,sy*1.474,2.58),(.027,.02,2.02),rubber,b=.005)
  for dz in [-.995,.995]:box('Cab door perimeter gasket',(end*7.8,sy*1.474,2.58+dz),(.664,.02,.027),rubber,b=.005)
# Material metadata, texture paths are portable and packed.
for im in bpy.data.images:
 if im.source=='FILE':
  if im.packed_file:
   (OUT/'textures'/Path(im.filepath).name).write_bytes(im.packed_file.data)
  else:im.pack()
  im.filepath='//textures/'+Path(im.filepath).name
root['visual_variant']='WAP-7 39002, Royapuram-inspired conventional white/vermilion; photo-led representative interpretation'
root['source_baseline_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();root['asset_status']='High-detail source refinement. Not converted or tested in TF3. Rig/coupling/interior contracts retained.'
# Staging is a separate module for repeatable render setup.
exec(compile((OUT/'scripts/build_stage.py').read_text(),'build_stage.py','exec'))
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
# Save folded clean authoring state; render script chooses independent live-control poses.
for n in ['PANTO_FRONT_CTRL','PANTO_REAR_CTRL']:bpy.data.objects[n]['extension']=0.0
bpy.context.view_layer.update()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=256;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.015;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=8;scene.cycles.sample_clamp_indirect=2.5;scene.cycles.blur_glossy=1.0;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.32
scene.render.resolution_x=1920;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False
scene.camera=bpy.data.objects['CAM_HERO'];scene.render.filepath='//previews/01_hero_trackside.png'
# Remove backups from future saves and pack authoring fonts/images.
scene['render_provenance']='Cycles rendering of delivered editable geometry. No image generation or photo backgrounds.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'WAP7_photoreal_v01.blend'),compress=True,relative_remap=False)
report={'source':str(SOURCE.name),'source_sha256':root['source_baseline_sha256'],'objects':len(bpy.data.objects),'new_geometry_objects':len(created),'collections':[c.name for c in bpy.data.collections],'packed_images':[i.name for i in bpy.data.images if i.packed_file],'rig_controls':['PANTO_FRONT_CTRL','PANTO_REAR_CTRL'],'units':'metres','render_engine':'Cycles CPU','notes':'Source-only refinement; presentation-only collection excluded from asset envelope.'}
(OUT/'qa/build_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
