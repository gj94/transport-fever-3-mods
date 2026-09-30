"""Adapt the source's illustrative 36-degree endpoint to TF3's wire height.

Only in-memory joint drivers change. Arm lengths and original source files stay
intact. The 45-degree endpoint reaches 5.944412 m; standard TF3 rail wire is
approximately 6.447 - 0.53 = 5.917 m above rail.
"""
import math

MIN_HEIGHT=4.212+2.45*math.sin(math.radians(1))
MAX_HEIGHT=4.212+2.45*math.sin(math.radians(45))

def configure_tf3_pantographs(bpy):
    original=str(math.radians(36)-math.radians(1))
    adapted=str(math.radians(45)-math.radians(1))
    for end in ('FRONT','REAR'):
        ctrl=bpy.data.objects['PANTO_'+end+'_CTRL']
        ctrl['raised_angle_deg']=45.
        for part in ('LOWER_PIVOT','ELBOW_PIVOT','HEAD_LEVEL_PIVOT'):
            ob=bpy.data.objects['PANTO_'+end+'_'+part]
            curve=next(d for d in ob.animation_data.drivers if d.data_path=='rotation_euler' and d.array_index==1)
            assert original in curve.driver.expression, curve.driver.expression
            curve.driver.expression=curve.driver.expression.replace(original,adapted)
        ctrl.update_tag()
    bpy.context.view_layer.update()
