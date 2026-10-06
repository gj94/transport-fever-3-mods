"""Original, metric-scale WAP-7 surface materials for Blender 4.3.2.

This module owns materials, not geometry. ``setup()`` only builds materials;
``apply()`` updates eligible legacy exterior slots and returns the role library.
All shader datablocks are prefixed SURFV02_. Cab/running-gear owner collections
and their materials are never edited. No source photograph is used as a texture.

The original construction-directed 6K paint maps are from make_surface_maps.py.
Microfinish is procedural in metres, anchored to WAP7_ROOT, not Generated space.
The small residual colour variations are independent of bump. Rust, paint, rubber
and dust are dielectric; conductive response belongs to exposed metal regions.
"""
import bpy, hashlib, math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1]
PREFIX = 'SURFV02_'
VERSION = '2.4.0'
PROTECTED_PREFIXES = ('CABV02_', 'RGV02_', 'RG_', 'V02_RG', 'GEARV02_', 'MACHV02_')
PROTECTED_COLLECTIONS = ('CAB_INTERIORS_V02', 'CABV02_', 'RGV02_', 'RG_', 'RUNNING_GEAR_V02', 'V02_RG_', 'MACHV02_')


def _node(nt, kind, name, x=0, y=0):
    n = nt.nodes.new(kind); n.name = name; n.label = name; n.location = (x, y)
    return n


def _link(nt, source, target):
    nt.links.new(source, target)


def _math(nt, operation, a, b=None, name=None):
    n = _node(nt, 'ShaderNodeMath', name or operation); n.operation = operation
    if isinstance(a, (int, float)): n.inputs[0].default_value = a
    else: _link(nt, a, n.inputs[0])
    if b is not None:
        if isinstance(b, (int, float)): n.inputs[1].default_value = b
        else: _link(nt, b, n.inputs[1])
    return n.outputs[0]


def _range(nt, source, low, high, name='Calibrated range'):
    n = _node(nt, 'ShaderNodeMapRange', name)
    n.inputs['From Min'].default_value = 0
    n.inputs['From Max'].default_value = 1
    n.inputs['To Min'].default_value = low
    n.inputs['To Max'].default_value = high
    _link(nt, source, n.inputs['Value'])
    return n.outputs['Result']


def _coord(nt, root=True):
    n = _node(nt, 'ShaderNodeTexCoord', 'Metric object coordinates', -1100, 0)
    if root: n.object = bpy.data.objects.get('WAP7_ROOT')
    return n.outputs['Object']


def _noise(nt, coord, scale, detail=2, name='Fine surface structure'):
    n = _node(nt, 'ShaderNodeTexNoise', name, -800, 0)
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = .55
    _link(nt, coord, n.inputs['Vector'])
    return n.outputs['Fac']


def _bump(nt, height, distance, strength=.18, normal=None, name='Micrometre finish'):
    n = _node(nt, 'ShaderNodeBump', name, 180, -260)
    n.inputs['Distance'].default_value = distance
    n.inputs['Strength'].default_value = strength
    _link(nt, height, n.inputs['Height'])
    if normal: _link(nt, normal, n.inputs['Normal'])
    return n.outputs['Normal']


def _principled(nt, name, color, roughness, metallic=0, x=350, y=0):
    p = _node(nt, 'ShaderNodeBsdfPrincipled', name, x, y)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    p.inputs['IOR'].default_value = 1.5
    p.inputs['Specular IOR Level'].default_value = .5
    return p


def _new(name, color=(.18, .18, .18)):
    name = name if name.startswith(PREFIX) else PREFIX + name
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; m.diffuse_color = (*color, 1)
    m.node_tree.nodes.clear()
    m['surface_version'] = VERSION
    m['provenance'] = 'Original constructed procedural shader; no photographic texture pixels'
    m['coordinate_units'] = 'metres; root-anchored body maps, per-object hardware grain, explicit buffer UV'
    return m, m.node_tree


def _output(nt, shader):
    o = _node(nt, 'ShaderNodeOutputMaterial', 'Material Output', 900, 0)
    _link(nt, shader, o.inputs['Surface'])
    return o


