"""WAP-7 running gear refinement. Blender 4.3+, metres, X longitudinal/Y axle.

Preserves every original rig/control datum. Replaces only legacy visible bogie
geometry and the named central underfloor equipment groups. Shared WAG9/WAP7 fabricated
bogie geometry follows IRICEN/CLW construction references; converted WAP7 brake
rigging is a representative four-cylinder system, not a TBU/PBU hybrid.
See ../references/running_gear_evidence.md for evidence and interpretation limits.

Integration: import this module and call apply(context=None). It never resets or
saves a scene and does not edit lights, cameras, roots, drivers or animation.
"""
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix
from math import sin, cos, pi

PREFIX = 'V02_RG_'
COLLECTION = PREFIX + 'Engineered running gear'
_CREATED = []
_COLL = None
_MAT = {}


def _material(name, color, metal=.25, rough=.58, dirt=False, bump=.00008):
    name=PREFIX+name
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    p=nt.nodes.new('ShaderNodeBsdfPrincipled'); out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(p.outputs['BSDF'],out.inputs['Surface'])
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough; m.diffuse_color=(*color,1)
    if dirt or bump:
        geo=nt.nodes.new('ShaderNodeNewGeometry')
        noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=48
        noise.inputs['Detail'].default_value=2; noise.inputs['Roughness'].default_value=.6
        nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
        if dirt:
            ramp=nt.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.1; ramp.color_ramp.elements[0].color=(*(c*.86 for c in color),1)
            ramp.color_ramp.elements[1].position=.9; ramp.color_ramp.elements[1].color=(*(c*1.12 for c in color),1)
            nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
            sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'],sep.inputs[0])
            mr=nt.nodes.new('ShaderNodeMapRange'); mr.clamp=True
            mr.inputs['From Min'].default_value=.15;mr.inputs['From Max'].default_value=.95
            mr.inputs['To Min'].default_value=.025;mr.inputs['To Max'].default_value=.19
            nt.links.new(sep.outputs['Z'],mr.inputs[0])
            mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.19,.145,.088,1)
            nt.links.new(mr.outputs[0],mix.inputs[0]);nt.links.new(ramp.outputs[0],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
        if bump:
            fine=nt.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=450
            fine.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],fine.inputs['Vector'])
            bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.12;bn.inputs['Distance'].default_value=bump
            nt.links.new(fine.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs['Normal'],p.inputs['Normal'])
    return m


def _mesh(name, verts, faces, material, parent, bevel=0, smooth=False, face_mats=None):
    me=bpy.data.meshes.new(PREFIX+name); me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update()
    o=bpy.data.objects.new(PREFIX+name,me);_COLL.objects.link(o)
    if parent:
        o.parent=parent; o.matrix_parent_inverse=parent.matrix_world.inverted()
    materials=material if isinstance(material,(list,tuple)) else [material]
    for m in materials:
        if m:me.materials.append(m)
    if smooth:
        for p in me.polygons:p.use_smooth=True
    if face_mats:
        for p,i in zip(me.polygons,face_mats):p.material_index=i
    if bevel:
        mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=bevel;mod.segments=3
        mod.affect='EDGES';mod.limit_method='ANGLE'
        norm=o.modifiers.new('Weighted planar normals','WEIGHTED_NORMAL');norm.keep_sharp=True
    o['component']='WAP7 running gear';o['construction']='Original geometric reconstruction from class references'
    _CREATED.append(o)
    return o


def _box(name,c,d,m,parent,b=.003):
    X,Y,Z=c;x,y,z=(v/2 for v in d)
    v=[(X+a,Y+bb,Z+cc) for a,bb,cc in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
    return _mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,parent,b)


def _prism_y(name,profile,y,thickness,m,parent,b=.003):
    # x,z profile is deliberately kept editable. Profile winding normalised.
    area=sum(profile[i][0]*profile[(i+1)%len(profile)][1]-profile[(i+1)%len(profile)][0]*profile[i][1] for i in range(len(profile)))
    if area<0:profile=list(reversed(profile))
    n=len(profile);v=[(x,yy,z) for yy in [y-thickness/2,y+thickness/2] for x,z in profile]
    f=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    return _mesh(name,v,f,m,parent,b)


def _lathe(name,center,profile,m,parent,axis='Y',segments=96,indices=None):
    # Closed lathed section; axis poles use one vertex and triangle fans.
    vs=[];rings=[]
    for a,r in profile:
        ring=[]
        for i in range(1 if abs(r)<1e-9 else segments):
            t=2*pi*i/segments;u=r*cos(t);v=r*sin(t)
            q=(u,a,v) if axis=='Y' else (a,u,v) if axis=='X' else (u,v,a)
            ring.append(len(vs));vs.append(tuple(q[k]+center[k] for k in range(3)))
        rings.append(ring)
    faces=[];mi=[]
    for j in range(len(profile)):
        a=rings[j];b=rings[(j+1)%len(profile)];idx=indices[j] if indices else 0
        if len(a)==len(b)==1:continue
        for i in range(segments):
            ii=(i+1)%segments
            if len(a)==1:f=(a[0],b[ii],b[i])
            elif len(b)==1:f=(a[i],a[ii],b[0])
            else:f=(a[i],a[ii],b[ii],b[i])
            faces.append(f);mi.append(idx)
    return _mesh(name,vs,faces,m,parent,smooth=True,face_mats=mi)


def _cyl(name,c,r,d,m,parent,axis='Z',N=32,b=0):
    vs=[]
    for a in [-d/2,d/2]:
        for i in range(N):
            u=r*cos(2*pi*i/N);v=r*sin(2*pi*i/N)
            q=(u,a,v) if axis=='Y' else (a,u,v) if axis=='X' else (u,v,a)
            vs.append(tuple(q[k]+c[k] for k in range(3)))
    fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    o=_mesh(name,vs,fs,m,parent)
    for p in o.data.polygons:p.use_smooth=(len(p.vertices)==4)
    if b:
        mod=o.modifiers.new('Machined edge radius','BEVEL');mod.width=b;mod.segments=2
    return o


def _curved_path(points,mode='flexible',steps=7):
    pts=[Vector(p) for p in points]
    if len(pts)<3:return pts
    if mode=='pipe':
        out=[pts[0]]
        for i in range(1,len(pts)-1):
            p=pts[i];before=p-pts[i-1];after=pts[i+1]-p
            if before.length<1e-6 or after.length<1e-6:continue
            d=min(.047,before.length*.30,after.length*.30)
            a=p-before.normalized()*d;b=p+after.normalized()*d
            out.append(a)
            for j in range(1,steps+1):
                t=j/steps;out.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
        out.append(pts[-1]);return out
    out=[]
    for i in range(len(pts)-1):
        p0=pts[max(i-1,0)];p1=pts[i];p2=pts[i+1];p3=pts[min(i+2,len(pts)-1)]
        for j in range(steps):
            t=j/steps
            out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    out.append(pts[-1]);return out


def _tube(name,points,r,m,parent,N=10,closed=False):
    pts=[Vector(p) for p in points]
    if not closed and 2<len(pts)<12:
        lname=name.lower()
        if any(k in lname for k in ['flexible','power cable','umbilical']):pts=_curved_path(pts,'flexible')
        elif any(k in lname for k in ['bent steel pipe','air connection','oil cooling pipe','feed elbow','air feed','brake supply pipe','compressor bent','cooler delivery pipe']):pts=_curved_path(pts,'pipe')
    if closed and (pts[0]-pts[-1]).length<1e-8:pts.pop()
    v=[];count=len(pts)
    for i,p in enumerate(pts):
        tangent=pts[(i+1)%count]-pts[(i-1)%count] if closed else pts[min(count-1,i+1)]-pts[max(0,i-1)]
        if tangent.length<1e-10:tangent=Vector((0,0,1))
        q=tangent.normalized().to_track_quat('Z','Y')
        v.extend(tuple(p+q@Vector((r*cos(2*pi*j/N),r*sin(2*pi*j/N),0))) for j in range(N))
    f=[] if closed else [tuple(reversed(range(N))),tuple(range((count-1)*N,count*N))]
    f.extend((i*N+j,i*N+(j+1)%N,((i+1)%count)*N+(j+1)%N,((i+1)%count)*N+j) for i in range(count if closed else count-1) for j in range(N))
    o=_mesh(name,v,f,m,parent,smooth=True)
    if not closed:
        o.data.polygons[0].use_smooth=False;o.data.polygons[1].use_smooth=False
    return o


def _hollow_nozzle(name,a,b,r0,r1,wall,m,parent,N=32):
    a=Vector(a);b=Vector(b);q=(b-a).normalized().to_track_quat('Z','Y');vs=[]
    for c,r in [(a,r0),(b,r1),(a,r0-wall),(b,r1-wall)]:
        vs.extend(tuple(c+q@Vector((r*cos(2*pi*i/N),r*sin(2*pi*i/N),0))) for i in range(N))
    fs=[]
    for i in range(N):
        j=(i+1)%N
        fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
    return _mesh(name,vs,fs,m,parent,smooth=True)


