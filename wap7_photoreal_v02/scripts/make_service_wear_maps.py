"""Original construction-located maintained-service wear, replacing the v02 starter maps.
No photographic pixels. Coordinates are metric rest-body coordinates; the nose
projection is widened by the material context together with front hardware.
The broad upper paint remains quiet. Soil is limited to sills, real joints,
filter rims, door touch points, roof attachment drains and unswept glass edges.
"""
from pathlib import Path
from PIL import Image
import numpy as np, math, json, hashlib, os
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(exist_ok=True)
S=P/'surfaces';S.mkdir(exist_ok=True)
SEED=3900327;rng=np.random.default_rng(SEED)
LOWER_SIDE_DUST_GAIN=1.5
FEATURE_GRIME_GAIN=1.25

def save(im,path):
 tmp=path.with_name(path.stem+'.writing.png');im.save(tmp);os.replace(tmp,path)

def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)

def linear(c):
 c=np.asarray(c,dtype=np.float32)/255
 return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)

def encode(c):
 c=np.clip(c,0,1);s=np.where(c<=.0031308,c*12.92,1.055*c**(1/2.4)-.055)
 return np.clip(np.rint(s*255),0,255).astype('uint8')

class Canvas:
 def __init__(self,w,h,xlim,ylim):
  self.w=w;self.h=h;self.xlim=xlim;self.ylim=ylim
  self.x=np.linspace(*xlim,w,dtype=np.float32)[None,:]
  self.y=np.linspace(ylim[1],ylim[0],h,dtype=np.float32)[:,None]
  self.fields={k:np.zeros((h,w),np.float32) for k in ('dust','grime','rust')}
 def roi(self,x0,x1,y0,y1):
  a=max(0,int((x0-self.xlim[0])/(self.xlim[1]-self.xlim[0])*self.w));b=min(self.w,int((x1-self.xlim[0])/(self.xlim[1]-self.xlim[0])*self.w)+1)
  c=max(0,int((self.ylim[1]-y1)/(self.ylim[1]-self.ylim[0])*self.h));d=min(self.h,int((self.ylim[1]-y0)/(self.ylim[1]-self.ylim[0])*self.h)+1)
  return a,b,c,d
 def gauss(self,key,x,y,sx,sy,amount,maximum=False):
  a,b,c,d=self.roi(x-3.6*sx,x+3.6*sx,y-3.6*sy,y+3.6*sy)
  if a>=b or c>=d:return
  val=amount*np.exp(-.5*((self.x[:,a:b]-x)/sx)**2-.5*((self.y[c:d]-y)/sy)**2)
  out=self.fields[key][c:d,a:b]
  if maximum:np.maximum(out,val,out=out)
  else:out+=(1-out)*val
 def streak(self,key,x,y,length,width,amount,sway=0):
  a,b,c,d=self.roi(x-4*width-abs(sway)-.008,x+4*width+abs(sway)+.008,y-length-.004,y+.004)
  if a>=b or c>=d:return
  t=(y-self.y[c:d])/length;valid=(t>=0)&(t<=1)
  center=x+sway*t+.0012*np.sin(t*8.1+rng.uniform(0,6))
  sigma=width*(1-.65*np.clip(t,0,1))+.0008
  val=amount*np.exp(-.5*((self.x[:,a:b]-center)/sigma)**2)*np.maximum(0,1-t)**.72*valid
  out=self.fields[key][c:d,a:b];out+=(1-out)*val
 def path(self,key,points,width,amount):
  # Max-composited stamps avoid opacity accumulating merely from sample density.
  lengths=[math.dist(a,b) for a,b in zip(points[:-1],points[1:])];total=sum(lengths);done=0
  for (a,b),length in zip(zip(points[:-1],points[1:]),lengths):
   for u in np.linspace(0,1,max(3,int(length/(width*.65)))):
    t=(done+u*length)/total;x=a[0]+u*(b[0]-a[0]);y=a[1]+u*(b[1]-a[1])
    self.gauss(key,x,y,width*(1-.60*t),width*(1-.60*t),amount*(1-.8*t),True)
   done+=length
 def export_paint(self,name,base=(219,219,207)):
  colors={'dust':linear((151,127,91)),'grime':linear((110,103,86)),'rust':linear((125,78,40))}
  out=np.empty((self.h,self.w,3),np.float32);out[:]=linear(base)
  rough=np.full((self.h,self.w),.43,np.float32);coverage=np.zeros_like(rough)
  stats={}
  for key,gain in [('dust',.26),('grime',.20),('rust',.24)]:
   a=np.clip(self.fields[key],0,.62);out*=1-a[:,:,None];out+=a[:,:,None]*colors[key]
   rough+=a*gain;coverage+=(1-coverage)*a
   stats[key]={'mean':float(a.mean()),'max':float(a.max())}
  # Only sub-DN paint finish variation; service wear comes from placed features.
  micro=rng.normal(0,.22,(self.h,self.w)).astype(np.float32)
  rgb=encode(out);rgb=np.clip(rgb.astype(np.float32)+micro[:,:,None],0,255).astype('uint8')
  save(Image.fromarray(rgb),P/(name+'_albedo.png'))
  save(Image.fromarray(np.rint(np.clip(rough,.42,.78)*255).astype('uint8')),P/(name+'_roughness.png'))
  save(Image.fromarray(np.rint(np.clip(coverage,0,1)*255).astype('uint8')),P/(name+'_grime_mask.png'))
  return stats