def basic(name, c, rough=.45, metal=0, noise=.018, micro=.000035, scale=1400,
          rough_variation=.014, root=False):
    """Compatibility factory; c is linear RGB, micro is height in metres.

    Restrained grain only. Neither this function nor any setup function assigns
    materials to objects. Paint should always pass metal=0.
    """
    m, nt = _new(name, c)
    p = _principled(nt, 'Principled BSDF', c, rough, metal)
    if noise or micro or rough_variation:
        fac = _noise(nt, _coord(nt, root), scale, 2, 'Submillimetre grain')
        if noise:
            ramp = _node(nt, 'ShaderNodeValToRGB', 'Very low amplitude colour variation', -450, 250)
            ramp.color_ramp.elements[0].color = (*(max(0, v * (1-noise)) for v in c), 1)
            ramp.color_ramp.elements[1].color = (*(min(1, v * (1+noise)) for v in c), 1)
            _link(nt, fac, ramp.inputs[0]); _link(nt, ramp.outputs['Color'], p.inputs['Base Color'])
        if rough_variation:
            _link(nt, _range(nt, fac, max(.01,rough-rough_variation), min(.98,rough+rough_variation),
                            'Narrow micro-roughness range'), p.inputs['Roughness'])
        if micro:
            _link(nt, _bump(nt, fac, micro), p.inputs['Normal'])
    _output(nt, p.outputs[0])
    return m


def image(m, filename, noncolor=False):
    """Pack an original map. Explicitly separate color from scalar data."""
    path = OUT / 'textures' / filename
    if not path.exists(): raise FileNotFoundError('Generate original maps first: ' + str(path))
    key = PREFIX + 'MAP_' + filename.replace('/', '_')
    im = bpy.data.images.get(key)
    stamp = str(path.stat().st_mtime_ns)
    if im is None:
        im = bpy.data.images.load(str(path), check_existing=False); im.name = key
    elif im.get('source_stamp') != stamp:
        if im.packed_file: im.unpack(method='REMOVE')
        im.filepath = str(path); im.reload()
    im.colorspace_settings.name = 'Non-Color' if noncolor else 'sRGB'
    im.filepath = str(path)
    if not im.packed_file: im.pack()
    im.filepath = '//textures/' + filename
    im['source_stamp'] = stamp
    t = _node(m.node_tree, 'ShaderNodeTexImage', filename, -700, 350)
    t.image = im; t.extension = 'EXTEND'; t.interpolation = 'Linear'
    return t


def _project(nt, axes, offset, size):
    sep = _node(nt, 'ShaderNodeSeparateXYZ', 'Body-fixed metric axes', -850, 650)
    _link(nt, _coord(nt), sep.inputs[0])
    comb = _node(nt, 'ShaderNodeCombineXYZ', 'Construction atlas coordinates', -500, 650)
    for j, axis in enumerate(axes):
        v = _math(nt, 'ADD', sep.outputs[axis], offset[j], axis+' atlas offset')
        v = _math(nt, 'DIVIDE', v, size[j], axis+' atlas scale in metres')
        _link(nt, v, comb.inputs[j])
    return comb.outputs[0]


def mapped_paint(name, prefix, axes='XZ', offset=(9.6,-1.44), size=(19.2,2.38)):
    """Dielectric enamel with construction-located runoff and lower-sill dust.

    Photo pixels and generic large mottling are intentionally absent. The map
    establishes where dirt goes; 0.7 mm finish affects grazing highlights only.
    """
    m = basic(name, (.70,.70,.66), .43, 0, 0, .000040, 1500, rough_variation=0, root=True)
    nt = m.node_tree; p = nt.nodes['Principled BSDF']; uv = _project(nt, axes, offset, size)
    albedo = image(m, prefix+'_albedo.png'); _link(nt, uv, albedo.inputs['Vector'])
    _link(nt, albedo.outputs['Color'], p.inputs['Base Color'])
    rough = image(m, prefix+'_roughness.png', True); _link(nt, uv, rough.inputs['Vector'])
    # Atlas values are approximately 0.43–0.58. Retain dry-rough deposited dirt without a
    # uniformly glossy automotive clearcoat over the entire locomotive.
    _link(nt, rough.outputs['Color'], p.inputs['Roughness'])
    p.inputs['Coat Weight'].default_value = 0
    # Gentle broad sheet response is <20 micrometres effective and limited to
    # surface normal, never silhouette displacement or colour cloudiness.
    previous = p.inputs['Normal'].links[0].from_socket
    warp = _noise(nt, _coord(nt), 3.0, 1, 'Subtle pressed-sheet highlight response')
    _link(nt, _bump(nt, warp, .00012, .12, previous, '18 micron effective sheet normal'), p.inputs['Normal'])
    m['substrate'] = 'Opaque polyurethane-type finish over steel; exposed substrate is separate geometry/material'
    m['wear_placement'] = 'Original mapped roof runoff, filter edges, doors and lower sill'
    return m


