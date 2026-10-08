from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(2400,820),(222,153,29));d=ImageDraw.Draw(im)
rows=[('തിരുവനന്തപുരം സെൻട്രൽ','/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf',125,80),('तिरुवनंतपुरम सेंट्रल','/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf',140,305),('THIRUVANANTHAPURAM CENTRAL','/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',111,594)]
for t,p,s,y in rows:
 f=ImageFont.truetype(p,s); box=d.textbbox((0,0),t,font=f);d.text(((2400-(box[2]-box[0]))/2,y),t,font=f,fill=(30,32,28))
im.save(P/'textures'/'TVC_trilingual_board.png')