manifest={'seed':SEED,'provenance':'Original constructive masks and linear-light pigment/soil mixing; no source photo pixels','features':{},'maps':[],'bounded_gain':{'lower_side_dust':LOWER_SIDE_DUST_GAIN,'filter_door_grime':FEATURE_GRIME_GAIN,'front_roof_buffers_glass_unchanged':True}}
layouts={1:[(4.78,.78,1.43,2.91),(-3.92,.52,1.20,3.02),(-6.2,.40,.47,3.10),(-6.72,.40,.47,3.10)],2:[(-4.8,1.43,1.3,2.94),(3.85,.52,1.3,2.96),(6.22,.38,.47,3.1),(6.7,.38,.47,3.1)]}
for side in [1,2]:
 c=Canvas(6144,1536,(-9.6,9.6),(1.44,3.82));X,Z=c.x,c.y
 # Soil thrown from bogie regions, confined to the lower paint field.
 low=smooth((2.15-Z)/.69)
 amount=.32+.085*np.exp(-((X+6.0)/2.35)**2)+.075*np.exp(-((X-6.0)/2.15)**2)
 modulation=1+.065*np.sin(X*2.3+side)+.025*np.sin(X*7.1+side*1.7)
 c.fields['dust'][:]=np.clip(low*amount*modulation*LOWER_SIDE_DUST_GAIN,0,.62)
 # Actual eaves/seam/downpipe sites; no all-over repeated streak barcode.
 for anchor in [-8.13,-7.48,-5.78,-2.95,0,2.95,5.78,7.48,8.13]:
  for j in range(6):
   x=anchor+rng.uniform(-.045,.045);z=rng.uniform(3.51,3.60)
   c.streak('grime',x,z,rng.uniform(.10,.39),rng.uniform(.0025,.0065),rng.uniform(.045,.11),rng.uniform(-.007,.007))
  c.gauss('dust',anchor,3.57,.070,.024,.12)
 eaves_grime=c.fields['grime'].copy()
 # Grille surrounds are narrow and irregular; dirt increases at real lower ledges.
 for x,w,h,z in layouts[side]:
  for edge in [x-w/2-.017,x+w/2+.017]:
   for zz in np.linspace(z-h/2,z+h/2,18):
    c.gauss('grime',edge+rng.uniform(-.003,.003),zz,.013,.050,rng.uniform(.06,.15),True)
   for zz in [z-h/2+.06,z,z+h/2-.06]:c.gauss('rust',edge,zz,.012,.027,rng.uniform(.04,.09))
  for xx in np.linspace(x-w/2,x+w/2,16):c.gauss('grime',xx,z-h/2-.016,.027,.015,.16,True)
  for j in range(7 if h>1 else 4):
   xx=x+rng.uniform(-w*.44,w*.44)
   c.streak('grime',xx,z-h/2-.018,rng.uniform(.14,.48) if h>1 else rng.uniform(.08,.23),rng.uniform(.003,.008),rng.uniform(.13,.26),rng.uniform(-.006,.010))
   if j<2:c.streak('rust',xx,z-h/2-.018,rng.uniform(.10,.32),.0025,rng.uniform(.055,.11),.002)
 # Door seals, hand/latch contact, hinge moisture, and actual window drain slots.
 for e in [-1,1]:
  x=e*7.80
  for edge in [x-.326,x+.326]:
   for zz in np.linspace(1.60,3.48,32):c.gauss('grime',edge,zz,.0065,.040,.10,True)
  latch=x-e*.21;c.gauss('grime',latch,2.485,.063,.083,.22)
  c.gauss('dust',latch-e*.055,2.49,.045,.035,.09)
  c.streak('grime',latch,2.444,.20,.0045,.10,e*.004)
  for z in [1.77,2.46,3.37]:
   hinge=x+e*.299;c.gauss('grime',hinge,z,.034,.056,.15)
   c.streak('rust',hinge, z-.04,.115,.003,.08,e*.003)
  for drain in [x-.148,x+.148]:c.streak('grime',drain,2.623,.17,.0035,.13,e*.002)
 # Strengthen only the added filter/door features; preserve the eaves contribution.
 c.fields['grime'][:]=np.clip(eaves_grime+np.maximum(0,c.fields['grime']-eaves_grime)*FEATURE_GRIME_GAIN,0,.62)
 stats=c.export_paint('v02_body_side'+str(side));manifest['features']['body_side'+str(side)]={'stats':stats,'filters':layouts[side],'latch_x':[-7.59,7.59],'latch_z':2.485,'lower_dust_top_m':2.15}
 del c

