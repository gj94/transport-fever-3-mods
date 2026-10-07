"""Prototype-length Vande Bharat 2.0 passenger interior.

All dimensions are metres. Editable real geometry, original procedural materials,
no reference photographs or external texture dependencies. Public entry: apply(ctx).
CC/EC detailed seat meshes are linked at the shared prototype-layout PAX anchors.
"""
import bpy
import math
from math import sin, cos, pi, tau
from mathutils import Vector, Matrix
from common import mesh, remove_prefix
from interior_layout import layout_for

PREFIX = 'VB02_INT_'
# Exact visual mesh ownership list. Never touch Saloon_floor, window glazing,
# exterior door leaves, DRIVER/PAX empties, or any other rig object.
REPLACED = (
    'CC_seating', 'EC_seating', 'Seat_headrest_covers', 'Seat_armrests',
    'Seat_armrest_posts', 'Seat_pedestals', 'Seat_mounts', 'Seat_back_trays',
    'Seat_back_pockets', 'Luggage_rack_edge', 'Luggage_rack_shelf', 'Rack_brackets',
    'Ceiling_LED', 'Reading_lights', 'HVAC_interior_vents', 'Saloon_bulkheads',
    'Bulkhead_lintel', 'Sliding_saloon_frame', 'Saloon_door_glass',
    'Info_screen_frame', 'Info_screen', 'Service_cabin', 'Service_door_handle',
    'Pantry_counter', 'Pantry_worktop', 'Pantry_drawer_front', 'Curved_ceiling_inner',
    'Window_roller_blinds',
)


def material(name, rgb, rough=.45, metallic=0, transmission=0, emission=0):
    name = PREFIX + name
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1)
    m.node_tree.nodes.clear()
    out = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    p = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.46
    if emission:
        p.inputs['Emission Color'].default_value = (*rgb, 1)
        p.inputs['Emission Strength'].default_value = emission
    m.node_tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return m


