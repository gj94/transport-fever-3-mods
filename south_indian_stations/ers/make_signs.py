#!/usr/bin/env python3
"""Original sign art, typeset with Noto fonts (OFL) and Pillow/RAQM."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent/'textures';P.mkdir(exist_ok=True)
F='/usr/share/fonts/truetype/noto/'
def sign(name,size,bg,lines):
 im=Image.new('RGB',size,bg);d=ImageDraw.Draw(im)
 for txt,font,y,maxw,h,col in lines:
  fs=h
  while True:
   f=ImageFont.truetype(F+font,fs); b=d.textbbox((0,0),txt,font=f)
   if b[2]-b[0]<=maxw:break
   fs-=1
  d.text(((size[0]-(b[2]-b[0]))/2-b[0],y-b[1]),txt,font=f,fill=col)
 im.save(P/(name+'.png'))
ml='NotoSansMalayalam-Bold.ttf';hi='NotoSansDevanagari-Bold.ttf';en='NotoSans-Bold.ttf'
# Separate panels keep regional glyph shaping correct and English fully legible.
for name,txt,font in [('ml','എറണാകുളം ജംഗ്ഷൻ',ml),('hi','एर्नाकुलम जंक्शन',hi),('en','ERNAKULAM JUNCTION',en)]:
 sign('entry_'+name,(2048,230),'#ddbf57',[(txt,font,54,1960,120,'#172023')])
for name,txt,font,col in [('ml','എറണാകുളം ജംഗ്ഷൻ',ml,'#253464'),('hi','एर्नाकुलम जंक्शन',hi,'#315e47'),('en','ERNAKULAM JUNCTION',en,'#953e36')]:
 sign('top_'+name,(2048,240),'#dedcd0',[(txt,font,55,1930,124,col)])
sign('platform_name',(1600,820),'#dcae2c', [('എറണാകുളം ജംഗ്ഷൻ',ml,50,1460,145,'#172223'),('एर्नाकुलम जंक्शन',hi,300,1460,145,'#172223'),('ERNAKULAM JUNCTION',en,570,1480,120,'#172223')])
sign('catering',(1200,450),'#1c6658',[('CATERING STALL',en,70,1120,106,'#eeeeda'),('TEA  •  COFFEE  •  SNACKS',en,265,1090,53,'#eeeeda')])
sign('coach_position',(512,600),'#edece4',[('COACH POSITION',en,55,470,43,'#155294'),('13',en,165,450,255,'#155294')])
sign('tickets',(1000,240),'#1f4d72',[('TICKETS  /  RESERVATION',en,67,930,80,'#f3efd9')])
sign('parking',(1000,300),'#26386a',[('CAR PARKING',en,50,940,94,'#eeeeeb'),('ENTRY  →',en,173,930,63,'#eeeeeb')])
sign('atm',(1000,250),'#256843',[('ATM',en,53,890,127,'#f5f4dd')])
print('Saved',len(list(P.glob('*.png'))),'sign textures')
