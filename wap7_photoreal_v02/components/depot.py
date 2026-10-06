"""Original generic depot background, not an as-built depiction of Royapuram shed."""
import bpy,math
from math import sin,pi
from mathutils import Vector
import common as C

def apply(col,mat):
 existing={o.name for o in col.objects}
 wall=mat('Depot weathered light cladding',(.30,.318,.312),.66,0,.09,120,.00012)
 roof=mat('Depot faded blue-grey roof',(.122,.160,.176),.53,0,.065,90,.00009)
 frame=mat('Depot dark structural paint',(.055,.064,.061),.56,0,.055,210,.00006)
 shutter=mat('Depot rolled aluminium shutters',(.177,.189,.184),.58,.7,.07,540,.00004)
 brick=mat('Depot brick plinth',(.21,.124,.067),.90,0,.15,150,.00075)
 mortar=brick.node_tree;bs=next(n for n in mortar.nodes if n.type=='BSDF_PRINCIPLED');tc=mortar.nodes.new('ShaderNodeTexCoord');sep=mortar.nodes.new('ShaderNodeSeparateXYZ');co=mortar.nodes.new('ShaderNodeCombineXYZ');mortar.links.new(tc.outputs['Object'],sep.inputs[0]);mortar.links.new(sep.outputs['X'],co.inputs[0]);mortar.links.new(sep.outputs['Z'],co.inputs[1]);br=mortar.nodes.new('ShaderNodeTexBrick');br.inputs['Scale'].default_value=2.2;br.inputs['Brick Width'].default_value=.50;br.inputs['Row Height'].default_value=.15;br.inputs['Mortar Size'].default_value=.018;br.inputs['Color1'].default_value=(.21,.10,.046,1);br.inputs['Color2'].default_value=(.285,.154,.070,1);br.inputs['Mortar'].default_value=(.215,.206,.183,1);mortar.links.new(co.outputs[0],br.inputs['Vector']);mortar.links.new(br.outputs['Color'],bs.inputs['Base Color'])
 glass=mat('Depot dark frosted windows',(.045,.066,.068),.27,.05,0,100,0)
 concrete=mat('Depot pale concrete apron',(.255,.255,.23),.91,0,.10,210,.0008)
 # Long shallow maintenance shed behind the track, with real bays/door recesses.
 doors=[-68,-54,-40,-26,-12];front=23.0
 def skin(a,b,lo,hi):
  N=max(2,int((b-a)/.027));v=[]
  for j in range(N+1):
   x=a+(b-a)*j/N;y=front+.010*sin(x*2*pi/.09);v.extend([(x,y,lo),(x,y,hi)])
  f=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(N)];C.mesh('ENV02 depot corrugated facade',v,f,wall,None,col)
 edges=[-87]+sum(([x-2.43,x+2.43] for x in doors),[])+[5]
 for i in range(0,len(edges)-1,2):
  a,b=edges[i],edges[i+1];skin(a,b,.58,4.25);C.box('ENV02 brick base wall',((a+b)/2,front+.09,.085),(b-a,.35,1.03),brick,None,col,b=.007)
 skin(-87,5,3.63,4.25)
 for x in doors:
  C.box('ENV02 shutter interior shadow',(x,front+.14,1.525),(4.86,.035,3.88),frame,None,col,b=0)
  # Fine rolled slats have bent fronts, and are genuinely recessed between structural columns.
  for j in range(55):
   z=-.37+j*.071;C.box('ENV02 rolled shutter slat',(x,front+.067,z),(4.66,.030,.067),shutter,None,col,b=.008)
  for xx in [x-2.43,x+2.43]:
   C.box('ENV02 door jamb steel channel',(xx,front-.05,1.565),(.16,.20,3.97),frame,None,col,b=.004)
  C.box('ENV02 door lintel steel channel',(x,front-.05,3.55),(5.01,.23,.16),frame,None,col,b=.004)
  C.box('ENV02 door threshold',(x,front-.09,-.34),(4.9,.40,.09),concrete,None,col,b=.008)
  C.box('ENV02 roller shutter hand grip',(x+.15,front+.037,.15),(.18,.035,.036),frame,None,col,b=.005)
  # Clipped clerestory panes and simple pressed mullions.
  for xx in [x-1.73,x-.57,x+.57,x+1.73]:
   C.box('ENV02 clerestory window',(xx,front-.007,3.92),(1.06,.019,.30),glass,None,col,b=.004)
   for dz in [-.157,.157]:C.box('ENV02 window transom',(xx,front-.025,3.92+dz),(1.10,.04,.018),frame,None,col,b=.002)
   C.box('ENV02 window mullion',(xx,front-.026,3.92),(.013,.04,.306),frame,None,col,b=.001)
 # Roof has a shallow industrial pitch and real corrugation/overhang, producing non-flat reflections.
 v=[];f=[];N=2300
 for i in range(N+1):
  x=-87.5+93*i/N;dz=.008*sin(x*2*pi/.09)
  for y,z in [(22.48,4.32),(30.0,6.07),(38.5,4.32)]:v.append((x,y,z+dz))
 for i in range(N):
  for j in range(2):f.append((i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1))
 C.mesh('ENV02 pitched corrugated shed roof',v,f,roof,None,col)
 for y,z in [(22.49,4.28),(38.49,4.28)]:C.box('ENV02 shed eaves channel',(-41,y,z),(93,.09,.13),frame,None,col,b=.008)
 C.box('ENV02 shed ridge flashing',(-41,30,6.085),(93,.21,.043),roof,None,col,b=.010)
 for x in [-83,-55,-27,1]:
  C.tube('ENV02 depot downpipe',C.bezier_points([(x,22.46,4.28),(x,22.34,4.18),(x,22.31,.05),(x,22.20,-.23)],7),.034,frame,None,col,N=14)
 for x in range(-84,5,6):
  C.box('ENV02 facade structural column',(x,front-.015,1.86),(.12,.15,4.05),frame,None,col,b=.004)
 # Weathered concrete maintenance apron ends before the railway ballast, not a blank infinite stage.
 C.box('ENV02 depot paved service apron',(-41,18.50,-.425),(101,8.7,.07),concrete,None,col,b=.008)
 for x in range(-88,6,4):C.box('ENV02 apron expansion joint',(x,18.5,-.386),(.009,8.65,.003),frame,None,col,b=0)
 # Low side wall closes the shed, rather than a featureless open card edge.
 for x in [-87,5]:C.box('ENV02 shed return masonry',(x,30,1.9),(.25,14,4.6),wall,None,col,b=.009)
 # A taller industrial volume closes the real sky-ground horizon behind the locomotive.
 # Keep the door bases at terrain level; stretch upper walls, jambs and columns continuously.
 for obj in list(col.objects):
  if obj.name.startswith('ENV02 ') and any(k in obj.name for k in ['depot corrugated facade','pitched corrugated shed roof','shed eaves channel','shed ridge flashing','depot downpipe','facade structural column','shed return masonry']):
   for v in obj.data.vertices:
    if v.co.z>2.80:v.co.z=2.80+(v.co.z-2.80)*2.40
 # Move the shed behind the rear half of the locomotive, avoiding a roof-line tangent at the nose.
 for obj in list(col.objects):
  if obj.name not in existing and obj.type=='MESH':
   for v in obj.data.vertices:v.co.x-=75.0
 # Distant masonry boundary returns stop the empty terrain edge without a photographic backplate.
 for a,b,y in [(-220,-86,28.0),(-220,-100,76.0)]:
  C.box('ENV02 distant depot boundary',((a+b)/2,y,.73),(b-a,.28,2.30),wall,None,col,b=.018)
  C.box('ENV02 boundary coping',((a+b)/2,y,1.895),(b-a,.36,.07),concrete,None,col,b=.013)
  for x in range(int(a),int(b)+1,5):C.box('ENV02 boundary buttress',(x,y-.19,.78),(.38,.46,2.40),concrete,None,col,b=.012)
 return {'type':'Original generic maintenance-depot background','location_claim':'None; not an as-built Royapuram shed reconstruction'}
