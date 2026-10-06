import bpy,sys,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'components'))
import surface_running_gear as G
M=G.setup();checks={}
checks['optional_three_role_contract']=set(M)=={'gear_frame','gear_cast','gear_wheelweb'}
checks['no_scene_assignment']=not any(o.type=='MESH' and any(m in M.values() for m in o.data.materials) for o in bpy.data.objects)
checks['only_pure_metal_or_dielectric_endpoints']=all(n.inputs['Metallic'].default_value in (0,1) for m in M.values() for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
checks['no_world_position_textures']=all(not n.outputs['Position'].is_linked for m in M.values() for n in m.node_tree.nodes if n.type=='NEW_GEOMETRY')
checks['no_automatic_pointiness_wear']=all(not n.outputs['Pointiness'].is_linked for m in M.values() for n in m.node_tree.nodes if n.type=='NEW_GEOMETRY')
checks['hardware_metric_local_coordinates']=all(n.object is None for m in M.values() for n in m.node_tree.nodes if n.type=='TEX_COORD')
checks['paint_wear_requires_authored_attribute']=all(any(n.type=='ATTRIBUTE' and n.attribute_name=='SURFV02_Wear' for n in M[k].node_tree.nodes) for k in ['gear_frame','gear_cast'])
checks['no_large_scale_noise']=all(n.inputs['Scale'].default_value>=850 for m in M.values() for n in m.node_tree.nodes if n.type=='TEX_NOISE')
checks['small_cast_tooth']=all(n.inputs['Distance'].default_value<.0002 for m in M.values() for n in m.node_tree.nodes if n.type=='BUMP')
result={'checks':checks,'passed':all(checks.values()),'roles':{k:m.name for k,m in M.items()},'scope':'Optional shader structure audit; running-gear owner does geometry/context visual review'}
(OUT/'qa'/'surfaces'/'gear_surface_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert result['passed']
