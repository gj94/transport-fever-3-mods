"""Rebuild original SURFV02 buffer contact masks (no photographic inputs).

Resolution 2048²; disc UV spans a nominal 0.51 m buffer plate. Geometry dimensions
remain authoritative. Fixed seed makes maps reproducible. Contact abrasion is
purposefully local to the buffer face rather than a generic grunge texture.
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, json, hashlib
OUT=Path(__file__).resolve().parents[1]/'textures'/'surfaces';OUT.mkdir(parents=True,exist_ok=True)
N=2048; rng=np.random.default_rng(3900206)
def noise(size):
    a=rng.random((size,size)); im=Image.fromarray((a*255).astype('uint8'))
    return np.asarray(im.resize((N,N),Image.Resampling.BICUBIC),dtype=np.float32)/255
x,y=np.meshgrid(np.linspace(-1,1,N,dtype=np.float32),np.linspace(1,-1,N,dtype=np.float32))
r=np.sqrt(x*x+y*y); theta=np.arctan2(y,x)
broad=noise(13); coarse=noise(67); medium=noise(180); fine=noise(580)
# Rubbed annulus with small, irregular surviving islands of old dry surface.
ring=np.clip((r-.46)/.16,0,1)*np.clip((1.005-r)/.07,0,1)
# Uneven surviving perimeter film and a swept transition band. The sparse
# chip mask is deliberately nonuniform around the disc, not leopard noise.
sector=(.5+.5*np.cos(theta-2.1))
chips=np.clip((coarse-.57)*3.0,0,1)*(.24+.76*broad)
wear=np.clip(ring*(.11+.13*sector+chips*.56+(medium-.5)*.08),0,1)
contact_transition=np.exp(-((r-(.57+(broad-.5)*.11))/.054)**2)
wear=np.clip(wear+contact_transition*.56,0,1)
# Two broader mechanical scuff islands break an otherwise even pale ring.
# Their positions rotate per buffer in the UV helper; there is no gravity drip.
for angle,width,amount in [(.65,.28,.44),(-2.20,.37,.33)]:
    delta=np.angle(np.exp(1j*(theta-angle)))
    scuff=np.exp(-.5*(delta/width)**2)*np.exp(-.5*((r-.82)/.15)**2)
    wear=np.clip(wear+scuff*amount*(.72+.38*medium),0,1)
# Centre grease is an actual contact mark, not universal dark albedo.
contact_r=np.sqrt(((x-.038)/1.025)**2+((y+.018)/.945)**2)
grease=np.clip((.645-contact_r)/.070+(broad-.5)*.85,0,1)*(.90+.04*broad)
# Random tangential scuffs, original constructive strokes, mm-scale.
scratch=Image.new('L',(N,N),0);d=ImageDraw.Draw(scratch)
for j in range(530):
    rr=rng.uniform(.54,.98); th=rng.uniform(-np.pi,np.pi); a=rng.uniform(.005,.06)
    pts=[]
    for tt in np.linspace(th-a,th+a,8):
        pts.append((int((rr*np.cos(tt)+1)*N/2),int((1-rr*np.sin(tt))*N/2)))
    d.line(pts,fill=int(rng.uniform(70,210)),width=int(rng.choice([1,1,2,3])))
s=np.asarray(scratch.filter(ImageFilter.GaussianBlur(.35)),dtype=np.float32)/255
wear=np.clip(wear+s*.45,0,1)
rough=np.clip(.30+(1-wear)*.31+(fine-.5)*.035-s*.10,.20,.75)
for suffix,a in [('wear',wear),('grease',grease),('roughness',rough)]:
    Image.fromarray(np.round(np.clip(a,0,1)*65535).astype('uint16')).save(OUT/('SURFV02_buffer_'+suffix+'.png'))
manifest={'seed':3900206,'resolution':[N,N],'nominal_disc_diameter_m':.51,
          'source':'Original numerical construction; no external raster or photograph pixels',
          'intended_use':'Buffer-face surface coverage and roughness only',
          'maps':[]}
for p in sorted(OUT.glob('SURFV02_buffer_*.png')):
    manifest['maps'].append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'colourspace':'Non-Color','bit_depth':16})
(OUT/'SURFV02_MAP_PROVENANCE.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
