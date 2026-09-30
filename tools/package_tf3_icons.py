from pathlib import Path
from PIL import Image
MOD=Path(__file__).resolve().parents[1]/'game_build'/'gj94_indian_rail_pack'
for folder in (MOD/'content'/'vehicle'/'train').iterdir():
    key=folder.name;icons=folder/'icons'
    if not (folder/(key+'.mdl')).is_file():continue
    Image.open(icons/(key+'_store.png')).save(icons/(key+'_store.tga'))
    small=Image.open(icons/(key+'_icon_small@2x.png')).convert('RGBA')
    for suffix,size in [('icon_small@2x',(300,112)),('icon_small',(150,56)),('icon20@2x',(108,40)),('icon20',(54,20))]:
        small.resize(size,Image.Resampling.LANCZOS).save(icons/(key+'_'+suffix+'.tga'))
    print('ICONS_READY',key)
