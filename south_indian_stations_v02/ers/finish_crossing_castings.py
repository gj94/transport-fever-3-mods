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
# One continuous ballast solid replaces every overlapping per-route/fan bed.
for ob in list(scene.objects):
 if ob.name.startswith(('Ballast formation ','Shared turnout granular formation')):bpy.data.objects.remove(ob,do_unlink=True)
data=D['ballast'];ob=mesh('Globally unioned ballast formation',data['vertices'],data['faces'],ballast)
bev=ob.modifiers.new('Tapered gravel formation shoulders','BEVEL');bev.width=.14;bev.segments=1;bev.limit_method='ANGLE';bev.angle_limit=.6
