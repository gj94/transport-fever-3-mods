"""Optional painted/dusty running-gear surfaces for the geometry owner's opt-in.

This module does not assign any material or edit any geometry. Existing polished
pins, fasteners and contact faces keep their separate conductive material roles.
Exposed enamel wear is zero unless explicitly authored in SURFV02_Wear.
"""
import bpy
import surface_materials as S


def _upward_dust(nt, coord, side=.10, top=.31):
    geo=S._node(nt,'ShaderNodeNewGeometry','Surface orientation only, never world Position')
    local=S._node(nt,'ShaderNodeVectorTransform','Object-local up direction')
    local.vector_type='NORMAL';local.convert_from='WORLD';local.convert_to='OBJECT'
    S._link(nt,geo.outputs['Normal'],local.inputs['Vector'])
    sep=S._node(nt,'ShaderNodeSeparateXYZ','Local normal Z')
    S._link(nt,local.outputs['Vector'],sep.inputs[0])
    mr=S._node(nt,'ShaderNodeMapRange','Upward deposition without side mottling')
    mr.clamp=True;mr.interpolation_type='SMOOTHSTEP'
    mr.inputs['From Min'].default_value=.10;mr.inputs['From Max'].default_value=.95
    mr.inputs['To Min'].default_value=side;mr.inputs['To Max'].default_value=top
    S._link(nt,sep.outputs['Z'],mr.inputs['Value'])
    fine=S._noise(nt,coord,1350,2,'Submillimetre dry dust grain')
    variation=S._range(nt,fine,.95,1.05,'Only five percent deposition grain')
    return S._math(nt,'MULTIPLY',mr.outputs['Result'],variation,'Thin directional dust coverage'),fine


def painted_gear(name,paint_color,roughness=.56,cast=False,side_dust=.09,top_dust=.30):
    m,nt=S._new(name,paint_color);co=S._coord(nt,False)
    paint=S._principled(nt,'Dielectric dark gear enamel',paint_color,roughness,0,280,280)
    dust=S._principled(nt,'Dry deposited mineral dust',(.172,.128,.075),.83,0,280,-50)
    steel=S._principled(nt,'Only intentionally exposed steel',(.40,.41,.395),.37,1,280,-350)
    coverage,fine=_upward_dust(nt,co,side_dust,top_dust)
    # Casting tooth is genuinely small and stays in normals/roughness, not large
    # colour clouds. Cast housings differ subtly from fabricated sheet sections.
    tooth=S._noise(nt,co,900 if cast else 1500,2,'Fine cast tooth' if cast else 'Fine enamel tooth')
    normal=S._bump(nt,tooth,.00013 if cast else .000050,.16)
    for node in (paint,dust,steel):S._link(nt,normal,node.inputs['Normal'])
    S._link(nt,S._range(nt,tooth,roughness-.018,roughness+.018,'Narrow paint finish'),paint.inputs['Roughness'])
    deposited=S._node(nt,'ShaderNodeMixShader','Opaque paint with thin dry deposit',620,150)
    S._link(nt,coverage,deposited.inputs[0]);S._link(nt,paint.outputs[0],deposited.inputs[1]);S._link(nt,dust.outputs[0],deposited.inputs[2])
    authored=S._node(nt,'ShaderNodeAttribute','Authored contact wear only')
    authored.attribute_name='SURFV02_Wear'
    clamped=S._node(nt,'ShaderNodeClamp','Bound authored wear to valid coverage')
    clamped.inputs['Min'].default_value=0;clamped.inputs['Max'].default_value=1
    S._link(nt,authored.outputs['Fac'],clamped.inputs['Value'])
    out=S._node(nt,'ShaderNodeMixShader','Sparse intentional exposed substrate',780,0)
    S._link(nt,clamped.outputs['Result'],out.inputs[0]);S._link(nt,deposited.outputs[0],out.inputs[1]);S._link(nt,steel.outputs[0],out.inputs[2])
    S._output(nt,out.outputs[0])
    m['physical_model']='Dielectric enamel + directional dielectric dust; exposed metal only from an authored mask'
    m['wear_attribute']='SURFV02_Wear, float or color attribute; absent means zero exposed-metal wear'
    m['dust_coordinates']='Object-local normal and metric local grain; no world-position texture swimming'
    return m


def setup():
    """Return optional roles; caller chooses its own explicit assignments."""
    M={
        'gear_frame':painted_gear('Gear_frame_painted_and_dusted',(.037,.038,.033),.55,False,.095,.30),
        'gear_cast':painted_gear('Gear_cast_housing_painted_and_dusted',(.034,.035,.030),.59,True,.11,.34),
        'gear_wheelweb':S._dirty_steel('Gear_wheelweb_oxide_film',(.40,.405,.375),.46,(.074,.051,.029),.92,.000075),
    }
    for key,m in M.items():m['surface_role']=key
    return M
