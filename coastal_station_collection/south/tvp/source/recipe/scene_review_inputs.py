import os
from pathlib import Path
import sys,json
R=Path(os.environ.get('SOUTH_STATION_OUTPUT_DIR',str(Path(__file__).resolve().parents[1]/sys.argv[1].lower())));q=json.loads((R/'QA_BUILD.json').read_text());b=q['building'];bx,by=b['center'];s=b['side'];z=.95+1.4;front=b['front_y'];back=b['platform_y'];rx=bx-b['width']*.35
r={'central_public_entry':[[bx,front+s*4,z],[bx,back-s,z]],'ramp_to_veranda':[[rx,front+s*4,z],[rx,front+s*1.8,z]],'veranda_to_central_entry':[[rx,front+s*1.8,z],[bx,front+s*1.8,z]]}
for off in [-.35,.35]:
 r['ramp_veranda_lateral_'+str(off)]=[[rx+off,front+s*3.5,z],[rx+off,front+s*1.8,z]]
r['full_ramp_bodypath']=[[rx,front+s*15.3,.76],[rx,front+s*3.7,1.89]]
r['full_ramp_low_clearance']=[[rx,front+s*15.3,.05],[rx,front+s*3.7,1.19]]
if sys.argv[1].upper()=='DAVM':
 # The observed ticket shelter has a closed ticket end wall, not a through-concourse.
 r['central_public_entry']=[[bx,front+s*4,z],[bx,back+s*1.2,z]]
 ax=bx+b['width']/2+.80
 r['external_platform_approach']=[[ax,front+s*3.1,1.4],[ax,back-s*.4,1.4]]
 r['veranda_to_external_approach']=[[bx,front+s*1.5,1.4],[ax,front+s*1.5,1.4]]
if b.get('enclosed_building_modelled') is False:r={}
ap=b.get('sanitary_annex_approach') or q.get('sanitary_annex_approach') or q.get('wc_approach')
if ap:
 a,c=ap['endpoints'];r['sanitary_approach_low']=[[a[0],a[1],a[2]+.30],[c[0],c[1],c[2]+.30]];r['sanitary_approach_waist']=[[a[0],a[1],a[2]+.90],[c[0],c[1],c[2]+.90]];r['sanitary_approach_head']=[[a[0],a[1],a[2]+1.60],[c[0],c[1],c[2]+1.60]]
if b.get('internal_stair'):
 f=b['internal_stair'];a=f['start'];c=f['end'];n=f['steps'];dx=(c[0]-a[0])/n;dy=(c[1]-a[1])/n;rise=f['nominal_rise_m']
 for h in [.30,.90,1.60]:r['internal_stair_body_'+str(h)]=[[a[0]+dx*.5,a[1]+dy*.5,a[2]+rise+h],[c[0]-dx*.5,c[1]-dy*.5,c[2]+h]]
for i,f in enumerate(q['footbridges']):
 fx,y=f['x'],f['y'];deck=f['deck_height'];end=f['landing_end_x'];di=f.get('stair_direction',1);r[f'bridge_{i+1}_upper_mouth']=[[fx+di*3.0,y,deck+1.15],[fx,y,deck+1.15]];r[f'bridge_{i+1}_toe']=[[end+di*1.0,y,.95+1.5],[end-di*.4,y,.95+1.5]]
(R/'QA_CIRCULATION_RAYS.json').write_text(json.dumps(r,indent=2));print(str(R/'QA_CIRCULATION_RAYS.json'))
