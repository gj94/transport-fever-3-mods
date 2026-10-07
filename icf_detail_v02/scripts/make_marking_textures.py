"""Optional original text-only decal regeneration. Requires Pillow with Raqm.
Pass --font path/to/NotoSansDevanagari-Regular.ttf on a non-Linux system.
Blender builds use the bundled PNGs and do not need this tool or these libraries.
"""
from pathlib import Path
import argparse
from PIL import Image,ImageDraw,ImageFont,features
p=argparse.ArgumentParser();p.add_argument('--font',default='/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf');a=p.parse_args()
if not features.check('raqm'):raise RuntimeError('Raqm shaping is required; unshaped Devanagari must not be substituted')
labels={'1A':'वातानुकूलित प्रथम श्रेणी','2A':'वातानुकूलित 2 टियर','3A':'वातानुकूलित 3 टियर','2S':'द्वितीय श्रेणी','CC':'वातानुकूलित कुर्सी यान','SL':'शयनयान','GS':'द्वितीय श्रेणी'}
font=ImageFont.truetype(a.font,128,layout_engine=ImageFont.Layout.RAQM);out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
for code,label in labels.items():
 b=font.getbbox(label);im=Image.new('RGBA',(b[2]-b[0]+16,b[3]-b[1]+16),(0,0,0,0));ImageDraw.Draw(im).text((8-b[0],8-b[1]),label,font=font,fill=(156,197,193,255),language='hi');im.save(out/f'class_hi_{code}.png')
print('Regenerated seven original class-label PNGs with proper Indic shaping')
