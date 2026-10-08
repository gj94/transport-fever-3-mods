"""Camera-local Blender Eevee proof, excludes documented distant collections only.
Retains furnished rooms, walls/ceilings, relevant lighting, heritage and first platform.
Use after saving authoritative blend. Never saves presentation visibility into source.
"""
import bpy,json,sys,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['05_Waiting_lounge']
name=args[0];S.camera=bpy.data.objects[name]
# Keep all station buildings and interior fittings; remove distant mesh-dense yard,
# rolling-ground utilities and remote urban context (not present in interior view).
hidden=[]
for c in bpy.data.collections:
 if c.name.startswith(('10_','10B','11_','11B','15_','16_','16B','17_','20_')):
  c.hide_render=True;hidden.append(c.name)
# Far platform slabs/roof trusses remain nearby lighting context. All internal walls stay.
S.render.engine='BLENDER_EEVEE_NEXT';S.render.threads_mode='FIXED';S.render.threads=4
S.eevee.taa_render_samples=64
S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.exposure=.35
S.render.filepath=str(R/'renders'/f'{name}_local_eevee.png')
print('LOCAL_VIEW_RENDER',name,'excluded',hidden,flush=True)
bpy.ops.render.render(write_still=True)
record={'camera':name,'source_blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'engine':'BLENDER_EEVEE_NEXT','resolution':[1200,800],'presentation_only_hidden_collections':hidden,'note':'Authoritative saved blend still contains every collection. Camera-local preview excludes distant yard/urban geometry.'}
(R/'renders'/f'{name}_local_eevee.json').write_text(json.dumps(record,indent=2))
