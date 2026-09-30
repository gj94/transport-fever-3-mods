"""Update the existing pack's two cab anchors without rebuilding geometry."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
model=ROOT/'game_build/gj94_indian_rail_pack/content/vehicle/train/wap7/wap7.mdl'
text=model.read_text()
pattern=r'(animation="driving_upright",crew=true,forward=(?:true|false),group="cab_[ab]_interior",transf=\{)([^}]+)(\})'
heights=[]
def correct(match):
    values=match.group(2).split(',')
    assert len(values)==16
    assert abs(float(values[12])-8.03)<.001 and abs(float(values[13])-.78)<.001
    assert abs(float(values[14])-2.22)<.001 or abs(float(values[14])-1.8)<.001
    values[14]='1.8';heights.append(float(values[14]))
    return match.group(1)+','.join(values)+match.group(3)
updated,count=re.subn(pattern,correct,text)
assert count==2, f'Expected both cab anchors, found {count}'
model.write_text(updated)
print('Driver anchors:',heights,'metres; geometry unchanged')
