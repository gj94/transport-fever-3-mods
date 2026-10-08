"""Small reconstructed sanitary-block approach link; no unrelated scene edits."""
import bpy,sys,json,hashlib,os
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];code=args[0] if args else 'AMVA';R=Path(os.environ.get('SOUTH_STATION_OUTPUT_DIR',str(BASE/code.lower())));src=R/f'{code}_station_v01.blend';oldsha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;Q=json.loads((R/'QA_BUILD.json').read_text());b=Q['building'];bx,by=b['center'];side=b['side'];x=bx+b['width']/2+3-.74;ya=by-side*1.0;yb=b['platform_y']-side*.60;za=1.04;zb=.964;w=1.10;bottom=-.20
if code not in ['AMVA','DAVM']:x=bx+b['width']/2+5;ya=by-side*1.95;yb=b['platform_y']-side*.60;za=1.005;zb=.964;w=1.60
if code=='DAVM':x=bx+b['width']/2+.80;ya=b['front_y']+side*3.6;yb=b['platform_y']-side*.60;za=1.005;zb=.964;w=1.60
sys.path.insert(0,str(BASE/'scripts'));from access_geometry import approach_end,link_clearance
D=json.loads((R/'source/layout.json').read_text());yb=approach_end(D,x,by,side)[0];clearance=link_clearance(D,x,ya,yb,w)
v=[(x-w/2,ya,bottom),(x+w/2,ya,bottom),(x+w/2,yb,bottom),(x-w/2,yb,bottom),(x-w/2,ya,za),(x+w/2,ya,za),(x+w/2,yb,zb),(x-w/2,yb,zb)];f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
me=bpy.data.meshes.new(code+' reconstructed access link mesh');me.from_pydata(v,[],f);me.materials.append(bpy.data.materials['concrete']);o=bpy.data.objects.new(code+' reconstructed approach link',me);bpy.data.collections['35_BUILDING_ACCESS'].objects.link(o);o['basis']='Reconstructed short continuous access path joining observed detached sanitary block to model platform; not surveyed.'
extra_bounds=[]
internal_stair_checks=[]
if code=='ERL':
 # Equalize the first internal rise to the actual terrazzo floor, without changing its footprint.
 low=.95+.1025;upper=.95+3.60;steps=24;run=.30;st0=.80;sx=b['width']*.38;front=b['front_y'];rise=(upper-low)/steps
 ob=S.objects.get('Internal upper-floor stair')
 if ob:
  extra_bounds.extend(tuple(ob.matrix_world@Vector(p)) for p in ob.bound_box)
  for ve in ob.data.vertices:
   j=ve.index//8;ve.co.z+=.1025*(1-(j+1)/steps)
  ob.data.update();extra_bounds.extend(tuple(ob.matrix_world@Vector(p)) for p in ob.bound_box)
 ob=S.objects.get('Internal stair rail')
 if ob:
  for ve in ob.data.vertices:
   ly=(front-ve.co.y)/side;t=max(0,min(1,(ly-st0)/(steps*run)));ve.co.z+=.1025*(1-t)
  ob.data.update()
 Q['building']['internal_stair']={'start':[bx+sx,front-side*st0,low],'end':[bx+sx,front-side*(st0+steps*run),upper],'steps':steps,'nominal_rise_m':rise,'going_m':run,'clear_width_m':2.10}
if code=='PASA':
 H=b['depth'];W=b['width'];front=b['front_y'];eave=.95+3.50;ridge=eave+.72;zf=eave+.72*.45/(H/2+.45);zr=eave+.72*.4/(H/2+.4)
 for gx in [-W/2,W/2]:
  prof=[(0,.95+3.45),(H,.95+3.45),(H,zr),(H/2,ridge),(0,zf)];vv=[(bx+gx+dx,front-side*yy,zz) for dx in [-.10,.10] for yy,zz in prof];ff=[(4,3,2,1,0),(5,6,7,8,9),*[(j,(j+1)%5,(j+1)%5+5,j+5) for j in range(5)]];me=bpy.data.meshes.new('PASA end gable repair mesh');me.from_pydata(vv,[],ff);me.materials.append(bpy.data.materials['cream']);ob=bpy.data.objects.new('PASA roof-end gable infill',me);bpy.data.collections['30_BUILDING_ENVELOPE_PHOTO_INFORMED'].objects.link(ob);extra_bounds.extend(vv)
if code=='DAVM':
 for ob in list(S.objects):
  if ob.name.startswith('Portal-clear red skirting'):extra_bounds.extend(tuple(ob.matrix_world@Vector(p)) for p in ob.bound_box);bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();probes=[]
