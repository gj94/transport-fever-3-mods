"""Remove only approximate veranda supports intruding into the entry/ramp clear corridors."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(__file__).resolve().parents[1];code=sys.argv[sys.argv.index('--')+1];R=B/code.lower();src=R/f'{code}_station_v01.blend';h0=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;Q=json.loads((R/'QA_BUILD.json').read_text());b=Q['building'];bx=b['center'][0];rx=bx-b['width']*.35;doorw=2.5 if b['width']>20 else 1.55;removed=[];bounds=[]
for o in list(S.objects):
 if o.name not in ['Verandah column','Verandah column plinth']:continue
 me=o.data;skip=set()
 for j in range(0,len(me.vertices),8):
  ids=list(range(j,min(j+8,len(me.vertices))));cx=sum((o.matrix_world@me.vertices[k].co).x for k in ids)/len(ids)
  if abs(cx-bx)<doorw/2+.40 or abs(cx-rx)<.85:
   skip.update(ids);bounds.extend(o.matrix_world@me.vertices[k].co for k in ids);removed.append({'object':o.name,'component':j//8,'center_x':cx})
 if not skip:continue
 keep=[v for v in me.vertices if v.index not in skip];mapping={v.index:i for i,v in enumerate(keep)};vs=[tuple(v.co) for v in keep];fs=[tuple(mapping[k] for k in p.vertices) for p in me.polygons if all(k in mapping for k in p.vertices)];new=bpy.data.meshes.new(me.name+' clear access');new.from_pydata(vs,[],fs)
 for m in me.materials:new.materials.append(m)
 o.data=new
if code=='TVCS':
 for ob in list(bpy.data.collections['32_ARCHITECTURAL_SIGNS'].objects):
  bounds.extend(ob.matrix_world@Vector(v) for v in ob.bound_box);bpy.data.objects.remove(ob,do_unlink=True)
 sg=b['side'];by=b['platform_y'];p=(bx,by-sg*.18,.95+2.68);sz=(9,.07,.48);vv=[(p[0]+i*sz[0]/2,p[1]+j*sz[1]/2,p[2]+k*sz[2]/2) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];ff=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];me=bpy.data.meshes.new('TVCS readable identity panel mesh');me.from_pydata(vv,[],ff);me.materials.append(bpy.data.materials['yellow']);ob=bpy.data.objects.new('TVCS current platform name panel',me);bpy.data.collections['32_ARCHITECTURAL_SIGNS'].objects.link(ob);bounds.extend(Vector(v) for v in vv)
 ft=bpy.data.curves.new('TVCS current platform identity','FONT');ft.body='THIRUVANANTHAPURAM SOUTH';ft.align_x='CENTER';ft.align_y='CENTER';ft.size=.34;ft.extrude=.004;ft.font=bpy.data.fonts.get('DejaVu Sans Condensed',bpy.data.fonts[0]);ft.materials.append(bpy.data.materials['dark']);ob=bpy.data.objects.new('TVCS current platform identity',ft);bpy.data.collections['32_ARCHITECTURAL_SIGNS'].objects.link(ob);ob.location=(bx,by-sg*.28,.95+2.68);ob.rotation_euler=(math.pi/2,0,0 if sg>0 else math.pi);Q['building']['identity_panel_basis']='Current station name documented in October2024; platform-facing panel placement reconstructed for readable identity.'
assert removed,'Expected an actual conflicting component'
Q['veranda_clearance_repair']={'removed_components':removed,'entry_clear_width_m':doorw+.80,'ramp_clear_width_m':1.70};Q.update(objects=len(S.objects),meshes=sum(o.type=='MESH' for o in S.objects),vertices=sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),polygons=sum(len(o.data.polygons) for o in S.objects if o.type=='MESH'));(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);h1=hashlib.sha256(src.read_bytes()).hexdigest();report={'station':code,'input_source_sha256':h0,'output_source_sha256':h1,'scope':'Veranda column/plinth components inside reconstructed entry/ramp corridors were removed. TVCS additionally replaces its roof-buried generic name strip with a readable current platform-facing identity panel; panel placement is reconstructed.','removed_components':removed};(R/'QA_VERANDA_REPAIR.json').write_text(json.dumps(report,indent=2))
lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)));corners=[Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]];prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());redo=[];ret=[]
for name,r in prov['views'].items():
 cam=S.objects.get(r.get('camera',''));oldloc=cam.location.copy();oldrot=cam.rotation_euler.copy();oldlens=cam.data.lens;ov=r.get('camera_override')
 if ov:cam.location=ov['location'];cam.rotation_euler=(Vector(ov['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=ov['lens_mm']
 pp=[world_to_camera_view(S,cam,p) for p in corners];out=max(v.z for v in pp)<=0 or max(v.x for v in pp)<0 or min(v.x for v in pp)>1 or max(v.y for v in pp)<0 or min(v.y for v in pp)>1;cam.location=oldloc;cam.rotation_euler=oldrot;cam.data.lens=oldlens
 if out:r.update(unchanged_view_verified=True,current_source_scene_sha256=h1,inheritance_basis='Only removed approach-obstructing column components, entirely outside recorded camera frustum');ret.append(name)
 else:redo.append(name[:2])
if code=='TVCS':redo.append('02');ret=[n for n in ret if not n.startswith('02_')]
prov['current_source_scene_sha256']=h1;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(R/'REPAIR_LINEAGE.json').write_text(json.dumps({'station':code,'input_source_sha256':h0,'output_source_sha256':h1,'changed_bounds':[list(lo),list(hi)],'retained_views':ret,'rerender_prefixes':sorted(set(redo))},indent=2))
