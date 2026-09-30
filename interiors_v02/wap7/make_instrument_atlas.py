from PIL import Image,ImageDraw
from pathlib import Path
import math
out=Path(__file__).resolve().parent/'textures';out.mkdir(exist_ok=True)
im=Image.new('RGB',(1024,1024),(13,19,20));d=ImageDraw.Draw(im)
# Original generic visual instruments. Not exact operational scales or labels.
for idx in range(4):
 x=(idx%2)*512;y=(idx//2)*512
 d.ellipse((x+35,y+35,x+477,y+477),fill=(20,25,25),outline=(120,130,124),width=6)
 for j in range(41):
  a=math.radians(140+j*6.5);r=195;r2=171 if j%5==0 else 182
  d.line((x+256+math.cos(a)*r,y+256+math.sin(a)*r,x+256+math.cos(a)*r2,y+256+math.sin(a)*r2),fill=(220,225,200),width=3)
 a=math.radians(215+idx*34)
 d.line((x+256,y+256,x+256+math.cos(a)*152,y+256+math.sin(a)*152),fill=(226,202,129),width=7)
 d.ellipse((x+244,y+244,x+268,y+268),fill=(175,181,166));d.rectangle((x+212,y+361,x+300,y+370),fill=(157,169,153))
im.save(out/'cab_gauges.png')
im=Image.new('RGB',(512,256),(9,22,15));d=ImageDraw.Draw(im)
for y in range(25,230,30):
 d.line((25,y,485,y),fill=(30,57,36),width=1)
for x in range(25,500,35):d.line((x,20,x,230),fill=(25,45,30),width=1)
for i in range(8):d.rectangle((30+i*58,40,64+i*58,75+(i*19)%125),fill=(103,147,78))
im.save(out/'cab_display.png')
