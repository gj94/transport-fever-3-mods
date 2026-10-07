"""Read-only source and portable-FBX QA for LHB detail masters (Blender 4.3+).

Run from this directory:
  blender -b -t 1 --python scripts/verify_lhb_detail.py -- --classes 3A
  blender -b -t 1 --python scripts/verify_lhb_detail.py -- --classes 1A 2A 3A 2S CC SL GS --fbx

This verifies geometry, not merely manifest declarations. No scene is saved and
no render is used. JSON/Markdown reports are the only written files. Closed mesh
components are required after modifiers, but intersections between independently
fabricated parts are not classified by a generic watertightness test. Source
crown excludes rooftop fittings; nominal tread diameter excludes wheel flanges.
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

BASE = Path(__file__).resolve().parent.parent
CAPACITY = {'1A':24,'2A':52,'3A':72,'2S':102,'CC':78,'SL':80,'GS':100}
SLEEPING = {'1A','2A','3A','SL'}
CODE = dict(zip(CAPACITY,['LWFAC','LWACCW','LWACCN','LWSCZ1','LWSCZAC','LWSCN1','LS1']))
TOL = 0.00005
SUPPORT_PREFIXES = ('FIRST_LOWER','MAIN_LOWER','SIDE_LOWER','CHAIR_cushion','GS_main_bench','GS_side_bench')
TOP_CONTRACTS = {'body_length_m':23.540,'body_width_m':3.240,'roof_height_m':4.039,'floor_height_m':1.303,'bogie_centres_m':14.900,'bogie_wheelbase_m':2.560,'wheel_tread_diameter_m':.915,'coupling_span_m':24.0}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def vec(v):return [round(float(x),8) for x in v]


def bbox(o, deps=None):
    obj = o.evaluated_get(deps) if deps else o
    if obj.type in {'FONT','CURVE','SURFACE'}:
        me=obj.to_mesh();ps=[obj.matrix_world@v.co for v in me.vertices];obj.to_mesh_clear()
    else:ps = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return ([min(p[i] for p in ps) for i in range(3)], [max(p[i] for p in ps) for i in range(3)])


def joined_bounds(bounds):
    if not bounds:return None
    lo=[min(b[0][i] for b in bounds) for i in range(3)]
    hi=[max(b[1][i] for b in bounds) for i in range(3)]
    return {'min_m':vec(lo),'max_m':vec(hi),'size_m':vec([hi[i]-lo[i] for i in range(3)])}


def center(b):return [(b[0][i]+b[1][i])/2 for i in range(3)]


def near(a,b,tol=TOL):return abs(float(a)-float(b))<=tol


def angular_distance(a,b):return abs((a-b+math.pi)%(2*math.pi)-math.pi)


def belongs(o,root):
    while o:
        if o==root:return True
        o=o.parent
    return False


def check(report, name, ok, details=None, severity='error'):
    row={'name':name,'status':'pass' if ok else severity}
    if details is not None:row['details']=details
    report['checks'].append(row)
    return ok


def issue_names(rows,limit=80):
    return {'count':len(rows),'examples':rows[:limit], 'truncated':len(rows)>limit}


def measure_scene(k,stage,reference=None,full_topology=True):
    start=time.time();scene=bpy.context.scene;scene.view_layers[0].update()
    deps=bpy.context.evaluated_depsgraph_get()
    objs=list(scene.objects)
    root=bpy.data.objects.get('LHB_'+k+'_ROOT_metres')
    r={'variant':k,'stage':stage,'checks':[],'assumptions_and_limits':[
        'Source geometry is representative authoring geometry, not manufacturer CAD or dimensional certification.',
        'Physical passenger/berth markers are not gameplay capacity or native TF3 runtime validation.',
        'PAX support uses actual cushion footprints and hip datum; full posed-character collisions, reach, comfort and egress are unverified.',
        'Topology is checked per evaluated component. Solid intersections, self-intersections, normals across separate parts and render appearance are not fully verified.',
        'Nominal .915 m tread diameter is checked at the actual nominal tread ring; flange envelope is intentionally larger.',
        '4.039 m crown is the roof skin; seams and non-AC ventilation hoods may protrude above it. Wheel flanges extend below railhead; CBC/handrails extend beyond the nominal body envelope.',
        'Editable-font cap seams use coincident vertices; text closure is checked after a disposable 0.1 micrometre weld.',
        'Procedural source materials are not expected to round-trip through FBX; exported alpha fallback is checked instead.'
    ]}
    check(r,'asset_root_present',root is not None)
    if root is None:return r,{}
    asset=[o for o in objs if belongs(o,root)]
    visual=[o for o in asset if o.type in {'MESH','FONT','CURVE','SURFACE'}]
    meshobjs=[o for o in visual if o.type=='MESH']
    bbs={o.name:bbox(o,deps) for o in visual}
    r['embedded_source_module_sha256']=json.loads(root.get('source_module_sha256','{}'))
    current_hashes={name:digest(BASE/name) for name in ['build_lhb_detail.py','lhb_shell.py','lhb_finish_detail.py','lhb_running_gear.py','lhb_identity_detail.py','lhb_hvac_detail.py','lhb_soft_finish.py','lhb_chair_detail.py'] if (BASE/name).exists()}
    check(r,'embedded_build_hashes_match_current_modules',r['embedded_source_module_sha256']==current_hashes,{'embedded':r['embedded_source_module_sha256'],'current':current_hashes})
    r['statistics']={'scene_objects':len(objs),'asset_objects':len(asset),'asset_mesh_objects':len(meshobjs),'asset_font_objects':sum(o.type=='FONT' for o in asset),'asset_empty_objects':sum(o.type=='EMPTY' for o in asset),'materials':len(bpy.data.materials)}
    r['bounds']=joined_bounds(list(bbs.values()))
    r['envelope_extremes']={axis:{'min':min(bbs,key=lambda n:bbs[n][0][i]),'max':max(bbs,key=lambda n:bbs[n][1][i])} for i,axis in enumerate('XYZ')}
    finitebad=[o.name for o in asset if any(not math.isfinite(x) for row in o.matrix_world for x in row)]
    check(r,'finite_transforms',not finitebad,issue_names(finitebad))
    check(r,'root_identity',all(near(root.matrix_world[i][j],1 if i==j else 0) for i in range(4) for j in range(4)),[vec(x) for x in root.matrix_world])
    body=bpy.data.objects.get('BODY_PIVOT')
    check(r,'body_parent_and_identity',body is not None and body.parent==root and all(near(body.matrix_world[i][j],1 if i==j else 0) for i in range(4) for j in range(4)))
    orphan=[o.name for o in objs if o.type in {'MESH','FONT','CURVE'} and not belongs(o,root)]
    check(r,'all_geometry_owned_by_asset_root',not orphan,issue_names(orphan))
    bad_scene=[o.name for o in asset if o.type in {'LIGHT','CAMERA'}]
    check(r,'presentation_excluded_from_asset_hierarchy',not bad_scene,issue_names(bad_scene))
    check(r,'scene_units_metres',near(scene.unit_settings.scale_length,1),{'unit_system':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length})
    check(r,'root_capacity_metadata',root.get('physical_capacity')==CAPACITY[k] and root.get('variant')==k and root.get('prototype_code')==CODE[k])
    check(r,'native_runtime_claims_false',root.get('native_TF3_conversion') in [False,0] and root.get('runtime_tested') in [False,0])
    extremes=r['bounds']; envelope_bad=[]
    for name,b in bbs.items():
        if b[0][0]<-12.35 or b[1][0]>12.35 or b[0][1]<-1.82 or b[1][1]>1.82 or b[0][2]<-.06 or b[1][2]>4.25:envelope_bad.append({'object':name,'bounds_m':[vec(x) for x in b]})
    check(r,'whole_asset_reasonable_envelope',not envelope_bad,issue_names(envelope_bad))
    def dimensions(name):
        b=bbs.get(name)
        return [b[1][i]-b[0][i] for i in range(3)] if b else None
    measurements={}
    for name,axis,expected,label,mode in [('UNDERFRAME_main',0,23.54,'body_length_m','size'),('ROOF_arch',1,3.24,'body_width_m','size'),('ROOF_arch',2,4.039,'roof_height_m','max'),('INTERIOR_floor',2,1.303,'floor_height_m','max')]:
        value=(dimensions(name)[axis] if mode=='size' else bbs[name][1][axis]) if name in bbs else None
        measurements[label]=value;check(r,'dimension_'+label,value is not None and near(value,expected),{'expected_m':expected,'actual_m':value,'object':name})
    bogies=[o for o in asset if re.fullmatch(r'BOGIE_(FRONT|REAR)_PIVOT',o.name)]
    axles=[o for o in asset if re.fullmatch(r'AXLE_(FRONT|REAR)_[AB]_PIVOT',o.name)]
    couplers=[o for o in asset if o.name in ['COUPLING_FRONT','COUPLING_REAR']]
    wheels=[o for o in asset if re.fullmatch(r'WHEEL_(FRONT|REAR)_[AB]_[LR]_profiled_monobloc',o.name)]
    discs=[o for o in asset if re.fullmatch(r'BRAKE_DISC_(FRONT|REAR)_[AB]_[12]_ROTATING',o.name)]
    check(r,'two_bogies_four_axles_eight_wheels_eight_discs',len(bogies)==2 and len(axles)==4 and len(wheels)==8 and len(discs)==8,{'bogies':len(bogies),'axles':len(axles),'wheels':len(wheels),'brake_discs':len(discs)})
    measurements['bogie_centres_m']=abs(bogies[0].matrix_world.translation.x-bogies[1].matrix_world.translation.x) if len(bogies)==2 else None
    check(r,'dimension_bogie_centres',measurements['bogie_centres_m'] is not None and near(measurements['bogie_centres_m'],14.9),measurements['bogie_centres_m'])
    gearerrors=[];discmeasure=[];wheelmeasure=[]
    for bo in bogies:
        aa=[a for a in axles if a.parent==bo]
        if bo.parent!=root or len(aa)!=2 or not near(abs(aa[0].matrix_world.translation.x-aa[1].matrix_world.translation.x),2.56):gearerrors.append(bo.name+' hierarchy/wheelbase')
    for a in axles:
        if not near(a.matrix_world.translation.z,.4575):gearerrors.append(a.name+' axle height')
        if len([o for o in wheels if o.parent==a])!=2 or len([o for o in discs if o.parent==a])!=2:gearerrors.append(a.name+' wheel/disc ownership')
    for o in wheels:
        a=o.parent;inv=a.matrix_world.inverted();vs=[inv@(o.matrix_world@v.co) for v in o.data.vertices]
        # Ring at |Y|=.838 carries radius .4570 on the structural wheel, while
        # separate machined band at the same ring carries nominal .4575 radius.
        rings=[math.hypot(v.x,v.z) for v in vs if abs(abs(v.y)-.838)<TOL]
        band=[q for q in asset if q.parent==a and q.name.startswith('WHEEL_'+a.name[5:-6]+'_bright_flange_and_tread')]
        rr=[]
        for q in band:
            for v in q.data.vertices:
                p=inv@(q.matrix_world@v.co)
                if abs(abs(p.y)-.838)<TOL:rr.append(math.hypot(p.x,p.z))
        dia=2*max(rr) if rr else None
        wheelmeasure.append({'object':o.name,'nominal_tread_diameter_m':dia,'flange_diameter_m':2*max(math.hypot(v.x,v.z) for v in vs),'back_face_abs_y_m':min(abs(v.y) for v in vs)})
        if dia is None or not near(dia,.915) or not near(min(abs(v.y) for v in vs),.800):gearerrors.append(o.name+' tread/back-to-back')
    for d in discs:
        cheek=[q for q in d.children if '_friction_cheek' in q.name]
        pts=[d.matrix_world.inverted()@(q.matrix_world@v.co) for q in cheek for v in q.data.vertices]
        dia=2*max((math.hypot(p.x,p.z) for p in pts),default=0);width=max((p.y for p in pts),default=0)-min((p.y for p in pts),default=0)
        discmeasure.append({'object':d.name,'cheeks':len(cheek),'diameter_m':dia,'width_m':width})
        if len(cheek)!=2 or not near(dia,.640) or not near(width,.110):gearerrors.append(d.name+' disc dimensions')
    check(r,'running_gear_geometry_and_parenting',not gearerrors,issue_names(gearerrors));r['wheel_measurements']=wheelmeasure;r['brake_disc_measurements']=discmeasure
    measurements['coupling_span_m']=abs(couplers[0].matrix_world.translation.x-couplers[1].matrix_world.translation.x) if len(couplers)==2 else None
    check(r,'coupling_anchor_contract',len(couplers)==2 and near(measurements['coupling_span_m'],24) and all(o.parent==root and near(o.matrix_world.translation.z,1.105) and near(o.matrix_world.translation.y,0) and angular_distance(o.rotation_euler.z,0 if o.name.endswith('FRONT') else math.pi)<TOL for o in couplers),{'span_m':measurements['coupling_span_m'],'anchors':{o.name:vec(o.matrix_world.translation) for o in couplers}})
    r['measured_dimensions']=measurements
    # Revision-specific design placement checks. These are measured authoring
    # contracts, not claims that the chosen fine layout is manufacturer CAD.
    door_pivots=[o for o in asset if re.fullmatch(r'DOOR_[LR]_[123]_PIVOT',o.name)]
    header_errors=[];header_rows=[]
    for dp in door_pivots:
        x=dp.matrix_world.translation.x+.48;y=dp.matrix_world.translation.y
        candidates=[o for o in visual if o.name.startswith('DOOR_portal_header') and abs(center(bbs[o.name])[0]-x)<.001 and center(bbs[o.name])[1]*y>0]
        if len(candidates)!=1:header_errors.append(dp.name+' header count');continue
        b=bbs[candidates[0].name]
        header_rows.append({'door':dp.name,'header':candidates[0].name,'bounds_m':[vec(v) for v in b]})
        if not near(b[0][0],x-.52) or not near(b[1][0],x+.52) or not near(b[0][2],3.415) or not near(b[1][2],3.580):header_errors.append(dp.name+' bridging bounds')
    check(r,'door_portal_headers_bridge_to_roof',len(door_pivots)==(6 if k=='GS' else 4) and not header_errors,{'doors':len(door_pivots),'errors':header_errors,'headers':header_rows})
    packages=[o for o in meshobjs if o.name.startswith('AC_ROOF_end_package')]
    hvac_errors=[];hvac_rows=[];component_errors=[];component_rows=[];platform_errors=[];platform_rows=[];clearance_errors=[];clearances=[]
    arch=bpy.data.objects.get('ROOF_arch');arch_inv=arch.matrix_world.inverted() if arch else None;arch_eval=arch.evaluated_get(deps) if arch else None
    def ray_down(obj,x,y):
        inv=obj.matrix_world.inverted();hit,loc,normal,_=obj.evaluated_get(deps).ray_cast(inv@Vector((x,y,4.20)),(inv.to_3x3()@Vector((0,0,-1))).normalized(),distance=1.0)
        return (obj.matrix_world@loc).z if hit else None
    for package in packages:
        pb=bbs[package.name];sgn=1 if center(pb)[0]>0 else -1
        if not near(pb[1][2],3.950):hvac_errors.append(package.name+' cover top')
        if not near(package.get('fan_bank_y_m',999),-.50*sgn) or not near(package.get('condenser_well_floor_z_m',999),3.8075) or not near(package.get('cover_top_z_m',999),3.950) or package.get('maintenance_cover_count')!=6:component_errors.append(package.name+' design metadata')
        wells=[('fan',sgn*x,-.50*sgn) for x in [9.30,10.17]]+[('intake',sgn*(9.08+j*.43),.62*sgn) for j in range(4)]
        for kind,x,y in wells:
            offsets=[(0,0),(.20,0),(0,.20)] if kind=='fan' else [(0,0),(.12,0),(0,.24)]
            for dx,dy in offsets:
                z=ray_down(package,x+dx,y+dy);roof_z=ray_down(arch,x+dx,y+dy) if arch else None
                hvac_rows.append({'package':package.name,'well_type':kind,'sample_xy_m':[x+dx,y+dy],'first_cover_hit_z_m':z,'depth_m':pb[1][2]-z if z is not None else None})
                if z is None or not near(z,3.8075,.0002) or not near(pb[1][2]-z,.1425,.0002):hvac_errors.append(package.name+' '+kind+' well floor/depth')
                clearance=z-roof_z if z is not None and roof_z is not None else None
                clearances.append({'package':package.name,'well_type':kind,'sample_xy_m':[x+dx,y+dy],'roof_top_z_m':roof_z,'well_floor_z_m':z,'clearance_m':clearance})
                if clearance is None or clearance<.1023:clearance_errors.append(package.name+' roof intersects or approaches well floor')
        blades=[o for o in visual if o.name.startswith('AC_fan_blade') and bbs[o.name][0][0]>pb[0][0] and bbs[o.name][1][0]<pb[1][0]]
        fan_counts={x:0 for x in [sgn*9.30,sgn*10.17]}
        for o in blades:
            bc=center(bbs[o.name]);fx=min(fan_counts,key=lambda x:abs(x-bc[0]));fan_counts[fx]+=1
            if bbs[o.name][1][2]>3.945 or bbs[o.name][0][2]<3.82 or math.hypot(bc[0]-fx,bc[1]+sgn*.50)>.375:hvac_errors.append(o.name+' fan recess/bank placement')
        if len(blades)!=12 or sorted(fan_counts.values())!=[6,6]:hvac_errors.append(package.name+' blade count')
        def nearby(prefix):return [o for o in visual if o.name.startswith(prefix) and pb[0][0]-.02<=center(bbs[o.name])[0]<=pb[1][0]+.02]
        frames=nearby('RMPU_intake_frame');wires=nearby('RMPU_intake_mesh_wire');fins=nearby('RMPU_condenser_fin');boxes=nearby('RMPU_electrical_junction_box');shadows=nearby('RMPU_condenser_intake_shadow');seams=nearby('RMPU_maintenance_cover_joint')
        if len(frames)!=16 or len(wires)!=160 or len(fins)!=64 or len(boxes)!=2 or len(shadows)!=4 or len(seams)!=3:component_errors.append(package.name+' intake/junction/cover component counts')
        for j in range(4):
            xx=sgn*(9.08+j*.43);yy=sgn*.62
            cellframes=[o for o in frames if abs(center(bbs[o.name])[0]-xx)<=.1971 and abs(center(bbs[o.name])[1]-yy)<=.3441]
            cellfins=[o for o in fins if abs(center(bbs[o.name])[0]-xx)<=.18 and abs(center(bbs[o.name])[1]-yy)<TOL]
            if len(cellframes)!=4 or len(cellfins)!=16:component_errors.append(package.name+' intake '+str(j)+' frames/fins')
            if any(bbs[o.name][0][2]<3.8075 or bbs[o.name][1][2]>=3.950 for o in cellfins):component_errors.append(package.name+' fin recess')
        if len(boxes)==2 and any(not near(abs(center(bbs[o.name])[1]),1.285) or not near(center(bbs[o.name])[0],sgn*10.86) for o in boxes):component_errors.append(package.name+' junction box placement')
        component_rows.append({'package':package.name,'fan_blades':len(blades),'blade_counts_per_well':fan_counts,'intake_frames':len(frames),'mesh_wires':len(wires),'fins':len(fins),'junction_boxes':len(boxes),'intake_shadow_floors':len(shadows),'cover_seams':len(seams),'maintenance_cover_metadata':package.get('maintenance_cover_count')})
        for x in [sgn*8.56,sgn*9.82,sgn*11.08]:
            for y in [-1.270,-1.250,-1.20,0,1.20,1.250,1.270]:
                z=ray_down(arch,x,y) if arch else None
                platform_rows.append({'sample_xy_m':[x,y],'roof_top_z_m':z})
                if z is None or not near(z,3.705,.0002):platform_errors.append({'sample_xy_m':[x,y],'expected_z_m':3.705,'actual_z_m':z})
    check(r,'HVAC_blind_wells_and_fans_recessed',len(packages)==(2 if k in {'1A','2A','3A','CC'} else 0) and not hvac_errors,{'packages':len(packages),'errors':hvac_errors,'ray_samples':hvac_rows})
    check(r,'RMPU_intakes_covers_and_paired_junction_boxes',not component_errors,{'errors':component_errors,'unit_measurements':component_rows})
    check(r,'RMPU_roof_platform_flat_to_1_27m_halfwidth',not platform_errors,{'errors':platform_errors,'sample_measurements':platform_rows})
    check(r,'RMPU_well_floors_clear_roof_platform',not clearance_errors,{'errors':clearance_errors,'clearance_measurements':clearances})
    ceiling=bbs.get('CEILING_main');ceiling_top=ceiling[1][2] if ceiling else None
    check(r,'RMPU_roof_and_ceiling_vertically_separate',not packages or ceiling_top is not None and ceiling_top<3.655 and ceiling_top<3.8075,{'ceiling_top_z_m':ceiling_top,'flat_roof_bottom_z_m':3.655,'well_floor_z_m':3.8075,'ceiling_to_roof_gap_m':3.655-ceiling_top if ceiling_top is not None else None})
    check(r,'temporary_boolean_cutters_removed',not any(o.name.startswith('TEMP_') for o in objs))
    slope=(3.46-2.08)/(11.77-10.60);livery_errors=[];livery_faces=0;livery_objects=[]
    for o in meshobjs:
        if not o.name.startswith(('BODYSIDE_header','BODYSIDE_rounded_aperture','BODYSIDE_window_pier')):continue
        b=bbs[o.name]
        if not (b[0][0]>10.58 or b[1][0]<-10.58):continue
        livery_objects.append(o.name)
        for face in o.data.polygons:
            pts=[o.matrix_world@o.data.vertices[i].co for i in face.vertices]
            deltas=[p.z-2.08-slope*(abs(p.x)-10.60) for p in pts]
            centre_delta=sum(deltas)/len(deltas)
            mat=o.data.materials[face.material_index] if face.material_index<len(o.data.materials) else None
            expected='Lower_body_light_grey' if centre_delta<.00001 else 'Class_livery'
            if min(deltas)<-.00001 and max(deltas)>.00001:livery_errors.append(o.name+' face crosses uncut wedge line')
            if not mat or not (mat.name.startswith(expected) or mat.name.startswith('Warm_FRP_liners') and abs(face.normal.y)<.05):livery_errors.append(o.name+' wrong material side')
            livery_faces+=1
    check(r,'end_livery_wedges_match_world_space_plane',len(livery_objects)>0 and not livery_errors,{'objects':livery_objects,'faces_checked':livery_faces,'errors':livery_errors[:30]})
    pax=sorted([o for o in asset if o.name.startswith('PAX_')],key=lambda x:x.name)
    berths=sorted([o for o in asset if o.name.startswith('BERTH_') and o.type=='EMPTY'],key=lambda x:x.name)
    check(r,'PAX_count',len(pax)==CAPACITY[k],{'expected':CAPACITY[k],'actual':len(pax)})
    check(r,'BERTH_count',len(berths)==(CAPACITY[k] if k in SLEEPING else 0),{'expected':CAPACITY[k] if k in SLEEPING else 0,'actual':len(berths)})
    check(r,'marker_root_metadata_consistent',root.get('seated_character_root_count')==len(pax) and root.get('berth_reference_count')==len(berths))
    supports=[o for o in visual if o.name.startswith(SUPPORT_PREFIXES)]
    support_rows=[];paxbad=[];duplicate=collections.defaultdict(list);blockages=[]
    partitions=[o for o in visual if o.name.startswith(('BAY_partition','SIDE_partition','CABIN_partition','CABIN_corridor_wall','SALOON_end_partition','SALOON_partition_transom','WC_','VESTIBULE_cabinet'))]
    for p in pax:
        pos=p.matrix_world.translation;cushion=float(p.get('cushion_top_z_m',1.84));hip=float(p.get('posed_hip_offset_m',.483))
        duplicate[tuple(round(v,5) for v in pos)].append(p.name)
        if p.type!='EMPTY' or p.parent!=body or p.get('pose')!='sitting' or not near(pos.z,cushion-hip) or not near(pos.z,1.270 if k=='CC' else 1.357) or angular_distance(p.rotation_euler.z,0)>TOL and angular_distance(p.rotation_euler.z,math.pi)>TOL:paxbad.append(p.name+' transform/pose')
        if abs(pos.x)>9.15 or abs(pos.y)>1.52:paxbad.append(p.name+' saloon bounds')
        candidates=[]
        for s in supports:
            b=bbs[s.name]
            if b[0][0]-.005<=pos.x<=b[1][0]+.005 and b[0][1]-.005<=pos.y<=b[1][1]+.005 and abs(b[1][2]-cushion)<.012:candidates.append(s.name)
        if len(candidates)!=1:paxbad.append(p.name+' cushion support count='+str(len(candidates)))
        support_rows.append({'marker':p.name,'world_m':vec(pos),'yaw_radians':round(p.rotation_euler.z,8),'cushion_supports':candidates})
        # Mid-torso point is .34 m above cushion, shifted 8 cm forward. Test
        # only permanent hard partitions, not upholstery or folded backrests.
        sample=Vector((pos.x+.08*math.cos(p.rotation_euler.z),pos.y+.08*math.sin(p.rotation_euler.z),cushion+.34))
        for o in partitions:
            b=bbs[o.name]
            if all(b[0][i]-.005<=sample[i]<=b[1][i]+.005 for i in range(3)):blockages.append({'marker':p.name,'obstacle':o.name,'sample_m':vec(sample)})
    duplicate=[v for v in duplicate.values() if len(v)>1]
    check(r,'PAX_seated_pose_and_single_lower_cushion_support',not paxbad,issue_names(paxbad))
    check(r,'PAX_unique_positions',not duplicate,issue_names(duplicate))
    check(r,'PAX_torso_clear_of_fixed_partitions',not blockages,issue_names(blockages))
    r['PAX_supports']=support_rows
    # Compare independent design-contract coordinates against evaluated geometry.
    # Matching is tolerance-based rather than lexicographic to tolerate FBX noise.
    def match_points(actual,expected,tolerance=TOL):
        unused=list(range(len(actual)));missing=[];pairs=[]
        for point in expected:
            if not unused:missing.append(vec(point));continue
            best=min(unused,key=lambda j:sum((actual[j][i]-point[i])**2 for i in range(len(point))))
            delta=max(abs(actual[best][i]-point[i]) for i in range(len(point)))
            if delta<=tolerance:unused.remove(best);pairs.append((best,point))
            else:missing.append(vec(point))
        return missing,unused,pairs
    fan_motors=[o for o in visual if re.fullmatch(r'FAN_motor(?:\.\d+)?',o.name)]
    if k=='SL':fan_expected=[(-8.1+j*1.8,y,3.355) for j in range(10) for y in [-1.08,-.42,.24]]
    elif k=='GS':fan_expected=[(half*(1.34+j*1.67),-half*y,3.355) for half in [-1,1] for j in range(5) for y in [-1.08,-.42,.24]]
    elif k=='2S':fan_expected=[(x,y,3.355) for x in [-7.5,-5.6,-3.7,-1.8,.1,2.0,3.9,5.8,7.7] for y in [-.55,.78]]
    else:fan_expected=[]
    fan_actual=[center(bbs[o.name]) for o in fan_motors];missing,extra,_=match_points(fan_actual,fan_expected)
    check(r,'ceiling_fan_count_and_class_positions',len(fan_motors)==len(fan_expected) and root.get('ceiling_fan_count')==len(fan_expected) and not missing and not extra,{'expected_count':len(fan_expected),'actual_count':len(fan_motors),'metadata_count':root.get('ceiling_fan_count'),'missing_positions':missing,'unexpected_objects':[fan_motors[i].name for i in extra],'actual_positions_m':{o.name:vec(fan_actual[i]) for i,o in enumerate(fan_motors)}})
    if k=='1A':
        steps=[o for o in visual if o.name.startswith('FIRST_upper_access_step')]
        stiles=[o for o in visual if o.name.startswith('FIRST_access_ladder_stile')]
        ladder_errors=[];ladder_rows=[]
        for step in steps:
            sb=bbs[step.name];sc=center(sb);touching=[]
            for stile in stiles:
                rb=bbs[stile.name]
                # The straight round stiles lean only in X. Interpolate the
                # centreline from their bounds at the tread's middle height.
                if not rb[0][2]<sc[2]<rb[1][2]:continue
                pts=[stile.matrix_world@v.co for v in stile.data.vertices]
                low=sorted(pts,key=lambda p:p.z)[:len(pts)//2]
                high=sorted(pts,key=lambda p:p.z)[len(pts)//2:]
                a=sum(low,Vector())/len(low);b=sum(high,Vector())/len(high)
                q=a+(b-a)*((sc[2]-a.z)/(b.z-a.z))
                if sb[0][0]-.005<=q.x<=sb[1][0]+.005 and sb[0][1]-.005<=q.y<=sb[1][1]+.005:touching.append(stile.name)
            if len(touching)!=2:ladder_errors.append(step.name)
            ladder_rows.append({'step':step.name,'attached_stiles':touching})
        check(r,'FIRST_ladder_treads_join_both_stiles',len(steps)==48 and len(stiles)==24 and not ladder_errors,{'step_count':len(steps),'stile_count':len(stiles),'errors':ladder_errors,'joints':ladder_rows})
        partitions=[o for o in visual if o.name.startswith(('CABIN_partition_','CABIN_end_partition'))]
        fittings=[o for o in visual if o.name.startswith(('CABIN_coat_hook_base','CABIN_magazine_frame'))]
        fixture_errors=[]
        for fitting in fittings:
            fb=bbs[fitting.name]
            contacts=[p.name for p in partitions if all(fb[0][a]<=bbs[p.name][1][a]+TOL and fb[1][a]>=bbs[p.name][0][a]-TOL for a in range(3))]
            if not contacts:fixture_errors.append(fitting.name)
        check(r,'FIRST_hooks_and_net_frames_attach_to_partitions',len(fittings)==108 and not fixture_errors,{'fitting_count':len(fittings),'errors':fixture_errors})

    if k=='GS':
        exp_pax=[];exp_benches=[];exp_side=[]
        for half in [-1,1]:
            for j in range(5):
                cx=half*(1.34+j*1.67);mirror=-half;exp_side.append((cx,1.24*mirror,1.776))
                for end in [-1,1]:
                    xx=cx+end*.54;exp_benches.append((xx,-.54*mirror,1.776))
                    for yy in [-1.26,-.78,-.30,.18]:exp_pax.append(((xx-end*.045,yy*mirror,1.357),0 if end<0 else math.pi))
                    exp_pax.append(((cx+end*.43,1.24*mirror,1.357),0 if end<0 else math.pi))
        missing,extra,pairs=match_points([list(o.matrix_world.translation) for o in pax],[p for p,yaw in exp_pax])
        bad_yaw=[]
        for index,point in pairs:
            expected_yaw=next(yaw for p,yaw in exp_pax if p==point)
            if angular_distance(pax[index].rotation_euler.z,expected_yaw)>TOL:bad_yaw.append(pax[index].name)
        benchobjs=[o for o in visual if o.name.startswith('GS_main_bench')];sideobjs=[o for o in visual if o.name.startswith('GS_side_bench')]
        bm,be,_=match_points([center(bbs[o.name]) for o in benchobjs],exp_benches)
        sm,se,_=match_points([center(bbs[o.name]) for o in sideobjs],exp_side)
        check(r,'GS_mirrored_furniture_and_PAX_banks',len(pax)==100 and len(benchobjs)==20 and len(sideobjs)==10 and not any([missing,extra,bad_yaw,bm,be,sm,se]),{'missing_PAX_positions':missing,'extra_PAX':[pax[i].name for i in extra],'wrong_X_facing_yaw':bad_yaw,'missing_main_benches':bm,'extra_main_benches':[benchobjs[i].name for i in be],'missing_side_benches':sm,'extra_side_benches':[sideobjs[i].name for i in se],'bank_contract':'Negative-X main bank at negative Y; positive-X main bank at positive Y; side bank mirrored; yaw unchanged by bank reflection'})
        rails=[o for o in visual if re.fullmatch(r'GS_TRANSVERSE_RACK_rail(?:\.\d+)?',o.name)]
        crosses=[o for o in visual if re.fullmatch(r'GS_TRANSVERSE_RACK_crossbar(?:\.\d+)?',o.name)]
        rackerrors=[];rackrows=[];claimed=set()
        for bx,by,bz in exp_benches:
            matches=[o for o in rails if abs(center(bbs[o.name])[0]-bx)<=.27005 and abs(center(bbs[o.name])[1]-by)<TOL and abs(center(bbs[o.name])[2]-2.96)<TOL]
            cmatches=[o for o in crosses if abs(center(bbs[o.name])[0]-bx)<TOL and abs(center(bbs[o.name])[1]-by)<=.96005 and abs(center(bbs[o.name])[2]-2.96)<TOL]
            spans=[bbs[o.name][1][1]-bbs[o.name][0][1] for o in matches]
            xms,xes,_=match_points([[center(bbs[o.name])[0]] for o in matches],[[bx-.27],[bx],[bx+.27]])
            if len(matches)!=3 or len(cmatches)!=15 or xms or xes or any(not near(span,1.92) for span in spans):rackerrors.append({'bench_center_m':[bx,by,bz],'rails':len(matches),'crossbars':len(cmatches),'Y_spans_m':spans})
            claimed.update(o.name for o in matches)
            rackrows.append({'bench_center_m':[bx,by,bz],'rails':[o.name for o in matches],'rail_Y_spans_m':spans,'crossbars':len(cmatches)})
        check(r,'GS_twenty_transverse_luggage_racks',len(rails)==60 and len(crosses)==300 and len(claimed)==60 and not rackerrors,{'assemblies':len(rackrows),'rails':len(rails),'crossbars':len(crosses),'errors':rackerrors,'assembly_measurements':rackrows})
    supports_bad=[];floor_supports=[]
    for o in visual:
        if not o.name.startswith(('LOWER_support','FIRST_berth_support','CHAIR_pedestal','GS_bench_leg')):continue
        b=bbs[o.name];bottom=b[0][2];top=b[1][2];floor_gap=bottom-1.303
        # Authored leg ends may meet the underside of the metal berth pan,
        # rather than the cushion itself; allow its 50 mm thickness/offset.
        supported=[q.name for q in supports if bbs[q.name][0][0]-.02<=center(b)[0]<=bbs[q.name][1][0]+.02 and bbs[q.name][0][1]-.02<=center(b)[1]<=bbs[q.name][1][1]+.02 and -.045<=bbs[q.name][0][2]-top<=.055]
        floor_supports.append({'object':o.name,'floor_gap_m':round(floor_gap,8),'supported_cushions':supported})
        if not -.005<=floor_gap<=.02 or not supported:supports_bad.append(o.name)
    check(r,'furniture_legs_meet_floor_and_lower_seat_structure',bool(floor_supports) and not supports_bad,issue_names(supports_bad))
    r['furniture_floor_supports']=floor_supports
    berthbad=[];types=collections.Counter();berthrow=[]
    for p in berths:
        pos=p.matrix_world.translation;typ=p.get('berth_type');types[typ]+=1
        if p.parent!=body or abs(pos.x)>9.15 or abs(pos.y)>1.52 or not 1.80<=pos.z<=3.30:berthbad.append(p.name+' transform/bounds')
        if typ=='MIDDLE_STOWED_REFERENCE':
            matches=[o.name for o in visual if o.name.startswith('MIDDLE_FOLDED_') and abs(center(bbs[o.name])[0]-pos.x)<.30 and abs(center(bbs[o.name])[1]-pos.y)<.01]
        else:
            matches=[o.name for o in visual if o.name.startswith(('FIRST_LOWER','FIRST_UPPER','MAIN_LOWER','MAIN_UPPER','SIDE_LOWER','SIDE_UPPER')) and bbs[o.name][0][0]-.01<=pos.x<=bbs[o.name][1][0]+.01 and bbs[o.name][0][1]-.01<=pos.y<=bbs[o.name][1][1]+.01 and abs(bbs[o.name][1][2]-pos.z)<.012]
        if len(matches)!=1:berthbad.append(p.name+' berth geometry count='+str(len(matches)))
        berthrow.append({'marker':p.name,'type':typ,'geometry':matches,'world_m':vec(pos)})
    check(r,'BERTH_references_match_lower_upper_or_stowed_geometry',not berthbad,issue_names(berthbad));r['BERTH_type_counts']=dict(types);r['BERTH_supports']=berthrow
    expected_types={'1A':{'LOWER':12,'UPPER':12},'2A':{'LOWER':17,'UPPER':17,'SIDE_LOWER':9,'SIDE_UPPER':9},'3A':{'LOWER':18,'UPPER':18,'MIDDLE_STOWED_REFERENCE':18,'SIDE_LOWER':9,'SIDE_UPPER':9},'SL':{'LOWER':20,'UPPER':20,'MIDDLE_STOWED_REFERENCE':20,'SIDE_LOWER':10,'SIDE_UPPER':10}}.get(k,{})
    check(r,'BERTH_class_type_distribution',dict(types)==expected_types,{'expected':expected_types,'actual':dict(types)})
    fixturebad=[];fixturemeasure=[]
    for o in visual:
        if not o.name.startswith(('WC_pedestal','WC_squat_bowl','VESTIBULE_washbasin')):continue
        b=bbs[o.name];ce=center(b);wc=o.name.startswith('WC_')
        expectedx=11.13 if wc else 10.95;expectedy=1.06 if wc else .36
        fixturemeasure.append({'object':o.name,'bounds_m':[vec(x) for x in b],'center_m':vec(ce)})
        if abs(abs(ce[0])-expectedx)>.002 or abs((abs(ce[1]) if wc else ce[1])-expectedy)>.002 or abs(b[0][0])>11.70 or abs(b[1][0])>11.70:fixturebad.append(o.name)
    check(r,'lavatory_and_basin_actual_placement',not fixturebad,issue_names(fixturebad));r['fixture_measurements']=fixturemeasure
    wcactual=sum(o.name.startswith(('WC_pedestal','WC_squat_bowl')) for o in visual)
    check(r,'lavatory_count',wcactual==(3 if k=='1A' else 4),{'expected':3 if k=='1A' else 4,'actual':wcactual})
    if k in {'1A','2A','3A','CC'}:
        outer=[o for o in meshobjs if o.name.startswith('GLASS_WINDOW') and not o.name.startswith('GLASS_WINDOW_inner_tempered')]
        inner=[o for o in meshobjs if o.name.startswith('GLASS_WINDOW_inner_tempered')]
        pane_errors=[];pane_pairs=[]
        for o in outer:
            a=bbs[o.name];ac=center(a)
            found=[q for q in inner if near(center(bbs[q.name])[0],ac[0]) and near(center(bbs[q.name])[2],ac[2]) and center(bbs[q.name])[1]*ac[1]>0]
            if len(found)!=1:pane_errors.append(o.name+' has '+str(len(found))+' inner panes');continue
            q=found[0];b=bbs[q.name];bc=center(b)
            ot=a[1][1]-a[0][1];it=b[1][1]-b[0][1];gap=abs(ac[1]-bc[1])-(ot+it)/2
            if not near(ot,.0084) or not near(it,.004) or not near(gap,.006):pane_errors.append(o.name+' wrong unit construction')
            pane_pairs.append({'outer':o.name,'inner':q.name,'outer_m':ot,'inner_m':it,'air_gap_m':gap})
        check(r,'sealed_window_8p4mm_outer_4mm_inner_6mm_gap',len(outer)==len(inner)>0 and not pane_errors,{'units':len(pane_pairs),'errors':pane_errors[:20]})
        r['sealed_window_pairs']=pane_pairs
    # Rays cast against actual rounded wall mesh must pass through the central aperture.
    apertures=[o for o in meshobjs if o.name.startswith('BODYSIDE_rounded_aperture')];aperturebad=[]
    for o in apertures:
        b=bbs[o.name];ce=center(b);origin=Vector((ce[0],ce[1]-.20,2.495));dest=Vector((0,1,0));inv=o.matrix_world.inverted()
        hit=o.evaluated_get(deps).ray_cast(inv@origin,(inv.to_3x3()@dest).normalized(),distance=.4)[0]
        if hit:aperturebad.append(o.name)
    check(r,'rounded_window_centres_are_actual_through_apertures',bool(apertures) and not aperturebad,{'apertures_checked':len(apertures),'blocked':aperturebad})
    glass=[o for o in visual if o.name.startswith('GLASS_')];glassmat=bpy.data.materials.get('GLASS_source_transmission_FBX_alpha')
    check(r,'separate_glazing_geometry_exists',bool(glass),{'objects':len(glass)})
    wc_glazing=[o for o in visual if o.name.startswith('GLASS_WC_frosted')]
    privacy_errors=[]
    for o in wc_glazing:
        mat=o.data.materials[0] if o.data.materials else None
        bs=mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
        if not mat or not mat.name.startswith('WC_privacy_frosted_glass') or not bs or not near(bs.inputs['Alpha'].default_value,1) or bs.inputs['Roughness'].default_value<.35:privacy_errors.append(o.name)
        if stage=='source' and bs and not near(bs.inputs['Transmission Weight'].default_value,.75):privacy_errors.append(o.name+' transmission')
    check(r,'WC_glazing_keeps_distinct_privacy_material',len(wc_glazing)==4 and not privacy_errors,{'count':len(wc_glazing),'errors':privacy_errors})
    if glassmat and glassmat.use_nodes:
        bs=glassmat.node_tree.nodes.get('Principled BSDF')
        alpha=bs.inputs['Alpha'].default_value if bs else None;trans=bs.inputs['Transmission Weight'].default_value if bs else None
        check(r,'source_glass_transmission' if stage=='source' else 'fbx_glass_alpha_fallback',bs is not None and (near(trans,.96) and near(alpha,1) if stage=='source' else near(alpha,.22,1e-4)),{'alpha':alpha,'transmission':trans})
    else:check(r,'glass_material_present',False)
    nonunit=[o.name for o in asset if any(not near(abs(s),1) for s in o.scale)]
    mirrored=[o.name for o in asset if o.matrix_world.to_3x3().determinant()<0]
    check(r,'no_negative_scale',not mirrored,issue_names(mirrored))
    r['non_unit_scale_objects']=nonunit
    if full_topology:
        tstats=collections.Counter();issues=[];source_open=[];evaluated_open=[];invalid=[];badnormals=[];textissues=[]
        for index,o in enumerate(visual):
            eo=o.evaluated_get(deps);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me)
            is_text=o.type=='FONT' or bool(reference and reference['objects'].get(o.name,{}).get('type')=='FONT')
            if is_text:
                # Blender's standard editable-font tessellation duplicates vertices
                # at cap seams. Verify geometric closure after a submicron weld
                # in the disposable BMesh; never mutate source or export meshes.
                seam_count=sum(e.is_boundary for e in bm.edges)
                bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
                tstats['text_objects_checked']+=1;tstats['text_seam_edges_before_weld']+=seam_count
            vv=len(bm.verts);ee=len(bm.edges);ff=len(bm.faces);tstats['vertices']+=vv;tstats['edges']+=ee;tstats['polygons']+=ff;tstats['triangles']+=sum(len(f.verts)-2 for f in bm.faces)
            boundary=sum(e.is_boundary for e in bm.edges);wire=sum(e.is_wire for e in bm.edges);nonman=sum(not e.is_manifold for e in bm.edges);zeroedge=sum(e.calc_length()<1e-8 for e in bm.edges);zeroarea=sum(f.calc_area()<1e-12 for f in bm.faces);nonfinite=sum(any(not math.isfinite(x) for x in v.co) for v in bm.verts);inconsistent=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);isolated=sum(not v.link_edges for v in bm.verts);signed_volume=bm.calc_volume(signed=True) if not nonman and ff else None
            if not is_text and signed_volume is not None:
                tstats['closed_fabricated_components_checked']+=1
            if nonman or wire or zeroedge or zeroarea or nonfinite or inconsistent or isolated or not ff or (not is_text and signed_volume is not None and signed_volume<=1e-15):
                row={'object':o.name,'category':'editable_text_tessellation' if is_text else 'fabricated_geometry','boundary_edges':boundary,'nonmanifold_edges':nonman,'wire_edges':wire,'zero_length_edges':zeroedge,'zero_area_faces':zeroarea,'nonfinite_vertices':nonfinite,'inconsistent_winding_edges':inconsistent,'faces':ff,'isolated_vertices':isolated,'signed_volume_m3_local':signed_volume}
                issues.append(row)
                if is_text:
                    textissues.append(row)
                    if nonfinite or not ff:invalid.append(o.name)
                else:
                    if nonman:evaluated_open.append(o.name)
                    if zeroedge or zeroarea or nonfinite or isolated or not ff or (signed_volume is not None and signed_volume<=1e-15):invalid.append(o.name)
                    if inconsistent:badnormals.append(o.name)
            if o.modifiers and any(m.type=='SOLIDIFY' for m in o.modifiers):source_open.append(o.name)
            bm.free();eo.to_mesh_clear()
        r['topology']={'evaluated_totals':dict(tstats),'issues':issues,'intentional_source_sheets_closed_by_solidify':source_open}
        check(r,'editable_text_tessellation_clean',not textissues,issue_names(textissues),severity='warning')
        check(r,'evaluated_fabricated_meshes_closed_manifold',not evaluated_open,issue_names(evaluated_open))
        check(r,'fabricated_mesh_no_degenerate_or_nonfinite_geometry',not invalid,issue_names(invalid))
        check(r,'fabricated_mesh_consistent_winding',not badnormals,issue_names(badnormals))
    else:r['topology']={'status':'not_run'}
    # No external photo/image/path dependencies expected in these procedural assets.
    images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath]
    libraries=[l.filepath for l in bpy.data.libraries]
    check(r,'no_external_image_or_linked_library_dependencies',not images and not libraries,{'image_paths':images,'libraries':libraries})
    snapshot={'objects':{o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'world_matrix':[vec(row) for row in o.matrix_world],'bounds_m':[vec(v) for v in bbs[o.name]] if o.name in bbs else None} for o in asset},'pax':{o.name:{'position':vec(o.matrix_world.translation),'yaw':float(o.rotation_euler.z)} for o in pax},'berths':{o.name:{'position':vec(o.matrix_world.translation)} for o in berths},'bounds':r['bounds']}
    if reference:
        missing=sorted(set(reference['objects'])-set(snapshot['objects']));extra=sorted(set(snapshot['objects'])-set(reference['objects']));changes=[]
        for name,a in reference['objects'].items():
            b=snapshot['objects'].get(name)
            if not b:continue
            # Font becomes a baked FBX mesh; that conversion is expected.
            if a['parent']!=b['parent']:changes.append({'object':name,'change':'parent','source':a['parent'],'fbx':b['parent']})
            if a['bounds_m'] and b['bounds_m']:
                delta=max(abs(a['bounds_m'][j][i]-b['bounds_m'][j][i]) for j in range(2) for i in range(3))
                if delta>.0002:changes.append({'object':name,'change':'bounds','max_delta_m':delta})
            elif a['type']=='EMPTY':
                delta=max(abs(a['world_matrix'][i][j]-b['world_matrix'][i][j]) for i in range(4) for j in range(4))
                if delta>.0002:changes.append({'object':name,'change':'empty_transform','max_delta':delta})
        check(r,'fbx_preserves_asset_names_and_membership',not missing and not extra,{'missing':missing,'unexpected':extra})
        check(r,'fbx_preserves_geometry_bounds_and_hierarchy',not changes,issue_names(changes))
        check(r,'fbx_excludes_all_presentation_objects',not any(o.type in {'CAMERA','LIGHT'} for o in objs))
        r['source_comparison']={'missing':missing,'unexpected':extra,'changed':changes}
    r['elapsed_seconds']=round(time.time()-start,2)
    r['status']='fail' if any(x['status']=='error' for x in r['checks']) else ('pass_with_warnings' if any(x['status']=='warning' for x in r['checks']) else 'pass')
    return r,snapshot


def verify(k,args):
    path=BASE/'models'/('LHB_'+k+'.blend')
    report={'variant':k,'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blender_version':bpy.app.version_string,'source_file':str(path),'checks':[]}
    if not path.exists():report['status']='missing';return report
    source_hash=digest(path);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    report['source'],snapshot=measure_scene(k,'source',full_topology=not args.skip_topology)
    report['sha256']={'blend':source_hash}
    manifestpath=path.with_name('LHB_'+k+'_manifest.json');markerpath=path.with_name('LHB_'+k+'_markers.json')
    if manifestpath.exists():
        manifest=json.loads(manifestpath.read_text());report['manifest']=manifest
        errs=[key for key,val in TOP_CONTRACTS.items() if key not in manifest or not near(manifest[key],val)]
        if manifest.get('physical_capacity')!=CAPACITY[k] or manifest.get('PAX_roots')!=CAPACITY[k] or manifest.get('BERTH_references')!=(CAPACITY[k] if k in SLEEPING else 0):errs.append('capacity')
        check(report,'manifest_declared_contract',not errs,errs)
        check(report,'manifest_build_hashes_match_source',manifest.get('source_module_sha256')==report['source'].get('embedded_source_module_sha256'))
        report['sha256']['manifest']=digest(manifestpath)
    else:check(report,'manifest_present',False)
    if markerpath.exists():
        data=json.loads(markerpath.read_text());mismatches=[]
        check(report,'marker_build_hashes_match_source',data.get('source_module_sha256')==report['source'].get('embedded_source_module_sha256'))
        for array,key in [('PAX_character_roots','pax'),('BERTH_sleeping_references','berths')]:
            rows=data.get(array,[]);expected=snapshot.get(key,{})
            if set(row['name'] for row in rows)!=set(expected):mismatches.append(array+' name set')
            for row in rows:
                name=row['name'];v=expected.get(name)
                if not v:continue
                if max(abs(row['position_parent_m'][i]-v['position'][i]) for i in range(3))>TOL:mismatches.append(name+' position')
                if key=='pax' and (row.get('parent')!='BODY_PIVOT' or row.get('pose')!='sitting' or angular_distance(row.get('yaw_radians',999),v['yaw'])>TOL):mismatches.append(name+' pose/yaw/parent')
                if key=='berths' and row.get('use_as_seated_passenger') is not False:mismatches.append(name+' seated exclusion')
        check(report,'marker_manifest_matches_actual_source',not mismatches,issue_names(mismatches));report['sha256']['markers']=digest(markerpath)
    else:check(report,'marker_manifest_present',False)
    fbxpath=path.with_suffix('.fbx')
    check(report,'fbx_file_present_and_nonempty',fbxpath.exists() and fbxpath.stat().st_size>1000,{'bytes':fbxpath.stat().st_size if fbxpath.exists() else None})
    if fbxpath.exists():report['sha256']['fbx']=digest(fbxpath)
    if args.fbx and fbxpath.exists():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(fbxpath),use_custom_props=True)
        report['fbx'],_=measure_scene(k,'fbx',reference=snapshot,full_topology=not args.skip_topology)
    else:report['fbx']={'status':'not_run','reason':'Use --fbx to import and compare the portable export.'}
    # A concurrent rebuild must never silently validate different file generations.
    unchanged=digest(path)==source_hash
    for label,fp in [('manifest',manifestpath),('markers',markerpath),('fbx',fbxpath)]:
        if label in report['sha256'] and (not fp.exists() or digest(fp)!=report['sha256'][label]):unchanged=False
    check(report,'input_files_unchanged_during_verification',unchanged)
    report['status']='fail' if report['source']['status']=='fail' or report['fbx']['status']=='fail' or any(c['status']=='error' for c in report['checks']) else ('pass_with_warnings' if any(report[stage]['status']=='pass_with_warnings' for stage in ['source','fbx']) else 'pass')
    return report


def write_summary(reports,path):
    lines=['# LHB detail source-geometry verification','', 'Read-only Blender inspection; no render or native TF3 conversion was performed.','']
    for r in reports:
        lines += ['## '+r['variant']+' — '+r['status'].upper(),'']
        for stage in ['source','fbx']:
            s=r.get(stage,{})
            lines.append('- '+stage+': '+s.get('status','not run'))
            for c in s.get('checks',[]):
                if c['status']!='pass':lines.append('  - '+c['status'].upper()+': '+c['name']+' — '+json.dumps(c.get('details',''))[:900])
        for c in r.get('checks',[]):
            if c['status']!='pass':lines.append('- '+c['status'].upper()+': '+c['name'])
        if 'source' in r:
            lines += ['- Source bounds (metres): '+json.dumps(r['source'].get('bounds')), '- Source mesh totals: '+json.dumps(r['source'].get('topology',{}).get('evaluated_totals',{}))]
        lines.append('')
    lines += ['## Limits','',*['- '+x for x in next((r['source']['assumptions_and_limits'] for r in reports if 'source' in r),[])],'','JSON reports contain the full checks, measured dimensions, source hashes, marker-to-furniture matches, fixture positions and export comparison.']
    path.write_text('\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--classes',nargs='+',choices=list(CAPACITY),default=list(CAPACITY));parser.add_argument('--fbx',action='store_true');parser.add_argument('--skip-topology',action='store_true');parser.add_argument('--output',default=str(BASE/'qa'/'source_geometry'));args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    reports=[json.loads(p.read_text()) for p in out.glob('LHB_*_geometry.json') if json.loads(p.read_text()).get('variant') not in args.classes]
    for k in args.classes:
        print('VERIFY_START',k,flush=True)
        try:r=verify(k,args)
        except Exception as e:
            import traceback
            r={'variant':k,'status':'verifier_error','error':str(e),'traceback':traceback.format_exc()}
            print(r['traceback'],flush=True)
        reports.append(r);reports.sort(key=lambda x:list(CAPACITY).index(x['variant']));(out/('LHB_'+k+'_geometry.json')).write_text(json.dumps(r,indent=2,allow_nan=False));write_summary(reports,out/'SUMMARY.md')
        print('VERIFY_RESULT',k,r['status'],flush=True)
        for stage in ['source','fbx']:
            for c in r.get(stage,{}).get('checks',[]):
                if c['status']!='pass':print('VERIFY_ISSUE',k,stage,c['name'],json.dumps(c.get('details',''))[:400],flush=True)
    (out/'aggregate.json').write_text(json.dumps({'status':('pass_with_warnings' if any(r['status']=='pass_with_warnings' for r in reports) else 'pass') if all(r['status'] in ['pass','pass_with_warnings'] for r in reports) else 'fail','classes':{r['variant']:r['status'] for r in reports},'fbx_roundtrip_requested':args.fbx,'topology_requested':not args.skip_topology},indent=2))
    print('VERIFY_REPORTS',out,flush=True)

if __name__=='__main__':main()