def _dirty_steel(name, color, roughness, dust_color, dirt_amount=.56, grain=.00011, grain_scale=850):
    """Spatial mixture of exposed conductive steel and dry dielectric film.

    This is for cast/forged hardware, never white or red body paint. Material
    roles provide the variation; the shader does not invent large rust islands.
    """
    m, nt = _new(name, dust_color); co = _coord(nt, False)
    exposed = _principled(nt, 'Exposed conductive metal', color, roughness, 1, 350, 200)
    film = _principled(nt, 'Dry oxide and deposited dust', dust_color, .72, 0, 350, -150)
    fine = _noise(nt, co, grain_scale, 2, 'Fine cast-surface tooth')
    normal = _bump(nt, fine, grain, .18)
    _link(nt, normal, exposed.inputs['Normal']); _link(nt, normal, film.inputs['Normal'])
    # +/- 0.055 coverage at millimetre scale: no broad concrete-looking albedo noise.
    coverage = _range(nt, fine, max(0,dirt_amount-.055), min(1,dirt_amount+.055), 'Dry film coverage')
    mix = _node(nt, 'ShaderNodeMixShader', 'Metal / dry dielectric coverage', 700, 0)
    _link(nt, coverage, mix.inputs[0]); _link(nt, exposed.outputs[0], mix.inputs[1]); _link(nt, film.outputs[0], mix.inputs[2])
    _output(nt, mix.outputs[0]); m['physical_model'] = 'Area mixture: conductive metal + dielectric dry film'
    return m


def machined_steel(name='Wheel_tread_polished_steel', axis='Y'):
    """Circumferential scoring on a wheel whose axle is axis (default Y).

    Axis-parallel metric coordinate generates fine bands along the tread, with
    no radial brown rust on the rail-contact surface. Animation remains valid
    for round treads; use per-wheel local coordinates for non-circular parts.
    """
    m = basic(name, (.48,.50,.52), .23, 1, .012, 0, 1900, .008)
    nt=m.node_tree; p=nt.nodes['Principled BSDF']
    sep=_node(nt,'ShaderNodeSeparateXYZ','Across the machined tread')
    _link(nt,_coord(nt,False),sep.inputs[0])
    x=_math(nt,'MULTIPLY',sep.outputs[axis],16000,'Fine 0.39 mm machining lines')
    sin=_math(nt,'SINE',x,name='Circumferential fine scoring')
    _link(nt,_range(nt,_math(nt,'ADD',_math(nt,'MULTIPLY',sin,.5),.5),.205,.245,'Contact polish roughness'),p.inputs['Roughness'])
    _link(nt,_bump(nt,sin,.000004,.16,name='Less than one micron scoring'),p.inputs['Normal'])
    p.inputs['Anisotropic'].default_value=.27
    tangent=_node(nt,'ShaderNodeTangent','Radial tangent to wheel')
    tangent.direction_type='RADIAL';tangent.axis=axis
    _link(nt,tangent.outputs['Tangent'],p.inputs['Tangent'])
    m['intended_role']='Only actual wheel contact bands, pins or exposed swept contact faces'
    return m


def _glass(name, tint=(.970,.985,.979), roughness=.026, ior=1.52):
    m=basic(name,tint,roughness,0,0,0,rough_variation=0)
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Transmission Weight'].default_value=1
    p.inputs['IOR'].default_value=ior
    m['geometry_requirement']='Closed solid pane with real 6–10 mm thickness and outward normals; no alpha blending'
    m['physical_model']='Clear soda-lime optical response; pane tint intentionally very restrained'
    return m


