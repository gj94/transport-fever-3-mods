"""BLENDER --python this.py -- /absolute/original_renderer.py VIEW_ARGS..."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import checkpoint_render
import render_dependency_identity
args=sys.argv[sys.argv.index('--')+1:];renderer=Path(args[0]);sys.argv=sys.argv[:sys.argv.index('--')+1]+args[1:]
source=renderer.read_text();needle='bpy.ops.render.render(write_still=True)';assert source.count(needle)==1
identity={'renderer_path':str(renderer),'renderer_sha256':checkpoint_render.sha(renderer)}
records=[]
def run_checkpoint():
 master=Path(bpy.data.filepath);identity['source_sha256']=checkpoint_render.sha(master)
 # Hash renderer sibling code and all directly imported presentation modules.
 identity.update(render_dependency_identity.collect(renderer, list(sys.modules.values()), bpy.data.images, bpy.path))
 identity['wrapper_script_sha256']=checkpoint_render.sha(__file__)
 record=checkpoint_render.render(bpy.context.scene,identity);records.append(record)
ns={'__file__':str(renderer),'__name__':'__main__','_checkpoint_render':run_checkpoint,'_checkpoint_records':records}
source=source.replace(needle,'_checkpoint_render()')
for variable in ['metadata','report']:
 source=source.replace('json.dumps('+variable+',','json.dumps(dict('+variable+', sampling_workflow=_checkpoint_records[-1]),')
exec(compile(source,str(renderer),'exec'),ns)
print('CHECKPOINT_RENDERER_COMPLETE',json.dumps([r['fingerprint'] for r in records]),flush=True)
