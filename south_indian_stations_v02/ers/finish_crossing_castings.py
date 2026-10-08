# Globally unioned running rails with all-route45mm flange-channel subtraction.
# Offline preprocessing is preserved in prepare_rail_solids.py; Blender only reads JSON.
collection('21 | UNIONED RAIL SOLIDS • all-route flange channels')
for ob in list(scene.objects):
 if ob.name.startswith(('Physical rail ','Tapered physical switch blade ','Derived manganese frog nose ','Cast crossing ','Crossing sole casting ')):
  old=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if old.users==0:bpy.data.meshes.remove(old)
D=json.loads((P/'geometry'/'rail_solids.json').read_text())
for kind,m in [('head',railhead),('blade',railhead),('web',railmat),('foot',railmat)]:
 data=D[kind];ob=mesh('Globally unioned railway '+kind,data['vertices'],data['faces'],m);ob['construction']='Planar union minus ALL mapped route flange channels; no duplicated head overlays';ob['gauge_m']=1.676
q=json.loads((P/'physical_pointwork.json').read_text());q['running_head_method']=D['method'];q['global_union_flange_width_m']=D['flangeway_width_m'];q['global_union_crossing_count']=len(D['crossing_points']);q['source_geometry']='geometry/rail_solids.json';(P/'physical_pointwork.json').write_text(json.dumps(q,indent=2))
# Dark granular ballast, no pale concrete-looking base.
bs=ballast.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.065,.073,.065,1)
for node in ballast.node_tree.nodes:
 if node.type=='VALTORGB':
  node.color_ramp.elements[0].color=(.035,.042,.035,1);node.color_ramp.elements[1].color=(.14,.15,.13,1)
 if node.type=='BUMP':node.inputs['Strength'].default_value=.45;node.inputs['Distance'].default_value=.06
# Continuous shared ballast underneath the common turnout bearer envelopes.
beds=Batch('Shared turnout granular formation',ballast)
for k in range(math.floor(-510/.65),math.ceil(850/.65)):
 x=k*.65
 for ya,yb in bands_at(x):beds.box((x,(ya+yb)/2,.18),(.65,yb-ya+.5,.28))
beds.finish()
# Trapezoidal outer shoulders instead of vertical blocks, where running beds remain.
for ob in scene.objects:
 if not ob.name.startswith('Ballast formation '):continue
 vv=ob.data.vertices
 for i in range(0,len(vv),4):
  if i+3>=len(vv):break
  center=(vv[i+2].co+vv[i+3].co)/2
  for j in [i+2,i+3]:vv[j].co=center+(vv[j].co-center)*.84