def buffer_contact(name='Buffer_face_scuffed_steel'):
    """UV-mapped steel abrasion, dry perimeter deposits and dark centre grease.

    Requires assign_buffer_uv(obj). Uses only original generated masks.
    """
    m,nt=_new(name,(.14,.13,.105))
    uv=_node(nt,'ShaderNodeUVMap','Buffer face projection');uv.uv_map='SURFV02_BufferUV'
    wear=image(m,'surfaces/SURFV02_buffer_wear.png',True)
    greasemask=image(m,'surfaces/SURFV02_buffer_grease.png',True)
    rough=image(m,'surfaces/SURFV02_buffer_roughness.png',True)
    for t in (wear,greasemask,rough):_link(nt,uv.outputs[0],t.inputs['Vector'])
    steel=_principled(nt,'Abraded conductive steel',(.47,.48,.47),.34,1,250,350)
    dry=_principled(nt,'Dry perimeter dust and oxide',(.16,.143,.107),.78,0,250,50)
    grease=_principled(nt,'Smeared graphite-black grease',(.018,.020,.017),.25,0,250,-250)
    grease.inputs['IOR'].default_value=1.47
    _link(nt,rough.outputs['Color'],steel.inputs['Roughness'])
    mix=_node(nt,'ShaderNodeMixShader','Scuff exposes metal',550,170)
    _link(nt,wear.outputs['Color'],mix.inputs[0]);_link(nt,dry.outputs[0],mix.inputs[1]);_link(nt,steel.outputs[0],mix.inputs[2])
    mix2=_node(nt,'ShaderNodeMixShader','Contact grease over worn face',750,0)
    _link(nt,greasemask.outputs['Color'],mix2.inputs[0]);_link(nt,mix.outputs[0],mix2.inputs[1]);_link(nt,grease.outputs[0],mix2.inputs[2])
    _output(nt,mix2.outputs[0]);m['wear_placement']='Scuffed near-contact annulus, irregular dusty perimeter, central grease smear'
    return m


def assign_buffer_uv(obj, axis='X', rotation=None):
    """Add an explicit local planar UV layer; preserve every existing layer."""
    indices={'X':(1,2),'Y':(0,2),'Z':(0,1)}[axis]
    if rotation is None:
        # Deterministic per-buffer variation without multiple texture copies.
        rotation=(int(hashlib.sha256(obj.name.encode()).hexdigest()[:8],16)/4294967295)*math.tau
    cr,sr=math.cos(rotation),math.sin(rotation)
    uv=obj.data.uv_layers.get('SURFV02_BufferUV') or obj.data.uv_layers.new(name='SURFV02_BufferUV')
    coords=[v.co for v in obj.data.vertices]
    lo=[min(c[i] for c in coords) for i in indices];hi=[max(c[i] for c in coords) for i in indices]
    for loop in obj.data.loops:
        c=coords[loop.vertex_index]
        u,v=tuple((c[j]-lo[k])/max(hi[k]-lo[k],1e-6)-.5 for k,j in enumerate(indices))
        uv.data[loop.index].uv=(u*cr-v*sr+.5,u*sr+v*cr+.5)
    return uv



def _map_range(nt, value, from_min, from_max, to_min, to_max, name):
    n=_node(nt,'ShaderNodeMapRange',name);n.clamp=True;n.interpolation_type='SMOOTHSTEP'
    for key,val in [('From Min',from_min),('From Max',from_max),('To Min',to_min),('To Max',to_max)]:n.inputs[key].default_value=val
    _link(nt,value,n.inputs['Value']);return n.outputs['Result']


