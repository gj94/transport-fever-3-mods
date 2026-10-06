"""Neutral close-up gallery from an explicit integrated master, without rebuilding it.
Usage: blender -b -t 5 --python render_detail_gallery.py -- MASTER wheel 384 1600 5
Views: wheel, compressor, underfloor, bogie, roof_electrics.
"""
import bpy,sys,hashlib,json,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
a=sys.argv[sys.argv.index('--')+1:]
master=Path(a[0]).resolve();view=a[1] if len(a)>1 else 'wheel'
samples=int(a[2]) if len(a)>2 else 384;width=int(a[3]) if len(a)>3 else 1600;threads=int(a[4]) if len(a)>4 else 5
sha=hashlib.sha256(master.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(master));s=bpy.context.scene
views={
 'wheel':((9.15,-4.0,1.30),(7.80,-1.12,.76),2.16,.82),
 'compressor':((3.25,-4.0,1.37),(2.18,-.76,.83),2.70,.82),
 'underfloor':((1.20,-6.0,1.28),(0,-.40,1.0),6.8,.52),
 'bogie':((8.5,-7.0,1.70),(5.8,-.1,.99),7.8,.44),
 'roof_electrics':((3.8,-5.6,6.6),(0,-.10,4.06),7.1,.64),
}
loc,target,span,ratio=views[view]
col=bpy.data.collections.new('DETAIL_GALLERY_TRANSIENT');s.collection.children.link(col)
d=bpy.data.cameras.new('DETAIL_GALLERY_camera');cam=bpy.data.objects.new(d.name,d);col.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=span;d.clip_start=.02;d.clip_end=300;d.dof.use_dof=False;s.camera=cam
# A restrained low reflection card reveals components normally shadowed by the sill.
# It is inspection lighting, not an emissive material applied to the running gear.
fill=None
if view!='roof_electrics':
 d=bpy.data.lights.new('DETAIL_GALLERY_low_inspection_fill','AREA');d.energy=180;d.shape='RECTANGLE';d.size=4.0;d.size_y=1.2;d.color=(.94,.97,1)
 fill=bpy.data.objects.new(d.name,d);col.objects.link(fill);fill.location=(target[0],-4.8,1.1);fill.rotation_euler=(Vector(target)-fill.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=samples;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=32;s.cycles.adaptive_threshold=.015 if samples>=192 else .022;s.render.threads_mode='FIXED';s.render.threads=threads;s.render.resolution_x=width;s.render.resolution_y=round(width*ratio);s.render.resolution_percentage=100;s.cycles.seed=0;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.film_transparent=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
out=P/'previews'/'details';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/(view+'.png'))
t=time.time();bpy.ops.render.render(write_still=True);elapsed=time.time()-t
after=hashlib.sha256(master.read_bytes()).hexdigest();assert after==sha,'Input master changed'
report={'master_sha256':sha,'render_driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'master_bytes_unchanged':True,'view':view,'samples':samples,'width':width,'height':s.render.resolution_y,'denoised':False,'adaptive_sampling':True,'minimum_samples':32,'noise_threshold':s.cycles.adaptive_threshold,'threads':threads,'seconds':elapsed,'camera':{'location':loc,'target':target,'orthographic_span_m':span},'inspection_fill_watts':180 if fill else 0,'visibility_changes':[],'component_rebuilds':False,'image_sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()}
(out/(view+'.json')).write_text(json.dumps(report,indent=2));print('DETAIL_GALLERY_DONE',view,elapsed,flush=True)
