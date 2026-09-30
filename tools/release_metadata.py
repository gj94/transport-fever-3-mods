"""Write public v1.0 identity while retaining TF3's monotonic build revision."""
import json
from pathlib import Path
from pack_settings import REVISION, RELEASE_NAME

ROOT=Path(__file__).resolve().parents[1]

def write_release_metadata(mod):
    mod.mkdir(parents=True,exist_ok=True)
    (mod/'_metadata').mkdir(exist_ok=True)
    (mod/'mod.json').write_text(json.dumps({
        'modId':'gj94_indian_rail_pack','revision':REVISION,
        'severityAdd':'None','severityRemove':'Warning','visible':True,'cosmetic':False
    },indent=2)+'\n',encoding='utf8')
    (mod/'_metadata/modinfo.json').write_text(json.dumps({
        'name':RELEASE_NAME,
        'summary':'WAP-7, WAG-9, WAG-12B, seven ICF and seven LHB classes, Vande Bharat 8/16-car sets',
        'description':'Indian Railways locomotives, coaches and trainsets with class-specific interiors, side-on icons and balanced capacities. Normal fares and automatic costs. Electric locomotives require electrified track. ICF from 1980, WAG-9 from 1995, WAP-7/LHB from 2000, WAG-12B from 2017 and Vande Bharat from 2019.',
        'authors':[{'name':'gj94','role':'CREATOR'}],'tags':['Vehicle','Train'],
        'url':'https://github.com/gj94/transport-fever-3-mods'
    },indent=2)+'\n',encoding='utf8')

if __name__=='__main__':
    write_release_metadata(ROOT/'game_build/gj94_indian_rail_pack')
    print(RELEASE_NAME, 'TF3 resource revision', REVISION)
