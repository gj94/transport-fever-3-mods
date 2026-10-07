"""Fresh reopen checks of full-size datums, actual seating meshes and pantograph kinematics."""
import bpy,math,json,hashlib,bmesh,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'));from prototype_dimensions import layout_for
KINDS=['DTC','MC','MC2','TC_CC','TC_EC','NDTC_EC','NDTC_EC2'];reports={}
for kind in KINDS:
 source=OUT/'cars'/f'VB_{kind}.blend';bpy.ops.wm.open_mainfile(filepath=str(source));sc=bpy.context.scene;root=bpy.data.objects[f'VB_{kind}_ROOT'];col=bpy.data.collections[f'VB_{kind}_ASSET'];L=layout_for(kind);checks={};fail=[]
 def test(n,v):checks[n]=bool(v);fail.extend([] if v else[n])
 test('metric_scale',sc.unit_settings.system=='METRIC' and sc.unit_settings.scale_length==1)
 test('identity_root',max(abs(v-(1 if i==j else 0)) for i,row in enumerate(root.matrix_world) for j,v in enumerate(row))<1e-7)
 for name,sign in [('FRONT',1),('REAR',-1)]:
  o=bpy.data.objects['COUPLING_'+name];z=1.105 if kind=='DTC' and sign>0 else .940
  test('coupling_'+name+'_datum',(o.location-Vector((sign*12,0,z))).length<1e-6 and o.parent==root)
 for lab,sign in [('A',1),('B',-1)]:
  bogie=bpy.data.objects[f'BOGIE_{lab}_YAW_Z'];test('bogie_'+lab+'_position',abs(bogie.location.x-sign*7.45)<1e-6 and bogie.parent==root)
  for j,x in [(1,-1.35),(2,1.35)]:
   ax=bpy.data.objects[f'AXLE_{lab}_{j}_ROLL_Y'];test(f'axle_{lab}_{j}_wheelbase_and_parent',abs(ax.location.x-x)<1e-6 and ax.parent==bogie)
 def under_root(o):
  while o.parent:o=o.parent
  return o==root
 test('asset_ancestry',all(under_root(o) for o in col.objects))
 test('finite_vertices',all(math.isfinite(c) for o in col.objects if o.type=='MESH' for v in o.data.vertices for c in v.co))
 test('external_images_resolve',all(im.packed_file or Path(bpy.path.abspath(im.filepath)).is_file() for im in bpy.data.images if im.source=='FILE'))
 pax=sorted([o for o in col.objects if o.type=='EMPTY' and o.name.startswith('PAX_')],key=lambda o:o.name);actual=[o for o in col.objects if o.type=='MESH' and o.get('detail_role')=='passenger_seat_instance']
 test('emergency_window_dimensions',all(abs(w['height']-.900)<1e-8 and abs(w['width']-1.580)<1e-8 for w in L['windows'] if w['emergency']))
 test('saloon_sill_callout',all(abs(w['center_z']-w['height']/2-2.085)<1e-8 for w in L['windows'] if w['role']=='saloon'))
 test('prototype_passenger_marker_count',len(pax)==L['expected_seats']);test('actual_detailed_chair_mesh_count',len(actual)==L['expected_seats'])
 test('actual_chairs_follow_separate_markers',all(o.parent in pax and o.scale==Vector((1,1,1)) for o in actual))
 test('seat_anchor_layout',all(abs(o.location.x-p['x'])<1e-5 and abs(o.location.y-p['y'])<1e-5 for o,p in zip(pax,L['seat_poses'])))
 test('two_secondary_bellows_each_bogie',sum(o.type=='MESH' and 'VB02_GEAR_secondary_air_bellow' in o.name for o in col.objects)==4)
 glass=[]
 for o in col.objects:
  if o.type=='MESH' and any(s in o.name for s in ['laminated_windscreen','cab_side_laminated_glass','door_laminated_glass']):
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());bm=bmesh.new();bm.from_mesh(ev.data);open_edges=sum(not e.is_manifold for e in bm.edges);bm.free();glass.append({'name':o.name,'nonmanifold_edges':open_edges})
 test('new_glazing_closed',all(g['nonmanifold_edges']==0 for g in glass))
 poses=[]
 if kind.startswith('TC'):
  ctrl=bpy.data.objects['PANTO_CTRL'];head=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT'];strips=[o for o in col.objects if o.name.startswith('VB02_ROOF_carbon_contact_strip')]
  for i in range(101):
   ctrl['extension']=i/100;ctrl.update_tag();bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in strips for v in o.data.vertices];normal=head.matrix_world.to_3x3()@Vector((0,0,1));poses.append({'extension':i/100,'contact_top_z':max(v.z for v in points),'head_level_error':(normal-Vector((0,0,1))).length})
  test('contact_top_folded_prototype_envelope',abs(poses[0]['contact_top_z']-4.260)<1e-5);test('contact_top_raised_authoring_target',abs(poses[-1]['contact_top_z']-5.917)<1e-5);test('head_level_101_poses',max(p['head_level_error'] for p in poses)<1e-6)
  ctrl['extension']=0;ctrl.update_tag();bpy.context.view_layer.update()
 build=json.loads((OUT/'qa'/f'VB_{kind}.json').read_text());seatreport=build['components']['interiors']
 report={'kind':kind,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'failures':fail,'actual_seat_meshes':len(actual),'armrest_clear_aisle_m':seatreport['armrest_clear_aisle_m'],'cab_glazing':glass,'pantograph_poses':poses,'dimension_contract':'24m pitch;14.9m bogie centers;2.7m bogie wheelbase;true-length source. Marker changes relative to compactv01 are intentional.','scope':'Authoring source QA; no accessibility certification, runtime character fit, TF3 conversion or full train dynamics asserted'};reports[kind]=report;print('QA',kind,fail,flush=True)
(OUT/'qa/validation_sources.json').write_text(json.dumps(reports,indent=2));assert not any(r['failures'] for r in reports.values()),'Source QA failures'
