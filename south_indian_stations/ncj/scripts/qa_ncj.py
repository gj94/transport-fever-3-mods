"""Reopen native file, inspect dependencies, geometry, gauge and GLB header."""
import bpy,json,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_2010_station.blend'))
s=bpy.context.scene
result={'reopen_blend':True,'blender':bpy.app.version_string,'scene_units':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'objects':len(s.objects),'mesh_objects':sum(o.type=='MESH' for o in s.objects),'materials':len(bpy.data.materials),'packed_fonts':[],'external_unpacked_images':[],'nonfinite_vertices':0,'render_samples':s.cycles.samples,'render_threads':s.render.threads,'denoising':s.cycles.use_denoising}
for f in bpy.data.fonts:
 if f.filepath!='<builtin>':result['packed_fonts'].append({'name':f.name,'packed':bool(f.packed_file)})
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:result['external_unpacked_images'].append(im.filepath)
for o in s.objects:
 if o.type=='MESH':
  for v in o.data.vertices:
   if not all(math.isfinite(a) for a in v.co):result['nonfinite_vertices']+=1
rails=sorted([o for o in s.objects if o.name.startswith('Rail head')],key=lambda o:o.location.y)
result['gauge_inner_faces_m']=round(rails[1].location.y-rails[0].location.y-(rails[0].dimensions.y+rails[1].dimensions.y)/2,6)
rail_top=rails[0].location.z+rails[0].dimensions.z/2
p=bpy.data.objects['Red oxide platform surfacing'];platform_top=p.location.z+p.dimensions.z/2
result['platform_top_above_rail_m']=round(platform_top-rail_top,6)
result['scope']='2010 facade photo reconstruction; rear/platform/context not a surveyed station layout'
f=R/'exports/NCJ_2010_station.glb'
with f.open('rb') as h:magic,version,length=struct.unpack('<4sII',h.read(12))
result['glb']={'magic':magic.decode(),'version':version,'header_size_matches':length==f.stat().st_size,'size_bytes':length}
result['checks_pass']=result['nonfinite_vertices']==0 and not result['external_unpacked_images'] and all(x['packed'] for x in result['packed_fonts']) and result['glb']['header_size_matches'] and abs(result['gauge_inner_faces_m']-1.676)<.001 and abs(result['platform_top_above_rail_m']-.760)<.001
(R/'QA.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
