"""Original procedural wear/marking maps. No photograph pixels are used."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, random, json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'textures'; OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(7318); random.seed(7318)
W,H=4096,1024
# Seam-directed shallow paint staining, deliberately restrained above the dusty sill.
u=np.linspace(-9.6,9.6,W)[None,:]; z=np.linspace(3.82,1.44,H)[:,None]
noise=np.zeros((H,W),np.float32)
for size,amp in [(16,.60),(64,.25),(256,.1),(1024,.05)]:
 a=rng.random((max(2,int(size*H/W)),size)); im=Image.fromarray(np.uint8(a*255)).resize((W,H),Image.Resampling.BICUBIC);noise+=np.asarray(im,dtype=np.float32)/255*amp
lower=np.clip((2.10-z)/.72,0,1)**1.6
roof=np.exp(-((3.79-z)/.095)**2)
dirt=.055*noise + lower*(.17+.15*noise)+roof*.18
# Local rain streaks below panel bolts and window/grille rims.
for x0 in [-7.38,-6.42,-6.22,-4.18,-3.66,-2.86,-2.34,2.34,2.86,4.35,4.40,5.15,5.20,6.22,7.38]+[random.uniform(-7,7) for _ in range(46)]:
 sig=random.uniform(.009,.026); end=random.uniform(1.9,3.1); top=random.uniform(3.35,3.73)
 streak=np.exp(-((u-x0)/sig)**2)*np.clip((z-end)/(top-end),0,1)*np.clip((top-z)/.07,0,1)
 dirt+=streak*random.uniform(.07,.21)
dirt=np.clip(dirt,0,.43)
col=np.stack([.87-dirt*.53,.865-dirt*.59,.824-dirt*.60],axis=2);col+=rng.normal(0,.0016,(H,W,1))
Image.fromarray(np.uint8(np.clip(col,0,1)*255),'RGB').save(OUT/'body_enamel_albedo.png')
rough=np.clip(.33+dirt*.8+noise*.035,0,1)
Image.fromarray(np.uint8(rough*255),'L').save(OUT/'body_enamel_roughness.png')
# Shaped typography is rasterized with FreeType/Raqm rather than unsupported Blender shaping.
font='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
hindi='/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf'
def label(name,text,size=180,color=(29,31,29,255),fontfile=font,stretch=1):
 f=ImageFont.truetype(fontfile,size); box=f.getbbox(text); im=Image.new('RGBA',(box[2]-box[0]+24,box[3]-box[1]+24));d=ImageDraw.Draw(im);d.text((12-box[0],12-box[1]),text,font=f,fill=color)
 if stretch!=1: im=im.resize((int(im.width*stretch),im.height),Image.Resampling.LANCZOS)
 im.save(OUT/name)
labels=[('railway_english.png','INDIAN RAILWAYS',180,(30,32,29,255),font,.74),('railway_hindi.png','भारतीय रेल',180,(30,32,29,255),hindi,1),('number_red.png','39002',200,(118,35,26,255),font,.82),('number_black.png','39002',180,(24,26,25,255),font,.83),('class.png','WAP 7',150,(24,26,25,255),font,.88),('shed.png','ROYAPURAM',120,(24,26,25,255),font,.77),('sr.png','SR',150,(24,26,25,255),font,1),('rpm.png','RPM',150,(24,26,25,255),font,1),('hog.png','HOG    MU',120,(34,36,33,255),font,.9),('cab1.png','CAB 1',100,(46,43,37,255),font,1),('cab2.png','CAB 2',100,(46,43,37,255),font,1),('lift.png','LIFT HERE',100,(195,185,145,255),font,1),('technical.png','25 kV  AC\nAXLE LOAD 20.5 t\nWAP-7  /  39002',90,(90,55,39,255),font,1)]
for a in labels: label(*a)
# Original simplified shed emblem and accurately proportioned tricolour.
im=Image.new('RGBA',(640,640));d=ImageDraw.Draw(im);d.ellipse((12,12,628,628),fill=(162,37,57),outline=(221,199,145),width=12);d.ellipse((100,100,540,540),fill=(238,231,192),outline=(238,220,125),width=12);d.ellipse((153,205,487,435),fill=(24,73,39));d.polygon([(145,343),(320,160),(495,343)],fill=(185,142,65));d.rectangle((181,314,459,350),fill=(238,234,200));
f=ImageFont.truetype(font,51); d.text((320,69),'ELECTRIC LOCO SHED',font=f,anchor='mm',fill='white');d.text((320,574),'ROYAPURAM',font=ImageFont.truetype(font,57),anchor='mm',fill='white');im.save(OUT/'shed_emblem.png')
im=Image.new('RGBA',(600,400));d=ImageDraw.Draw(im);d.rectangle((0,0,600,133),fill=(240,138,41));d.rectangle((0,133,600,267),fill=(239,239,222));d.rectangle((0,267,600,400),fill=(47,120,49));d.ellipse((252,152,348,248),outline=(26,54,100),width=5)
for i in range(24):
 t=i*np.pi/12;d.line((300,200,300+47*np.cos(t),200+47*np.sin(t)),fill=(26,54,100),width=2)
im.save(OUT/'indian_flag.png')
print('Created original material and decal maps:',len(list(OUT.glob('*.png'))))
