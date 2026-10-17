"""Shared export/update settings for the requested gameplay performance upgrade."""
from freight_locomotives import SPECS as FREIGHT_SPECS
from vande_bharat import SPEED, MOTOR_POWER, MOTOR_EFFORT, COMFORT_CC, COMFORT_EC

WAP7 = dict(speed=200, year=2000, power=9000, effort=600)
UPGRADED_KEYS = ('wap7', 'wag12b_a', 'wag12b_b', 'vb_dtc', 'vb_mc', 'vb_mc2',
                 'vb_tc_cc', 'vb_tc_ec', 'vb_ndtc_ec', 'vb_ndtc_ec2')


def settings(key):
    if key == 'wap7':
        return WAP7
    if key in FREIGHT_SPECS:
        return FREIGHT_SPECS[key]
    if key.startswith('vb_'):
        kind = key[3:].upper()
        powered = kind.startswith('MC')
        return dict(speed=SPEED, power=MOTOR_POWER if powered else 0,
                    effort=MOTOR_EFFORT if powered else 0,
                    comfort=COMFORT_EC if 'EC' in kind else COMFORT_CC)
    return None


def description(key):
    spec = settings(key)
    if key.startswith('vb_'):
        return f'Gameplay upgrade: {spec["speed"]} km/h, comfort {spec["comfort"]:g}. Normal fares; requires electrified track.'
    return f'Gameplay upgrade: {spec["speed"]} km/h, {spec["power"]:,} kW and {spec["effort"]:,} kN. Requires electrified track.'


def apply_performance(metadata, key):
    spec = settings(key)
    if spec is None:
        return
    metadata['landVehicle']['topSpeed'] = spec['speed'] / 3.6
    metadata['landVehicle']['engines'] = ([dict(power=spec['power'],
        tractiveEffort=spec['effort'], type='ELECTRIC')] if spec['power'] else [])
    if 'comfort' in spec:
        metadata['transportVehicle']['comfortFactor'] = spec['comfort']
    if key in UPGRADED_KEYS:
        metadata['description']['description'] = description(key)
