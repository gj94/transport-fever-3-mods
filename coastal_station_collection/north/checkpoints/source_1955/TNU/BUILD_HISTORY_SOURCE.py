"""Add an explicitly unplaced August2016 Tirunettur facade/interior scene; preserve mapped-corridor scene."""
import bpy,math,json,sys,ast,hashlib,random,resource
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'TNU';q0=json.load(open(P/'QA_BUILD.json'));src=P/q0['blend_file'];bpy.ops.wm.open_mainfile(filepath=str(src));mapped=bpy.context.scene;mapped.name='MAP_CORRIDOR_ONLY__REMNANTS_UNVERIFIED';mapped['site_status']='CLOSED2017; historical remnant location not verified'
for o in mapped.objects:
 if o.type=='CAMERA':
  if o.name.startswith('01'):o.name='M1_Mapped_corridor_record'
  elif o.name.startswith('02'):o.name='M2_Closed_site_context'
  else:o.name='M3_Trackwork_optional'
sc=bpy.data.scenes.new('HISTORIC_2016_BUILDING__UNPLACED');bpy.context.window.scene=sc;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=1280;sc.render.resolution_y=854;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.image_settings.file_format='PNG'
sc.world=bpy.data.worlds.new('Historic neutral daylight');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.65,.78,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;sc.view_settings.view_transform='Standard';sc.view_settings.look='Medium High Contrast'
COL=None;CAT=None;BATCH={}
# Reuse original mesh/material utility definitions only, without running another station build.
master=Path(__file__).with_name('build_north.py');tree=ast.parse(master.read_text());names={'coll','mat','mesh','batchgeom','box','beam','cyl','tube','txt','texmat','plane'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=defs,type_ignores=[]),str(master),'exec'))
M={}
for name,color,rough,metal,noise in [('peach',(.87,.70,.56),.82,0,5),('orange',(.74,.29,.12),.78,0,6),('purple',(.24,.115,.20),.75,0,5),('red',(.48,.15,.15),.8,0,5),('white',(.8,.82,.75),.78,0,5),('dark',(.035,.035,.03),.72,0,0),('steel',(.30,.35,.34),.42,.7,8),('floor',(.44,.43,.38),.9,0,28),('wood',(.25,.12,.045),.8,0,7),('paper',(.84,.80,.63),.9,0,0)]:M[name]=mat('H2016 '+name,color,rough,metal,noise)
SIGN=texmat('H2016 original Tirunettur nameboard','board.png');NOTICE=texmat('H2016 original information graphic','notice.png')
coll('H2016 | Photo-derived historical envelope · UNPLACED')
W=15.5;D=6.8;floor=.15;h=4.5
box('Historical building floor',(0,0,.10),(W,D,.20),M['floor']);box('Historical context apron, approximate',(0,-6,-.025),(26,13,.05),M['floor'])
for x in[-W/2,W/2]:box('Historic end wall',(x,0,2.30),(.22,D,4.30),M['peach'])
# Real facade opening geometry, based on the visible2016 photograph.
openings=[(-5.1,-3.6,1.35,3.25,'grille'),(-1.0,1.0,.15,3.72,'entry'),(3.65,4.65,.15,2.90,'door'),(5.75,6.75,1.20,2.85,'shutter')]
last=-W/2
for a,b,zb,zt,kind in openings:
 if a>last:box('Historic facade masonry pier',((last+a)/2,-D/2,2.30),(a-last,.22,4.30),M['peach'])
 if zb>floor:box('Facade below opening',((a+b)/2,-D/2,(zb+floor)/2),(b-a,.22,zb-floor),M['peach'])
 box('Facade above opening',((a+b)/2,-D/2,(zt+h)/2),(b-a,.22,h-zt),M['peach'])
 if kind in['door','shutter']:
  box('Purple paneled '+kind,((a+b)/2,-D/2+.08,(zb+zt)/2),(b-a-.08,.09,zt-zb-.06),M['purple'])
  for z in [zb+.2,zb+(zt-zb)*.48,zt-.2]:box('Purple raised panel rail',((a+b)/2,-D/2-.005,z),(b-a-.16,.065,.055),M['purple'])
  for x in[a+.15,b-.15]:box('Purple vertical panel stile',(x,-D/2-.005,(zb+zt)/2),(.06,.065,zt-zb-.15),M['purple'])
 if kind=='grille':
  box('Dark recessed historic window',((a+b)/2,-D/2+.08,(zb+zt)/2),(b-a,.05,zt-zb),M['dark'])
  for z in[zb+.15+i*.25 for i in range(7)]:beam('Historic grille horizontal',(a,-D/2-.04,z),(b,-D/2-.04,z),.028,M['steel'])
  for x in[a+.22,a+.55,a+.88,a+1.2]:beam('Historic grille vertical',(x,-D/2-.04,zb),(x,-D/2-.04,zt),.026,M['steel'])
 if kind=='entry':
  for sg in[-1,1]:
   for j in range(8):x=sg*(.88+j*.018);beam('Folded black entry gate',(x,-D/2+.05,.16),(x,-D/2+.05,3.70),.022,M['dark'])
 last=b
