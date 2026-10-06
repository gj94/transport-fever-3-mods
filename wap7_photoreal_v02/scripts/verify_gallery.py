"""Verify the ten delivered PNG/provenance pairs against the immutable master.
Run with ordinary Python: python scripts/verify_gallery.py [PACKAGE_DIRECTORY].
Works before or after metadata-only PNG cleanup when the primary image hash in
the associated provenance has been updated and the raw render hash retained.
This checks consistency; visual inspection is separately documented.
"""
import hashlib,json,struct,sys
from pathlib import Path
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
EXPECTED='25aa1f264f7dbab9f25e9e2fe27ff2f2e9d6b8ab513133d374717fcff0e24930'
ITEMS=[
 ('Exterior hero','previews/outdoor_hero.png','qa/outdoor_hero.json','scripts/render_outdoor.py'),
 ('Cab Panel A','previews/cab/panel_A.png','previews/cab/panel_A.provenance.json','scripts/render_cab_gallery_uniform.py'),
 ('Coupler and connections','previews/probe_coupler_top.png','qa/probe_coupler_top.json','scripts/render_probe.py'),
 ('Machinery corridor','previews/machinery_gallery/machinery_through_door.png','previews/machinery_gallery/machinery_through_door.json','scripts/render_machinery_gallery.py'),
 ('Wheel and entry detail','previews/details/wheel.png','previews/details/wheel.json','scripts/render_detail_gallery.py'),
 ('Pantograph','previews/probe_pantograph.png','qa/probe_pantograph.json','scripts/render_probe.py'),
 ('Cab overview','previews/cab/overview_A.png','previews/cab/overview_A.provenance.json','scripts/render_cab_gallery.py'),
 ('Underfloor equipment','previews/details/underfloor.png','previews/details/underfloor.json','scripts/render_detail_gallery.py'),
 ('Machinery cutaway','previews/machinery_gallery/machinery_cutaway.png','previews/machinery_gallery/machinery_cutaway.json','scripts/render_machinery_gallery.py'),
 ('Technical side elevation','previews/probe_side.png','qa/probe_side.json','scripts/render_probe.py'),
]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
master=P/'WAP7_detail_v02.blend';assert sha(master)==EXPECTED,'Unexpected model bytes'
results=[]
for label,image,provenance,driver in ITEMS:
 im=P/image;rp=P/provenance
 assert im.is_file() and rp.is_file(),label+' is incomplete'
 data=im.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and data[12:16]==b'IHDR',image
 width,height=struct.unpack('>II',data[16:24]);j=json.loads(rp.read_text())
 assert j['master_sha256']==EXPECTED,label+' uses another master'
 assert j.get('image_sha256',j.get('png_sha256'))==sha(im),label+' image hash mismatch'
 assert j.get('master_file_unchanged',j.get('master_bytes_unchanged',False)),label+' lacks unchanged-master proof'
 assert j.get('status','rendered')=='rendered' and not j.get('stage_only',False),label+' is not a finished render'
 settings=j.get('presentation',{}).get('render',j.get('render_settings',{}))
 assert not j.get('denoised',settings.get('denoising',False)),label+' has unexpected denoising'
 assert width==j.get('width',settings.get('width',width)) and height==j.get('height',settings.get('height',height)),label+' dimension mismatch'
 assert j.get('source_geometry_unchanged',True) and not j.get('mesh_data_edited',False),label+' reports source edits'
 recorded=j.get('render_driver_sha256',j.get('script_sha256'))
 if recorded:assert sha(P/driver)==recorded,label+' producer mismatch'
 for path,digest in j.get('render_source_sha256',{}).items():assert sha(P/path)==digest,label+' render dependency mismatch: '+path
 samples=j.get('samples',settings.get('maximum_samples',settings.get('samples',settings.get('maximum_samples_per_pixel'))))
 results.append({'view':label,'image':image,'provenance':provenance,'image_sha256':sha(im),'width':width,'height':height,'maximum_samples':samples,'master_sha256':EXPECTED,'producer':driver,'passed':True})
report={'master_sha256':EXPECTED,'image_count':len(results),'all_pass':all(r['passed'] for r in results),'checks':results,'scope':'File, source, producer, dimensions and completed-render consistency only; pixel review is recorded in VISUAL_QA.md'}
(P/'qa/final_gallery_validation.json').write_text(json.dumps(report,indent=2))
print('GALLERY_CONSISTENCY_PASS',len(results),EXPECTED)
