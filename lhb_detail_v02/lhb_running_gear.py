"""Detailed, original LHB FIAT running gear, CBC and underfloor authoring module.

SI metres; X longitudinal, Y lateral, Z above rail. Call:
    build_running_gear(None, root, body, collection, ac=True)
The API argument is reserved and ignored. Nothing resets the Blender scene.

Dimensional authority: Indian Railways Maintenance Manual of LHB Coaches,
chapter 4 pp 6–10, 19, 23–26; see running_gear_references.md. Fine geometry is
representative original modelling, not certified manufacturer CAD or kinematics.
"""
from math import pi, tau, sin, cos, sqrt
from mathutils import Vector
import bpy
import bmesh

DIMENSIONS = {
    'gauge_m': 1.676, 'wheel_back_to_back_m': 1.600,
    'new_wheel_tread_diameter_m': .915, 'wheel_axle_world_z_m': .4575,
    'bogie_wheelbase_m': 2.560, 'bogie_centres_m': 14.900,
    'brake_disc_diameter_m': .640, 'brake_disc_width_m': .110,
    'brake_discs_per_axle': 2, 'nominal_bogie_length_m': 3.534,
    'nominal_bogie_width_m': 3.030, 'coupling_anchor_span_m': 24.000,
    'coupling_anchor_world_z_m': 1.105,
}
SOURCE = 'Indian Railways LHB Maintenance Manual chapter 4; original representative fine geometry'


