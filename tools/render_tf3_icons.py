"""Render the original vehicle masters on transparent backgrounds for TF3 UI."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from model_sources import selected_models,asset_objects
for key,source in selected_models(sys.argv):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/source))
    root,objects=asset_objects(bpy)
    keep=set(objects)
    for ob in bpy.data.objects:
        if ob.type in {'MESH','FONT','CURVE'}:
            ob.hide_render=ob not in keep
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=False
    scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.render.resolution_percentage=100
    cam=scene.camera
    if cam is None:
        cam=bpy.data.objects.new('TF3_ICON_CAMERA',bpy.data.cameras.new('TF3_ICON_CAMERA'))
        scene.collection.objects.link(cam);scene.camera=cam
        for location,energy,size in [((4,-8,13),2200,8),((-8,4,10),1600,7),((0,0,15),1500,9)]:
            light=bpy.data.lights.new('TF3_ICON_LIGHT','AREA');light.energy=energy;light.shape='DISK';light.size=size
            ob=bpy.data.objects.new('TF3_ICON_LIGHT',light);scene.collection.objects.link(ob);ob.location=location
            ob.rotation_euler=(Vector((0,0,1.8))-ob.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'
    out=ROOT/'game_build'/'gj94_indian_rail_pack'/'content'/'vehicle'/'train'/key/'icons'
    out.mkdir(parents=True,exist_ok=True)
    for suffix,width,height,location,scale in [('store',414,286,(25,-32,17),29),('icon_small@2x',300,112,(7,-35,13),28)]:
        cam.location=location
        cam.rotation_euler=(Vector((0,0,1.9))-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=scale
        scene.render.resolution_x=width;scene.render.resolution_y=height
        scene.render.filepath=str(out/(key+'_'+suffix+'.png'))
        bpy.ops.render.render(write_still=True)
    print('ICONS_RENDERED',key)
