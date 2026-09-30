MODELS=[('wap7','pantograph_v04/WAP7_pantograph_v04.blend'),('lhb_3a','interiors_v02/lhb/LHB_3A_interior_v02.blend'),('icf_sleeper','coupling_v03/icf/ICF_sleeper_CBC_retrofit_v03.blend')]
VB_TYPES=('DTC','MC','MC2','TC_CC','TC_EC','NDTC_EC','NDTC_EC2')
MODELS += [('vb_'+kind.lower(),'vande_bharat_v01/cars/VB_'+kind+'.blend') for kind in VB_TYPES]
MODELS += [('wag9','wag9_v01/WAG9_master.blend'),
           ('wag12b_a','wag12_v01/sections/WAG12B_A.blend'),
           ('wag12b_b','wag12_v01/sections/WAG12B_B.blend')]

def selected_models(argv):
 """Optionally rebuild a family or comma-separated model keys."""
 if '--only' not in argv:return MODELS
 keys=argv[argv.index('--only')+1].split(',')
 selected=[(key,path) for key,path in MODELS if key in keys or ('vb' in keys and key.startswith('vb_'))]
 if not selected:raise ValueError('No matching models: '+','.join(keys))
 return selected

def asset_objects(bpy):
 root=next(o for o in bpy.data.objects if o.type=='EMPTY' and 'ROOT' in o.name.upper() and not o.parent)
 return root,[root,*root.children_recursive]