box('Historic facade end',((last+W/2)/2,-D/2,2.30),(W/2-last,.22,4.30),M['peach'])
for sg in[-1,1]:box('Rear wall beside through passage',(sg*(W/4+.50),D/2,2.30),(W/2-1,.22,4.30),M['peach'])
box('Rear opening lintel',(0,D/2,4.05),(2.1,.22,.90),M['peach']);box('Historic flat roof slab',(0,0,4.50),(W+.2,D+.2,.20),M['peach']);box('Orange top parapet fascia',(0,-D/2-.02,4.67),(W+.35,.26,.22),M['orange'])
box('Deep continuous orange sunshade',(0,-D/2-.52,3.87),(W+.50,1.13,.22),M['orange']);box('Pale attic band',(0,-D/2,4.18),(W,.23,.50),M['peach']);beam('Visible diagonal drain stub',(.4,-D/2-.2,4.60),(.7,-D/2-.7,5.13),.075,M['floor']);beam('Left rainwater pipe',(-7.45,-D/2-.2,.15),(-7.45,-D/2-.2,4.55),.06,M['white'])
plane('Historic yellow Tirunettur wall name',(2.24,-D/2-.13,1.66),1.45,1.12,SIGN);plane('Original red information placard',(-1.50,-D/2-.13,1.50),.40,.65,NOTICE)
def bench(x,y):
 for z in [.53,.68,.83]:box('Historic red bench back slat',(x,y+.20,z),(2.15,.075,.115),M['red'])
 for yy in[y-.18,y,y+.18]:box('Historic red bench seat slat',(x,yy,.46),(2.15,.145,.08),M['red'])
 for xx in[x-.78,x+.78]:box('White concrete bench foot',(xx,y,.27),(.28,.58,.40),M['white'])
bench(-4.2,-4.55);bench(7.8,-4.5)
coll('H2016 | Furnished interior reconstruction · NOT SURVEYED')
# Modest waiting/booking interior, not a fabricated large concourse.
for y in[-1.6,.2]:bench(3.0,y)
box('Wood booking counter',(-4.3,.2,.72),(3.5,.80,1.10),M['wood']);box('Counter top',(-4.3,.2,1.30),(3.7,1.0,.09),M['wood'])
for x in[-5.75,-2.85]:box('Booking grille uprights',(x,.2,2.0),(.05,.07,1.35),M['steel'])
for x in[-5.4,-5,-4.6,-4.2,-3.8,-3.4]:box('Booking grille bars',(x,.2,2.0),(.022,.025,1.35),M['steel'])
box('Ticket shelf paperwork',(-4.6,.3,1.38),(.6,.45,.09),M['paper']);box('Station desk',(-4.3,2.0,.80),(2.1,.80,.09),M['wood'])
for x in[-5.1,-3.5]:box('Desk trestle',(x,2.0,.47),(.12,.65,.70),M['steel'])
box('Office chair seat',(-4.3,2.8,.50),(.55,.55,.10),M['wood']);box('Office chair back',(-4.3,3.03,.87),(.55,.075,.65),M['wood'])
for x in[-4.5,-4.1]:
 for y in[2.6,3.0]:beam('Office chair leg',(x,y,.15),(x,y,.47),.03,M['steel'])
