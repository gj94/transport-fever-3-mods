"""Convert the original palette textures into DDS with complete mip chains."""
from pathlib import Path
from PIL import Image
import io,struct
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'game_build'/'gj94_indian_rail_pack'
def save_dds(im,path):
 levels=[];size=im.size
 while True:
  buf=io.BytesIO();im.save(buf,format='DDS',pixel_format='DXT5' if '_glass_' in path.name else 'DXT1');levels.append(buf.getvalue())
  if im.width==1 and im.height==1:break
  im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.BOX)
 header=bytearray(levels[0][:128]);flags=struct.unpack_from('<I',header,8)[0]
 struct.pack_into('<I',header,8,flags|0x20000)
 struct.pack_into('<I',header,20,len(levels[0])-128)
 struct.pack_into('<I',header,28,len(levels))
 struct.pack_into('<I',header,108,0x1000|0x8|0x400000)
 path.write_bytes(bytes(header)+b''.join(level[128:] for level in levels))
 check=Image.open(path);assert check.size==size
for folder in (MOD/'content'/'vehicle'/'train').iterdir():
 if not (folder/'mat').is_dir():continue
 for tga in (folder/'mat'/'tex').glob('*.tga'):
  im=Image.open(tga).convert('RGBA')
  if tga.stem.endswith('_normal'):im=Image.new('RGBA',im.size,(128,128,255,255))
  if '_glass_' in tga.stem:im=Image.new('RGBA',im.size,(184,222,230,36))
  # DDS sampling uses the opposite vertical origin from Blender's TGA output.
  im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  save_dds(im,tga.with_suffix('.dds'))
 for mtl in (folder/'mat').glob('*.mtl'):
  content=mtl.read_text().replace('.tga','.dds')
  if mtl.stem!='glass':content=content.replace('cutout=false,sorted=false,alphaThreshold=0,a2CThreshold=0','cutout=true,sorted=false,alphaThreshold=0.8,a2CThreshold=0.9')
  mtl.write_text(content)
 print('DDS_READY',folder.name)