def _rod(name,a,b,r,m,parent,N=16):return _tube(name,[a,b],r,m,parent,N)


def _ring(name,c,ro,ri,d,m,parent,axis='Y',N=40):
    return _lathe(name,c,[(-d/2,ri),(-d/2,ro),(d/2,ro),(d/2,ri)],m,parent,axis,N)


def _bolt(name,c,parent,axis='Y',s=1,r=.012,m=None):
    m=m or _MAT['fastener']; d=.013
    _cyl(name+' washer',c,r*1.35,.0035,_MAT['washer'],parent,axis,24)
    cc=list(c); cc['XYZ'.index(axis)]+=s*.0065
    o=_cyl(name+' hex head',cc,r,d,m,parent,axis,6,b=.00055)
    for p in o.data.polygons:p.use_smooth=False
    return o


def _eye(name,p,ro,ri,depth,parent,s=1,m=None,axis='Y'):
    _ring(name+' forged eye',p,ro,ri,depth,m or _MAT['steel'],parent,axis)
    elastomer=any(k in name.lower() for k in ['damper','spheribloc'])
    _cyl(name+(' rubber spheribloc bush' if elastomer else ' greased plain-bearing bush'),p,ri*.98,depth*.85,_MAT['rubber'] if elastomer else _MAT['pin'],parent,axis,32)
    _cyl(name+' bearing pin',p,ri*.46,depth+.026,_MAT['pin'],parent,axis,24)
    ai='XYZ'.index(axis)
    if elastomer:
        for ss in [-1,1]:
            c=list(p);c[ai]+=ss*(depth/2+.014)
            _bolt(name+' pin retainer',c,parent,axis,s=ss,r=ri*.42)
    else:
        # Brake/safety pivots are steel plain pins with washer and cotter, not
        # fictional rubber joints copied from the suspension spheriblocs.
        c=list(p);c[ai]-=s*(depth/2+.013)
        _cyl(name+' headed clevis pin',c,ri*.68,.011,_MAT['fastener'],parent,axis,24,b=.0008)
        c=list(p);c[ai]+=s*(depth/2+.015)
        _ring(name+' clevis retaining washer',c,ri*.78,ri*.43,.0035,_MAT['washer'],parent,axis,32)
        # A dimensional split cotter passes through the retaining cross-hole.
        yy=c[ai]+s*.007
        clip=[]
        for u,v in [(-.018,-.004),(-.005,-.002),(.008,-.002),(.013,.001),(.012,.005),(.006,.007),(-.007,.007),(-.020,.011)]:
            q=list(p);q[ai]=yy;q[0 if axis=='Y' else 1]+=u;q[2]+=v;clip.append(q)
        _tube(name+' split cotter pin',clip,.0017,_MAT['fastener'],parent,8)


def _spring(name,x,y,z0,z1,meanr,wire,turns,parent,m=None,nested=False):
    # Ground, nearly closed end turns; real helix with open core, not stacked toroids.
    n=math.ceil(turns*64);points=[]
    for i in range(n+1):
        t=i/n; phase=t*turns*2*pi
        # first/last 0.6 turn compresses end pitch smoothly to seat.
        q=.6/turns
        h=(max(0,t-q*.5)-max(0,t-(1-q*.5)))/(1-q)
        h=max(0,min(1,h))
        points.append((x+meanr*cos(phase),y+meanr*sin(phase),z0+wire+(z1-z0-2*wire)*h))
    o=_tube(name,points,wire,m or _MAT['spring'],parent,12)
    o['spring_type']='Nested middle-axle inner coil' if nested else 'Helical steel spring with closed ground ends'
    if not nested:
        # One narrow aluminium identification band around a visible turn follows
        # the monograph's spring tolerance-batch marking, not decorative stripes.
        target=3*pi/2+2*pi*max(1,int(turns*.38))
        tt=target/(turns*2*pi);band=[]
        for j in range(9):
            t=tt+(j/8-.5)*.018/(meanr*turns*2*pi)
            phase=t*turns*2*pi;q=.6/turns
            h=(max(0,t-q*.5)-max(0,t-(1-q*.5)))/(1-q)
            band.append((x+meanr*cos(phase),y+meanr*sin(phase),z0+wire+(z1-z0-2*wire)*h))
        _tube('Spring tolerance identification band',band,wire+.00035,_MAT['band'],parent,12)
    return o


def _damper(name,a,b,parent,s=1,r=.048):
    a=Vector(a);b=Vector(b);v=b-a;u=v.normalized()
    pinaxis='X' if abs(v.y)>max(abs(v.x),abs(v.z)) else 'Y'
    _eye(name+' lower',tuple(a),r*.92,r*.52,.07,parent,s,axis=pinaxis)
    _eye(name+' upper',tuple(b),r*.92,r*.52,.07,parent,s,axis=pinaxis)
    p0=a+u*.044;p1=a+v*.64;p2=b-u*.043
    _rod(name+' lower dust tube',p0,p1,r,_MAT['damper'],parent,40)
    _rod(name+' exposed hard-chrome rod',p1,p2,r*.34,_MAT['chrome'],parent,32)
    _rod(name+' dust seal collar',p1-u*.022,p1+u*.008,r*1.06,_MAT['grease'],parent,32)
    # The upper shroud has an actual shoulder, avoiding a featureless sausage.
    _rod(name+' formed shroud end',p0,p0+u*.035,r*1.06,_MAT['steel'],parent,32)
    for p in [a,b]:
        _box(name+' mounting cheek',(p.x-s*.039,p.y,p.z) if pinaxis=='X' else (p.x,p.y-s*.039,p.z),(.026,.098,.105) if pinaxis=='X' else (.098,.026,.105),_MAT['frame'],parent,.004)


def _wheel(x,s,axle):
    # 1.092m nominal rolling-circle diameter. Inboard flange and dish are one solid.
    # Axial coordinate here is positive distance from track centre, mirrored by side.
    # The 1.596m back-to-back wheel-face convention gives room for BG flanges.
    profile=[
        (.798,.112),(.798,.453),(.798,.548),(.802,.568),(.809,.575),(.817,.574),
        (.825,.562),(.833,.551),(.846,.5475),(.873,.546),(.910,.5442),(.931,.5410),
        (.939,.532),(.939,.474),(.934,.463),(.919,.455),(.916,.438),(.909,.395),
        (.894,.305),(.910,.224),(.952,.186),(1.005,.176),(1.016,.157),(1.016,.112)]
    profile=[(s*y,r) for y,r in profile]
    # web oxide (0), rubbed tyre flank (1), polished contact band (2), hub steel (3)
    ix=[0,0,1,2,2,2,2,2,2,2,2,2,1,1,1,0,0,0,0,0,0,3,3,3]
    o=_lathe('Wheel solid forged dish and tread',(x,0,.546),profile,[_MAT['wheelweb'],_MAT['rimside'],_MAT['tread'],_MAT['hub']],axle,'Y',128,ix)
    o['nominal_tread_diameter_m']=1.092;o['flange_side']='inboard';o['wheel_back_to_back_m']=1.596
    # Small turning/gauge witness grooves follow the actual face and stay restrained.
    for rr in [.483,.514]:
        _ring('Wheel tyre face turning witness',(x,s*.9395,.546),rr+.0006,rr-.0006,.0008,_MAT['rimline'],axle,N=128)
    # Wheel hub split line/labyrinth behind the non-rotating axlebox.
    _ring('Wheel hub labyrinth',(x,s*1.018,.546),.160,.112,.014,_MAT['grease'],axle,N=64)
    return o