box('Station storage cabinet',(-6.65,2.6,1.15),(1.05,.70,2.0),M['white'])
for z in[.55,1,1.45,1.90]:box('Cabinet handle',(-6.65,2.22,z),(.24,.04,.03),M['steel'])
for x in[-2.5,2.5]:
 beam('Ceiling fan stem',(x,0,4.30),(x,0,3.75),.035,M['dark']);cyl('Ceiling fan hub',(x,0,3.73),.11,.10,M['white'])
 for a in[0,math.tau/3,2*math.tau/3]:beam('Fan blade',(x+.1*math.cos(a),.1*math.sin(a),3.73),(x+.7*math.cos(a),.7*math.sin(a),3.73),.13,M['white'],.025)
 box('Ceiling light batten',(x,1.2,4.32),(1.15,.12,.06),M['white'])
for(cat,mn),g in BATCH.items():COL=g['col'];mesh(cat+' / '+mn,g['v'],g['f'],g['m'])
BATCH.clear();coll('H2016 | Review cameras and lighting')
def cam(name,pos,target,lens=42,ortho=None):
 ca=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,ca);COL.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens
 if ortho:ca.type='ORTHO';ca.ortho_scale=ortho
 return o
c1=cam('H1_Historical_2016_facade',(15,-23,8),(0,-2,2),45);c2=cam('H2_Historical_interior',(5,-2.5,2),(-3.2,.9,1.65),27);c3=cam('H3_Historical_building_overview',(16,-18,16),(0,-1,1.5),45,23);sc.camera=c1
sun=bpy.data.lights.new('H2016 afternoon sun','SUN');sun.energy=2.0;sun.angle=.16;o=bpy.data.objects.new('H2016 afternoon sun',sun);COL.objects.link(o);o.rotation_euler=(.5,-.4,-.5)
li=bpy.data.lights.new('Historic room soft fill','AREA');li.energy=180;li.size=5;o=bpy.data.objects.new('Historic room soft fill',li);COL.objects.link(o);o.location=(0,0,4.15)
sc['station_code']='TNU';sc['status']='Historical August2016 appearance. Closed10 July2017.';sc['georeferenced']=False;sc['location_status']='Unplaced facade/interior study. Do not position as a verified current remnant.';sc['interior_basis']='Reconstructed furniture and unseen rooms; no interior survey';sc['no_trains']=True
bpy.ops.file.pack_all();out=P/'TNU_coastal_station_v02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
q=q0.copy();q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'historical_scene_included':True,'historical_scene_name':sc.name,'mapped_scene_name':mapped.name,'historical_geometry_georeferenced':False,'historical_building_dimensions_m':[W,D,4.78],'historical_facade_basis':'Actual August2016 capture; current survival and precise remnant location unresolved.','furnished_interiors':'Historical2016 building only: modest reconstructed waiting and booking furniture. Current corridor scene has no invented operating station.','build_history_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'all_scene_names':[s.name for s in bpy.data.scenes],'cameras':[{'name':x,'scene':sc.name if x.startswith('H') else mapped.name} for x in ['H1_Historical_2016_facade','H2_Historical_interior','H3_Historical_building_overview','M1_Mapped_corridor_record','M2_Closed_site_context']]});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('HISTORICAL_TNU_ADDED',q['blend_sha256'])
