"""Focused automated validation for the surface library (does not save base scene)."""
import bpy,sys,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
import surface_materials as sm
bpy.ops.wm.read_factory_settings(use_empty=True)
root=bpy.data.objects.new('WAP7_ROOT',None);bpy.context.scene.collection.objects.link(root)
M=sm.setup();checks={};errors=[]
required='white white2 nose cream red roof blackpaint iron cast dust rust steel bright grease rubber ochre copper ceramic glass lens redlens green brass carbon'.split()
checks['role_contract']=all(k in M for k in required)
checks['datablock_namespace']=all(m.name.startswith('SURFV02_') for m in M.values())
checks['all_maps_packed']=all(i.packed_file for i in bpy.data.images if i.source=='FILE')
checks['map_dimensions_positive']=all(min(i.size)>0 for i in bpy.data.images if i.source=='FILE')
checks['no_world_position_nodes']=all(n.type!='NEW_GEOMETRY' for m in M.values() for n in m.node_tree.nodes)
checks['body_metric_coords_root_anchored']=all(n.object==root for key in ['white','white2','nose'] for n in M[key].node_tree.nodes if n.type=='TEX_COORD')
checks['hardware_coords_object_local']=all(n.object is None for key in ['cast','bright','tread','rubber','grease','copper','ochre'] for n in M[key].node_tree.nodes if n.type=='TEX_COORD')
paint='white white2 nose cream red roof blackpaint ochre green'.split()
checks['dielectric_paint']=all(m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value==0 for k,m in M.items() if k in paint)
checks['dielectric_rubber_dust_rust_grease']=all(M[k].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value==0 for k in ['rubber','dust','rust','grease'])
checks['windscreen_film_bounded']=M['windscreen']['maximum_dust_fraction']<=.025
checks['real_glass_transmission']=all(M[k].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value==1 and M[k].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value==1 for k in ['glass','lens'])
checks['scalar_maps_noncolor']=all(n.image.colorspace_settings.name=='Non-Color' for m in M.values() for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and any(x in n.image.name for x in ['roughness','wear','grease']))
checks['bounded_micro_bump']=all(n.inputs['Distance'].default_value<=(.00035 if m==M['cast'] else .00020) for m in M.values() for n in m.node_tree.nodes if n.type=='BUMP')
# Service residue must be on the exterior face only, never both interfaces.
for end in [1,-1]:
    xa,xb=sorted([end*9.430,end*9.436]);y0,y1=(.2,1.15) if end>0 else (-1.15,-.2)
    vs=[(x,y,z) for z in [2.55,3.44] for x,y in [(xa,y0),(xb,y0),(xb,y1),(xa,y1)]]
    fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new('QA_Windshield_'+str(end));me.from_pydata(vs,[],fs);me.update()
    obj=bpy.data.objects.new('QA_Windshield_'+str(end),me);bpy.context.scene.collection.objects.link(obj);me.materials.append(M['glass'])
    sm.assign_windscreen_service(obj,M['windscreen'])
    checks['windscreen_external_face_only_'+str(end)]=sum(f.material_index==1 for f in me.polygons)==1
    checks['windscreen_named_uv_'+str(end)]='SURFV02_WindscreenUV' in me.uv_layers

# Verify that apply does not modify CAB/RG-owned material slots or nodes.
legacy=bpy.data.materials.new('PBR • rubbed black metal');legacy.use_nodes=True
original_color=tuple(legacy.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
protected=[]
for name,coll in [('CABV02_test','CABV02_TEST'),('RGV02_test','RGV02_TEST'),('CabLegacy','CAB_INTERIORS_V02'),('GearLegacy','RUNNING_GEAR_V02'),('V02_RG_test','V02_RG_Engineered running gear'),('MACHV02_test','MACHV02_Machinery room')]:
    c=bpy.data.collections.new(coll);bpy.context.scene.collection.children.link(c)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])
    o=bpy.data.objects.new(name,mesh);c.objects.link(o);mesh.materials.append(legacy);protected.append(o)
shared=bpy.data.objects.new('Unprotected shared-data sibling',protected[0].data);bpy.context.scene.collection.objects.link(shared)
sm.apply({'body_width_factor':1.1})
nose=M['nose'].node_tree.nodes
checks['nose_projection_follows_width_context']=abs(nose['Y atlas offset'].inputs[1].default_value-1.55*1.1)<1e-6 and abs(nose['Y atlas scale in metres'].inputs[1].default_value-3.1*1.1)<1e-6
checks['side_projection_unchanged_by_width_context']=abs(M['white'].node_tree.nodes['X atlas scale in metres'].inputs[1].default_value-19.2)<1e-5
checks['protected_linked_mesh_data_unchanged']=shared.data.materials[0]==legacy
checks['protected_owner_slots_unchanged']=all(o.data.materials[0]==legacy for o in protected)
checks['legacy_material_nodes_not_mutated']=tuple(legacy.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)==original_color
checks['no_duplicate_surface_images']=not any(i.name.startswith(sm.PREFIX) and i.name[-4:]=='.001' for i in bpy.data.images)
checks['namespace_count_no_duplicate_suffixes']=not any(m.name.startswith(sm.PREFIX) and m.name[-4:]=='.001' for m in bpy.data.materials)
for k,v in checks.items():
    if not v:errors.append(k)
report={'version':sm.VERSION,'blender':bpy.app.version_string,'scope':'Focused shader library validation, not a final vehicle/render pass','checks':checks,'passed':not errors,'errors':errors,'roles':{},'image_assets':[]}
for role,m in M.items():
    report['roles'][role]={'material':m.name,'nodes':len(m.node_tree.nodes),'surface_model':m.get('physical_model','Principled BSDF'),'micro_bump_max_m':max([n.inputs['Distance'].default_value*n.inputs['Strength'].default_value for n in m.node_tree.nodes if n.type=='BUMP'] or [0])}
for im in bpy.data.images:
    if im.source=='FILE':report['image_assets'].append({'name':im.name,'width':im.size[0],'height':im.size[1],'colorspace':im.colorspace_settings.name,'packed':bool(im.packed_file)})
p=OUT/'qa'/'surfaces'/'surface_validation.json';p.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if errors:raise AssertionError(errors)
