"""Create a full-size car scaffold with explicit prototype datums, not stretched compact meshes."""
import bpy,math,sys,importlib.util
from pathlib import Path
from mathutils import Matrix
from prototype_dimensions import layout_for
LEGACY=Path(__file__).resolve().parents[2]/'vande_bharat_v01/build_vande_bharat.py'
saved_args=sys.argv;sys.argv=[sys.argv[0]]
spec=importlib.util.spec_from_file_location('legacy_vb_primitives',LEGACY);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);sys.argv=saved_args

def build(kind):
 bpy.ops.wm.read_factory_settings(use_empty=True);g.M.clear();g.batches.clear();g.materials();g.PITCH=24.;g.HALF=12.;g.BODYEND=11.55;g.BOGIE=7.45;g.WBASE=2.7
 L=layout_for(kind);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=24
 g.COL=bpy.data.collections.new(f'VB_{kind}_ASSET');sc.collection.children.link(g.COL);g.ROOT=g.empty(f'VB_{kind}_ROOT');root=g.ROOT;body=g.empty('BODY',root)
 root['asset_type']=kind;root['coupling_pitch_m']=24.;root['source_dimensions']='Prototype VB2 2022:24m over couplers,14.9m bogie centers';root['coordinate_system']='Metres,+Xforward,Ylateral,+Zup,railZ0';root['baseline_relationship']='New full-size source; original compact v01 remains unchanged'
 for name,sign in [('FRONT',1),('REAR',-1)]:
  e=g.empty('COUPLING_'+name,root,(sign*12,0,1.105 if kind=='DTC' and sign>0 else .940));e.rotation_euler.z=0 if sign>0 else math.pi;e['mating_plane_axis']='local +X outward';e['datum_role']='Nominal24m over-coupler datum; DTC closed fairing tip is behind this plane' if kind=='DTC' and sign>0 else 'Internal semi-permanent coupling datum'
 end=L['cab_shell_rear_x'] if kind=='DTC' else 11.55
 # Segmented side walls are built directly around correct full-size glazing and entry openings.
 windows=L['windows'];doors=L['passenger_door_x']
 for s in [-1,1]:
  holes=[(w['x']-w['width']/2,w['x']+w['width']/2,w['center_z']-w['height']/2,w['center_z']+w['height']/2,'window') for w in windows if s in w.get('sides',[-1,1])]+[(x-.505,x+.505,1.32,3.20,'door') for x in doors]
  xs=sorted(set([-11.55,end]+[p for h in holes for p in h[:2]]));zs=sorted(set([1.20,1.32,3.20]+[z for h in holes for z in h[2:4]]))
  for a,b in zip(xs,xs[1:]):
   if a<-11.55 or b>end:continue
   for za,zb in zip(zs,zs[1:]):
    if any(h[0]<(a+b)/2<h[1] and h[2]<(za+zb)/2<h[3] for h in holes):continue
    g.box('Open_sidewall',body,((a+b)/2,s*1.572,(za+zb)/2),(b-a,.096,zb-za),'Pearl_white')
   if not any(h[4]=='door' and h[0]<(a+b)/2<h[1] for h in holes):g.box('Lower_blue_belt',body,((a+b)/2,s*1.623,1.51),(b-a,.006,.07),'Cobalt_blue')
  for wi,w in enumerate(windows):
   if s not in w.get('sides',[-1,1]):continue
   x=w['x'];hw=w['width']/2;lo=w['center_z']-w['height']/2;hi=w['center_z']+w['height']/2
   g.panel('Window_clear_glazing',body,[(x-hw,s*1.614,lo),(x+hw,s*1.614,lo),(x+hw,s*1.614,hi),(x-hw,s*1.614,hi)],'Clear_glass')
  for j,x in enumerate(doors):
   e=g.empty(f'DOOR_{"L" if s>0 else "R"}_{j+1}_SLIDE',body,(x,s*1.58,1.32));e['open_translation_local_m']=[1.04,s*.09,0];e['closed_location_m']=list(e.location);e['type']='Single plug-sliding leaf, actual runtime trigger not supplied'
   g.box('Door_threshold',body,(x,s*1.593,1.315),(1.10,.07,.025),'Steel')
 # Full structural shell/floor. Detailed roofs/linings replace visual scaffold accessories.
 g.roof(body,-11.55,end)
 g.box('Saloon_floor',body,((-11.55+end)/2,0,1.26),(end+11.55,3.09,.12),'Floor')
 if kind=='DTC':
  outline=[(7.30,-1.49),(11.20,-1.38)]+[(11.70-.24*((-1.38+i*2.76/20)/1.43)**2,-1.38+i*2.76/20) for i in range(21)]+[(11.20,1.38),(7.30,1.49)]
  nn=len(outline);vv=[(x,y,z) for z in [1.20,1.32] for x,y in outline];ff=[tuple(reversed(range(nn))),tuple(range(nn,2*nn))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)];g.add('Cab_floor',body,vv,ff,'Floor')
  for s in [-1,1]:g.box('Cab_partition',body,(7.30,s*.99,2.36),(.065,1.15,2.16),'Interior_ivory')
  g.box('Cab_partition_lintel',body,(7.30,0,3.34),(.065,.85,.20),'Interior_ivory')
 # Actual-count markers come from the same layout records used by detailed seats.
 for i,p in enumerate(L['seat_poses'],1):
  e=g.empty(f'PAX_{i:03d}',body,(p['x'],p['y'],1.267));e.rotation_euler.z=0 if p['facing']>0 else math.pi;e['facing_local_axis']='+X';e['cushion_top_z_m']=1.75;e['posed_hip_offset_assumed_m']=.483;e['layout_seat_index']=i
 if kind=='DTC':
  for i,y in enumerate([-.73,.73],1):
   e=g.empty(f'DRIVER_{i:03d}',body,(9.35,y,1.267));e['cushion_top_z_m']=1.75;e['posed_hip_offset_assumed_m']=.483
  g.empty('CAB_EYE_CAMERA_REFERENCE',body,(9.39,-.73,2.49))['note']='Authoring eye reference, not runtime camera certification'
  for s in [-1,1]:
   for j,z in enumerate([1.91,2.095]):g.empty(f'LIGHT_{"L" if s>0 else "R"}_{j}_ANCHOR',body,(11.62,s*1.28,z))
 g.bogies(body,kind.startswith('MC'))
 # Role-specific underfloor equipment is laid out, with component lengths retained.
 U=L['underframe'];g.box('Underframe_spine',body,(0,0,1.08),(22.8,.55,.23),'Graphite')
 for s in [-1,1]:g.box('Body_sill',body,((-11.55+end)/2,s*1.46,1.16),(end+11.55,.19,.19),'Roof_silver')
 if kind.startswith('MC'):
  for x in U['converter_centres']:g.box('Traction_converter_cabinets',body,(x,0,.76),(2.5,2.35,.53),'Roof_silver')
  if kind=='MC2':g.box('Electrical_changeover_switch',body,(0,-.70,.75),(.88,.7,.51),'Graphite')
 elif kind.startswith('TC'):
  x=U['transformer_x'];g.box('Transformer_case',body,(x,0,.71),(3.0,2.30,.55),'Graphite')
  for k in range(16):g.box('Transformer_cooling_fins',body,(x-1.42+k*.19,0,.72),(.045,2.52,.58),'Roof_silver')
  g.box('Auxiliary_converter',body,(U['auxiliary_x'],0,.76),(2.0,2.27,.49),'Roof_silver')
 else:
  hand=-1 if kind=='NDTC_EC2' else 1
  g.box('Battery_box',body,(hand*U['battery_x'],0,.76),(2.4,2.2,.48),'Roof_silver')
  x=hand*U['reservoir_x'];g.rod('Main_reservoir',body,(x-1.3,-.6,.73),(x+1.3,-.6,.73),.24,'Graphite',24)
  x=hand*U['water_x'];g.rod('Water_tank',body,(x-1.2,.65,.75),(x+1.2,.65,.75),.28,'Roof_silver',24)
  g.box('Compressor',body,(hand*U['compressor_x'],0,.76),(1.,1.45,.5),'Graphite')
 # 0.9m body-end gap, hollow gangways and matching internal coupling planes.
 for sg in [-1] if kind=='DTC' else [-1,1]:
  x=sg*11.55
  for s in [-1,1]:g.box('End_wall',body,(x,s*1.03,2.24),(.09,1.08,2.06),'Pearl_white')
  g.box('End_wall_top',body,(x,0,3.44),(.09,3.06,.36),'Pearl_white')
  for k in range(9):g.ring('Gangway_bellows',body,sg*(11.58+k*.0485),1.19,1.32,3.38,'Rubber',.036)
  g.box('Gangway_floor_bridge',body,(sg*11.765,0,1.305),(.43,1.1,.04),'Steel')
  g.rod('Semipermanent_coupling_bar',body,(sg*11.20,0,.940),(sg*12.,0,.940),.085,'Graphite',16)
  for s in [-1,1]:g.line('Intercar_hoses',body,[(sg*11.51,s*.31,1.12),(sg*11.77,s*.32,.95),(sg*11.975,s*.31,1.04)],.022,'Rubber',12)
 if kind.startswith('TC'):
  g.pantograph(body);base=bpy.data.objects['PANTO_BASE'];base.location.x=L['panto_base_x'];base.rotation_euler.z=L['panto_rotation_z']
  ctrl=bpy.data.objects['PANTO_CTRL'];amin=math.asin((4.260-4.0-.032)/2.7);amax=math.asin((5.917-4.0-.032)/2.7);ctrl['angle_min_rad']=amin;ctrl['angle_max_rad']=amax
  for name,fac in [('PANTO_LOWER_PIVOT',-1),('PANTO_ELBOW_PIVOT',2),('PANTO_HEAD_LEVEL_PIVOT',-1)]:bpy.data.objects[name].animation_data.drivers[0].driver.expression=f'{fac}*({amin}+max(0,min(1,e))*{amax-amin})'
 g.flush();bpy.context.view_layer.update();return {'kind':kind,'root':root,'body':body,'collection':g.COL,'layout':L}
