"""Make a portable, externally textured delivery copy without changing the authoring master.

Usage: blender -b -t 1 --python prepare_delivery_master.py -- SOURCE.blend DESTINATION
The destination may be refreshed before release. All source-only hidden replacements
remain in the original authoring checkpoint and deterministic component scripts.
"""
import bpy, sys, hashlib, json, shutil, array, struct
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:]
source=Path(args[0]).resolve();out=Path(args[1]).resolve()
assert source.parent!=out, 'Delivery must be a separate directory'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
out.mkdir(parents=True,exist_ok=True);(out/'textures').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
def visible_fingerprint():
 """Hash actual visible mesh coordinates/topology/assignments, not merely object names."""
 h=hashlib.sha256();data_hashes={}
 for obj in sorted(bpy.data.objects,key=lambda o:o.name):
  if obj.hide_render or obj.type not in {'MESH','FONT','CURVE','SURFACE'}:continue
  meta={'name':obj.name,'type':obj.type,'parent':obj.parent.name if obj.parent else None,'matrix':[list(r) for r in obj.matrix_world],'materials':[slot.material.name if slot.material else None for slot in obj.material_slots],'modifiers':[(m.name,m.type) for m in obj.modifiers]}
  if obj.type=='MESH':
   me=obj.data
   if me.name not in data_hashes:
    mh=hashlib.sha256()
    for seq,prop,kind,n in [(me.vertices,'co','f',len(me.vertices)*3),(me.loops,'vertex_index','i',len(me.loops)),(me.polygons,'loop_start','i',len(me.polygons)),(me.polygons,'loop_total','i',len(me.polygons)),(me.polygons,'material_index','i',len(me.polygons))]:
     a=array.array(kind,[0])*n;seq.foreach_get(prop,a);mh.update(a.tobytes())
    data_hashes[me.name]=mh.hexdigest()
   meta['geometry']=data_hashes[me.name]
  elif obj.type=='FONT':meta['text']=[obj.data.body,obj.data.size,obj.data.extrude,obj.data.bevel_depth]
  else:
   meta['curves']=[{'type':sp.type,'points':[list(p.co) for p in sp.points],'bezier':[[list(p.co),list(p.handle_left),list(p.handle_right)] for p in sp.bezier_points]} for sp in obj.data.splines]
  h.update(json.dumps(meta,sort_keys=True,separators=(',',':')).encode())
 return h.hexdigest()
before_fingerprint=visible_fingerprint()
before={o.name for o in bpy.data.objects if o.type in {'MESH','FONT','CURVE','SURFACE'} and not o.hide_render}
protected={o.name:[list(r) for r in o.matrix_world] for o in bpy.data.objects if o.type=='EMPTY'}
# Keep any visual proxy used as an explicit target by the live control graph.
referenced=set()
for obj in bpy.data.objects:
 for con in obj.constraints:
  for prop in con.bl_rna.properties:
   if prop.type=='POINTER':
    val=getattr(con,prop.identifier,None)
    if isinstance(val,bpy.types.Object):referenced.add(val.name)
 for mod in obj.modifiers:
  for prop in mod.bl_rna.properties:
   if prop.type=='POINTER':
    val=getattr(mod,prop.identifier,None)
    if isinstance(val,bpy.types.Object):referenced.add(val.name)
 if obj.animation_data:
  for fc in obj.animation_data.drivers:
   for var in fc.driver.variables:
    for target in var.targets:
     if isinstance(target.id,bpy.types.Object):referenced.add(target.id.name)
removed=[]
for obj in list(bpy.data.objects):
 if obj.type in {'MESH','FONT','CURVE','SURFACE'} and obj.hide_render and not obj.children and obj.name not in referenced:
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
dependencies=[];written_names={}
for im in bpy.data.images:
 if im.source!='FILE':continue
 name=Path(im.filepath).name
 if not name:name=im.name+'.png'
 if im.packed_file:
  data=bytes(im.packed_file.data)
 else:
  src=Path(bpy.path.abspath(im.filepath));assert src.is_file(),str(src);data=src.read_bytes()
 # Reuse the reproducible component-map layout when its exact bytes match.
 # This avoids shipping an identical flattened copy of every instrument/buffer map.
 for subdir in ['cab','surfaces']:
  candidate=source.parent/'textures'/subdir/name
  if candidate.is_file() and candidate.read_bytes()==data:
   name=subdir+'/'+name;break
 dest=out/'textures'/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if name in written_names and written_names[name]!=hashlib.sha256(data).hexdigest():
  # Distinct datablocks with same basename must never silently replace each other.
  np=Path(name);name=str(np.with_name(np.stem+'_'+hashlib.sha256(data).hexdigest()[:10]+np.suffix));dest=out/'textures'/name
 dest.write_bytes(data);written_names[name]=hashlib.sha256(data).hexdigest()
 if im.packed_file:im.unpack(method='REMOVE')
 im.filepath=str(dest);im.reload();im.filepath='//textures/'+name
 dependencies.append({'kind':'image','datablock':im.name,'path':'textures/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
for font in bpy.data.fonts:
 if font.filepath in {'','<builtin>'} or font.packed_file:continue
 src=Path(bpy.path.abspath(font.filepath));assert src.is_file(),str(src)
 dest=out/'fonts'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
 font.filepath='//fonts/'+src.name
 dependencies.append({'kind':'font','datablock':font.name,'path':'fonts/'+src.name,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
after={o.name for o in bpy.data.objects if o.type in {'MESH','FONT','CURVE','SURFACE'} and not o.hide_render}
assert before==after,'Visible geometry changed during delivery cleanup'
after_fingerprint=visible_fingerprint()
assert before_fingerprint==after_fingerprint,'Visible topology, coordinates or assignments changed'
for name,mat in protected.items():
 obj=bpy.data.objects.get(name);assert obj and max(abs(v-mat[i][j]) for i,row in enumerate(obj.matrix_world) for j,v in enumerate(row))<1e-8,name
bpy.context.preferences.filepaths.save_version=0
dest=out/'WAP7_detail_v02.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True,relative_remap=False)
assert source_hash==hashlib.sha256(source.read_bytes()).hexdigest(),'Authoring source was modified'
report={'authoring_sha256':source_hash,'delivery_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'delivery_bytes':dest.stat().st_size,'object_count':len(bpy.data.objects),'visible_geometry_count':len(after),'visible_names_unchanged':True,'empty_transforms_unchanged':True,'removed_hidden_replacements':removed,'dependencies':dependencies,'portability':'Full folder required; image pixels externalized without recompression or downsampling'}
report.update({'visible_geometry_before_sha256':before_fingerprint,'visible_geometry_after_sha256':after_fingerprint,'visible_geometry_and_assignments_unchanged':before_fingerprint==after_fingerprint})
(out/'delivery_manifest.json').write_text(json.dumps(report,indent=2))
print('DELIVERY_COPY_READY',dest,report['delivery_bytes'],len(after),flush=True)