def _colour_soil_overlay(m, factor, dirt_color, roughness_gain, label):
    nt=m.node_tree;p=nt.nodes['Principled BSDF']
    old=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
    mix=_node(nt,'ShaderNodeMixRGB',label+' colour');mix.blend_type='MIX'
    _link(nt,factor,mix.inputs[0]);mix.inputs[2].default_value=(*dirt_color,1)
    if old:_link(nt,old,mix.inputs[1])
    else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
    _link(nt,mix.outputs[0],p.inputs['Base Color'])
    rough=p.inputs['Roughness'].links[0].from_socket if p.inputs['Roughness'].is_linked else p.inputs['Roughness'].default_value
    value=_math(nt,'ADD',rough,_math(nt,'MULTIPLY',factor,roughness_gain,label+' roughness increment'))
    _link(nt,value,p.inputs['Roughness'])


def add_stripe_service_film(m, width_factor=1):
    """Continue real drip/deposit locations over the coloured coating very lightly."""
    nt=m.node_tree;side_uv=_project(nt,'XZ',(9.6,-1.44),(19.2,2.38))
    front_uv=_project(nt,'YZ',(1.55*width_factor,-1.40),(3.1*width_factor,2.2))
    masks=[]
    for name,uv in [('v02_body_side1_grime_mask.png',side_uv),('v02_body_side2_grime_mask.png',side_uv),('v02_nose_grime_mask.png',front_uv)]:
        t=image(m,name,True);_link(nt,uv,t.inputs[0]);masks.append(t.outputs['Color'])
    sep=_node(nt,'ShaderNodeSeparateXYZ','Body region for service film');_link(nt,_coord(nt),sep.inputs[0])
    lr=_math(nt,'GREATER_THAN',sep.outputs['Y'],0,'Select opposite flank')
    mix=_node(nt,'ShaderNodeMixRGB','Actual asymmetric flank masks')
    _link(nt,lr,mix.inputs[0]);_link(nt,masks[0],mix.inputs[1]);_link(nt,masks[1],mix.inputs[2])
    front=_map_range(nt,_math(nt,'ABSOLUTE',sep.outputs['X']),8.98,9.18,0,1,'Cab corner to nose transition')
    select=_node(nt,'ShaderNodeMixRGB','Front versus side deposits')
    _link(nt,front,select.inputs[0]);_link(nt,mix.outputs[0],select.inputs[1]);_link(nt,masks[2],select.inputs[2])
    amount=_math(nt,'MULTIPLY',select.outputs[0],.17,'Thin soil over vermilion')
    _colour_soil_overlay(m,amount,(.105,.076,.043),.30,'Located soil film')
    m['service_film']='Same construction-located masks as white paint, at only 17 percent of mask coverage; clean pigment is unchanged'


def add_roof_foot_runoff(m):
    nt=m.node_tree;uv=_project(nt,'XY',(9.6,1.75),(19.2,3.5))
    t=image(m,'surfaces/SURFV02_roof_foot_runoff.png',True);_link(nt,uv,t.inputs[0])
    sep=_node(nt,'ShaderNodeSeparateXYZ','Roof-only metric height gate');_link(nt,_coord(nt),sep.inputs[0])
    lower=_map_range(nt,sep.outputs['Z'],3.53,3.62,0,1,'Above roof shoulder')
    upper=_map_range(nt,sep.outputs['Z'],4.00,4.07,1,0,'Exclude elevated lamp and horns')
    amount=_math(nt,'MULTIPLY',t.outputs['Color'],_math(nt,'MULTIPLY',lower,upper))
    _colour_soil_overlay(m,amount,(.090,.045,.018),.13,'Roof attachment runoff')
    m['service_film']='Sparse actual horn-foot and searchlight-foot runoff; XY metric map with soft roof-height gate'


def windscreen_service_glass():
    """Preserve clear optics, with at most 2.5 percent service film outside a sweep."""
    m=_glass('Laminated_windscreen_with_service_film');nt=m.node_tree
    glass=nt.nodes['Principled BSDF'];out=nt.nodes['Material Output']
    uv=_node(nt,'ShaderNodeUVMap','Pane-normalized service sweep');uv.uv_map='SURFV02_WindscreenUV'
    t=image(m,'surfaces/SURFV02_windscreen_service_film.png',True);_link(nt,uv.outputs[0],t.inputs[0])
    factor=_math(nt,'MULTIPLY',t.outputs['Color'],.025,'Maximum 2.5 percent unswept dust')
    _link(nt,_range(nt,t.outputs['Color'],.026,.054,'Clean versus unswept micro-roughness'),glass.inputs['Roughness'])
    dust=_principled(nt,'Thin exterior mineral film',(.10,.078,.045),.85,0,350,-300)
    mix=_node(nt,'ShaderNodeMixShader','Clear pane with restrained exterior residue',720,0)
    _link(nt,factor,mix.inputs[0]);_link(nt,glass.outputs[0],mix.inputs[1]);_link(nt,dust.outputs[0],mix.inputs[2]);_link(nt,mix.outputs[0],out.inputs['Surface'])
    m['maximum_dust_fraction']=.025
    m['optical_scope']='Front windscreens only; same clear glass IOR/transmission as before. Side panes remain clear.'
    return m