def _frame(bx,bog,label):
    # Welded box-section longitudinal beams. A continuous narrow upper rail with
    # deeper welded posts around guide-link anchors, rather than a flat plate cutout.
    for s in [-1,1]:
        y=s*1.12
        profile=[(-3.1045,1.02),(-2.84,1.19),(-2.24,1.19),(-2.13,1.165),(-1.48,1.165),(-1.30,1.19),
                 (-.50,1.19),(-.34,1.165),(.34,1.165),(.50,1.19),(1.30,1.19),(1.48,1.165),(2.13,1.165),(2.24,1.19),(2.84,1.19),(3.1045,1.02),
                 (3.1045,.948),(2.40,.948),(2.27,1.011),(1.43,1.011),(1.27,.936),(.48,.936),(.33,1.011),(-.33,1.011),(-.48,.936),(-1.27,.936),(-1.43,1.011),(-2.27,1.011),(-2.40,.948),(-3.1045,.948)]
        o=_prism_y('Bogie '+label+' welded longitudinal box beam',[(bx+x,z) for x,z in profile],y,.240,_MAT['frame'],bog,.007)
        o['fabrication']='Welded fabricated steel box section; not cast'
        # Top/bottom flange seams are 3mm weld beads, not random chunky strips.
        for z in [1.17,.985]:
            _tube('Longitudinal box seam',[(bx-2.70,s*1.242,z),(bx-2.23,s*1.242,z),(bx+2.23,s*1.242,z),(bx+2.70,s*1.242,z)],.0024,_MAT['weld'],bog,8)
        # Structural suspension/guide-link posts taper to their lower eyes.
        for dx in [-2.59,-.74,1.11]:
            prof=[(bx+dx-.21,.966),(bx+dx+.19,.966),(bx+dx+.125,.606),(bx+dx-.12,.606)]
            _prism_y('Fabricated guide-link drop bracket',prof,y,.190,_MAT['frame'],bog,.007)
            for oy in [-.105,.105]:
                _prism_y('Drop bracket welded gusset',[(bx+dx-.23,.955),(bx+dx+.18,.955),(bx+dx+.095,.650),(bx+dx-.075,.650)],y+oy,.015,_MAT['plate'],bog,.002)
                _tube('Guide bracket gusset weld',[(bx+dx-.226,y+oy+s*.010,.952),(bx+dx-.075,y+oy+s*.010,.650),(bx+dx+.095,y+oy+s*.010,.650),(bx+dx+.177,y+oy+s*.010,.952)],.0028,_MAT['weld'],bog,8)
            _box('Guide-link lower mounting flange',(bx+dx,y,.610),(.305,.275,.035),_MAT['steel'],bog,.006)
        # Removable inspection plugs, flame-cut lug pads, and restrained repair seam.
        for dx in [-2.48,-1.19,.62,2.44]:
            _box('Sidebeam service cover flange',(bx+dx,s*1.247,1.077),(.180,.012,.128),_MAT['plate'],bog,.007)
            _box('Sidebeam service cover gasket',(bx+dx,s*1.255,1.077),(.148,.004,.097),_MAT['grease'],bog,.004)
            _box('Sidebeam service cover',(bx+dx,s*1.259,1.077),(.139,.006,.089),_MAT['frame'],bog,.005)
            for a in [-.071,.071]:_bolt('Service cover fastener',(bx+dx+a,s*1.265,1.077),bog,s=s,r=.0075)
        for dx in [-2.13,-.32,.32,2.13]:
            _box('Primary spring locating pad',(bx+dx,y,.963),(.242,.247,.032),_MAT['steel'],bog,.004)
        # At the centre, the shared flexicoil design carries paired secondary springs.
        _box('Secondary twin spring seat',(bx,y,1.193),(.96,.34,.047),_MAT['frame'],bog,.012)
        # Lifting eye plate with a genuine hole. The opening is dimensional geometry.
        for dx in [-2.64,2.64]:
            _ring('Bogie lifting eye',(bx+dx,s*1.255,1.20),.051,.023,.031,_MAT['steel'],bog,N=40)
    # Real end headstocks and two deep transoms wrap the motors.
    for dx in [-3.0195,3.0195]:
        _box('Box-section bogie end headstock',(bx+dx,0,1.055),(.17,2.24,.25),_MAT['frame'],bog,.009)
        _box('Headstock reinforcing top flange',(bx+dx,0,1.184),(.170,2.33,.014),_MAT['steel'],bog,.004)
        for sy in [-1,1]:
            es=1 if dx>0 else -1
            _prism_y('Headstock corner gusset',[(bx+dx-es*.25,1.16),(bx+dx+es*.070,1.16),(bx+dx-es*.08,.91)],sy*.98,.045,_MAT['steel'],bog,.006)
    for dx in [-.925,.925]:
        _box('Deep welded bogie cross transom',(bx+dx,0,.978),(.255,2.20,.340),_MAT['frame'],bog,.008)
        for y in [-.70,.70]:
            _box('Traction motor nose suspension foundation',(bx+dx,y,.794),(.19,.145,.115),_MAT['steel'],bog,.007)


def _axlebox(x,s,bog,middle=False):
    y=s*1.12
    # The axlebox wing casting is borne by its journal, with shelves under the springs.
    profile=[(-.402,.748),(-.385,.778),(-.19,.754),(-.145,.722),(.145,.722),(.19,.754),(.385,.778),(.402,.748),
             (.393,.703),(.344,.690),(.191,.404),(.141,.365),(-.141,.365),(-.191,.404),(-.344,.690),(-.393,.703)]
    _prism_y('Axlebox wing housing',[(x+a,z) for a,z in profile],y,.232,_MAT['axlebox'],bog,.012)
    # Main journal case stepped front face and cap, not a button on a square cube.
    _cyl('Journal bearing cylindrical barrel',(x,s*1.16,.546),.177,.226,_MAT['axlebox'],bog,'Y',64,b=.004)
    _ring('Journal cap flanged machined shoulder',(x,s*1.289,.546),.179,.141,.023,_MAT['steel'],bog,N=64)
    _cyl('Journal inspection cap',(x,s*1.305,.546),.142,.022,_MAT['axlebox'],bog,'Y',64,b=.005)
    _cyl('Journal central raised boss',(x,s*1.321,.546),.070,.012,_MAT['steel'],bog,'Y',48,b=.003)
    _ring('Journal cap oil-dark gasket',(x,s*1.317,.546),.144,.139,.003,_MAT['grease'],bog,N=64)
    for k in range(6):
        a=2*pi*k/6+pi/6
        _bolt('Journal cover bolt',(x+.155*cos(a),s*1.306,.546+.155*sin(a)),bog,s=s,r=.013)
    # Drain/greasing plug at the low point, and a grease-dark joint only there.
    _bolt('Axlebox drain plug',(x,s*1.289,.397),bog,s=s,r=.015,m=_MAT['grease'])
    for off in [-.27,.27]:
        _cyl('Primary spring compensating shim',(x+off,y,.777),.126,.009,_MAT['shim'],bog,N=48)
        _cyl('Primary spring insulating base',(x+off,y,.787),.123,.011,_MAT['rubber'],bog,N=48)
        _cyl('Primary spring lower locating lip',(x+off,y,.797),.114,.009,_MAT['steel'],bog,N=48)
        _spring('Primary nested outer spring' if middle else 'Primary end-axle coil spring',x+off,y,.804,.996,.096,.0155,4.20,bog)
        if middle:_spring('Middle axle inner nested coil',x+off,y,.806,.994,.056,.0108,5.00,bog,_MAT['spring_inner'],True)
        _cyl('Primary upper spring insulating pad',(x+off,y,1.002),.123,.009,_MAT['rubber'],bog,N=48)
        _cyl('Primary upper retaining plate',(x+off,y,1.010),.128,.012,_MAT['steel'],bog,N=48)
        # Wing casting triangular rib and spring-centre locating nub are structural.
        _prism_y('Axlebox wing reinforcing rib',[(x+off-.12,.723),(x+off+.12,.723),(x+off*.52,.509)],s*1.248,.018,_MAT['steel'],bog,.004)
    if not middle:
        _damper('Primary end-axle vertical damper',(x,s*1.343,.659),(x,s*1.343,1.186),bog,s,r=.047)
    else:
        # Middle axle has a safety lifting link, expressly no hydraulic damper.
        _box('Middle axle lifting safety strap',(x,s*1.343,.892),(.072,.045,.420),_MAT['steel'],bog,.008)
        for z in [.706,1.082]:_eye('Middle-axle safety-link', (x,s*1.343,z),.052,.026,.068,bog,s)
    # Guide link runs longitudinally from the box to the tapered bogie post.
    a=(x-.13,s*1.17,.579);b=(x-.74,s*1.17,.615)
    _rod('Forged wheelset guide rod',a,b,.038,_MAT['steel'],bog,24)
    for p in [a,b]:_eye('Guide-link spheribloc',p,.074,.044,.134,bog,s)
    # Earth brush and speed pickup use one small outlet and a clipped flexible loop.
    _cyl(('Axle speed-pulse pickup gland' if s<0 else 'Axle earthing-brush cable gland'),(x+.113,s*1.329,.582),.016,.032,_MAT['fastener'],bog,'Y',20)
    _tube(('Axle speed-pulse flexible lead' if s<0 else 'Axle earthing-brush flexible lead'),[(x+.113,s*1.349,.582),(x+.21,s*1.364,.658),(x+.25,s*1.366,.829),(x+.17,s*1.349,.904),(x+.10,s*1.290,.927)],.008,_MAT['cable'],bog,10)
    _box('Sensor cable retaining clip',(x+.10,s*1.29,.93),(.034,.025,.040),_MAT['fastener'],bog,.002)


