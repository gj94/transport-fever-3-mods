"""Write TF3 native resources from consolidated Blender meshes.

The installed game's .msh descriptors use byte offsets/counts, float32 attributes,
and uint32 indices. No proprietary base-game geometry is copied.
"""
import bpy, json, math, struct, copy, re
from pathlib import Path
from mathutils import Vector
from vande_bharat import CAPACITY,WEIGHT,SPEED as VB_SPEED,YEAR as VB_YEAR
from freight_locomotives import SPECS as FREIGHT_SPECS
from coach_families import SPECS as COACH_SPECS
from pack_settings import CACHE_VERSION
from release_metadata import write_release_metadata

def lua(value):
 if isinstance(value,dict): return '{'+','.join(k+'='+lua(v) for k,v in value.items())+'}'
 if isinstance(value,(list,tuple)): return '{'+','.join(lua(v) for v in value)+'}'
 if isinstance(value,str): return json.dumps(value)
 if isinstance(value,bool): return 'true' if value else 'false'
 if isinstance(value,float):
  assert math.isfinite(value)
  return format(value,'.9g')
 return str(value)

def write_lua(path,value): path.write_text('function data()\nreturn '+lua(value)+'\nend\n',encoding='utf8')

def mesh_resource(path,mesh):
 mesh.calc_loop_triangles(); pos=[];norm=[];uv=[];tan=[];lookup={};idxs=[]
 normals=mesh.corner_normals; uvdata=mesh.uv_layers.active.data
 for tri in mesh.loop_triangles:
  for vi,li in zip(tri.vertices,tri.loops):
   p=mesh.vertices[vi].co;n=normals[li].vector
   axis=Vector((0,0,1)) if abs(n.z)<.9 else Vector((1,0,0))
   t=axis.cross(n).normalized()
   xy=uvdata[li].uv
   vertex=tuple(round(float(v),7) for v in (*p,*n,*xy,*t,1.0))
   idx=lookup.get(vertex)
   if idx is None:
    idx=len(pos)//3;lookup[vertex]=idx;pos.extend(p);norm.extend(n);uv.extend(xy);tan.extend((*t,1.0))
   idxs.append(idx)
 attrs={};blob=bytearray()
 for name,values,ncomp in [('position',pos,3),('normal',norm,3),('uv0',uv,2),('tangent',tan,4)]:
  block=struct.pack('<'+str(len(values))+'f',*values)
  attrs[name]={'count':len(block),'numComp':ncomp,'offset':len(blob)};blob.extend(block)
 count=len(idxs);indices=struct.pack('<'+str(count)+'I',*idxs)
 indexdesc={'count':len(indices),'offset':len(blob)};blob.extend(indices)
 write_lua(path,{'subMeshes':[{'indices':{name:indexdesc for name in attrs}}],'vertexAttr':attrs})
 Path(str(path)+'.blob').write_bytes(blob)
 return count//3

def far_box(mesh):
 lo=[min(v.co[a] for v in mesh.vertices) for a in range(3)];hi=[max(v.co[a] for v in mesh.vertices) for a in range(3)]
 vertices=[(x,y,z) for z in (lo[2],hi[2]) for y in (lo[1],hi[1]) for x in (lo[0],hi[0])]
 faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
 box=bpy.data.meshes.new('far_box');box.from_pydata(vertices,[],faces);box.update()
 src=mesh.uv_layers.active.data;poly=mesh.polygons[0]
 center=[sum(src[i].uv[a] for i in poly.loop_indices)/len(poly.loop_indices) for a in range(2)]
 uv=box.uv_layers.new()
 for poly in box.polygons:
  for j,i in enumerate(poly.loop_indices):uv.data[i].uv=(center[0]+.005*math.cos(j*math.pi/2),center[1]+.005*math.sin(j*math.pi/2))
 return box

