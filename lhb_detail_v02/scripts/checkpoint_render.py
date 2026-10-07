"""Restart-safe real Cycles rendering; average equal-weight scene-linear EXRs only."""
from pathlib import Path
import bpy, numpy as np, hashlib, json, os, time

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(p,d):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(d,indent=2));t.replace(p)

def render(scene, identity, batches=8, samples=64):
 output=Path(scene.render.filepath); cache=output.parent/'.checkpoints'/output.stem;cache.mkdir(parents=True,exist_ok=True)
 start=time.monotonic(); image_settings=scene.render.image_settings
 original=(image_settings.file_format,image_settings.color_mode,image_settings.color_depth,scene.cycles.seed)
 spec={'identity':identity,'wrapper_sha256':sha(__file__),'batches':batches,'samples_per_batch':samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],'camera_matrix':[list(r) for r in scene.camera.matrix_world],'camera_lens':scene.camera.data.lens,'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma,'method':'equal-weight mean of independent-seed uniform-sample scene-linear RGBA float32 EXRs; one final display transform','denoising':False,'adaptive_sampling':False}
 fingerprint=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest(); manifest=cache/'manifest.json'
 if manifest.exists():
  old=json.loads(manifest.read_text());assert old['fingerprint']==fingerprint,'Checkpoint scene or renderer mismatch; preserve cache for review'
 records=[]
 scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=False;scene.cycles.samples=samples
 for i in range(batches):
  seed=104729*(i+1)+17;exr=cache/f'batch_{i:02d}.exr';side=exr.with_suffix('.json')
  valid=False
  if exr.exists() and side.exists():
   rec=json.loads(side.read_text());valid=rec.get('fingerprint')==fingerprint and rec.get('sha256')==sha(exr) and rec.get('seed')==seed
  if not valid:
   scene.cycles.seed=seed;scene.cycles.use_animated_seed=False
   scene.render.filepath=str(exr);image_settings.file_format='OPEN_EXR';image_settings.color_mode='RGBA';image_settings.color_depth='32';image_settings.exr_codec='ZIP'
   t=time.monotonic();bpy.ops.render.render(write_still=True)
   assert exr.exists()
   rec={'file':exr.name,'sha256':sha(exr),'seed':seed,'samples':samples,'fingerprint':fingerprint,'seconds':time.monotonic()-t,'format':'OPEN_EXR RGBA float32 scene-linear'};atomic_json(side,rec)
  records.append(rec);atomic_json(manifest,{'fingerprint':fingerprint,'spec':spec,'completed':records});print('CHECKPOINT_COMPLETE',output.name,i+1,batches,flush=True)
 accum=None;shape=None
 for rec in records:
  im=bpy.data.images.load(str(cache/rec['file']),check_existing=False)
  try:
   assert im.is_float, 'Checkpoint is not float data';shape=tuple(im.size)
   values=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(values)
   assert np.all(np.isfinite(values)), 'Non-finite radiance'
   if accum is None:accum=values.astype(np.float64)
   else:accum+=values
  finally:bpy.data.images.remove(im)
 mean=(accum/batches).astype(np.float32)
 result=bpy.data.images.new('CHECKPOINT_linear_average',width=shape[0],height=shape[1],alpha=True,float_buffer=True)
 result.pixels.foreach_set(mean);result.update()
 image_settings.file_format='OPEN_EXR';image_settings.color_mode='RGBA';image_settings.color_depth='32'
 merged=cache/'combined_linear.exr';result.save_render(str(merged),scene=scene)
 image_settings.file_format,image_settings.color_mode,image_settings.color_depth=original[:3]
 result.save_render(str(output),scene=scene);bpy.data.images.remove(result)
 scene.render.filepath=str(output);scene.cycles.samples=batches*samples;scene.cycles.seed=original[3]
 report={'workflow':'independent_seed_linear_exr_average_v1','total_uniform_samples':batches*samples,'adaptive_sampling':False,'batches':records,'fingerprint':fingerprint,'spec':spec,'combined_linear_sha256':sha(merged),'image_sha256':sha(output),'duration_seconds':time.monotonic()-start}
 atomic_json(output.with_suffix('.checkpoint.json'),report)
 return report
