"""Gameplay settings for the source coach families, anchored to revision 12.

Physical accommodation supplies seating markers. Commercial capacity scales by
20/72 for ICF and 22/72 for LHB, rounded to the nearest whole depot passenger,
then doubled at the user's request. The game stores four times that capacity.
Prices/upkeep and fares stay stock.
Existing ICF sleeper and LHB 3A resource IDs survive the new source geometry.
"""
import math

CLASSES = ('1A', '2A', '3A', '2S', 'CC', 'SL', 'GS')
LABELS = {'1A': 'AC First Class', '2A': 'AC 2-tier', '3A': 'AC 3-tier',
          '2S': 'Second Sitting', 'CC': 'AC Chair Car', 'SL': 'Sleeper (CBC retrofit)',
          'GS': 'General Second Class'}
PHYSICAL = {'icf': (18, 46, 64, 108, 73, 72, 108),
            'lhb': (24, 52, 72, 102, 78, 80, 100)}
SPECS = {}
for family, physical_counts in PHYSICAL.items():
    for kind, physical in zip(CLASSES, physical_counts):
        key = 'icf_sleeper' if family == 'icf' and kind == 'SL' else family + '_' + kind.lower()
        baseline = 20 if family == 'icf' else 22
        game_capacity = 2 * math.floor(physical * baseline / 72 + .5)
        source = (f'icf_family_v01/{kind}/ICF_{kind}_master.blend' if family == 'icf'
                  else f'lhb_family_v01/models/LHB_{kind}.blend')
        SPECS[key] = dict(family=family, kind=kind, source=source,
                          name=family.upper() + ' ' + LABELS[kind],
                          physical=physical, game_capacity=game_capacity,
                          capacity=game_capacity * 4,
                          length=22.297 if family == 'icf' else 24.0,
                          weight=39000 if family == 'icf' else 49000,
                          speed=110 if family == 'icf' else 200,
                          year=1980 if family == 'icf' else 2000,
                          bogie_distance=7.3915 if family == 'icf' else 7.45,
                          comfort=.5 if family == 'icf' else .8)