def native_export(rootdir,key,newcoll,merged,mats,image,seats,pantograph_tracks=None):
 mod=rootdir/'game_build'/'gj94_indian_rail_pack';folder=mod/'content'/'vehicle'/'train'/key
 for sub in ('msh','mat/tex','icons'): (folder/sub).mkdir(parents=True,exist_ok=True)
 (mod/'_metadata').mkdir(parents=True,exist_ok=True)
 from vehicle_browser import write_vehicle_browser
 write_vehicle_browser(mod)
 write_release_metadata(mod)
 texdir=folder/'mat'/'tex';image.filepath_raw=str(texdir/(key+'_albedo_opacity.tga'));image.file_format='TARGA';image.save()
 for name in ('normal','metal_gloss_ao'):
  im=bpy.data.images.new(key+'_'+name,width=128,height=128);pixels=[]
  for y in range(128):
   for x in range(128):
    idx=(y//16)*8+x//16
    if name=='normal': color=(.5,.5,1,1)
    else:
     m=mats[idx] if idx<len(mats) else None;p=m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
     color=(float(p.inputs['Metallic'].default_value) if p else 0,1-float(p.inputs['Roughness'].default_value) if p else .5,1,1)
    pixels.extend(color)
  im.pixels.foreach_set(pixels);im.filepath_raw=str(texdir/(key+'_'+name+'.tga'));im.file_format='TARGA';im.save()
 params={'alpha_test':{'fragmentProperties':[{'cutout':True,'sorted':False,'alphaThreshold':.8,'a2CThreshold':.9}]},'light_receiver':{'fragmentProperties':[{'isLegacyMaterial':True,'lightMask':2}]}}
 for name,sampler in [('albedo_opacity','albedoOpacityTex'),('normal','normalTex'),('metal_gloss_ao','metalGlossAoTex')]:
  params['map_'+name]={'fragmentSamplers':{sampler:{'fileName':'tex/'+key+'_'+name+'.tga','type':'TWOD','wrapS':'REPEAT','wrapT':'REPEAT'}}}
 write_lua(folder/'mat'/'palette.mtl',{'order':0,'params':params,'type':'PHYS_TRANSPARENT_NRML_MAP'})
 # Keep transmissive panes separate from opaque paint and retain instrument UVs.
 glass=bpy.data.images.new(key+'_glass',width=128,height=128)
 glass.pixels.foreach_set([.72,.87,.9,.14]*(128*128));glass.filepath_raw=str(texdir/(key+'_glass_albedo_opacity.tga'));glass.file_format='TARGA';glass.save()
 for kind in {ob['tf3_material'] for ob in merged}-{'palette'}:
  custom=copy.deepcopy(params)
  if kind=='glass':
   custom['alpha_test']={'fragmentProperties':[{'cutout':False,'sorted':True,'disableDepthAndNormalWrite':True}]}
   filename=key+'_glass_albedo_opacity.tga'
  else:
   material=next(m for m in mats if re.sub(r'[^a-z0-9_]','_',m.name.lower())==kind)
   tex=next(n.image for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
   filename=key+'_'+kind+'_albedo_opacity.tga'
   tex.filepath_raw=str(texdir/filename);tex.file_format='TARGA';tex.save()
  custom['map_albedo_opacity']['fragmentSamplers']['albedoOpacityTex']['fileName']='tex/'+filename
  write_lua(folder/'mat'/(kind+'.mtl'),{'order':1 if kind=='glass' else 0,'params':custom,'type':'PHYS_TRANSPARENT_NRML_MAP'})
 def transform(ob):return [float(ob.matrix_local[r][c]) for c in range(4) for r in range(4)]
 pantograph_tracks=pantograph_tracks or {}
 if pantograph_tracks:
  (folder/'ani').mkdir(exist_ok=True)
  for name,track in pantograph_tracks.items():
   states={track['state']:track} if 'state' in track else track
   for state,values in states.items():
    filename=name+'.ani' if key=='wap7' else name+'_'+state+'.ani'
    write_lua(folder/'ani'/filename,{'times':values['times'],'transfs':values['transfs']})
 if key=='wap7' and pantograph_tracks:
  write_lua(folder/'wap7.trf.lua',{'updateScript':{'fileName':'wap7_transformator.script@wap7.updateFn','params':{}},'updateParticleSystemScript':{'fileName':'::/vehicle/train/shared/transformator_train.script@train.updateParticleSystemFn','params':{}}})
  (folder/'wap7_transformator.script.tl').write_text((rootdir/'tools'/'wap7_transformator.script.tl').read_text(),encoding='utf8')
 elif key in {'vb_tc_cc','vb_tc_ec'}:
  write_lua(folder/'vb.trf.lua',{'updateScript':{'fileName':'vb_transformator.script@vb.updateFn','params':{}},'updateParticleSystemScript':{'fileName':'::/vehicle/train/shared/transformator_train.script@train.updateParticleSystemFn','params':{}}})
  (folder/'vb_transformator.script.tl').write_text((rootdir/'tools/vb_transformator.script.tl').read_text(),encoding='utf8')
 elif key in FREIGHT_SPECS:
  family='wag9' if key=='wag9' else 'wag12b'
  write_lua(folder/(family+'.trf.lua'),{'updateScript':{'fileName':family+'_transformator.script@'+family+'.updateFn','params':{}},'updateParticleSystemScript':{'fileName':'::/vehicle/train/shared/transformator_train.script@train.updateParticleSystemFn','params':{}}})
  (folder/(family+'_transformator.script.tl')).write_text((rootdir/'tools'/(family+'_transformator.script.tl')).read_text(),encoding='utf8')
 roots=[o for o in newcoll.objects if not o.parent]
 def node(ob,lod):
  data={'name':ob.name,'transf':transform(ob)}
  if ob.name in pantograph_tracks:
   track=pantograph_tracks[ob.name]
   states={track['state']:track} if 'state' in track else track
   data['animations']={state:{'params':{'id':'ani/'+ob.name+('' if key=='wap7' else '_'+state)+'.ani'},'type':'FILE_REF'} for state in states}
  if ob.type=='MESH': data.update(mesh='msh/'+ob.name+f'_lod{lod}.msh',materials=['mat/'+ob['tf3_material']+'.mtl'])
  children=[node(c,lod) for c in ob.children if c in newcoll.objects[:]]
  if children:data['children']=children
  return data
 lods=[];counts=[]
 for lod,ratio in enumerate((1.0,.24,.055,.0025)):
  mods=[]
  if lod and lod!=3:
   for ob in merged:
    if len(ob.data.polygons)<100:continue
    m=ob.modifiers.new('TF3_LOD','DECIMATE');m.ratio=ratio;m.use_collapse_triangulate=True;mods.append((ob,m))
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();total=0
  for ob in merged:
   ev=ob.evaluated_get(dg);mesh=ev.to_mesh();far=far_box(mesh) if lod==3 else None
   total+=mesh_resource(folder/'msh'/(ob.name+f'_lod{lod}.msh'),far or mesh)
   if far:bpy.data.meshes.remove(far)
   ev.to_mesh_clear()
  counts.append(total)
  lods.append({'node':{'name':'RootNode','transf':[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],'children':[node(o,lod) for o in roots]},'visibleFrom':[0,100,400,1000][lod],'visibleTo':[100,400,1000,2500][lod]})
  for ob,m in mods:ob.modifiers.remove(m)
 names={'wap7':'Indian Railways WAP-7','lhb_3a':'LHB AC 3-tier','icf_sleeper':'ICF Sleeper (CBC retrofit)'}
 # Gameplay capacity is normalized slightly above the 72 physical berth locators.
 # User-selected speeds/years; power, capacity and fare balance are separate.
 specs={'wap7':(20.562,123000,180,2000,0,6)}
 if key in COACH_SPECS:
  coach=COACH_SPECS[key]
  names[key]=coach['name']
  specs[key]=(coach['length'],coach['weight'],coach['speed'],coach['year'],coach['capacity'],coach['bogie_distance'])
 vb=key.startswith('vb_');kind=key[3:].upper() if vb else None
 if vb:
  names[key]='Vande Bharat '+kind
  specs[key]=(19.375,WEIGHT[kind],VB_SPEED,VB_YEAR,CAPACITY[kind],5.85)
 if key in FREIGHT_SPECS:
  freight=FREIGHT_SPECS[key]
  names[key]=freight['name']
  specs[key]=(freight['length'],freight['weight'],freight['speed'],freight['year'],0,freight['bogie_distance'])
 spec=specs[key]
 length,weight,speed,year,capacity,bogiedist=spec
 # Vehicle spacing uses mating planes; rendering bounds include the projecting heads.
 anchors={o.name:float(o.matrix_world.translation.x) for o in newcoll.objects if o.name in {'coupling_front','coupling_rear'}}
 front=anchors.get('coupling_front',length/2);rear=anchors.get('coupling_rear',-length/2)
 length=front-rear
 points=[ob.matrix_world@v.co for ob in merged for v in ob.data.vertices]
 render_bounds={'bbMin':[min(p[a] for p in points) for a in range(3)],'bbMax':[max(p[a] for p in points) for a in range(3)]}
 if key=='wap7' or key in {'vb_tc_cc','vb_tc_ec'}:render_bounds['bbMax'][2]=max(render_bounds['bbMax'][2],6.0)
 if key in FREIGHT_SPECS:render_bounds['bbMax'][2]=max(render_bounds['bbMax'][2],FREIGHT_SPECS[key]['panto_high'])
 axles=[o.name for o in newcoll.objects if o.type=='EMPTY' and 'axle' in o.name]
 compartment={'loadConfigs':[{'cargoEntry':{'capacity':capacity,'cargoTypeSet':{'cargoClassesIncluded':['PASSENGERS'] if capacity else [],'cargoClassesExcluded':[],'cargoTypesIncluded':[],'cargoTypesExcluded':[]},'loadIndicator':'','seats':[]},'toHide':[]}]}
 metadata={'availability':{'yearFrom':year,'yearTo':0},'cost':{'price':-1},'description':{'name':names[key],'description':'Original Indian Railways prototype converted for TF3.'},'emissions':{'noise':{'score':35},'pollution':{'score':5}},'extent':{'bbMin':[-length/2,-1.9,-.03],'bbMax':[length/2,1.9,4.5]},'landVehicle':{'brakeDeceleration':2.5,'engines':[{'power':4500,'tractiveEffort':392,'type':'ELECTRIC'}] if key=='wap7' else [],'friction':.02,'topSpeed':speed/3.6,'weightEmpty':weight,'weightMaxPayload':capacity*80},'maintenance':{'lifespan':10957,'runningCosts':-1},'railVehicle':{'config':{'axles':axles,'fakeBogies':[[],[],[{'group':'RootNode','offset':0,'position':-bogiedist},{'group':'RootNode','offset':0,'position':bogiedist}]]}},'seatProvider':{'crewModels':[],'drivingLicense':'RAIL','seats':[]},'soundConfig':{'soundSet':{'name':'::/vehicle/'+('train/shared/sound/train_electric_modern.snd' if key=='wap7' else 'waggon/shared/sound/waggon_modern.snd')}},'transformatorConfig':{'skipFromLod':2,'transformator':{'name':'::/vehicle/train/shared/default_train.trf'}},'transportVehicle':{'carrier':'RAIL','comfortFactor':.8 if key=='lhb_3a' else .5,'compartments':[compartment],'engineTransportModes':['ELECTRIC_TRAIN'] if key=='wap7' else [],'transportModes':['TRAIN','ELECTRIC_TRAIN'],'filterTags':['default'],'reversible':key=='wap7','loadSpeed':3,'maintenanceFactor':1,'priceFactor':.5},'versioning':{'__version':CACHE_VERSION}}
 metadata['railVehicle']['config']['fakeBogies'].append(metadata['railVehicle']['config']['fakeBogies'][-1])
 metadata['extent']['bbMin'][0]=rear;metadata['extent']['bbMax'][0]=front
 metadata['seatProvider']['seats']=seats
 if key in COACH_SPECS:
  metadata['transportVehicle']['comfortFactor']=COACH_SPECS[key]['comfort']
  metadata['description']['description']=f"Indian Railways {names[key]}. Normalized capacity: {COACH_SPECS[key]['game_capacity']} passengers at standard game scale."
 if key in FREIGHT_SPECS:
  freight=FREIGHT_SPECS[key]
  metadata['landVehicle']['engines']=[{'power':freight['power'],'tractiveEffort':freight['effort'],'type':'ELECTRIC'}]
  metadata['soundConfig']['soundSet']['name']='::/vehicle/train/shared/sound/train_electric_modern.snd'
  metadata['transportVehicle'].update(engineTransportModes=['ELECTRIC_TRAIN'],reversible=True)
  if key!='wag9':metadata['transportVehicle'].update(multipleUnitOnly=True,filterTags=[])
  metadata['extent']['bbMax'][2]=render_bounds['bbMax'][2]
  family='wag9' if key=='wag9' else 'wag12b'
  metadata['transformatorConfig']={'skipFromLod':4,'transformator':{'name':family+'.trf'}}
  from wap7_audio import attach_local_horn
  attach_local_horn(rootdir,mod/'content/vehicle/train/wap7',metadata['soundConfig'])
 if key=='wap7':
  from wap7_audio import attach_local_horn
  attach_local_horn(rootdir,folder,metadata['soundConfig'])
 if key=='wap7' and pantograph_tracks:
  metadata['transformatorConfig']={'skipFromLod':4,'transformator':{'name':'wap7.trf'}}
 if vb:
  powered=kind.startswith('MC')
  metadata['landVehicle']['engines']=[{'power':1200,'tractiveEffort':90,'type':'ELECTRIC'}] if powered else []
  metadata['soundConfig']['soundSet']['name']='::/vehicle/'+('train/shared/sound/train_electric_modern.snd' if powered or kind=='DTC' else 'waggon/shared/sound/waggon_modern.snd')
  # Stock express comfort, normal ticket income and standard maintenance.
  # priceFactor is a fare factor, not the purchase-price multiplier.
  metadata['transportVehicle'].update(engineTransportModes=['ELECTRIC_TRAIN'] if powered else [],multipleUnitOnly=True,filterTags=[],reversible=True,comfortFactor=.8 if 'EC' in kind else .7,loadSpeed=4,priceFactor=.5,maintenanceFactor=1)
  metadata['extent']['bbMax'][2]=render_bounds['bbMax'][2]
  if kind.startswith('TC'):metadata['transformatorConfig']={'skipFromLod':4,'transformator':{'name':'vb.trf'}}
 if capacity:
  metadata['transportVehicle']['entrances']=[{'path':[[x,y*3,.56],[x,0,1.3]]} for x in (-length/2+2,length/2-2) for y in (-1,1)]
  if key in COACH_SPECS and COACH_SPECS[key]['family']=='lhb':
   doors=[o for o in newcoll.objects if o.name.startswith('door_') and o.name.endswith('_pivot') and o.type=='EMPTY']
   metadata['transportVehicle']['entrances']=[{'path':[[o.matrix_world.translation.x,3 if o.matrix_world.translation.y>0 else -3,.56],[o.matrix_world.translation.x,0,1.303]]} for o in doors]
  if vb:
   doors=[o for o in newcoll.objects if o.name.startswith('door_') and o.type=='EMPTY']
   metadata['transportVehicle']['entrances']=[{'path':[[o.matrix_world.translation.x,3 if o.matrix_world.translation.y>0 else -3,.56],[o.matrix_world.translation.x,0,1.23]]} for o in doors]
 write_lua(folder/(key+'.mdl'),{'boundingInfo':render_bounds,'collider':{'type':'BOX','params':{'halfExtents':[length/2,1.9,2.25]},'transf':[1,0,0,0,0,1,0,0,0,0,1,0,0,0,2.25,1]},'lods':lods,'metadata':metadata,'version':2})
 print('TF3_COUPLING',key,anchors,'spacing span',length,'render bounds',render_bounds)
 print('TF3_NATIVE',key,counts)