for i in range(11):
 t=max(.001,min(.999,i/10)) if code=='DAVM' else i/10;y=ya+(yb-ya)*t;hit=S.ray_cast(dep,Vector((x,y,1.20)),Vector((0,0,-1)),distance=2);assert hit[0];z=float(hit[1].z);assert .96<=z<=1.05,(y,z);probes.append({'x':x,'y':y,'floor_z':z,'object':hit[4].name})
if code=='ERL':
 for j in range(24):
  yy=front-side*(st0+(j+.5)*run);hit=S.ray_cast(dep,Vector((bx+sx,yy,upper+.2)),Vector((0,0,-1)),distance=4);expected=low+(j+1)*rise;assert hit[0] and abs(hit[1].z-expected)<.015,(j,hit,expected);internal_stair_checks.append({'step':j+1,'actual_floor_z':float(hit[1].z),'expected_floor_z':expected})
Q.update(objects=len(S.objects),meshes=sum(o.type=='MESH' for o in S.objects),vertices=sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),polygons=sum(len(o.data.polygons) for o in S.objects if o.type=='MESH'));Q['wc_approach' if code=='AMVA' else 'external_platform_approach' if code=='DAVM' else 'sanitary_annex_approach']={'center_x':x,'width_m':w,'endpoints':[[x,ya,za],[x,yb,zb]],'basis':'Reconstructed continuous short sanitary-block/platform link'};(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));S['wc_access_repair_input_sha256']=oldsha;bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);newsha=hashlib.sha256(src.read_bytes()).hexdigest()
(R/'QA_ACCESS_REPAIR.json').write_text(json.dumps({'station':code,'input_source_sha256':oldsha,'output_source_sha256':newsha,'scope':'Short reconstructed continuous access link. PASA additionally closes the two pitched-roof end seams; DAVM removes unsupported generic red threshold skirting and receives the already-requested wider interior proof camera.','foot_probes':probes,'source_layout_clearance':clearance,'internal_stair_checks':internal_stair_checks,'status':'Eleven actual floor support rays passed'},indent=2))
# Conservative frame inheritance based on the whole added element's camera bounds.
allbounds=v+extra_bounds;lo=Vector(tuple(min(p[i] for p in allbounds) for i in range(3)));hi=Vector(tuple(max(p[i] for p in allbounds) for i in range(3)));corners=[Vector((a,b,c)) for a in [lo.x,hi.x] for b in [lo.y,hi.y] for c in [lo.z,hi.z]];prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());rerender=[];retained=[]
for name,r in prov['views'].items():
 cam=S.objects.get(r.get('camera',''))
 if cam is None:rerender.append(name[:2]);continue
 oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldlens=cam.data.lens;ov=r.get('camera_override')
 if ov:cam.location=ov['location'];cam.rotation_euler=(Vector(ov['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=ov['lens_mm']
 vv=[world_to_camera_view(S,cam,p) for p in corners];out=(max(p.z for p in vv)<=0 or max(p.x for p in vv)<0 or min(p.x for p in vv)>1 or max(p.y for p in vv)<0 or min(p.y for p in vv)>1);cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.lens=oldlens
 if out:
  r.setdefault('inheritance_chain',[]).append({'from_scene_sha256':oldsha,'to_scene_sha256':newsha,'previous_basis':r.get('inheritance_basis'),'basis':'Only added approach link is outside recorded camera frustum'});r.update(unchanged_view_verified=True,current_source_scene_sha256=newsha,inheritance_basis='Only added WC approach link, entirely outside recorded camera frustum');retained.append(name)
 else:rerender.append(name[:2])
if code=='DAVM':
 # The interior proof camera is also explicitly widened to include the complete ticket hatch.
 rerender.append('04');retained=[n for n in retained if not n.startswith('04_')]
histpath=R/'REPAIR_HISTORY.json';history=json.loads(histpath.read_text()) if histpath.exists() else [];previous=R/'REPAIR_LINEAGE.json'
if previous.exists():history.append(json.loads(previous.read_text()))
histpath.write_text(json.dumps(history,indent=2))
prov['current_source_scene_sha256']=newsha;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(R/'REPAIR_LINEAGE.json').write_text(json.dumps({'station':code,'input_source_sha256':oldsha,'output_source_sha256':newsha,'changed_bounds':[list(lo),list(hi)],'retained_views':retained,'rerender_prefixes':sorted(set(rerender))},indent=2))
