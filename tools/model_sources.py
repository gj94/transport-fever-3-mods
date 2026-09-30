MODELS=[('wap7','pantograph_v04/WAP7_pantograph_v04.blend'),('lhb_3a','interiors_v02/lhb/LHB_3A_interior_v02.blend'),('icf_sleeper','coupling_v03/icf/ICF_sleeper_CBC_retrofit_v03.blend')]

def asset_objects(bpy):
 root=next(o for o in bpy.data.objects if o.type=='EMPTY' and 'ROOT' in o.name.upper() and not o.parent)
 return root,[root,*root.children_recursive]
