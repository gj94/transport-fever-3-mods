"""Detailed conventional all-coil ICF coach bogies and self-generating undergear.

Blender component, metres, X longitudinal / Y transverse / Z above rail. Public
entry point: build(api, ac=False). Geometry is original procedural interpretation
of the cited railway maintenance drawings, not an interchange/production CAD.

The wheelset, brake block, coil, frame and drive are actual separate surfaces.
No FIAT/LHB disc-brake or air-spring parts are used. Fixed axleboxes do NOT inherit
wheel rotation. Only wheel/axle/pulley meshes descend from rotating axle empties.
"""
from math import sin, cos, pi, sqrt, atan2, acos
import bpy
import bmesh
from mathutils import Vector, Matrix

REFERENCES = [
    {"title": "Indian Railways ICF Maintenance Manual, Chapter 3: Bogies", "url": "https://scr.indianrailways.gov.in/uploads/files/1341833527005-Bogies.PDF", "used": "Sections 301-315, Figure 3.1: 2896 wheelbase, 915 new wheels, 3950 x 2364 bogie envelope, primary dashpots, all-coil suspension, BSS hangers, diagonal anchor links, oil-bath side bearers and tread brake layout"},
    {"title": "Indian Railways ICF Maintenance Manual, Chapter 7: Train Lighting", "url": "https://scr.indianrailways.gov.in/uploads/files/1341896144130-Train%20Light.PDF", "used": "Bogie/transom-mounted brushless alternator and matched four V-belt non-AC drive"},
    {"title": "Indian Railways ICF Maintenance Manual, Chapter 8: Air Conditioning", "url": "https://scr.indianrailways.gov.in/uploads/files/1341832085307-Air%20Conditioning.PDF", "used": "Self-generating AC equipment with six V-belts on each side of each alternator shaft"},
    {"title": "RDSO V-belt specification RDSO/PE/SPEC/AC/0059-2011 Rev.1", "url": "https://rdso.indianrailways.gov.in/works/uploads/File/New%20spec_v-belt_%20revesion1.pdf", "used": "Appendix A: 572.6 mm axle and 200 mm alternator pitch diameters; 136.5 mm four-groove non-AC pulley width; double-ended six-belt AC topology. Local groove/belt cross-sections remain visual interpretations."},
    {"title": "CAMTECH Procedure for IOH of Broad Gauge BVZI", "url": "https://indianrailways.gov.in/railwayboard/uploads/directorate/eff_res/camtech/mechanical/YearWise/Procedure%20for%20IOH%20of%20Broad%20gauge%20BVZI.pdf", "used": "ICF bogie components: oil-bath side bearers, silent-block anchor links, BSS hangers, equalising stays, brake heads and safety wire ropes"},
]
NOMINAL_DIMENSIONS = dict(bogie_pivot_spacing_m=14.783, bogie_wheelbase_m=2.896,
    wheel_diameter_new_m=.915, wheel_back_to_back_m=1.600,
    bogie_frame_length_m=3.950, bogie_nominal_width_m=2.364,
    side_bearer_spacing_m=1.600, primary_guide_pitch_m=.570,
    primary_spring_wire_diameter_m=.0335, bolster_spring_wire_diameter_m=.042)


