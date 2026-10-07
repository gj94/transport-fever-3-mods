"""Editable WBL22.03-informed pantograph small hardware, with live flexible shunts.

The Schunk Train-18 manual, pp20/34/125, supports the construction vocabulary:
base mounting feet and adjustable brackets, copper bearing-bypass shunts with eye
lugs, rocker boxes, flat springs, strip clamps and pneumatic monitoring fittings.
The non-dimensioned small-hardware dimensions/routes below are visual
approximations, not a manufacturing model. All inherited rig controls are kept.
"""
import math
import bpy
from mathutils import Vector
from common import mesh, box, cyl, ring, tube, beam, bolt, bezier_points, remove_prefix

P = 'VB02_PMICRO_'
SOURCE = 'https://rskr.irimee.in/forum/wp-content/uploads/2023/07/Operational%20Manual%20Pantograph%20_Train%2018.pdf'


def _finish(name, rgb, metallic, roughness, scale=1800):
    m = bpy.data.materials.get(P + name) or bpy.data.materials.new(P + name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1)
    n = m.node_tree.nodes
    n.clear()
    p = n.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    out = n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs[0], out.inputs[0])
    tex = n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 2
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .12
    bump.inputs['Distance'].default_value = .000055
    m.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    m.node_tree.links.new(bump.outputs[0], p.inputs['Normal'])
    return m


