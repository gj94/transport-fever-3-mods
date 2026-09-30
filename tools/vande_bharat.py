"""TF3 integration settings for the compact Vande Bharat source family."""
import json, math

CAPACITY={'DTC':40,'MC':60,'MC2':60,'TC_CC':60,'TC_EC':40,'NDTC_EC':40,'NDTC_EC2':40}
# Initial gameplay tuning, not certified full-size train specifications.
WEIGHT={'DTC':42000,'MC':45000,'MC2':45000,'TC_CC':48000,'TC_EC':48000,'NDTC_EC':44000,'NDTC_EC2':44000}

def sample_tracks(bpy,objects,clean):
 from mathutils import Matrix
 tracks={}
 ctrl=next((o for o in objects if o.name=='PANTO_CTRL'),None)
 if ctrl:
  pivots=[bpy.data.objects['PANTO_'+part] for part in ('LOWER_PIVOT','ELBOW_PIVOT','HEAD_LEVEL_PIVOT')]
  ctrl['extension']=0.;ctrl.update_tag();bpy.context.view_layer.update()
  rest={o:o.matrix_local.copy() for o in pivots};values={o:[] for o in pivots}
  low=4.032+2.7*math.sin(ctrl['angle_min_rad']);high=5.917
  for i in range(101):
   height=low+(high-low)*i/100
   ctrl['extension']=(math.asin((height-4.032)/2.7)-ctrl['angle_min_rad'])/(ctrl['angle_max_rad']-ctrl['angle_min_rad'])
   ctrl.update_tag();bpy.context.view_layer.update()
   head=pivots[-1].matrix_world
   assert abs(head.translation.z+.032-height)<2e-5
   assert max(abs(v) for v in head.to_euler())<1e-5
   for o in pivots:
    delta=rest[o].inverted()@o.matrix_local
    values[o].append([float(delta[r][c]) for c in range(4) for r in range(4)])
  ctrl['extension']=0.;ctrl.update_tag();bpy.context.view_layer.update()
  for o in pivots:tracks[clean(o.name)]={'pantograph':{'times':list(range(0,1001,10)),'transfs':values[o]}}
 for o in objects:
  if not o.name.startswith('DOOR_') or 'open_translation_local_m' not in o:continue
  travel=o['open_translation_local_m'];values=[]
  for i in range(21):
   t=i/20;slide=max(0,(t-.2)/.8);plug=min(1,t/.2)
   matrix=Matrix.Translation((travel[0]*slide,travel[1]*plug,0))
   values.append([float(matrix[r][c]) for c in range(4) for r in range(4)])
  side='left' if '_L_' in o.name else 'right';states={}
  for action in ('open','close'):
   track={'times':list(range(0,2001,100)),'transfs':values if action=='open' else list(reversed(values))}
   states[action+'_doors_'+side]=track;states[action+'_all_doors']=track
  tracks[clean(o.name)]=states
 return tracks

def write_formations(rootdir,write_lua):
 folder=rootdir/'game_build/gj94_indian_rail_pack/content/vehicle/train/vande_bharat'
 folder.mkdir(parents=True,exist_ok=True)
 report=[]
 for count in (8,16):
  source=json.loads((rootdir/f'vande_bharat_v01/assemblies/VB_{count}_formation.json').read_text())
  # Game MU ordering is front-to-back (+X first), opposite the source's
  # ascending-X review layout. Preserve handedness relative to the train.
  vehicles=[{'name':'gj94_indian_rail_pack::/vehicle/train/vb_'+car['type'].lower()+'/vb_'+car['type'].lower()+'.mdl','forward':car['rotation_z_deg']==180} for car in source['cars']]
  assert vehicles[0]['forward'] and not vehicles[-1]['forward']
  assert sum(CAPACITY[c['type']] for c in source['cars'])==source['passenger_seats_compact_total']
  write_lua(folder/f'vande_bharat_{count}.mu.lua',{'vehicles':vehicles,'name':f'Vande Bharat Express ({count} cars)','desc':f'Compact white/blue electric trainset. {source["passenger_seats_compact_total"]} seats, {source["total_outer_anchor_span_m"]:g} m spacing length. Requires electrified track.','filterTags':['default']})
  report.append({'cars':count,'capacity':source['passenger_seats_compact_total'],'spacing_length_m':source['total_outer_anchor_span_m'],'pantograph_indices':source['pantograph_indices'],'vehicles':vehicles})
 (rootdir/'game_build/vande_bharat_formations.json').write_text(json.dumps(report,indent=2))
