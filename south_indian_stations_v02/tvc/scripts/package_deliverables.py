"""Package verified scene/source, review gallery and exchange parts separately."""
from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parents[1];P=R/'packages';P.mkdir(exist_ok=True)
a=json.loads((R/'FINAL_FILE_ALLOWLIST.json').read_text());files=a['files'];source=[p for p in files if not p.startswith(('renders/','exchange/')) and p!='TVC_v02_review_contact_sheet.png'];review=[p for p in files if p.startswith('renders/')]+['TVC_v02_review_contact_sheet.png','GALLERY.md','MODELLING_PLAN.md','TVC_track_coverage_plan.pdf','TRACK_REGISTER.csv'];exchange=[str(p.relative_to(R)) for p in (R/'exchange').glob('*') if p.is_file()]
packages=[]
for name,items in [('TVC_v02_editable_source.zip',source),('TVC_v02_review_gallery.zip',review),('TVC_v02_exchange_glb.zip',exchange+['EXCHANGE_QA.json','EXCHANGE_REIMPORT_QA.json','README.md','MODELLING_PLAN.md','FINAL_QA.md'])]:
 if not items:continue
 out=P/name;manifest=[]
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in sorted(set(items)):
   path=R/f;z.write(path,'TVC_v02/'+f);manifest.append({'path':f,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  z.writestr('TVC_v02/ARCHIVE_MANIFEST_'+name.replace('.zip','.json'),json.dumps(manifest,indent=2))
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 packages.append({'file':name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(manifest)})
(P/'MANIFEST.json').write_text(json.dumps(packages,indent=2));print(json.dumps(packages,indent=2))
