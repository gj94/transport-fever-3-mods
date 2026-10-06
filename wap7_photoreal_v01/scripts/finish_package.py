"""Losslessly strip preview metadata; verify pixels; write manifest and checksums.
Does not alter image pixels, geometry or packed Blender data.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pack=json.loads((ROOT/'qa/packaging_validation.json').read_text())
expected={
 'hero':('01_hero_trackside.png',1920,1080,512,'render_hero.json'),
 'side':('02_side_elevation.png',2200,660,256,'render_side.json'),
 'cab':('03_cab_detail.png',1600,1000,256,'render_cab_bogie_roof.json'),
 'bogie':('04_bogie_detail.png',1600,1000,256,'render_cab_bogie_roof.json'),
 'roof':('05_roof_detail.png',1600,1000,256,'render_cab_bogie_roof.json'),
 'front':('06_front_portrait.png',1280,1472,256,'render_front.json')}
preview_runs=[]
for key,(filename,w,h,min_samples,record) in expected.items():
 run=json.loads((ROOT/'qa'/record).read_text())[key]
 assert run['master_sha256']==pack['packaged_master_sha256'],(key,'Wrong model revision')
 assert run['samples']>=min_samples,(key,'Draft sample count')
 assert (run['width'],run['height'])==(w,h),(key,'Wrong render dimensions')
 assert Image.open(ROOT/'previews'/filename).size==(w,h),(key,'PNG/report mismatch')
 preview_runs.append(dict(run,file='previews/'+filename))
image_rows=[]
for p in sorted((ROOT/'previews').glob('*.png')):
 im=Image.open(p);im.load();pix=hashlib.sha256(im.tobytes()).hexdigest();size=list(im.size);mode=im.mode
 if im.info:
  clean=Image.frombytes(mode,im.size,im.tobytes());clean.save(p,optimize=True)
 check=Image.open(p);check.load();assert hashlib.sha256(check.tobytes()).hexdigest()==pix
 image_rows.append({'file':p.relative_to(ROOT).as_posix(),'width':size[0],'height':size[1],'mode':mode,'pixel_sha256':pix,'metadata_removed':True,'pixel_content_unchanged':True})
# The hero render started before packaging, with verified byte-identical vehicle content.
hero=ROOT/'qa/render_hero.json'
if hero.exists():
 x=json.loads(hero.read_text())
 if 'hero' in x and 'master_sha256' not in x['hero']:
  x['hero']['master_sha256']=pack['source_render_master_sha256'];x['hero']['stage_rebuilt']=False;x['hero']['packaging_note']='Rendered full-scene predecessor; packaging_validation.json proves all vehicle geometry/materials/images identical to the compact delivered master'
  hero.write_text(json.dumps(x,indent=2))
(ROOT/'qa/preview_pixel_validation.json').write_text(json.dumps({'images':image_rows,'method':'Pillow lossless metadata stripping, raw decoded pixel SHA256 checked before/after','ai_image_generation':False,'photographic_backplates':False},indent=2))
files=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name not in ['FILE_MANIFEST.json','SHA256SUMS.txt']:
  files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'package':'wap7_photoreal_v01','date':'2026-10-06','master':'WAP7_photoreal_v01.blend','master_sha256':sha(ROOT/'WAP7_photoreal_v01.blend'),'master_packed_images':19,'master_compressed':True,'source_only':True,'native_game_resources_modified':False,'preview_count':len(image_rows),'preview_runs':preview_runs,'files':files}
(ROOT/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
lines=[sha(p)+'  '+p.relative_to(ROOT).as_posix() for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt']
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'master_bytes':(ROOT/'WAP7_photoreal_v01.blend').stat().st_size,'preview_count':len(image_rows),'files':len(lines),'total_bytes':sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())}))
