"""Isolated CC furniture checks. Runs a disposable build; never edits live models.
Usage: LHB_CC_TEST_DIR=/workspace/shared/lhb-cc-test blender -b -t 2 --python scripts/test_lhb_chair_detail.py
The target directory must contain copies of current .py build modules.
"""
import os,sys,json,math,hashlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
P=Path(os.environ.get('LHB_CC_TEST_DIR','/workspace/shared/lhb-cc-test'))
sys.path.insert(0,str(P))
src=(P/'build_lhb_detail.py').read_text()
g={'__file__':str(P/'build_lhb_detail.py'),'__name__':'lhb_chair_test_build'}
exec(compile(src.split('\nargs=sys.argv')[0],str(P/'build_lhb_detail.py'),'exec'),g)
for name in ('models','qa','previews','docs'):(P/name).mkdir(exist_ok=True)
import lhb_chair_detail as cc
k='CC';c=g['CFG'][k]
print('CC_TEST_BUILD_START',flush=True)
g['common'](k,c);g['chair'](k,c)
print('CC_TEST_CORE_COMPLETE',flush=True)
bpy.context.view_layer.update()
before={o.name:(tuple(o.location),o.parent.name if o.parent else None) for o in g['pax']}
cc.refine_core(g,k,c)
import lhb_finish_detail
lhb_finish_detail.refine(g,k,c)
cc.refine_finish(g,k,c)
import lhb_soft_finish
lhb_soft_finish.apply(g,k,c)
import lhb_identity_detail
lhb_identity_detail.apply(g,k,c)
bpy.context.view_layer.update()
print('CC_TEST_FINISH_COMPLETE',flush=True)
checks=[]
def check(name,passed,details=None):
    checks.append({'name':name,'passed':bool(passed),'details':details})
def obs(prefix):return [o for o in bpy.data.objects if o.name.startswith(prefix)]
def bounds(o):
    points=[o.matrix_world@v.co for v in o.data.vertices]
    return [(min(p[i] for p in points),max(p[i] for p in points)) for i in range(3)]
check('78 PAX preserved, names/parents/XY unchanged',len(g['pax'])==78 and all(o.name in before and tuple(o.location)[:2]==before[o.name][0][:2] and o.parent.name==before[o.name][1] for o in g['pax']))
check('CC TOP 1.753 and PAX root 1.270',abs(g['TOP']-1.753)<1e-8 and all(abs(o.location.z-1.270)<1e-6 and abs(o['cushion_top_z_m']-1.753)<1e-6 for o in g['pax']))
check('78 level closed cushions at 450 mm floor height',len(obs('CHAIR_cushion_'))==78 and all(abs(bounds(o)[2][1]-1.753)<1e-6 and abs(o.rotation_euler.x)+abs(o.rotation_euler.y)<1e-8 for o in obs('CHAIR_cushion_')))
check('78 upright backrests are 17 degrees',len(obs('CHAIR_back_'))==78 and all(abs(abs(o.rotation_euler.y)-math.radians(17))<1e-6 for o in obs('CHAIR_back_')))
arm_errors=[]
for seat in g['_cc_detail_seats']:
    sid=seat['id'];arms=[o for o in obs('CHAIR_armrest_'+sid) if o.name in ('CHAIR_armrest_'+sid,'CHAIR_armrest_'+sid+'.001') or o.name.split('.')[0]=='CHAIR_armrest_'+sid]
    spans=sorted(bounds(o)[1] for o in arms)
    if len(spans)!=2 or abs(spans[1][0]-spans[0][1]-.420)>1e-6:arm_errors.append((sid,spans))
check('420 mm actual clear armrest gap',not arm_errors,arm_errors)
check('pedestals still grounded',all(abs(bounds(o)[2][0]-g['FLOOR'])<1e-6 for o in obs('CHAIR_pedestal_')))
check('old curtains and rod racks absent',not obs(('CURTAIN_','WINDOW_pleated_curtain','LUGGAGE_RACK_')))
check('32 actual thick glass rack panels',len(obs('CC_RACK_tempered_glass'))==32 and all(abs(bounds(o)[2][1]-bounds(o)[2][0]-.008)<1e-6 for o in obs('CC_RACK_tempered_glass')))
check('78 reading lamps, magazine nets, bottle holders, footrests',all(len(obs(prefix))==78 for prefix in ('CC_RACK_reading_lamp_lens_','CC_MAGAZINE_net_','CC_TABLE_bottle_holder_','CC_FOOTREST_tread_')))
check('78 thin draped antimacassars and sewn hems',len(obs('HEADREST_'))==78 and len(obs('CC_ANTIMACASSAR_sewn_hem_'))==78 and all(abs(o.get('textile_thickness_m',0)-.0012)<1e-8 for o in obs('HEADREST_')))
check('156 bottle-cage connecting brackets',len(obs('CC_BOTTLE_mount_bracket_'))==156)
check('all three roller blind states represented',set(o['manual_state'] for o in obs('CC_BLIND_roller_housing'))=={'full_open','half_open','full_closed'} and len(obs('CC_BLIND_roller_housing'))==30)
# Validate both original meshes and modifier results of every affected component.
errors=[];count=0;minimum=1e9
deps=bpy.context.evaluated_depsgraph_get()
prefixes=('CC_','CHAIR_','HEADREST_','SEATBACK_','ARM_support_','UPHOLSTERY_edge_piping_soft','UPHOLSTERY_back_seam_soft')
for ob in bpy.data.objects:
    if ob.type!='MESH' or not ob.name.startswith(prefixes):continue
    for evaluated in (False,True):
        ev=ob.evaluated_get(deps) if evaluated else ob
        data=ev.to_mesh() if evaluated else ob.data
        bm=bmesh.new();bm.from_mesh(data)
        volume=bm.calc_volume(signed=True)
        # Do not impose a volume threshold on very fine but valid fabric/wire.
        if not bm.faces or any(not e.is_manifold for e in bm.edges) or volume<=0:
            errors.append({'name':ob.name,'evaluated':evaluated,'volume':volume,'non_manifold':sum(not e.is_manifold for e in bm.edges)})
        if volume>0:minimum=min(minimum,volume)
        bm.free()
        if evaluated:ev.to_mesh_clear()
    count+=1
check('all CC component base/evaluated meshes manifold and positive-volume',not errors,{'objects':count,'minimum_positive_volume_m3':minimum,'errors':errors})
# Non-CC hooks must not even change the current scene or the datum global.
count_before=len(bpy.data.objects);top_before=g['TOP'];ids_before={o.name for o in bpy.data.objects}
cc.refine_core(g,'2S',g['CFG']['2S']);cc.refine_finish(g,'2S',g['CFG']['2S'])
check('2S hooks are exact no-ops',count_before==len(bpy.data.objects) and ids_before=={o.name for o in bpy.data.objects} and g['TOP']==top_before)
# Re-entry must not duplicate geometry or lower the chair a second time.
cc.refine_core(g,k,c);cc.refine_finish(g,k,c)
check('both CC hooks are idempotent',len(bpy.data.objects)==count_before and all(abs(o.location.z-1.270)<1e-6 for o in g['pax']))
report={'status':'pass' if all(x['passed'] for x in checks) else 'fail','module_sha256':hashlib.sha256((P/'lhb_chair_detail.py').read_bytes()).hexdigest(),'source_module_sha256':g['SOURCE_HASHES'],'checks':checks}
(P/'qa/cc_furnishing_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
assert report['status']=='pass'
g['finish'](k,c)
print('CC_TEST_COMPLETE',flush=True)