def _material(name, color, metallic=.0, roughness=.5, noise_scale=80.0, bump=.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if bump:
        tex = nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = noise_scale
        tex.inputs['Detail'].default_value = 3
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .18
        ramp.color_ramp.elements[0].color = tuple(v*.58 for v in color)+(1,)
        ramp.color_ramp.elements[1].position = .85
        ramp.color_ramp.elements[1].color = tuple(min(1,v*1.3) for v in color)+(1,)
        nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        b = nt.nodes.new('ShaderNodeBump')
        b.inputs['Strength'].default_value = .20
        b.inputs['Distance'].default_value = bump
        nt.links.new(tex.outputs['Fac'], b.inputs['Height'])
        nt.links.new(b.outputs['Normal'], bs.inputs['Normal'])
    return mat


class GearBuilder:
    """Direct data API geometry: reproducible, no context-sensitive operators."""
    def __init__(self, collection):
        self.collection = collection
        self.created = []
        self.m = {
            'paint': _material('LHB_GEAR_graphite_cast_steel', (.075,.085,.088), .68,.5,95,.0012),
            'edge': _material('LHB_GEAR_worn_steel_edges', (.25,.285,.29), .8,.31,110,.0003),
            'wheel': _material('LHB_GEAR_wheel_web_steel', (.095,.11,.115), .78,.47,75,.001),
            'tread': _material('LHB_GEAR_machined_rolling_bands', (.40,.46,.47), .95,.24,250,.00015),
            'disc': _material('LHB_GEAR_brake_disc_friction', (.32,.34,.34), .86,.34,180,.0002),
            'rubber': _material('LHB_GEAR_rubber_hoses', (.009,.012,.014), .03,.78,150,.0006),
            'spring': _material('LHB_GEAR_coil_spring_black', (.033,.042,.046), .55,.44,140,.0005),
            'silver': _material('LHB_GEAR_stainless_equipment', (.39,.435,.43), .76,.37,140,.00035),
            'cabinet': _material('LHB_GEAR_powder_coated_cabinets', (.28,.305,.30), .45,.55,100,.0006),
            'dark': _material('LHB_GEAR_recesses', (.018,.023,.025), .18,.71),
            'brass': _material('LHB_GEAR_pneumatic_brass', (.32,.23,.105), .74,.37),
            'red': _material('LHB_GEAR_BP_handle_red', (.38,.018,.011), .18,.49),
            'yellow': _material('LHB_GEAR_FP_handle_yellow', (.55,.33,.025), .18,.49),
            'ivory': _material('LHB_GEAR_plate_lettering', (.72,.73,.64), .12,.53),
        }

    def empty(self, name, parent, loc=(0,0,0), yaw=0):
        o = bpy.data.objects.new(name, None)
        self.collection.objects.link(o)
        o.parent=parent; o.location=loc; o.rotation_euler.z=yaw
        o.empty_display_type='PLAIN_AXES'; o.empty_display_size=.15
        self.created.append(o)
        return o

    def mesh(self, name, verts, faces, material, parent, bevel=0, smooth=False):
        me=bpy.data.meshes.new(name+'_mesh')
        me.from_pydata(verts, [], faces); me.update()
        bm=bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        ob=bpy.data.objects.new(name, me); self.collection.objects.link(ob)
        ob.parent=parent
        me.materials.append(self.m.get(material,material))
        if smooth:
            for p in me.polygons: p.use_smooth=True
        if bevel:
            m=ob.modifiers.new('Small fabricated edge radius','BEVEL')
            m.width=bevel; m.segments=2
            m=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
            m.keep_sharp=True; m.weight=40
        self.created.append(ob)
        return ob

    def box(self, name, loc, size, material, parent, bevel=.003):
        a,b,c=[d/2 for d in size]
        v=[(loc[0]+x*a,loc[1]+y*b,loc[2]+z*c) for x,y,z in
           [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
        return self.mesh(name,v,f,material,parent,bevel)

    def extrusion(self,name,outline,depth,axis,center,material,parent,bevel=0):
        # Outline coordinates are XY for Z extrusion, XZ for Y extrusion.
        verts=[]
        for d in [-depth/2,depth/2]:
            for u,v in outline:
                verts.append((u+center[0],d+center[1],v+center[2]) if axis=='Y'
                             else (u+center[0],v+center[1],d+center[2]))
        n=len(outline)
        return self.mesh(name,verts,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+
                         [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],material,parent,bevel)

    def rod(self,name,a,b,r,material,parent,n=16,r2=None,smooth=True):
        a,b=Vector(a),Vector(b); delta=b-a
        direction=delta.normalized()
        u=direction.cross(Vector((0,0,1)))
        if u.length<.1: u=direction.cross(Vector((0,1,0)))
        u.normalize(); v=direction.cross(u)
        radii=(r,r if r2 is None else r2)
        verts=[tuple(p+rr*(u*cos(tau*j/n)+v*sin(tau*j/n))) for p,rr in zip((a,b),radii) for j in range(n)]
        ob=self.mesh(name,verts,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+
                     [(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],material,parent,0,smooth)
        # End caps flat, cylindrical faces smooth.
        ob.data.polygons[0].use_smooth=False; ob.data.polygons[1].use_smooth=False
        return ob

    def tube(self,name,points,r,material,parent,sides=8):
        """Capped polygonal sweep, including genuine helical spring geometry."""
        pts=[Vector(p) for p in points]; verts=[]
        for i,p in enumerate(pts):
            tangent=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]
            tangent.normalize(); u=tangent.cross(Vector((0,0,1)))
            if u.length<.1: u=tangent.cross(Vector((0,1,0)))
            u.normalize(); v=tangent.cross(u)
            verts.extend(tuple(p+r*(u*cos(j*tau/sides)+v*sin(j*tau/sides))) for j in range(sides))
        fs=[tuple(range(sides-1,-1,-1)),tuple(range((len(pts)-1)*sides,len(pts)*sides))]
        for i in range(len(pts)-1):
            fs.extend((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for j in range(sides))
        return self.mesh(name,verts,fs,material,parent,smooth=True)

    def helix(self,name,center,radius,height,wire,turns,parent,phase=0):
        count=int(turns*28)
        pts=[]
        for i in range(count+1):
            t=i/count
            # Closed end coils with gradual rise retain a visible, honest helical shape.
            u=max(0,min(1,(t-.075)/.85))
            z=height*(u*u*(3-2*u)*.22+u*.78)
            pts.append((center[0]+radius*cos(t*tau*turns+phase),
                        center[1]+radius*sin(t*tau*turns+phase),center[2]+z))
        ob=self.tube(name,pts,wire,'spring',parent,10)
        ob['representation']='Original nested helical wire mesh; coil pitch and wire gauge representative'
        ob['coil_turns']=turns
        return ob

    def ring(self,name,center,major,minor,material,parent,axis='Z',n=40,m=8):
        pts=[]
        for i in range(n+1):
            a=tau*i/n
            pts.append((center[0]+major*cos(a),center[1]+major*sin(a),center[2]) if axis=='Z' else
                       (center[0]+major*cos(a),center[1],center[2]+major*sin(a)))
        return self.tube(name,pts,minor,material,parent,m)

    def lathe_y(self,name,profile,material,parent,segments=64,center=(0,0,0)):
        """Closed radial profile revolved around Y: profile contains (Y,radius)."""
        n=len(profile)
        verts=[(center[0]+r*cos(tau*j/segments),center[1]+y,center[2]+r*sin(tau*j/segments))
               for y,r in profile for j in range(segments)]
        fs=[]
        for i in range(n):
            k=(i+1)%n
            fs.extend((i*segments+j,i*segments+(j+1)%segments,k*segments+(j+1)%segments,k*segments+j) for j in range(segments))
        return self.mesh(name,verts,fs,material,parent,smooth=True)

    def bolts(self,name,points,normal,parent,r=.014,depth=.012,material='edge'):
        # One mesh per bolt set reduces object count while preserving actual hex heads.
        d=Vector(normal).normalized(); u=d.cross(Vector((0,0,1)))
        if u.length<.1:u=d.cross(Vector((0,1,0)))
        u.normalize(); v=d.cross(u); verts=[]; faces=[]
        for p in points:
            p=Vector(p); k=len(verts)
            for h in [0,depth]:
                verts.extend(tuple(p+d*h+r*(u*cos(tau*j/6)+v*sin(tau*j/6))) for j in range(6))
            faces += [tuple(k+j for j in range(5,-1,-1)),tuple(k+j for j in range(6,12))]
            faces += [(k+j,k+(j+1)%6,k+(j+1)%6+6,k+j+6) for j in range(6)]
        return self.mesh(name,verts,faces,material,parent,bevel=.001)

    def damper(self,name,a,b,parent,r=.043):
        a,b=Vector(a),Vector(b); d=b-a; direction=d.normalized()
        self.rod(name+'_oil_cylinder',a+d*.07,a+d*.68,r,'paint',parent,20)
        self.rod(name+'_polished_piston',a+d*.63,b-d*.09,r*.43,'tread',parent,16)
        self.rod(name+'_dust_seal',a+d*.62,a+d*.70,r*1.13,'rubber',parent,20)
        for p in (a,b):
            self.rod(name+'_eye_bush',p-Vector((0,.045,0)),p+Vector((0,.045,0)),r*1.13,'rubber',parent,16)
            self.rod(name+'_eye_pin',p-Vector((0,.052,0)),p+Vector((0,.052,0)),r*.5,'edge',parent,12)

    def label(self,name,string,loc,parent,size=.034,side=-1):
        d=bpy.data.curves.new(name,'FONT'); d.body=string; d.size=size; d.align_x='CENTER';d.extrude=.00005
        o=bpy.data.objects.new(name,d);self.collection.objects.link(o);o.parent=parent;o.location=loc
        o.rotation_euler=(pi/2,0,0 if side<0 else pi);d.materials.append(self.m['ivory']);self.created.append(o)
        return o


def _wheelset(g,bogie,label,x,z0):
    ax=g.empty('AXLE_'+label+'_PIVOT',bogie,(x,0,.4575-z0))
    ax['motion']='Rotate local Y; axle, wheels and disc rotors follow; axleboxes and calipers remain stationary'
    ax['rolling_radius_m']=.4575;ax['rotation_axis']='LOCAL_Y'
    g.rod('AXLE_'+label+'_forged_shaft',(0,-1.155,0),(0,1.155,0),.088,'edge',ax,40)
    for side in [-1,1]:
        # Inner wheel back face 0.800 m, flange root and conical tread are separate from dished web.
        prof=[(.800,.118),(.800,.340),(.800,.455),(.806,.479),(.816,.484),(.827,.472),
              (.838,.4570),(.924,.4527),(.936,.445),(.936,.370),(.918,.346),(.882,.318),
              (.866,.174),(.934,.146),(.955,.120),(.955,.089),(.817,.089)]
        prof=[(side*y,r) for y,r in prof]
        ob=g.lathe_y('WHEEL_'+label+('_L' if side>0 else '_R')+'_profiled_monobloc',prof,'wheel',ax,80)
        ob['diameter_at_nominal_tread_m']=.915;ob['wheel_back_to_back_m']=1.600
        band=[(side*y,r) for y,r in [(.808,.4795),(.816,.4845),(.827,.4725),(.838,.4575),(.924,.4532),(.936,.4455),(.932,.444),(.922,.4525),(.838,.4568),(.825,.471),(.814,.483),(.808,.478)]]
        g.lathe_y('WHEEL_'+label+'_bright_flange_and_tread',band,'tread',ax,80)
        g.rod('WHEEL_'+label+'_pressed_hub',(0,side*.887,0),(0,side*.984,0),.122,'edge',ax,36)
        g.ring('WHEEL_'+label+'_hub_fillet',(0,side*.935,0),.143,.008,'edge',ax,'Y')
        g.rod('WHEEL_'+label+'_oil_extraction_plug',(.105,side*.959,.067),(.105,side*.975,.067),.011,'brass',ax,6)
    for index,y in enumerate([-.41,.41],1):
        disc=g.empty('BRAKE_DISC_'+label+'_'+str(index)+'_ROTATING',ax)
        disc['outer_diameter_m']=.640;disc['width_m']=.110
        # Two friction cheeks enclose actual open radial cooling vanes.
        for s in [-1,1]:
            pr=[(y+s*.055,.142),(y+s*.055,.318),(y+s*.050,.320),(y+s*.035,.320),(y+s*.035,.146)]
            g.lathe_y('BRAKE_DISC_'+label+'_friction_cheek',pr,'disc',disc,64)
            g.ring('BRAKE_DISC_'+label+'_outer_wear_line',(0,y+s*.0557,0),.303,.0009,'edge',disc,'Y',64,6)
        g.rod('BRAKE_DISC_'+label+'_mount_hub',(0,y-.059,0),(0,y+.059,0),.148,'paint',disc,36)
        for j in range(24):
            a=tau*j/24; u=Vector((cos(a),0,sin(a)));v=Vector((-sin(a),0,cos(a)))
            verts=[tuple(u*rr+v*ww+Vector((0,yy,0))) for rr,ww,yy in
                   [(.15,-.007,y-.035),(.15,.007,y-.035),(.305,.007,y-.035),(.305,-.007,y-.035),
                    (.15,-.007,y+.035),(.15,.007,y+.035),(.305,.007,y+.035),(.305,-.007,y+.035)]]
            g.mesh('BRAKE_DISC_'+label+'_vent_vane',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'paint',disc)
        for s in [-1,1]:
            g.bolts('BRAKE_DISC_'+label+'_hub_bolts',[(.119*cos(tau*j/8),y+s*.062,.119*sin(tau*j/8)) for j in range(8)],(0,s,0),disc,.012,.009)
        # Caliper support and brake cylinder belong to bogie, not spinning wheelset.
        cal=g.empty('BRAKE_CALIPER_'+label+'_'+str(index)+'_FIXED',bogie,(x,y,.4575-z0))
        cal['motion']='Fixed to bogie frame; not a child of wheelset'
        for s in [-1,1]:
            g.box('BRAKE_CALIPER_'+label+'_friction_pad',(-.233,s*.076,.154),(.146,.026,.21),'dark',cal,.012)
            g.box('BRAKE_CALIPER_'+label+'_pad_holder',(-.239,s*.105,.155),(.18,.03,.24),'paint',cal,.014)
            g.rod('BRAKE_CALIPER_'+label+'_lever',(-.225,s*.105,.245),(-.048,s*.11,.388),.029,'paint',cal,12)
            g.bolts('BRAKE_CALIPER_'+label+'_holder_bolts',[(-.285,s*.124,.10),(-.285,s*.124,.213)],(0,s,0),cal,.013,.013)
        g.rod('BRAKE_CALIPER_'+label+'_bridge',(-.08,-.155,.358),(-.08,.155,.358),.039,'paint',cal,16)
        g.rod('BRAKE_CYLINDER_'+label,(-.095,-.165,.388),(-.095,.075,.388),.085,'paint',cal,32)
        g.rod('BRAKE_CYLINDER_'+label+'_piston',(-.095,.06,.388),(-.095,.19,.388),.025,'tread',cal,16)
        g.tube('BRAKE_CALIPER_'+label+'_supply_hose',[(-.10,-.16,.40),(-.12,-.21,.47),(-.40,-.25,.49),(-.55,-.25,.54)],.009,'rubber',cal)
    return ax


def _bogie(g,root,sign):
    label='FRONT' if sign>0 else 'REAR'; z0=.72
    bog=g.empty('BOGIE_'+label+'_PIVOT',root,(sign*7.450,0,z0))
    bog['motion']='Yaw local Z about bogie centre; all frame equipment and wheelsets follow'
    bog['source']=SOURCE;bog['wheelbase_m']=2.560;bog['suspension']='Conventional nested steel-coil FIAT, not air-spring variant'
    # Swept sideframe is deliberately thin enough to expose spring and control-arm hardware.
    # Coordinates below are world-height values minus bogie datum.
    top=[(-1.767,.905),(-1.62,.982),(-1.14,.982),(-.95,.916),(-.72,.717),(-.42,.688),(.42,.688),(.72,.717),(.95,.916),(1.14,.982),(1.62,.982),(1.767,.905)]
    lower=[(1.767,.764),(1.58,.770),(1.09,.775),(.87,.682),(.69,.510),(.42,.487),(-.42,.487),(-.69,.510),(-.87,.682),(-1.09,.775),(-1.58,.770),(-1.767,.764)]
    shape=[(x,z-z0) for x,z in top+lower]
    for s in [-1,1]:
        y=s*1.225
        frame=g.extrusion('FIAT_'+label+'_profiled_sideframe',shape,.225,'Y',(0,y,0),'paint',bog,.012)
        frame['representation']='Welded H-frame profile informed by manual Fig 4-2; plate details representative'
        for coords,suffix in [(top,'top'),(list(reversed(lower)),'bottom')]:
            g.tube('FIAT_'+label+'_'+suffix+'_weld_seam',[(x,y+s*.115,z-z0) for x,z in coords],.003,'edge',bog,6)
        for x in [-1.55,-.90,-.64,.64,.90,1.55]:
            z=.865 if abs(x)>1 else (.75 if abs(x)>.8 else .585)
            g.box('FIAT_'+label+'_web_stiffening_rib',(x,y+s*.12,z-z0),(.027,.027,.125),'edge',bog,.002)
        # One nested primary spring assembly and articulated bearing control arm per axle end.
        for x in [-1.28,1.28]:
            primary=g.empty('PRIMARY_'+label+('_A' if x<0 else '_B')+('_L' if s>0 else '_R'),bog,(x,y,.4575-z0))
            inward=1 if x<0 else -1
            arm=[(-.20,.075),(-.145,.135),(.14,.135),(.19,.066),(.19,-.100),(.095,-.157),(-.11,-.157),(-.20,-.09)]
            g.extrusion('AXLEBOX_'+label+'_control_arm_bearing_housing',arm,.27,'Y',(0,0,0),'paint',primary,.011)
            g.rod('AXLEBOX_'+label+'_bearing_outer_cover',(0,s*.132,0),(0,s*.177,0),.123,'paint',primary,40)
            g.rod('AXLEBOX_'+label+'_bearing_cover_rim',(0,s*.173,0),(0,s*.188,0),.129,'edge',primary,40)
            g.rod('AXLEBOX_'+label+'_bearing_cap',(0,s*.184,0),(0,s*.202,0),.112,'paint',primary,40)
            g.bolts('AXLEBOX_'+label+'_cover_screws',[(.086*cos(tau*j/6),s*.204,.086*sin(tau*j/6)) for j in range(6)],(0,s,0),primary,.012,.010)
            # Cast swing arm reaches inward to resilient pivot, below the dropped sideframe.
            armshape=[(0,.067),(inward*.24,.091),(inward*.55,.012),(inward*.59,-.05),(inward*.54,-.135),(inward*.20,-.105),(0,-.105)]
            g.extrusion('AXLEBOX_'+label+'_articulated_control_arm',armshape,.185,'Y',(0,0,0),'paint',primary,.014)
            g.rod('AXLEBOX_'+label+'_control_arm_resilient_joint',(inward*.54,-.15,-.06),(inward*.54,.15,-.06),.09,'rubber',primary,28)
            g.rod('AXLEBOX_'+label+'_control_arm_pin',(inward*.54,-.172,-.06),(inward*.54,.172,-.06),.031,'edge',primary,16)
            g.rod('PRIMARY_'+label+'_lower_spring_seat',(0,0,.132),(0,0,.158),.143,'edge',primary,36)
            g.rod('PRIMARY_'+label+'_upper_spring_seat',(0,0,.382),(0,0,.41),.143,'edge',primary,36)
            g.helix('PRIMARY_'+label+'_outer_helical_coil',(0,0,.181),.114,.182,.021,4.8,primary)
            g.helix('PRIMARY_'+label+'_inner_helical_coil',(0,0,.179),.069,.185,.015,6.0,primary,pi/2)
            g.rod('PRIMARY_'+label+'_central_bump_stop',(0,0,.158),(0,0,.212),.037,'rubber',primary,20)
            g.rod('PRIMARY_'+label+'_rubber_top_pad',(0,0,.410),(0,0,.429),.132,'rubber',primary,32)
            g.damper('PRIMARY_'+label+'_vertical_damper',(x-inward*.25,y+s*.14,.4675-z0),(x-inward*.25,y+s*.14,.916-z0),bog,.035)
            g.box('PRIMARY_'+label+'_damper_mount',(x-inward*.25,y+s*.08,.909-z0),(.085,.15,.08),'paint',bog,.006)
            g.tube('AXLEBOX_'+label+'_WSP_sensor_cable',[(x,y+s*.205,.4575-z0),(x+.075,y+s*.224,.60-z0),(x+.19,y+s*.211,.73-z0),(x+.20,y,.78-z0)],.008,'rubber',bog)
            g.rod('AXLEBOX_'+label+'_WSP_sensor',(0,s*.20,.025),(0,s*.243,.025),.029,'edge',primary,16)
            g.tube('AXLEBOX_'+label+'_earth_braid',[(x-.10,y+s*.17,.48-z0),(x-.16,y+s*.23,.57-z0),(x-.27,y+s*.16,.75-z0)],.009,'brass',bog,6)
        # Large nested secondary flexicoils outboard of centre and freely visible.
        sec=g.empty('SECONDARY_'+label+('_L' if s>0 else '_R'),bog,(0,s*1.225,.691-z0))
        g.rod('SECONDARY_'+label+'_base_seat',(0,0,-.035),(0,0,.006),.260,'paint',sec,48)
        g.rod('SECONDARY_'+label+'_lower_rubber_pad',(0,0,.006),(0,0,.027),.237,'rubber',sec,40)
        g.helix('SECONDARY_'+label+'_outer_flexicoil',(0,0,.060),.204,.240,.027,5.2,sec)
        g.helix('SECONDARY_'+label+'_inner_flexicoil',(0,0,.050),.125,.263,.020,6.5,sec,pi)
        g.rod('SECONDARY_'+label+'_upper_rubber_pad',(0,0,.335),(0,0,.354),.238,'rubber',sec,40)
        g.rod('SECONDARY_'+label+'_upper_seat',(0,0,.354),(0,0,.382),.255,'paint',sec,48)
        g.damper('SECONDARY_'+label+'_vertical_damper',(.40,s*1.235,.595-z0),(.40,s*1.235,1.076-z0),bog,.046)
        g.damper('YAW_'+label+'_longitudinal_damper',(-.73,s*1.423,.73-z0),(.50,s*1.423,.80-z0),bog,.049)
        # Safety cable and clamp have shape and clearance, not a straight placeholder cylinder.
        for xx in [-.33,.33]:
            g.tube('SECONDARY_'+label+'_safety_cable',[(xx,s*1.43,.68-z0),(xx+.018,s*1.45,.79-z0),(xx+.012,s*1.445,.93-z0),(xx,s*1.41,1.035-z0)],.013,'edge',bog)
            for zz in [.68,1.035]:
                g.box('SECONDARY_'+label+'_cable_anchor',(xx,s*1.41,zz-z0),(.076,.074,.048),'paint',bog,.006)
                g.bolts('SECONDARY_'+label+'_cable_anchor_bolt',[(xx,s*1.45,zz-z0)],(0,s,0),bog,.012,.010)
        g.bolts('FIAT_'+label+'_frame_bracket_bolts',[(x,s*1.352,z-z0) for x,z in [(-1.69,.854),(-.82,.748),(.82,.748),(1.69,.854)]],(0,s,0),bog,.015,.012)
    # Twin transverse members and lowered centre traction hardware.
    for x in [-.56,.56]:
        g.box('FIAT_'+label+'_transverse_boxbeam',(x,0,.625-z0),(.24,2.56,.195),'paint',bog,.013)
        for y in [-.8,-.42,.42,.8]:
            g.box('FIAT_'+label+'_brake_unit_hanger',(x,y,.714-z0),(.31,.095,.135),'paint',bog,.009)
    bolster=g.empty('BOLSTER_'+label+'_BEAM',bog)
    g.box('BOLSTER_'+label+'_central_beam',(0,0,1.031-z0),(.39,2.35,.145),'paint',bolster,.014)
    for y in [-.82,.82]:g.box('BOLSTER_'+label+'_body_support',(0,y,1.095-z0),(.39,.31,.08),'edge',bolster,.009)
    g.rod('TRACTION_'+label+'_centre_pin',(0,0,.50-z0),(0,0,1.052-z0),.083,'paint',bog,28)
    g.box('TRACTION_'+label+'_rocker_lever',(0,0,.535-z0),(.21,.65,.09),'paint',bog,.018)
    for s in [-1,1]:
        g.rod('TRACTION_'+label+'_rod',(0,s*.29,.55-z0),(s*.57,s*.51,.62-z0),.037,'paint',bog,20)
    g.damper('LATERAL_'+label+'_damper',(-.21,-.43,.81-z0),(-.21,.44,.83-z0),bog,.040)
    for s in [-1,1]:
        g.box('BUMPSTOP_'+label+'_longitudinal',(s*.265,0,.805-z0),(.11,.24,.115),'rubber',bog,.015)
        g.box('BUMPSTOP_'+label+'_lateral',(0,s*.275,.805-z0),(.25,.10,.115),'rubber',bog,.015)
        g.box('BUMPSTOP_'+label+'_support_bracket',(s*.337,0,.759-z0),(.035,.42,.20),'paint',bog,.006)
    g.rod('ANTIROLL_'+label+'_torsion_bar',(.32,-1.15,.965-z0),(.32,1.15,.965-z0),.037,'edge',bog,20)
    for s in [-1,1]:
        g.rod('ANTIROLL_'+label+'_drop_link',(.32,s*1.15,.963-z0),(.66,s*1.15,.69-z0),.027,'paint',bog,16)
    # Compressed air distribution with unions and flexible axle feeds.
    for y in [-.70,.70]:
        g.tube('FIAT_'+label+'_brake_pipe',[(-1.01,y,.84-z0),(-.63,y,.77-z0),(.63,y,.77-z0),(1.01,y,.84-z0)],.010,'edge',bog)
        for x in [-.54,.54]:
            g.rod('FIAT_'+label+'_brake_union',(x-.024,y,.77-z0),(x+.024,y,.77-z0),.019,'brass',bog,6)
    axles=[_wheelset(g,bog,label+('_A' if x<0 else '_B'),x,z0) for x in [-1.28,1.28]]
    return bog,axles


def _cbc(g,root,body,sign):
    label='FRONT' if sign>0 else 'REAR'
    anchor=g.empty('COUPLING_'+label,root,(sign*12,0,1.105),0 if sign>0 else pi)
    anchor['mating_plane']=True;anchor['forward_axis']='+X';anchor['span_m']=24.0
    anchor['compatibility']='Shared legacy ICF visual mating datum and contact profile only; not a certified mechanism or WAP7 validation'
    gear=g.empty('CBC_'+label+'_DRAW_GEAR',anchor)
    g.box('CBC_'+label+'_draft_pocket',(-.875,0,.005),(.79,.48,.36),'paint',gear,.016)
    for y in [-.268,.268]:
        g.box('CBC_'+label+'_pocket_longitudinal_flange',(-.87,y,-.135),(.83,.065,.065),'edge',gear,.004)
        g.bolts('CBC_'+label+'_pocket_fixing_bolts',[(-1.18,y,-.177),(-.97,y,-.177),(-.72,y,-.177),(-.50,y,-.177)],(0,0,-1),gear,.021,.018)
    g.box('CBC_'+label+'_draft_elastomer',(-.675,0,0),(.22,.30,.265),'rubber',gear,.023)
    for x in [-.76,-.70,-.64,-.58]:g.box('CBC_'+label+'_draft_pack_separator',(x,0,0),(.018,.32,.275),'edge',gear,.003)
    g.box('CBC_'+label+'_forged_tapered_shank',(-.385,0,0),(.46,.187,.171),'paint',gear,.019)
    # Legacy complementary contact envelope intentionally has NO outward bevel.
    outline=[(-.30,-.10),(-.23,-.18),(-.08,-.18),(-.08,-.045),(.08,.045),(.08,.18),(-.15,.18),(-.30,.10)]
    head=g.extrusion('CBC_'+label+'_HEAD_MATING_PROFILE',outline,.230,'Z',(0,0,0),'paint',gear)
    head['contact_profile']='Exact legacy ICF complementary XY contact envelope; no modifier growth'
    # Collar, moulded root, independent lock block and a separate vertical knuckle pin.
    g.extrusion('CBC_'+label+'_cast_neck_collar',[(-.43,-.112),(-.30,-.147),(-.235,-.147),(-.235,.147),(-.30,.147),(-.43,.112)],.263,'Z',(0,0,0),'paint',gear,.006)
    g.rod('CBC_'+label+'_knuckle_pivot_pin',(-.16,.085,-.133),(-.16,.085,.146),.026,'edge',gear,24)
    g.rod('CBC_'+label+'_knuckle_pin_head',(-.16,.085,.144),(-.16,.085,.154),.036,'paint',gear,24)
    g.rod('CBC_'+label+'_cotter_pin',(-.197,.085,.157),(-.12,.085,.157),.005,'edge',gear,8)
    g.box('CBC_'+label+'_lock_block',(-.208,.042,-.144),(.084,.075,.053),'edge',gear,.005)
    g.tube('CBC_'+label+'_knuckle_cast_seam',[(-.20,.173,.116),(-.08,.173,.116),(.04,.173,.116)],.0017,'edge',gear,6)
    g.box('CBC_'+label+'_striker_carrier',(-.402,0,-.183),(.16,.35,.085),'paint',gear,.008)
    for y in [-.145,.145]:g.rod('CBC_'+label+'_carrier_guide',(-.41,y,-.14),(-.41,y,.15),.026,'edge',gear,16)
    # Accessible operating lever: all components clear the front mating envelope.
    g.rod('CBC_'+label+'_uncoupling_operating_rod',(-.29,-.14,-.15),(-.38,-.88,-.15),.012,'edge',gear,12)
    g.tube('CBC_'+label+'_uncoupling_handle',[(-.38,-.88,-.15),(-.43,-.95,-.11),(-.49,-.96,.05)],.014,'edge',gear,12)
    g.ring('CBC_'+label+'_lock_lift_eye',(-.24,-.10,-.147),.024,.006,'edge',gear,'Y',20,6)
    # Two distinct pneumatic systems with angle cocks and curved rubber hoses.
    for y,kind,color in [(-.46,'BRAKE_PIPE','red'),(.46,'FEED_PIPE','yellow')]:
        hose=g.empty(kind+'_'+label+'_CONNECTION',anchor)
        g.rod(kind+'_'+label+'_fixed_riser',(-.53,y,-.12),(-.30,y,-.12),.023,'edge',hose,16)
        g.rod(kind+'_'+label+'_angle_cock',(-.31,y,-.12),(-.24,y,-.12),.037,'brass',hose,8)
        g.rod(kind+'_'+label+'_cock_stem',(-.27,y,-.11),(-.27,y,-.045),.011,'brass',hose,12)
        g.box(kind+'_'+label+'_cock_handle',(-.23,y,-.027),(.11,.027,.02),color,hose,.005)
        g.tube(kind+'_'+label+'_curved_flexible_hose',[(-.24,y,-.12),(-.18,y,-.21),(-.13,y,-.36),(-.15,y,-.47),(-.24,y,-.51),(-.33,y,-.455)],.027,'rubber',hose,12)
        for x,z in [(-.237,-.145),(-.320,-.468)]:
            g.ring(kind+'_'+label+'_hose_ferrule',(x,y,z),.03,.005,'edge',hose,'Y',20,6)
        g.box(kind+'_'+label+'_gladhand_head',(-.34,y,-.43),(.068,.061,.092),'edge',hose,.008)
        g.rod(kind+'_'+label+'_gladhand_seal',(-.304,y,-.42),(-.294,y,-.42),.028,'rubber',hose,16)
    # High-voltage jumper terminals, coiled slack cable and protective moulded sockets.
    for y in [-.80,.80]:
        elec=g.empty('EOG_'+label+'_JUMPER',anchor)
        g.box('EOG_'+label+'_junction_box',(-.49,y,.005),(.17,.18,.25),'cabinet',elec,.012)
        g.rod('EOG_'+label+'_socket',(-.39,y,-.02),(-.34,y,-.02),.058,'rubber',elec,24)
        g.rod('EOG_'+label+'_socket_cap',(-.35,y,-.02),(-.33,y,-.02),.062,'paint',elec,24)
        g.tube('EOG_'+label+'_jumper_slack',[(-.36,y,-.08),(-.29,y,-.20),(-.28,y,-.41),(-.40,y,-.51),(-.52,y,-.45),(-.56,y,-.31)],.024,'rubber',elec,12)
        g.rod('EOG_'+label+'_cable_gland',(-.36,y,-.05),(-.36,y,-.125),.036,'edge',elec,16)
    return anchor


def _cabinet(g,parent,name,x,y,z,size,label,vent=True):
    w,d,h=size; group=g.empty(name,parent,(x,y,z))
    group['representation']='Representative enclosure arrangement; not a coach-specific equipment schedule'
    g.box(name+'_sealed_case',(0,0,0),size,'cabinet',group,.014)
    s=-1 if y<0 else 1
    front=s*(d/2+.006)
    # Paired removable doors with separate gaskets, recessed panels, hinges and latches.
    for j in [-1,1]:
        xx=j*w*.243
        g.box(name+'_door_seal',(xx,front,0),(w*.467,.015,h*.87),'rubber',group,.008)
        g.box(name+'_door_skin',(xx,front+s*.010,0),(w*.447,.013,h*.835),'cabinet',group,.008)
        for zz in [-h*.26,h*.26]:
            g.rod(name+'_door_hinge',(xx-j*w*.203,front+s*.019,zz-.038),(xx-j*w*.203,front+s*.019,zz+.038),.012,'edge',group,12)
        g.box(name+'_quarter_turn_latch',(xx+j*w*.155,front+s*.020,0),(.035,.017,.069),'edge',group,.004)
        g.rod(name+'_latch_keyway',(xx+j*w*.155,front+s*.03,-.01),(xx+j*w*.155,front+s*.042,-.01),.008,'dark',group,8)
        if vent:
            g.box(name+'_vent_aperture',(xx,front+s*.019,-h*.03),(w*.31,.006,h*.40),'dark',group,.003)
            for k in range(7):
                ob=g.box(name+'_pressed_louvre',(xx,front+s*.032,-h*.20+k*h*.056),(w*.312,.033,.012),'edge',group,.002)
                # Raised leading edge and dark gaps read as individual folded vanes.
        g.bolts(name+'_door_fasteners',[(xx+dx*w*.20,front+s*.025,zz*h*.38) for dx in [-1,1] for zz in [-1,1]],(0,s,0),group,.008,.006)
    for xx in [-w*.39,w*.39]:
        g.box(name+'_suspension_bracket',(xx,0,h/2+.11),(.067,d+.12,.24),'edge',group,.004)
        for sy in [-1,1]:g.bolts(name+'_hanger_bolt',[(xx,sy*(d/2+.07),h/2+.10)],(0,sy,0),group,.016,.011)
    g.box(name+'_service_plate',(0,front+s*.028,h*.28),(min(.28,w*.22),.008,.058),'dark',group,.002)
    g.label(name+'_service_stencil',label,(0,front+s*.034,h*.265),group,min(.025,w*.02),s)
    for xx in [-w*.20,w*.20]:
        g.rod(name+'_cable_gland',(xx,-s*d*.22,-h*.51),(xx,-s*d*.22,-h*.61),.020,'rubber',group,16)
    return group


def _tank(g,parent,name,x,y,z,length,radius,material='silver'):
    tank=g.empty(name,parent,(x,y,z));tank['representation']='Representative vessel, brackets and service fittings'
    g.rod(name+'_cylindrical_shell',(-length/2,0,0),(length/2,0,0),radius,material,tank,48)
    # Dished ends represented by several concentric frusta, avoiding sphere-like inflated tanks.
    for sign in [-1,1]:
        for i in range(4):
            ra=radius*sqrt(max(0,1-(i/4)**2));rb=radius*sqrt(max(.001,1-((i+1)/4)**2))
            g.rod(name+'_dished_head',(sign*(length/2+radius*.23*i/4),0,0),(sign*(length/2+radius*.23*(i+1)/4),0,0),ra,material,tank,48,rb)
        g.rod(name+'_end_union',(sign*(length/2+radius*.21),0,0),(sign*(length/2+radius*.36),0,0),.026,'brass',tank,6)
    for xx in [-length*.32,length*.32]:
        pts=[(xx,radius*1.015*cos(tau*j/40),radius*1.015*sin(tau*j/40)) for j in range(41)]
        g.tube(name+'_retaining_strap',pts,.012,'paint',tank,8)
        g.box(name+'_cradle',(xx,0,radius+.07),(.077,radius*2+.09,.065),'paint',tank,.008)
        for sy in [-1,1]:
            g.rod(name+'_strap_tension_rod',(xx,sy*(radius+.025),-.045),(xx,sy*(radius+.025),radius+.13),.008,'edge',tank,8)
            g.bolts(name+'_strap_nut',[(xx,sy*(radius+.025),radius+.13)],(0,0,1),tank,.013,.010)
    g.rod(name+'_drain_valve',(0,0,-radius),(0,0,-radius-.065),.018,'brass',tank,8)
    return tank


def _underfloor(g,body,ac):
    equip=g.empty('UNDERFLOOR_EQUIPMENT_FIXED',body)
    equip['layout']='Representative EOG electrical and pneumatic equipment; AC/non-AC enclosure distinction'
    # Longitudinal structural members and open crossmembers remain visually distinct from equipment.
    for y in [-1.30,1.30]:
        g.box('UNDERFRAME_longitudinal_lower_flange',(0,y,1.037),(22.80,.15,.027),'edge',equip,.003)
    for x in [-5.30,-4.55,-2.5,0,2.5,4.55,5.30]:
        g.box('UNDERFRAME_visible_transverse_beam',(x,0,1.047),(.086,2.65,.10),'paint',equip,.004)
        for y in [-1.18,1.18]:g.bolts('UNDERFRAME_crossmember_flange_bolts',[(x,y,1.105)],(0,0,1),equip,.015,.01)
    boxes=[_cabinet(g,equip,'BATTERY_BOX',-3.92,-.75,.710,(1.86,.92,.49),'BATTERY'),
           _cabinet(g,equip,'BRAKE_CONTROL_CONTAINER',1.65,-.79,.740,(1.35,.86,.43),'AIR BRAKE'),
           _cabinet(g,equip,'LOW_VOLTAGE_DISTRIBUTION',3.90,-.86,.790,(1.17,.71,.35),'110 V DC',False)]
    if ac:
        boxes.append(_cabinet(g,equip,'EOG_TRANSFORMER',-1.09,-.69,.682,(1.70,1.04,.54),'750 / 415 V'))
        # Cooling fins, resilient feet and isolated terminal housings.
        for j in range(13):
            g.box('EOG_TRANSFORMER_cooling_fin',(-1.82+j*.123,-1.231,.67),(.027,.12,.42),'edge',equip,.004)
        boxes.append(_cabinet(g,equip,'AC_AUXILIARY_CONVERTER',4.20,.66,.77,(1.57,.92,.37),'AUX CONVERTER'))
    else:
        boxes.append(_cabinet(g,equip,'NONAC_CONTROL_BOX',-.72,-.78,.825,(1.17,.77,.28),'CONTROL'))
    _tank(g,equip,'MAIN_AIR_RESERVOIR',-2.55,.80,.687,1.12,.180,'paint')
    _tank(g,equip,'AUXILIARY_AIR_RESERVOIR',-.80,.80,.726,.91,.148,'paint')
    _tank(g,equip,'FRESH_WATER_TANK',1.30,.63,.69,1.85,.243,'silver')
    # Separate valve panel and manifold instead of anonymous cylinders.
    panel=g.empty('PNEUMATIC_SERVICE_MANIFOLD',equip,(.15,-1.04,.89))
    g.box('PNEUMATIC_manifold_mount',(0,0,0),(.57,.075,.20),'paint',panel,.005)
    for i in range(4):
        x=-.22+i*.147
        g.rod('PNEUMATIC_service_union',(x,-.05,-.07),(x,-.05,-.16),.020,'brass',panel,6)
        g.rod('PNEUMATIC_isolating_stem',(x,-.04,.015),(x,-.10,.015),.012,'brass',panel,12)
        g.box('PNEUMATIC_isolating_handle',(x,-.113,.024),(.072,.014,.018),'yellow' if i%2 else 'red',panel,.003)
    for y in [-.23,.23]:
        g.tube('UNDERFLOOR_BP_FP_longitudinal_pipe',[(-11.48,y,1.01),(-9.55,y,1.01),(-9.33,y,.953),(-5.5,y,.953),(5.5,y,.953),(9.33,y,.953),(9.55,y,1.01),(11.48,y,1.01)],.013,'edge',equip,10)
        for x in [-5.0,-3.0,-1.0,1.0,3.0,5.0]:
            g.box('UNDERFLOOR_pipe_clamp',(x,y,.971),(.035,.07,.058),'paint',equip,.003)
            g.bolts('UNDERFLOOR_pipe_clamp_bolt',[(x,y,.999)],(0,0,1),equip,.009,.007)
    g.tube('UNDERFLOOR_insulated_cable_trunk',[(-5.3,-.34,1.024),(-4.9,-.34,1.024),(4.85,-.34,1.024),(5.3,-.42,1.024)],.032,'rubber',equip,12)
    for x in [-4.60,-3.7,-1.7,1.3,3.9]:
        g.tube('UNDERFLOOR_equipment_drop_cable',[(x,-.34,1.024),(x,-.41,.92),(x+.14,-.49,.85),(x+.21,-.59,.85)],.016,'rubber',equip,8)
    for end in [-1,1]:
        for side in [-1,1]:
            # Toilet holding tank boxes deliberately leave coupler centre clear.
            bio=g.empty('BIO_TANK_'+str(end)+'_'+str(side),equip,(end*10.40,side*.91,.73))
            g.box('BIO_TANK_stainless_chamber',(0,0,0),(1.34,.67,.41),'silver',bio,.022)
            for xx in [-.48,.48]:g.box('BIO_TANK_hanger',(xx,0,.215),(.065,.81,.072),'paint',bio,.004)
            g.box('BIO_TANK_removable_access_lid',(0,side*.341,0),(1.15,.016,.27),'cabinet',bio,.008)
            g.bolts('BIO_TANK_lid_bolts',[(x,side*.353,z) for x in [-.49,0,.49] for z in [-.103,.103]],(0,side,0),bio,.009,.007)
            g.rod('BIO_TANK_drain_outlet',(-end*.48,0,-.17),(-end*.48,0,-.28),.038,'paint',bio,16)
    return equip,boxes


def build_running_gear(api,root,body,collection,ac=True):
    """Build into collection, preserving the caller's scene and body geometry.

    Returns Blender object lists plus dimension/provenance data. Parent transforms
    should be identity at build time. Fixed underfloor equipment inherits body;
    bogies and coupling anchors inherit root. Each wheelset rotates on local Y.
    """
    g=GearBuilder(collection)
    bogies=[];wheelsets=[]
    for sign in [1,-1]:
        b,a=_bogie(g,root,sign);bogies.append(b);wheelsets.extend(a)
    couplers=[_cbc(g,root,body,sign) for sign in [1,-1]]
    underfloor,cabinets=_underfloor(g,body,bool(ac))
    root['running_gear_revision']='LHB detailed v02 conventional coil FIAT'
    root['running_gear_provenance']=SOURCE
    root['fine_equipment_geometry']='Representative interpretation; known datums listed separately'
    return {'bogies':bogies,'wheelsets':wheelsets,'couplers':couplers,
            'underfloor':underfloor,'cabinets':cabinets,'objects':g.created,
            'dimensions':dict(DIMENSIONS),
            'notes':['Two 640 mm x 110 mm discs per axle, fixed calipers',
                     'Nested primary and secondary coil meshes',
                     'CBC legacy ICF visual contact envelope only; no certified mechanism claim']}
