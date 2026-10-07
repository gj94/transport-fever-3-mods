"""Prototype-length VB2 cab: rigid ergonomic subassemblies in a drawing-led envelope.
The exact fascia inscriptions, diagnostic pages and switch allocations are illustrative.
apply(ctx) is intentionally a no-op for every type other than DTC.
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from common import box, cyl, ring, tube, rod, mesh, sphere, extrude_xy, remove_prefix

PREFIX = 'VB02_CAB_'
PHOTO = 'https://commons.wikimedia.org/wiki/File:Cabin_of_Vande_Bharat_Express.jpg'
OEM = 'https://rskr.irimee.in/forum/wp-content/uploads/2023/07/Maintenance%20Manual%20for%20DD_MAE675UV2.pdf'
LAYOUT_REFERENCE = 'CAMTECH Maintenance Manual of VBE Trainset V2.0, DTC drawing TS/DTC-9-0-001, p28'


def _material(name, color, rough=.5, metal=0, grain=0, emission=0):
    m = bpy.data.materials.get(PREFIX+name) or bpy.data.materials.new(PREFIX+name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1)
    nd=m.node_tree.nodes; nd.clear()
    p=nd.new('ShaderNodeBsdfPrincipled'); out=nd.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'],out.inputs[0])
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1)
        p.inputs['Emission Strength'].default_value=emission
    if grain:
        tex=nd.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=820
        tex.inputs['Detail'].default_value=2
        bump=nd.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.14
        bump.inputs['Distance'].default_value=grain
        m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m


def _remove_old():
    # These are exclusively the cab's former visuals. Never delete or alter empties.
    owned = {'Cab_console','Console_wings','Driver_seats','Driver_pedals',
        'Driver_screen_frame','Driver_screens','Screen_UI_lines','Analog_gauges',
        'Gauge_faces','Gauge_needles','Console_buttons','Control_levers'}
    removed=[]
    for o in list(bpy.data.objects):
        base=o.name.split('.')[0]
        if o.type == 'MESH' and base in owned:
            removed.append(o.name); bpy.data.objects.remove(o,do_unlink=True)
    # Standalone application also works when the interior has not been rebuilt.
    # These baseline mesh objects contain both passenger and driver subassemblies.
    for o in list(bpy.data.objects):
        if o.type=='MESH' and o.name.split('.')[0] in {'Seat_armrests','Seat_armrest_posts','Seat_pedestals','Seat_mounts'}:
            bm=bmesh.new(); bm.from_mesh(o.data)
            vs=[v for v in bm.verts if (o.matrix_world@v.co).x>5.9]
            if vs:
                bmesh.ops.delete(bm,geom=vs,context='VERTS'); bm.to_mesh(o.data); o.data.update()
            bm.free()
    return removed


def apply(ctx):
    if ctx['kind']!='DTC':
        return {'component':'cab','applied':False,'reason':'Driving cab belongs to DTC only'}
    remove_prefix(PREFIX)
    removed=_remove_old()
    parent=ctx['body']; coll=ctx['collection']; base=ctx['materials']
    # Absolute metre datums, coordinated with the prototype shell/base builder.
    # DTC's 24 m pitch is dimensioned by ICF. Cab stations are drawing-read fits,
    # not claimed factory dimensions. Devices and seats are never stretched.
    layout=ctx.get('layout', {})
    partition_x=layout.get('cab_partition_x', 7.30)
    driver_x=layout.get('driver_x', 9.35)
    floor_z=layout.get('floor_z', 1.32)
    nose_dx=layout.get('nose_dx', 1.72169)
    fascia_x=driver_x+.98
    windshield_lower_x=9.80+nose_dx
    windshield_upper_x=8.65+nose_dx
    current_zone='console'
    offsets={'console':(fascia_x-7.37,0,0),
             'seating':(driver_x-6.39,0,0),
             'floor':(driver_x-6.39,0,floor_z-1.31),
             'rear':(partition_x-5.56,0,0),
             'ceiling':(partition_x-5.56,0,0),
             'windscreen':(nose_dx-.070,0,0),
             'prototype':(0,0,0)}
    M=dict(base)
    M.update({
      'desk':_material('Blue_grey_moulded_console',(.105,.165,.22),.38,grain=.00010),
      'panel':_material('Charcoal_instrument_tiles',(.031,.039,.043),.49,grain=.000055),
      'seat':_material('Black_seat_vinyl',(.018,.022,.026),.56,grain=.00014),
      'seam':_material('Seat_stitching',(.115,.126,.13),.88),
      'stitchdark':_material('Seat_seam_shadow',(.006,.008,.010),.85),
      'dial':_material('Warm_white_gauge_print',(.76,.81,.77),.55),
      'print':_material('White_screenprint',(.81,.85,.81),.62),
      'ink':_material('Printed_black',(.007,.012,.015),.7),
      'screenbg':_material('Display_dark_glass',(.008,.019,.025),.28),
      'uiwhite':_material('UI_white',(.68,.79,.73),.55,emission=.25),
      'uiblue':_material('UI_blue',(.027,.21,.35),.48,emission=.22),
      'uigreen':_material('UI_green',(.12,.58,.29),.45,emission=.25),
      'uired':_material('UI_red',(.68,.042,.025),.5,emission=.15),
      'uiamber':_material('UI_amber',(.82,.43,.047),.48,emission=.22),
      'trim':_material('Cab_lining_warm_grey',(.61,.63,.59),.44),
      'shade':_material('Windscreen_shade_fabric',(.43,.44,.38),.82,grain=.00018),
      'mat':_material('Cab_floor_rubber_mat',(.045,.052,.059),.86,grain=.00017),
    })
    made=[]; labels=[]
    def mark(o, group=None):
        # One rigid translation per functional subassembly, including text.
        # Keeping every local ergonomic dimension avoids stretched furniture.
        shift=offsets[current_zone]
        o.location+=Vector(shift)
        o['cab_fit_zone']=current_zone
        o['cab_rigid_offset_m']=shift
        made.append(o)
        if group:o['cab_group']=group
        return o
    def B(n,c,d,ma='panel',b=.002,g=None):
        return mark(box(PREFIX+n,c,d,M[ma],parent,coll,b),g)
    def C(n,c,r,d,ma='steel',axis='Z',N=24,g=None):
        return mark(cyl(PREFIX+n,c,r,d,M[ma],parent,coll,axis,N),g)
    def R(n,c,ro,ri,d,ma='steel',axis='Z',N=36,g=None):
        return mark(ring(PREFIX+n,c,ro,ri,d,M[ma],parent,coll,axis,N),g)
    def T(n,pts,r,ma='black',N=10,g=None):
        return mark(tube(PREFIX+n,pts,r,M[ma],parent,coll,N),g)
    def S(n,c,r,ma='black',scale=(1,1,1),g=None):
        return mark(sphere(PREFIX+n,c,r,M[ma],parent,coll,24,12,scale),g)
    def X(n,poly,z0,z1,ma='desk',b=.02,g=None):
        return mark(extrude_xy(PREFIX+n,poly,z0,z1,M[ma],parent,coll,b),g)
    def faceframe(origin,u=(0,-1,0),v=(0,0,1)):
        u=Vector(u).normalized();v=Vector(v).normalized();n=u.cross(v).normalized()
        return Vector(origin),u,v,n
    def P(fr,a,b,h=0):
        o,u,v,n=fr;return tuple(o+u*a+v*b+n*h)
    def fb(n,fr,c,d,ma='panel',bevel=.002,g=None):
        # Boxes in an arbitrary instrument/desk plane; local Z faces the operator.
        a,b,h=c; w,he,th=d; verts=[]
        for za in [-1,1]:
            for ua,va in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                verts.append(P(fr,a+ua*w/2,b+va*he/2,h+za*th/2))
        return mark(mesh(PREFIX+n,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],M[ma],parent,coll,bevel),g)
    def disc(n,fr,a,b,r,depth=.007,ma='steel',h=0,N=40,g=None):
        verts=[P(fr,a+r*math.cos(i*math.tau/N),b+r*math.sin(i*math.tau/N),h+z) for z in [-depth/2,depth/2] for i in range(N)]
        faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
        o=mark(mesh(PREFIX+n,verts,faces,M[ma],parent,coll),g)
        for f in o.data.polygons:
            if len(f.vertices)==4:f.use_smooth=True
        return o
    def line(n,fr,pts,r=.001,ma='print',h=.01,g=None):
        return T(n,[P(fr,a,b,h) for a,b in pts],r,ma,6,g)
    def text(n,body,fr,a,b,size=.014,ma='print',h=.01,align='CENTER',g=None):
        cu=bpy.data.curves.new(PREFIX+n+'_font','FONT');cu.body=body;cu.size=size
        cu.align_x=align;cu.align_y='CENTER';cu.space_character=1.10
        cu.extrude=.000055;cu.resolution_u=2
        ob=bpy.data.objects.new(PREFIX+n+'_font',cu);coll.objects.link(ob)
        ob.location=P(fr,a,b,h)
        o,u,v,norm=fr;ob.rotation_euler=Matrix((u,v,norm)).transposed().to_euler()
        bpy.context.view_layer.update()
        me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        res=bpy.data.objects.new(PREFIX+n,me);coll.objects.link(res);res.matrix_world=ob.matrix_world
        res.parent=parent;res.matrix_parent_inverse=parent.matrix_world.inverted();me.materials.append(M[ma])
        bpy.data.objects.remove(ob,do_unlink=True);bpy.data.curves.remove(cu)
        res['inscription']=body;labels.append(body)
        return mark(res,g)
    def screw(n,fr,a,b,h=.012,r=.004,g=None):
        disc(n+' head',fr,a,b,r,.0026,'steel',h,16,g)
        line(n+' cross 1',fr,[(a-r*.60,b),(a+r*.60,b)],.00042,'ink',h+.0015,g)
        line(n+' cross 2',fr,[(a,b-r*.60),(a,b+r*.60)],.00042,'ink',h+.0015,g)
    def panel(n,fr,w,h,ma='panel',group=None):
        fb(n+' gasket',fr,(0,0,-.004),(w+.014,h+.014,.012),'rubber',.010,group)
        fb(n+' removable tile',fr,(0,0,.004),(w,h,.012),ma,.007,group)
        for a in [-w/2+.013,w/2-.013]:
            for b in [-h/2+.013,h/2-.013]:screw(n+' captive screw',fr,a,b,.012,g=group)
    def button(n,fr,a,b,col='green',label='',r=.0135,g=None):
        disc(n+' bezel',fr,a,b,r+.004,.007,'brushed',.017,28,g)
        disc(n+' gasket',fr,a,b,r+.001,.007,'rubber',.022,28,g)
        disc(n+' lens',fr,a,b,r,.008,col,.027,28,g)
        if label:text(n+' label',label,fr,a,b-r-.013,.0085,h=.012,g=g)
    def toggle(n,fr,a,b,label,setting=0,g=None):
        disc(n+' collar',fr,a,b,.017,.006,'steel',.02,24,g)
        disc(n+' boot',fr,a,b,.012,.012,'rubber',.026,24,g)
        T(n+' stem',[P(fr,a,b,.03),P(fr,a+.008*setting,b+.014,.061)],.0038,'brushed',10,g)
        S(n+' switch tip',P(fr,a+.008*setting,b+.014,.063),.0075,'black',(.80,.8,1.6),g)
        text(n+' legend',label,fr,a,b-.03,.009,h=.012,g=g)
    # Continuous blue-grey moulded desk: front cowl, return wings and thin top reveal.
    outline=[(6.69,1.405),(7.45,1.45),(8.16,1.33),(8.35,1.07),(8.40,.60),(8.41,0),(8.40,-.60),(8.35,-1.07),(8.16,-1.33),(7.45,-1.45),(6.69,-1.405),(6.64,-1.115),(6.91,-1.01),(7.00,-.78),(6.98,-.43),(6.92,0),(6.98,.43),(7.00,.78),(6.91,1.01),(6.64,1.115)]
    X('sculpted horseshoe desktop',outline,1.945,2.02,'desk',.045)
    # Raised under-windshield cowl. This remains below the baseline sill at Z2.30.
    cowl=[(7.40,-1.29),(7.68,-1.42),(8.16,-1.33),(8.38,-1.04),(8.40,0),(8.38,1.04),(8.16,1.33),(7.68,1.42),(7.40,1.29)]
    X('upper curved instrument binnacle',cowl,2.016,2.295,'desk',.045)
    X('top anti glare brow',[(7.34,-1.24),(7.54,-1.43),(8.10,-1.34),(8.21,0),(8.10,1.34),(7.54,1.43),(7.34,1.24)],2.298,2.326,'panel',.014)
    # Redrawn short demister shelf: no scaling of console/chair/control geometry.
    # Its nose-facing perimeter stays 105 mm behind the curved lower pane datum.
    current_zone='prototype'
    shelf_front=lambda y:windshield_lower_x-.24*(y/1.55)**2-.105
    shelf=[(fascia_x+.64,-1.31),(shelf_front(-1.31),-1.31),
           (shelf_front(-1.20),-1.20),(shelf_front(-.82),-.82),
           (shelf_front(0),0),(shelf_front(.82),.82),
           (shelf_front(1.20),1.20),(shelf_front(1.31),1.31),
           (fascia_x+.64,1.31)]
    X('forward windshield demister shelf',shelf,2.162,2.242,'panel',.021)
    current_zone='console'
    # Glareshield fascia is supported by this blue-grey front web.
    main=faceframe((7.37,0,2.165),v=(.18,0,.983666))
    fb('continuous sloping main fascia',main,(0,0,-.012),(2.66,.365,.035),'desk',.015)
    for s in [-1,1]:
        X('side console pedestal '+str(s),[(6.72,s*1.105),(6.72,s*1.405),(7.75,s*1.42),(7.83,s*1.13)],1.32,1.945,'desk',.018)
        fr=faceframe((6.711,s*1.256,1.635))
        panel('return cabinet '+str(s),fr,.25,.51,'desk')
        fb('return cabinet recessed latch '+str(s),fr,(0,-.095,.022),(.072,.028,.011),'black',.004)
        for z in [1.46,1.83]:C('return cabinet hinge '+str(s),(6.696,s*1.377,z),.01,.08,'steel','Z',16)
        # Swept instrument side tiles: rotate toward their associated seat.
        u=Vector((-.62,-s*.785,0));v=Vector((.10*s,-.079, .992)).normalized()
        if s==-1:u=-u;v=Vector((.10,-.079,.992)).normalized()
        # Exact cross product orientation is made operator-facing for either side.
        u=Vector((-.50*s,-.866,0));v=Vector((.15, -.0866*s, .985)).normalized()
        side=faceframe((7.16,s*1.23,2.116),u,v)
        panel('side auxiliary fascia '+str(s),side,.37,.205,group='side controls '+str(s))
        for i,(lab,col) in enumerate([('CAB','green'),('BLOWER','green'),('LAMP','amber'),('ACK','uiblue')]):
            button('wing indicator '+str(s)+str(i),side,-.133+i*.088,.041,col,lab,.0115,'side controls '+str(s))
        for i,lab in enumerate(['LIGHT','WIPER','WASH']):toggle('wing selector '+str(s)+str(i),side,-.112+i*.112,-.025,lab,1,'side controls '+str(s))
    # Main upper tiles closely follow the inspected photo's asymmetric arrangement.
    # Left: TCMS display; center-left: analogue speed; center: 4x4 annunciators;
    # center-right: smaller driver display. Outboard pressure gauges are separate.
    display=faceframe(P(main,-.815,0,.022),v=(.18,0,.983666))
    panel('TCMS primary display',display,.44,.323,group='TCMS interface')
    fb('TCMS inset screen',display,(0,.012,.021),(.351,.221,.009),'screenbg',.005,'TCMS interface')
    # Static original geometry, deliberately not an exact supplier software image.
    text('TCMS heading','TRAIN STATUS',display,0,.102,.014,'uiwhite',.028,g='TCMS interface')
    line('TCMS heading rule',display,[(-.159,.082),(.159,.082)],.0007,'uiblue',.028,'TCMS interface')
    for i in range(8):
        a=-.142+i*.04
        fb('TCMS car block '+str(i),display,(a,.038,.028),(.032,.031,.001),'uiblue',0,'TCMS interface')
        text('TCMS car ID '+str(i),str(i+1),display,a,.038,.010,'uiwhite',.03,g='TCMS interface')
        disc('TCMS car healthy '+str(i),display,a,.013,.0035,.001,'uigreen',.03,12,'TCMS interface')
    for j,(title,value) in enumerate([('MODE','STANDBY'),('DOORS','CLOSED'),('BRAKE','APPLIED')]):
        b=-.023-j*.029
        text('TCMS status title '+str(j),title,display,-.15,b,.0105,'uiwhite',.03,'LEFT','TCMS interface')
        text('TCMS status value '+str(j),value,display,.143,b,.0105,'uigreen',.03,'RIGHT','TCMS interface')
    for s in [-1,1]:
        for j in range(5):
            fb('TCMS bezel key',display,(s*.197,.08-j*.039,.019),(.014,.019,.007),'black',.001,'TCMS interface')
            line('TCMS bezel key glyph',display,[(s*.197-.003,.08-j*.039),(s*.197+.003,.08-j*.039)],.0006,'print',.024,'TCMS interface')
    for i in range(8):fb('TCMS softkey',display,(-.14+i*.04,-.139,.019),(.022,.016,.007),'black',.001,'TCMS interface')
    text('TCMS bezel name','TCMS  /  DRIVER INTERFACE',display,0,-.111,.009,'print',.03,g='TCMS interface')
    # OEM August 2022 drawing explicitly shows an unpopulated TCAS bay.
    tcas=faceframe(P(main,-.453,0,.022),v=(.18,0,.983666))
    panel('reserved TCAS interface bay',tcas,.264,.323,group='TCAS reserved bay')
    fb('TCAS blanking plate',tcas,(0,0,.02),(.226,.266,.006),'panel',.004,'TCAS reserved bay')
    text('TCAS bay lower legend','TCAS',tcas,0,-.119,.009,h=.026,g='TCAS reserved bay')
    # In use, all analogue dials have editable needles, numbers and major/minor ticks.
    def gauge(name,fr,a,b,r,scale_max,label,value=0,double=False,group='analogue instruments'):
        disc(name+' mounting ring',fr,a,b,r+.008,.014,'black',.022,64,group)
        disc(name+' silver bezel',fr,a,b,r+.004,.012,'brushed',.030,64,group)
        disc(name+' dial face',fr,a,b,r-.003,.004,'dial',.038,64,group)
        for i in range(41):
            an=math.radians(220-i*260/40);major=i%5==0
            ra=r*(.73 if major else .81);rb=r*.9
            line(name+' tick '+str(i),fr,[(a+ra*math.cos(an),b+ra*math.sin(an)),(a+rb*math.cos(an),b+rb*math.sin(an))],.0008 if major else .00042,'ink',.041,group)
            if major:
                text(name+' numeral '+str(i),str(int(scale_max*i/40)),fr,a+r*.585*math.cos(an),b+r*.585*math.sin(an),r*.14,'ink',.041,g=group)
        text(name+' unit',label,fr,a,b-r*.38,r*.13,'ink',.041,g=group)
        ang=math.radians(220-value/scale_max*260)
        line(name+' needle',fr,[(a-r*.17*math.cos(ang),b-r*.17*math.sin(ang)),(a+r*.69*math.cos(ang),b+r*.69*math.sin(ang))],.0019,'uired',.045,group)
        if double:
            ang=math.radians(220-4.8/scale_max*260)
            line(name+' second needle',fr,[(a,b),(a+r*.63*math.cos(ang),b+r*.63*math.sin(ang))],.00145,'ink',.046,group)
        disc(name+' spindle',fr,a,b,.006,.004,'steel',.048,20,group)
    speed=faceframe(P(main,-.177,0,.022),v=(.18,0,.983666))
    panel('speed recorder tile',speed,.22,.323,group='speed instrument')
    gauge('speed recorder',speed,0,.035,.086,200,'km/h',0,group='speed instrument')
    text('speed recorder label','SPEED RECORDER',speed,0,.139,.009,h=.025,g='speed instrument')
    fb('speed recorder LCD',speed,(0,-.080,.025),(.127,.034,.008),'screenbg',.001,'speed instrument')
    text('speed recorder LCD digits','000.0 km/h',speed,0,-.078,.012,'uigreen',.031,g='speed instrument')
    for j in range(2):
        for k in range(6):fb('speed recorder keypad',speed,(-.057+k*.023,-.118-j*.016,.025),(.018,.011,.003),'rubber',0,'speed instrument')
    ann=faceframe(P(main,.118,0,.022),v=(.18,0,.983666))
    panel('central annunciator tile',ann,.30,.323,group='annunciators')
    alarm_labels=[['VCB','PANTO','FAULT','TRIP'],['HV','AUX','BRAKE','SLIP'],['DOOR','TCMS','BATT','FIRE'],['READY','CAB','ACK','TEST']]
    alarm_cols=[['amber','amber','red','red'],['red','amber','red','red'],['red','black','uiblue','uiblue'],['green','green','amber','red']]
    for j in range(4):
        for k in range(4):button('annunciator '+str(j)+str(k),ann,-.107+k*.071,.104-j*.070,alarm_cols[j][k],alarm_labels[j][k],.014,'annunciators')
    small=faceframe(P(main,.465,0,.022),v=(.18,0,.983666))
    panel('secondary driver display',small,.34,.323,group='secondary display')
    for k in range(4):button('secondary lamp '+str(k),small,-.115+k*.076,.115,['uiblue','black','black','black'][k],'',.012,'secondary display')
    fb('secondary screen',small,(0,-.025,.021),(.27,.165,.008),'screenbg',.004,'secondary display')
    fb('secondary top bar',small,(0,.044,.027),(.25,.022,.001),'uiblue',0,'secondary display')
    text('secondary page title','PIS / COMMUNICATION',small,0,.044,.012,'uiwhite',.029,g='secondary display')
    for j,(lab,val) in enumerate([('PA','READY'),('INTERCOM','READY'),('CAB LINK','STANDBY')]):
        text('secondary pressure '+str(j),lab,small,-.10,.01-j*.029,.012,'uiwhite',.029,'LEFT','secondary display')
        text('secondary value '+str(j),val,small,.103,.01-j*.029,.012,'uigreen',.029,'RIGHT','secondary display')
    text('secondary page footer','MCP  /  CREW COMMUNICATION',small,0,-.12,.009,h=.024,g='secondary display')
    cctv=faceframe(P(main,.814,0,.022),v=(.18,0,.983666))
    panel('CCTV display tile',cctv,.325,.323,group='CCTV interface')
    fb('CCTV glass inset',cctv,(0,.015,.021),(.269,.219,.009),'screenbg',.003,'CCTV interface')
    text('CCTV heading','CCTV  /  CAMERA SELECT',cctv,0,.108,.010,'uiwhite',.028,g='CCTV interface')
    # Original schematic quadrants, not photography or a fabricated external view.
    for j in range(2):
        for k in range(2):
            a=-.066+k*.133;b=.047-j*.087
            fb('CCTV channel pane',cctv,(a,b,.028),(.119,.071,.001),'uiblue',0,'CCTV interface')
            text('CCTV channel status','CAM '+str(1+j*2+k),cctv,a,b+.013,.010,'uiwhite',.03,g='CCTV interface')
            text('CCTV channel ready','STANDBY',cctv,a,b-.015,.008,'uiwhite',.03,g='CCTV interface')
    for k in range(5):fb('CCTV bezel key',cctv,(-.105+k*.052,-.132,.019),(.029,.016,.007),'black',.001,'CCTV interface')
    for s in [-1,1]:
        gf=faceframe(P(main,s*1.214,-.017,.022),v=(.18,0,.983666))
        panel('pressure instrument tile '+str(s),gf,.207,.292,group='pressure instruments '+str(s))
        if s<0:
            gauge('MR BC pressure dial',gf,.034,.071,.054,10,'MR / BC',8,True,'pressure instruments '+str(s))
            gauge('BP pressure dial',gf,-.032,-.055,.054,10,'BP',5,False,'pressure instruments '+str(s))
        else:
            gauge('guard BP pressure dial',gf,0,.031,.079,10,'bar',5,False,'pressure instruments '+str(s))
            text('guard pressure legend','BRAKE PIPE',gf,0,-.105,.009,h=.025,g='pressure instruments '+str(s))
    # Horizontal driver desk panels. All controls are actual mechanical geometry.
    desk=faceframe((7.159,0,2.033),u=(0,-1,0),v=(1,0,0))
    for a,w in [(-.64,.47),(-.20,.25),(.18,.30),(.60,.37)]:
        fr=faceframe(P(desk,a,0),u=(0,-1,0),v=(1,0,0));panel('desktop removable panel '+str(a),fr,w,.322)
    # Master controller T handle below the speed-recorder region (OEM Figure 6).
    fb('master gate slot',desk,(-.185,-.004,.014),(.27,.028,.004),'black',.005,'master controller')
    for i,lab in enumerate(['B','0','P1','P2','P3','P4']):
        a=-.303+i*.047
        line('master controller detent '+str(i),desk,[(a,.02),(a,.034)],.001,'print',.023,'master controller')
        text('master controller legend '+str(i),lab,desk,a,.057,.012,h=.023,g='master controller')
    C('master controller shaft',P(desk,-.23,-.004,.083),.012,.12,'brushed','Z',24,'master controller')
    # T grip is horizontal across the control's axis, as visible in the reference.
    C('master controller horizontal grip',P(desk,-.23,-.004,.149),.022,.19,'black','Y',32,'master controller')
    for y in [-.075,.075]:R('master grip collar',P(desk,-.23+y,-.004,.149),.023,.021,.004,'rubber','Y',32,'master controller')
    text('master controller label','TRACTION / BRAKE',desk,-.185,-.10,.014,h=.025,g='master controller')
    # Paired independent/automatic brake controls sit beneath the outer-left TCMS.
    for a,n,ht in [(-.865,'automatic brake controller',.17),(-.70,'independent brake controller',.10)]:
        disc(n+' base',desk,a,-.038,.043,.012,'brushed',.023,48,n)
        disc(n+' rubber boot',desk,a,-.038,.031,.018,'rubber',.035,40,n)
        for j in range(4):R(n+' boot convolution',P(desk,a,-.038,.045+j*.010),.027-j*.003,.017-j*.002,.008,'rubber','Z',32,n)
        T(n+' lever',[P(desk,a,-.038,.065),P(desk,a+.01,-.035,ht)],.007,'steel',16,n)
        S(n+' grip',P(desk,a+.01,-.035,ht+.013),.024,'black',(.75,.75,.84),n)
        text(n+' label','AUTO BRAKE' if ht>.12 else 'IND. BRAKE',desk,a,-.111,.011,h=.024,g=n)
    # Small forward/neutral/reverse selector beneath the reserved TCAS plate.
    disc('direction selector collar',desk,-.443,-.052,.022,.007,'steel',.025,32,'direction selector')
    fb('direction selector rotary grip',desk,(-.443,-.052,.044),(.011,.044,.025),'black',.004,'direction selector')
    for j,lab in enumerate(['F','N','R']):text('direction legend '+lab,lab,desk,-.480+j*.039,.00,.012,h=.027,g='direction selector')
    text('direction selector label','DIRECTION',desk,-.443,-.11,.012,h=.027,g='direction selector')
    # The slender tall devices around the MCP are communications microphones.
    for a in [.287,.626]:
        disc('microphone base',desk,a,.075,.026,.010,'black',.021,32,'gooseneck microphones')
        points=[P(desk,a,.075,.023),P(desk,a,.078,.18),P(desk,a+.016,.063,.274),P(desk,a+.032,.025,.315)]
        T('flexible microphone gooseneck',points,.0053,'black',12,'gooseneck microphones')
        S('microphone capsule',points[-1],.011,'panel',(.85,.85,2.35),'gooseneck microphones')
        for i in range(18):R('microphone stem corrugation',P(desk,a,.076,.054+i*.006),.0062,.0054,.0016,'dark_metal','Z',16,'gooseneck microphones')
    for a,lab,col in [(.49,'HORN','black'),(.60,'VIGILANCE','amber'),(.71,'RESET','green')]:button('desktop '+lab,desk,a,-.006,col,lab,.018,'desk pushbuttons')
    # Mushroom emergency control on the outboard area, recessed in a yellow warning ring.
    stop=faceframe((6.98,-1.235,2.03),u=(0,-1,0),v=(1,0,0))
    disc('emergency surround',stop,0,0,.047,.006,'amber',.009,48,'emergency controls')
    C('emergency mushroom stalk',(6.98,-1.235,2.065),.016,.061,'black','Z',24,'emergency controls')
    S('emergency mushroom',(6.98,-1.235,2.098),.035,'red',(1,1,.48),'emergency controls')
    text('emergency stop label','EMERGENCY',stop,0,-.072,.011,h=.008,g='emergency controls')
    # Communications: cradle, handset, coiled lead, speaker and keypad.
    radio=faceframe((6.96,1.236,2.045),u=(0,-1,0),v=(1,0,0))
    panel('cab radio control panel',radio,.245,.285,group='communications')
    fb('radio frequency display',radio,(0,.086,.027),(.15,.042,.008),'screenbg',.003,'communications')
    text('radio channel text','CAB RADIO  01',radio,0,.086,.011,'uigreen',.033,g='communications')
    for j in range(3):
        for i in range(3):
            a=-.045+i*.045;b=.027-j*.04
            fb('radio keypad '+str(j)+str(i),radio,(a,b,.026),(.032,.026,.009),'black',.003,'communications')
            text('radio keypad glyph '+str(j)+str(i),str(1+j*3+i),radio,a,b,.010,h=.032,g='communications')
    for a in [-.094,.094]:disc('radio rotary knob',radio,a,-.106,.015,.017,'black',.03,24,'communications')
    B('radio handset cradle',(6.98,1.01,2.045),(.27,.075,.025),'black',.01,'communications')
    T('radio handset moulding',[(6.86,1.01,2.085),(6.885,1.01,2.12),(7.075,1.01,2.12),(7.10,1.01,2.085)],.021,'black',16,'communications')
    for xx in [6.87,7.09]:S('radio receiver end',(xx,1.01,2.089),.035,'black',(1.2,.95,.62),'communications')
    coil=[]
    for i in range(241):
        t=i/240;a=t*math.tau*20
        coil.append((6.82-.08*t,1.01+.18*t+.012*math.cos(a),2.085-.34*math.sin(math.pi*t)+.012*math.sin(a)))
    T('radio handset curled cable',coil,.003,'black',6,'communications')
    # Center equipment cabinet has separated socket covers and clear panel boundaries.
    B('central underdesk equipment tower',(7.32,0,1.64),(.48,.49,.60),'desk',.012)
    apron=faceframe((7.071,0,1.66))
    panel('central equipment access panel',apron,.446,.571,'panel',group='lower equipment cabinet')
    text('central equipment title','CAB EQUIPMENT',apron,0,.235,.018,h=.02,g='lower equipment cabinet')
    for j in range(2):
        for s in [-1,1]:
            a=s*.107;b=.13-j*.171
            fb('covered auxiliary socket',apron,(a,b,.023),(.115,.112,.012),'black',.007,'lower equipment cabinet')
            line('socket cover hinge',apron,[(a-.035,b+.039),(a+.035,b+.039)],.003,'steel',.033,'lower equipment cabinet')
            text('socket legend','AUX',apron,a,b-.010,.014,h=.035,g='lower equipment cabinet')
    for i in range(11):fb('equipment cabinet air slot',apron,(-.18+i*.036,-.24,.019),(.017,.036,.003),'black',.003,'lower equipment cabinet')
    def upholstery_loft(n,y,profiles,ma='seat'):
        # Superelliptical padded sections provide a shaped silhouette and broad,
        # softly crowned face rather than a stack of rectangular cushion blocks.
        vs=[];fs=[];N=40
        for z,x,w,d in profiles:
            for i in range(N):
                a=i*math.tau/N;cx=math.cos(a);sy=math.sin(a)
                vs.append((x+d/2*math.copysign(abs(cx)**.60,cx),y+w/2*math.copysign(abs(sy)**.60,sy),z))
        fs.append(tuple(reversed(range(N))))
        for j in range(len(profiles)-1):
            for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
        fs.append(tuple(range((len(profiles)-1)*N,len(profiles)*N)))
        o=mark(mesh(PREFIX+n,vs,fs,M[ma],parent,coll,smooth=True))
        o.data.polygons[0].use_smooth=False;o.data.polygons[-1].use_smooth=False
        return o
    # Reposition full-size chairs while retaining the cushion-top height 1.75 m.
    # Prototype marker relocation belongs to the base builder, not this module.
    for idx,y in enumerate([-.73,.73],1):
        current_zone='seating'
        tag='seat '+str(idx);x=6.39
        B(tag+' floor mounting plate',(x,y,floor_z+.014),(.42,.47,.028),'dark_metal',.008)
        for dx in [-.145,.145]:
            for dy in [-.174,.174]:
                C(tag+' bolt washer',(x+dx,y+dy,floor_z+.032),.016,.006,'brushed','Z',24,tag+' mechanics')
                C(tag+' mounting bolt',(x+dx,y+dy,floor_z+.039),.010,.010,'steel','Z',6,tag+' mechanics')
        for dx in [-.12,.12]:B(tag+' slider rail',(x+dx,y,1.367),(.037,.36,.025),'brushed',.003,tag+' mechanics')
        C(tag+' suspension pedestal',(x-.035,y,1.445),.10,.16,'dark_metal','Z',40,tag+' mechanics')
        for z in [1.39,1.42,1.45,1.48,1.51]:R(tag+' suspension boot rib',(x-.035,y,z),.106,.093,.018,'rubber','Z',40,tag+' mechanics')
        C(tag+' swivel column',(x-.035,y,1.56),.054,.13,'brushed','Z',36,tag+' mechanics')
        B(tag+' seat pan underside',(x+.015,y,1.64),(.49,.55,.047),'dark_metal',.018)
        # Cushions are separately modelled rounded panels with soft side bolsters.
        B(tag+' seat cushion',(x+.02,y,1.702),(.50,.535,.096),'seat',.043)
        for s in [-1,1]:B(tag+' seat side bolster',(x+.035,y+s*.234,1.716),(.43,.086,.063),'seat',.028)
        upholstery_loft(tag+' ergonomic rear shell',y,[(1.756,x-.213,.37,.10),(1.792,x-.225,.515,.12),(1.94,x-.245,.535,.12),(2.17,x-.273,.533,.12),(2.32,x-.290,.510,.125),(2.395,x-.288,.443,.11),(2.429,x-.281,.28,.075)],'panel')
        back_profiles=[(1.771,x-.13,.32,.085),(1.806,x-.14,.434,.115),(1.94,x-.135,.465,.132),(2.085,x-.155,.457,.135),(2.26,x-.172,.477,.136),(2.361,x-.185,.443,.12),(2.409,x-.183,.291,.080)]
        upholstery_loft(tag+' continuous shaped back cushion',y,back_profiles)
        for s in [-1,1]:
            upholstery_loft(tag+' sculpted side bolster '+str(s),y+s*.229,[(1.797,x-.12,.046,.07),(1.84,x-.115,.078,.14),(2.05,x-.123,.073,.148),(2.24,x-.144,.070,.14),(2.345,x-.164,.058,.114),(2.374,x-.171,.024,.052)])
        # Sewn divisions follow the actual crowned face, with no floating lines.
        def seam_points(z,dz=0):
            pts=[]
            for k in range(17):
                dy=-.177+k*.354/16;zz=z+dz-.008*(1-(dy/.177)**2)
                j=next(j for j in range(len(back_profiles)-1) if back_profiles[j][0]<=zz<=back_profiles[j+1][0])
                a,b=back_profiles[j:j+2];f=(zz-a[0])/(b[0]-a[0])
                xx=a[1]*(1-f)+b[1]*f;ww=a[2]*(1-f)+b[2]*f;dd=a[3]*(1-f)+b[3]*f
                front=xx+dd/2*max(0,1-abs(dy/(ww/2))**(1/.30))**.30
                pts.append((front+.0009,y+dy,zz))
            return pts
        for z in [1.83,1.965,2.12,2.31]:
            T(tag+' upholstered seam',seam_points(z),.0015,'stitchdark',8,tag+' upholstery detail')
            for dz in [-.004,.004]:T(tag+' seam stitching',seam_points(z,dz),.00045,'seam',6,tag+' upholstery detail')
        for s in [-1,1]:
            C(tag+' headrest support',(x-.21,y+s*.12,2.473),.009,.143,'steel','Z',24,tag+' mechanics')
        upholstery_loft(tag+' separate rounded headrest',y,[(2.430,x-.208,.267,.081),(2.451,x-.212,.375,.135),(2.50,x-.222,.407,.163),(2.610,x-.238,.393,.161),(2.664,x-.239,.325,.135),(2.687,x-.236,.195,.076)])
        # Black adjustable arms and mechanical hinge hardware.
        for s in [-1,1]:
            C(tag+' armrest pivot',(x-.184,y+s*.295,1.932),.036,.026,'dark_metal','Y',32,tag+' mechanics')
            T(tag+' armrest bracket',[(x-.185,y+s*.297,1.932),(x-.075,y+s*.299,1.955),(x+.10,y+s*.299,1.955)],.017,'black',12,tag+' mechanics')
            B(tag+' padded armrest',(x+.038,y+s*.30,1.985),(.365,.066,.073),'seat',.022)
        C(tag+' recline handwheel',(x-.199,y+.291,1.758),.040,.036,'black','Y',28,tag+' mechanics')
        T(tag+' adjustment handle',[(x+.074,y-.265,1.605),(x+.208,y-.265,1.605),(x+.235,y-.25,1.628)],.008,'black',10,tag+' mechanics')
        # Floor mats, driver's deadman and adjacent treadled pedal.
        current_zone='floor'
        B(tag+' anti slip floor mat',(6.95,y,1.318),(.62,.53,.016),'mat',.014)
        for k in range(12):B(tag+' mat rib',(6.69+k*.046,y,1.328),(.010,.46,.005),'rubber',0,tag+' pedals')
        for s in [-1,1]:
            B(tag+' pedal hinge block',(7.107,y+s*.125,1.343),(.12,.085,.024),'dark_metal',.005,tag+' pedals')
            C(tag+' pedal hinge pin',(7.133,y+s*.125,1.368),.012,.10,'steel','Y',20,tag+' pedals')
            fr=faceframe((7.081,y+s*.125,1.397),u=(0,-1,0),v=(.86,0,-.51))
            fb(tag+' pedal tread',fr,(0,0,0),(.087,.174,.021),'black',.008,tag+' pedals')
            for k in range(5):fb(tag+' pedal anti slip bar',fr,(0,-.065+k*.032,.013),(.070,.007,.006),'rubber',0,tag+' pedals')
    # Interior accessory lining details do not replace the nose, glass or apertures.
    # Under-windshield defroster bank, below the existing glass and away from wipers.
    current_zone='prototype'
    for y in [-.70,0,.70]:
        vent_x=windshield_lower_x-.24*(y/1.55)**2-.245
        B('demister vent surround',(vent_x,y,2.248),(.155,.49,.026),'desk',.01)
        for j in range(9):B('demister slot',(vent_x-.012,y-.19+j*.047,2.263),(.073,.009,.003),'black',.003,'demister vents')
    # Retracted blind follows the shell, independently of the desk. The 70 mm
    # aft setback clears the curved solid header lining at the bracket top.
    current_zone='windscreen'
    C('windscreen blind roller',(8.45,0,3.195),.044,2.03,'trim','Y',40)
    B('windscreen blind fabric',(8.51,0,3.16),(.016,2.00,.065),'shade',.004)
    C('windscreen blind bottom rail',(8.51,0,3.125),.010,2.04,'brushed','Y',24)
    for s in [-1,1]:
        B('blind roller bracket '+str(s),(8.45,s*1.055,3.194),(.10,.035,.105),'trim',.01)
        T('blind pull loop '+str(s),[(8.53,s*1.038,3.16),(8.56,s*1.038,2.95),(8.57,s*1.038,2.927),(8.56,s*1.038,2.90),(8.53,s*1.038,3.16)],.0019,'seam',6,'blind fittings')
    # Back wall fittings follow the prototype partition; entrance remains clear.
    current_zone='rear'
    back=faceframe((5.606,0,2.47),u=(0,1,0),v=(0,0,1))
    for s in [-1,1]:
        fr=faceframe(P(back,s*1.055,0),u=(0,1,0),v=(0,0,1))
        panel('rear cab equipment panel '+str(s),fr,.53,.61,'trim',group='rear cab fittings')
        text('rear panel warning '+str(s),'CAB SERVICES' if s<0 else 'ELECTRICAL PANEL',fr,0,.228,.022,'ink',.017,g='rear cab fittings')
        for j in range(8):fb('rear equipment louvre',fr,(0,-.14+j*.03,.017),(.39,.008,.004),'black',.002,'rear cab fittings')
        disc('rear panel cam lock',fr,.197,.16,.012,.007,'steel',.02,24,'rear cab fittings')
    # Extinguisher / holder is at the rear corner, not in the aisle or seat envelope.
    C('fire extinguisher cylinder',(5.80,-1.358,1.77),.078,.44,'red','Z',40)
    S('fire extinguisher shoulder',(5.80,-1.358,1.981),.078,'red',(1,1,.56))
    C('fire extinguisher valve',(5.80,-1.358,2.039),.017,.045,'steel','Z',24)
    B('fire extinguisher handle',(5.83,-1.358,2.069),(.11,.025,.022),'black',.006)
    R('extinguisher retaining strap',(5.80,-1.358,1.81),.082,.078,.026,'steel','Z',40)
    B('extinguisher wall bracket',(5.80,-1.443,1.79),(.11,.03,.43),'dark_metal',.008)
    T('extinguisher hose',[(5.82,-1.37,2.041),(5.90,-1.397,1.99),(5.914,-1.403,1.69)],.010,'rubber',12)
    fr=faceframe((5.881,-1.358,1.82),u=(0,1,0),v=(0,0,1))
    fb('extinguisher instruction label',fr,(0,0,0),(.077,.146,.001),'print',.002,'rear cab fittings')
    text('extinguisher label title','FIRE',fr,0,.033,.019,'uired',.002,g='rear cab fittings')
    text('extinguisher label type','ABC',fr,0,-.005,.017,'ink',.002,g='rear cab fittings')
    # Speaker, grab handles and coat hooks, deliberately shallow on the back partition.
    fr=faceframe((5.607,.73,3.09),u=(0,1,0),v=(0,0,1))
    fb('rear speaker housing',fr,(0,0,0),(.23,.17,.022),'panel',.012,'rear cab fittings')
    for j in range(7):line('rear speaker grille',fr,[(-.088,-.056+j*.018),(.088,-.056+j*.018)],.002,'black',.014,'rear cab fittings')
    for s in [-1,1]:
        T('rear partition grab rail '+str(s),[(5.635,s*.456,1.99),(5.682,s*.456,2.035),(5.682,s*.456,2.59),(5.635,s*.456,2.64)],.015,'brushed',16)
        T('cab coat hook '+str(s),[(5.615,s*1.20,3.14),(5.67,s*1.20,3.14),(5.68,s*1.20,3.18)],.008,'steel',12,'rear cab fittings')
    # Shallow ceiling fittings above the aft entrance zone.
    current_zone='ceiling'
    B('rear cab ceiling lamp base',(6.03,0,3.64),(.47,.23,.033),'trim',.025)
    B('rear cab ceiling lamp diffuser',(6.03,0,3.617),(.39,.17,.014),'emissive',.019)
    # Identity/provenance remains machine-readable; no unsupported replica claims.
    for o in made:
        o['component']='cab';o['reference_scope']='Prototype-length VB2, drawing-read cab fit; exact placement and UI illustrative'
    # Consolidate tiny text/ticks/screws in named assemblies, preserving material slots.
    groups={}
    for o in made:
        g=o.get('cab_group')
        if g:groups.setdefault(g,[]).append(o)
    dg=bpy.context.evaluated_depsgraph_get()
    for group,objs in groups.items():
        verts=[];faces=[];mi=[];materials=[];smooth=[]
        for o in objs:
            ev=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev)
            off=len(verts);xf=parent.matrix_world.inverted()@o.matrix_world
            verts.extend([tuple(xf@v.co) for v in me.vertices])
            for p in me.polygons:
                faces.append(tuple(off+i for i in p.vertices));smooth.append(p.use_smooth)
                mat=me.materials[p.material_index] if len(me.materials)>p.material_index else M['black']
                if mat not in materials:materials.append(mat)
                mi.append(materials.index(mat))
            bpy.data.meshes.remove(me)
        result=mesh(PREFIX+group.replace(' ','_'),verts,faces,materials,parent,coll,local=True)
        for p,m,s in zip(result.data.polygons,mi,smooth):p.material_index=m;p.use_smooth=s
        result['component']='cab';result['detail_parts']=len(objs)
        result['reference_scope']='Prototype-length VB2, drawing-read cab fit; exact placement and UI illustrative'
        result['cab_fit_zones']=sorted(set(o.get('cab_fit_zone','') for o in objs))
        result['ergonomic_scale']=(1.,1.,1.)
        for o in objs:bpy.data.objects.remove(o,do_unlink=True)
    # Remove orphaned intermediate meshes created by the procedural grouping pass.
    for me in list(bpy.data.meshes):
        if me.name.startswith(PREFIX) and me.users==0:bpy.data.meshes.remove(me)
    objects=[o for o in coll.objects if o.name.startswith(PREFIX)]
    return {'component':'cab','applied':True,'objects':len(objects),
        'vertices':sum(len(o.data.vertices) for o in objects if o.type=='MESH'),
        'faces':sum(len(o.data.polygons) for o in objects if o.type=='MESH'),
        'inscriptions':len(labels),'removed_baseline_visuals':removed,
        'photo_reference':PHOTO,'oem_console_reference':OEM,'external_image_dependencies':[],
        'layout_reference':LAYOUT_REFERENCE,
        'prototype_datums_m':{'cab_partition_x':partition_x,'driver_seat_center_x':driver_x,
            'main_fascia_x':fascia_x,'horizontal_control_plane_x':fascia_x-.211,
            'floor_z':floor_z,'seat_cushion_top_z':1.75,
            'windshield_lower_center':[windshield_lower_x,0,2.30],
            'windshield_upper_center':[windshield_upper_x,0,3.22],
            'blind_roller_center':[8.45+nose_dx-.070,0,3.195]},
        'ergonomic_scale':[1.,1.,1.],
        'preserved':['all context empties and their transforms','BODY parenting',
            'base-owned DRIVER_001/002 and CAB_EYE_CAMERA_REFERENCE',
            'prototype cab floor','prototype partitions','exterior/glass/lights/wipers'],
        'approximations':['24 m coach pitch is primary-dimension based; cab partition and body stations are drawing-read approximations',
            'Seat centers, fascia and eye point are coordinated ergonomic fits, not factory-dimension claims',
            'Per-unit instrument implementation, gauge settings, labels, buttons and display pages are representative original artwork',
            'Controls, seating suspension and auxiliary fittings are static visual geometry, not a functioning cab',
            'Cushion top 1.75 m retained; seated character animation fit remains unverified'],
        'cameras':{'overview':{'location':[partition_x+.52,0,2.89],'target':[fascia_x+.28,0,2.03],'lens_mm':19},
                   'entrance':{'location':[partition_x+.24,-.88,2.72],'target':[fascia_x+.12,.15,2.16],'lens_mm':21},
                   'driver_eye':{'location':[driver_x+.04,-.73,2.49],'target':[windshield_lower_x+.45,-.40,2.42],'lens_mm':20},
                   'instruments':{'location':[driver_x+.11,-.18,2.68],'target':[fascia_x+.03,0,2.16],'lens_mm':28},
                   'seat_detail':{'location':[fascia_x+.16,-1.02,2.82],'target':[driver_x-.03,.18,1.97],'lens_mm':22},
                   'rear_wall':{'location':[driver_x+.35,.02,2.69],'target':[partition_x+.07,0,2.45],'lens_mm':22},
                   'floor_pedals':{'location':[driver_x+.20,-.73,1.98],'target':[fascia_x-.20,-.73,1.38],'lens_mm':26},
                   'ceiling':{'location':[driver_x+.37,0,2.42],'target':[partition_x+.95,0,3.60],'lens_mm':23}}}
