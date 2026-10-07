"""Full-size VB2 authoring datums. Exact callouts are separate from inferred fittings."""
PITCH=24.0
BODY_END=11.55
BOGIE_CENTRES=14.9
WHEELBASE=2.7
GAUGE=1.676
FLOOR_Z=1.32
NOSE_DX=11.778-10.054231491088867
FORMATIONS={8:['DTC','MC','TC_EC','MC2','MC2','TC_CC','MC','DTC'],16:['DTC','MC','TC_CC','MC2','MC','TC_CC','MC2','NDTC_EC','NDTC_EC2','MC2','TC_CC','MC','MC2','TC_CC','MC','DTC']}

def layout_for(kind):
 from interior_layout import layout_for as interiors
 result=interiors(kind)
 result.update({'pitch':PITCH,'body_min':-BODY_END,'body_max':BODY_END,'bogie_centres':BOGIE_CENTRES,'wheelbase':WHEELBASE,'gauge':GAUGE,'floor_z':FLOOR_Z,'width':3.24,'nose_dx':NOSE_DX,'nose_tip_x':11.778,'cab_partition_x':7.30,'cab_shell_rear_x':5.65+NOSE_DX,'driver_x':9.35,'cab_door_x':8.25,'passenger_door_x':[-10.75,4.03] if kind=='DTC' else [-10.73,10.73],'windshield':{'lower_center_x':9.80+NOSE_DX,'lower_z':2.30,'upper_center_x':8.65+NOSE_DX,'upper_z':3.22},'dimension_source':'CAMTECH VB2 2022 system documentation pp28–33, primary drawing callouts','estimated_placement_precision_m':[.05,.10]})
 # Major roof positions are drawing-led estimates, separately documented from exact car dimensions.
 result['hvac_centres']=[-10.2,5.85] if kind=='DTC' else [-10.0,5.8] if kind.startswith('TC') else [-10.0,10.0]
 result['panto_base_x']=9.5;result['panto_rotation_z']=3.141592653589793
 result['underframe']={'converter_centres':[-3.8,3.8],'transformer_x':3.6,'auxiliary_x':-3.7,'battery_x':.5,'compressor_x':-4.8,'reservoir_x':-3.4,'water_x':2.6}
 return result