def _arc_block(name,x,s,angle,r0,r1,a0,a1,y0,y1,m,bog):
    n=20;vs=[]
    for y in [s*y0,s*y1]:
        for r in [r0,r1]:
            for i in range(n+1):
                a=angle+a0+(a1-a0)*i/n;vs.append((x+r*cos(a),y,.546+r*sin(a)))
    k=n+1;f=[]
    for i in range(n):
        f.extend([(i,i+1,2*k+i+1,2*k+i),(k+i,3*k+i,3*k+i+1,k+i+1),
                  (i,k+i,k+i+1,i+1),(2*k+i,2*k+i+1,3*k+i+1,3*k+i)])
    f.extend([(0,2*k,3*k,k),(n,k+n,3*k+n,2*k+n)])
    return _mesh(name,vs,f,m,bog,bevel=.0015)


def _brakes(bx,bog,label):
    # Conventional converted WAP7 clasp rigging: four cylinders per bogie.
    # Brake shoes are curved around the tread with physical release clearance.
    for s in [-1,1]:
        for ai,dx in enumerate([-1.85,0,1.85]):
            x=bx+dx
            for end in [-1,1]:
                angle=0 if end==1 else pi
                _arc_block('Curved composite tread brake block',x,s,angle,.552,.582,-.235,.235,.848,.938,_MAT['brake'],bog)
                _arc_block('Curved cast brake shoe backing',x,s,angle,.584,.606,-.265,.265,.837,.954,_MAT['steel'],bog)
                # Backing shoe key and retainer can be read in wheel closeups.
                _box('Brake shoe locking key',(x+end*.610,s*.897,.546),(.013,.075,.110),_MAT['fastener'],bog,.003)
                _cyl('Brake shoe hanger pivot',(x+end*.602,s*1.005,.546),.036,.143,_MAT['pin'],bog,'Y',32)
                # Two flat steel hanging straps with upper and lower eyes.
                hx=x+end*.615
                for yy in [.986,1.034]:
                    profile=[(hx-.034,.553),(hx+.034,.553),(hx+end*.032+.030,1.042),(hx+end*.032-.030,1.042)]
                    _prism_y('Brake hanger steel strap',profile,s*yy,.016,_MAT['steel'],bog,.003)
                _eye('Brake hanger upper pivot',(hx+end*.032,s*1.015,1.030),.045,.022,.118,bog,s)
                # Drop lever connects the shoe pivot to the bottom pull rod.
                _prism_y('Brake lower crank lever',[(hx-.037,.565),(hx+.037,.565),(hx+end*.045+.041,.320),(hx+end*.045-.041,.320)],s*1.024,.028,_MAT['steel'],bog,.004)
                _eye('Brake pull-rod clevis pin',(hx+end*.045,s*1.058,.337),.038,.019,.088,bog,s)
            # Low mounted pull bar with forged clevis ends, adjustment holes and locknuts.
            y=s*1.120; z=.337
            _rod('Brake wheel tie pull rod',(x-.621,y,z),(x+.621,y,z),.0175,_MAT['rod'],bog,24)
            for end in [-1,1]:
                ex=x+end*.580
                for yy in [-.030,.030]:_box('Brake pull-rod fork leaf',(ex,y+yy,z),(.150,.015,.043),_MAT['steel'],bog,.003)
                for step in [0,.055]:
                    _cyl('Brake tie adjusting hex locknut',(x+end*(.37+step),y,z),.027,.021,_MAT['fastener'],bog,'X',6)
            # Inter-wheel compensating connection, behind the visible primary suspension.
            if ai<2:_rod('Longitudinal brake equalising rod',(x+.64,s*.75,.760),(x+1.85-.64,s*.75,.760),.018,_MAT['rod'],bog,16)
        # Each side has two separate top-mounted cylinders driving bellcrank shafts.
        for direction in [-1,1]:
            cx=bx+direction*1.22;cy=s*.975;cz=1.249
            _box('Brake cylinder welded mounting stool',(cx,cy,1.135),(.34,.265,.078),_MAT['frame'],bog,.005)
            profile=[(-.21,0),(-.21,.098),(-.198,.115),(-.175,.119),(.145,.119),(.175,.110),(.183,.097),(.183,0)]
            _lathe('Conventional pneumatic brake cylinder',(cx,cy,cz),profile,_MAT['cylinder'],bog,'X',64)
            # Cast end plate flange, six tie bolts, piston boot and pushrod.
            for d in [-.185,.160]:_ring('Brake cylinder end flange',(cx+d,cy,cz),.124,.107,.016,_MAT['steel'],bog,'X',64)
            for k in range(6):
                a=2*pi*k/6
                yy=cy+.113*cos(a);zz=cz+.113*sin(a)
                _rod('Brake cylinder through stud',(cx-.195,yy,zz),(cx+.177,yy,zz),.006,_MAT['fastener'],bog,10)
                _bolt('Brake cylinder end nut',(cx-.200,yy,zz),bog,axis='X',s=-1,r=.010)
            px=cx-direction*.21;pe=px-direction*.22
            _rod('Brake cylinder piston push rod',(px,cy,cz),(pe,cy,cz),.021,_MAT['chrome'],bog,32)
            _rod('Brake piston protective boot',(px,cy,cz),(px-direction*.080,cy,cz),.034,_MAT['rubber'],bog,32)
            _eye('Brake cylinder output fork',(pe,cy,cz),.043,.024,.105,bog,s)
            # Bellcrank plate and transverse shaft transmit cylinder force down to rigging.
            qx=pe-direction*.060
            _prism_y('Top brake bellcrank plate',[(pe,cz+.035),(pe,cz-.035),(qx,.944),(qx-direction*.055,.965),(qx-direction*.010,1.070)],cy,.027,_MAT['steel'],bog,.003)
            if s==-1:_cyl('Top brake bellcrank cross shaft',(qx,0,1.040),.026,1.950,_MAT['rod'],bog,'Y',24)
            _rod('Brake cylinder actuating drop link',(qx,cy,1.020),(qx+direction*.27,s*.75,.760),.018,_MAT['rod'],bog,20)
            # 3/8-inch air pipe, compression elbows, connection hose and protective loop.
            p=(cx+.10,cy,cz+.118)
            _cyl('Brake cylinder air inlet union',p,.020,.051,_MAT['fastener'],bog,'Z',6)
            _tube('Brake cylinder flexible air connection',[p,(p[0]+.08,cy,1.43),(p[0]+.20,s*1.23,1.42),(p[0]+.23,s*1.255,1.21)],.009,_MAT['cable'],bog,12)
        # Pipe snakes around a pair of frame mounting brackets, with proper clips/unions.
        _tube('Clipped longitudinal brake supply pipe',[(bx-2.71,s*1.272,1.138),(bx-2.41,s*1.272,1.138),(bx-2.33,s*1.272,1.108),(bx-1.55,s*1.272,1.108),(bx-1.46,s*1.272,1.138),(bx+2.71,s*1.272,1.138)],.0105,_MAT['pipe'],bog,12)
        for dx in [-2.44,-1.58,-.55,.52,1.60,2.44]:
            _box('Brake air pipe saddle',(bx+dx,s*1.264,1.133),(.024,.040,.054),_MAT['fastener'],bog,.003)
            _bolt('Brake pipe saddle fixing',(bx+dx,s*1.287,1.160),bog,s=s,r=.007)
        for dx in [-1.40,1.37]:
            _cyl('Brake air pipe hex union',(bx+dx,s*1.272,1.138),.017,.034,_MAT['fastener'],bog,'X',6)