def assign_windscreen_uv(obj):
    """Stable Y/Z pane UVs, mirrored so the outboard wiper pivot stays canonical."""
    uv=obj.data.uv_layers.get('SURFV02_WindscreenUV') or obj.data.uv_layers.new(name='SURFV02_WindscreenUV')
    coords=[v.co for v in obj.data.vertices];ys=[v.y for v in coords];zs=[v.z for v in coords]
    y0,y1,z0,z1=min(ys),max(ys),min(zs),max(zs);flip=(y0+y1)>0
    for loop in obj.data.loops:
        p=coords[loop.vertex_index];u=(p.y-y0)/max(y1-y0,1e-6)
        uv.data[loop.index].uv=(1-u if flip else u,(p.z-z0)/max(z1-z0,1e-6))
    obj['windscreen_film_scope']='Representative unswept perimeter and wiper field; original clear optical model preserved'
    return uv



def assign_windscreen_service(obj, material):
    """Apply film only to the exterior face; preserve clear inner/edge surfaces."""
    uv=assign_windscreen_uv(obj)
    try:index=list(obj.data.materials).index(material)
    except ValueError:
        index=len(obj.data.materials);obj.data.materials.append(material)
    end=1 if sum(v.co.x for v in obj.data.vertices)>=0 else -1
    count=0
    for face in obj.data.polygons:
        if face.normal.x*end>.65:face.material_index=index;count+=1
    if not count:raise ValueError('Windscreen service helper found no exterior +/−X pane face: '+obj.name)
    obj['windscreen_service_polygons']=count
    return uv


def setup(context=None):
    width_factor=float((context or {}).get('body_width_factor',1.0))
    if width_factor<=0:raise ValueError('body_width_factor must be positive')
    M={}
    M['white']=mapped_paint('White_side_1_enamel','v02_body_side1')
    M['white2']=mapped_paint('White_side_2_enamel','v02_body_side2')
    M['nose']=mapped_paint('Cab_nose_enamel','v02_nose','YZ',(1.55*width_factor,-1.40),(3.1*width_factor,2.2))
    M['nose']['projection_width_factor']=width_factor
    M['cream']=basic('Aged_signal_white_hardware',(.64,.635,.579),.43,0,.014,.000032,1600)
    M['red']=basic('Vermilion_enamel',(.46,.080,.010),.44,0,.015,.000037,1700)
    M['roof']=basic('Graphite_roof_enamel',(.066,.068,.064),.53,0,.028,.000060,1100)
    add_stripe_service_film(M['red'],width_factor)
    add_roof_foot_runoff(M['roof'])
    M['blackpaint']=basic('Charcoal_hardware_enamel',(.022,.026,.024),.48,0,.024,.000045,1250)
    M['iron']=_dirty_steel('Seasoned_structural_steel',(.39,.39,.36),.48,(.105,.083,.056),.81,.00015)
    M['cast']=_dirty_steel('Cast_coupler_steel',(.37,.37,.345),.54,(.069,.055,.038),.82,.00032,700)
    M['dust']=basic('Settled_fine_ochre_dust',(.19,.147,.092),.85,0,.035,.000045,1800,.025)
    M['dust'].node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value=.10
    M['rust']=basic('Dry_iron_oxide',(.108,.044,.015),.80,0,.055,.000095,1000,.025)
    M['steel']=_dirty_steel('Weathered_zinc_fastener',(.54,.56,.55),.34,(.125,.13,.119),.22,.000022)
    M['bright']=basic('Rubbed_metal_contact',(.48,.50,.52),.245,1,.010,.000010,1600,.012)
    M['grease']=basic('Joint_grease',(.012,.014,.011),.24,0,.025,.000030,650,.022)
    M['grease'].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.47
    M['rubber']=basic('Dry_EPDM_rubber',(.009,.011,.010),.66,0,.027,.000048,1800,.026)
    M['ochre']=basic('Faded_ochre_pantograph_enamel',(.31,.211,.060),.47,0,.023,.000050,1400)
    M['copper']=_dirty_steel('Oxidised_copper_conductor',(.72,.34,.14),.31,(.094,.045,.019),.48,.000026)
    M['ceramic']=basic('Brown_glazed_porcelain',(.064,.020,.007),.18,0,.006,.000009,2400,.005)
    M['ceramic'].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.52
    M['glass']=_glass('Clear_laminated_cab_glass')
    M['windscreen']=windscreen_service_glass()
    M['lens']=_glass('Moulded_optical_glass',(.985,.988,.982),.033,1.51)
    M['redlens']=basic('Ruby_signal_lens',(.23,.004,.0015),.18,0,.008,.000009,2000,.005)
    M['redlens'].node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.55
    M['green']=basic('Green_connector_enamel',(.018,.135,.065),.43,0,.02,.000032,1400)
    M['brass']=_dirty_steel('Seasoned_brass_fittings',(.60,.40,.13),.31,(.095,.072,.024),.25,.000027)
    M['carbon']=basic('Graphite_collector_carbon',(.019,.022,.022),.62,0,.035,.000027,1800,.018)
    # Optional extended roles; established dictionary keys remain unchanged.
    M['tread']=machined_steel()
    M['buffer']=buffer_contact()
    for role,m in M.items():m['surface_role']=role
    return M


