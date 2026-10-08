"""Source-grounded vector coverage plan, independent of expensive beauty renders."""
from pathlib import Path
import json,math,html
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'references/local_geometry.json').read_text());cases=json.loads((R/'references/physical_turnout_cases.json').read_text());nodes=json.loads((R/'references/junction_node_positions.json').read_text())
W,H=1800,1120;im=Image.new('RGB',(W,H),'#f7f8fa');D=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="#f7f8fa"/>']
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(t,x,y,size=20,c='#172535',strong=False):
 f=ImageFont.truetype(bold if strong else font,size);D.text((x,y),t,font=f,fill=c);svg.append(f'<text x="{x}" y="{y+size*.86}" fill="{c}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{700 if strong else 400}">{html.escape(t)}</text>')
def poly(ps,c,fill=None,width=1):
 if fill:D.polygon(ps,fill=fill)
 D.line(ps,fill=c,width=max(1,round(width)),joint='curve');svg.append(f'<polyline points="'+ ' '.join(f'{x:.2f},{y:.2f}'for x,y in ps)+f'" fill="{fill or "none"}" stroke="{c}" stroke-width="{width}" stroke-linejoin="round"/>')
def circ(x,y,r,c):D.ellipse((x-r,y-r,x+r,y+r),outline=c,width=2);svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c}" stroke-width="2"/>')
def rect(x,y,w,h,fill,stroke='#ccd3dc'):
 D.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke);svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
text('NAGERCOIL JUNCTION',60,35,38,strong=True);text('Full-scale track and model coverage',60,88,25,c='#3c5269')
text('Mapped centrelines + platform bodies | local metre axes | no rolling stock',60,130,18)
text('Mixed-date source evidence; reconstructed rooms and engineering detail are identified below.',60,160,17,c='#536476')
rect(60,215,1680,440,'#ffffff');scale=.675
T=lambda x,y:(85+(x+1230)*scale,635-(y+10)*scale)
# A clipped source-centreline plan. Only true source nodes are drawn, not a guessed physical-line count.
for w in rows:
 if w['tags'].get('railway')=='platform':
  ps=[T(x+45,y)for x,y in w['local']];poly(ps,'#b17c0b','#ffe7a4',1.3)
for w in rows:
 if w['tags'].get('railway')!='rail':continue
 col='#bf701b'if w['tags'].get('construction')else'#24669a'if w['tags'].get('usage')=='main'else'#596775';pts=w['local']
 for a,b in zip(pts,pts[1:]):
  ax,ay=a[0]+45,a[1];bx,by=b[0]+45,b[1];n=max(1,int(math.hypot(bx-ax,by-ay)/10));run=[]
  for i in range(n+1):
   x=ax+(bx-ax)*i/n;y=ay+(by-ay)*i/n
   if -1220<=x<=1150 and -30<=y<=610:run.append(T(x,y))
   elif len(run)>1:poly(run,col,width=1.4);run=[]
  if len(run)>1:poly(run,col,width=1.4)
# Two explicitly inferred pit-road links used in the3D reconstruction.
railrows=[w for w in rows if w['tags'].get('railway')=='rail']
for wid in ['1302623382','1302623383']:
 w=next(w for w in railrows if w['id']==wid);P=max([(x+45,y)for x,y in [w['local'][0],w['local'][-1]]]);target=(P[0]+90,P[1]);best=None
 for v in railrows:
  if v['id']==wid:continue
  ps=[(x+45,y)for x,y in v['local']]
  for a,b in zip(ps,ps[1:]):
   if max(a[0],b[0])<P[0]+45 or min(a[0],b[0])>P[0]+160:continue
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((target[0]-a[0])*dx+(target[1]-a[1])*dy)/max(1e-9,dx*dx+dy*dy)));q=(a[0]+t*dx,a[1]+t*dy);dist=math.dist(q,target)
   if 0<q[0]-P[0]<170 and abs(q[1]-P[1])<30 and (best is None or dist<best[0]):best=(dist,q)
 if best:
  Q=best[1];ps=[]
  for j in range(61):t=j/60;ease=t*t*(3-2*t);ps.append(T(P[0]+(Q[0]-P[0])*t,P[1]+(Q[1]-P[1])*ease))
  poly(ps,'#ce5c98',width=1.8)
for c in cases['accepted']:
 x,y=T(*c['position']);circ(x,y,3.8,'#008462')
for c in cases['excluded']:
 x,y=T(*nodes[c['node']]);poly([(x,y-4),(x+4,y),(x,y+4),(x-4,y),(x,y-4)],'#9b4b9e',width=1.2)
for label,x,y in [('TVC / Nagercoil Town',-1170,-13),('Tirunelveli',-1110,605),('Kanniyakumari',800,500),('1A terminal bay',-625,100),('PF 1',-260,-18),('PF 2 / 3 island',-285,128),('Maintenance / pit roads',-600,180),('South throat / sidings',255,200)]:
 px,py=T(x,y);text(label,px,py,15,c='#263b51')
# Scale bar, not a claim of survey accuracy.
x,y=T(-1150,55);poly([(x,y),(x+200*scale,y)],'#172535',width=3);text('200 m',x+40,y-26,15)
text('All 34 mapped junctions receive explicit treatment: 20 simple reconstructions + 14 simplified compound crossings.',60,680,19,strong=True)
text('Source ways are segments, not physical track counts. Orange retains a construction tag; commissioning is unverified.',60,712,16,c='#536476')
# Enlarged building coverage inset.
rect(60,765,920,285,'#ffffff');text('ENLARGED INTERIOR COVERAGE — inferred room arrangement',80,781,19,strong=True)
S=lambda x,y:(90+(x+82)*6.35,1022-(y+1)*6.35)
rooms=[('Toilets',-77,-59,1,12.3,'#d9e8f3'),('Offices',-56.3,-39,3.1,12.3,'#e2e0f1'),('Waiting',-35.8,-18.2,-.7,9.1,'#dae9d9'),('Ticket hall',-18,18,0,10,'#ffe3c8'),('Service',22,34,1,10,'#e1e6eb')]
for name,x0,x1,y0,y1,c in rooms:
 a=S(x0,y1);b=S(x1,y0);rect(a[0],a[1],b[0]-a[0],b[1]-a[1],c,'#607183');text(name,a[0]+7,a[1]+10,14,strong=True)
text('Platform access',325,838,16,c='#92610b');poly([S(-78,15),S(35,15)],'#cf941c',width=5)
text('Main entrance / heritage portico',455,1028,15,c='#6a4c34')
# Figure legend and explicit evidence boundary.
text('COVERAGE AND EVIDENCE',1035,782,22,strong=True)
legend=[('#24669a','Mapped main-route centreline'),('#596775','Mapped yard / siding centreline'),('#bf701b','Source retains construction tag'),('#008462','Source-fitted simple turnout'),('#9b4b9e','Simplified compound crossing'),('#b17c0b','Mapped platform footprint'),('#ce5c98','Inferred pit-road connections')]
for i,(c,t)in enumerate(legend):poly([(1038,826+i*30),(1090,826+i*30)],c,width=3);text(t,1110,814+i*30,17)
text('Not an as-built, interlocking or fabrication drawing.',1035,1016,16,c='#6c4e4e')
text('Source: OpenStreetMap contributors, extract 8 Oct 2026 · ODbL · openstreetmap.org/copyright',60,1080,15,c='#536476')
svg.append('</svg>');(R/'references/NCJ_TRACK_COVERAGE_PLAN.svg').write_text('\n'.join(svg));im.save(R/'references/NCJ_TRACK_COVERAGE_PLAN.png')