def cloth(name, rgb, ec=False):
    m = material(name, rgb, .89)
    n, l = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    p.inputs['Sheen Weight'].default_value = .07
    p.inputs['Sheen Roughness'].default_value = .55
    p.inputs['Specular IOR Level'].default_value = .22
    tc=n.new('ShaderNodeTexCoord');tc.label='Metre-scaled upholstery coordinates'
    sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0])
    def op(kind,a,b=None,label=None):
        q=n.new('ShaderNodeMath');q.operation=kind
        if label:q.label=label
        for i,v in enumerate([a,b]):
            if v is None:continue
            if isinstance(v,(float,int)):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    # Two perpendicular, submillimetre yarn families. The diagonal X+Z
    # projection keeps the same physical thread scale on cushion and back.
    u=sep.outputs['Y'];v=op('ADD',sep.outputs['X'],sep.outputs['Z'])
    warp=op('POWER',op('ABSOLUTE',op('SINE',op('MULTIPLY',u,2*pi/0.00072))),5)
    weft=op('POWER',op('ABSOLUTE',op('SINE',op('MULTIPLY',v,2*pi/0.00081))),5)
    weave=op('ADD',op('MULTIPLY',warp,.52),op('MULTIPLY',weft,.48),'Warp and weft')
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=870
    noise.inputs['Detail'].default_value=2.0;l.new(tc.outputs['Object'],noise.inputs['Vector'])
    height=op('ADD',op('MULTIPLY',weave,.82),op('MULTIPLY',noise.outputs['Fac'],.18))
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.00007;bump.label='Subtle 0.07 mm woven relief'
    l.new(height,bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    l.new(op('ADD',.82,op('MULTIPLY',height,.12)),p.inputs['Roughness'])
    if not ec:
        # Small, mostly regular pale yarn flecks sit above the fine weave;
        # they are the upholstery motif, not coarse pebbled plastic relief.
        du=op('SUBTRACT',op('FRACT',op('MULTIPLY',u,65)),.5)
        dv=op('SUBTRACT',op('FRACT',op('MULTIPLY',v,65)),.5)
        dot=op('LESS_THAN',op('ADD',op('MULTIPLY',du,du),op('MULTIPLY',dv,dv)),.007)
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*rgb,1)
        mix.inputs[2].default_value=(.072,.115,.30,1);l.new(op('MULTIPLY',dot,.68),mix.inputs[0])
        modulation=n.new('ShaderNodeMixRGB');modulation.blend_type='MULTIPLY'
        modulation.inputs[0].default_value=.12;l.new(mix.outputs[0],modulation.inputs[1])
        l.new(op('ADD',.64,op('MULTIPLY',height,.36)),modulation.inputs[2])
        l.new(modulation.outputs[0],p.inputs['Base Color'])
    else:
        # Original broken zigzag jacquard; not a photographic replica.
        sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0])
        def op(kind, a, b=None):
            q=n.new('ShaderNodeMath');q.operation=kind
            for i,v in enumerate([a,b]):
                if v is None:continue
                if isinstance(v,(int,float)):q.inputs[i].default_value=v
                else:l.new(v,q.inputs[i])
            return q.outputs[0]
        zz=op('MULTIPLY',sep.outputs['Z'],42)
        jag=op('PINGPONG',zz,1)
        yy=op('MULTIPLY',sep.outputs['Y'],12)
        phase=op('ADD',yy,op('MULTIPLY',jag,.24))
        stripe=op('LESS_THAN',op('ABSOLUTE',op('SUBTRACT',op('FRACT',phase),.5)),.055)
        broken=op('GREATER_THAN',op('FRACT',op('MULTIPLY',sep.outputs['Z'],11)),.19)
        mask=op('MULTIPLY',stripe,broken)
        col=n.new('ShaderNodeValToRGB');col.color_ramp.interpolation='CONSTANT'
        colors=[(.14,.34,.13,1),(.5,.36,.07,1),(.42,.14,.23,1),(.19,.19,.45,1),(.035,.04,.045,1)]
        for e in list(col.color_ramp.elements)[1:]:col.color_ramp.elements.remove(e)
        col.color_ramp.elements[0].color=colors[0]
        for i,c in enumerate(colors[1:],1):col.color_ramp.elements.new(i/len(colors)).color=c
        l.new(op('FRACT',op('MULTIPLY',sep.outputs['Y'],2.2)),col.inputs['Fac'])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(*rgb,1)
        l.new(mask,mix.inputs[0]);l.new(col.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    return m


def materials(ctx):
    m = dict(ctx['materials'])
    m.update({
        'cc':cloth('Royal_blue_speckled_CC',(.012,.024,.16)),
        'ec':cloth('Charcoal_jacquard_EC',(.055,.064,.078),True),
        'cover':cloth('Powder_blue_headrest_linen',(.22,.45,.61)),
        'seam_cc':material('Blue_piping',(.025,.073,.28),.88),
        'seam_ec':material('Graphite_piping',(.065,.079,.093),.86),
        'thread_cc':material('Blue_sewing_thread',(.055,.095,.24),.91),
        'thread_ec':material('Graphite_sewing_thread',(.11,.13,.15),.91),
        'shell':material('Warm_grey_moulded_seat_shell',(.49,.52,.51),.43),
        'lining':material('Ivory_laminate',(.76,.77,.71),.42),
        'trim':material('Anodized_satin_aluminium',(.52,.59,.62),.27,.73),
        'chrome':material('Polished_stainless',(.57,.66,.69),.17,.95),
        'rubber_int':material('Graphite_elastomer',(.014,.019,.025),.75),
        'grey':material('Panel_recess_grey',(.15,.18,.19),.54),
        'blind':material('Blue_grey_roller_fabric',(.16,.24,.31),.82),
        'aqua':material('Frosted_aqua_rack_shelf',(.38,.64,.64),.26,0,.42),
        'rack_pattern':material('Etched_rack_chevrons',(.21,.37,.38),.66),
        'led':material('Diffused_daylight_LED',(.86,.95,1),.35,0,0,3),
        'green_led':material('Green_PIS_letters',(.15,.85,.17),.37,0,0,2),
        'label':material('Navy_information_label',(.025,.065,.12),.45),
        'label_white':material('White_print_and_ceramic',(.89,.91,.87),.4),
        'red_int':material('Safety_red',(.53,.028,.024),.4),
        'black_int':material('Dark_pocket_net',(.007,.012,.016),.8),
        'glass_int':material('Clear_saloon_toughened_glass',(.79,.89,.91),.085,0,.98),
        'frit':material('Saloon_glass_safety_frit',(.72,.79,.79),.41),
        'mirror':material('Washroom_mirror',(.87,.91,.91),.055,1),
        'floor_int':material('Speckled_non_slip_vinyl',(.29,.30,.30),.8),
    })
    # Vinyl has subtle granular, scaled-in-metres nonslip texture.
    n=m['floor_int'].node_tree.nodes;l=m['floor_int'].node_tree.links
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=320
    p=n.get('Principled BSDF');b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.0007;b.inputs['Strength'].default_value=.16
    l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    return m


class Batch:
    """Batch by named physical assembly and material; no per-fastener modifiers."""
    def __init__(self,ctx,m):
        self.ctx=ctx;self.m=m;self.groups={};self.pose=None
    def pt(self,p):
        if self.pose is None:return tuple(p)
        x,y,f=self.pose
        return (x+f*p[0],y+f*p[1],p[2])
    def add(self,name,verts,faces,ma,smooth=False,parent=None):
        par=parent or self.ctx['body'];key=(name,ma,par.name)
        if key not in self.groups:self.groups[key]=[[],[],[],par]
        vv,ff,ss,_=self.groups[key];offset=len(vv)
        vv.extend(self.pt(p) for p in verts)
        ff.extend(tuple(offset+i for i in f) for f in faces)
        ss.extend([smooth]*len(faces))
    def box(self,n,c,d,ma,parent=None):
        v=[(c[0]+x*d[0]/2,c[1]+y*d[1]/2,c[2]+z*d[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.add(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,parent=parent)
    def rounded(self,n,c,d,ma,r=.025,axis='Z',parent=None):
        # Rounded rectangle extrusion with eased end rings and baked topology.
        idx={'X':(1,2,0),'Y':(0,2,1),'Z':(0,1,2)}[axis]
        a,b,h=[d[i] for i in idx];r=min(r,a*.47,b*.47,h*.47)
        vs=[]
        for z,shrink in [(-h/2,r*.42),(-h/2+r*.48,0),(h/2-r*.48,0),(h/2,r*.42)]:
            aa=a/2-shrink;bb=b/2-shrink;rr=max(.001,r-shrink)
            for sx,sy,base in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
                for j in range(5):
                    an=math.radians(base+j*22.5)
                    q=[0,0,0];q[idx[0]]=sx*(aa-rr)+rr*cos(an);q[idx[1]]=sy*(bb-rr)+rr*sin(an);q[idx[2]]=z
                    vs.append(tuple(c[k]+q[k] for k in range(3)))
        fs=[tuple(reversed(range(20))),tuple(range(60,80))]
        fs += [(20*k+j,20*k+(j+1)%20,20*(k+1)+(j+1)%20,20*(k+1)+j) for k in range(3) for j in range(20)]
        self.add(n,vs,fs,ma,True,parent)
    def loft(self,n,sections,ma,N=24):
        # Sections: (height, x centre, depth, width), smoothly rounded upholstery.
        vs=[]
        for z,x,d,w in sections:
            for j in range(N):
                a=tau*j/N
                def ss(v):return math.copysign(abs(v)**.42,v)
                vs.append((x+d/2*ss(cos(a)),w/2*ss(sin(a)),z))
        fs=[tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))]
        fs += [(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(len(sections)-1) for j in range(N)]
        self.add(n,vs,fs,ma,True)
    def tube(self,n,pts,r,ma,N=10,parent=None,closed=False):
        pts=[Vector(p) for p in pts];vs=[];L=len(pts)
        for i,p in enumerate(pts):
            prev=pts[(i-1)%L] if closed else pts[max(0,i-1)]
            nxt=pts[(i+1)%L] if closed else pts[min(L-1,i+1)]
            q=(nxt-prev).normalized().to_track_quat('Z','Y')
            vs.extend(tuple(p+q@Vector((r*cos(tau*j/N),r*sin(tau*j/N),0))) for j in range(N))
        fs=[] if closed else [tuple(reversed(range(N))),tuple(range((L-1)*N,L*N))]
        fs += [(k*N+j,k*N+(j+1)%N,((k+1)%L)*N+(j+1)%N,((k+1)%L)*N+j) for k in range(L if closed else L-1) for j in range(N)]
        self.add(n,vs,fs,ma,True,parent)
    def rod(self,n,a,b,r,ma,N=12,parent=None):self.tube(n,[a,b],r,ma,N,parent)
    def ring(self,n,c,ro,ri,h,ma,axis='Z',N=32,parent=None):
        vs=[]
        for z,r in [(-h/2,ro),(h/2,ro),(h/2,ri),(-h/2,ri)]:
            for j in range(N):
                q=(r*cos(tau*j/N),r*sin(tau*j/N),z)
                if axis=='X':q=(q[2],q[0],q[1])
                elif axis=='Y':q=(q[0],q[2],q[1])
                vs.append(tuple(c[k]+q[k] for k in range(3)))
        fs=[(k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j) for k in range(4) for j in range(N)]
        self.add(n,vs,fs,ma,True,parent)
    def text(self,n,words,c,size,ma,normal='X',parent=None):
        # Conversion via evaluated mesh avoids selection/global bpy.ops changes.
        cu=bpy.data.curves.new(PREFIX+'temporary_font','FONT');cu.body=words;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.extrude=.00012;cu.resolution_u=2
        o=bpy.data.objects.new(PREFIX+'temporary_font',cu);self.ctx['collection'].objects.link(o)
        o.location=c
        # Font local +Z faces requested direction, local Y always upward.
        transforms={'X':(pi/2,0,pi/2),'-X':(pi/2,0,-pi/2),'Y':(pi/2,0,pi),'-Y':(pi/2,0,0),'Z':(0,0,0)}
        o.rotation_euler=transforms[normal]
        bpy.context.view_layer.update()
        me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        self.add(n,[o.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons],ma,parent=parent)
        bpy.data.meshes.remove(me);bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(cu)
    def flush(self):
        objects=[]
        for (n,ma,pn),(v,f,s,par) in self.groups.items():
            o=mesh(PREFIX+n,v,f,self.m[ma],par,self.ctx['collection'])
            for poly,sm in zip(o.data.polygons,s):poly.use_smooth=sm
            o['detail_role']=n;o['source_component']='interiors.py';objects.append(o)
        return objects


def seat(b,anchor,ec):
    x,y=anchor.location.x,anchor.location.y
    f=1 if cos(anchor.rotation_euler.z)>0 else -1
    b.pose=(x,y,f);w=.54 if ec else .435;ma='ec' if ec else 'cc';seam='seam_ec' if ec else 'seam_cc'
    # Original full-size chair geometry: cushion datum remains exactly 1.750 m.
    b.loft('seats_cushion',[(1.616,.01,.40,w*.88),(1.63,.01,.474,w),(1.705,.012,.484,w),(1.742,.008,.452,w*.94),(1.75,0,.395,w*.81)],ma)
    height=2.68 if ec else 2.58
    b.loft('seats_sculpted_back',[(1.72,-.143,.10,w*.90),(1.77,-.152,.155,w),(1.92,-.173,.162,w),(2.11,-.207,.15,w*.98),(2.32,-.242,.144,w),(height-.13,-.26,.155,w*(1.04 if ec else 1)),(height-.035,-.28,.12,w*.97),(height,-.285,.066,w*.83)],ma)
    # Lumbar/body bolsters subtly break the seat into ergonomic padded volumes.
    for s in [-1,1]:
        b.tube('seats_side_piping',[(-.10,s*w*.455,1.76),(-.13,s*w*.46,1.91),(-.16,s*w*.45,2.12),(-.18,s*w*.465,2.33),(-.205,s*w*.45,height-.07)],.0033,seam,8)
    def cushion_seam(z):
        t=(z-1.705)/(.037);depth=.484+(.452-.484)*t;width=w+(w*.94-w)*t;xc=.012+(.008-.012)*t
        def ss(v):return math.copysign(abs(v)**.42,v)
        return [(xc+depth*.5*ss(cos(math.radians(a))),width*.5*ss(sin(math.radians(a))),z) for a in range(-90,91,15)]
    b.tube('seats_cushion_piping',cushion_seam(1.728),.0019,seam,8)
    # Paired lockstitch runs are real geometry, visible in close inspection.
    # Thread diameter 0.9 mm; 3 mm stitch / 3 mm gap, not oversized dots.
    thread='thread_ec' if ec else 'thread_cc'
    def stitch(pts):
        for pa,pb in zip(pts,pts[1:]):
            pa,pb=Vector(pa),Vector(pb);length=(pb-pa).length
            for i in range(max(1,int(length/.006))):
                t=(i+.12)*.006/length
                if t>=1:continue
                b.rod('seats_double_lockstitch',pa.lerp(pb,t),pa.lerp(pb,min(1,t+.003/length)),.00045,thread,5)
    for side in [-1,1]:
        for offset in [.006,.010]:
            stitch([(-.100,side*(w*.455-offset),1.77),(-.130,side*(w*.46-offset),1.91),
                    (-.160,side*(w*.45-offset),2.12),(-.180,side*(w*.465-offset),2.33),
                    (-.205,side*(w*.45-offset),height-.075)])
    stitch(cushion_seam(1.734))
    # Grey back shell, kick panel and sculpted shoulder transitions.
    b.loft('seats_moulded_shell',[(1.62,-.248,.043,w*.82),(1.68,-.265,.042,w*.96),(1.88,-.282,.038,w),(2.11,-.316,.032,w),(2.25,-.337,.029,w*.97),(2.295,-.337,.024,w*.89)],'shell')
    b.rounded('seats_kick_panel',(-.292,0,1.68),(.022,w*.80,.085),'shell',.012,'X')
    # Folded back tray with raised perimeter, recess, hinge barrel, two pivot caps,
    # retaining latch, plus a genuinely open net pocket below it.
    b.rounded('seats_tray_perimeter',(-.348,0,2.074),(.034,w*.82,.375),'shell',.022,'X')
    b.rounded('seats_tray_inset',(-.370,0,2.077),(.007,w*.75,.314),'lining',.014,'X')
    b.rod('seats_tray_hinge',(-.367,-w*.36,1.892),(-.367,w*.36,1.892),.011,'trim')
    b.rounded('seats_tray_latch_base',(-.373,0,2.302),(.011,.032,.037),'shell',.004,'X')
    b.tube('seats_tray_latch_lever',[(-.384,.012,2.316),(-.384,-.023,2.274)],.008,'shell',10)
    b.rod('seats_latch_fastener',(-.392,0,2.31),(-.397,0,2.31),.006,'chrome',12)
    # Black diamond mesh with real openings; cords clipped to pocket perimeter.
    pocketw=w*.73;zlo,zhi=1.716,1.88
    b.rounded('seats_pocket_back',(-.288,0,(zlo+zhi)/2),(.012,pocketw+.017,zhi-zlo+.026),'grey',.012,'X')
    for direction in [-1,1]:
        for k in range(-10,11):
            ya=k*.041; candidates=[]
            for z in [zlo,zhi]:
                yy=ya+direction*(z-zlo)*.80
                if abs(yy)<=pocketw/2+.0001:candidates.append((-.321,yy,z))
            for yy in [-pocketw/2,pocketw/2]:
                zz=zlo+(yy-ya)/(direction*.80)
                if zlo<=zz<=zhi:candidates.append((-.321,yy,zz))
            if len(candidates)>=2:b.rod('seats_diamond_net',candidates[0],candidates[1],.0028,'black_int',6)
    b.tube('seats_pocket_frame',[(-.325,-pocketw/2,zhi),(-.327,-pocketw/2,zlo),(-.328,pocketw/2,zlo),(-.325,pocketw/2,zhi)],.009,'black_int',8)
    b.rod('seats_pocket_elastic',(-.326,-pocketw/2,zhi),(-.326,pocketw/2,zhi),.005,'black_int',8)
    # Cast articulated arm supports, padded rests and recline button.
    for s in [-1,1]:
        yy=s*(w/2+.009)
        b.rounded('seats_arm_hinge',(-.16,yy,1.81),(.095,.024,.115),'shell',.012,'Y')
        b.rod('seats_arm_pivot',(-.16,yy-.018,1.82),(-.16,yy+.018,1.82),.029,'trim',20)
        b.tube('seats_cast_arm_support',[(-.16,yy,1.80),(-.165,yy,1.93),(-.10,yy,1.968),(.185,yy,1.968)],.016,'shell',10)
        b.rounded('seats_arm_pads',(.012,yy,1.99),(.43,.041,.045),'rubber_int' if ec else 'seam_cc',.015)
        b.rod('seats_recline_button',(.16,yy-s*.024,1.97),(.16,yy-s*.030,1.97),.011,'trim',16)
    # Pedestal mount plate, rotary EC bearing, floor bolting and lower foot bar.
    b.rounded('seats_floor_plate',(-.025,0,1.345),(.29,w*.64,.040),'trim',.013)
    b.rod('seats_support_column',(-.026,0,1.365),(-.026,0,1.598),.056 if ec else .047,'grey',20)
    b.rounded('seats_underseat_cradle',(-.03,0,1.585),(.305,w*.80,.044),'grey',.014)
    b.rounded('seats_charging_outlet_housing',(.14,w*.32,1.58),(.030,.087,.083),'shell',.006,'X')
    b.rod('seats_charging_socket',(.158,w*.32,1.593),(.162,w*.32,1.593),.020,'rubber_int',20)
    for yy,zz in [(-.008,0),(.008,0),(0,.009)]:b.rod('seats_charging_socket_contacts',(.162,w*.32+yy,1.593+zz),(.164,w*.32+yy,1.593+zz),.003,'black_int',8)
    b.rounded('seats_USB_charging_port',(.160,w*.32,1.550),(.006,.026,.009),'black_int',.003,'X')
    if ec:
        b.ring('seats_EC_rotary_bearing',(-.025,0,1.572),.115,.055,.031,'trim')
        # Wider headrest wings and separate textile antimacassar.
        for s in [-1,1]:
            b.rounded('seats_EC_headrest_wings',(-.218,s*w*.42,2.51),(.18,.09,.305),ma,.04,'X')
        b.rounded('seats_EC_linen_cover',(-.170,0,2.525),(.012,w*.48,.277),'cover',.019,'X')
        b.tube('seats_EC_linen_hem',[(-.161,-w*.22,2.643),(-.161,-w*.235,2.410),(-.161,0,2.394),(-.161,w*.235,2.410),(-.161,w*.22,2.643)],.0022,'cover',8)
    else:
        b.tube('seats_CC_top_grab_handle',[(-.292,-w*.29,2.536),(-.300,-w*.25,2.622),(-.300,-w*.20,2.645),(-.300,w*.20,2.645),(-.300,w*.25,2.622),(-.292,w*.29,2.536)],.016,'shell',12)
    b.tube('seats_foldaway_footrest',[(-.24,-w*.32,1.58),(-.395,-w*.32,1.475),(-.395,w*.32,1.475),(-.24,w*.32,1.58)],.011,'grey',10)
    b.rod('seats_footrest_rubber',(-.395,-w*.26,1.475),(-.395,w*.26,1.475),.022,'rubber_int',12)
    for xx in [-.125,.077]:
        for yy in [-w*.24,w*.24]:b.rod('seats_mount_bolt',(xx,yy,1.367),(xx,yy,1.377),.007,'chrome',6)
    b.pose=None


def lining_racks(b,ctx,dtc,ec):
    layout=ctx.get('layout') or layout_for(ctx['kind'])
    xmin,xmax=layout['saloon_bounds']
    total=xmax-xmin;mid=(xmin+xmax)/2
    # Lowered crowned interior shell: removable access panels and continuous LED
    # coves. Each surface remains inside the actual roof, leaving HVAC outside.
    cross=[(-1.516,3.13),(-1.48,3.34),(-1.29,3.50),(-.91,3.62),(-.73,3.65),(0,3.675),(.73,3.65),(.91,3.62),(1.29,3.50),(1.48,3.34),(1.516,3.13)]
    rear,front=layout['lining_bounds']
    for (y,z),(yy,zz) in zip(cross,cross[1:]):
        b.add('ceiling_curved_lining',[(rear,y,z),(front,y,z),(front,yy,zz),(rear,yy,zz)],[(0,1,2,3)],'lining')
    # Segment seams make the ceiling read as manufactured panels, not one tube.
    for x in [xmin+i*1.08 for i in range(int(total/1.08)+1)]:
        b.tube('ceiling_access_panel_joints',[(x,y,z-.006) for y,z in cross[2:-2]],.0026,'grey',6)
    b.rounded('ceiling_center_perforated_panel',(mid,0,3.648),(total,.99,.032),'shell',.014)
    for x in [xmin+.12+i*.088 for i in range(int((total-.2)/.088))]:
        for j in range(-6,7):
            b.rounded('ceiling_acoustic_slot_recesses',(x,j*.067,3.630),(.039,.009,.002),'grey',.003)
    for s in [-1,1]:
        b.rounded('ceiling_light_recess',(mid,s*.746,3.610),(total,.103,.052),'grey',.018)
        b.rounded('ceiling_continuous_diffuser',(mid,s*.746,3.580),(total,.050,.020),'led',.009)
        for yy in [-.045,.045]:b.rod('ceiling_LED_edge_trim',(xmin,s*.746+yy,3.587),(xmax,s*.746+yy,3.587),.006,'trim',8)
        # Each rack uses translucent infill panels, edge extrusion, anti-roll rail
        # and curving triangular struts. Front rail stays outside head space.
        b.rod('racks_polished_front_rail',(xmin,s*.998,3.185),(xmax,s*.998,3.185),.024,'chrome',20)
        b.rod('racks_outer_mount_rail',(xmin,s*1.473,3.153),(xmax,s*1.473,3.153),.015,'trim',16)
        bays=max(1,round(total/1.12))
        for k in range(bays):
            a=xmin+k*total/bays+.012;c=xmin+(k+1)*total/bays-.012
            b.rounded('racks_frosted_aqua_shelf',((a+c)/2,s*1.247,3.151),(c-a,.472,.016),'aqua',.006)
            # Original etched diagonal hatch, true fine geometry.
            for xx in [a+.08+j*.15 for j in range(max(0,int((c-a-.1)/.15)))]:
                for yy in [1.10,1.25,1.40]:
                    b.rod('racks_etched_shelf_pattern',(xx-.018,s*(yy-.020),3.142),(xx+.018,s*(yy+.020),3.142),.0013,'rack_pattern',4)
        for x in [xmin+i*total/bays for i in range(bays+1)]:
            b.tube('racks_triangular_hangers',[(x,s*1.488,3.005),(x,s*1.49,3.165),(x,s*1.445,3.222),(x,s*1.005,3.197),(x,s*1.018,3.147),(x,s*1.462,3.061)],.015,'chrome',12)
            b.rounded('racks_wall_bracket_mount',(x,s*1.485,3.07),(.08,.028,.14),'shell',.014,'Y')
        # Passenger-service units and numbering are generated from actual
        # anchors in each bank. Missing end/companion seats never get a phantom
        # nozzle or a fictitious full-row number range.
        anchors=[o for o in ctx['collection'].objects if o.name.startswith('PAX_') and o.type=='EMPTY' and o.location.y*s>0]
        xs=sorted(set(round(o.location.x,5) for o in anchors))
        for x in xs:
            bank=sorted([o for o in anchors if abs(o.location.x-x)<.001],key=lambda o:o.name)
            b.rounded('PSU_undershelf_housing',(x,s*1.262,3.096),(.31,.37,.045),'shell',.014)
            for j in range(len(bank)):
                yy=s*(1.12+.145*j)
                b.ring('PSU_nozzle_surround',(x+.061,yy,3.071),.033,.023,.015,'trim',N=24)
                b.rod('PSU_air_jet',(x+.061,yy,3.077),(x+.061,yy,3.064),.019,'grey',20)
                for ll in [-1,0,1]:b.box('PSU_air_jet_vanes',(x+.061+ll*.010,yy,3.055),(.003,.030,.008),'shell')
            b.ring('PSU_reading_light_bezel',(x-.076,s*1.195,3.069),.031,.024,.012,'trim',N=24)
            b.rod('PSU_reading_light_lens',(x-.076,s*1.195,3.070),(x-.076,s*1.195,3.060),.023,'led',20)
            b.rod('PSU_light_button',(x-.075,s*1.33,3.070),(x-.075,s*1.33,3.058),.012,'rubber_int',16)
            b.rounded('racks_seat_number_plaque',(x,s*1.487,3.015),(.22,.008,.052),'label',.004,'Y')
            numbers=' '.join(f'{int(o.name.split("_")[-1]):02d}' for o in bank)
            b.text('racks_seat_numbers',numbers,(x,s*1.479,3.015),.027,'label_white','-Y' if s>0 else 'Y')
    # Centerline speakers/smoke detector/CCTV, visible but carefully subordinate.
    for x in [xmin+.9,mid,xmax-.9]:
        b.ring('ceiling_speaker_bezel',(x,0,3.617),.089,.073,.012,'lining',N=32)
        b.rod('ceiling_speaker_grille',(x,0,3.618),(x,0,3.612),.072,'grey',32)
        for k in range(-4,5):
            rr=math.sqrt(max(0,.065**2-(k*.014)**2));b.box('ceiling_speaker_slits',(x+k*.014,0,3.608),(.004,rr*2,.003),'shell')
    b.rod('ceiling_smoke_detector',(mid+.46,0,3.630),(mid+.46,0,3.598),.061,'lining',32)
    b.ring('ceiling_detector_vent',(mid+.46,0,3.590),.048,.032,.019,'grey',N=24)
    b.rounded('ceiling_CCTV_housing',(xmax-.35,0,3.553),(.105,.09,.062),'lining',.020)
    b.rod('ceiling_CCTV_lens',(xmax-.37,0,3.525),(xmax-.37,0,3.518),.026,'black_int',24)
    # Interior wall finish is segmented around existing actual glass apertures.
    windows=layout['windows']
    for s in [-1,1]:
        b.rounded('wall_lower_saloon_lining',(mid,s*1.511,1.618),(total,.025,.594),'lining',.012,'Y')
        b.rounded('wall_skirt_scuff_strip',(mid,s*1.488,1.368),(total,.020,.102),'trim',.008,'Y')
        side_windows=[q for q in windows if s in q.get('sides',[-1,1])]
        for j,win in enumerate(side_windows):
            x=win['x'];w=win['width'];top=win['center_z']+win['height']/2
            # Exterior module owns dimension-correct window aperture/jamb/sill.
            b.rounded('wall_blind_cassette',(x,s*1.473,top+.029),(w+.038,.071,.078),'lining',.016)
            b.rounded('wall_roller_blind_fabric',(x,s*1.473,top-.04),(w-.012,.015,.081),'blind',.006,'Y')
            b.rod('wall_blind_bottom_rail',(x-w/2+.018,s*1.457,top-.080),(x+w/2-.018,s*1.457,top-.080),.008,'shell',12)
            b.rounded('wall_blind_pull',(x,s*1.445,top-.089),(.082,.024,.025),'shell',.006)
        main=sorted([q for q in side_windows if q['role']=='saloon'],key=lambda q:q['x'])
        pier_x=[(main[i]['x']+main[i+1]['x'])/2 for i in range(len(main)-1)]
        for x in (pier_x if dtc else pier_x[::2]):
            b.rounded('wall_emergency_hammer_case',(x,s*1.476,2.876),(.10,.049,.18),'lining',.016,'Y')
            b.rounded('wall_emergency_hammer_window',(x,s*1.443,2.876),(.058,.007,.12),'glass_int',.006,'Y')
            b.rod('wall_emergency_hammer_grip',(x,s*1.452,2.822),(x,s*1.452,2.887),.009,'red_int',10)
            b.rod('wall_emergency_hammer_head',(x-.025,s*1.453,2.9),(x+.025,s*1.453,2.9),.009,'chrome',10)
            b.rounded('wall_emergency_instructions',(x,s*1.464,2.70),(.135,.007,.13),'red_int',.004,'Y')
            b.text('wall_emergency_print','EMERGENCY\nHAMMER',(x,s*1.456,2.70),.022,'label_white','-Y' if s>0 else 'Y')


def partitions(b,ctx,dtc,ec,toilet_end=-1):
    layout=ctx.get('layout') or layout_for(ctx['kind'])
    xmin,xmax=layout['partition_centers']
    for x,inward in [(xmin,1),(xmax,-1)]:
        # Hollow portal: .92 m unobstructed width before glazing; no hidden full
        # width wall. Glazing has real closed thickness for two-sided refraction.
        for s in [-1,1]:
            b.rounded('saloon_bulkhead_wings',(x,s*1.015,2.397),(.063,1.085,2.174),'lining',.027,'X')
            b.rounded('saloon_decorative_side_inlay',(x+inward*.038,s*1.145,2.39),(.012,.11,1.84),'shell',.007,'X')
            b.rounded('saloon_door_jamb',(x+inward*.040,s*.463,2.287),(.065,.063,1.958),'trim',.017)
            b.rounded('saloon_jamb_rubber_seal',(x+inward*.047,s*.432,2.281),(.014,.012,1.898),'rubber_int',.003)
        b.rounded('saloon_header',(x,0,3.421),(.102,1.13,.304),'lining',.045,'X')
        b.rounded('saloon_door_track',(x+inward*.035,0,3.24),(.063,.93,.068),'trim',.018)
        b.box('saloon_clear_sliding_glass',(x,0,2.284),(.008,.855,1.873),'glass_int')
        for z in [1.345,3.22]:b.rounded('saloon_door_leaf_horizontal_frame',(x,0,z),(.025,.87,.035),'trim',.007)
        for s in [-1,1]:b.rounded('saloon_door_leaf_side_frame',(x,s*.424,2.28),(.025,.022,1.90),'trim',.005)
        # Frosted safety dots and narrow waist stripe retain useful sight lines.
        for j in range(-8,9):
            for z in [2.20,2.24]:b.rod('saloon_glass_safety_dots',(x-inward*.006,j*.046,z),(x+inward*.006,j*.046,z),.009,'frit',12)
        b.rounded('saloon_glass_safety_band',(x+inward*.006,0,2.155),(.002,.834,.010),'frit',.001)
        b.tube('saloon_assist_handle',[(x+inward*.055,-.325,2.15),(x+inward*.095,-.325,2.17),(x+inward*.095,-.325,2.41),(x+inward*.055,-.325,2.43)],.011,'chrome',12)
        normal='X' if inward>0 else '-X'
        b.rounded('PIS_black_surround',(x+inward*.07,0,3.421),(.058,.79,.218),'black_int',.027,'X')
        b.rounded('PIS_display_glass',(x+inward*.106,0,3.425),(.008,.723,.159),'screen',.005,'X')
        b.text('PIS_message','WELCOME ABOARD',(x+inward*.112,0,3.440),.052,'green_led',normal)
        b.text('PIS_subline','VANDE BHARAT',(x+inward*.112,0,3.384),.026,'label_white',normal)
        b.rounded('saloon_EXIT_label',(x+inward*.038,0,3.565),(.005,.255,.069),'green',.008,'X')
        b.text('saloon_EXIT_letters','EXIT',(x+inward*.043,0,3.565),.047,'label_white',normal)
        b.rounded('saloon_door_touch_panel',(x+inward*.048,.573,2.28),(.024,.092,.19),'label',.013,'X')
        b.rod('saloon_door_touch_ring',(x+inward*.063,.573,2.30),(x+inward*.068,.573,2.30),.025,'green',24)
        b.text('saloon_door_touch_label','OPEN',(x+inward*.065,.573,2.235),.020,'label_white',normal)
        b.rounded('saloon_class_plaque',(x+inward*.036,-1.06,2.83),(.007,.46,.19),'label',.012,'X')
        b.text('saloon_class_lettering','EXECUTIVE' if ec else 'CHAIR CAR',(x+inward*.042,-1.06,2.84),.046,'label_white',normal)
        b.text('saloon_class_lettering','2 + 2' if ec else '3 + 2',(x+inward*.042,-1.06,2.778),.027,'label_white',normal)
        # Full-size service bays begin immediately outside the partition.
        # Luggage storage is overhead; no inherited miniature floor tower is
        # inserted through the pantry or electrical cabinet envelope.


def toilet_room(b,x,s,western=True,length=1.890,width=1.005,accessible=False):
    """Dimensioned room envelope, with unchanged-size plumbing assemblies."""
    yy=s*(1.50-width/2);inner=s*(1.50-width);normal='-Y' if s>0 else 'Y'
    half=length/2
    if accessible:
        # DTC has ONE accessible WC. The large circle across the corridor in
        # the drawing is maneuvering clearance, never a second lavatory.
        # Rounded inward wall and sliding curved door are original geometry;
        # inferred 1.78 m transverse outline is not accessibility certification.
        left,right=x-half,x+half;outer=-1.50;inside=.28;r=.60
        pts=[(left,outer),(right,outer),(right,inside-r)]
        pts += [(right-r+r*cos(t*pi/2/10),inside-r+r*sin(t*pi/2/10)) for t in range(1,11)]
        pts += [(left+r,inside)]
        pts += [(left+r+r*cos(pi/2+t*pi/2/10),inside-r+r*sin(pi/2+t*pi/2/10)) for t in range(1,11)]
        for j,(pa,pb) in enumerate(zip(pts,pts[1:]+[pts[0]])):
            # Central inward-facing wall is the separately removable door.
            n='service_removable_closed_door' if abs(pa[1]-inside)<.001 and abs(pb[1]-inside)<.001 else 'service_accessible_curved_wall'
            tangent=Vector((pb[0]-pa[0],pb[1]-pa[1],0)).normalized()
            normal=Vector((-tangent.y,tangent.x,0))*.012
            vs=[]
            for q in [-1,1]:
                for pt in [(pa[0],pa[1],1.32),(pb[0],pb[1],1.32),(pb[0],pb[1],3.29),(pa[0],pa[1],3.29)]:
                    vs.append(tuple(Vector(pt)+normal*q))
            b.add(n,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'lining')
        b.add('service_cabin_roof',[(xx,yy,3.29) for xx,yy in pts],[tuple(range(len(pts)))],'lining')
        b.add('service_cabin_floor',[(xx,yy,1.329) for xx,yy in pts],[tuple(range(len(pts)))],'floor_int')
        b.tube('service_accessible_door_top_track',[(xx,yy,3.28) for xx,yy in pts[2:-1]],.023,'trim',12)
        for xx in [left+r,right-r]:
            b.rounded('service_accessible_clear_opening_jamb',(xx,inside,2.305),(.035,.055,1.97),'trim',.010)
        b.rounded('service_accessible_door_header',(x,inside,3.28),(length-2*r,.055,.065),'trim',.012)

        b.tube('service_accessible_door_handle',[(x+.36,inside+.025,2.04),(x+.36,inside+.065,2.07),(x+.36,inside+.065,2.44),(x+.36,inside+.025,2.47)],.015,'chrome',12)
        b.rounded('service_WC_plaque',(x,inside+.008,2.80),(.49,.009,.20),'label',.012,'Y')
        b.text('service_WC_letters','ACCESSIBLE WC',(x,inside+.016,2.81),.057,'label_white','Y')
        b.text('service_WC_type','VACUUM TOILET',(x,inside+.016,2.746),.028,'label_white','Y')
        # Support hardware, call button and folded-assist rail are fixed-size.
        b.tube('toilet_accessible_assist_rail',[(x-.54,-.47,1.38),(x-.54,-.47,2.06),(x-.54,-.96,2.06)],.019,'chrome',16)
        b.rounded('toilet_assistance_call_plate',(x-.70,-1.463,2.14),(.12,.020,.17),'label',.012,'Y')
        b.rod('toilet_assistance_call_button',(x-.70,-1.446,2.16),(x-.70,-1.432,2.16),.030,'red_int',24)
    else:
        for xx in [x-half,x+half]:b.rounded('service_cabin_end_partitions',(xx,yy,2.305),(.035,width,1.99),'lining',.014)
        b.rounded('service_cabin_roof',(x,yy,3.29),(length,width,.035),'lining',.014)
        b.rounded('service_cabin_floor',(x,yy,1.329),(length-.035,width-.035,.018),'floor_int',.006)
        # A real door within a long wall, not a stretched miniature door.
        for q in [-1,1]:
            w=(length-.790)/2
            b.rounded('service_cabin_aisle_fixed_panels',(x+q*(.395+w/2),inner,2.305),(w,.035,1.99),'lining',.012,'Y')
        for xx in [x-.395,x+.395]:b.rounded('service_aisle_door_jamb',(xx,inner,2.30),(.074,.04,1.98),'shell',.013)
        b.rounded('service_aisle_door_header',(x,inner,3.276),(.84,.045,.064),'shell',.012)
        b.rounded('service_removable_closed_door',(x,inner,2.286),(.704,.026,1.863),'lining',.018,'Y')
        b.rounded('service_door_kickplate',(x,inner-s*.020,1.513),(.655,.01,.23),'trim',.006,'Y')
        b.rounded('service_door_lock_escutcheon',(x+.227,inner-s*.027,2.27),(.062,.017,.16),'trim',.010,'Y')
        b.tube('service_door_lever',[(x+.227,inner-s*.035,2.287),(x+.227,inner-s*.065,2.287),(x+.12,inner-s*.065,2.287)],.009,'chrome',10)
        b.rod('service_occupied_indicator',(x+.226,inner-s*.037,2.33),(x+.226,inner-s*.042,2.33),.013,'green',16)
        b.rounded('service_WC_plaque',(x,inner-s*.018,2.758),(.18,.007,.15),'label',.008,'Y')
        b.text('service_WC_letters','WC',(x,inner-s*.024,2.764),.080,'label_white',normal)
        b.text('service_WC_type','WESTERN' if western else 'INDIAN',(x,inner-s*.024,2.711),.020,'label_white',normal)
    # Bowl/pan is modelled as an open-lipped shell; no solid cube substitutes.
    bx=x-half+.43;by=s*1.175
    if western:
        b.rounded('toilet_pedestal',(bx,by,1.491),(.30,.27,.323),'label_white',.06)
        # Elliptical open ceramic bowl and seat.
        for z,rx,ry,rz,ma in [(1.677,.245,.172,.072,'label_white'),(1.720,.254,.182,.028,'shell')]:
            vs=[];N=40
            for zz,factor in [(-rz/2,1),(rz/2,1),(rz/2,.73),(-rz/2,.70)]:
                for j in range(N):vs.append((bx+rx*factor*cos(tau*j/N),by+ry*factor*sin(tau*j/N),z+zz))
            fs=[(k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j) for k in range(4) for j in range(N)]
            b.add('toilet_open_bowl_and_seat',vs,fs,ma,True)
        b.rounded('toilet_bowl_inner_shadow',(bx,by,1.61),(.30,.22,.016),'grey',.06)
        b.rounded('toilet_tank',(bx-.196,by,1.92),(.071,.331,.355),'label_white',.022)
        b.rod('toilet_flush_button',(bx-.196,by,2.102),(bx-.196,by,2.109),.018,'chrome',20)
    else:
        b.rounded('toilet_squat_pan_surround',(bx,by,1.342),(.61,.46,.022),'trim',.045)
        b.rounded('toilet_squat_pan_recess',(bx,by,1.356),(.35,.21,.009),'grey',.035)
        for ss in [-1,1]:
            b.rounded('toilet_foot_pad',(bx,by+ss*.18,1.369),(.40,.09,.021),'shell',.018)
            for j in range(-5,6):b.box('toilet_foot_pad_grip',(bx+j*.029,by+ss*.18,1.382),(.006,.076,.005),'trim')
        b.rod('toilet_flush_pipe',(bx-.24,by,1.39),(bx-.24,by,2.04),.018,'chrome',14)
        b.rod('toilet_flush_valve',(bx-.24,by,2.04),(bx-.24,by-s*.075,2.04),.032,'chrome',16)
    # Corner washbasin, recessed basin, tap, mirror, dispensers, handrail.
    sx=x+half-.22;sy=s*1.10
    # Real recessed basin with an open cutout, dished inner wall, drain and trap.
    for q in [-1,1]:
        b.rounded('toilet_sink_counter',(sx+q*.131,sy,2.008),(.029,.42,.040),'shell',.009)
        b.rounded('toilet_sink_counter',(sx,sy+q*.185,2.008),(.236,.050,.040),'shell',.010)
    vs=[];N=32
    profile=[(2.030,.121,.168),(2.039,.119,.166),(2.040,.103,.147),(2.015,.096,.137),(1.947,.075,.105),(1.913,.028,.037),(1.902,.028,.037),(1.930,.086,.115),(1.995,.119,.164)]
    for z,rx,ry in profile:
        vs.extend((sx+rx*cos(tau*j/N),sy+ry*sin(tau*j/N),z) for j in range(N))
    fs=[(k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j) for k in range(len(profile)) for j in range(N)]
    b.add('toilet_sink_recessed_ceramic_bowl',vs,fs,'label_white',True)
    b.rod('toilet_sink_drain',(sx,sy,1.909),(sx,sy,1.915),.020,'chrome',20)
    for j in range(6):b.rod('toilet_sink_drain_perforations',(sx+.01*cos(tau*j/6),sy+.01*sin(tau*j/6),1.915),(sx+.01*cos(tau*j/6),sy+.01*sin(tau*j/6),1.916),.0024,'black_int',8)
    b.tube('toilet_sink_waste_trap',[(sx,sy,1.904),(sx,sy,1.77),(sx+.048,sy,1.73),(sx+.108,sy,1.77),(sx+.145,sy,1.82)],.017,'chrome',12)
    b.tube('toilet_sensor_faucet',[(sx+.106,sy,2.015),(sx+.106,sy,2.163),(sx+.072,sy,2.186),(sx+.005,sy,2.186)],.012,'chrome',12)
    b.rounded('toilet_mirror_frame',(x+half-.035,s*1.078,2.48),(.027,.355,.44),'trim',.02,'X')
    b.rounded('toilet_mirror',(x+half-.052,s*1.078,2.48),(.006,.315,.40),'mirror',.009,'X')
    b.rounded('toilet_soap_dispenser',(x+half-.11,s*1.365,2.42),(.10,.10,.175),'lining',.02)
    b.rounded('toilet_tissue_dispenser',(x-half+.10,s*.763,2.145),(.13,.13,.14),'lining',.02)
    b.tube('toilet_support_rail',[(x-.34,s*1.459,1.99),(x-.34,s*1.41,1.99),(x+.08,s*1.41,1.99),(x+.10,s*1.459,1.99)],.015,'chrome',12)
    b.rod('toilet_ceiling_light',(x,s*.94,3.265),(x,s*.94,3.255),.107,'led',32)
    b.rounded('toilet_extractor_grille',(x+.25,yy,3.263),(.18,.19,.017),'shell',.015)
    for k in range(-4,5):b.box('toilet_extractor_slots',(x+.25+k*.017,yy,3.252),(.006,.15,.004),'grey')


def galley_appliance_module(b,x,s):
    """Fixed-size pantry hardware module; never longitudinally scaled."""
    y=s*1.03;front=s*.556;normal='-Y' if s>0 else 'Y'
    b.rounded('galley_modular_sidewalls',(x+.417,y,2.30),(.035,.947,1.98),'lining',.014)
    b.rounded('galley_modular_sidewalls',(x-.417,y,2.30),(.035,.947,1.98),'lining',.014)
    b.rounded('galley_top_cupboard',(x,y,3.07),(.79,.92,.40),'lining',.018)
    b.rounded('galley_fridge_carcass',(x+.215,y,1.724),(.37,.884,.768),'lining',.017)
    b.rounded('galley_freezer_door',(x+.215,front,1.729),(.328,.027,.67),'shell',.016,'Y')
    b.tube('galley_freezer_handle',[(x+.10,front-s*.018,1.87),(x+.10,front-s*.048,1.87),(x+.10,front-s*.048,1.58),(x+.10,front-s*.018,1.58)],.008,'chrome',10)
    b.text('galley_appliance_print','FREEZER',(x+.216,front-s*.02,2.010),.021,'label',normal)
    # Removable catering trolley parked in its under-counter recess.
    b.rounded('galley_trolley_body',(x-.205,y,1.737),(.34,.71,.624),'trim',.012)
    for z in [1.51,1.72,1.92]:
        b.rounded('galley_trolley_drawer',(x-.205,y-s*.36,z),(.302,.018,.158),'shell',.009,'Y')
        b.rod('galley_trolley_pull',(x-.298,y-s*.381,z+.027),(x-.11,y-s*.381,z+.027),.007,'chrome',10)
    for xx in [x-.32,x-.09]:
        for yy in [y-.25,y+.25]:
            b.rod('galley_trolley_casters',(xx,yy-.018,1.389),(xx,yy+.018,1.389),.041,'rubber_int',16)
    # Commercial heating cabinet with black glazed cavity and control fascia.
    b.rounded('galley_heating_oven',(x-.17,y+.11*s,2.376),(.43,.52,.426),'trim',.017)
    b.rounded('galley_oven_glass',(x-.20,y-.16*s,2.38),(.323,.009,.277),'black_int',.017,'Y')
    b.tube('galley_oven_pull',[(x-.332,y-.17*s,2.51),(x-.332,y-.21*s,2.51),(x-.07,y-.21*s,2.51),(x-.07,y-.17*s,2.51)],.008,'chrome',10)
    b.rod('galley_oven_control',(x+.01,y-.164*s,2.40),(x+.01,y-.179*s,2.40),.023,'grey',20)
    b.text('galley_appliance_print','HEATING OVEN',(x-.17,y-.171*s,2.216),.025,'label_white',normal)
    # Boiler and a separate round warming vessel with lid and handles.
    b.rod('galley_boiler_vessel',(x+.253,y+.19*s,2.16),(x+.253,y+.19*s,2.615),.108,'trim',28)
    b.rod('galley_boiler_lid',(x+.253,y+.19*s,2.615),(x+.253,y+.19*s,2.63),.112,'chrome',28)
    b.rod('galley_boiler_lid_knob',(x+.253,y+.19*s,2.63),(x+.253,y+.19*s,2.655),.024,'rubber_int',16)
    b.tube('galley_boiler_tap',[(x+.253,y+.07*s,2.266),(x+.253,y+.01*s,2.266),(x+.253,y+.01*s,2.231)],.009,'chrome',10)
    b.rod('galley_soup_warmer',(x+.235,y-.245*s,2.16),(x+.235,y-.245*s,2.30),.114,'trim',28)
    b.ring('galley_soup_warmer_lid',(x+.235,y-.245*s,2.307),.119,.024,.014,'chrome',N=28)
    b.rod('galley_soup_lid_knob',(x+.235,y-.245*s,2.309),(x+.235,y-.245*s,2.34),.027,'rubber_int',16)
    b.text('galley_header_letters','MINI PANTRY',(x,front-s*.021,3.07),.064,'label',normal)


def electrical_cupboard(b,x,s,length=1.60):
    # Opposite full-height electrical cupboard, visible inset seams, ventilation,
    # lockable handles and guarded service controls. No live functional wiring.
    ey=s*1.03;ef=s*.49;enormal='-Y' if s>0 else 'Y'
    b.rounded('electrical_cupboard_carcass',(x,ey,2.294),(length,1.005,1.968),'lining',.019)
    for xx in [x-length*.25,x+length*.25]:
        b.rounded('electrical_cupboard_doors',(xx,ef,2.305),(length/2-.022,.026,1.844),'shell',.011,'Y')
    for xx in [x-.035,x+.035]:
        b.rounded('electrical_cabinet_lock',(xx,ef-s*.022,2.25),(.021,.018,.133),'chrome',.006,'Y')
    for z in [1.49,2.99]:
        b.rounded('electrical_vent_recess',(x,ef-s*.018,z),(.68,.006,.152),'grey',.007,'Y')
        for k in range(-3,4):b.box('electrical_vent_louvres',(x,ef-s*.027,z+k*.019),(.658,.014,.009),'trim')
    b.rounded('electrical_warning_plaque',(x,ef-s*.018,2.605),(.27,.006,.158),'label',.008,'Y')
    b.text('electrical_warning_letters','ELECTRICAL\nPANEL',(x,ef-s*.024,2.605),.041,'label_white',enormal)


def full_galley(b,galley):
    x,s,length=galley['x'],galley['side'],galley['length']
    # Centre module retains the independently modelled .8 m appliances. Side
    # modules add storage and a genuine preparation counter to the full bay.
    galley_appliance_module(b,x-.30,s)
    for xx in [x-length/2,x+length/2]:
        b.rounded('galley_full_bay_sidewall',(xx,s*.9975,2.30),(.035,1.005,1.98),'lining',.014)
    b.rounded('galley_full_length_worktop',(x,s*.995,2.128),(length,1.01,.043),'trim',.014)
    # The center appliance module occupies [x-.717,x+.117]. Full-height end
    # cabinet and a separate fixed-size preparation/wash-up cabinet fill bay.
    for left,right in [(x-length/2+.025,x-.735),(x+.135,x+length/2-.025)]:
        width=right-left
        if width<.15:continue
        mid=(left+right)/2
        b.rounded('galley_storage_carcass',(mid,s*1.005,1.725),(width,.94,.78),'lining',.014)
        doors=max(1,round(width/.40))
        for k in range(doors):
            xx=left+(k+.5)*width/doors
            b.rounded('galley_storage_doors',(xx,s*.515,1.74),(width/doors-.018,.028,.71),'shell',.012,'Y')
            b.rod('galley_storage_pulls',(xx-.07,s*.486,1.93),(xx+.07,s*.486,1.93),.008,'chrome',10)
        b.rounded('galley_full_bay_top_storage',(mid,s*1.03,3.06),(width,.93,.43),'lining',.018)
        b.rounded('galley_upper_cabinet_front',(mid,s*.552,3.06),(width-.016,.025,.387),'shell',.012,'Y')
        b.rod('galley_upper_pull',(mid-.07,s*.525,2.97),(mid+.07,s*.525,2.97),.008,'chrome',10)
    b.text('galley_full_bay_label','PANTRY / STORAGE',(x+.67,s*.503,2.033),.036,'label','-Y' if s>0 else 'Y')


def wheelchair_and_crew(b,layout):
    bay=layout.get('wheelchair_bay')
    if not bay:return
    x,y=bay['x'],bay['y']
    # Wheelchair space deliberately empty: flush floor marking and safety rail.
    a,c=x-bay['length']/2,x+bay['length']/2
    d,e=y-bay['width']/2,y+bay['width']/2
    for xx in [a,c]:b.box('wheelchair_bay_floor_boundary',(xx,y,1.326),(.022,bay['width'],.003),'label')
    for yy in [d,e]:b.box('wheelchair_bay_floor_boundary',(x,yy,1.326),(bay['length'],.022,.003),'label')
    b.tube('wheelchair_bay_assist_rail',[(a+.15,1.465,2.03),(a+.15,1.415,2.03),(c-.15,1.415,2.03),(c-.15,1.465,2.03)],.019,'chrome',14)
    b.rounded('wheelchair_space_sign',(x,1.478,2.78),(.47,.012,.17),'label',.015,'Y')
    b.text('wheelchair_space_label','WHEELCHAIR SPACE',(x,1.468,2.78),.039,'label_white','-Y')
    # The large rear-end circle in the plan denotes clear maneuvering space.
    # It is represented only by a flush discrete floor perimeter, not furniture.
    pts=[(-10.62+.75*cos(tau*j/64),.70+.75*sin(tau*j/64),1.326) for j in range(64)]
    b.tube('wheelchair_turning_zone_floor',pts,.002,'label',6,closed=True)
    # Cab-side crew rest / CCMS enclosure opposite pantry, within +4.6..7.15.
    for xx in [4.64,7.15]:b.rounded('crew_room_end_partition',(xx,-1.006,2.29),(.032,.988,1.94),'lining',.012)
    b.rounded('crew_room_aisle_partition',(6.05,-.498,2.29),(1.12,.035,1.94),'lining',.012,'Y')
    b.rounded('crew_room_door',(5.00,-.498,2.29),(.70,.034,1.89),'lining',.012,'Y')
    b.rod('crew_room_door_handle',(5.21,-.465,2.18),(5.21,-.465,2.36),.011,'chrome',12)
    b.rounded('crew_room_CCMS_display',(6.13,-.474,2.77),(.57,.025,.36),'black_int',.018,'Y')
    b.rounded('crew_room_CCMS_screen',(6.13,-.458,2.77),(.51,.005,.28),'screen',.009,'Y')
    b.text('crew_room_CCMS_label','CREW / CCMS',(6.13,-.452,3.00),.046,'label','Y')
    for xx in [5.42,5.96]:
        b.rounded('crew_tipup_seat_back',(xx,-1.441,2.00),(.43,.085,.50),'shell',.025,'Y')
        b.rounded('crew_tipup_seat_folded',(xx,-1.356,1.73),(.43,.085,.40),'cc',.035,'Y')


def vestibules_pantry(b,ctx,dtc):
    layout=ctx.get('layout') or layout_for(ctx['kind'])
    hand=layout['galley']['side'];toilet_end=layout['toilet_end']
    for room in layout['toilet_rooms']:
        toilet_room(b,room['x'],room['side'],True,room['length'],room['width'],room['accessible'])
    full_galley(b,layout['galley'])
    electrical_cupboard(b,layout['electrical']['x'],layout['electrical']['side'],layout['electrical']['length'])
    if dtc:wheelchair_and_crew(b,layout)
    rear,front=layout['lining_bounds'];xmin,xmax=layout['saloon_bounds']
    for a,c in [(rear+.05,xmin-.05),(xmax+.05,front-.05)]:
        b.box('vestibule_vinyl_finish',((a+c)/2,0,1.323),(c-a,3.08,.006),'floor_int')
    # Discrete fire equipment beside the pantry partition, clear of doors.
    fx=layout['galley']['x']-(-toilet_end)*layout['galley']['length']/2+.15*(-toilet_end)
    fy=-hand*1.43
    b.rounded('vestibule_safety_backplate',(fx,fy,2.25),(.25,.046,.70),'lining',.015,'Y')
    b.rod('vestibule_extinguisher_body',(fx,fy+hand*.076,1.98),(fx,fy+hand*.076,2.35),.080,'red_int',24)
    b.rod('vestibule_extinguisher_neck',(fx,fy+hand*.076,2.35),(fx,fy+hand*.076,2.41),.029,'chrome',16)
    b.rounded('vestibule_extinguisher_handle',(fx,fy+hand*.076,2.43),(.12,.038,.035),'rubber_int',.009)
    b.tube('vestibule_extinguisher_hose',[(fx+.025,fy+hand*.075,2.415),(fx+.13,fy+hand*.075,2.39),(fx+.14,fy+hand*.075,2.05)],.011,'rubber_int',10)
    b.rounded('vestibule_extinguisher_label',(fx,fy+hand*.159,2.2),(.08,.003,.12),'label_white',.003,'Y')
    b.rounded('vestibule_safety_sign',(fx,fy+hand*.029,2.67),(.21,.005,.12),'red_int',.006,'Y')
    b.text('vestibule_safety_sign_print','FIRE / EXTINGUISHER',(fx,fy+hand*.035,2.67),.018,'label_white','Y' if hand>0 else '-Y')
    # Entry doors: interior leaf framing and grab rail move with original pivots.
    for p in ctx['collection'].objects:
        if p.type!='EMPTY' or not p.name.startswith('DOOR_') or not p.name.endswith('_SLIDE'):continue
        x=p.location.x;s=1 if p.location.y>0 else -1;yi=s*1.535;z0=p.location.z
        # World coordinates supplied and correctly converted by common.mesh.
        b.rounded('entry_inner_door_lower_panel',(x,yi,z0+.352),(.89,.019,.695),'lining',.016,'Y',p)
        b.rounded('entry_inner_door_header',(x,yi,z0+1.759),(.89,.019,.272),'lining',.016,'Y',p)
        for dx in [-.344,.344]:b.rounded('entry_inner_door_stile',(x+dx,yi,z0+1.16),(.23,.019,.921),'lining',.015,'Y',p)
        for dx in [-.221,.221]:b.rounded('entry_inner_glass_trim',(x+dx,yi-s*.011,z0+1.16),(.022,.025,.923),'trim',.006,'Y',p)
        for z in [z0+.699,z0+1.621]:b.rounded('entry_inner_glass_trim',(x,yi-s*.011,z),(.464,.025,.022),'trim',.006,'Y',p)
        b.tube('entry_inner_grab_rail',[(x+.369,yi-s*.02,z0+.81),(x+.369,yi-s*.075,z0+.83),(x+.369,yi-s*.075,z0+1.15),(x+.369,yi-s*.02,z0+1.17)],.013,'chrome',12,p)
        b.rounded('entry_inner_caution_label',(x,yi-s*.016,z0+.414),(.25,.007,.072),'label',.005,'Y',p)
        b.text('entry_inner_caution_print','KEEP CLEAR',(x,yi-s*.022,z0+.414),.031,'label_white','-Y' if s>0 else 'Y',p)
        # Fixed body controls on the jamb, not on the moving door.
        cx=x+.595
        b.rounded('entry_door_control_plate',(cx,s*1.494,2.262),(.116,.024,.23),'trim',.014,'Y')
        b.rod('entry_open_button_bezel',(cx,s*1.472,2.282),(cx,s*1.460,2.282),.037,'black_int',24)
        b.rod('entry_green_open_button',(cx,s*1.457,2.282),(cx,s*1.451,2.282),.027,'green',24)
        b.text('entry_button_text','OPEN',(cx,s*1.449,2.201),.025,'label','-Y' if s>0 else 'Y')
        b.rounded('entry_emergency_release_box',(cx,s*1.484,2.645),(.133,.054,.157),'red_int',.015,'Y')
        b.rounded('entry_release_cover',(cx,s*1.451,2.645),(.099,.009,.119),'glass_int',.008,'Y')
        b.rod('entry_release_pull',(cx-.032,s*1.457,2.643),(cx+.032,s*1.457,2.643),.014,'red_int',12)
        b.rounded('entry_antislip_threshold',(x,s*1.410,1.324),(1.0,.25,.022),'trim',.009)
        for j in range(-4,5):b.box('entry_threshold_grooves',(x+j*.104,s*1.410,1.337),(.008,.23,.003),'grey')


def centre_snack_tables(b,layout,dtc,ec):
    if ec:return
    # Main face-to-face bay has genuine wall-side tables. Their fixed depth
    # leaves space to seated fronts and the same unobstructed offset aisle.
    xx=-2.045 if dtc else -.35
    for yy,width in ([(.764,1.433),(-1.0085,.932)] if dtc else [(-.764,1.433),(1.0085,.932)]):
        depth=.50 if dtc else .30
        b.rounded('saloon_centre_tabletop',(xx,yy,2.065),(depth,width,.035),'lining',.020)
        b.rounded('saloon_table_edge',(xx,yy,2.051),(depth+.006,width+.006,.022),'trim',.009)
        b.rod('saloon_table_pedestal',(xx,yy,1.351),(xx,yy,2.038),.039,'trim',20)
        b.rounded('saloon_table_floor_foot',(xx,yy,1.339),(.29,.39,.029),'trim',.012)
        side=1 if yy>0 else -1
        b.tube('saloon_table_wall_support',[(xx,side*1.482,1.94),(xx,side*1.42,1.94),(xx,side*1.24,2.032)],.018,'trim',12)


def linked_passenger_seats(ctx,m,anchors,ec):
    """One detailed, exact-size mesh datablock, one real instance per seat.

    Seat instances are parented to their own PAX controls with an explicit
    Z-offset, so the full mesh follows marker translation/rotation. This is
    inspectable geometry instancing, not empty seat-count metadata.
    """
    from types import SimpleNamespace
    temp=Batch(ctx,m)
    anchor=SimpleNamespace(location=Vector((0,0,1.267)),rotation_euler=Vector((0,0,0)))
    seat(temp,anchor,ec)
    verts=[];faces=[];smooth=[];indices=[];materials_list=[]
    for (name,ma,parent),(vv,ff,ss,par) in temp.groups.items():
        if m[ma] not in materials_list:materials_list.append(m[ma])
        mi=materials_list.index(m[ma]);off=len(verts)
        verts.extend(vv);faces.extend(tuple(off+k for k in f) for f in ff)
        smooth.extend(ss);indices.extend([mi]*len(ff))
    proto=mesh(PREFIX+'seat_001',verts,faces,materials_list,None,ctx['collection'])
    for poly,sm,mi in zip(proto.data.polygons,smooth,indices):
        poly.use_smooth=sm;poly.material_index=mi
    data=proto.data;data.name=PREFIX+('EC' if ec else 'CC')+'_fixed_size_seat_mesh'
    data['width_cushion_m']=.54 if ec else .435
    data['cushion_top_local_z_m']=1.750
    data['instancing']='Actual reusable detailed seat mesh; no geometric scaling'
    objects=[]
    for i,anchor in enumerate(anchors):
        obj=proto if i==0 else bpy.data.objects.new(PREFIX+f'seat_{i+1:03d}',data)
        if i:ctx['collection'].objects.link(obj)
        obj.parent=anchor;obj.location=(0,0,-anchor.location.z);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
        obj['detail_role']='passenger_seat_instance';obj['seat_anchor']=anchor.name
        obj['source_component']='interiors.py';obj['seat_class']='EC' if ec else 'CC'
        objects.append(obj)
    return objects


def apply(ctx):
    remove_prefix(PREFIX)
    layout=ctx.get('layout') or layout_for(ctx['kind']);ctx['layout']=layout
    removed=[]
    mixed={'Seat_armrests','Seat_armrest_posts','Seat_pedestals','Seat_mounts'}
    for n in REPLACED:
        o=bpy.data.objects.get(n)
        if not o or o.type!='MESH':continue
        if ctx['kind']=='DTC' and n in mixed:
            import bmesh
            bm=bmesh.new();bm.from_mesh(o.data)
            kill=[v for v in bm.verts if v.co.x<layout['cab_bulkhead']]
            bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
            removed.append(n+' passenger-only vertices')
        else:
            bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
    m=materials(ctx);b=Batch(ctx,m)
    floor=bpy.data.objects.get('Saloon_floor')
    if floor and floor.type=='MESH':
        floor.data.materials.clear();floor.data.materials.append(m['floor_int'])
    anchors=sorted([o for o in ctx['collection'].objects if o.type=='EMPTY' and o.name.startswith('PAX_')],key=lambda o:o.name)
    ec='EC' in ctx['kind'];dtc=ctx['kind']=='DTC'
    assert len(anchors)==layout['expected_seats'], (ctx['kind'],'PAX layout not rebuilt',len(anchors))
    for anchor,pose in zip(anchors,layout['seat_poses']):
        assert abs(anchor.location.x-pose['x'])<.00001 and abs(anchor.location.y-pose['y'])<.00001, (anchor.name,'layout mismatch')
        assert (1 if cos(anchor.rotation_euler.z)>0 else -1)==pose['facing'], (anchor.name,'facing mismatch')
    original=[(o.name,tuple(o.location),tuple(o.rotation_euler)) for o in anchors]
    seats=linked_passenger_seats(ctx,m,anchors,ec)
    lining_racks(b,ctx,dtc,ec)
    centre_snack_tables(b,layout,dtc,ec)
    partitions(b,ctx,dtc,ec,layout['toilet_end'])
    vestibules_pantry(b,ctx,dtc)
    obs=b.flush()+seats
    bpy.context.view_layer.update()
    assert original==[(o.name,tuple(o.location),tuple(o.rotation_euler)) for o in anchors], 'PAX anchors were changed'
    actual=[o for o in ctx['collection'].objects if o.type=='MESH' and o.get('detail_role')=='passenger_seat_instance']
    assert len(actual)==layout['expected_seats']
    # Real vertex envelope checks, independent of PAX counts.
    xmin,xmax=layout['saloon_bounds'];minclear=100;seat_bounds=[]
    for o in actual:
        points=[o.matrix_world@v.co for v in o.data.vertices]
        lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
        clear=min(lo[0]-xmin,xmax-hi[0]);minclear=min(minclear,clear)
        assert clear>=-.001, (o.name,'seat intersects saloon end',lo,hi)
        assert lo[1]>=-1.515 and hi[1]<=1.515, (o.name,'seat exceeds sidewall',lo,hi)
        assert o.scale==Vector((1,1,1)), (o.name,'seat was scaled')
        seat_bounds.append(dict(object=o.name,anchor=o.parent.name,min=lo,max=hi))
    lateral_gaps=[]
    for i,pa in enumerate(seat_bounds):
        for pb in seat_bounds[i+1:]:
            if abs((pa['min'][0]+pa['max'][0])-(pb['min'][0]+pb['max'][0]))>.001:continue
            gap=max(pa['min'][1]-pb['max'][1],pb['min'][1]-pa['max'][1])
            assert gap>=-.00001, (pa['object'],pb['object'],'adjacent seat meshes overlap',gap)
            lateral_gaps.append(gap)
    if dtc:
        bay=layout['wheelchair_bay']; bx0=bay['x']-bay['length']/2; bx1=bay['x']+bay['length']/2
        by0=bay['y']-bay['width']/2; by1=bay['y']+bay['width']/2
        for pa in seat_bounds:
            dx=min(bx1,pa['max'][0])-max(bx0,pa['min'][0]);dy=min(by1,pa['max'][1])-max(by0,pa['min'][1])
            assert dx<=0 or dy<=0,(pa['object'],'seat enters reserved wheelchair bay',dx,dy)
    report={
        'component':'passenger_interiors','kind':ctx['kind'],
        'passenger_seats':len(anchors),'actual_seat_mesh_instances':len(actual),
        'minimum_adjacent_armrest_gap_m':min(lateral_gaps),
        'armrest_clear_aisle_m':.530 if not ec else .541,
        'unique_detailed_seat_meshes':len({o.data.as_pointer() for o in actual}),
        'seat_layout':'2+2' if ec else '3+2 with reference end exceptions',
        'toilet_count':len(layout['toilet_rooms']),'toilet_end':'+X' if layout['toilet_end']>0 else '-X',
        'accessible_toilet':dtc,'wheelchair_space_empty':dtc,
        'DTC_accessible_layout':{'turning_circle_center_xy':[-10.62,.70],'turning_circle_diameter_m':1.50,'WC_opening_between_jambs_m':1.130,'minimum_corridor_including_handle_m':1.164,'certified_accessibility':False} if dtc else None,
        'unchanged_PAX_transforms':True,'floor_z_m':1.32,'cushion_top_z_m':1.75,
        'saloon_clear_bounds_m':layout['saloon_bounds'],
        'minimum_actual_seat_mesh_to_saloon_end_m':minclear,
        'seat_mesh_bounds':seat_bounds,
        'new_mesh_objects':len(obs),'mesh_vertices_instanced':sum(len(o.data.vertices) for o in obs),
        'mesh_triangles_instanced':sum(len(p.vertices)-2 for o in obs for p in o.data.polygons),
        'baseline_visual_replacements':removed,
        'provenance':'CAMTECH September 2022 system layouts pp28–33, with original procedural fitting detail and textile shaders',
        'limitations':['DTC cubicle outline, seat reference datums and small fittings are drawing-derived visual interpretations, not production or accessibility certification',
                       'Jacquard, weave and shelf etching are original approximations, not copied photographs',
                       'Passenger trays, recline, rotary seats and service doors are static geometry; each chair follows its own PAX anchor',
                       'TC_EC reuses the 52-seat EC layout as the disclosed eight-car derivative interpretation'],
        'camera_suggestions':{
            'CC_aisle':{'location':[-7.9,.18,2.73],'target':[6.8,.18,2.41],'lens_mm':20},
            'EC_aisle':{'location':[-7.7,0,2.75],'target':[6.8,0,2.44],'lens_mm':20},
            'seat_detail':{'location':[-1.8,.28,2.62],'target':[-2.1,-.74,2.22],'lens_mm':45},
            'mini_pantry':{'location':[10.6,.0,2.64],'target':[8.8,1.0,2.30],'lens_mm':24},
            'toilet_detail':{'location':[-9.265,.14,2.6],'target':[-9.45,1.16,1.98],'lens_mm':18},
            'toilet_cutaway':'Hide VB02_INT_service_removable_closed_door and cabin_roof, view from centre passage'},
    }
    return report
