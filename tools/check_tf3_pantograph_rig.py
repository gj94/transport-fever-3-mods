"""Check the extended mechanical envelope before exporting it to the game."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from pantograph_rig import configure_tf3_pantographs,MIN_HEIGHT,MAX_HEIGHT
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'pantograph_v04/WAP7_pantograph_v04.blend'))
configure_tf3_pantographs(bpy)

def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [(min(v[i] for v in p),max(v[i] for v in p)) for i in range(3)]

def tree(o):
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False,epsilon=1e-7)

moving=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('PANTO_')]
obstacles=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o in moving:continue
    bb=bounds(o)
    if bb[2][1]>3.85 and bb[2][0]<5 and bb[0][0]<7 and bb[0][1]>-7:
        obstacles.append((o,bb,tree(o)))
collisions=[];max_tilt=0.;max_height_error=0.
poses=[(i/100,i/100) for i in range(101)]+[(0,1),(1,0)]
for front,rear in poses:
    for end,extension in [('FRONT',front),('REAR',rear)]:
        ctrl=bpy.data.objects['PANTO_'+end+'_CTRL'];ctrl['extension']=extension;ctrl.update_tag()
    bpy.context.view_layer.update()
    for end,extension in [('FRONT',front),('REAR',rear)]:
        lo,up,he=[bpy.data.objects['PANTO_'+end+'_'+s] for s in ('LOWER_PIVOT','ELBOW_PIVOT','HEAD_LEVEL_PIVOT')]
        assert abs((up.matrix_world.translation-lo.matrix_world.translation).length-1.4)<1e-5
        assert abs((he.matrix_world.translation-up.matrix_world.translation).length-1.05)<1e-5
        max_tilt=max(max_tilt,max(abs(math.degrees(v)) for v in he.matrix_world.to_euler()))
        top=max((bpy.data.objects['PANTO_'+end+'_CONTACT_STRIP_1'].matrix_world@v.co).z for v in bpy.data.objects['PANTO_'+end+'_CONTACT_STRIP_1'].data.vertices)
        expected=4.212+2.45*math.sin(math.radians(1+44*extension))
        max_height_error=max(max_height_error,abs(top-expected))
    for o in moving:
        bb=bounds(o)
        candidates=[(p,b,t) for p,b,t in obstacles if all(bb[i][0]<=b[i][1] and b[i][0]<=bb[i][1] for i in range(3))]
        if not candidates:continue
        t=tree(o)
        for p,b,pt in candidates:
            if 'BASE_BEARING' in o.name and p.name.startswith('Pantograph base'):continue
            if t.overlap(pt):collisions.append((front,rear,o.name,p.name))
assert max_tilt<.0001 and max_height_error<1e-5 and not collisions,(max_tilt,max_height_error,collisions)
report={'poses':len(poses),'contact_height_range_m':[MIN_HEIGHT,MAX_HEIGHT],'max_head_tilt_deg':max_tilt,'max_contact_height_error_m':max_height_error,'roof_intersections':collisions,'standard_wire_height_above_rail_m':5.917,'standard_wire_extension':(math.degrees(math.asin((5.917-4.212)/2.45))-1)/44}
(ROOT/'game_build'/'pantograph_validation.json').write_text(json.dumps(report,indent=2))
print('TF3_PANTOGRAPH_QA',json.dumps(report))
