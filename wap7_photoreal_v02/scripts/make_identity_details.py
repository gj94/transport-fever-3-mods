"""Original drawn approximation of the photo-visible Royapuram shed crest.
No photograph pixels are copied. This is not an authenticated official logo asset."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math
P=Path(__file__).resolve().parents[1]/'textures';N=1536;im=Image.new('RGBA',(N,N),(0,0,0,0));d=ImageDraw.Draw(im)
S=N/1024
q=lambda p:tuple(int(x*S) for x in p)
maroon=(131,37,51,255);cream=(235,218,170,255);white=(239,234,216,255)
d.ellipse(q((12,12,1012,1012)),fill=cream);d.ellipse(q((19,19,1005,1005)),fill=maroon);d.ellipse(q((150,150,874,874)),fill=cream);d.ellipse(q((161,161,863,863)),fill=(117,169,176,255))
# Separate clipped inner scene of the heritage railway-building and locomotive motif.
art=Image.new('RGBA',(N,N),(0,0,0,0));a=ImageDraw.Draw(art)
a.rectangle(q((150,510,875,875)),fill=(64,101,48,255));a.polygon(q((152,570,866,554,873,667,154,754)),fill=(189,170,113,255));a.rectangle(q((241,351,803,534)),fill=(172,69,58,255));a.rectangle(q((225,337,819,360)),fill=cream)
a.rectangle(q((237,511,810,536)),fill=(226,206,153,255));a.polygon(q((236,337,309,299,793,299,819,337)),fill=(202,152,103,255));a.rectangle(q((307,288,793,307)),fill=cream)
for x in [253,330,407,484,561,638,715,785]:
 a.rectangle(q((x,356,x+17,517)),fill=(231,215,170,255));a.rectangle(q((x-4,355,x+21,369)),fill=cream);a.rectangle(q((x-4,503,x+21,518)),fill=cream)
for x in [276,353,430,507,584,661,738]:
 a.rounded_rectangle(q((x,382,x+43,508)),radius=int(22*S),fill=(71,50,43,255));a.rectangle(q((x,425,x+43,508)),fill=(67,47,40,255))
# Small white electric locomotive, original icon, angled across the lower scene.
a.polygon(q((242,579,639,537,792,591,795,666,380,720,236,659)),fill=(207,210,183,255));a.polygon(q((238,608,385,653,795,603,795,625,382,677,237,632)),fill=(162,47,36,255));a.polygon(q((262,574,638,531,784,580,391,632)),fill=(54,62,52,255));a.polygon(q((250,584,356,614,354,645,250,614)),fill=(27,45,44,255));a.polygon(q((240,652,382,697,793,645,793,677,380,732,239,681)),fill=(39,46,39,255))
for x,y in [(314,701),(423,711),(680,679),(754,670)]:a.ellipse(q((x-22,y-16,x+22,y+20)),fill=(31,35,29,255))
a.line(q((243,752,827,673)),fill=(57,57,46,255),width=int(9*S));a.line(q((218,788,809,704)),fill=(66,60,48,255),width=int(8*S))
mask=Image.new('L',(N,N),0);ImageDraw.Draw(mask).ellipse(q((166,166,858,858)),fill=255);im.alpha_composite(Image.composite(art,Image.new('RGBA',(N,N)),mask))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',int(80*S))
def arctext(txt,angles,r,top=True):
 for ch,ang in zip(txt,angles):
  if ch==' ':continue
  tile=Image.new('RGBA',(int(110*S),int(110*S)),(0,0,0,0));dr=ImageDraw.Draw(tile);dr.text((55*S,55*S),ch,font=font,fill=white,anchor='mm',stroke_width=0)
  tile=tile.rotate(-(ang+90) if top else 90-ang,resample=Image.Resampling.BICUBIC,expand=True)
  x=(512+r*math.cos(math.radians(ang)))*S;y=(512+r*math.sin(math.radians(ang)))*S;im.alpha_composite(tile,(round(x-tile.width/2),round(y-tile.height/2)))
txt='ELECTRIC LOCO SHED';angles=[-166+i*152/(len(txt)-1) for i in range(len(txt))];arctext(txt,angles,422)
txt='ROYAPURAM';angles=[151-i*122/(len(txt)-1) for i in range(len(txt))];arctext(txt,angles,421,False)
d=ImageDraw.Draw(im)
for x in [103,921]:d.ellipse(q((x-6,518,x+6,530)),fill=cream)
im.save(P/'v02_royapuram_crest.png',optimize=True)
print('Original crest saved')
