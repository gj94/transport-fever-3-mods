"""Prototype-scale VB2 layout contract shared by shell, markers and interiors.

Metres. The 23.100 m intermediate body and 15.570 m clear saloon are
explicit CAMTECH 2022 drawing dimensions. Seat reference coordinates and
DTC cubicle outlines are drawing-calibrated visual interpretations, not an
accessibility or production-installation certification. No compact-v01 data.
"""
from copy import deepcopy


def layout_for(kind):
    dtc = kind == 'DTC'
    ec = 'EC' in kind
    reverse = kind == 'NDTC_EC2'
    saloon = [-7.86, 3.33] if dtc else [-8.135, 7.435]
    walls = [-7.86, 3.33] if dtc else [-8.2175, 7.5175]
    # CC detailed mesh is .494 m across arms. A .499 m seat-centre
    # spacing leaves 5 mm between individual rests; bank centres preserve
    # a true .530 m armrest-clear aisle inside the unchanged body width.
    poses = []
    if dtc:
        # Pantry-to-toilet order: 20 in ten pairs; 24 in the opposite bank.
        # A shortened first bank, a companion single and a wheelchair bay are
        # actual exceptions, never hidden or overlaid nominal seats.
        counts = [2, 3, 3, 3, 3, 3, 3, 3, 1, 0]
        xs = [2.69 - .99 * j - (.56 if j >= 5 else 0) for j in range(10)]
        for row, (x, count) in enumerate(zip(xs, counts), 1):
            facing = -1 if row <= 5 else 1
            for y in [-1.258, -.759]:
                poses.append(dict(x=x, y=y, facing=facing, row=row, bank='pair'))
            for y in [1.263, .764, .265][:count]:
                poses.append(dict(x=x, y=y, facing=facing, row=row, bank='triple'))
        windows = [dict(x=x,width=1.58 if i==2 else 1.50,
                        height=.900 if i==2 else .88,
                        center_z=2.535 if i==2 else 2.525,
                        emergency=i==2,role='saloon')
                   for i,x in enumerate([1.00,-.96,-2.92,-4.88,-6.84])]
        windows += [dict(x=2.48,width=.60,height=.88,center_z=2.525,
                         emergency=False,role='saloon_end'),
                    dict(x=5.96,width=.60,height=.75,center_z=2.525,
                         emergency=False,role='crew'),
                    dict(x=-8.78,width=1.10,height=.88,center_z=2.525,
                         emergency=False,role='service',sides=[1])]
        windows.sort(key=lambda w:w['x'])
        rooms = [dict(x=-9.0425, side=-1, length=2.365, width=1.78,
                      bounds=[-10.225,-7.86,-1.50,.28], accessible=True,
                      turning_circle_center=[-10.62,.70],turning_circle_diameter=1.50)]
        galley = dict(x=5.875, side=1, length=2.55, width=1.005)
        electrical = dict(x=6.68, side=-1, length=.86, width=1.005, crew=True)
    elif ec:
        xs = [-.35 + (row - 6) * 1.18 for row in range(13)]
        for row, x in enumerate(xs, 1):
            for y in [-1.18,-.57,.57,1.18]:
                poses.append(dict(x=x,y=y,facing=1,row=row,bank='pair'))
        rooms = [dict(x=-9.265,side=s,length=1.890,width=1.005,accessible=False) for s in [-1,1]]
        galley = dict(x=8.861,side=1,length=2.522,width=1.005)
        electrical = dict(x=8.51,side=-1,length=1.835,width=1.005)
        windows = []
    else:
        # The drawing's approximately 960 mm row rhythm is interpreted at
        # 944 mm cushion-anchor pitch to retain >=440 mm end clearance for
        # the unchanged detailed seat and its folded footrest. Face-to-face
        # rows retain the larger 1.460 m central interval.
        xs = [-.35-(.730+j*.944) for j in reversed(range(8))] + [-.35+.730+j*.944 for j in range(8)]
        for row, x in enumerate(xs, 1):
            facing = 1 if row <= 8 else -1
            for y in [.759,1.258]:
                poses.append(dict(x=x,y=y,facing=facing,row=row,bank='pair'))
            for y in ([-1.263,-.764] if row in [1,16] else [-1.263,-.764,-.265]):
                poses.append(dict(x=x,y=y,facing=facing,row=row,bank='triple'))
        rooms = [dict(x=-9.265,side=s,length=1.890,width=1.005,accessible=False) for s in [-1,1]]
        galley = dict(x=8.8655,side=1,length=2.531,width=1.005)
        electrical = dict(x=8.40,side=-1,length=1.600,width=1.005)
        windows = []
    if not dtc:
        for j in range(8):
            emergency=j in [2,5]
            windows.append(dict(x=-.35+(j-3.5)*1.96,width=1.58 if emergency else 1.50,
                                height=.900 if emergency else .88,
                                center_z=2.535 if emergency else 2.525,
                                emergency=emergency,role='saloon'))
    layout = dict(kind=kind,saloon_bounds=saloon,partition_centers=walls,
                  lining_bounds=[-11.55,7.30 if dtc else 11.55],toilet_end=-1,
                  toilet_rooms=rooms,galley=galley,electrical=electrical,
                  seat_poses=poses,windows=windows,floor_z=1.32,
                  cushion_top_z=1.75,anchor_z=1.267,cab_bulkhead=7.30 if dtc else None,
                  expected_seats=44 if dtc else 52 if ec else 78,
                  wheelchair_bay=dict(x=-7.025,y=.925,length=1.44,width=1.10) if dtc else None,
                  basis='CAMTECH September 2022, system documentation, drawings pp28–33; furniture reference points are inferred')
    if reverse:
        layout['saloon_bounds']=[-saloon[1],-saloon[0]]
        layout['partition_centers']=[-walls[1],-walls[0]]
        layout['toilet_end']=1
        for p in poses:p.update(x=-p['x'],y=-p['y'],facing=-p['facing'])
        for w in windows:w['x']=-w['x']
        windows.sort(key=lambda w:w['x'])
        for r in rooms:r.update(x=-r['x'],side=-r['side'])
        for z in [galley,electrical]:z.update(x=-z['x'],side=-z['side'])
    assert len(poses)==layout['expected_seats'], (kind,len(poses))
    return deepcopy(layout)
