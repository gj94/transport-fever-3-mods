"""Physically separated finish roles; subtle procedural microstructure in metre space."""
import bpy

def make(name,color,metal=0,rough=.4,noise=0,scale=120):
 m=bpy.data.materials.get('VB02_'+name) or bpy.data.materials.new('VB02_'+name);m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;n.clear();p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs[0],out.inputs[0]);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if noise:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=2
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*(c*(1-noise) for c in color),1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*(min(1,c*(1+noise)) for c in color),1);m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.00012;m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
 return m

def apply(ctx=None):
 specs={'white':((.83,.86,.88),.10,.24,.025),'blue':((.012,.047,.26),.18,.25,.04),'black':((.008,.012,.017),0,.33,.05),'rubber':((.013,.018,.024),0,.72,.15),'steel':((.43,.49,.54),.93,.24,.05),'brushed':((.48,.54,.59),.78,.34,.06),'alloy':((.36,.40,.43),.73,.4,.10),'dark_metal':((.045,.057,.066),.68,.45,.13),'glass':((.88,.96,.98),0,.065,0),'ivory':((.76,.77,.73),0,.39,.025),'floor':((.25,.28,.31),0,.76,.28),'fabric_cc':((.025,.075,.40),0,.86,.30),'fabric_ec':((.18,.18,.16),0,.85,.20),'headrest':((.06,.18,.48),0,.82,.17),'emissive':((.93,.96,1),0,.23,0),'red':((.52,.008,.012),.1,.26,0),'green':((.015,.39,.14),.05,.29,0),'amber':((.93,.32,.01),.1,.31,0),'screen':((.009,.022,.035),0,.25,0)}
 M={k:make(k,*v) for k,v in specs.items()}
 glass=M['glass'].node_tree.nodes.get('Principled BSDF');glass.inputs['Transmission Weight'].default_value=1;glass.inputs['IOR'].default_value=1.46
 e=M['emissive'].node_tree.nodes.get('Principled BSDF');e.inputs['Emission Color'].default_value=(.86,.93,1,1);e.inputs['Emission Strength'].default_value=2
 for key in ['white','blue']:
  p=M[key].node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.24;p.inputs['Coat Roughness'].default_value=.19
 mapping={'Pearl_white':'white','Cobalt_blue':'blue','Roof_silver':'alloy','Graphite':'dark_metal','Rubber':'rubber','Steel':'steel','Interior_ivory':'ivory','Floor':'floor','Seat_CC':'fabric_cc','Seat_EC':'fabric_ec','Headrest':'headrest','Clear_glass':'glass','Headlamp':'emissive','LED_warm':'emissive','Display_black':'black','Red':'red','Green':'green','Amber':'amber'}
 for obj in bpy.data.objects:
  if obj.type=='MESH':
   for slot in obj.material_slots:
    if slot.material and slot.material.name in mapping:slot.material=M[mapping[slot.material.name]]
 # Different underfloor finishes read as assembled equipment rather than one grey block.
 casing=make('equipment_powdercoat',(.18,.215,.235),.28,.52,.10,70)
 ceramic=make('transformer_oxidized_case',(.11,.135,.15),.55,.56,.15,45)
 reservoir=make('reservoir_service_finish',(.115,.145,.16),.45,.48,.14,85)
 for obj in bpy.data.objects:
  if obj.type=='MESH':
   target=casing if obj.name.startswith(('Battery_box','Auxiliary_converter','Traction_converter_cabinets','Electrical_changeover_switch')) else ceramic if obj.name.startswith('Transformer_case') else reservoir if obj.name.startswith('Main_reservoir') else None
   if target:
    for i in range(len(obj.data.materials)):obj.data.materials[i]=target
 M['equipment']=casing;M['reservoir']=reservoir
 return M