def setmat(o,m):
    if hasattr(o.data,'materials'):
        o.data.materials.clear();o.data.materials.append(m)


def _protected(o):
    if o.name.startswith(PROTECTED_PREFIXES):return True
    return any(c.name.startswith(PROTECTED_COLLECTIONS) for c in o.users_collection)


def _world_center(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    center=sum(pts,Vector())/8
    root=bpy.data.objects.get('WAP7_ROOT')
    return root.matrix_world.inverted()@center if root else center


def apply(context=None):
    """Swap legacy exterior material slots only; never globally edit shared mats."""
    M=setup(context);shell=bpy.data.objects.get('Chamfered welded body shell')
    if shell is not None:
        shell.data.materials.clear()
        for k in ('white','white2','nose','roof'):shell.data.materials.append(M[k])
        for p in shell.data.polygons:
            if p.center.z>3.555:p.material_index=3
            elif abs(p.normal.x)>.48:p.material_index=2
            else:p.material_index=0 if p.center.y<0 else 1
    swaps={'PBR • vermilion oxide stripe':'red','PBR • soot-grey roof enamel':'roof',
           'PBR • rubbed black metal':'blackpaint','PBR • weathered EPDM':'rubber',
           'PBR • glazed brown porcelain':'ceramic','PBR • worn ochre pantograph paint':'ochre',
           'PBR • dark oxidised copper bus':'copper','PBR • laminated cab glazing':'glass',
           'PBR • clear prismatic lamp lens':'lens','PBR • dark ruby marker lens':'redlens',
           'PBR • aged iron oxide':'rust','PBR • polished steel contact edges':'steel',
           'PBR • dusty cast bogie steel':'iron'}
    protected_data={o.data for o in bpy.data.objects if o.type=='MESH' and _protected(o)}
    for o in list(bpy.data.objects):
        if o.type!='MESH' or o==shell or _protected(o) or o.data in protected_data:continue
        # Protected owner materials are deliberately untouched even if reused.
        for i,mat in enumerate(list(o.data.materials)):
            if not mat:continue
            if mat.name=='PBR • aged signal-white enamel':
                center=_world_center(o)
                o.data.materials[i]=M['nose'] if abs(center.x)>9 else M['white' if center.y<0 else 'white2']
            elif mat.name in swaps:o.data.materials[i]=M[swaps[mat.name]]
    return M