class _Gear:
    def __init__(self, api, ac):
        self.api, self.ac = api, ac
        self.root, self.body = api.root, api.body
        self.hanger_half = .750 if ac else .700
        self.transom_half = .770 if ac else .720
        self.created = []
        self.m = dict(api.materials)
        self.m['frame'] = self.material('ICF running gear graphite paint', (.065,.072,.069), .48, .60)
        self.m['cast'] = self.material('ICF cast steel and dark wheel web', (.072,.067,.057), .66, .55)
        self.m['spring'] = self.material('ICF oiled suspension spring steel', (.13,.14,.13), .73, .32)
        self.m['tread'] = self.material('ICF turned wheel tread polished steel', (.34,.36,.35), .90, .27)
        self.m['dust'] = self.material('ICF oxide road dust metal', (.105,.074,.047), .38, .76)
        self.m['label'] = self.material('ICF maintenance stencil', (.67,.66,.53), .05, .62)
        self.m['group'] = self.material('ICF spring group blue paint', (.045,.13,.24), .32, .47)
        self.m['brake'] = self.material('ICF composition tread brake material', (.045,.038,.031), .12, .86)
        self.m['battery'] = self.material('ICF battery cabinet charcoal paint', (.14,.15,.145), .34, .63)

    def material(self, name, rgb, metal, rough):
        m = bpy.data.materials.get(name)
        if m: return m
        m = bpy.data.materials.new(name); m.use_nodes=True
        m.diffuse_color=(*rgb,1)
        p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*rgb,1)
        p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        return m

    def mark(self, ob, part):
        if ob is not None:
            ob['icf_component']=part
            self.created.append(ob)
        return ob

    def box(self,n,c,d,mat='frame',parent=None,bevel=.003):
        return self.mark(self.api.cube(n,c,d,self.m[mat],bevel=bevel,parent=parent or self.body), n)

    def cyl(self,n,c,r,d,mat='steel',axis='Z',parent=None,segments=32):
        return self.mark(self.api.cylinder(n,c,r,d,self.m[mat],axis=axis,parent=parent or self.body,vertices=segments), n)

    def mesh(self,n,v,f,mat='frame',parent=None,smooth=False):
        ob=self.api.mesh(n,v,f,self.m[mat],parent=parent or self.body)
        # Consistent outward normals matter for one-sided game-export materials.
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(ob.data);bm.free();ob.data.update()
        if smooth:
            for p in ob.data.polygons:p.use_smooth=True
        return self.mark(ob,n)

    def empty(self,n,pos,parent):
        ob=self.api.empty(n,(0,0,0),parent=parent)
        ob.matrix_world=Matrix.Translation(pos)
        bpy.context.view_layer.update()
        return self.mark(ob,n)

    def tube(self,n,pts,r,mat='steel',parent=None,sides=8,closed=False):
        # One watertight tube mesh, rather than hundreds of separate spring rods.
        pts=[Vector(p) for p in pts]
        if len(pts)<2:return None
        if closed and (pts[0]-pts[-1]).length < 1e-8:pts.pop()
        verts=[];count=len(pts)
        for i,p in enumerate(pts):
            if closed:t=pts[(i+1)%count]-pts[(i-1)%count]
            elif i==0:t=pts[1]-p
            elif i==count-1:t=p-pts[i-1]
            else:t=pts[i+1]-pts[i-1]
            t.normalize(); ref=Vector((0,0,1)) if abs(t.z)<.95 else Vector((0,1,0))
            u=t.cross(ref).normalized();v=t.cross(u).normalized()
            verts.extend(tuple(p+r*(cos(j*2*pi/sides)*u+sin(j*2*pi/sides)*v)) for j in range(sides))
        faces=[]
        for i in range(count if closed else count-1):
            nxt=(i+1)%count
            for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,nxt*sides+(j+1)%sides,nxt*sides+j))
        if not closed:faces.extend([tuple(reversed(range(sides))),tuple((count-1)*sides+j for j in range(sides))])
        return self.mesh(n,verts,faces,mat,parent,True)

    def rod(self,n,a,b,r,mat='steel',parent=None,sides=12):
        return self.tube(n,[a,b],r,mat,parent,sides)

    def ring(self,n,c,r,tube,mat='steel',axis='Z',parent=None,nseg=32):
        x,y,z=c;pts=[]
        for i in range(nseg):
            a=i*2*pi/nseg
            pts.append((x+r*cos(a),y+r*sin(a),z) if axis=='Z' else ((x+r*cos(a),y,z+r*sin(a)) if axis=='Y' else (x,y+r*cos(a),z+r*sin(a))))
        return self.tube(n,pts,tube,mat,parent,8,True)

    def prism_xz(self,n,outline,y,depth,mat='frame',parent=None):
        count=len(outline)
        v=[(x,y+sy*depth/2,z) for sy in [-1,1] for x,z in outline]
        f=[tuple(reversed(range(count))),tuple(range(count,2*count))]
        f += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        return self.mesh(n,v,f,mat,parent)

    def spring(self,n,c,r,height,wire,turns,parent):
        x,y,z=c;nt=int(turns*22);pts=[]
        # Squared and closed ends: the first/last 0.7 turns rise very little.
        flat=.70/turns
        for i in range(nt+1):
            u=i/nt;a=u*turns*2*pi
            elev=.025*u/flat if u<flat else (height-.025+.025*(u-1+flat)/flat if u>1-flat else .025+(height-.05)*(u-flat)/(1-2*flat))
            pts.append((x+r*cos(a),y+r*sin(a),z+elev))
        ob=self.tube(n,pts,wire,'spring',parent,10)
        ob['wire_diameter_m']=wire*2;ob['loaded_height_m']=height+wire*2
        # Short matching-height group-blue dabs on every coil, at three azimuths.
        for turn in range(1,int(turns)):
            for a0 in [0,2*pi/3,4*pi/3]:
                pp=[]
                for k in range(4):
                    a=turn*2*pi+a0+(k-1.5)*.07;u=a/(turns*2*pi)
                    if u>=1-flat:continue
                    elev=.025+(height-.05)*(u-flat)/(1-2*flat)
                    pp.append((x+(r+.0007)*cos(a),y+(r+.0007)*sin(a),z+elev))
                if len(pp)>1:self.tube(n+' group mark',pp,wire+.0005,'group',parent,6)
        return ob

    def bolt(self,n,c,axis='Y',r=.012,mat='steel',parent=None):
        ob=self.cyl(n+' hex head',c,r,r*.65,mat,axis,parent,6)
        return ob

    def pin(self,n,c,length,axis='Y',r=.018,parent=None):
        self.cyl(n+' pin',c,r,length,'steel',axis,parent,16)
        vi={'X':0,'Y':1,'Z':2}[axis]
        for s in [-1,1]:
            p=list(c);p[vi]+=s*length*.5
            self.cyl(n+' retaining washer',p,r*1.55,.006,'dust',axis,parent,20)
            p[vi]+=s*.008;self.bolt(n+' retaining',p,axis,r*1.2,'steel',parent)

    def flatlink(self,n,a,b,width,depth,mat='frame',parent=None):
        # Forged strap in XZ, with round pin bosses rather than a round bar.
        a=Vector(a);b=Vector(b);dv=b-a;u=Vector((-dv.z,0,dv.x)).normalized()*width/2
        outline=[(p.x,p.z) for p in [a+u,b+u,b-u,a-u]]
        self.prism_xz(n+' strap',outline,(a.y+b.y)/2,depth,mat,parent)
        for p in [a,b]:self.cyl(n+' eye',p,width*.65,depth,mat,'Y',parent,20)

    def lathe_y(self,n,x,z,profile,mat='cast',parent=None,segments=72,side=1):
        # Share a single axis vertex at a closed tip: no zero-area pole quads.
        v=[];rings=[]
        for y,r in profile:
            if r < 1e-9:
                rings.append([len(v)]);v.append((x,side*y,z))
            else:
                rings.append(list(range(len(v),len(v)+segments)))
                v.extend((x+r*cos(j*2*pi/segments),side*y,z+r*sin(j*2*pi/segments)) for j in range(segments))
        f=[]
        for k,ring in enumerate(rings):
            nxt=rings[(k+1)%len(rings)]
            if len(ring)==1 and len(nxt)==1:continue
            for j in range(segments):
                if len(ring)==1:face=(ring[0],nxt[(j+1)%segments],nxt[j])
                elif len(nxt)==1:face=(ring[j],ring[(j+1)%segments],nxt[0])
                else:face=(ring[j],ring[(j+1)%segments],nxt[(j+1)%segments],nxt[j])
                f.append(tuple(reversed(face)) if side>0 else face)
        return self.mesh(n,v,f,mat,parent,True)

    def wheel(self,ax,side,ar):
        # Cross-section has a dished web, thick hub, full rim, conical tread,
        # radiused flange root and inner flange. This is not a pile of cylinders.
        pr=[(.775,.100),(.775,.145),(.794,.162),(.820,.169),(.846,.210),(.853,.326),(.836,.375),(.810,.399),(.800,.432),(.800,.469),(.808,.4835),(.818,.4855),(.827,.478),(.839,.465),(.849,.4587),(.873,.4575),(.916,.45535),(.932,.447),(.935,.425),(.924,.399),(.905,.381),(.887,.363),(.880,.327),(.859,.214),(.875,.175),(.929,.157),(.978,.145),(.991,.124),(.991,.100)]
        ob=self.lathe_y('ICF monobloc 915mm dished wheel',ax,.4575,pr,'cast',ar,96,side)
        ob.data.materials.append(self.m['tread'])
        for p in ob.data.polygons:
            if 8 <= p.index//96 <= 18:p.material_index=1
        ob['wheel_diameter_m']=.915;ob['flange_max_radius_m']=.4855;ob['tread_reference_y_m']=side*.873
        # Clearly separate forged hub shoulder and circumferential machining line.
        self.ring('Wheel hub machining line',(ax,side*.978,.4575),.142,.0022,'tread','Y',ar,48)
        self.ring('Wheel rim witness line',(ax,side*.933,.4575),.421,.0018,'steel','Y',ar,72)

    def axlebox(self,ax,s,bg):
        y=s*1.0795
        # Cast wing type housing: each wing carries a concentric spring/dashpot.
        self.prism_xz('Wing-type axlebox casting',[(ax-.43,.452),(ax-.43,.536),(ax-.20,.55),(ax-.15,.626),(ax+.15,.626),(ax+.20,.55),(ax+.43,.536),(ax+.43,.452),(ax+.17,.441),(ax+.12,.342),(ax-.12,.342),(ax-.17,.441)],y,.215,'cast',bg)
        self.cyl('Axlebox spherical bearing housing',(ax,y,.4575),.141,.255,'cast','Y',bg,40)
        self.cyl('Axlebox circular gasket',(ax,s*1.215,.4575),.129,.006,'rubber','Y',bg,40)
        self.cyl('Axlebox bolted front cover',(ax,s*1.226,.4575),.139,.020,'frame','Y',bg,40)
        self.cyl('Axlebox centre inspection emboss',(ax,s*1.240,.4575),.075,.012,'cast','Y',bg,32)
        for a in [pi/6+i*pi/3 for i in range(6)]:
            self.bolt('Axlebox cover M20',(ax+.112*cos(a),s*1.244,.4575+.112*sin(a)),'Y',.015,'steel',bg)
        self.box('Axlebox crown bump rubber',(ax,y,.648),(.11,.14,.031),'rubber',bg)
        self.box('Axlebox crown stop bracket',(ax,y,.746),(.12,.16,.032),'frame',bg)
        self.cyl('Crown clearance stop bolt',(ax,y,.71),.014,.065,'steel','Z',bg,8)
        for dx in [-.285,.285]:
            x=ax+dx
            self.cyl('Primary lower spring seat cup',(x,y,.551),.128,.046,'cast','Z',bg,32)
            self.cyl('Primary isolation rubber pad',(x,y,.580),.124,.012,'rubber','Z',bg,32)
            self.cyl('Primary dashpot oil cylinder',(x,y,.632),.069,.163,'frame','Z',bg,32)
            self.cyl('Telescopic axle guide piston sleeve',(x,y,.778),.047,.182,'steel','Z',bg,28)
            self.ring('Dashpot sealing lip',(x,y,.711),.065,.007,'rubber','Z',bg)
            self.cyl('Primary upper spring seat',(x,y,.872),.129,.026,'frame','Z',bg,32)
            self.spring('Primary 33.5mm helical spring',(x,y,.60275),.099,.23950,.01675,6.15,bg)
            self.bolt('Dashpot oil filling vent screw',(x,y,1.060),'Z',.013,'brass',bg)
            # Narrow U retention strap is separate from the load-bearing coil.
            self.tube('Dashpot safety U bolt',[(x-.090,y+s*.074,.557),(x-.090,y+s*.074,.51),(x+.090,y+s*.074,.51),(x+.090,y+s*.074,.557)],.008,'steel',bg)
        for dx in [-.20,.20]:
            self.prism_xz('Axlebox wing strengthening rib',[(ax+dx,.49),(ax+dx,.59),(ax+dx+( -.13 if dx<0 else .13),.538)],y+s*.10,.016,'cast',bg)

    def brake_block(self,ax,s,front,bg):
        # Curve stays clear of the flange-root transition as well as the tread.
        # The nominal radial gap is 5 mm near the inner working edge.
        a0=0 if front>0 else pi;count=14;ys=[s*.853,s*.925]
        vv=[]
        for y in ys:
            for r in [.463,.511]:
                for i in range(count+1):
                    a=a0-.285+i*.570/count;vv.append((ax+r*cos(a),y,.4575+r*sin(a)))
        row=count+1;faces=[]
        for side in [0,1]:
            off=side*2*row
            for i in range(count):faces.append((off+i,off+i+1,off+row+i+1,off+row+i))
        for rr in [0,1]:
            off=rr*row
            for i in range(count):faces.append((off+i,2*row+off+i,2*row+off+i+1,off+i+1))
        faces += [(0,row,3*row,2*row),(row-1,2*row-1,4*row-1,3*row-1)]
        self.mesh('Curved K-type composition tread brake block',vv,faces,'brake',bg)
        x=ax+front*.530;y=s*.884
        self.box('Brake head cast backplate',(x,y,.4575),(.032,.117,.201),'cast',bg,.005)
        self.pin('Brake head shoe retaining pin',(x-front*.014,y,.4575),.160,'Y',.014,bg)
        self.flatlink('Brake block suspension hanger',(x,y,.51),(ax+front*.454,y,.887),.043,.034,'frame',bg)
        self.pin('Brake hanger upper pivot',(ax+front*.454,y,.886),.094,'Y',.012,bg)
        # Safety wire is slack and spatially separate from the working hanger.
        self.tube('Brake beam safety wire rope',[(ax+front*.44,s*.78,.88),(ax+front*.57,s*.78,.67),(ax+front*.56,s*.78,.42)],.004,'steel',bg)

    def brake_gear(self,bx,bg):
        for ax in [bx-1.448,bx+1.448]:
            for front in [-1,1]:
                x=ax+front*.530
                self.box('Brake transverse channel beam',(x,0,.4575),(.047,1.86,.064),'frame',bg)
                self.rod('Brake beam tension truss',(x, -.86,.437),(x+front*.07,0,.365),.012,'steel',bg)
                self.rod('Brake beam tension truss',(x+front*.07,0,.365),(x,.86,.437),.012,'steel',bg)
                for s in [-1,1]:self.brake_block(ax,s,front,bg)
        # Two 8-inch integral-slack-adjuster cylinders: each works one wheelset.
        for s in [-1,1]:
            x=bx+s*.92;y=-s*.36
            self.cyl('Bogie mounted 8-inch air brake cylinder',(x,y,.740),.109,.29,'frame','X',bg,36)
            self.cyl('Brake cylinder end flange',(x-s*.156,y,.740),.122,.025,'cast','X',bg,36)
            self.cyl('Brake cylinder piston guide',(x+s*.17,y,.740),.046,.080,'steel','X',bg,24)
            self.rod('Brake cylinder piston rod',(x+s*.20,y,.740),(x+s*.43,y,.740),.016,'steel',bg)
            for a in [i*pi/3 for i in range(6)]:self.bolt('Brake cylinder flange',(x-s*.175,y+.096*cos(a),.740+.096*sin(a)),'X',.010,'steel',bg)
            self.box('Brake cylinder transom support',(x,y,.891),(.30,.24,.045),'frame',bg)
            self.tube('Brake cylinder air flex hose',[(x-s*.1,y,.843),(x-s*.18,y,.95),(bx+s*.60,y,.975)],.009,'rubber',bg)
            ax=bx+s*1.448
            for k in [-1,1]:
                y2=k*.37
                self.flatlink('Brake live lever',(ax-s*.53,y2,.4575),(ax-s*.18,y2,.756),.047,.030,'frame',bg)
                self.pin('Brake lever fulcrum',(ax-s*.26,y2,.687),.10,'Y',.014,bg)
                self.tube('Curved brake pull rod',[(ax-s*.57,y2,.486),(ax-s*.18,y2,.359),(ax+s*.17,y2,.359),(ax+s*.53,y2,.4575)],.016,'steel',bg)
                self.box('Brake rigging safety cradle',(ax,y2,.320),(.14,.080,.028),'frame',bg)
            self.rod('Brake cross balance spindle',(ax-s*.20,-.39,.725),(ax-s*.20,.39,.725),.024,'steel',bg)

    def bolster(self,bx,bg):
        # Floating bolster box: raised central web and broad spring-seat ends.
        self.box('Floating bogie bolster main box',(bx,0,.933),(.51,1.89,.214),'frame',bg,.007)
        for xoff in [-.26,.26]:self.box('Bolster upper flange',(bx+xoff,0,1.044),(.040,2.34,.024),'frame',bg)
        for s in [-1,1]:
            y=s*1.0795
            self.box('Bolster spring head seat',(bx,y,.880),(1.04,.322,.055),'frame',bg)
            self.box('Lower spring beam end tray',(bx,y,.495),(1.18,.338,.085),'frame',bg)
            for dx in [-.26,.26]:
                x=bx+dx
                self.cyl('Bolster spring bottom rubber pad',(x,y,.5465),.161,.018,'rubber','Z',bg,32)
                self.cyl('Bolster spring top seating flange',(x,y,.850),.161,.022,'frame','Z',bg,32)
                self.spring('Secondary 42mm bolster coil',(x,y,.5765),.133,.2415,.021,5.35,bg)
            # Double plates of each BSS hanger are open between the pin bosses.
            for dx in [-self.hanger_half,self.hanger_half]:
                tx=bx+dx;lx=bx+dx*.928
                for dy in [-.065,.065]:
                    yy=y+dy
                    self.flatlink('BSS swing hanger forged link',(tx,yy,.965),(lx,yy,.525),.062,.024,'cast',bg)
                self.pin('BSS upper hanger pin',(tx,y,.965),.195,'Y',.0185,bg)
                self.pin('BSS lower hanger pin',(lx,y,.525),.195,'Y',.0185,bg)
                self.box('BSS hanger block',(tx,y,.985),(.124,.15,.089),'frame',bg)
                self.box('Spring plank hanger block',(lx,y,.51),(.125,.19,.075),'frame',bg)
            # Paired bolster safety straps drop under the floating head flange.
            for dx in [-.48,.48]:
                self.tube('Bolster safety U strap',[(bx+dx,y-.14,1.02),(bx+dx,y-.14,.806),(bx+dx,y+.14,.806),(bx+dx,y+.14,1.02)],.013,'steel',bg)
            dx=.515*s;x=bx+dx
            self.cyl('Vertical secondary hydraulic damper body',(x,s*1.292,.68),.041,.254,'frame','Z',bg,24)
            self.cyl('Secondary damper polished piston',(x,s*1.292,.882),.016,.159,'tread','Z',bg,20)
            self.cyl('Secondary damper dust sleeve',(x,s*1.292,.81),.044,.10,'frame','Z',bg,24)
            for zz in [.533,.973]:
                self.cyl('Damper eye silent rubber',(x,s*1.292,zz),.036,.075,'rubber','Y',bg,24)
                self.pin('Secondary damper eye pin',(x,s*1.292,zz),.111,'Y',.013,bg)
                self.box('Damper attachment lug',(x,s*1.240,zz),(.12,.095,.055),'frame',bg)
            # Side bearer oil baths are 1.600 m apart. Pivot carries no weight.
            sy=s*.80
            self.box('Side bearer lubricating oil bath',(bx,sy,1.076),(.368,.266,.106),'cast',bg,.013)
            self.box('Side bearer bronze wearing piece',(bx,sy,1.132),(.265,.170,.045),'brass',bg,.010)
            self.box('Side bearer dust excluding cover',(bx,sy,1.163),(.349,.243,.030),'frame',bg,.006)
            self.box('Body bolster side-bearer attachment',(bx,sy,1.192),(.280,.200,.033),'frame',self.body)
            self.tube('Side bearer oil filler pipe',[(bx,sy,1.075),(bx-.26,sy,1.075),(bx-.26,s*1.008,1.109)],.010,'steel',bg)
            self.cyl('Side bearer oil filler cap',(bx-.26,s*1.008,1.116),.026,.018,'brass','Z',bg,12)
            # The two diagonally opposed traction/braking anchor links.
            aa=(bx+s*.24,s*.84,.956);bb=(bx+s*.775,s*.84,.956)
            self.rod('Bolster diagonal anchor link shank',aa,bb,.025,'cast',bg)
            for p in [aa,bb]:
                self.cyl('Anchor link silent block outer housing',p,.055,.104,'cast','Y',bg,28)
                self.cyl('Anchor link rubber bush',p,.043,.112,'rubber','Y',bg,24)
                self.pin('Anchor link pin',p,.152,'Y',.0125,bg)
            # Lateral equalising stays connect lower plank to the bolster.
            self.rod('Equalising stay rod',(bx-.28,s*.44,.540),(bx+.28,s*.93,.902),.020,'steel',bg)
            for p in [(bx-.28,s*.44,.54),(bx+.28,s*.93,.902)]:
                self.cyl('Equalising stay pin eye',p,.043,.080,'cast','Y',bg,24)
                self.pin('Equalising stay pin',p,.113,'Y',.015,bg)
        for dx in [-.30,.30]:
            self.box('Lower spring cradle transverse channel',(bx+dx,0,.480),(.13,2.31,.098),'frame',bg)
            for y in [-.65,0,.65]:self.box('Spring cradle transverse stiffener',(bx+dx,y,.541),(.16,.026,.047),'cast',bg)
        self.cyl('Centre pivot silent block housing',(bx,0,1.060),.153,.18,'cast','Z',bg,40)
        self.cyl('Centre pivot rubber silent block',(bx,0,1.140),.095,.109,'rubber','Z',bg,32)
        self.cyl('Centre pivot tractive force pin',(bx,0,1.195),.048,.178,'steel','Z',bg,32)
        self.box('Centre pivot retaining plate',(bx,0,.962),(.226,.226,.020),'steel',bg)
        for dx in [-.087,.087]:
            for dy in [-.087,.087]:self.bolt('Centre pivot retaining screw',(bx+dx,dy,.948),'Z',.012,'steel',bg)

    def frame(self,bx,bg):
        for s in [-1,1]:
            y=s*1.0795
            outline=[(bx-1.975,.887),(bx-1.932,1.026),(bx-1.79,1.058),(bx+1.79,1.058),(bx+1.932,1.026),(bx+1.975,.887),(bx+1.84,.84),(bx-1.84,.84)]
            for dy in [-.091,.091]:self.prism_xz('Fabricated sideframe vertical web',outline,y+dy,.012,'frame',bg)
            self.box('Sideframe continuous upper flange',(bx,y,1.059),(3.80,.207,.020),'frame',bg)
            self.box('Sideframe lower spring flange',(bx,y,.847),(3.68,.207,.020),'frame',bg)
            for dx in [-1.83,-1.16,-.73,.73,1.16,1.83]:
                self.box('Sideframe welded vertical stiffener',(bx+dx,y,.948),(.018,.192,.194),'frame',bg)
                self.rod('Visible sideframe fillet weld',(bx+dx-.012,y+s*.097,.859),(bx+dx-.012,y+s*.097,1.04),.0032,'dust',bg,6)
            self.box('Bogie maker plate',(bx+.02,y+s*.107,1.004),(.265,.008,.069),'steel',bg,.001)
            for dx in [-.115,.115]:self.bolt('Maker plate rivet',(bx+dx+.02,y+s*.113,1.004),'Y',.004,'cast',bg)
        for dx in [-1.899,1.899]:
            self.box('Bogie headstock transverse box',(bx+dx,0,.947),(.124,2.15,.184),'frame',bg)
            self.box('Headstock upper flange',(bx+dx,0,1.043),(.158,2.24,.022),'frame',bg)
            for s in [-1,1]:
                self.prism_xz('Headstock corner gusset',[(bx+dx,.866),(bx+dx,.994),(bx+dx-(.16 if dx>0 else -.16),.994)],s*.99,.17,'frame',bg)
        for dx in [-self.transom_half,self.transom_half]:
            self.box('Bogie centre transom box',(bx+dx,0,.944),(.105,2.08,.192),'frame',bg)
            self.box('Transom upper closing flange',(bx+dx,0,1.045),(.153,2.12,.017),'frame',bg)
        # Air feeds follow the upper inside face, with support clamps.
        self.tube('Bogie air feed manifold',[(bx-1.61,-.966,1.027),(bx-.75,-.966,1.027),(bx-.75,-.36,.975),(bx+.75,-.36,.975)],.010,'steel',bg)
        for dx in [-1.5,-1,-.5,0,.5,1,1.5]:self.box('Bogie feed pipe clip',(bx+dx,-.966,1.033),(.028,.045,.011),'dust',bg,.001)

    def pulley(self,n,x,y,z,r,width,grooves,parent):
        profile=[(y-width/2,.046),(y-width/2,r+.005)]
        pitch=width/grooves
        for i in range(grooves):
            q=y-width/2+i*pitch
            profile.extend([(q+.002,r+.005),(q+pitch*.40,r-.009),(q+pitch*.60,r-.009),(q+pitch-.002,r+.005)])
        profile += [(y+width/2,r+.005),(y+width/2,.046)]
        ob=self.lathe_y(n,x,z,profile,'cast',parent,48)
        ob['pitch_diameter_m']=2*r;ob['groove_count']=grooves;ob['face_width_m']=width
        return ob

    def belt(self,n,a,b,ra,rb,y,parent):
        # Open-belt external tangents, not a crude rectangle or crossed drive.
        ax,az=a;bx,bz=b;dx=bx-ax;dz=bz-az;dd=sqrt(dx*dx+dz*dz)
        phi=atan2(dz,dx);alpha=acos((ra-rb)/dd)
        up=phi+alpha;dn=phi-alpha
        pts=[]
        for i in range(23):
            t=up+(2*pi-2*alpha)*i/22
            pts.append((ax+ra*cos(t),y,az+ra*sin(t)))
        for i in range(17):
            t=dn+(2*alpha)*i/16
            pts.append((bx+rb*cos(t),y,bz+rb*sin(t)))
        # Swept trapezoidal V section: broad outer face, narrower inner face.
        # One closed watertight belt, with true external tangent spans.
        verts=[];faces=[];count=len(pts)
        for i,p in enumerate(pts):
            p=Vector(p);t=(Vector(pts[(i+1)%count])-Vector(pts[(i-1)%count])).normalized()
            radial=Vector((t.z,0,-t.x))
            for width,dr in [(-.011,.007),(.011,.007),(.0065,-.007),(-.0065,-.007)]:
                verts.append(tuple(p+Vector((0,width,0))+radial*dr))
        for i in range(count):
            for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,((i+1)%count)*4+(j+1)%4,((i+1)%count)*4+j))
        ob=self.mesh(n,verts,faces,'rubber',parent)
        ob['belt_section']='visual trapezoidal V section';ob['belt_width_m']=.022
        return ob

    def alternator(self,bx,bg,ar,ac):
        # Transom mount, rotating axis Y, axle pulley on inner half of wheelset.
        ax=bx-1.448;x=bx-(.610 if ac else .580);z=.510;y=-.20 if ac else -.34
        radius=.183 if ac else .147;length=.46 if ac else .36
        self.cyl(('18kW split-AC' if ac else '4.5kW')+' self-generating alternator barrel',(x,y,z),radius,length,'frame','Y',bg,48)
        for dy in [-length/2,length/2]:
            self.cyl('Alternator bolted end shield',(x,y+dy,z),radius+.014,.027,'cast','Y',bg,36)
            for a in [i*pi/4 for i in range(8)]:self.bolt('Alternator end shield',(x+(radius-.013)*cos(a),y+dy*1.06,z+(radius-.013)*sin(a)),'Y',.010,'steel',bg)
        for i in range(18):
            a=i*2*pi/18
            self.rod('Alternator longitudinal cooling fin',(x+radius*cos(a),y-length*.40,z+radius*sin(a)),(x+radius*cos(a),y+length*.40,z+radius*sin(a)),.008,'cast',bg,5)
        self.box('Alternator field terminal box',(x,y,z+radius+.048),(.18,.18,.093),'frame',bg,.011)
        self.tube('Alternator flexible cable',[(x+.08,y,z+radius+.09),(x+.20,y,.90),(bx+.10,-.35,1.055)],.014,'rubber',bg)
        mount_x=bx-self.transom_half
        self.box('Alternator suspension crossbar',(mount_x,y,.921),(.14,.73,.080),'frame',bg)
        for dy in [-.16,.16]:
            self.flatlink('Alternator suspension arm',(mount_x,y+dy,.870),(x,y+dy,z+radius*.80),.065,.037,'cast',bg)
            self.pin('Alternator suspension pin',(mount_x,y+dy,.85),.088,'Y',.016,bg)
        ng=6 if ac else 4;w=.200 if ac else .1365
        rotor=self.empty('ALTERNATOR_%d_ROTOR_Y'% (1 if bx<0 else 2),(x,y,z),bg)
        rotor['rotation_axis']='+Y local';rotor['drive_ratio']=.2863/.100
        rotor['driven_by_axle']=ar.name
        pulley_sides=[-1,1] if ac else [1]
        for ps in pulley_sides:
            py=y+ps*(length/2+w/2+.025)
            self.pulley('Split axle V-belt drive pulley',ax,py,.4575,.2863,w,ng,ar)
            self.pulley('Alternator V-belt driven pulley',x,py,z,.100,w,ng,rotor)
            for i in range(ng):self.belt('Matched alternator V belt %02d'%(i+1),(ax,.4575),(x,z),.287,.1015,py-w/2+(i+.5)*w/ng,bg)
            for a in [i*pi/3 for i in range(6)]:self.bolt('Split axle pulley fixing',(ax+.15*cos(a),py+ps*(w/2+.01),.4575+.15*sin(a)),'Y',.012,'steel',ar)
        self.rod('Alternator spring tension screw',(x+.05,y-.14,.70),(x+.47,y-.14,.76),.012,'steel',bg)
        self.box('Alternator tension rod clevis',(x+.46,y-.14,.761),(.13,.075,.06),'frame',bg)
        self.box('Alternator tension bracket vertical support',(x+.46,y-.14,.868),(.13,.050,.189),'frame',bg)
        # Two hanging safety chains with visibly alternating link planes.
        for dy in [-.21,.21]:
            for i in range(10):
                px=x-.13+.028*i;pz=.78-.16*sin(pi*i/9)
                self.ring('Alternator safety chain link',(px,y+dy,pz),.017,.004,'dust','Y' if i%2 else 'Z',bg,10)

    def bogie(self,bx,num):
        bg=self.empty(f'BOGIE_{num}_PIVOT',(bx,0,1.0),self.root)
        bg['wheelbase_m']=2.896;bg['design']='ICF conventional all-coil, tread-braked';bg['axle_load_tonnes']=16.25 if self.ac else 13.0
        bg['rotation_axis']='+Z local';bg['side_bearer_pitch_m']=1.6
        self.frame(bx,bg);self.bolster(bx,bg);ars=[]
        for i,ax in enumerate([bx-1.448,bx+1.448],1):
            ar=self.empty(f'BOGIE_{num}_AXLE_{i}_ROTATE_Y',(ax,0,.4575),bg);ars.append(ar)
            ar['rotation_axis']='+Y local';ar['rolling_radius_m']=.4575
            profile=[(-1.156,.064),(-1.040,.065),(-1.014,.080),(-.968,.090),(-.770,.092),(-.71,.080),(.71,.080),(.770,.092),(.968,.090),(1.014,.080),(1.040,.065),(1.156,.064),(1.156,0),(-1.156,0)]
            self.lathe_y('Turned stepped solid ICF axle',ax,.4575,profile,'steel',ar,40)
            for s in [-1,1]:self.wheel(ax,s,ar);self.axlebox(ax,s,bg)
        self.brake_gear(bx,bg)
        if self.ac or num==1:self.alternator(bx,bg,ars[0],self.ac)
        return bg,ars

    def cabinet(self,n,x,y,z,length,width,height,doors=3,vents=True):
        self.box(n+' enclosure',(x,y,z),(length,width,height),'battery',self.body,.008)
        sign=-1 if y<0 else 1;face=y+sign*(width/2+.011)
        for i in range(doors):
            xx=x-length/2+(i+.5)*length/doors;ww=length/doors-.026
            self.box(n+' service panel',(xx,face,z),(ww,.021,height-.049),'frame',self.body,.003)
            for d in [-1,1]:
                self.box(n+' exposed hinge',(xx-ww*.43,face+sign*.015,z+d*height*.26),(.026,.015,.043),'steel',self.body,.002)
            self.tube(n+' lifting handle',[(xx-.052,face+sign*.015,z),(xx-.052,face+sign*.052,z),(xx+.052,face+sign*.052,z),(xx+.052,face+sign*.015,z)],.008,'steel',self.body)
            self.box(n+' turn latch',(xx+ww*.37,face+sign*.025,z),(.021,.012,.082),'steel',self.body,.002)
            if vents:
                for j in range(4):self.box(n+' ventilation louver',(xx,face+sign*.015,z+height*.23+j*.025),(ww*.62,.012,.011),'dark',self.body,.001)
            for d in [-1,1]:self.bolt(n+' panel captive bolt',(xx+d*ww*.43,face+sign*.020,z-height*.38),'Y',.006,'steel',self.body)
        for dx in [-length*.37,length*.37]:
            self.box(n+' hanger channel',(x+dx,y,1.035),(.060,width+.14,.28),'frame',self.body)
            self.box(n+' lower cradle',(x+dx,y,z-height/2-.018),(.065,width+.08,.036),'steel',self.body)
        self.box(n+' data plate',(x-length*.32,face+sign*.020,z+height*.38),(.17,.004,.032),'label',self.body,.001)

    def reservoir(self,n,c,length,r,axis='X'):
        x,y,z=c
        # Dished pressure vessel ends with actual taper surfaces.
        if axis=='X':
            profile=[(-length/2-.056,0),(-length/2-.052,r*.45),(-length/2-.033,r*.78),(-length/2,r),(length/2,r),(length/2+.033,r*.78),(length/2+.052,r*.45),(length/2+.056,0)]
            verts=[];rings=[];faces=[];segments=40
            for u,rr in profile:
                if rr==0:
                    rings.append([len(verts)]);verts.append((x+u,y,z))
                else:
                    rings.append(list(range(len(verts),len(verts)+segments)))
                    verts.extend((x+u,y+rr*cos(j*2*pi/segments),z+rr*sin(j*2*pi/segments)) for j in range(segments))
            for ring,nxt in zip(rings,rings[1:]):
                for j in range(segments):
                    if len(ring)==1:face=(ring[0],nxt[j],nxt[(j+1)%segments])
                    elif len(nxt)==1:face=(ring[j],nxt[0],ring[(j+1)%segments])
                    else:face=(ring[j],nxt[j],nxt[(j+1)%segments],ring[(j+1)%segments])
                    faces.append(face)
            self.mesh(n,verts,faces,'frame',self.body,True)
            for dx in [-length*.31,length*.31]:
                self.ring(n+' retaining strap',(x+dx,y,z),r+.007,.013,'steel','X',self.body,32)
                for sy in [-1,1]:self.box(n+' hanging bracket',(x+dx,y+sy*(r+.035),(z+1.12)/2),(.05,.036,1.12-z),'frame',self.body)
            self.cyl(n+' drain cock',(x,y,z-r-.038),.018,.071,'brass','Z',self.body,10)
            self.box(n+' drain handle',(x,y,z-r-.071),(.089,.020,.010),'steel',self.body,.002)

    def undergear(self):
        eq=self.empty('ICF_UNDERFRAME_EQUIPMENT',(0,0,0),self.body)
        oldbody=self.body;self.body=eq
        # Self-generating battery boxes, ventilated louvered doors and cradle.
        for x in [-3.7,3.7]:self.cabinet('Battery box',x,-1.065,.758,1.86,.61,.495,4,True)
        self.cabinet('Rectifier regulator unit',-1.55,-1.02,.855,.72,.54,.345,2,True)
        self.cabinet('Train lighting junction box',1.25,-1.07,.899,.53,.36,.276,1,False)
        self.reservoir('Auxiliary air reservoir',(0,.24,.774),1.17,.207)
        self.reservoir('Control reservoir',(2.20,.37,.854),.53,.117)
        # Distributor valve has stacked cast bodies, release arm and fitted lines.
        self.box('Distributor valve mounting bracket',(-1.39,.38,.985),(.48,.35,.058),'frame')
        self.box('Distributor valve cast body',(-1.39,.38,.835),(.29,.23,.224),'cast')
        self.cyl('Distributor valve diaphragm cover',(-1.39,.25,.852),.121,.071,'frame','Y')
        for i in range(6):
            a=i*pi/3;self.bolt('Distributor cover bolt',(-1.39+.099*cos(a),.21,.852+.099*sin(a)),'Y',.009)
        self.rod('Brake manual release rod',(-1.45,-1.43,.82),(-1.45,.43,.82),.006)
        self.ring('Manual brake release pull ring',(-1.45,-1.46,.82),.046,.005,'steel','X',nseg=20)
        for yy in [-.18,.01]:
            self.tube('Continuous brake pipe' if yy<0 else 'Continuous feed pipe',[(-10.45,yy,1.084),(-5,yy,1.084),(0,yy,1.084),(5,yy,1.084),(10.45,yy,1.084)],.018 if yy<0 else .016,'steel')
            for xx in [-9,-6,-3,0,3,6,9]:
                self.box('Train pipe saddle clip',(xx,yy,1.109),(.031,.056,.026),'frame')
                self.cyl('Train pipe threaded union',(xx+.27,yy,1.084),.024,.060,'cast','X',segments=8)
        for bx in [-7.3915,7.3915]:
            self.tube('Body to bogie flexible brake feed',[(bx,.04,1.086),(bx-.23,.14,.978),(bx-.20,.36,.87),(bx+.11,.41,.949)],.013,'rubber')
        for xx in [-1.55,0,2.20]:
            self.tube('Underframe pneumatic equipment pipe',[(xx,.01,1.084),(xx,.38,1.084),(xx,.38,.90)],.011,'steel')
        # Looped electrical conduits and visible cable support saddles.
        self.tube('Main insulated lighting cable conduit',[(-7.0,-.42,1.125),(-4.7,-.42,1.125),(-4.7,-1.00,1.08),(-2.65,-1.00,1.08),(-2.65,-.42,1.125),(7.0,-.42,1.125)],.014,'rubber')
        for x in [-4.38,-3.02,3.02,4.38]:self.tube('Battery terminal cable',[(x,-1.02,1.01),(x,-.60,1.06),(x,-.43,1.125)],.012,'rubber')
        if self.ac:
            # Traditional under-slung AC refrigeration train: two condensers,
            # compressor units and receiver, rather than an LHB equipment skirt.
            for xx in [-2.8,2.8]:
                self.cabinet('Under-slung AC condenser',xx,1.03,.765,1.72,.74,.49,2,True)
                for fx in [xx-.42,xx+.42]:
                    self.cyl('Condenser underside fan shroud',(fx,1.03,.504),.226,.050,'frame','Z',segments=40)
                    for rr in [.08,.145,.211]:self.ring('Condenser circular fan guard',(fx,1.03,.470),rr,.004,'steel','Z',nseg=32)
                    for k in range(8):
                        aa=k*pi/4;self.rod('Condenser grille radial wire',(fx,1.03,.467),(fx+.221*cos(aa),1.03+.221*sin(aa),.467),.003,'steel',sides=6)
                    self.cyl('Condenser fan hub',(fx,1.03,.489),.047,.043,'cast','Z',segments=20)
            for xx in [-.68,.68]:
                self.cyl('Refrigeration compressor housing',(xx,1.00,.767),.174,.42,'cast','X',segments=36)
                self.box('Compressor steel mounting skid',(xx,1.00,.563),(.57,.57,.054),'frame')
                self.cyl('Compressor upper terminal head',(xx,1.00,.971),.088,.142,'frame','Z',segments=24)
                self.tube('Refrigerant formed copper pipe',[(xx+.22,1.00,.83),(xx+.28,.73,.83),(xx+.28,.73,1.11),(xx+1.3,.73,1.11)],.009,'brass')
            self.cabinet('AC battery charger precooling box',0,-1.01,.764,1.46,.59,.491,3,True)
        else:
            self.cabinet('Lighting switch fuse cabinet',0,-1.03,.918,.55,.40,.281,1,False)
        self.body=oldbody
        return eq


