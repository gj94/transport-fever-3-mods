"""Apply the agreed coach capacity scale to an existing geometry build."""
import re
from pathlib import Path
from coach_families import SPECS
from check_tf3_balance import model_stats

ROOT=Path(__file__).resolve().parents[1]
for key,spec in SPECS.items():
    path=ROOT/'game_build/gj94_indian_rail_pack/content/vehicle/train'/key/(key+'.mdl')
    text=path.read_text()
    text,count=re.subn(r'cargoEntry=\{capacity=\d+,',f"cargoEntry={{capacity={spec['capacity']},",text)
    assert count==1, key
    text,count=re.subn(r'weightMaxPayload=\d+',f"weightMaxPayload={spec['capacity']*80}",text)
    assert count==1, key
    text=re.sub(r'Normalized capacity: \d+ passengers',f"Normalized capacity: {spec['game_capacity']} passengers",text)
    assert model_stats(text)['capacity']==spec['capacity']
    path.write_text(text,encoding='utf8')
    print(key,spec['game_capacity'],'game passengers')
