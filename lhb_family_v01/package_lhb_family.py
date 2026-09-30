"""Create original-render contact sheets, summary manifest and package checksums."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,sys
P=Path(__file__).resolve().parent
classes=['1A','2A','3A','2S','CC','SL','GS'];qa=json.loads((P/'qa/all_variants_validation.json').read_text());rows=[]
for k in classes:
 r=json.loads((P/'models'/('LHB_'+k+'_manifest.json')).read_text());r['qa_pass']=qa[k]['source']['pass'] and qa[k]['fresh_fbx']['pass'] and qa[k]['bounds_match'];r['evaluated_triangles']=qa[k]['source']['evaluated_triangles'];r['used_materials']=qa[k]['source']['materials'];r['actual_mesh_bounds_m']=qa[k]['source']['actual_mesh_bounds_m'];rows.append(r)
manifest={'name':'LHB coach family v01','baseline_repository_commit':'baf66cb5c267125ce2c6e82bf03c0fc6986bf786','blender':'4.3.2','native_TF3_conversion':False,'runtime_tested':False,'original_geometry':True,'variants':rows}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
(P/'dimensions.json').write_text(json.dumps({'units':'metres','axes':{'X':'longitudinal forward','Y':'lateral','Z':'up'},'railhead_z':0,'body_length':23.54,'body_width':3.24,'roof_crown':4.039,'bogie_centres':14.9,'bogie_wheelbase':2.56,'new_wheel_tread_diameter':.915,'gauge':1.676,'floor':1.303,'cushion_top_z':1.840,'PAX_character_root_z':1.357,'coupling_front':[12,0,1.105],'coupling_rear':[-12,0,1.105],'coupling_span':24,'actual_evaluated_bounds_by_variant':{r['variant']:r['actual_mesh_bounds_m'] for r in rows}},indent=2))
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(fontpath,25);small=ImageFont.truetype(fontpath,22)
for mode in ['exterior','layout_cutaway','interior']:
 if not all((P/'renders'/('LHB_'+k+'_'+mode+'.png')).exists() for k in classes):
  if '--preview-only' in sys.argv:continue
  raise RuntimeError('Missing render set: '+mode)
 W=1600;cw=800;im=Image.new('RGB',(W,4*490+95),(22,29,38));d=ImageDraw.Draw(im);d.text((28,18),'LHB CLASS FAMILY | '+mode.replace('_',' ').upper(),font=font,fill='white');d.text((28,57),'Original source-model review | 24 m coupling span | Blender QA, no native TF3 test',font=small,fill=(177,191,208))
 for j,r in enumerate(rows):
  k=r['variant'];img=Image.open(P/'renders'/('LHB_'+k+'_'+mode+'.png')).convert('RGB');img.thumbnail((cw,450));x=(j%2)*cw;y=95+(j//2)*490;im.paste(img,(x,y));label=k+'  |  '+str(r['physical_capacity'])+' '+r['capacity_type']+'  |  '+r['prototype_code'];d.text((x+20,y+454),label,font=small,fill='white')
 im.save(P/'renders'/('LHB_family_'+mode+'_contact_sheet.jpg'),quality=91)
if '--preview-only' in sys.argv:sys.exit(0)
files=sorted(p for p in P.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and p.suffix not in ['.log','.blend1','.pyc'] and '__pycache__' not in p.parts)
(P/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(P).as_posix() for p in files)+'\n')
print('Package manifest and contact sheets generated',len(files))