# The front remains cleaner than the flank: deposits at hardware, not a brown wash.
c=Canvas(2048,2048,(-1.55,1.55),(1.40,3.60));Y,Z=c.x,c.y
c.fields['dust'][:]=smooth((1.83-Z)/.41)*(.15+.035*np.cos(Y*3.1))
for side in [-1,1]:
 center=side*.618
 for yy in [center-.5065,center+.5065]:
  for zz in np.linspace(2.555,3.48,22):c.gauss('grime',yy,zz,.012,.045,.10,True)
  c.streak('grime',yy,2.54,.24,.005,.19,side*.003)
 for yy in [center-.35,center+.35]:c.streak('grime',yy,3.51,.15,.003,.055,side*.002)
 c.gauss('grime',side*.798,2.54,.030,.028,.16)
 c.streak('grime',side*.918,2.49,.16,.003,.12,side*.003)
 c.gauss('grime',side*.535,1.69,.095,.085,.19)
 c.streak('grime',side*.535,1.62,.18,.008,.12,side*.005)
 c.streak('rust',side*1.255,3.53,.20,.005,.085,side*.002)
manifest['features']['nose']={'stats':c.export_paint('v02_nose'),'projection':'Y/Z, expanded with front width context','front_cleaner_than_flank':True}
del c

# Sparse actual roof-foot drainage. Metric world XY; roof fittings were not widened.
c=Canvas(4096,1024,(-9.6,9.6),(-1.75,1.75))
for e in [-1,1]:
 for side in [-1,1]:
  c.gauss('rust',e*8.40,side*.56,.070,.057,.34)
  for j in range(3):
   y=side*(.535+j*.022)
   c.path('rust',[(e*8.43,y),(e*8.61,y+side*.025),(e*8.86,y+side*.09),(e*9.06,y+side*.17)],.0045+j*.001,.28-j*.045)
  c.path('grime',[(e*8.42,side*.56),(e*8.70,side*.65),(e*9.05,side*.81)],.014,.16)
 for y in [-.085,.085]:
  c.gauss('rust',e*8.61,y,.055,.028,.22)
  c.path('rust',[(e*8.63,y),(e*8.83,y*1.13),(e*9.12,y*1.45)],.005,.23)
roof=np.clip(c.fields['rust']+.40*c.fields['grime'],0,.48)
save(Image.fromarray(np.rint(roof*255).astype('uint8')),S/'SURFV02_roof_foot_runoff.png')
manifest['features']['roof']={'horn_feet_xyz':[[e*8.40,s*.56,3.979] for e in [-1,1] for s in [-1,1]],'searchlight_foot_x':[-8.575,8.575],'projection_xy_extent':[-9.6,9.6,-1.75,1.75],'shader_z_gate':[3.55,4.06]}
del c

# UV film outside the swept field: only a tiny dust fraction is used by the shader.
W=H=2048;u=np.linspace(0,1,W,dtype=np.float32)[None,:];v=np.linspace(1,0,H,dtype=np.float32)[:,None]
x=(u-.31)*1.03;z=(v+.042)*.877;r=np.sqrt(x*x+z*z);ang=np.arctan2(z,x)
sweep=smooth((r-.20)/.055)*smooth((.90-r)/.055)*smooth((ang-math.radians(34))/math.radians(7))*smooth((math.radians(133)-ang)/math.radians(7))
edge=np.minimum(np.minimum(u,1-u),np.minimum(v,1-v));edgefilm=np.exp(-edge/.037)
film=np.clip(.08+.66*(1-sweep)+.35*edgefilm,0,1)
# Faint boundary witness, not an opaque rainbow/painted arc.
film+=.06*np.exp(-((r-.89)/.012)**2);film=np.clip(film,0,1)
save(Image.fromarray(np.rint(film*255).astype('uint8')),S/'SURFV02_windscreen_service_film.png')
manifest['features']['windscreen']={'canonical_outboard_pivot_uv':[.31,-.042],'model_width_m':1.03,'model_height_m':.877,'shader_max_dust_fraction':.025,'interpretation':'Representative service sweep, not a measured motion path; outward side is mirrored in UV helper'}
for p in list(P.glob('v02_body_side*_*.png'))+list(P.glob('v02_nose_*.png'))+[S/'SURFV02_roof_foot_runoff.png',S/'SURFV02_windscreen_service_film.png']:
 manifest['maps'].append({'file':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(S/'SURFV02_SERVICE_WEAR_PROVENANCE.json').write_text(json.dumps(manifest,indent=2))
print('SERVICE_WEAR_MAPS_READY',len(manifest['maps']))