def _motor(x,bog,drive_sign=1):
    # ABB-family axle-hung nose-suspended motor mass, casing and gearcase.
    # No fictitious ventilated disc brakes occupy the gear/motor clearances.
    mx=x+.39;z=.617
    prof=[(-.575,.19),(-.575,.24),(-.534,.280),(-.480,.306),(.44,.306),(.485,.291),(.535,.240),(.535,.19)]
    _lathe('Axle-hung traction motor main casing',(mx,0,z),prof,_MAT['motor'],bog,'Y',64)
    _box('Traction motor top terminal housing',(mx,0,.905),(.40,.77,.095),_MAT['motor'],bog,.021)
    _box('Traction motor removable terminal lid',(mx,0,.958),(.375,.72,.014),_MAT['plate'],bog,.008)
    for xx in [-.155,.155]:
        for yy in [-.305,.305]:_bolt('Motor terminal-lid bolt',(mx+xx,yy,.973),bog,'Z',r=.009)
    # Distinct endshields, flange joints and the external cooling ribs.
    for sy in [-1,1]:
        _ring('Motor endshield annular flange',(mx,sy*.505,z),.288,.213,.033,_MAT['steel'],bog,N=64)
        for k in range(12):
            a=2*pi*k/12
            _bolt('Motor endshield fastener',(mx+.256*cos(a),sy*.53,z+.256*sin(a)),bog,s=sy,r=.009)
        for k in range(9):
            a=pi*.12+pi*.76*k/8
            _rod('Motor cooling cast rib',(mx+.297*cos(a),sy*.25,z+.297*sin(a)),(mx+.297*cos(a),sy*.48,z+.297*sin(a)),.010,_MAT['steel'],bog,8)
    # Gear housing is a recognisable offset figure-eight case around axle and pinion.
    sy=drive_sign
    gp=[(x-.355,.36),(x-.377,.50),(x-.35,.72),(x-.23,.86),(x+.01,.91),(mx+.19,.84),(mx+.30,.69),(mx+.30,.51),(mx+.22,.40),(x+.16,.30),(x-.18,.30)]
    _prism_y('Bolted final-drive gearcase',gp,sy*.638,.186,_MAT['motor'],bog,.017)
    # A two-part housing has an actual circumferential split flange and drain point.
    _prism_y('Gearcase split flange',gp,sy*.738,.018,_MAT['steel'],bog,.005)
    for xx,zz in gp[:-1]:_bolt('Gearcase flange bolt',(xx,sy*.756,zz),bog,s=sy,r=.009)
    _bolt('Gearcase oil drain',(x-.08,sy*.756,.337),bog,s=sy,r=.016,m=_MAT['grease'])
    _cyl('Gearcase filler breather',(x+.16,sy*.64,.907),.024,.068,_MAT['fastener'],bog,'Z',8)
    # Actual axle suspension tube and the nose link mount occupy centre bay.
    _ring('Motor axle suspension hollow tube',(x,0,.546),.173,.114,1.02,_MAT['motor'],bog,N=64)
    for yy in [-.38,.38]:
        _box('Motor nose support lug',(mx+.31,yy,.772),(.17,.10,.125),_MAT['steel'],bog,.008)
        _eye('Motor nose suspension spheribloc',(mx+.32,yy,.797),.055,.027,.10,bog,1)
    for k in range(3):
        y=-.16+k*.16
        _tube('Motor power cable service loop',[(mx-.07,y,.981),(mx+.09,y,.993),(mx+.27,y,1.042),(mx+.48,y,1.100),(x+.925,y,1.154)],.015,_MAT['cable'],bog,12)
        _cyl('Motor cable gland',(mx-.07,y,.973),.023,.043,_MAT['fastener'],bog,'Z',6)


def _secondary(bx,bog,label):
    for s in [-1,1]:
        for dx in [-.255,.255]:
            _cyl('Secondary spring insulating seat',(bx+dx,s*1.12,1.229),.170,.023,_MAT['rubber'],bog,N=64)
            _cyl('Secondary spring compensation plate',(bx+dx,s*1.12,1.246),.165,.013,_MAT['shim'],bog,N=64)
            _spring('Secondary flexicoil 575mm loaded',bx+dx,s*1.12,1.253,1.828,.1255,.0265,9.50,bog)
            _cyl('Secondary upper rubber seat',(bx+dx,s*1.12,1.836),.165,.016,_MAT['rubber'],bog,N=64)
            _cyl('Secondary upper body pocket flange',(bx+dx,s*1.12,1.853),.175,.018,_MAT['steel'],bog,N=64)
        _damper('Secondary vertical damper',(bx+.595,s*1.320,.983),(bx+.595,s*1.320,1.544),bog,s,r=.059)
        _damper('Secondary longitudinal yaw damper',(bx-1.405,s*1.205,1.283),(bx-.500,s*1.205,1.343),bog,s,r=.060)
        # Transverse damper and progressive rubber bump stop.
        _damper('Secondary lateral damper',(bx+.63,s*.46,1.27),(bx+.63,s*1.07,1.27),bog,s,r=.048)
        _box('Lateral bump-stop steel seat',(bx+.78,s*1.17,1.273),(.18,.20,.105),_MAT['steel'],bog,.006)
        _box('Lateral progressive rubber stop',(bx+.78,s*1.17,1.350),(.14,.155,.067),_MAT['rubber'],bog,.012)
        # Safety chain has alternating link planes and is visibly attached at both ends.
        for i in range(8):
            z=1.125+i*.045;xx=bx-.018+sin(i*pi/7)*.018;yy=s*1.32
            points=[]
            for j in range(32):
                a=2*pi*j/32;u=.014*cos(a);v=.029*sin(a)
                points.append((xx+u,yy,z+v) if i%2==0 else (xx,yy+u,z+v))
            _tube('Secondary suspension safety chain link',points,.0048,_MAT['chain'],bog,8,True)
        for z in [1.115,1.468]:_eye('Safety-chain attachment eye',(bx,s*1.32,z),.033,.019,.037,bog,s)


def _sand_and_services(bx,bog,label):
    for s in [-1,1]:
        for end in [-1,1]:
            x=bx+end*2.565;y=s*1.03
            # Rectangular hopper with sloped lower funnel, hinged access lid and latch.
            profile=[(x-.195,1.013),(x+.195,1.013),(x+.195,.823),(x+.105,.751),(x-.105,.751),(x-.195,.823)]
            _prism_y('Sand hopper welded body',profile,y,.375,_MAT['sandbox'],bog,.007)
            _box('Sand hopper flanged lid',(x,y,1.027),(.418,.397,.024),_MAT['steel'],bog,.006)
            _box('Sand hopper filler cover',(x,y,1.046),(.230,.275,.019),_MAT['sandbox'],bog,.005)
            for dx in [-.080,.080]:
                _cyl('Sand lid hinge knuckle',(x+dx,y+s*.128,1.060),.012,.052,_MAT['steel'],bog,'X',20)
                _bolt('Sand lid fastener',(x+dx,y-s*.125,1.062),bog,'Z',r=.009)
            _box('Sand lid latch plate',(x,y-s*.150,1.06),(.08,.04,.008),_MAT['fastener'],bog,.002)
            _cyl('Sand ejector body',(x,y,.718),.034,.081,_MAT['steel'],bog,'Z',24)
            # End delivery points aim at the rail ahead of the outer wheel contact.
            wx=bx+end*1.85;tipx=wx+end*.35
            _tube('Sand delivery bent steel pipe',[(x,y,.707),(x-end*.02,s*.990,.587),(tipx+end*.12,s*.884,.283),(tipx,s*.872,.115)],.017,_MAT['pipe'],bog,16)
            _hollow_nozzle('Open-bore sand delivery nozzle',(tipx+end*.036,s*.875,.164),(tipx,s*.872,.114),.019,.024,.0025,_MAT['steel'],bog)
            _tube('Sand ejector compressed-air feed',[(x+end*.14,s*1.275,1.136),(x+end*.19,s*1.277,.904),(x+end*.11,s*1.21,.715),(x,s*1.03,.719)],.008,_MAT['pipe'],bog,12)
            _box('Sand pipe support lug',(x-end*.008,s*1.04,.644),(.05,.055,.130),_MAT['steel'],bog,.003)
            _bolt('Sand delivery clamp bolt',(x-end*.008,s*1.076,.624),bog,s=s,r=.008)
        # Local distribution manifold with unions and a drain cock, no arbitrary loose pipes.
        mx=bx-1.015
        _box('Bogie air distribution manifold',(mx,s*1.291,1.052),(.162,.076,.073),_MAT['steel'],bog,.009)
        for dx in [-.055,.055]:
            _cyl('Air manifold compression fitting',(mx+dx,s*1.337,1.053),.015,.035,_MAT['fastener'],bog,'Y',6)
        _cyl('Manifold drain cock',(mx,s*1.296,.993),.013,.052,_MAT['fastener'],bog,'Z',6)
        _rod('Manifold drain handle',(mx-.025,s*1.296,.975),(mx+.025,s*1.296,.975),.0045,_MAT['red'],bog,8)
    # Flexible heavy traction link towards locomotive centre, with bolted rubber bushing.
    inward=1 if bx<0 else -1
    p0=(bx+inward*2.94,0,.615);p1=(bx+inward*3.85,0,.600)
    _rod('Low-slung central traction link',p0,p1,.073,_MAT['steel'],bog,32)
    for p in [p0,p1]:_eye('Traction-link rubber spheribloc',p,.133,.075,.250,bog,1)
    _box('Traction-link bogie mounting fork',(p0[0],0,.684),(.25,.36,.115),_MAT['frame'],bog,.010)
    # Distinct near-bogie flexible service umbilical into underframe.
    for k in range(3):
        y=-.37+k*.095
        _tube('Bogie flexible services umbilical',[(bx+inward*2.40,y,1.12),(bx+inward*2.70,y,1.24),(bx+inward*2.83,y,.98),(bx+inward*3.04,y,1.21),(bx+inward*3.13,y,1.40)],.013 if k else .020,_MAT['cable'],bog,12)


def _bolt_normal(name,p,n,parent,r=.010):
    p=Vector(p);n=Vector(n).normalized()
    _rod(name+' washer',p-n*.0015,p+n*.0020,r*1.4,_MAT['washer'],parent,24)
    o=_rod(name+' hex head',p+n*.0020,p+n*.014,r,_MAT['fastener'],parent,6)
    for f in o.data.polygons:f.use_smooth=False


