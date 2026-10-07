"""Read-only Blender authoring QA; use on each completed master."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=next(o for o in bpy.data.objects if o.name.endswith('_ROOT') and o.name.startswith('ICF_'))
asset=[root]+list(root.children_recursive);meshes=[o for o in asset if o.type=='MESH'];variant=root['variant'];folder=Path(bpy.data.filepath).parent
bad=[];inward=[];closed=0;open_mesh=[];degenerate=[];finite=True
for ob in meshes:
 if any(not all(math.isfinite(c) for c in v.co) for v in ob.data.vertices):finite=False;bad.append(ob.name)
 bm=bmesh.new();bm.from_mesh(ob.data)
 if bm.edges and all(e.is_manifold for e in bm.edges):
  closed+=1
  if bm.calc_volume(signed=True)<-1e-10:inward.append(ob.name)
 else:open_mesh.append(ob.name)
 tiny=sum(f.calc_area()<1e-12 for f in bm.faces)
 if tiny:degenerate.append({'name':ob.name,'faces':tiny})
 bm.free()
points=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
bounds=[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)]
parents={o.name:o.parent.name if o.parent else None for o in asset if o.type=='EMPTY'}
pax=[o for o in asset if o.name.startswith('PAX_SEATED_')];berths=[o for o in asset if o.name.startswith('BERTH_')]
anchors=[bpy.data.objects['COUPLING_'+s].matrix_world.translation for s in ['FRONT','REAR']]
pivots=[bpy.data.objects['BOGIE_'+str(i)+'_PIVOT'].matrix_world.translation for i in [1,2]]
checks={'finite_geometry':finite,'pax_count':len(pax)==root['physical_capacity'],'berth_count':len(berths)==root['physical_berths'],'buffer_anchor_span':abs((anchors[0]-anchors[1]).length-22.297)<1e-5,'bogie_pivot_span':abs((pivots[0]-pivots[1]).length-14.783)<1e-5,'bounds_reasonable':bounds[0][0]>-11.16 and bounds[0][1]<11.16 and bounds[1][0]>-1.80 and bounds[1][1]<1.80 and bounds[2][0]>-.06 and bounds[2][1]<4.15,'no_inward_closed_meshes':not inward,'no_zero_area_faces':not degenerate,'no_studio_in_asset':not any(o.name.startswith('STUDIO') for o in asset)}
report={'variant':variant,'checks':checks,'passed':all(checks.values()),'meshes':len(meshes),'closed_meshes':closed,'open_surface_meshes':len(open_mesh),'inward_meshes':inward,'degenerate_faces':degenerate,'bounds_m':bounds,'seated_roots':len(pax),'berth_markers':len(berths),'open_surface_note':'Window surrounds, cloth, thin sheet surfaces and mirrored fittings can be intentionally open; an open surface alone is not a failure.','checked_blend':Path(bpy.data.filepath).name}
(folder/'qa'/'geometry_checks.json').write_text(json.dumps(report,indent=2))
print('DETAIL_GEOMETRY_QA',json.dumps(report),flush=True)
