"""Open copied sources from an independent directory and resolve relative libraries."""
import bpy,sys,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];folder=Path(args[0]).resolve() if args else OUT;results=[]
for file in sorted((folder/'cars').glob('*.blend'))+sorted((folder/'assemblies').glob('*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(file));missing=[]
 for lib in bpy.data.libraries:
  resolved=Path(bpy.path.abspath(lib.filepath));
  if not resolved.is_file():missing.append({'library':lib.filepath,'reason':'missing file'})
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file():missing.append({'image':im.name,'reason':'missing unpacked pixels'})
 for font in bpy.data.fonts:
  if font.filepath and font.filepath!='<builtin>' and not getattr(font,'packed_file',None) and not Path(bpy.path.abspath(font.filepath)).is_file():missing.append({'font':font.name,'reason':'missing unpacked font'})
 results.append({'file':str(file.relative_to(folder)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'libraries':[lib.filepath for lib in bpy.data.libraries],'missing_dependencies':missing,'objects':len(bpy.data.objects)})
 print('PORTABLE',file.name,'PASS' if not missing else 'FAIL',flush=True)
(OUT/'qa/portability.json').write_text(json.dumps({'fresh_directory_test':folder!=OUT,'files':results,'scope':'Only model source folder copied; image-free procedural materials. Rendering environment is separately referenced by render scripts.'},indent=2));assert all(not r['missing_dependencies'] for r in results)