def _compressor(end,body):
    """Photo-led RR20100 CG-M-style W compressor, not an underfloor air tank.
    Manufacturer envelope reference1450x871x768mm; brackets/routing representative.
    The motor sits below the bogie headstock, while tall pump heads face the tank.
    """
    side=-end
    def P(u,v,z):return (end*(2.200-u),side*(.750+v),z)
    def N(v):return Vector((-end*v[0],side*v[1],v[2]))
    # Open fabricated skid; standing feet remain on the underslung mounting cradle.
    for v in [-.335,.335]:
        _box('Compressor base folded channel',P(0,v,.374),(1.390,.048,.074),_MAT['frame'],body,.005)
    for u in [-.590,.500]:
        _box('Compressor base crossmember',P(u,0,.374),(.092,.720,.074),_MAT['frame'],body,.005)
    # Direct-coupled20hp three-phase induction motor, finned body and removable fan cover.
    mp=[(-.320,0),(-.320,.145),(-.297,.173),(-.248,.180),(.240,.180),(.283,.169),(.312,.141),(.320,0)]
    _lathe('Compressor induction motor body',P(-.325,0,.640),[(end*-u,r) for u,r in mp],_MAT['motor'],body,'X',64)
    for k in range(16):
        ang=2*pi*k/16;v=.186*cos(ang);z=.640+.186*sin(ang)
        _rod('Compressor motor axial cooling fin',P(-.562,v,z),P(-.095,v,z),.007,_MAT['steel'],body,8)
    for u in [-.558,-.100]:
        for v in [-.124,.124]:
            _box('Compressor motor cast mounting foot',P(u,v,.451),(.150,.091,.041),_MAT['motor'],body,.009)
            _bolt('Compressor motor foot bolt',P(u,v,.478),body,'Z',r=.012)
    _ring('Compressor motor rear fan casing',P(-.670,0,.640),.184,.158,.064,_MAT['motor'],body,'X',64)
    _cyl('Compressor fan dark recessed hub',P(-.672,0,.640),.039,.023,_MAT['steel'],body,'X',32)
    for k in range(20):
        a=2*pi*k/20
        _rod('Compressor fan guard radial wire',P(-.708,.039*cos(a),.640+.039*sin(a)),P(-.708,.166*cos(a),.640+.166*sin(a)),.0028,_MAT['steel'],body,8)
    for rr in [.076,.120,.160]:_ring('Compressor fan guard concentric ring',P(-.710,0,.640),rr+.0025,rr-.0025,.005,_MAT['steel'],body,'X',64)
    # Motor terminal box and supported flexible power lead to the underframe.
    _box('Compressor motor electrical terminal box',P(-.340,.209,.710),(.218,.109,.160),_MAT['motor'],body,.016)
    _box('Compressor terminal-box gasket',P(-.340,.268,.710),(.201,.008,.143),_MAT['rubber'],body,.008)
    _box('Compressor terminal-box cover',P(-.340,.275,.710),(.195,.008,.137),_MAT['plate'],body,.008)
    for u in [-.417,-.263]:
        for z in [.663,.757]:_bolt('Compressor terminal-box screw',P(u,.284,z),body,s=side,r=.007)
    _tube('Compressor electrical flexible supply', [P(-.33,.26,.80),P(-.39,.27,.94),P(-.47,.23,1.15),P(-.50,.17,1.523)],.017,_MAT['cable'],body,14)
    # Coupling guard is open rod/annulus geometry, surrounding the real shaft.
    _cyl('Compressor direct-drive shaft',P(.010,0,.640),.036,.176,_MAT['pin'],body,'X',32)
    for u in [-.030,.080]:_ring('Compressor coupling guard end ring',P(u,0,.640),.145,.133,.015,_MAT['steel'],body,'X',48)
    for k in range(18):
        a=2*pi*k/18
        _rod('Compressor coupling guard grille',P(-.03,.139*cos(a),.640+.139*sin(a)),P(.08,.139*cos(a),.640+.139*sin(a)),.0035,_MAT['steel'],body,8)
    # W-arranged three cylinder pump: cast crankcase, crank-end cover and oil ports.
    _box('W compressor crankcase',P(.300,0,.583),(.432,.456,.323),_MAT['motor'],body,.036)
    _cyl('Compressor crank-end bearing housing',P(.535,0,.586),.140,.067,_MAT['motor'],body,'X',56)
    _ring('Compressor crank-end gasket',P(.572,0,.586),.125,.115,.004,_MAT['grease'],body,'X',48)
    for k in range(6):
        a=2*pi*k/6;_bolt('Compressor crank cover bolt',P(.579,.101*cos(a),.586+.101*sin(a)),body,'X',s=-end,r=.009)
    _cyl('Compressor oil-level window rim',P(.343,.237,.585),.029,.026,_MAT['steel'],body,'Y',32)
    _cyl('Compressor oil-level inspection glass',P(.343,.253,.585),.020,.007,_MAT['grease'],body,'Y',40)
    _bolt('Compressor oil sump drain',P(.302,.242,.465),body,s=side,r=.015,m=_MAT['grease'])
    for angle,diam in [(-48,.112),(0,.083),(48,.112)]:
        t=math.radians(angle);direction=N((0,sin(t),cos(t))).normalized()
        root=Vector(P(.29,.056*sin(t),.698));length=.305 if angle else .326
        top=root+direction*length
        _rod('Compressor finned cylinder barrel',root,top,diam*.70,_MAT['motor'],body,48)
        for i in range(11):
            c=root+direction*(.019+i*.025)
            _rod('Compressor cylinder cooling fin',c-direction*.0038,c+direction*.0038,diam,_MAT['motor'],body,48)
        _rod('Compressor cylinder flanged head',top-direction*.013,top+direction*.013,diam*1.04,_MAT['motor'],body,48)
        q=direction.to_track_quat('Z','Y')
        for k in range(6):
            a=2*pi*k/6;pt=top+direction*.015+q@Vector((diam*.82*cos(a),diam*.82*sin(a),0))
            _bolt_normal('Compressor cylinder-head bolt',pt,direction,body,.008)
        # Two serviceable valve covers per head are seated on the machined head face.
        for off in [-.038,.038]:
            c=top+direction*.020+N((off,0,0))
            _rod('Compressor inlet-discharge valve cap',c,c+direction*.018,.028,_MAT['steel'],body,32)
    # Dual suction filter canisters and the curved black intake hoses visible in photos.
    for v in [-.235,.235]:
        _cyl('Compressor black suction-filter canister',P(-.135,v,1.0),.105,.170,_MAT['cable'],body,'Y',56,b=.003)
        outward=1 if v>0 else -1
        _ring('Compressor filter cap rolled seam',P(-.135,v+outward*.086,1.0),.106,.099,.009,_MAT['steel'],body,'Y',48)
        _cyl('Compressor filter removable end cap',P(-.135,v+outward*.092,1.0),.098,.008,_MAT['plate'],body,'Y',48)
        _bolt('Compressor filter retaining screw',P(-.135,v+outward*.102,1.0),body,s=side*outward,r=.009)
        _tube('Compressor flexible suction connection',[P(-.07,v,.958),P(.060,v,.925),P(.18,v*.85,.91),P(.27,v*.77,.905)],.025,_MAT['cable'],body,14)
    # Aftercooler with a genuinely open fine metal guard over the dark fin core.
    _box('Compressor aftercooler fin core',P(.641,0,.667),(.091,.640,.427),_MAT['motor'],body,.008)
    for v in [-.330,.330]:_box('Compressor cooler side flange',P(.692,v,.667),(.041,.026,.458),_MAT['steel'],body,.004)
    for z in [.440,.894]:_box('Compressor cooler horizontal flange',P(.692,0,z),(.041,.681,.027),_MAT['steel'],body,.004)
    for i in range(26):_box('Compressor cooler guard horizontal bar',P(.719,0,.461+i*.0164),(.005,.637,.0033),_MAT['steel'],body,.0008)
    for i in range(29):_box('Compressor cooler guard vertical bar',P(.721,-.307+i*.0219,.667),(.004,.0035,.412),_MAT['steel'],body,.0008)
    for v in [-.301,.301]:
        for z in [.471,.863]:_bolt('Compressor cooler guard screw',P(.726,v,z),body,'X',s=-end,r=.007)
    _cyl('Compressor power-cable floor gland',P(-.50,.17,1.474),.027,.036,_MAT['fastener'],body,'Z',6)
    # Flanged delivery pipes run from the head to cooler and up to the body air system.
    _tube('Compressor bent interstage discharge',[P(.30,.33,.927),P(.39,.386,.90),P(.54,.396,.67),P(.62,.335,.513)],.025,_MAT['pipe'],body,14)
    _tube('Compressor cooler delivery pipe',[P(.64,-.33,.82),P(.57,-.385,.88),P(.16,-.390,.865),P(-.23,-.390,1.12),P(-.27,-.36,1.525)],.023,_MAT['pipe'],body,14)
    _cyl('Compressor air-delivery bulkhead nut',P(-.27,-.36,1.475),.039,.032,_MAT['fastener'],body,'Z',6)
    _ring('Compressor air-delivery floor flange',P(-.27,-.36,1.491),.056,.025,.012,_MAT['steel'],body,'Z',40)
    for u,v,z in [(.30,.33,.927),(.62,.335,.513),(.64,-.33,.82)]:
        _cyl('Compressor discharge-pipe hex union',P(u,v,z),.038,.032,_MAT['fastener'],body,'Y',6)
    # Underslung mounting cradles with explicit wire-rope isolators, not tank straps.
    for u in [-.584,.517]:
        for v in [-.360,.360]:
            _box('Compressor cradle vertical strap',P(u,v,.760),(.037,.033,.755),_MAT['steel'],body,.005)
            _box('Compressor isolator lower shoe',P(u,v,1.133),(.115,.095,.021),_MAT['frame'],body,.004)
            for k in range(4):
                pts=[]
                for j in range(28):
                    a=2*pi*j/28;pts.append(P(u-.038+k*.025,v+.035*cos(a),1.181+.038*sin(a)))
                _tube('Compressor wire-rope vibration isolator',pts,.0035,_MAT['chain'],body,8,True)
            _box('Compressor isolator upper shoe',P(u,v,1.224),(.135,.102,.022),_MAT['frame'],body,.004)
            _box('Compressor frame hanging tab',P(u,v,1.276),(.045,.084,.102),_MAT['steel'],body,.004)
            _bolt('Compressor frame-hanger fastening',P(u,v,1.337),body,'Z',r=.012)
    # Corresponding body support ties both hanging ends into existing crossmembers.
    for u,dx in [(.517,.467),(-.584,.316)]:
        x=end*(2.200-u)
        _box('Compressor body suspension cross tie',(x,side*.750,1.325),(.125,.885,.035),_MAT['frame'],body,.005)
        _box('Compressor body upper longitudinal bracket',(end*(2.200-u+dx/2),side*.750,1.400),(abs(dx)+.080,.165,.150),_MAT['frame'],body,.005)


