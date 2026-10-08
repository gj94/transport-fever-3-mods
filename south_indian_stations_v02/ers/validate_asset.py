import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'ERS_full_station_v02.blend'));s=bpy.context.scene
heads=[o for o in s.objects if o.name.startswith('Physical rail crown')];pairs={}
for o in heads:
 bits=o.name.split();key=bits[3];side=bits[4];pairs.setdefault(key,{}).setdefault(side,[])
 allv=list(o.data.vertices)
 for i in range(0,len(allv),4):
  vv=allv[i:i+4]
  if len(vv)==4:pairs[key][side].append(sum((o.matrix_world@v.co for v in vv),Vector())/4)
gauges=[]
for key,ss in pairs.items():
 if '-1' not in ss or '1' not in ss:continue
 for a in ss['-1'][::max(1,len(ss['-1'])//20)]:
  matching=[(a-b).length for b in ss['1'] if abs((a-b).length-1.736)<.0001]
  if matching:gauges.append({'route':key,'inner_gauge_m':min(matching,key=lambda x:abs(x-1.736))-.060})
q={'opens_successfully':True,'objects':len(s.objects),'mesh_vertices':sum(len(o.data.vertices) for o in s.objects if o.type=='MESH'),'metres_per_unit':s.unit_settings.scale_length,'gauge_pairs_checked':len(gauges),'gauge_max_abs_error_m':max((abs(g['inner_gauge_m']-1.676) for g in gauges),default=None),'gauge_samples':gauges,'packed_image_count':sum(bool(im.packed_file) for im in bpy.data.images),'unpacked_file_images':[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'cameras':[o.name for o in s.objects if o.type=='CAMERA'],'collections':[c.name for c in bpy.data.collections],'no_rolling_stock_name_candidates':[o.name for o in s.objects if any(t in o.name.lower() for t in ['locomotive','rolling stock','wagon','bogie'])],'metadata':dict(s.items())}
railcheck=json.loads((P/'geometry/rail_geometry_validation.json').read_text())
q['gauge_pairs_checked']=len(railcheck['gauge_checks']);q['gauge_max_abs_error_m']=railcheck['gauge_max_abs_error_m'];q['gauge_samples']=railcheck['gauge_checks'];q['rail_geometry_validation_file']='geometry/rail_geometry_validation.json'
q['all_route_flange_interior_overlap_m2']=railcheck['all_route_flange_channel_interior_overlap_area_m2']
q['global_rail_objects']=[o.name for o in s.objects if o.name.startswith('Globally unioned railway ')]
q['obsolete_rail_overlay_objects']=[o.name for o in s.objects if o.name.startswith(('Physical rail ','Tapered physical switch blade ','Derived manganese frog nose ','Cast crossing '))]
(P/'qa_validation.json').write_text(json.dumps(q,indent=2,default=str));print(json.dumps({k:v for k,v in q.items() if k not in ['gauge_samples','collections','metadata']},indent=2))
