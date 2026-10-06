"""Original instrument face artwork, derived from visible equipment classes.
No photograph, logo or third-party raster is embedded. Scale values are illustrative.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, json
OUT=Path(__file__).resolve().parents[1]/'textures/cab';OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s,b=False):return ImageFont.truetype(BOLD if b else FONT,s)
def txt(d,xy,t,s,fill=(35,39,37),anchor='mm',b=False):d.text(xy,t,font=font(s,b),fill=fill,anchor=anchor)
def dial(name,label,unit,maximum=10,dual=False):
 S=1024;im=Image.new('RGB',(S,S),(225,226,212));d=ImageDraw.Draw(im)
 d.ellipse((18,18,S-18,S-18),fill=(228,230,218),outline=(123,132,124),width=4)
 cx,cy=512,512
 steps=60 if maximum in (6,12) else 50
 for j in range(steps+1):
  ang=math.radians(225-j*270/steps);ro=426;ri=ro-(38 if j%5==0 else 20)
  d.line([(cx+ri*math.cos(ang),cy-ri*math.sin(ang)),(cx+ro*math.cos(ang),cy-ro*math.sin(ang))],fill=(36,43,40),width=6 if j%5==0 else 3)
  if j%10==0:
   v=maximum*j/steps;txt(d,(cx+344*math.cos(ang),cy-344*math.sin(ang)),str(int(v)) if v==int(v) else str(round(v,1)),52)
 txt(d,(cx,618),label,60,b=True);txt(d,(cx,686),unit,38)
 # Deliberately no serials, test seals, manufacturer logos, or status text.
 if dual:
  txt(d,(cx,750),'1 / 2' if label=='BC' else 'MR / FP',32)
 im.save(OUT/(name+'.png'))
for args in [('gauge_bc','BC','kgf/cm²',6,True),('gauge_mrfp','MR / FP','kgf/cm²',12,True),('gauge_bp','BP','kgf/cm²',10,False),('gauge_afi','AIR FLOW','',10,False),('gauge_pb','PB','kgf/cm²',10,False)]:dial(*args)
# MEMOTEL-style speed indication: dimensions and exact face calibration are representative.
im=Image.new('RGB',(1024,1024),(231,234,221));d=ImageDraw.Draw(im);cx,cy=512,580
for j in range(91):
 a=math.radians(220-j*260/90);ro=438;ri=ro-(40 if j%10==0 else 24 if j%5==0 else 13)
 d.line([(cx+ri*math.cos(a),cy+ri*math.sin(a)),(cx+ro*math.cos(a),cy+ro*math.sin(a))],fill=(21,30,27),width=5 if j%5==0 else 2)
 if j%10==0:txt(d,(cx+344*math.cos(a),cy+344*math.sin(a)),str(j*2),47,b=True)
txt(d,(512,742),'km/h',47);d.rounded_rectangle((324,822,700,946),radius=15,fill=(35,48,39));txt(d,(512,882),'000',74,(126,165,109),b=True)
im.save(OUT/'speedometer.png')
# Battery moving-coil voltmeter.
im=Image.new('RGB',(768,768),(231,233,220));d=ImageDraw.Draw(im);cx,cy=384,584
for j in range(31):
 a=math.radians(150-j*4);ro=456;ri=ro-(45 if j%5==0 else 24)
 d.line([(cx+ri*math.cos(a),cy-ri*math.sin(a)),(cx+ro*math.cos(a),cy-ro*math.sin(a))],fill=(30,35,31),width=5 if j%5==0 else 3)
 if j%10==0:txt(d,(cx+360*math.cos(a),cy-360*math.sin(a)),str(j*5),44)
txt(d,(384,483),'V',70);txt(d,(384,686),'U  BA',38,b=True);im.save(OUT/'meter_battery.png')
# Slender OHE/tractive-effort instruments.
for name,title,maxv,unit,signed in [('meter_ohe','U',30,'kV',False),('meter_bogie1','BOGIE 1',300,'kN',True),('meter_bogie2','BOGIE 2',300,'kN',True)]:
 im=Image.new('RGB',(512,1024),(228,231,217));d=ImageDraw.Draw(im)
 d.rectangle((213,100,244,844),fill=(45,55,47));d.rectangle((270,120,294,503 if signed else 305),fill=(87,122,95))
 if signed:d.rectangle((270,509,294,826),fill=(162,124,103))
 for i in range(31):
  y=840-i*24;d.line((165 if i%5==0 else 188,y,248,y),fill=(27,38,32),width=4 if i%5==0 else 2)
  if i%10==0:txt(d,(118,y),str((-150+i*15) if signed else i),38)
 txt(d,(256,55),unit,41);txt(d,(256,928),title,38,b=True);im.save(OUT/(name+'.png'))
# Screen: a dim blank phosphor LCD, no fictitious train state or operating instruction.
im=Image.new('RGB',(1024,256),(31,50,33));d=ImageDraw.Draw(im)
for y in range(8,250,5):d.line((8,y,1016,y),fill=(32,52,35),width=1)
im.save(OUT/'lcd_blank.png')
(OUT/'PROVENANCE.json').write_text(json.dumps({'authoring':'Original Python/Pillow artwork; no photographic projection','readable_abbreviations':'Real equipment designators, cross checked against Railway Board Annexure E and inspected Panel A photo','calibration':'Face calibrations, needle states, font spacing and physical dimensions are representative visual art, not an operational instrument or certified 39002 survey','file_count':len(list(OUT.glob('*.png')))},indent=2))
print('cab texture artwork',len(list(OUT.glob('*.png'))))
