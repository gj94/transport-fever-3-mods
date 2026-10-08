"""Content-addressed render-only dependencies; independent of checkout location."""
from pathlib import Path
import hashlib

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def collect(renderer, modules, images, bpy_path):
 renderer=Path(renderer).resolve();root=renderer.parent
 helpers={}
 for module in modules:
  file=getattr(module,'__file__',None)
  if not file:continue
  p=Path(file).resolve()
  if p.suffix=='.py' and (p.is_relative_to(root) or p.is_relative_to((root.parent/'vande_bharat_detail_v02').resolve())):
   helpers[p.name]={'sha256':sha(p),'resolved_path':str(p)}
 textures={}
 for image in images:
  if image.source!='FILE' or not image.filepath:continue
  p=Path(bpy_path.abspath(image.filepath)).resolve()
  if p.is_file():textures[image.name]={'sha256':sha(p),'bytes':p.stat().st_size,'resolved_path':str(p)}
 return {'presentation_modules':helpers,'loaded_image_dependencies':textures,'identity_helper_sha256':sha(__file__)}
