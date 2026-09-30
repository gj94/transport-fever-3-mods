"""Independent source + fresh FBX roundtrip verification. Blender 4.3.2."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
vs=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['1A','2A','3A','2S','CC','SL','GS']
TOL=2e-5
summaries=[]
def bbox(obs):
 pts=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
def mat_rows(m):return [[float(x) for x in r] for r in m]
def near(a,b):return max(abs(x-y) for x,y in zip(a,b))<TOL
for v in vs:
 folder=P/v;man=json.loads((folder/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(folder/f'ICF_{v}_master.blend'));root=bpy.data.objects[man['root']];obs=[root]+list(root.children_recursive);obs=[o for o in obs if not o.name.startswith('STUDIO')];bpy.context.view_layer.update()
 errors=[];sourcebounds=bbox(obs);rig={o.name:{'parent':o.parent.name if o.parent else None,'world':mat_rows(o.matrix_world)} for o in obs if o.type=='EMPTY' and not o.name.startswith('BERTH_')};pax=[o for o in obs if o.name.startswith('PAX_')];berths=[o for o in obs if o.name.startswith('BERTH_')]
 if root.type!='EMPTY' or any(abs(root.matrix_world[i][j]-(1 if i==j else 0))>TOL for i in range(4) for j in range(4)):errors.append('Root is not identity EMPTY')
 if len(pax)!=man['physical_capacity'] or len(berths)!=man['physical_berths']:errors.append('Marker count mismatch')
 cushions=[o for o in obs if o.type=='MESH' and o.get('component')=='seat_cushion'];fits=[]
 for o in pax:
  p=o.matrix_world.translation;targets=[]
  for cu in cushions:
   bb=bbox([cu])
   if bb[0][0]<=p.x<=bb[0][1] and bb[1][0]<=p.y<=bb[1][1] and abs(bb[2][1]-p.z-.483)<.002:targets.append(cu.name)
  fits.append({'marker':o.name,'position':list(p),'yaw_degrees':round(math.degrees(o.rotation_euler.z),3),'cushion_candidates':targets})
  if not targets:errors.append('No valid lower cushion at pelvis for '+o.name)
  if o.parent.name!='INTERIOR':errors.append('Unstable PAX parent '+o.name)
  if abs(p.z-man['dimensions_m']['floor_top']-.44+.483)>.002:errors.append('Wrong PAX height '+o.name)
 # Primary shell aperture test against opaque skin and inner sidewall, at every saloon window.
 skin=[o for o in obs if o.type=='MESH' and o.name.startswith(('Lower blue bodyside','Upper blue letterboard','Window zone','Lower interior sidewall','Upper interior sidewall','Interior aperture pier','Wide AC window transom'))]
 verts=[];faces=[]
 for o in skin:
  n=len(verts);verts.extend(o.matrix_world@q.co for q in o.data.vertices);faces.extend(tuple(n+i for i in f.vertices) for f in o.data.polygons)
 tree=BVHTree.FromPolygons(verts,faces);aperture=[]
 for w in man['window_apertures']:
  s=1 if w['y']>0 else -1;p=Vector((w['x'],s*1.8,2.43));hit=tree.ray_cast(p,Vector((0,-s,0)),.32)[0];aperture.append({'x':w['x'],'side':s,'opaque_shell_blocked':hit is not None})
  if hit is not None:errors.append('Opaque wall seals window '+str(w))
 meshes=[o for o in obs if o.type=='MESH'];mats={m.name for o in meshes for m in o.data.materials if m}
 if len(mats)>64:errors.append('Material count over64')
 source={'passed':not errors,'errors':errors,'root_identity_empty':True,'units':'metres X longitudinal Y lateral Z up','mesh_bounds_m':sourcebounds,'materials':len(mats),'pax_count':len(pax),'berth_references':len(berths),'cushion_pelvis_checks':fits,'aperture_ray_checks':aperture,'hierarchy':rig,'scope':'Geometric checks plus root+0.483m sitting-pelvis convention. Full stock character limbs and animation fit remain runtime checks.'}
 (folder/'qa'/'source_validation.json').write_text(json.dumps(source,indent=2));assert not errors,(v,errors)
 (folder/'pax_markers.json').write_text(json.dumps([{'name':o.name,'parent':o.parent.name,'animation':'sitting','local_matrix_rows':mat_rows(o.matrix_local),'world_position_m':list(o.matrix_world.translation),'yaw_degrees':math.degrees(o.rotation_euler.z),'root_to_pelvis_m':.483,'commercial_capacity_is_separate':True} for o in pax],indent=2))
 (folder/'berth_references.json').write_text(json.dumps([{'name':o.name,'world_position_m':list(o.matrix_world.translation),'reference_only':True,'exclude_from_passenger_export':True} for o in berths],indent=2))
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(folder/f'ICF_{v}.fbx'));bpy.context.view_layer.update();allobs=list(bpy.data.objects);errors=[]
 if any(o.type in {'CAMERA','LIGHT'} for o in allobs):errors.append('Render objects leaked')
 if any(o.name.startswith('BERTH_') for o in allobs):errors.append('Berth references leaked')
 for n,spec in rig.items():
  o=bpy.data.objects.get(n)
  if not o:errors.append('Missing marker or pivot '+n);continue
  if (o.parent.name if o.parent else None)!=spec['parent']:errors.append('Parent changed '+n)
  if max(abs(o.matrix_world[i][j]-spec['world'][i][j]) for i in range(4) for j in range(4))>TOL:errors.append('Transform changed '+n)
 freshbounds=bbox(allobs)
 if max(abs(freshbounds[i][j]-sourcebounds[i][j]) for i in range(3) for j in range(2))>TOL:errors.append('FBX mesh envelope changed')
 glass=[]
 for m in bpy.data.materials:
  if m.name.startswith(('GLASS','FROST')):
   bs=m.node_tree.nodes.get('Principled BSDF');alpha=bs.inputs['Alpha'].default_value;trans=bs.inputs['Transmission Weight'].default_value
   glass.append({'name':m.name,'alpha':alpha,'transmission':trans,'fallback_valid':0<alpha<1})
   if not 0<alpha<1:errors.append('Opaque FBX glass '+m.name)
 if len(glass)!=2:errors.append('Glass materials missing')
 if len([o for o in allobs if o.name.startswith('PAX_')])!=man['PAX_marker_count']:errors.append('FBX PAX count mismatch')
 if any(any(abs(s-1)>TOL for s in o.scale) for o in allobs):errors.append('Nonunit object scale in FBX')
 fbx={'passed':not errors,'errors':errors,'fresh_scene_import':True,'mesh_bounds_m':freshbounds,'mesh_count':len([o for o in allobs if o.type=='MESH']),'PAX_count':len([o for o in allobs if o.name.startswith('PAX_')]),'BERTH_count':0,'glass':glass,'verified_rig_nodes':len(rig),'unit_scales':True,'axis_forward':'X','axis_up':'Z','render_objects_excluded':True,'note':'Blender FBX transmission loss is expected. Nonopaque alpha fallback verified; assign target game transparent glass material during conversion.'}
 (folder/'qa'/'fbx_fresh_import.json').write_text(json.dumps(fbx,indent=2));assert not errors,(v,errors)
 summaries.append({'variant':v,'source_passed':source['passed'],'fbx_passed':fbx['passed'],'triangles':man['triangles'],'materials':source['materials'],'pax':source['pax_count'],'berths_source':source['berth_references'],'berths_fbx':0,'opaque_aperture_blockers':sum(w['opaque_shell_blocked'] for w in aperture)})
 print('VALIDATED',v,flush=True)
(P/'qa_summary.json').write_text(json.dumps(summaries,indent=2))
