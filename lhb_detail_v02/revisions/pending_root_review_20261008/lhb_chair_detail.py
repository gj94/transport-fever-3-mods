"""Source-led conventional 78-seat LHB AC chair-car furniture.

Hooks: refine_core immediately after chair(); refine_finish after finish-detail.
Both are no-ops outside CC. CAMTECH LHB manual, chapter 1, sections 1.6,
1.7 and 1.9 (PDF pages 34–35), is the evidence for the component inventory,
450 mm cushion height, 420 mm clear armrests and 17-degree upright recline.
Original, representative fabrication; the manual is not manufacturer seat CAD.
"""
import math
import bpy
from mathutils import Vector

SOURCE_URL = 'https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf'
SEAT_HEIGHT = .450
ARM_CLEAR = .420
UPRIGHT_ANGLE = math.radians(17)


def _remove(prefixes, objects=None):
    for ob in list(objects if objects is not None else bpy.data.objects):
        if ob.name.startswith(prefixes):
            bpy.data.objects.remove(ob, do_unlink=True)


def _local_bounds(ob):
    return [(min(v.co[i] for v in ob.data.vertices),
             max(v.co[i] for v in ob.data.vertices)) for i in range(3)]


def _set_size(ob, dims):
    """Resize mesh data, preserving names, parent, scale and modifier contracts."""
    bounds = _local_bounds(ob)
    for v in ob.data.vertices:
        for i, (lo, hi) in enumerate(bounds):
            v.co[i] = (v.co[i] - (lo + hi)/2) * dims[i] / (hi - lo)
    ob.data.update()
    for mod in ob.modifiers:
        if mod.type == 'BEVEL':
            mod.width = min(mod.width, .45*min(dims))


def refine_core(g, k, c):
    if k != 'CC':
        return
    if g['root'].get('CC_core_refined'):
        return
    g['TOP'] = g['FLOOR'] + SEAT_HEIGHT
    top = g['TOP']
    objects = {o.name: o for o in g['inter'].objects}
    seats = []
    for cushion in sorted((o for o in objects.values()
                           if o.name.startswith('CHAIR_cushion_')), key=lambda o: o.name):
        sid = cushion.name[len('CHAIR_cushion_'):]
        marker = bpy.data.objects['PAX_' + sid]
        face = 1 if math.cos(marker.rotation_euler.z) > 0 else -1
        x, y = cushion.location.x, cushion.location.y
        cushion.location.z = top - .06
        cushion['seat_height_above_floor_m'] = SEAT_HEIGHT
        marker.location.z = top - g['HIP']
        marker['cushion_top_z_m'] = top
        back = objects['CHAIR_back_' + sid]
        back.rotation_euler.y = -face * UPRIGHT_ANGLE
        pivot_z = top - .020
        back.location = (x-face*(.225 + .325*math.sin(UPRIGHT_ANGLE)),
                         y, pivot_z + .325*math.cos(UPRIGHT_ANGLE))
        back['upright_recline_degrees'] = 17.0
        back['full_rest_recline_degrees_reference'] = 37.0
        back['reference'] = 'CAMTECH section 1.9; shown in upright position'
        head = objects['HEADREST_' + sid]
        # Head pad follows the same backrest plane, rather than floating upright.
        head.rotation_euler.y = back.rotation_euler.y
        head.location = back.location + back.rotation_euler.to_matrix() @ Vector((face*.018, 0, .265))
        tray = objects['SEATBACK_tray_' + sid]
        tray.rotation_euler.y = back.rotation_euler.y
        tray.location = back.location + back.rotation_euler.to_matrix() @ Vector((-face*.084, 0, -.012))
        tray['state'] = 'folded_stowed'
        tray['feature'] = 'Foldable table; associated wire bottle holder below'
        pedestal = objects['CHAIR_pedestal_' + sid]
        support_top = top-.122
        _set_size(pedestal, (.09, .10, support_top-g['FLOOR']))
        pedestal.location.z = (support_top+g['FLOOR'])/2
        for ob in objects.values():
            if ob.name == 'CHAIR_armrest_'+sid or ob.name.startswith('CHAIR_armrest_'+sid+'.'):
                sign = 1 if ob.location.y > y else -1
                ob.location.y = y + sign*(ARM_CLEAR+.035)/2
                ob.location.z = top+.160
                ob['clear_between_armrests_m'] = ARM_CLEAR
            elif ob.name == 'ARM_support_'+sid or ob.name.startswith('ARM_support_'+sid+'.'):
                # Rod helper stores global coordinates in mesh data, unlike boxes.
                coords = [v.co.copy() for v in ob.data.vertices]
                cy = sum(v.y for v in coords)/len(coords)
                sign = 1 if cy > y else -1
                dy = y+sign*(ARM_CLEAR+.035)/2-cy
                dz = top-1.840
                for vertex in ob.data.vertices:
                    vertex.co.y += dy
                    vertex.co.z += dz
                ob.data.update()
        seats.append({'id':sid, 'x':x, 'y':y, 'face':face})
    # Capture the actual shell apertures; no independently guessed window pitch.
    bpy.context.view_layer.update()
    windows = []
    for rail in [o for o in g['inter'].objects if o.name.startswith('CURTAIN_rail')]:
        pts = [rail.matrix_world @ v.co for v in rail.data.vertices]
        windows.append({'x':(min(p.x for p in pts)+max(p.x for p in pts))/2,
                        'y':sum(p.y for p in pts)/len(pts),
                        'width':max(p.x for p in pts)-min(p.x for p in pts)})
    g['_cc_detail_seats'] = seats
    g['_cc_detail_windows'] = sorted(windows, key=lambda d:(d['y'], d['x']))
    # Removing curtain rails here prevents the shared finish from creating curtains.
    _remove(('CURTAIN_', 'WINDOW_pleated_curtain', 'LUGGAGE_RACK_'), g['inter'].objects)
    root = g['root']
    root['CC_core_refined'] = True
    root['CC_seat_height_above_floor_m'] = SEAT_HEIGHT
    root['CC_clear_between_armrests_m'] = ARM_CLEAR
    root['CC_upright_backrest_angle_deg'] = 17
    root['CC_furnishing_reference'] = SOURCE_URL+'#page=34'
    root['CC_furnishing_basis'] = 'CAMTECH chapter 1 sections 1.6, 1.7, 1.9; dimensions not stated there remain representative'
    bpy.context.view_layer.update()


