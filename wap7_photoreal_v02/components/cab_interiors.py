"""Reference-grounded, editable WAP-7 cabs for Blender 4.3.2.

Call apply(context=None) on the accepted source scene. This module never resets,
saves, renders, changes the exterior shell, or changes original roots/anchors.
The old interior's visible meshes are hidden reversibly. All additions CABV02_.

Evidence: factory WAP-7 30221 seatless photograph, real Panel A photograph,
and Railway Board WTA-554 Annexure E's WAP7/E70 equipment list. It is a
representative conventional-cab interpretation, NOT a measured 39002 survey.
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi

PREFIX='CABV02_'
TEXTURES=Path(__file__).resolve().parents[1]/'textures'/'cab'
SOURCE_PANEL='https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/6/3/6/1366636/0/detailedviewpanelawap7loco147148.jpg'
SOURCE_FACTORY='https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/5/9/4/1593594/16557400/wap7seatless134598.jpg'
SOURCE_EQUIPMENT='https://indianrailways.gov.in/railwayboard/rb/corrigendum/1731932781388_Corrig%20No-4_Bid%20Doc%20Ver-1_%20Revised%20Spec_Anned-13_Annex-14.pdf'

def material(name,color,metal=0,rough=.5,noise=0):
 n=PREFIX+name;m=bpy.data.materials.get(n)
 paint=name in {'Warm grey interior enamel','Folded desk light grey satin','Charcoal removable instrument panel'}
 if m and (not paint or m.get('cab_paint_recipe')=='dielectric_metric_v1'):return m
 if not m:m=bpy.data.materials.new(n)
 m.use_nodes=True;m.diffuse_color=(*color,1);nt=m.node_tree
 if paint:
  nt.nodes.clear();p=nt.nodes.new('ShaderNodeBsdfPrincipled');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs[0],out.inputs['Surface'])
 else:p=nt.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=0 if paint else metal;p.inputs['Roughness'].default_value=rough
 if paint:
  # Physical paint calibration matches the validated surface-library recipe.
  # Object coordinates are real local metres, never normalised Generated space.
  p.inputs['IOR'].default_value=1.5;p.inputs['Specular IOR Level'].default_value=.5;p.inputs['Coat Weight'].default_value=0
  coord=nt.nodes.new('ShaderNodeTexCoord');coord.name='Metric object coordinates'
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.name='Submillimetre enamel grain';tex.inputs['Scale'].default_value=1500;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.55;nt.links.new(coord.outputs['Object'],tex.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.name='Low amplitude paint variation'
  ramp.color_ramp.elements[0].color=(*(v*.988 for v in color),1);ramp.color_ramp.elements[1].color=(*(min(1,v*1.012) for v in color),1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
  mr=nt.nodes.new('ShaderNodeMapRange');mr.name='Narrow paint micro roughness';mr.inputs['To Min'].default_value=rough-.015;mr.inputs['To Max'].default_value=rough+.015;nt.links.new(tex.outputs['Fac'],mr.inputs['Value']);nt.links.new(mr.outputs['Result'],p.inputs['Roughness'])
  bump=nt.nodes.new('ShaderNodeBump');bump.name='Micrometre paint finish';bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.000040;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
  m['cab_paint_recipe']='dielectric_metric_v1';m['coordinate_units']='metres, per-object local';m['substrate']='Dielectric satin paint; no clearcoat or exposed metal mixture'
 elif noise:
  tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=2
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0003
  nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m

def texture_material(file,emission=0):
 n=PREFIX+'ART_'+file;m=bpy.data.materials.get(n)
 if m:return m
 m=material('ART_'+file,(.6,.65,.56),0,.56);nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(TEXTURES/file),check_existing=True);t.image.pack();t.image.filepath='//textures/cab/'+file
 nt.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if emission:nt.links.new(t.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=emission
 return m

def palette():
 m={
  'wall':material('Warm grey interior enamel',(.43,.465,.443),0,.53,1500),
  'desk':material('Folded desk light grey satin',(.345,.382,.365),0,.43,1500),
  'panel':material('Charcoal removable instrument panel',(.023,.030,.029),0,.55,1500),
  'edge':material('Satin aluminium collars',(.34,.38,.38),.72,.32,600),
  'steel':material('Chrome control shaft',(.49,.52,.51),.85,.24),
  'screw':material('Satin screw heads',(.35,.375,.37),.7,.34),
  'rubber':material('Moulded black rubber',(.017,.021,.019),.0,.72,180),
  'floor':material('Safety PVC floor',(.085,.097,.089),.0,.80,90),
  'vinyl':material('Blue vinyl crew seat',(.015,.061,.112),.0,.45,380),
  'vinylside':material('Blue vinyl seam shadow',(.009,.030,.064),.0,.57,240),
  'stitch':material('Upholstery seam thread',(.11,.17,.23),.0,.78),
  'ivory':material('Engraved ivory legends',(.77,.79,.71),.0,.7),
  'black':material('Black recesses',(.003,.005,.004),.0,.86),
  'red':material('Red translucent control cap',(.45,.015,.009),.08,.27),
  'amber':material('Amber translucent control cap',(.67,.26,.012),.08,.28),
  'yellow':material('Yellow pushbutton',(.66,.47,.018),.05,.30),
  'green':material('Green pushbutton',(.008,.32,.049),.05,.28),
  'blue':material('Blue pushbutton',(.008,.115,.32),.05,.31),
  'brass':material('Brass key and bushing',(.31,.23,.09),.72,.34),
  'diffuser':material('Frosted lamp diffuser',(.78,.80,.73),0,.38),
  'glass':material('Instrument cover glass',(.91,.96,.93),0,.07),
 }
 g=m['glass'].node_tree.nodes.get('Principled BSDF');g.inputs['Transmission Weight'].default_value=.96;g.inputs['IOR'].default_value=1.47
 # Thin clear covers: retain glass reflections while allowing diffuse illumination of
 # the actual recessed scale. This avoids black fake dials from disabled caustics.
 nt=m['glass'].node_tree
 if not nt.nodes.get('Thin cover transparent mix'):
  tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.name='Thin cover transparent mix';mix.inputs[0].default_value=.14
  nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(g.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
 return m

class Cab:
 def __init__(self,root,index,collection,materials):
  self.root=root;self.index=index;self.coll=collection;self.m=materials;self.name=PREFIX+str(index)+'_';self.created=[]
 def obj(self,n,verts,faces,mat,bevel=0,smooth=False):
  name=self.name+n;me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);self.coll.objects.link(o);o.parent=self.root
  if mat:me.materials.append(self.m.get(mat,mat) if isinstance(mat,str) else mat)
  if bevel:
   mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=3;mod.affect='EDGES';o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
  if smooth:
   for p in me.polygons:p.use_smooth=True
  o['cab']=self.index;o['static_visual_detail']=True;self.created.append(o);return o
 def box(self,n,c,d,mat,b=.003):
  c=Vector(c);x,y,z=[k/2 for k in d];v=[c+Vector((a,bb,cc)) for a,bb,cc in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
  return self.obj(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,b)
 def slab(self,n,c,w,h,d,mat,R=(0,-1,0),U=(0,0,1),b=.002):
  c,R,U=Vector(c),Vector(R),Vector(U);N=R.cross(U).normalized();v=[]
  for a,bb,cc in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:v.append(c+R*(a*w/2)+U*(bb*h/2)+N*(cc*d/2))
  return self.obj(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,b)
 def cyl(self,n,c,r,d,mat,axis=(0,0,1),N=32,b=0):
  c=Vector(c);A=Vector(axis).normalized();R=A.orthogonal().normalized();U=A.cross(R).normalized();v=[c+R*(r*cos(2*pi*i/N))+U*(r*sin(2*pi*i/N))+A*z for z in[-d/2,d/2] for i in range(N)]
  fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  o=self.obj(n,v,fs,mat,b)
  for p in o.data.polygons:
   if len(p.vertices)==4:p.use_smooth=True
  return o
 def rod(self,n,a,b,r,mat,N=12):
  a,b=Vector(a),Vector(b);return self.cyl(n,(a+b)/2,r,(b-a).length,mat,b-a,N)
 def tube(self,n,points,r,mat,N=8,closed=False):
  pts=[Vector(p) for p in points]
  if closed:pts.append(pts[0])
  v=[]
  for i,p in enumerate(pts):
   tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();R=tangent.orthogonal().normalized();U=tangent.cross(R).normalized()
   v.extend([p+R*(r*cos(2*pi*j/N))+U*(r*sin(2*pi*j/N)) for j in range(N)])
  fs=[tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))]+[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
  return self.obj(n,v,fs,mat,smooth=True)
 def ring(self,n,c,ro,ri,d,mat,R=(0,-1,0),U=(0,0,1),N=48):
  c,R,U=Vector(c),Vector(R),Vector(U);A=R.cross(U).normalized();v=[]
  for z,r in[(-d/2,ro),(d/2,ro),(-d/2,ri),(d/2,ri)]:
   for j in range(N):v.append(c+R*r*cos(2*pi*j/N)+U*r*sin(2*pi*j/N)+A*z)
  fs=[]
  for i in range(N):
   j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)])
  return self.obj(n,v,fs,mat,smooth=True)
 def discart(self,n,c,r,mat,R=(0,-1,0),U=(0,0,1),N=64):
  c,R,U=Vector(c),Vector(R),Vector(U);vs=[c]+[c+R*(r*cos(2*pi*j/N))+U*(r*sin(2*pi*j/N)) for j in range(N)];faces=[(0,j+1,(j+1)%N+1) for j in range(N)];o=self.obj(n,vs,faces,mat);uv=o.data.uv_layers.new(name='Instrument UV')
  for poly in o.data.polygons:
   for idx in poly.loop_indices:
    v=o.data.vertices[o.data.loops[idx].vertex_index].co-c;uv.data[idx].uv=(.5+v.dot(R)/(r*2),.5+v.dot(U)/(r*2))
  return o
 def art(self,n,c,w,h,mat,R=(0,-1,0),U=(0,0,1)):
  c,R,U=Vector(c),Vector(R),Vector(U);o=self.obj(n,[c-R*w/2-U*h/2,c+R*w/2-U*h/2,c+R*w/2+U*h/2,c-R*w/2+U*h/2],[(0,1,2,3)],mat);uv=o.data.uv_layers.new(name='Original art UV')
  for i,p in zip(o.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
  return o
 def text(self,n,t,c,size=.010,mat='ivory',R=(0,-1,0),U=(0,0,1)):
  R,U=Vector(R),Vector(U);N=R.cross(U).normalized();cu=bpy.data.curves.new(self.name+n,'FONT');cu.body=t;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.space_character=1.04;cu.resolution_u=3;cu.extrude=0;cu.fill_mode='BOTH'
  o=bpy.data.objects.new(self.name+n,cu);self.coll.objects.link(o);o.parent=self.root;o.matrix_basis=Matrix((R,U,N)).transposed().to_4x4();o.location=c;cu.materials.append(self.m[mat]);o['legends_source']='Inspected WAP7 control photo / Railway Board equipment terminology';self.created.append(o);return o
 def screw(self,n,c,r=.0045,R=(0,-1,0),U=(0,0,1)):
  c,R,U=Vector(c),Vector(R),Vector(U);N=R.cross(U).normalized();self.cyl(n+'_head',c,r,.0028,'screw',N,16,b=.0005);self.slab(n+'_slot',c+N*.0015,r*1.23,.0009,.00035,'black',R,U,b=.0001)
 def rounded_path(self,c,w,h,r,R=(0,-1,0),U=(0,0,1)):
  c,R,U=Vector(c),Vector(R),Vector(U);pts=[]
  for xx,yy,start in[(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for j in range(9):
    a=math.radians(start+90*j/8);pts.append(c+R*(xx+r*cos(a))+U*(yy+r*sin(a)))
  return pts
 def panel(self,n,c,w,h,tilt=.32,yaw=0,depth=.15):
  # Screen-right is cab -Y, and tilt gives the real aft-facing surface an upward normal.
  R=Vector((sin(yaw),-cos(yaw),0));N0=Vector((-cos(yaw),-sin(yaw),0));U=Vector((cos(yaw)*sin(tilt),sin(yaw)*sin(tilt),cos(tilt)));N=R.cross(U).normalized();c=Vector(c)
  self.slab(n+'_formed_housing',c-N*(depth/2),w+.042,h+.048,depth,'desk',R,U,b=min(.016,depth/4))
  self.slab(n+'_plate_gasket',c+N*.004,w+.006,h+.006,.009,'rubber',R,U,b=.006)
  self.slab(n+'_removable_face',c+N*.012,w,h,.006,'panel',R,U,b=.004)
  for i,u in enumerate([-w/2+.017,0,w/2-.017]):
   for j,v in enumerate([-h/2+.013,h/2-.013]):self.screw(n+f'_fastener_{i}_{j}',c+R*u+U*v+N*.017,R=R,U=U)
  return Panel(self,n,c+N*.017,R,U,N)

class Panel:
 def __init__(self,cab,n,c,R,U,N):self.b=cab;self.n=n;self.c=c;self.R=R;self.U=U;self.N=N
 def p(self,u=0,v=0,d=0):return self.c+self.R*u+self.U*v+self.N*d
 def label(self,t,u,v,size=.010):return self.b.text(self.n+'_legend_'+t,t,self.p(u,v,.0015),size,R=self.R,U=self.U)
 def screw(self,n,u,v,r=.004):self.b.screw(self.n+'_'+n,self.p(u,v,.004),r,self.R,self.U)
 def button(self,label,u,v,color='amber',r=.018,legend=True,mushroom=False):
  b=self.b;n=self.n+'_'+label
  b.cyl(n+'_socket',self.p(u,v,.004),r*1.22,.008,'rubber',self.N,32)
  b.ring(n+'_threaded_collar',self.p(u,v,.011),r*1.13,r*.83,.009,'edge',self.R,self.U,N=40)
  # Knurl cuts are real separated radial ridges around the collar.
  for i in range(20):
   a=i*2*pi/20;pt=self.p(u+cos(a)*r*1.08,v+sin(a)*r*1.08,.011);b.cyl(n+f'_knurl_{i}',pt,.0006,.007,'screw',self.N,6)
  if mushroom:
   b.cyl(n+'_stem',self.p(u,v,.018),r*.54,.024,'rubber',self.N,32)
   b.cyl(n+'_mushroom_cap',self.p(u,v,.037),r,.025,color,self.N,48,b=.007)
  else:
   b.cyl(n+'_rubber_lip',self.p(u,v,.015),r*.92,.009,'rubber',self.N,36)
   b.cyl(n+'_lens',self.p(u,v,.022),r*.85,.009,color,self.N,40,b=.003)
   b.ring(n+'_lens_moulding',self.p(u,v,.028),r*.78,r*.68,.001,color,self.R,self.U,N=36)
  if legend:self.label(label,u,v-r*1.6-.010,.010)
 def switch(self,label,u,v,angle=0,legend=True):
  b=self.b;n=self.n+'_'+label
  b.cyl(n+'_thread',self.p(u,v,.008),.013,.010,'edge',self.N,24)
  b.cyl(n+'_hex_locknut',self.p(u,v,.013),.011,.006,'screw',self.N,6)
  b.slab(n+'_sealed_rubber_base',self.p(u,v,.022),.030,.023,.021,'rubber',self.R,self.U,b=.004)
  # A slim paddle, with a visible raised index rib and pivot rather than generic pegs.
  axis=self.U*cos(angle)+self.R*sin(angle)
  b.rod(n+'_pivot',self.p(u,v,.027)-self.R*.012,self.p(u,v,.027)+self.R*.012,.004,'steel',12)
  b.rod(n+'_paddle_shank',self.p(u,v,.027),self.p(u,v,.038)+axis*.018,.0035,'steel',12)
  b.slab(n+'_paddle_tip',self.p(u,v,.040)+axis*.020,.021,.029,.009,'rubber',self.R,axis,b=.0025)
  b.slab(n+'_index',self.p(u,v,.046)+axis*.025,.011,.0013,.001,'ivory',self.R,axis,b=.0001)
  self.label('0',u+.024,v+.012,.007);self.label('I',u+.024,v-.010,.007)
  if legend:self.label(label,u,v-.033,.009)
 def meter(self,n,u,v,w,h,file,vertical=False):
  b=self.b;b.slab(self.n+'_'+n+'_gasket',self.p(u,v,.007),w+.011,h+.012,.014,'rubber',self.R,self.U,b=.004)
  b.slab(self.n+'_'+n+'_bezel',self.p(u,v,.020),w+.005,h+.005,.023,'panel',self.R,self.U,b=.003)
  b.art(self.n+'_'+n+'_scale',self.p(u,v,.034),w-.009,h-.011,texture_material(file),self.R,self.U)
  if vertical:
   b.slab(self.n+'_'+n+'_moving_pointer',self.p(u,v+(.006 if 'bogie' in file else .035),.036),w*.62,.0020,.0015,'black',self.R,self.U,b=.0002)
  else:
   b.rod(self.n+'_'+n+'_needle',self.p(u,v-h*.23,.037),self.p(u+w*.24,v+h*.24,.037),.0011,'black',10);b.cyl(self.n+'_'+n+'_needle_pivot',self.p(u,v-h*.23,.038),.004,.0015,'edge',self.N,24)
  b.slab(self.n+'_'+n+'_glass',self.p(u,v,.040),w-.008,h-.010,.0015,'glass',self.R,self.U,b=.001)
  self.label(n,u,v-h/2-.013,.0085)
 def gauge(self,label,u,v,r,file,dual=False,angle=-.6):
  b=self.b;n=self.n+'_'+label
  b.cyl(n+'_case',self.p(u,v,-.010),r*1.06,.044,'panel',self.N,48)
  b.ring(n+'_gasket',self.p(u,v,.012),r*1.09,r*.96,.009,'rubber',self.R,self.U)
  b.ring(n+'_polished_bezel',self.p(u,v,.020),r*1.05,r*.925,.014,'edge',self.R,self.U,N=64)
  b.discart(n+'_original_scale',self.p(u,v,.021),r*.93,texture_material(file),self.R,self.U)
  for i,(a,col) in enumerate([(angle,'black')]+([(angle+.5,'red')] if dual else [])):
   base=self.p(u,v,.025+i*.0015);tip=self.p(u+r*.73*sin(a),v+r*.73*cos(a),.025+i*.0015);tail=self.p(u-r*.14*sin(a),v-r*.14*cos(a),.025+i*.0015)
   b.rod(n+f'_needle_{i}',tail,tip,r*.019,col,10)
  b.cyl(n+'_spindle',self.p(u,v,.029),r*.084,.002,'edge',self.N,32)
  b.cyl(n+'_cover_glass',self.p(u,v,.031),r*.925,.0012,'glass',self.N,64)
  for i,a in enumerate([pi/4,pi*5/4]):self.screw(label+f'_clamp_{i}',u+cos(a)*r*1.19,v+sin(a)*r*1.19,.0026)

def build_controls(b):
 # Formed sheet-metal desktop: real softened front edge and hanging apron.
 poly=[(8.415,-1.42),(8.435,-1.46),(9.12,-1.46),(9.16,-1.39),(9.16,1.39),(9.12,1.46),(8.435,1.46),(8.415,1.42)]
 N=len(poly);vs=[(x,y,z) for z in[2.345,2.423] for x,y in poly]
 b.obj('Desk_continuous_folded_top',vs,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],'desk',.018)
 b.box('Desk_front_folded_apron',(8.435,0,2.336),(.036,2.83,.145),'desk',.013)
 b.box('Desk_front_lower_return',(8.448,0,2.263),(.055,2.82,.012),'panel',.003)
 # The central equipment pedestal follows the factory photo's narrower footwell split.
 b.box('Desk_central_pedestal',(8.80,-.17,1.995),(.58,.62,.74),'desk',.018)
 b.box('Desk_central_removable_panel',(8.503,-.17,1.987),(.020,.572,.624),'desk',.008)
 for y in[-.428,.088]:
  for z in[1.714,2.27]:b.screw('Desk_access_screw',(8.49,y,z),.006)
 b.box('Desk_pedestal_seam',(8.490,-.17,1.963),(.006,.575,.004),'panel',.001)
 b.box('Desk_pedestal_vent_recess',(8.487,-.17,1.815),(.011,.443,.155),'black',.006)
 for i in range(10):b.box(f'Desk_pedestal_louvre_{i}',(8.477,-.17,1.752+i*.014),(.018,.423,.008),'desk',.002)
 b.box('Desk_pedestal_foot_return',(8.72,-.17,1.655),(.43,.65,.045),'rubber',.009)
 for side in[-1,1]:
  b.box(f'Desk_end_support_{side}',(8.86,side*1.365,1.997),(.53,.13,.71),'desk',.012)
  b.box(f'Desk_end_gasket_{side}',(8.577,side*1.365,2.015),(.008,.10,.53),'rubber',.002)
 # Main panel: placement and designators correspond to the inspected real Panel A photograph.
 p=b.panel('Panel_A',(8.787,.568,2.663),1.12,.397,tilt=.30)
 p.meter('UBA',-.465,.072,.117,.152,'meter_battery.png')
 p.meter('U',-.330,.061,.072,.183,'meter_ohe.png',True)
 p.meter('BOGIE 1',-.229,.061,.078,.183,'meter_bogie1.png',True)
 p.meter('BOGIE 2',-.123,.061,.078,.183,'meter_bogie2.png',True)
 for label,u,col in[('LSDJ',.035,'red'),('LSHO',.142,'amber'),('LSP',.249,'amber'),('LSAF',.356,'red')]:p.button(label,u,.130,col,.020)
 p.button('LSVW',.356,.016,'yellow',.022)
 p.button('LSCE',-.498,-.087,'amber',.018)
 p.switch('ZBAN',.028,.008)
 for label,u in[('ZPT',-.282),('BLDJ',-.201),('BLCP',-.120),('BLHO',-.039),('ZTEL',.042)]:p.switch(label,u,-.098)
 for label,u,col in[('BPCS',.154,'green'),('BPPB',.262,'red'),('BPVR',.370,'yellow')]:p.button(label,u,-.103,col,.020)
 # Actual key-switch designator. Cab 2 inactive: no duplicated inserted key.
 u,v=-.390,-.098
 b.cyl('Panel_A_BL_key_bezel',p.p(u,v,.013),.017,.013,'brass',p.N,40)
 b.cyl('Panel_A_BL_key_center',p.p(u,v,.021),.012,.007,'edge',p.N,32)
 b.slab('Panel_A_BL_key_slot',p.p(u,v,.025),.004,.017,.0007,'black',p.R,p.U,b=.0001)
 p.label('BL',u,v-.032,.010);p.label('0   D',u,v+.032,.007)
 if b.index==1:
  b.slab('Panel_A_BL_inserted_key',p.p(u,v,.043),.029,.012,.038,'brass',p.R,p.U,b=.002)
  b.ring('Panel_A_BL_key_ring',p.p(u,v-.027,.063),.022,.0205,.002,'steel',p.R,p.U,N=48)
  # A flexible retained loop hangs below the key ring; no angular wire segments.
  cord=[p.p(u+.029*sin(a),v-.049+.052*(cos(a)-1),.064+.004*(1-cos(a))) for a in[2*pi*j/64 for j in range(64)]]
  b.tube('Panel_A_BL_key_tether',cord,.0012,'rubber',8,closed=True)
 p.button('Emergency_stop',.490,-.089,'red',.032,False,True)
 b.ring('Panel_A_emergency_yellow_legend_disc',p.p(.49,-.089,.009),.057,.023,.002,'yellow',p.R,p.U,N=64)
 label='EMERGENCY STOP'
 for j,ch in enumerate(label):
  a=math.radians(155-j*130/(len(label)-1));c=p.p(.49+cos(a)*.044,-.089+sin(a)*.044,.011)
  R=p.R*sin(a)-p.U*cos(a);U=p.R*cos(a)+p.U*sin(a);b.text(f'Panel_A_emergency_legend_{j}',ch,c,.0068,'black',R,U)
 # Panel B is angled inward at the driver's left. Four principal gauges + separate PB.
 q=b.panel('Panel_B',(8.750,1.262,2.640),.300,.349,.24,yaw=.78,depth=.035)
 q.gauge('BC',-.077,.078,.052,'gauge_bc.png',True,-1.3)
 q.gauge('MR_FP',.077,.078,.052,'gauge_mrfp.png',True,.3)
 q.gauge('AIR_FLOW',-.077,-.073,.052,'gauge_afi.png',False,-1.25)
 q.gauge('BP',.077,-.073,.052,'gauge_bp.png',False,-.2)
 q.label('PANEL B',0,-.157,.007)
 # Separate parking brake gauge mounted below/alongside B, as listed in classic cab documentation.
 pb=Panel(b,'Parking_brake_gauge',Vector((8.547,1.265,2.330)),q.R,q.U,q.N);pb.gauge('PB',0,0,.038,'gauge_pb.png',False,-1.0)
 # Central display panel, with discrete keys and visible captive fasteners.
 r=b.panel('Panel_C',(8.797,-.412,2.650),.720,.390,.30)
 b.slab('Panel_C_DDU_instrument_body',r.p(-.153,.018,.014),.348,.235,.032,'rubber',r.R,r.U,b=.005)
 for u in[-.313,.005]:
  for v in[-.084,.121]:r.screw('DDU_captive_screw',u,v,.0032)
 b.slab('Panel_C_LCD_raised_surround',r.p(-.154,.055,.035),.272,.077,.014,'edge',r.R,r.U,b=.003)
 b.slab('Panel_C_LCD_inner_recess',r.p(-.154,.055,.044),.249,.056,.006,'black',r.R,r.U,b=.001)
 b.art('Panel_C_LCD_original_blank_screen',r.p(-.154,.055,.048),.240,.046,texture_material('lcd_blank.png',.10),r.R,r.U)
 b.slab('Panel_C_LCD_cover_glass',r.p(-.154,.055,.049),.240,.046,.0008,'glass',r.R,r.U,b=.0005)
 # Factory photo: little navigation cross and three narrow selection keys.
 for j,(u,v,symbol) in enumerate([(-.245,-.016,'↑'),(-.268,-.041,'←'),(-.245,-.041,'•'),(-.222,-.041,'→'),(-.245,-.066,'↓'),(-.054,-.010,'1'),(-.054,-.039,'2'),(-.054,-.068,'3')]):
  b.slab(f'Panel_C_key_{j}',r.p(u,v,.040),.017,.016,.006,'ivory',r.R,r.U,b=.0016);b.text(f'Panel_C_key_symbol_{j}',symbol,r.p(u,v,.044),.008,'panel',r.R,r.U)
 r.label('DDU',-.154,.155,.008)
 for i,label in enumerate(['ZLC','ZLI','ZLDD']):r.switch(label,.076+i*.066,.109)
 r.button('LSFI',.049,-.016,'red',.014)
 r.button('BPFA',.049,-.098,'amber',.017)
 for i,label in enumerate(['BLPR','ZPRD','ZLFW','ZLFR']):r.switch(label,.116+i*.062,-.094)
 r.button('BPFL',.292,-.013,'amber',.014)
 # Three-frequency buzzer grill with concentric rings and radial support.
 c=r.p(.283,.109,.025);b.cyl('Panel_C_buzzer_cavity',c,.043,.020,'black',r.N,40)
 for rad in[.011,.018,.025,.032,.039]:b.ring('Panel_C_buzzer_guard',c+r.N*.011,rad+.0008,rad-.0008,.002,'edge',r.R,r.U,48)
 for a in[0,pi/2,pi,3*pi/2]:b.rod('Panel_C_buzzer_guard_spoke',c+r.N*.012,c+r.N*.012+r.R*(.040*cos(a))+r.U*(.040*sin(a)),.0013,'panel')
 # Discrete assistant driver's panel, not a second driver's full control desk.
 a=b.panel('Panel_D',(8.825,-1.207,2.619),.367,.320,.21)
 a.switch('ZLDA',-.105,.080);a.switch('ZLH',.094,.080)
 a.button('BPVG',-.095,-.058,'green',.021)
 b.cyl('Panel_D_PCLH_socket_recess',a.p(.086,-.056,.014),.026,.015,'rubber',a.N,36)
 b.cyl('Panel_D_PCLH_socket_inner',a.p(.086,-.056,.025),.019,.011,'black',a.N,32)
 for u,v in[(-.007,0),(.007,0),(0,.010)]:b.cyl('Panel_D_PCLH_contact',a.p(.086+u,-.056+v,.030),.0028,.001,'brass',a.N,16)
 a.label('PCLH',.086,-.105,.010)
 # The classic MEMOTEL-sized speedometer at the windscreen mullion.
 speed=Panel(b,'Speedometer',Vector((9.033,-.006,3.047)),Vector((0,-1,0)),Vector((-.045,0,.999)),Vector((-.999,0,-.045)))
 b.slab('Speedometer_mounting_bracket',(9.112,-.006,2.991),.16,.30,.11,'desk',speed.R,speed.U,b=.008)
 b.slab('Speedometer_individual_case',speed.p(0,0,-.031),.273,.304,.088,'panel',speed.R,speed.U,b=.022)
 speed.gauge('Speed',0,.034,.105,'speedometer.png',False,-2.23)
 b.slab('Speedometer_lower_control_bar',speed.p(0,-.118,.022),.218,.035,.008,'rubber',speed.R,speed.U,b=.003)
 for i in range(8):
  b.slab('Speedometer_membrane_key',speed.p(-.090+i*.025,-.118,.029),.018,.016,.003,'yellow',speed.R,speed.U,b=.0015)
  b.text('Speedometer_key_numeral',str(i+1),speed.p(-.090+i*.025,-.118,.031),.008,'black',speed.R,speed.U)
 for yy in[-.119,.119]:
  for zz in[-.142,.139]:speed.screw('case_screw',yy,zz)
 # Visual distinction is restrained: Cab 2 carries the recorder memory/interface cover.
 if b.index==2:
  b.slab('Speedometer_Cab2_memory_cover',speed.p(.159,-.06,-.019),.018,.061,.044,'rubber',speed.R,speed.U,b=.003)
 # Master controller and reverser on the horizontal surface ahead of driver's hand.
 build_levers(b)


def sphere(b,n,c,r,mat,N=32,rows=16):
 c=Vector(c);v=[c+Vector((0,0,r))]
 for j in range(1,rows):
  a=pi*j/rows
  for k in range(N):t=2*pi*k/N;v.append(c+Vector((r*sin(a)*cos(t),r*sin(a)*sin(t),r*cos(a))))
 bottom=len(v);v.append(c+Vector((0,0,-r)));f=[]
 for k in range(N):f.append((0,1+k,1+(k+1)%N))
 for j in range(rows-2):
  for k in range(N):i=1+j*N+k;f.append((i,1+j*N+(k+1)%N,1+(j+1)*N+(k+1)%N,i+N))
 for k in range(N):f.append((1+(rows-2)*N+k,bottom,1+(rows-2)*N+(k+1)%N))
 return b.obj(n,v,f,mat,smooth=True)


def build_levers(b):
 # Inspected WAP7 photo: the ball-topped TE/BE throttle and a shorter reverser
 # share a rectangular slotted plate at the A/C boundary, on the driver's right.
 x,y=8.592,.038
 b.box('Master_controller_combined_mounting_gasket',(x,y,2.434),(.262,.240,.012),'rubber',.008)
 b.box('Master_controller_combined_mounting_plate',(x,y,2.442),(.247,.226,.009),'edge',.004)
 b.box('Master_controller_black_slot_plate',(x,y,2.448),(.220,.202,.005),'panel',.003)
 b.box('Master_controller_fore_aft_slot',(x,y+.044,2.452),(.185,.059,.004),'black',.009)
 for xx in[x-.109,x+.109]:
  for yy in[y-.096,y+.096]:b.screw('Master_controller_mount_screw',(xx,yy,2.449),.004,(1,0,0),(0,1,0))
 # A curved rotating drum is visible in the slot; no fictitious rubber gaiter.
 v=[];N=32
 for yy in[y+.014,y+.076]:
  for i in range(N+1):a=i*pi/N;v.append((x+.073*cos(a),yy,2.446+.052*sin(a)))
 faces=[tuple(reversed(range(N+1))),tuple(range(N+1,2*(N+1)))]+[(i,i+1,N+2+i,N+1+i) for i in range(N)]
 b.obj('Master_controller_rotating_drum',v,faces,'panel',.001,smooth=True)
 b.rod('Master_controller_polished_shaft',(x,y+.044,2.483),(x-.008,y+.044,2.675),.010,'steel',28)
 sphere(b,'Master_controller_ball_grip',(x-.008,y+.044,2.695),.031,'rubber',40,20)
 b.cyl('Master_controller_ball_grip_neck',(x-.008,y+.044,2.666),.015,.018,'panel',(0,0,1),32)
 for t,xx in[('TE',x+.071),('0',x),('BE',x-.071)]:b.text('Master_controller_index_'+t,t,(xx,y+.091,2.453),.008,'ivory',(0,-1,0),(1,0,0))
 # Short reverser at the adjacent small slot on the same factory plate.
 b.box('Reverser_slot',(x+.040,y-.059,2.453),(.112,.027,.004),'black',.005)
 b.rod('Reverser_lever_shaft',(x+.012,y-.059,2.460),(x+.057,y-.059,2.546),.006,'steel',20)
 b.slab('Reverser_short_grip',(x+.060,y-.059,2.552),.032,.063,.025,'rubber',R=(0,-1,0),U=(.63,0,.777),b=.006)
 for t,xx in[('F',x+.084),('0',x+.038),('R',x-.010)]:b.text('Reverser_index_'+t,t,(xx,y-.085,2.453),.008,'ivory',(0,-1,0),(1,0,0))
 # Automatic train-brake unit on the driver's left: inclined metal scale plate,
 # deep cast housing and short red transverse handle. Size is representative.
 x,y=8.546,1.323
 b.box('Automatic_train_brake_floor_gasket',(x,y,2.435),(.226,.210,.015),'rubber',.009)
 poly=[(x-.102,2.442),(x+.095,2.442),(x+.095,2.522),(x-.070,2.475),(x-.102,2.457)]
 v=[(xx,yy,zz) for yy in[y-.094,y+.094] for xx,zz in poly];N=len(poly)
 b.obj('Automatic_train_brake_cast_housing',v,[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],'panel',.009)
 R=Vector((0,-1,0));U=Vector((.960,0,.280));normal=R.cross(U)
 c=Vector((x+.010,y,2.502))
 b.slab('Automatic_train_brake_inclined_scale_plate',c,.149,.128,.004,'edge',R,U,b=.004)
 b.slab('Automatic_train_brake_arc_recess',c+normal*.003,.105,.089,.003,'panel',R,U,b=.010)
 for u in[-.066,.066]:
  for vv in[-.053,.053]:b.screw('Automatic_train_brake_scale_screw',c+R*u+U*vv+normal*.004,.003,R,U)
 b.cyl('Automatic_train_brake_spindle',(x+.056,y,2.529),.017,.024,'steel',(0,0,1),32)
 b.rod('Automatic_train_brake_short_lever',(x+.056,y,2.529),(x+.037,y,2.626),.008,'steel',24)
 b.rod('Automatic_train_brake_red_handle',(x+.037,y-.041,2.627),(x+.037,y+.041,2.627),.019,'red',36)
 # Direct locomotive brake is the longer black lever on a lower round quadrant.
 x,y=8.508,1.065
 b.box('Direct_brake_mounting_gasket',(x,y,2.435),(.176,.153,.012),'rubber',.006)
 b.box('Direct_brake_cast_base',(x,y,2.452),(.164,.144,.035),'panel',.014)
 b.cyl('Direct_brake_quadrant',(x+.008,y,2.475),.061,.021,'panel',(0,0,1),48,b=.005)
 b.ring('Direct_brake_quadrant_trim',(x+.008,y,2.487),.053,.049,.002,'edge',(1,0,0),(0,1,0),48)
 b.rod('Direct_brake_lever',(x+.008,y,2.483),(x+.055,y,2.642),.009,'steel',28)
 b.slab('Direct_brake_black_grip',(x+.055,y,2.654),.054,.060,.038,'rubber',R=(0,-1,0),U=(.28,0,.960),b=.008)
 for xx in[x-.063,x+.063]:
  for yy in[y-.053,y+.053]:b.screw('Direct_brake_base_screw',(xx,yy,2.473),.0035,(1,0,0),(0,1,0))
 # Red pneumatic horn knobs are visible in the inspected real WAP7 cab photograph.
 for j,y in enumerate([1.124,-.893]):
  b.cyl(f'Horn_{j}_mount_flange',(8.691,y,2.441),.035,.011,'panel',(0,0,1),36)
  for k in range(4):b.cyl(f'Horn_{j}_rubber_gaiter',(8.691,y,2.450+k*.007),.028-k*.004,.009,'rubber',(0,0,1),32)
  b.rod(f'Horn_{j}_stem',(8.691,y,2.473),(8.682,y,2.554),.006,'steel',20)
  sphere(b,f'Horn_{j}_red_grip',(8.682,y,2.560),.018,'red',32,14)

def build_door_leaf(b):
 # Closed, watertight door mesh with a genuine rounded inspection-pane aperture.
 R=(0,1,0);U=(0,0,1)
 outer=b.rounded_path((7.295,0,2.56825),.693,1.8305,.012,R,U)
 inner=b.rounded_path((7.295,0,2.805),.410,.455,.038,R,U)
 n=len(outer);v=[]
 for dx,path in[(.0145,outer),(.0145,inner),(-.0145,outer),(-.0145,inner)]:v.extend([p+Vector((dx,0,0)) for p in path])
 f=[]
 for i in range(n):
  j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
 o=b.obj('Rear_door_leaf_with_real_window',v,f,'wall',.0018)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()

def build_shell_fittings(b):
 # The original cavity and glazing apertures are retained. Only cabin lining is replaced.
 b.box('Floor_PVC_liner',(8.17,0,1.608),(2.04,2.90,.053),'floor',.003)
 for y in[-.51,.48]:b.box('Floor_PVC_welded_seam',(8.17,y,1.636),(2.02,.003,.0018),'rubber',.0004)
 for x in[7.24,8.25]:b.box('Floor_expansion_seam',(x,0,1.637),(.004,2.87,.002),'rubber',.0004)
 # Four real framing pieces leave the walk-through opening clear.
 for side in[-1,1]:b.box('Rear_bulkhead_side_liner',(7.227,side*.912,2.594),(.070,1.076,1.994),'wall',.003)
 b.box('Rear_bulkhead_door_header',(7.227,0,3.553),(.070,.748,.076),'wall',.003)
 b.box('Rear_bulkhead_threshold_web',(7.227,0,1.60275),(.070,.748,.0115),'wall',.001)
 # Distinct perimeter seal, inset door leaf, glazed inspection pane and working-looking latch.
 for side in[-1,1]:b.box('Rear_door_frame_side_gasket',(7.271,side*.3605,2.56175),(.028,.027,1.9065),'rubber',.008)
 for z in[1.623,3.5005]:b.box('Rear_door_frame_cross_gasket',(7.271,0,z),(.028,.695,.029),'rubber',.008)
 build_door_leaf(b)
 b.box('Rear_door_lower_panel',(7.314,0,2.047),(.009,.604,.729),'desk',.005)
 b.tube('Rear_door_pane_inner_rubber',b.rounded_path((7.316,0,2.805),.438,.482,.05,R=(0,1,0)),.011,'rubber',10,True)
 # Actual opening and pane permit the independently authored central-room view.
 glass=b.m['glass'];b.slab('Rear_door_glass',(7.312,0,2.805),.410,.455,.004,glass,R=(0,1,0),b=.020)
 for z in[1.915,3.225]:
  b.box('Rear_door_hinge_leaf',(7.321,.337,z),(.016,.040,.073),'edge',.002)
  b.cyl('Rear_door_hinge_barrel',(7.349,.348,z),.012,.094,'steel',(0,0,1),28)
  for zz in[z-.041,z+.041]:b.cyl('Rear_door_hinge_knuckle',(7.349,.348,zz),.013,.008,'edge',(0,0,1),24)
  for zz in[z-.023,z+.023]:b.screw('Rear_door_hinge_screw',(7.334,.328,zz),.0038,R=(0,1,0))
 b.box('Rear_door_latch_plate',(7.325,-.268,2.365),(.011,.047,.178),'edge',.005)
 b.rod('Rear_door_handle_standoff1',(7.332,-.27,2.34),(7.38,-.27,2.34),.011,'steel')
 b.rod('Rear_door_handle_standoff2',(7.332,-.27,2.45),(7.38,-.27,2.45),.011,'steel')
 b.rod('Rear_door_handle_grip',(7.38,-.27,2.34),(7.38,-.27,2.45),.014,'rubber',24)
 b.cyl('Rear_door_lock_cylinder',(7.338,-.270,2.300),.013,.007,'brass',(1,0,0),28)
 b.box('Rear_door_lock_slot',(7.343,-.270,2.300),(.001,.002,.013),'black',.0004)
 b.box('Rear_door_threshold',(7.323,0,1.640),(.136,.780,.012),'edge',.003)
 for i in range(6):b.box('Rear_door_threshold_serration',(7.276+i*.019,0,1.648),(.005,.73,.003),'panel',.001)
 # Move the single door as a physical assembly, while frame/threshold stay fixed.
 pivot=bpy.data.objects.new(b.name+'Rear_door_hinge',None);b.coll.objects.link(pivot);pivot.parent=b.root
 # Neutralise the inherited legacy nonuniform Y scale at this rotational joint.
 # The door remains a rigid body when opened, while still following its cab root.
 root_matrix=b.root.matrix_world.copy();pivot.matrix_parent_inverse=root_matrix.inverted();pivot.location=root_matrix @ Vector((7.349,.348,2.475))
 base_angle=math.atan2(root_matrix[1][0],root_matrix[0][0]);pivot.rotation_euler.z=base_angle;pivot.empty_display_type='ARROWS';pivot.empty_display_size=.12
 bpy.context.view_layer.update();preserve_matrix=pivot.matrix_world.inverted() @ root_matrix
 pivot['open_angle_deg']=0.0;pivot['role']='Rear cab door: closed by default, open for interior review'
 pivot.id_properties_ui('open_angle_deg').update(min=0,max=90,soft_min=0,soft_max=90)
 for obj in list(b.created):
  short=obj.name[len(b.name):]
  if short.startswith('Rear_door_') and not short.startswith(('Rear_door_frame_','Rear_door_threshold')):
   obj.parent=pivot;obj.matrix_parent_inverse=preserve_matrix
 fc=pivot.driver_add('rotation_euler',2);dv=fc.driver.variables.new();dv.name='a';dv.type='SINGLE_PROP';dv.targets[0].id=pivot;dv.targets[0].data_path='["open_angle_deg"]';fc.driver.expression=f'{base_angle} + a * 0.017453292519943295';b.created.append(pivot)
 # Segmented removable bulkhead covers. Their detailed dimensions remain representative.
 for side in[-1,1]:
  y=side*.911
  b.box('Rear_bulkhead_service_cover',(7.272,y,2.875),(.016,.717,.767),'wall',.006)
  for yy in[y-.326,y+.326]:
   for z in[2.517,3.234]:b.screw('Rear_bulkhead_cover_screw',(7.283,yy,z),.005,R=(0,1,0))
  b.box('Rear_bulkhead_lower_cover',(7.275,y,1.99),(.018,.717,.680),'wall',.005)
  for yy in[y-.324,y+.324]:
   for z in[1.68,2.29]:b.screw('Rear_lower_cover_screw',(7.288,yy,z),.005,R=(0,1,0))
  b.rod('Rear_bulkhead_visible_conduit',(7.298,side*1.312,1.77),(7.298,side*1.312,3.27),.012,'desk',20)
  for z in[1.92,2.63,3.15]:
   b.box('Conduit_P_clip',(7.306,side*1.312,z),(.028,.041,.017),'edge',.002)
   b.screw('Conduit_P_clip_screw',(7.323,side*1.338,z),.0032,R=(0,1,0))
  b.box('Side_lower_lining',(8.15,side*1.444,2.091),(1.876,.038,.894),'wall',.004)
  b.box('Side_lower_lining_base_trim',(8.15,side*1.417,1.685),(1.88,.021,.070),'rubber',.003)
  b.box('Side_door_inner_kickplate',(7.795,side*1.416,1.868),(.565,.017,.326),'edge',.006)
  for x in[7.546,8.044]:
   for z in[1.727,2.009]:b.screw('Side_kickplate_screw',(x,side*1.405,z),.004,R=(side,0,0))
  b.box('Side_door_front_jamb',(8.103,side*1.435,2.665),(.043,.045,1.642),'wall',.004)
  b.box('Side_door_back_jamb',(7.449,side*1.435,2.665),(.050,.045,1.642),'wall',.004)
  b.box('Side_door_header',(7.781,side*1.444,3.526),(.692,.038,.11),'wall',.003)
  # Interior door latch is on the panel below the preserved door window.
  b.box('Side_door_latch_plate',(7.568,side*1.412,2.377),(.057,.015,.175),'edge',.004)
  b.rod('Side_door_handle_mount',(7.568,side*1.398,2.402),(7.568,side*1.355,2.402),.010,'steel',20)
  b.rod('Side_door_handle',(7.568,side*1.355,2.402),(7.697,side*1.355,2.402),.014,'steel',28)
  b.cyl('Side_door_lock',(7.568,side*1.399,2.330),.010,.008,'brass',(0,side,0),24)
  for x,w in[(7.80,.395),(8.55,.51)]:
   R=(side,0,0);U=(0,0,1);c=(x,side*1.421,3.024)
   b.tube('Side_window_inner_painted_reveal',b.rounded_path(c,w+.049,.805,.044,R,U),.016,'wall',10,True)
   b.tube('Side_window_EPDM_inner_lip',b.rounded_path((x,side*1.403,3.024),w+.006,.756,.036,R,U),.009,'rubber',10,True)
   # Sliding window channels and practical small latch beneath the sill.
   b.box('Side_window_sill_channel',(x,side*1.390,2.637),(w+.04,.036,.028),'edge',.004)
   b.box('Side_window_sill_insert',(x,side*1.375,2.645),(w,.013,.010),'rubber',.002)
   b.box('Side_window_latch',(x+.10,side*1.370,2.662),(.069,.023,.024),'panel',.004)
  b.box('Side_entry_threshold',(7.78,side*1.354,1.658),(.619,.149,.037),'edge',.004)
  for j in range(5):b.box('Side_entry_antislip_channel',(7.78,side*(1.300+j*.026),1.681),(.569,.009,.005),'rubber',.001)
  # A small real socket-size detail; no invented safety notice or serial plate.
  b.box('Side_service_socket_housing',(8.326,side*1.406,2.114),(.145,.051,.102),'desk',.009)
  b.cyl('Side_service_socket_cap',(8.326,side*1.372,2.114),.027,.020,'rubber',(0,side,0),32)
 # Window surrounds follow the existing sloped aperture, without moving any glazing.
 R=Vector((0,-1,0));U=Vector((-.28,0,.96))
 for y in[-.67,.67]:
  b.tube('Front_windscreen_painted_reveal',b.rounded_path((9.301,y,3.015),1.107,1.015,.118,R,U),.022,'wall',12,True)
  b.tube('Front_windscreen_inner_EPDM_lip',b.rounded_path((9.286,y,3.015),1.068,.947,.103,R,U),.009,'rubber',10,True)
  b.tube('Front_windscreen_fine_locking_strip',b.rounded_path((9.277,y,3.015),1.063,.943,.102,R,U),.0027,'panel',8,True)
  # Raised roller blind: hollow brackets, spindle end caps, a rolled fabric edge.
  b.rod('Blind_roller',(9.093,y-.515,3.491),(9.093,y+.515,3.491),.027,'rubber',40)
  b.box('Blind_painted_cover',(9.080,y,3.509),(.108,1.107,.050),'desk',.006)
  b.box('Blind_raised_fabric',(9.057,y,3.475),(.009,1.010,.039),'rubber',.002)
  b.rod('Blind_lower_weight',(9.050,y-.505,3.455),(9.050,y+.505,3.455),.007,'edge',20)
  for yy in[y-.542,y+.542]:
   b.box('Blind_mounting_bracket',(9.081,yy,3.488),(.105,.019,.099),'edge',.003)
   b.cyl('Blind_spindle_endcap',(9.093,yy,3.49),.021,.014,'panel',(0,1,0),32)
   b.screw('Blind_bracket_screw',(9.021,yy,3.51),.004)
  b.tube('Blind_pull_cord',[(9.036,y+.511,3.484),(9.015,y+.526,3.325),(9.019,y+.518,3.222)],.0015,'rubber',8)
  b.cyl('Blind_cord_end',(9.019,y+.518,3.218),.005,.018,'panel',(0,0,1),20,b=.001)
 # Thin cab identity above the actual mullion. The rest is kept free of invented placards.
 b.text('Cab_number','CAB '+str(b.index),(9.081,0,3.453),.037,'panel')
 build_ceiling(b)
 build_foot_controls(b)


def build_ceiling(b):
 # A tapered roof-following lining replaces the old rectangular plate that pierced
 # the narrowed nose crown. For x>=8.80 its top stays at or below 3.525 m.
 stations=[(7.17,1.395,3.590),(8.38,1.395,3.590),(8.57,1.365,3.535),(8.78,1.290,3.510),(8.98,1.200,3.507),(9.065,1.145,3.500)]
 def liner_height(x):
  for a,bb in zip(stations,stations[1:]):
   if a[0]<=x<=bb[0]:return a[2]+(bb[2]-a[2])*(x-a[0])/(bb[0]-a[0])
  return stations[0][2] if x<stations[0][0] else stations[-1][2]
 def loft(name,rows,thickness,mat):
  v=[]
  for x,w,z in rows:v.extend([(x,-w,z-thickness/2),(x,w,z-thickness/2),(x,w,z+thickness/2),(x,-w,z+thickness/2)])
  f=[(3,2,1,0),tuple(range((len(rows)-1)*4,len(rows)*4))]
  for i in range(len(rows)-1):
   for j in range(4):f.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
  o=b.obj(name,v,f,mat,.002);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 loft('Ceiling_tapered_roof_following_liner',stations,.028,'wall')
 loft('Ceiling_center_duct',[(x,.13,z-.058) for x,w,z in stations],.070,'desk')
 for x,w in[(7.52,1.39),(8.10,1.39),(8.68,1.30)]:b.box('Ceiling_panel_join',(x,0,liner_height(x)-.015),(.004,w*2,.003),'panel',.001)
 for y in[-1.26,1.26]:
  for x in[7.35,7.86,8.36,8.88]:b.screw('Ceiling_liner_screw',(x,y if x<8.80 else y*.90,liner_height(x)-.016),.0048,(1,0,0),(0,-1,0))
 for side in[-1,1]:
  y=side*.65
  b.box('Ceiling_tube_light_body',(8.026,y,3.548),(.69,.137,.047),'desk',.009)
  b.box('Ceiling_tube_light_dark_gasket',(8.026,y,3.523),(.63,.111,.010),'rubber',.006)
  b.box('Ceiling_tube_light_diffuser',(8.026,y,3.513),(.609,.096,.018),'diffuser',.005)
  for x in[7.741,8.312]:
   b.box('Ceiling_light_end_clip',(x,y,3.511),(.024,.11,.030),'edge',.002)
   b.screw('Ceiling_light_clip_screw',(x,y,3.493),.0035,(1,0,0),(0,-1,0))
  # Behind the desk edge, a small directional task-lamp fitting.
  b.box('Desk_task_lamp_mount',(8.921,side*1.072,3.423),(.165,.064,.055),'desk',.008)
  b.box('Desk_task_lamp_diffuser',(8.921,side*1.072,3.391),(.129,.043,.012),'diffuser',.004)
  build_fan(b,side)
 # Air grille has real slots and fasteners, not a black painted rectangle.
 b.box('Ceiling_vent_frame',(7.573,0,3.546),(.283,.249,.044),'desk',.006)
 b.box('Ceiling_vent_dark_cavity',(7.573,0,3.520),(.244,.209,.013),'black',.005)
 for j in range(12):b.box('Ceiling_vent_louvre',(7.463+j*.020,0,3.506),(.011,.207,.016),'edge',.002)
 for x in[7.446,7.700]:
  for y in[-.113,.113]:b.screw('Ceiling_vent_fastener',(x,y,3.517),.0033,(1,0,0),(0,-1,0))


def build_fan(b,side):
 n='Crew_fan_'+str(side);c=Vector((8.735,side*1.177,3.308));A=Vector((-.77,-side*.13,-.39)).normalized();R=Vector((0,-1,0));R=(R-A*R.dot(A)).normalized();U=A.cross(R).normalized()
 # A guarded 260 mm fan, tilted toward the crew, with motor and articulated bracket.
 b.box(n+'_wall_base',(8.852,side*1.414,3.328),(.120,.041,.113),'desk',.007)
 b.rod(n+'_support',(8.852,side*1.39,3.328),c-A*.09,.014,'edge',24)
 b.cyl(n+'_tilt_joint',c-A*.09,.026,.044,'edge',R,32)
 b.cyl(n+'_motor',c-A*.047,.052,.071,'desk',A,40,b=.008)
 b.cyl(n+'_shaft',c-A*.003,.013,.053,'steel',A,24)
 b.ring(n+'_cage_outer',c,.135,.131,.029,'panel',R,U,64)
 # Rear and front wire cages: radial ribs plus concentric rings.
 for face in[-1,1]:
  for rad in[.045,.068,.090,.111,.130]:
   z=face*(.020+.018*(1-(rad/.135)**2));b.ring(n+'_guard_ring',c+A*z,rad+.0011,rad-.0011,.0022,'edge',R,U,64)
  for j in range(12):
   a=j*2*pi/12;pts=[]
   for k in range(6):
    rad=.024+k*.0212;z=face*(.020+.018*(1-(rad/.135)**2));pts.append(c+A*z+R*(rad*cos(a))+U*(rad*sin(a)))
   b.tube(n+'_guard_spoke',pts,.00145,'edge',8)
 # Three broad curved blades with a deliberately tiny aerodynamic twist.
 for j in range(3):
  ang=j*2*pi/3;pts=[]
  for r,a,z in[(.024,-.30,.001),(.103,-.04,.009),(.118,.20,.001),(.111,.45,-.009),(.032,.68,-.006)]:
   pts.append(c+R*(r*cos(ang+a))+U*(r*sin(ang+a))+A*z)
  b.obj(n+'_blade',pts,[tuple(range(5))],'desk',.001,smooth=False)
 b.cyl(n+'_hub_front',c+A*.033,.025,.017,'panel',A,40,b=.004)
 b.cyl(n+'_hub_cap',c+A*.044,.015,.004,'edge',A,32,b=.001)
 b.tube(n+'_power_lead',[c-A*.074,c-A*.105+Vector((0,side*.04,.07)),Vector((8.87,side*1.411,3.429)),Vector((8.58,side*1.411,3.51))],.004,'rubber',10)


def build_foot_controls(b):
 R=Vector((0,-1,0));U=Vector((.907,0,.422));N=R.cross(U);c=Vector((8.728,.783,1.823))
 b.slab('Driver_inclined_footboard',c,1.006,.415,.047,'desk',R,U,b=.009)
 for u in[-.472,.472]:
  for v in[-.176,.176]:b.screw('Footboard_captive_screw',c+R*u+U*v+N*.026,.006,R,U)
 for j,label in enumerate(['SANDING','PVEF','VIGILANCE']):
  cc=c+R*(-.295+j*.295)+U*.015+N*.039
  b.slab(label+'_foot_switch_body',cc,.106,.153,.033,'panel',R,U,b=.008)
  b.slab(label+'_foot_switch_pedal',cc+N*.020,.092,.109,.018,'rubber',R,U,b=.006)
  for k in range(6):b.slab(label+'_pedal_grip_rib',cc+N*.031+U*(-.040+k*.016),.084,.0035,.003,'panel',R,U,b=.0008)
  for u in[-.038,.038]:b.screw(label+'_base_screw',cc+R*u-U*.066+N*.018,.003,R,U)
  # Function remains in the object name. Factory photo does not establish a
  # readable floor legend, so no invented printed tag is added.
 # Assistant's unobstructed footwell and low heater grille.
 b.box('Assistant_footwell_heel_bar',(8.625,-.968,1.711),(.154,.480,.045),'rubber',.009)
 b.box('Footwell_heater_housing',(8.896,-.935,1.853),(.215,.619,.220),'desk',.011)
 b.box('Footwell_heater_recess',(8.777,-.935,1.853),(.012,.545,.151),'black',.003)
 for j in range(12):b.box('Footwell_heater_louvre',(8.765,-1.183+j*.045,1.853),(.018,.023,.148),'desk',.002)

def build_seats(b):
 for j,y in enumerate([.78,-.90]):
  n='Driver_seat' if j==0 else 'Assistant_seat';x=7.98
  b.cyl(n+'_floor_pedestal_flange',(x,y,1.674),.181,.083,'desk',(0,0,1),56,b=.007)
  b.ring(n+'_flange_rubber_seal',(x,y,1.639),.185,.142,.012,'rubber',(1,0,0),(0,1,0),56)
  for a in[pi/4,pi*3/4,pi*5/4,pi*7/4]:
   xx=x+.146*cos(a);yy=y+.146*sin(a);b.cyl(n+'_flange_washer',(xx,yy,1.707),.014,.003,'edge',(0,0,1),24);b.cyl(n+'_flange_hexbolt',(xx,yy,1.713),.010,.010,'screw',(0,0,1),6,b=.001)
  b.cyl(n+'_pedestal_sleeve',(x,y,1.80),.071,.214,'panel',(0,0,1),48,b=.007)
  b.cyl(n+'_chrome_suspension_column',(x,y,1.883),.052,.184,'steel',(0,0,1),48)
  b.cyl(n+'_column_wiper_ring',(x,y,1.87),.066,.021,'rubber',(0,0,1),40,b=.002)
  b.box(n+'_suspension_base',(x,y,1.927),(.276,.261,.044),'panel',.007)
  # Real accordion folds, complete sides, with little valleys between the ribs.
  b.box(n+'_suspension_bellows_core',(x,y,1.982),(.217,.215,.138),'rubber',.014)
  for k in range(7):b.box(n+f'_suspension_bellows_fold_{k}',(x,y,1.929+k*.017),(.258,.248,.013),'rubber',.009)
  # Visible height adjustment and fore/aft slide hardware.
  for yy in[y-.180,y+.180]:
   b.box(n+'_fore_aft_rail',(8.009,yy,2.071),(.477,.037,.039),'edge',.004)
   b.box(n+'_fore_aft_rail_slot',(8.009,yy,2.077),(.389,.007,.015),'black',.001)
  b.rod(n+'_adjustment_lever',(8.087,y+.203,2.035),(8.190,y+.281,2.040),.008,'steel',20)
  b.cyl(n+'_adjustment_grip',(8.193,y+.280,2.042),.019,.065,'rubber',(1,0,0),32,b=.005)
  b.rod(n+'_slider_release_bar',(8.219,y-.173,2.06),(8.219,y+.173,2.06),.010,'panel',24)
  b.box(n+'_pressed_seat_pan',(8.015,y,2.102),(.486,.535,.059),'panel',.029)
  # Soft compound-curved cushion: slightly hollowed centre, raised bolsters, rounded perimeter.
  NX,NY=16,16;v=[]
  def cushion_z(xx,yy):return 2.186+.018*abs(xx/.249)**5+.034*abs(yy/.262)**4-.011*cos(xx/.249*pi/2)*cos(yy/.262*pi/2)
  for k in range(NX+1):
   xx=-.249+k*.498/NX
   for l in range(NY+1):
    yy=-.262+l*.524/NY;v.append((8.025+xx,y+yy,cushion_z(xx,yy)))
  faces=[]
  for k in range(NX):
   for l in range(NY):
    a=k*(NY+1)+l;faces.append((a,a+1,a+NY+2,a+NY+1))
  edge=list(range(NY+1))+[k*(NY+1)+NY for k in range(1,NX+1)]+[NX*(NY+1)+l for l in range(NY-1,-1,-1)]+[k*(NY+1) for k in range(NX-1,0,-1)]
  bottom=[]
  for idx in edge:xx,yy,zz=v[idx];bottom.append(len(v));v.append((xx,yy,2.132))
  for k,idx in enumerate(edge):faces.append((idx,edge[(k+1)%len(edge)],bottom[(k+1)%len(edge)],bottom[k]))
  faces.append(tuple(reversed(bottom)));o=b.obj(n+'_contoured_vinyl_cushion',v,faces,'vinyl',.010,True);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  # Perimeter piping is a true narrow bead. Stitch runs are short dashes, not drawn scratches.
  pts=[]
  for xx,yy in[(-.232,-.243),(.226,-.243),(.242,-.224),(.242,.224),(.226,.243),(-.232,.243),(-.242,.224),(-.242,-.224)]:pts.append((8.025+xx,y+yy,cushion_z(xx,yy)-.007))
  b.tube(n+'_cushion_piping',pts,.0022,'vinylside',10,True)
  for yy in[-.196,.196]:
   pts=[(7.800+k*.450/20,y+yy,cushion_z(-.225+k*.450/20,yy)+.0008) for k in range(21)]
   b.tube(n+'_cushion_sewn_channel',pts,.00085,'vinylside',6)
   for k in range(31):
    xx=-.223+k*.0145;z=cushion_z(xx,yy)+.0011;b.rod(n+'_cushion_stitch',(8.025+xx,y+yy+.002,z),(8.025+xx+.006,y+yy+.002,z),.00045,'stitch',6)
  # Back shell and shaped vinyl front preserve the original crew seat location.
  b.slab(n+'_back_shell',(7.742,y,2.493),.523,.574,.098,'panel',R=(0,-1,0),U=(-.08988,0,.99595),b=.040)
  for yy in[y-.159,y+.159]:b.rod(n+'_back_support',(7.791,yy,2.100),(7.752,yy,2.49),.018,'panel',24)
  NZ,NY=18,16;v=[]
  def face_x(yy,z):return 7.844-.09*(z-2.23)+.023*(1-(yy/.251)**2)+.006*cos((z-2.23)/.526*pi)
  for k in range(NZ+1):
   z=2.233+k*.526/NZ
   for l in range(NY+1):
    yy=-.251+l*.502/NY;v.append((face_x(yy,z),y+yy,z))
  faces=[]
  for k in range(NZ):
   for l in range(NY):a=k*(NY+1)+l;faces.append((a,a+1,a+NY+2,a+NY+1))
  edge=list(range(NY+1))+[k*(NY+1)+NY for k in range(1,NZ+1)]+[NZ*(NY+1)+l for l in range(NY-1,-1,-1)]+[k*(NY+1) for k in range(NZ-1,0,-1)]
  rear=[]
  for idx in edge:xx,yy,z=v[idx];rear.append(len(v));v.append((xx-.082,yy,z))
  for k,idx in enumerate(edge):faces.append((idx,edge[(k+1)%len(edge)],rear[(k+1)%len(edge)],rear[k]))
  faces.append(tuple(reversed(rear)));o=b.obj(n+'_shaped_vinyl_backrest',v,faces,'vinyl',.012,True);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  pts=[]
  for yy,z in[(-.227,2.254),(.227,2.254),(.240,2.276),(.240,2.715),(.219,2.740),(-.219,2.740),(-.240,2.715),(-.240,2.276)]:pts.append((face_x(yy,z)+.001,y+yy,z))
  b.tube(n+'_backrest_piping',pts,.0022,'vinylside',10,True)
  for yy in[-.189,.189]:
   pts=[(face_x(yy,z)+.001,y+yy,z) for z in[2.277+k*.440/20 for k in range(21)]];b.tube(n+'_backrest_channel',pts,.0010,'vinylside',8)
   for k in range(31):
    z=2.278+k*.014;b.rod(n+'_backrest_stitch',(face_x(yy,z)+.0016,y+yy+.002,z),(face_x(yy,z+.006)+.0016,y+yy+.002,z+.006),.00045,'stitch',6)
  # Hinged armrests, pivot buttons, underside brackets and lightly radiused pads.
  for side in[-1,1]:
   yy=y+side*.294
   b.rod(n+'_armrest_upright',(7.823,yy,2.102),(7.823,yy,2.370),.018,'edge',28)
   b.cyl(n+'_armrest_pivot',(7.823,yy,2.354),.030,.035,'panel',(0,1,0),32,b=.003)
   b.cyl(n+'_armrest_pivot_cap',(7.823,yy+side*.023,2.354),.021,.009,'edge',(0,1,0),32,b=.001)
   b.box(n+'_armrest_underbar',(7.999,yy,2.373),(.350,.040,.027),'panel',.007)
   b.box(n+'_armrest_vinyl_pad',(7.999,yy,2.410),(.375,.076,.054),'rubber',.023)
   for xx in[7.86,8.12]:b.cyl(n+'_armrest_pad_fastener',(xx,yy,2.361),.004,.006,'screw',(0,0,1),16)
  # Subtle coat-hook and adjustment knob are physical fittings, not random detail.
  b.cyl(n+'_back_recline_adjuster',(7.783,y-.291,2.207),.038,.030,'rubber',(0,1,0),48,b=.003)
  for k in range(20):
   a=k*2*pi/20;b.cyl(n+'_adjuster_knurl',(7.783+.037*cos(a),y-.291,2.207+.037*sin(a)),.0024,.028,'panel',(0,1,0),8)


def apply(context=None):
 """Replace old visible cab furnishing reversibly. Return build evidence.

 context may contain texture_dir, material_overrides, and roots=(cab1,cab2).
 The controls are static visual assemblies; no game camera/runtime claim.
 """
 global TEXTURES
 ctx=context if isinstance(context,dict) else {}
 if 'texture_dir' in ctx:TEXTURES=Path(ctx['texture_dir'])
 needed=['meter_battery.png','gauge_bc.png','lcd_blank.png','speedometer.png']
 for f in needed:
  if not (TEXTURES/f).is_file():raise FileNotFoundError('Run scripts/make_cab_instruments.py first: '+str(TEXTURES/f))
 roots=ctx.get('roots') or [bpy.data.objects.get('CAB_A_INTERIOR'),bpy.data.objects.get('CAB_B_INTERIOR')]
 if len(roots)!=2 or not all(roots):raise ValueError('Both preserved CAB_A_INTERIOR and CAB_B_INTERIOR roots are required')
 for o in list(bpy.data.objects):
  if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
 coll=bpy.data.collections.get(PREFIX+'INTERIORS')
 if not coll:coll=bpy.data.collections.new(PREFIX+'INTERIORS');bpy.context.scene.collection.children.link(coll)
 coll['reference_scope']='Conventional WAP7/E70 visual interpretation; not a surveyed exact 39002 cab'
 coll['source_factory']=SOURCE_FACTORY;coll['source_controls']=SOURCE_PANEL;coll['source_equipment']=SOURCE_EQUIPMENT
 coll['machine_room_scope']='Framed rear openings and hinged doors default closed. Central machinery room supplied separately; this module makes no exterior shell cuts.'
 old=bpy.data.collections.get('CAB_INTERIORS_V02');hidden=[]
 if old:
  for o in old.objects:
   if o.type!='EMPTY':
    o.hide_render=True;o.hide_viewport=True;o['CABV02_replaced_visible']=True;hidden.append(o.name)
 materials=palette();materials.update(ctx.get('material_overrides') or {})
 builds=[]
 for index,root in enumerate(roots,1):
  b=Cab(root,index,coll,materials);build_shell_fittings(b);build_controls(b);build_seats(b);builds.append(b)
 bpy.context.view_layer.update()
 stats={'cab_roots':[o.name for o in roots],'added_objects':sum(len(b.created) for b in builds),'hidden_legacy_interior_objects':len(hidden),'texture_assets':len(list(TEXTURES.glob('*.png'))),'preserved_cavity':True,'machine_room_modelled':False,'rear_doors':'Physical opening, glass pane, hinge with open_angle_deg default 0','rear_door_clear_opening_m':[.694,1.8365],'static_visual_controls':True,'exact_unit_survey':False,'reference_panel_a':'Photograph visually inspected, readable equipment designators transcribed','gauge_calibrations':'Representative original artwork; no functional calibration claim','confidence_dimensions':'Estimated within preserved cavity, not measured manufacturer dimensions'}
 coll['build_report']=json.dumps(stats);return stats


def set_rear_door_angle(cab_index, angle_degrees=0.0):
 """Open an existing authored door rigidly. Intended for review/cutaway variants."""
 hinge=bpy.data.objects[f'CABV02_{int(cab_index)}_Rear_door_hinge']
 hinge['open_angle_deg']=max(0.0,min(90.0,float(angle_degrees)))
 hinge.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
 return hinge