def _underfloor(body):
    # Central transformer tank, two battery boxes and underslung compressors. The detailed
    # exterior is representative; no claim is made for invisible internal wiring.
    _box('Traction transformer tank', (0,0,.976),(2.90,1.98,.520),_MAT['equipment'],body,.035)
    _box('Transformer lower sump', (0,0,.696),(2.55,1.72,.110),_MAT['motor'],body,.028)
    # Explicit welded transverse supports connect the heavy tank to the open
    # perimeter underframe; they replace the support formerly implied by a slab.
    for x in [-1.15,1.15]:
        _box('Transformer mounting transverse web',(x,0,1.405),(.020,2.990,.164),_MAT['frame'],body,.004)
        for z in [1.319,1.491]:
            _box('Transformer mounting beam flange',(x,0,z),(.180,2.990,.016),_MAT['steel'],body,.003)
        for sy in [-1,1]:
            _box('Transformer vertical suspension lug',(x,sy*1.106,1.301),(.192,.052,.128),_MAT['steel'],body,.006)
            _box('Transformer hanger upper seat',(x,sy*1.106,1.327),(.245,.158,.025),_MAT['frame'],body,.004)
            for dx in [-.070,.070]:_bolt('Transformer suspension securing bolt',(x+dx,sy*1.106,1.349),body,'Z',r=.015)
    for s in [-1,1]:
        # Tank seam, folded corner flanges, service panels, and mounting outriggers.
        _box('Transformer cover flange',(0,s*1.003,1.193),(2.93,.043,.034),_MAT['steel'],body,.004)
        for dx in [-1.35,-.90,-.45,0,.45,.90,1.35]:
            _bolt('Transformer flange fastener',(dx,s*1.03,1.190),body,s=s,r=.010)
        for dx in [-1.32,-.65,.65,1.32]:
            _box('Transformer folded vertical rib',(dx,s*1.013,.973),(.048,.037,.385),_MAT['plate'],body,.004)
        for dx in [-1.03,.0,1.03]:
            _box('Transformer gasketed side inspection cover',(dx,s*1.025,.978),(.52,.038,.288),_MAT['plate'],body,.012)
            for xx in [-.22,.22]:
                for zz in [-.108,.108]:_bolt('Transformer cover bolt',(dx+xx,s*1.05,.978+zz),body,s=s,r=.009)
        for dx in [-1.15,1.15]:
            _box('Transformer body mounting outrigger',(dx,s*1.106,1.195),(.255,.26,.150),_MAT['frame'],body,.009)
            for xx in [-.082,.082]:_bolt('Transformer mounting bolt',(dx+xx,s*1.243,1.224),body,s=s,r=.018)
        # Physical large oil hose connections run to tank fittings and their clips.
        for dx in [-1.20,1.20]:
            _tube('Transformer oil cooling pipe',[(dx,s*.970,.920),(dx,s*1.105,.920),(dx*.94,s*1.162,1.087),(dx*.86,s*1.163,1.518)],.028,_MAT['pipe'],body,16)
            _cyl('Transformer oil union',(dx,s*1.039,.921),.046,.068,_MAT['fastener'],body,'Y',8)
            _cyl('Transformer oil-pipe floor bulkhead nut',(dx*.86,s*1.163,1.475),.040,.027,_MAT['fastener'],body,'Z',6)
            _ring('Transformer oil-pipe bulkhead flange',(dx*.86,s*1.163,1.490),.061,.029,.012,_MAT['steel'],body,'Z',40)
        _cyl('Transformer low-level drain plug',(1.10,s*1.02,.780),.024,.045,_MAT['grease'],body,'Y',6)
    # Body-side low traction-link forks are connected to the underframe. Keeping
    # these between the transformer and compressor bays avoids a floating rod eye.
    for end in [-1,1]:
        x=end*2.15
        for y in [-.175,.175]:
            prof=[(x-.180,1.305),(x+.180,1.305),(x+.115,.584),(x-.115,.584)]
            _prism_y('Body low-traction-link tapered fork',prof,y,.050,_MAT['frame'],body,.010)
            _box('Traction-link body fork upper flange',(x,y,1.302),(.43,.13,.030),_MAT['steel'],body,.004)
            for dx in [-.145,.145]:_bolt('Traction-link body anchoring bolt',(x+dx,y,1.329),body,'Z',r=.016)
        _cyl('Traction-link body fork cross pin',(x,0,.600),.035,.474,_MAT['pin'],body,'Y',32)
        for sy in [-1,1]:_bolt('Traction body fork pin retainer',(x,sy*.243,.600),body,s=sy,r=.020)
    # Separate outer service cabinets clear the transformer and compressor bays.
    for s in [-1,1]:
        for end in [-1,1]:
            if s!=end:continue
            x=end*2.22;y=s*1.250
            _box('Underfloor battery compartment box',(x,y,1.020),(.84,.42,.510),_MAT['equipment'],body,.016)
            _box('Electrical cabinet front gasket',(x,s*1.467,1.020),(.802,.009,.464),_MAT['rubber'],body,.009)
            _box('Folded service cabinet door',(x,s*1.475,1.020),(.786,.009,.448),_MAT['plate'],body,.010)
            # Hinges and an over-centre latch have separate pivot, catch and handle.
            for z in [.903,1.143]:
                _box('Cabinet hinge leaf',(x-end*.367,s*1.483,z),(.041,.009,.086),_MAT['steel'],body,.003)
                _cyl('Cabinet hinge barrel',(x-end*.374,s*1.495,z),.010,.071,_MAT['fastener'],body,'Z',20)
                for dz in [-.028,.028]:_bolt('Cabinet hinge screw',(x-end*.352,s*1.490,z+dz),body,s=s,r=.005)
            _box('Cabinet latch mounting plate',(x+end*.315,s*1.487,1.020),(.051,.015,.097),_MAT['steel'],body,.004)
            _cyl('Cabinet latch spindle',(x+end*.315,s*1.503,1.027),.012,.024,_MAT['fastener'],body,'Y',24)
            _rod('Cabinet latch handle',(x+end*.315,s*1.520,1.032),(x+end*.315,s*1.520,.986),.009,_MAT['fastener'],body,16)
            for dx in [-.340,.340]:
                _box('Cabinet lower folded support',(x+dx,y,.778),(.048,.39,.020),_MAT['steel'],body,.003)
                _bolt('Cabinet chassis anchor',(x+dx,s*1.34,1.267),body,'Z',r=.011)
                _box('Cabinet vertical suspension bracket',(x+dx,s*1.319,1.289),(.053,.026,.114),_MAT['steel'],body,.003)
                _box('Cabinet upper angle hanger',(x+dx,s*1.401,1.339),(.070,.190,.024),_MAT['frame'],body,.004)
                _bolt('Cabinet frame-hanger bolt',(x+dx,s*1.482,1.357),body,'Z',r=.011)
        # Closed cable raceway section with lid lip, lapped joints and steel clips.
        _box('Underframe cable raceway',(0,s*1.416,1.380),(5.92,.074,.073),_MAT['plate'],body,.008)
        _box('Raceway lid overlap',(0,s*1.458,1.394),(5.92,.008,.040),_MAT['steel'],body,.003)
        for x in [-2.75,-1.85,-.93,0,.93,1.85,2.75]:
            _box('Cable raceway retaining band',(x,s*1.417,1.383),(.032,.093,.094),_MAT['steel'],body,.004)
            _bolt('Cable raceway clamp fixing',(x,s*1.472,1.410),body,s=s,r=.008)
        for x in [-1.48,1.48]:
            _box('Cable raceway expansion-joint sleeve',(x,s*1.416,1.380),(.057,.080,.079),_MAT['rubber'],body,.004)
    for end in [-1,1]:_compressor(end,body)