def refine_finish(g, k, c):
    if k != 'CC':
        return
    root = g['root']
    if root.get('CC_finish_refined'):
        return
    if not root.get('CC_core_refined'):
        raise RuntimeError('CC refine_core must run immediately after chair(), before shared finish')
    box, mesh, rod, material = [g[n] for n in ['box','mesh','rod','material']]
    inter = g['inter']
    steel, rubber, ivory, glass, blue = [g[n] for n in ['steel','rubber','ivory','glass','blue']]
    aluminium = material('CC_anodised_aluminium', (.46,.50,.52), .72, .30)
    cast = material('CC_powder_coated_cast_cheeks', (.59,.62,.61), .28, .36)
    cloth = material('CC_sun_protection_blind', (.22,.36,.35), 0, .87)
    lens = material('CC_reading_lamp_diffuser', (.80,.77,.64), 0, .25)
    lp = lens.node_tree.nodes.get('Principled BSDF')
    lp.inputs['Emission Color'].default_value = (1,.88,.66,1)
    lp.inputs['Emission Strength'].default_value = .65
    switch = material('CC_lamp_switch', (.43,.31,.095), .08, .43)
    # Shared finish details assumed vertical seat backs. Replace them in the
    # proper reclined coordinate frame. Raised sewn patches exceeded seat datum.
    _remove(('SEAT_cushion_centre_sewn_panel','UPHOLSTERY_back_seam',
             'CHAIR_lumbar_bolster','CHAIR_recline_hinge','TRAY_latch',
             'TRAY_hinge','HEADREST_embroidery','CURTAIN_',
             'WINDOW_pleated_curtain','LUGGAGE_RACK_'), inter.objects)

    def B(name, loc, dims, mat, bevel=0):
        return box(name, loc, dims, mat, min(bevel,.45*min(dims)), coll=inter)

    def R(name, a, b, radius, mat=aluminium, segments=12):
        return rod(name, a, b, radius, mat, segments, coll=inter)

    def rods_mesh(name, segments, radius, mat, sides=8):
        """Closed tube pieces in one mesh: no zero-area caps/open textile edges."""
        verts, faces = [], []
        for start, end in segments:
            a,b = Vector(start),Vector(end)
            tangent = (b-a).normalized()
            u = tangent.cross(Vector((0,0,1)))
            if u.length < .01:
                u = tangent.cross(Vector((0,1,0)))
            u.normalize()
            v = tangent.cross(u)
            off = len(verts)
            for p in (a,b):
                verts.extend(tuple(p+radius*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))) for j in range(sides))
            faces += [tuple(off+j for j in range(sides-1,-1,-1)), tuple(off+sides+j for j in range(sides))]
            faces += [(off+j,off+(j+1)%sides,off+sides+(j+1)%sides,off+sides+j) for j in range(sides)]
        ob = mesh(name, verts, faces, mat, coll=inter)
        for p in ob.data.polygons:
            if len(p.vertices)==4:
                p.use_smooth=True
        return ob

    def extrusion(name, x0, x1, yz, mat):
        n=len(yz)
        verts=[(x,y,z) for x in (x0,x1) for y,z in yz]
        faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
        faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        return mesh(name,verts,faces,mat,coll=inter)

    # Closed folded/stowed table fittings, welded underframe and source-listed
    # magazine net / bottle cage / foot rest. No pose or capacity changes.
    for seat in g['_cc_detail_seats']:
        sid,x,y,f = [seat[n] for n in ['id','x','y','face']]
        back=bpy.data.objects['CHAIR_back_'+sid]
        mat=back.matrix_local.copy()
        def q(a,b,c):
            return tuple(mat @ Vector((f*a,b,c)))
        tray=bpy.data.objects['SEATBACK_tray_'+sid]
        # Latch and hinge axes are fixed to the tilted rear shell.
        latch=B('CC_TRAY_latch_'+sid,q(-.110,0,.115),(.016,.075,.022),steel,.006)
        latch.rotation_euler.y=back.rotation_euler.y
        for sy in (-1,1):
            R('CC_TRAY_hinge_'+sid,q(-.086,sy*.115,-.147),q(-.086,sy*.146,-.147),.010)
        # Two structural crossmembers and a side frame under the cushion.
        B('CC_CHAIR_welded_crossmember_'+sid,(x,y,g['TOP']-.126),(.34,.36,.026),steel,.008)
        for sy in (-1,1):
            R('CC_CHAIR_recline_hinge_'+sid,(x-f*.225,y+sy*.189,g['TOP']-.020),
              (x-f*.225,y+sy*.209,g['TOP']-.020),.027,steel,16)
        # Source photo: rectangular net below the stowed rear table.
        meshx=-.081; ylo,yhi=-.155,.155; zlo,zhi=-.312,-.166
        frame=[(q(meshx,ylo,zlo),q(meshx,yhi,zlo)),(q(meshx,yhi,zlo),q(meshx,yhi,zhi)),
               (q(meshx,yhi,zhi),q(meshx,ylo,zhi)),(q(meshx,ylo,zhi),q(meshx,ylo,zlo))]
        rods_mesh('CC_MAGAZINE_frame_'+sid,frame,.006,aluminium)
        # Clipped criss-cross cords form genuine open diamonds, not an opaque decal.
        cords=[]
        for sign in (-1,1):
            for i in range(12):
                start=ylo-.15+i*.044
                points=[]
                for z in (zlo+.008,zhi-.008):
                    yy=start+sign*(z-zlo)
                    if ylo+.008<=yy<=yhi-.008:
                        points.append((yy,z))
                for yy in (ylo+.008,yhi-.008):
                    z=zlo+(yy-start)/sign
                    if zlo+.008<z<zhi-.008:
                        points.append((yy,z))
                if len(points)==2 and (Vector(points[0])-Vector(points[1])).length>.003:
                    cords.append((q(meshx-.014,*points[0]),q(meshx-.014,*points[1])))
        rods_mesh('CC_MAGAZINE_net_'+sid,cords,.0017,rubber,6)
        # Associated bottle holder is visibly hollow, below the table and beside
        # the magazine net, as in the manual's rear-chair photograph.
        cx=x-f*.385; cy=y+.190; cz=g['TOP']+.012
        cage=[]
        for zz in (cz-.055,cz+.080):
            for j in range(16):
                a=j*math.tau/16;b=(j+1)*math.tau/16
                cage.append(((cx+.037*math.cos(a),cy+.037*math.sin(a),zz),
                             (cx+.037*math.cos(b),cy+.037*math.sin(b),zz)))
        for j in range(4):
            a=j*math.tau/4
            cage.append(((cx+.037*math.cos(a),cy+.037*math.sin(a),cz-.055),
                         (cx+.037*math.cos(a),cy+.037*math.sin(a),cz+.080)))
        cage.append(((cx-.037,cy,cz-.055),(cx+.037,cy,cz-.055)))
        rods_mesh('CC_TABLE_bottle_holder_'+sid,cage,.0027,aluminium,8)
        # Two small brackets connect the hollow cage to the tilted rear shell.
        # Their inner ends penetrate the shell rather than leaving a floating
        # accessory; dimensions remain representative fabrication details.
        for zz,local_z in [(cz+.080,-.250),(cz-.055,-.285)]:
            R('CC_BOTTLE_mount_bracket_'+sid,q(-.035,.170,local_z),
              (cx+f*.037,cy,zz),.006,aluminium,12)

        # Footrest projects behind its host seat for the passenger behind.
        footx=x-f*.49; footz=g['FLOOR']+.153
        for sy in (-1,1):
            R('CC_FOOTREST_arm_'+sid,(x-f*.21,y+sy*.143,g['TOP']-.167),
              (footx,y+sy*.143,footz),.010,steel)
        B('CC_FOOTREST_tread_'+sid,(footx,y,footz),(.14,.30,.028),rubber,.010)
        for j in range(4):
            B('CC_FOOTREST_rib_'+sid,(footx-.050+j*.033,y,footz+.016),(.009,.274,.006),rubber,.002)

    # Aluminium extrusions and closed 8 mm safety-glass panels. Rail cross-section
    # includes the broad light/wiring strip seen in the manual; no rod-shelf proxy.
    shelf_z=2.966
    for side in (-1,1):
        for rail_y,depth in ((.946,.112),(1.470,.045)):
            y0=rail_y-depth/2;y1=rail_y+depth/2
            profile=[(side*y0,2.918),(side*y1,2.918),(side*(y1+.008),2.940),
                     (side*y1,2.982),(side*y0,2.982),(side*(y0-.008),2.957)]
            extrusion('CC_RACK_extruded_rail',-8.82,8.82,profile,aluminium)
        for j in range(16):
            x=-8.25+j*1.10
            pane=box('CC_RACK_tempered_glass',(x,side*1.225,shelf_z),(1.064,.438,.008),glass,.0015,coll=g['glasscoll'])
            pane['material_specification']='Tempered safety glass; thickness is representative'
        for j in range(17):
            xx=-8.80+j*1.10
            # Closed ring extrusion gives cast cheek a real open triangular aperture.
            outer=[(1.49,2.942),(.924,2.942),(.905,3.002),(1.092,3.109),(1.415,3.214),(1.49,3.214)]
            inner=[(1.453,2.984),(1.021,2.984),(1.006,3.000),(1.142,3.069),(1.414,3.166),(1.453,3.166)]
            n=len(outer);verts=[]
            for dx in (-.012,.012):
                verts += [(xx+dx,side*y,z) for y,z in outer+inner]
            faces=[]
            for i in range(n):
                ni=(i+1)%n
                faces += [(i,ni,n+ni,n+i),(2*n+i,3*n+i,3*n+ni,2*n+ni),
                          (i,2*n+i,2*n+ni,ni),(n+i,n+ni,3*n+ni,3*n+i)]
            cheek=mesh('CC_RACK_cast_open_side_cheek',verts,faces,cast,coll=inter)
            cheek['reference']='CAMTECH section 1.7, powder-coated cast aluminium side cheeks'
            B('CC_RACK_wall_bracket',(xx,side*1.496,3.077),(.072,.024,.275),aluminium,.006)
        # A shallow polymer strip closes the wiring channel on its underside.
        B('CC_RACK_lexan_wiring_cover',(0,side*.949,2.916),(17.54,.070,.006),ivory,.002)
    # Each occupied row bank receives one lamp for every actual seat.
    rows={}
    for seat in g['_cc_detail_seats']:
        side=-1 if seat['y']<0 else 1
        rows.setdefault((round(seat['x'],4),side),[]).append(seat)
    for (x,side),seats in sorted(rows.items()):
        for j,seat in enumerate(seats):
            xx=x+(j-(len(seats)-1)/2)*.135
            R('CC_RACK_reading_lamp_bezel_'+seat['id'],(xx,side*.947,2.918),(xx,side*.947,2.897),.029,aluminium,24)
            lamp=R('CC_RACK_reading_lamp_lens_'+seat['id'],(xx,side*.947,2.897),(xx,side*.947,2.894),.022,lens,24)
            lamp['seat_id']=seat['id']
            R('CC_RACK_lamp_switch_'+seat['id'],(xx+.050,side*.947,2.916),(xx+.050,side*.947,2.901),.007,switch,16)
            R('CC_RACK_focus_adjustment_'+seat['id'],(xx-.046,side*.947,2.916),(xx-.046,side*.947,2.908),.003,rubber,10)
        hx=x+.32
        B('CC_RACK_coat_hook_slider',(hx,side*.902,2.932),(.042,.024,.027),aluminium,.006)
        rods_mesh('CC_RACK_movable_coat_hook',[
            ((hx,side*.901,2.925),(hx,side*.901,2.844)),
            ((hx,side*.901,2.844),(hx,side*.864,2.836)),
            ((hx,side*.864,2.836),(hx,side*.854,2.864))],.006,aluminium,10)

    # Manually controlled taut blinds. States are explicit discrete stops, not
    # guessed continuously draped curtains. Default shows all three manual states.
    # Caller may supply CC_BLIND_STATES keyed by sorted-window index or a global
    # CC_BLIND_STATE = full_open / half_open / full_closed before this hook.
    states={'full_open':0.0,'half_open':.5,'full_closed':1.0}
    realised={name:0 for name in states}
    for index,window in enumerate(g['_cc_detail_windows']):
        x,y,w=window['x'],window['y'],window['width']
        side=1 if y>0 else -1
        local_index=index%15
        default='full_closed' if local_index==11 else ('half_open' if local_index in (3,7,14) else 'full_open')
        state=g.get('CC_BLIND_STATES',{}).get(index,g.get('CC_BLIND_STATE',default))
        if state not in states:
            raise ValueError('Unsupported CC roller-blind state: '+str(state))
        realised[state]+=1
        head_z=2.895; bottom=head_z-states[state]*.783
        housing=B('CC_BLIND_roller_housing',(x,side*1.474,2.916),(w+.030,.055,.066),cast,.018)
        housing['manual_state']=state
        housing['supported_states']='full_open, half_open, full_closed'
        housing['control']='Manual wire-tensioned roller blind, CAMTECH section 1.6'
        for dx in (-w/2+.018,w/2-.018):
            R('CC_BLIND_tension_wire',(x+dx,side*1.457,2.902),(x+dx,side*1.457,2.113),.0012,steel,8)
            B('CC_BLIND_wire_anchor',(x+dx,side*1.469,2.111),(.014,.021,.018),aluminium,.003)
        # Full-open sheet remains wound in housing; avoid a degenerate zero-height face.
        if states[state]>0:
            sheet=B('CC_BLIND_sun_fabric',(x,side*1.461,(head_z+bottom)/2),(w-.053,.0018,head_z-bottom),cloth,.0005)
            sheet['manual_state']=state
            sheet['surface']='Taut sun-protection fabric; closed thin solid'
        bar=B('CC_BLIND_bottom_pull_rail',(x,side*1.457,bottom),(w-.035,.022,.021),aluminium,.006)
        bar['manual_state']=state
        B('CC_BLIND_manual_pull',(x,side*1.442,bottom-.004),(.066,.025,.016),cast,.004)
    root['CC_finish_refined']=True
    root['CC_manual_blind_state_counts']=str(realised)
    root['CC_individual_reading_lights']=len(g['_cc_detail_seats'])
    root['CC_rack_glass_panel_count']=32
    root['CC_furnishing_geometry']='Closed solids; representational hardware dimensions; no supplier-CAD claim'
    bpy.context.view_layer.update()
