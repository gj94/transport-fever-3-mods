from pathlib import Path
from PIL import Image
from tf3_icons import construction_sizes
MOD=Path(__file__).resolve().parents[1]/'game_build'/'gj94_indian_rail_pack'
for folder in (MOD/'content'/'vehicle'/'train').iterdir():
    key=folder.name;icons=folder/'icons'
    if not (folder/(key+'.mdl')).is_file():continue
    Image.open(icons/(key+'_store.png')).save(icons/(key+'_store.tga'))
    small=Image.open(icons/(key+'_icon_small@2x.png')).convert('RGBA')
    for suffix,size in construction_sizes(small.width):
        small.resize(size,Image.Resampling.LANCZOS).save(icons/(key+'_'+suffix+'.tga'))
    print('ICONS_READY',key)