def apply(context=None):
    """Apply the isolated running-gear detail module to an opened WAP7 master.

    Optional dict keys: material_overrides (role -> bpy Material), underfloor
    (bool, defaults True). Returns machine-readable component/validation facts.
    """
    global _COLL,_CREATED,_MAT
    context=context or {};_CREATED=[]
    scene=bpy.context.scene
    required=['WAP7_ROOT','BODY','BOGIE_A_YAW_Z','BOGIE_B_YAW_Z']+[f'AXLE_{b}_{i}_ROLL_Y' for b in 'AB' for i in (1,2,3)]
    missing=[n for n in required if n not in bpy.data.objects]
    if missing:raise RuntimeError('Running gear requires preserved controls: '+', '.join(missing))
    before={n:tuple(v for row in bpy.data.objects[n].matrix_world for v in row) for n in required}
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            data=o.data if o.type=='MESH' else None;bpy.data.objects.remove(o,do_unlink=True)
            if data and data.users==0:bpy.data.meshes.remove(data)
    _COLL=bpy.data.collections.get(COLLECTION) or bpy.data.collections.new(COLLECTION)
    if _COLL.name not in scene.collection.children:scene.collection.children.link(_COLL)
    _COLL['purpose']='Detailed visual running gear, preserved original axle and bogie control hierarchy'
    _MAT={
        'frame':_material('dusty black fabricated frame',(.060,.052,.039),.27,.57,True),
        'plate':_material('rolled black cover steel',(.042,.039,.032),.40,.52,True),
        'steel':_material('rubbed structural black steel',(.055,.049,.040),.51,.43,True),
        'weld':_material('weld bead blackened steel',(.038,.034,.028),.47,.57,True),
        'axlebox':_material('axlebox painted cast iron',(.072,.063,.047),.30,.54,True),
        'spring':_material('spring oiled steel',(.034,.030,.025),.67,.38,True),
        'spring_inner':_material('spring shaded inner steel',(.020,.020,.019),.54,.45,False),
        'damper':_material('damper worn graphite enamel',(.057,.056,.045),.27,.41,True),
        'rubber':_material('dry suspension rubber',(.013,.013,.012),.0,.77,False,.0001),
        'grease':_material('local lubricated joint film',(.019,.013,.008),.18,.26,False,.00002),
        'pin':_material('working joint pins',(.14,.13,.107),.88,.29,False),
        'chrome':_material('hard chrome piston surface',(.38,.40,.39),.98,.17,False,.00001),
        'fastener':_material('aged fastener steel',(.105,.096,.075),.80,.39,True,.000035),
        'washer':_material('oxide dark washers',(.042,.036,.027),.72,.49,False),
        'shim':_material('spring compensation steel',(.14,.125,.095),.75,.48,True),
        'cable':_material('rubber cable sheathing',(.014,.015,.013),.0,.53,False,.00003),
        'wheelweb':_material('oxidised forged wheel web',(.091,.061,.035),.74,.57,False,.00006),
        'rimside':_material('tyre lateral brushed steel',(.18,.165,.135),.92,.36,False,.000025),
        'tread':_material('clean polished wheel running tread',(.38,.40,.40),.98,.21,False,.000012),
        'rimline':_material('subtle tyre turning witness',(.115,.116,.106),.91,.32,False,0),
        'hub':_material('forged wheel hub',(.077,.063,.043),.78,.41,False),
        'brake':_material('composite brake block',(.031,.021,.015),.10,.82,False,.00016),
        'rod':_material('brake pull rod rubbed steel',(.074,.056,.034),.73,.43,True),
        'cylinder':_material('pneumatic cylinder dark enamel',(.049,.051,.043),.22,.49,True),
        'pipe':_material('dark steel air and sand pipe',(.038,.036,.029),.47,.46,True),
        'motor':_material('traction motor cast shell',(.040,.037,.030),.42,.56,True),
        'sandbox':_material('painted sand hopper steel',(.080,.068,.049),.24,.62,True),
        'band':_material('spring tolerance aluminium band',(.25,.25,.22),.78,.49,False,.00001),
        'chain':_material('worn safety chain',(.071,.065,.050),.85,.35,False),
        'equipment':_material('underfloor equipment enamel',(.071,.071,.061),.24,.56,True),
        'red':_material('worn drain-cock oxide paint',(.17,.036,.013),.19,.53,True),
    }
    _MAT.update(context.get('material_overrides',{}))
    p=_MAT['tread'].node_tree.nodes.get('Principled BSDF')
    if p and 'Anisotropic IOR Level' in p.inputs:p.inputs['Anisotropic IOR Level'].default_value=.62
    hidden=[]
    for o in list(bpy.data.objects):
        if o.name.startswith('V02_') or o.name.startswith('SURFV02_') or o.type not in {'MESH','CURVE'}:continue
        p=o.parent;old_bogie=False
        while p:
            if p.name in {'BOGIE_A_YAW_Z','BOGIE_B_YAW_Z'}:old_bogie=True;break
            p=p.parent
        if old_bogie or (context.get('underfloor',True) and o.name.split('.')[0] in {'Traction transformer underfloor','Main air reservoir','Transformer fin bank','Transformer cooling fin','Underfloor equipment cabinet','Underfloor service-panel seam','Cabinet latch handle','Service cover fastener','Underframe cable trunking','Cable-trunk clamp','Bodyside air line'}):
            o.hide_render=True;o.hide_viewport=True;o['V02_running_gear_replaced']=True;hidden.append(o.name)
    body=bpy.data.objects['BODY']
    for label,bx in [('A',-6.0),('B',6.0)]:
        bog=bpy.data.objects[f'BOGIE_{label}_YAW_Z']
        _frame(bx,bog,label)
        for ai,dx in enumerate([-1.85,0,1.85],1):
            ax=bpy.data.objects[f'AXLE_{label}_{ai}_ROLL_Y'];x=bx+dx
            _lathe('Forged wheelset axle and journals',(x,0,.546),[(-1.255,0),(-1.255,.096),(-1.220,.106),(-1.04,.106),(-1.018,.112),(-.775,.112),(-.725,.108),(.725,.108),(.775,.112),(1.018,.112),(1.04,.106),(1.22,.106),(1.255,.096),(1.255,0)],_MAT['hub'],ax,'Y',64)
            for s in [-1,1]:
                _wheel(x,s,ax);_axlebox(x,s,bog,ai==2)
            _motor(x,bog,1 if label=='A' else -1)
        _secondary(bx,bog,label);_brakes(bx,bog,label);_sand_and_services(bx,bog,label)
    if context.get('underfloor',True):_underfloor(body)
    bpy.context.view_layer.update()
    after={n:tuple(v for row in bpy.data.objects[n].matrix_world for v in row) for n in required}
    if before!=after:raise RuntimeError('Protected rig control transforms changed')
    _COLL['source_class']='WAP7 conventional four-cylinder clasp-brake bogie; shared fabricated WAG9 suspension'
    _COLL['unit_specificity']='Small fittings/routing representative; no inaccessible 39002 engineering drawing claimed'
    result={'prefix':PREFIX,'created_objects':len(_CREATED),'hidden_legacy_objects':len(hidden),'protected_controls_unchanged':True,
            'bogie_wheelbase_m':3.700,'adjacent_axle_spacing_m':1.850,'wheel_rolling_diameter_m':1.092,
            'bogie_width_m':2.480,'primary_spring_lateral_spacing_m':2.240,'frame_over_headstocks_m':6.209,
            'primary_suspension':'24 outer coils plus 8 nested middle-axle inner coils; eight end-axle dampers and four middle safety links',
            'brake_system':'8 conventional pneumatic cylinders total, 24 curved tread blocks; no TBU/PBU installed',
            'underfloor_system':'Two W-type underslung compressor assemblies and two battery boxes; no external main reservoirs',
            'sources':'references/running_gear_evidence.md'}
    _COLL['validation_summary']=json.dumps(result)
    print('RUNNING_GEAR_V02',json.dumps(result),flush=True)
    return result
