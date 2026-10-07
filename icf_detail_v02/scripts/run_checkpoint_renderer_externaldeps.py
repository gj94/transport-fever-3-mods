"""BLENDER --python this.py -- /absolute/original_renderer.py VIEW_ARGS..."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import checkpoint_render
args=sys.argv[sys.argv.index('--')+1:];renderer=Path(args[0]);sys.argv=sys.argv[:sys.argv.index('--')+1]+args[1:]
source=renderer.read_text();needle='bpy.ops.render.render(write_still=True)';assert source.count(needle)==1
identity={'renderer_path':str(renderer),'renderer_sha256':checkpoint_render.sha(renderer)}
records=[]
def run_checkpoint():
 master=Path(bpy.data.filepath);identity['source_sha256']=checkpoint_render.sha(master)
 # Hash renderer sibling code and all directly imported presentation modules.
 identity['presentation_modules']={str(Path(m.__file__)):checkpoint_render.sha(m.__file__) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(getattr(m,'__file__','')).resolve().is_relative_to(Path(__file__).resolve().parent) and str(getattr(m,'__file__','')).endswith('.py')}
 # Bind external outdoor dependencies before selecting any reusable sample cache.
 environment=ns.get('environment_report') or {}
 deps=environment.get('external_dependency_sha256',{})
 if deps:
  root=renderer.resolve().parents[2]
  identity['external_presentation_dependencies']={name:checkpoint_render.sha(root/name) for name in deps}
  assert identity['external_presentation_dependencies']==deps,'Presentation dependency changed while preparing render'
 record=checkpoint_render.render(bpy.context.scene,identity);records.append(record)
ns={'__file__':str(renderer),'__name__':'__main__','_checkpoint_render':run_checkpoint,'_checkpoint_records':records}
source=source.replace(needle,'_checkpoint_render()')
for variable in ['metadata','report']:
 source=source.replace('json.dumps('+variable+',','json.dumps(dict('+variable+', sampling_workflow=_checkpoint_records[-1]),')
exec(compile(source,str(renderer),'exec'),ns)
print('CHECKPOINT_RENDERER_COMPLETE',json.dumps([r['fingerprint'] for r in records]),flush=True)