def _ribbon(name, points, width, thickness, mat, parent, coll, width_axis=(0,1,0)):
    """Closed, flat-section spring/formed metal strip; deliberately not a round tube."""
    pts = [Vector(p) for p in points]
    axis = Vector(width_axis).normalized()
    vs = []
    for i, p in enumerate(pts):
        tangent = (pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        normal = tangent.cross(axis).normalized()
        for u, v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            vs.append(tuple(p + u*width*.5*axis + v*thickness*.5*normal))
    fs = [(3,2,1,0), tuple((len(pts)-1)*4+j for j in range(4))]
    for i in range(len(pts)-1):
        for j in range(4):
            fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    return mesh(P+name,vs,fs,mat,parent,coll,bevel=.00045,local=True)


def _eye_plate(name, center, outer, inner, thickness, mat, parent, coll, axis='Y'):
    return ring(P+name,center,outer,inner,thickness,mat,parent,coll,axis,40,True)


def _slotted_plate(name, x, y, z, width, height, slot_width, slot_height, mat, parent, coll):
    """Thin upright with a genuine elongated oval through slot, along Y."""
    N=40; ro=[]
    for j in range(N):
        a=math.tau*j/N;dx=math.cos(a);dz=math.sin(a)
        k=min(width*.5/max(abs(dx),1e-10),height*.5/max(abs(dz),1e-10))
        ro.append((x+dx*k,z+dz*k))
    ri=[(x+slot_width*.5*math.cos(math.tau*j/N),z+slot_height*.5*math.sin(math.tau*j/N)) for j in range(N)]
    vs=[(xx, yy, zz) for yy in [y-.004,y+.004] for loop in [ro,ri] for xx,zz in loop]
    fs=[]
    for j in range(N):
        k=(j+1)%N
        fs += [(j,k,N+k,N+j),(2*N+j,3*N+j,3*N+k,2*N+k),
               (j,2*N+j,2*N+k,k),(N+j,N+k,3*N+k,3*N+j)]
    return mesh(P+name,vs,fs,mat,parent,coll,bevel=.0007,local=True)


def _endpoint(name, parent, pos, tangent_world, coll):
    e=bpy.data.objects.new(P+name,None);coll.objects.link(e);e.parent=parent
    e.location=pos;e.empty_display_type='PLAIN_AXES';e.empty_display_size=.025
    direction=parent.matrix_world.to_3x3().inverted()@Vector(tangent_world)
    e.rotation_euler=direction.to_track_quat('X','Z').to_euler()
    e['role']='Flexible cable attachment, rigidly parented to the named mechanical link'
    return e


def _hook_mesh(obj, endpoint_a, endpoint_b, rings, ring_size):
    """Two live Hook modifiers with rigid endpoint rings and a smooth interior blend.

    Endpoint rings have exactly one unit-weight Hook. Their centroid therefore
    follows its endpoint empty exactly, including root and link transforms.
    Middle rings are visually blended, not a cable-length/physics simulation.
    """
    groups=[obj.vertex_groups.new(name='Rigid A to soft middle'),obj.vertex_groups.new(name='Soft middle to rigid B')]
    for i in range(rings):
        t=i/(rings-1)
        u=max(0,min(1,(t-.12)/.76));u=u*u*(3-2*u)
        ids=list(range(i*ring_size,(i+1)*ring_size))
        if u<1:groups[0].add(ids,1-u,'REPLACE')
        if u>0:groups[1].add(ids,u,'REPLACE')
    for target,group in zip([endpoint_a,endpoint_b],groups):
        h=obj.modifiers.new('Live endpoint '+target.name.rsplit('_',1)[-1], 'HOOK')
        h.object=target;h.vertex_group=group.name;h.strength=1;h.falloff_type='NONE'
        h.matrix_inverse=target.matrix_world.inverted()@obj.matrix_world
    obj['flexible_joint']=True
    obj['endpoint_a']=endpoint_a.name;obj['endpoint_b']=endpoint_b.name
    obj['endpoint_ring_vertices']=ring_size
    obj['endpoint_ring_count']=rings
    obj['deformation_scope']='Hook blend for endpoint-preserving visual articulation; not cable mechanics'


def _flex(name, pa, posa, pb, posb, slack, radius, mat, ctrl, coll, copper=None, braid=False):
    """S-slack between endpoints, all local cable vertices under the static controller."""
    bpy.context.view_layer.update()
    wa=pa.matrix_world@Vector(posa);wb=pb.matrix_world@Vector(posb)
    ci=ctrl.matrix_world.inverted();a=ci@wa;b=ci@wb;v=b-a;slack=Vector(slack)
    points=[]
    N=65
    for i in range(N):
        t=i/(N-1)
        # S-shaped out-of-line centre section, vanishing at the fixed eye lugs.
        points.append(a+v*t+slack*math.sin(math.tau*t)*math.sin(math.pi*t)
                      +Vector((0,0,-.025))*math.sin(math.pi*t))
    ea=_endpoint(name+'_A',pa,posa,ctrl.matrix_world.to_3x3()@(points[1]-points[0]),coll)
    eb=_endpoint(name+'_B',pb,posb,ctrl.matrix_world.to_3x3()@(points[-2]-points[-1]),coll)
    bpy.context.view_layer.update()
    o=tube(P+name,[tuple(p) for p in points],radius,mat,ctrl,coll,12,True)
    bpy.context.view_layer.update();_hook_mesh(o,ea,eb,N,12)
    # Real fine braid relief is readable in close-ups without an oversized cable.
    if braid:
        for handed in [-1,1]:
            for strand in range(4):
                pp=[]
                for i,p in enumerate(points):
                    t=i/(N-1);tan=(points[min(i+1,N-1)]-points[max(0,i-1)]).normalized()
                    q=tan.to_track_quat('Z','Y');angle=handed*math.tau*6*t+strand*math.tau/4
                    pp.append(p+q@Vector((radius*math.cos(angle),radius*math.sin(angle),0)))
                wire=tube(P+name+'_braid',[tuple(p) for p in pp],.00043,copper or mat,ctrl,coll,6,True)
                bpy.context.view_layer.update();_hook_mesh(wire,ea,eb,N,6)
                wire['endpoint_ring_vertices']=0 # Centre core is the attachment QA witness.
    return o,ea,eb


def apply(ctx):
    if ctx['kind'] not in ('TC_CC','TC_EC'):
        return {'pantograph_microhardware':False}
    remove_prefix(P)
    M=ctx['materials'];C=ctx['collection'];base=bpy.data.objects['PANTO_BASE'];ctrl=bpy.data.objects['PANTO_CTRL']
    lo=bpy.data.objects['PANTO_LOWER_PIVOT'];up=bpy.data.objects['PANTO_ELBOW_PIVOT'];head=bpy.data.objects['PANTO_HEAD_LEVEL_PIVOT']
    bpy.context.view_layer.update()
    # Only known superseded helper meshes are removed. All controls are untouched.
    replaced=['head_leaf_spring','head_braided_shunt','head_rocker_box','head_rocker_pin','carbon_downturned_horn']
    for o in list(bpy.data.objects):
        if o.type=='MESH' and any(o.name=='VB02_ROOF_'+n or o.name.startswith('VB02_ROOF_'+n+'.') for n in replaced):
            bpy.data.objects.remove(o,do_unlink=True)
    carbon=_finish('carbon_contact_graphite',(.026,.030,.033),.04,.64,2600)
    for o in C.objects:
        if o.type=='MESH' and o.name.startswith('VB02_ROOF_carbon_contact_strip'):
            o.data.materials.clear();o.data.materials.append(carbon)
    copper=_finish('warm_copper_braid',(.31,.105,.044),.87,.38)
    tin=_finish('tinned_eye_lugs',(.46,.47,.43),.88,.34)
    spring=_finish('spring_tempered_steel',(.10,.13,.16),.82,.31)
    plated=_finish('zinc_plated_fixings',(.49,.53,.56),.84,.28)
    nickel=_finish('nickel_pneumatic_fittings',(.38,.41,.42),.91,.25)
    redmark=_finish('torque_witness_ochre',(.58,.29,.025),.12,.59)
    def B(n,c,d,m=M['alloy'],pa=head,b=.001):return box(P+n,c,d,m,pa,C,b,True)
    def CY(n,c,r,d,m=plated,pa=head,axis='Z',N=32):return cyl(P+n,c,r,d,m,pa,C,axis,N,.0004,True)
    def BT(n,c,r=.006,d=.004,pa=head,axis='Z',mat=plated):return bolt(P+n,c,r,d,mat,pa,C,axis,True,True)
    def T(n,pts,r=.003,m=M['rubber'],pa=head):return tube(P+n,bezier_points(pts,8),r,m,pa,C,10,True)

    # Four insulated feet with outboard paired fasteners and folded reinforcing webs.
    for x in [-.28,.55]:
        for s in [-1,1]:
            y=s*.54
            B('base_outboard_mounting_foot',(x,y,.165),(.215,.19,.016),M['dark_metal'],base,.002)
            for dx in [-.062,.062]:
                CY('mounting_foot_stud',(x+dx,y,.184),.0055,.020,plated,base)
                BT('mounting_foot_paired_nut',(x+dx,y,.183),.009,.008,base)
            # Visible triangular gussets, entirely outside arm sweep.
            for dx in [-.043,.043]:
                vv=[(x+dx-.003,s*.447,.184),(x+dx-.003,s*.554,.176),(x+dx-.003,s*.447,.218),
                    (x+dx+.003,s*.447,.184),(x+dx+.003,s*.554,.176),(x+dx+.003,s*.447,.218)]
                mesh(P+'base_foot_welded_gusset',vv,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],M['dark_metal'],base,C,.0006,local=True)
            ring(P+'insulator_top_clamp',(x,y,.146),.077,.064,.007,plated,base,C,'Z',40,True)
    # Adjustable uprights, real elongated holes, stops and lifting eyes.
    for s in [-1,1]:
        for x in [-.11,.66]:
            _slotted_plate('base_upright_slotted_bracket',x,s*.458,.242,.070,.135,.013,.070,M['dark_metal'],base,C)
            for zz in [.205,.275]:BT('bracket_lock_bolt',(x,s*.468,zz),.008,.006,base,'Y')
            B('base_bracket_folded_lip',(x,s*.435,.310),(.070,.055,.008),M['dark_metal'],base)
        for x in [-.31,.52]:
            _eye_plate('base_lifting_eye',(x,s*.487,.240),.023,.014,.008,plated,base,C,'Y')
            B('lifting_eye_weld_pad',(x,s*.487,.216),(.066,.023,.011),M['dark_metal'],base)
        CY('folded_stop_threaded_stem',(.39,s*.45,.232),.008,.038,plated,base)
        BT('folded_stop_locknut',(.39,s*.45,.242),.012,.008,base)
        CY('folded_stop_rubber_bumper',(.39,s*.45,.266),.019,.019,M['rubber'],base)
        # Low base bearing side retainers and grease nipple.
        for dx in [-.039,.039]:BT('base_bearing_retainer',(dx,s*.445,-.025),.007,.005,ctrl,'Y')
        CY('base_grease_nipple',(0,s*.465,.012),.004,.014,nickel,ctrl,'Y',16)

    # Open rocker boxes: two slim cheeks per side, an actual hole around each axle,
    # transverse heel, separated washers and serviceable bolted covers.
    for s in [-1,1]:
        y=s*.40
        B('rocker_box_lower_bridge',(0,y,-.117),(.206,.145,.012),M['alloy'])
        for yy in [y-.065,y+.065]:
            # Through-bored cheek: annulus overlaps thin side lands, never fills bore.
            _eye_plate('rocker_cheek_bored_boss',(0,yy,-.055),.046,.0355,.008,M['alloy'],head,C,'Y')
            for xx in [-.072,.072]:
                B('rocker_cheek_end',(xx,yy,-.075),(.052,.008,.069),M['alloy'])
                BT('rocker_cheek_recess_bolt',(xx,yy+(-.006 if yy<y else .006),-.073),.007,.005,head,'Y')
            B('rocker_cheek_lower_rail',(0,yy,-.111),(.190,.008,.012),M['alloy'])
        for xx in [-.084,.084]:
            CY('rocker_transverse_pin',(xx,y,-.052),.007,.16,plated,head,'Y')
            for ss in [-1,1]:
                BT('rocker_pin_end_nut',(xx,y+ss*.083,-.052),.009,.006,head,'Y')
                ring(P+'rocker_pin_shim',(xx,y+ss*.075,-.052),.012,.007,.002,spring,head,C,'Y',28,True)
        for x in [-.195,.195]:
            direction=1 if x>0 else -1
            # Paired flat leaves with a visible interleaf seam; actual rectangular section.
            for k in range(2):
                pts=bezier_points([(0,y,-.091-k*.004),(direction*.065,y,-.077-k*.004),
                    (direction*.132,y,-.038-k*.004),(x,y,-.012-k*.004)],12)
                ob=_ribbon('flat_curved_leaf_spring',pts,.030,.003,spring,head,C)
                ob['section']='30mm flat width / 3mm thickness, representative'
            B('leaf_root_clamp',(direction*.018,y,-.084),(.037,.048,.012),M['alloy'])
            for yy in [y-.016,y+.016]:BT('leaf_root_clamp_screw',(direction*.018,yy,-.075),.0048,.004)
            B('carbon_carrier_saddle',(x,y,-.012),(.066,.062,.014),M['alloy'])
            for yy in [y-.022,y+.022]:
                BT('carrier_underslung_clamp_nut',(x,yy,-.023),.0062,.005)
            # Strip-carrier side fasteners remain under the carbon contact plane.
            for xx in [x-.033,x+.033]:BT('carrier_side_clamp_bolt',(xx,y,-.012),.0062,.004,head,'X')
        # Small T connection block and the characteristic separated curved monitoring lines.
        by=s*.245
        B('head_monitoring_T_block',(0,by,-.091),(.028,.034,.027),nickel)
        BT('T_block_mounting_screw',(0,by,-.074),.0045,.003)
        for sx in [-1,1]:
            CY('T_block_compression_hex',(sx*.021,by,-.091),.0078,.013,nickel,head,'X',6)
            CY('T_block_tube_ferrule',(sx*.030,by,-.091),.0056,.006,tin,head,'X')
            pts=[(sx*.033,by,-.091),(sx*.072,by,-.097),(sx*.143,s*.31,-.085),
                 (sx*.189,s*.365,-.030),(sx*.195,s*.385,-.014)]
            T('head_monitoring_airline',pts,.0026)
            CY('carbon_monitoring_inlet',(sx*.195,s*.385,-.014),.0058,.012,nickel,head,'Z',6)
        T('head_monitoring_crossfeed',[(0,by,-.106),(.028,by,-.116),(.036,0,-.116)],.0028)
        CY('T_block_vertical_fitting',(0,by,-.111),.0065,.012,nickel,head,'Z',6)

    # Four formed metallic horns: nominal overall 1.800m panhead width preserved.
    for x in [-.195,.195]:
        for s in [-1,1]:
            pts=bezier_points([(x,s*.675,.007),(x,s*.730,-.002),(x,s*.786,-.024),
                 (x,s*.839,-.061),(x,s*.877,-.105),(x,s*.8964,-.151)],10)
            horn=_ribbon('formed_carbon_end_horn',pts,.033,.008,M['brushed'],head,C,(1,0,0))
            # Set exact nominal lateral envelope without changing the contact carrier.
            peak=max(abs(v.co.y) for v in horn.data.vertices)
            if peak>.9:
                for v in horn.data.vertices:
                    if abs(v.co.y)>.87:v.co.y=s*(.87+(abs(v.co.y)-.87)*(.03/(peak-.87)))
            for yy,zz in [(s*.666,.006),(s*.705,-.004)]:
                for side in [-1,1]:BT('horn_attachment_bolt',(x+side*.0185,yy,zz),.0055,.004,head,'X')
            # Underside carrier longitudinal locking screws.
            for yy in [s*.18,s*.55]:BT('strip_carrier_lock_screw',(x,yy,-.012),.005,.004)

    def lug(e):
        # A tubular crimp transitioning to a flat, genuinely holed eye tab.
        CY('shunt_crimp_barrel',(-.011,0,0),.0092,.028,tin,e,'X')
        for xx in [-.006,-.013,-.020]:ring(P+'shunt_crimp_witness',(xx,0,0),.0095,.0089,.001,tin,e,C,'X',24,True)
        B('shunt_flattened_neck',(-.029,0,-.001),(.027,.019,.006),tin,e,.002)
        _eye_plate('shunt_flattened_eye_lug',(-.048,0,-.001),.013,.0052,.006,tin,e,C,'Z')
        CY('shunt_eye_attachment_stud',(-.048,0,.002),.0043,.016,plated,e)
        BT('shunt_eye_clamping_nut',(-.048,0,.009),.0075,.006,e)
        # Small torque witness line on each otherwise neutral mechanical nut.
        B('shunt_nut_torque_witness',(-.048,0,.0122),(.002,.010,.0005),redmark,e,.0001)

    shunts=[]
    for s in [-1,1]:
        # Mounts bypass the base, elbow and head bearings on BOTH sides. Endpoints
        # stay rigidly attached to the correct links rather than a frozen world wire.
        specs=[('base',ctrl,(-.085,s*.43,.014),lo,(.19,s*.348,-.014),(.07,s*.105,.035)),
               ('elbow',lo,(1.38,s*.21,-.005),up,(-.15,s*.155,-.007),(.07,s*.10,.065)),
               ('head',up,(-1.12,s*.325,-.012),head,(.10,s*.43,-.097),(.05,s*.095,-.025))]
        for label,pa,a,pb,b,slack in specs:
            ob,ea,eb=_flex('copper_bypass_'+label+('_L' if s<0 else '_R'),pa,a,pb,b,slack,.006,copper,ctrl,C,tin,True)
            shunts.append(ob.name);lug(ea);lug(eb)
    # Short head shunts also bridge rocker-to-carrier bearing/spring paths.
    # These links do not have separate authored rocker animation, but both ends
    # remain explicitly attached to the levelled head rather than world space.
    for s in [-1,1]:
        for sx in [-1,1]:
            ob,ea,eb=_flex('copper_bypass_rocker_'+str(s)+'_'+str(sx),head,
                (sx*.018,s*.31,-.092),head,(sx*.173,s*.35,-.021),
                (0,s*.058,-.010),.0045,copper,ctrl,C,copper,True)
            shunts.append(ob.name);lug(ea);lug(eb)
    # Monitoring feeder follows the upper arm, then flexes into the levelled head.
    T('upper_frame_monitoring_pipe',[(-.13,-.155,-.026),(-.53,-.206,-.026),(-1.05,-.297,-.026)],.003,pa=up)
    for t in [.27,.55,.84]:
        x=-.13-.92*t;y=-.155-.142*t
        B('monitoring_pipe_saddle',(x,y,-.026),(.019,.022,.012),M['rubber'],up,.002)
        BT('pipe_saddle_screw',(x,y-.014,-.021),.004,.003,up)
    ob,ea,eb=_flex('monitoring_head_flex',up,(-1.05,-.297,-.026),head,(.036,0,-.116),(.06,-.06,-.018),.003,M['rubber'],ctrl,C)
    for e in [ea,eb]:
        CY('flex_airline_end_ferrule',(-.005,0,0),.0054,.013,nickel,e,'X',6)

    bpy.context.view_layer.update()
    objects=[o for o in C.objects if o.name.startswith(P)]
    for o in objects:
        o['reference_source']=SOURCE
        o['reference_status']='OEM construction-informed; undimensioned small hardware/routes approximated'
    # Camera positions are calculated from rig-local framing, useful in either car.
    old=float(ctrl['extension']);ctrl['extension']=1;ctrl.update_tag();bpy.context.view_layer.update()
    hp=head.matrix_world.translation.copy()
    cameras={
        'head_macro':{'location':list(hp+Vector((.98,-1.82,.83))),'target':list(hp+Vector((0,0,-.048))),'lens_mm':48,'extension':1},
        'head_underside':{'location':list(hp+Vector((.98,-1.45,-.28))),'target':list(hp+Vector((0,0,-.052))),'lens_mm':48,'extension':1},
        'base_macro':{'location':list(base.matrix_world@Vector((-.9,1.48,1.25))),'target':list(base.matrix_world@Vector((.15,0,.24))),'lens_mm':55,'extension':1},
    }
    ctrl['extension']=old;ctrl.update_tag();bpy.context.view_layer.update()
    return {'pantograph_microhardware':True,'objects':len(objects),'mesh_objects':sum(o.type=='MESH' for o in objects),
            'live_copper_shunts':shunts,'hook_deformed_meshes':[o.name for o in objects if o.type=='MESH' and o.get('flexible_joint')],
            'head_contact_plane_local_m':.032,'nominal_head_width_m':1.8,'strip_center_spacing_m':.390,
            'cameras':cameras,'source':SOURCE,'source_pages':[20,34,125],
            'scope':'OEM-informed small hardware; visual Hook deformation retains endpoints, not a cable dynamics/manufacturing model'}
