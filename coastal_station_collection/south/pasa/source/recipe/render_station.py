import os
import bpy,sys,json,hashlib,time,math
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];code=args[0].upper();R=Path(os.environ.get('SOUTH_STATION_OUTPUT_DIR',str(BASE/code.lower())));scene_path=R/f'{code}_station_v01.blend';bpy.ops.wm.open_mainfile(filepath=str(scene_path));s=bpy.context.scene;scenehash=hashlib.sha256(scene_path.read_bytes()).hexdigest();selected=args[1:] or ['01','02','03','04','05'];record=json.loads((R/'RENDER_PROVENANCE.json').read_text()) if (R/'RENDER_PROVENANCE.json').exists() else dict(station=code,views={})
for prefix in selected:
 cam=next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith(prefix+'_'));s.camera=cam;s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
 override=None
 if prefix=='02' and code in ['AMVA','KZTW','ERL']:
  Q=json.loads((R/'QA_BUILD.json').read_text());bb=Q['building'];bx,by=bb['center'];sg=bb['side'];W=bb['width'];target=(bx+(2 if code=='AMVA' else 0),by,2.5 if code=='ERL' else 2.0);pos=(bx+(W*1.4 if code=='AMVA' else -W*.85),by-sg*max(25,W*.75),8 if code!='ERL' else 10);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=42;override={'reason':'Unobstructed oblique view of photographed platform facade, rather than unreferenced rear wall','location':list(cam.location),'target':target,'lens_mm':42}
 if prefix=='02' and code in ['TVCS','TVP']:
  Q=json.loads((R/'QA_BUILD.json').read_text());bb=Q['building'];bx,by=bb['center'];sg=bb['side'];W=bb['width'];target=(bx,bb['platform_y']-sg*.30,2.7);cam.location=(bx+W*.75,bb['platform_y']-sg*(12 if code=='TVCS' else 14),3.4 if code=='TVCS' else 3.8);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34;override={'reason':'Low oblique proof of the photograph-derived platform face beneath its canopy','location':list(cam.location),'target':target,'lens_mm':34}
 if prefix=='04' and code=='DAVM':
  Q=json.loads((R/'QA_BUILD.json').read_text());bb=Q['building'];bx,by=bb['center'];sg=bb['side'];target=(bx+.05,bb['platform_y']+sg*.10,2.60);cam.location=(bx,bb['front_y']-sg*.5,2.35);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24;override={'reason':'Complete photographed ticket hatch, speaking panel and both modest benches fit the interior proof','location':list(cam.location),'target':target,'lens_mm':24}
 if prefix=='04' and code=='KZTW':
  Q=json.loads((R/'QA_BUILD.json').read_text());bb=Q['building'];bx,by=bb['center'];sg=bb['side'];target=(bx,by,1.4);cam.location=(bx-7,bb['front_y']+sg*7,10);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=37
  for co in bpy.data.collections:
   if co.name=='31_ROOFS_REMOVABLE':co.hide_render=True
  override={'reason':'Roof-off review of the three modest reconstructed rooms and their existing furnishings','location':list(cam.location),'target':target,'lens_mm':37,'hidden_render_collections':['31_ROOFS_REMOVABLE']}
 if prefix=='05' and code=='PYD':
  D=json.loads((R/'source/layout.json').read_text());p=D['platforms'][0];xx=min(q[0] for q in p['xy'])+65;w=D['ways'][0];best=min(w['xy'],key=lambda q:abs(q[0]-xx));yy=best[1];target=(xx+7,yy,.25);cam.location=(xx-7,yy-8,6);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=42;override={'reason':'Clear track-detail angle without the near OHE mast','location':list(cam.location),'target':target,'lens_mm':42}
 if prefix=='03':
  D=json.loads((R/'source/layout.json').read_text());Q=json.loads((R/'QA_BUILD.json').read_text())
  def sect(p,x):
   yy=[]
   for a,b in zip(p['xy'],p['xy'][1:]):
    if min(a[0],b[0])<=x<max(a[0],b[0]) and abs(b[0]-a[0])>.00001:yy.append(a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1]))
   return (min(yy),max(yy)) if len(yy)>1 else None
  bx,by=Q['building']['center'];p0=next((p for p in D['platforms'] if p['id']==D['config'].get('primary_platform_id')),min(D['platforms'],key=lambda p:abs(sum(sect(p,bx) or [by,by])/2-by)))
  px=min(x[0] for x in p0['xy'])+10;tx=min(px+200,max(x[0] for x in p0['xy'])-15)
  def roady(x,near):
   ys=[]
   for w in D['ways']:
    for a,b in zip(w['xy'],w['xy'][1:]):
     if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>.00001:ys.append(a[1]+(x-a[0])/(b[0]-a[0])*(b[1]-a[1]))
   return min(ys,key=lambda y:abs(y-near))
  sec=sect(p0,px);mid=sum(sec)/2;ry=roady(px,mid);edge=sec[0] if ry<mid else sec[1];py=edge+(-.75 if ry<mid else .75);sec1=sect(p0,tx);mid1=sum(sec1)/2;ry1=roady(tx,mid1);edge1=sec1[0] if ry1<mid1 else sec1[1];target=(tx,(ry1+edge1)/2,2.1);cam.location=(px,py,3.4);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30;override={'reason':'Railward platform-end viewpoint avoids nameboards, benches and stair undersides; render-only camera transform, source geometry unchanged','location':list(cam.location),'target':target,'lens_mm':30}
 out=R/'renders'/(cam.name+'.png');s.render.filepath=str(out);t=time.time();bpy.ops.render.render(write_still=True);record['views'][out.name]=dict(source_scene_sha256=scenehash,file_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),camera=cam.name,engine=s.render.engine,resolution=[1600,900],seconds=round(time.time()-t,2),camera_override=override);(R/'RENDER_PROVENANCE.json').write_text(json.dumps(record,indent=2));print('RENDERED',code,cam.name,flush=True)