def build(api, ac=False):
    """Build both conventional ICF bogies plus undergear exactly once.

    API mesh and primitives accept WORLD/vehicle coordinates and preserve their
    world placement on parenting. API empty has parent-local location semantics.
    No structural coach floor, solebars, toilet tanks or coach end gear are added.
    """
    g=_Gear(api,bool(ac));bogies=[];axles=[]
    for i,bx in enumerate([-7.3915,7.3915],1):
        bg,ars=g.bogie(bx,i);bogies.append(bg.name);axles.extend(a.name for a in ars)
    eq=g.undergear();bpy.context.view_layer.update()
    return {"component":"Conventional ICF all-coil running gear", "version":"v02.3", "ac":bool(ac),
        "refs":REFERENCES, "nominaldims":NOMINAL_DIMENSIONS,
        "bogie_names":bogies,"axle_names":axles,"equipment_root":eq.name,
        "created_objects":len(g.created),"primary_springs":16,"secondary_springs":8,
        "brake_blocks":16,"wheelsets":4,"alternators":2 if ac else 1,"alternator_belts":24 if ac else 4,
        "scope_notes":["Major design, suspension topology and nominal leading dimensions are referenced; local castings, fasteners, equipment arrangement and small pipe routes are visual interpretations.","Monobloc wheel profile preserves nominal tread diameter and broad-gauge back-to-back. It is a visual section, not a manufacturing tread gauge.","Self-generating equipment subtype is used; Traditional underslung split-AC units carry two 18kW alternators, each with two six-belt drives; non-AC carries one four-belt 4.5kW alternator.","All-coil suspension and bogie-mounted tread brakes; no FIAT disc brakes or air springs."]}
