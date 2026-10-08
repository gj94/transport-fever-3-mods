from pathlib import Path
import json,html,math
P=Path(__file__).resolve().parent
W=json.loads((P/'references'/'osm_rail.json').read_text())
def xy(p):
 e=(p[0]-76.29105)*109640;n=(p[1]-9.9693)*111195;return(n*.981-e*.194,e*.981+n*.194+14)
def px(p):return ((p[0]+530)*1.15+50,480-(p[1]-50)*1.65)
a=['<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="780" viewBox="0 0 1700 780"><rect width="1700" height="780" fill="#f5f3ed"/>','<style>text{font-family:DejaVu Sans,Arial;fill:#173031}.title{font-size:30px;font-weight:bold}.label{font-size:19px}.small{font-size:15px}</style>','<text x="55" y="55" class="title">ERNAKULAM JUNCTION · FULL STATION COVERAGE</text>','<text x="55" y="87" class="label">Six platform faces • connected mapped running lines, crossovers and sidings • no rolling stock</text>']
for w in W:
 if w['tags'].get('railway')=='platform':
  pts=[px(xy(p)) for p in w['points']];a.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'" fill="#e6b551" stroke="#b36b32" stroke-width="1.4"/>')
for w in W:
 if w['tags'].get('railway')!='rail':continue
 pts=[]
 for p in w['points']:
  q=xy(p)
  if -510<q[0]<850 and -30<q[1]<155:pts.append(px(q))
  else:
   if len(pts)>1:a.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'" fill="none" stroke="#465957" stroke-width="1.7"/>')
   pts=[]
 if len(pts)>1:a.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'" fill="none" stroke="#465957" stroke-width="1.7"/>')
for x in [-60,100]:
 q=px((x,12));r=px((x,106));a.append(f'<line x1="{q[0]}" y1="{q[1]}" x2="{r[0]}" y2="{r[1]}" stroke="#397b9a" stroke-width="7"/>')
for x,y,w,h in [(3,1,72,14),(0,111,62,18.4),(520,168,30,14)]:
 q=px((x-w/2,y+h/2));a.append(f'<rect x="{q[0]}" y="{q[1]}" width="{w*1.15}" height="{h*1.65}" fill="#326a8b"/>')
def label(text,pt,at):
 q=px(pt);a.append(f'<line x1="{q[0]}" y1="{q[1]}" x2="{at[0]}" y2="{at[1]-7}" stroke="#8b9896" stroke-width="1.2"/><circle cx="{q[0]}" cy="{q[1]}" r="3" fill="#173031"/><text x="{at[0]+5}" y="{at[1]}" class="label">{html.escape(text)}</text>')
for t,p,at in [('PF1 · west side', (275,19),(990,650)),('PF2/3 · island',(290,48),(1180,585)),('PF4/5 · island',(290,68),(1200,210)),('PF6 · staggered east side',(-170,95),(130,205)),('West hall + offices + toilets',(0,1),(470,685)),('East booking + waiting hall',(0,111),(520,180)),('Covered footbridges',(-60,70),(370,265)),('North throat + service sidings',(555,89),(1320,285)),('South approach + crossovers',(-360,45),(60,615)),('P-way workshop · reconstructed',(520,168),(1160,130))]:label(t,p,at)
a+=['<text x="55" y="725" class="small">Architectural baseline: inspected 2017 photographs. Yard: current OSM-derived mixed-date reconstruction, not a surveyed 2017 as-built.</text>','<text x="55" y="749" class="small">© OpenStreetMap contributors · ODbL 1.0 · metre-scale local station coordinates. North runs approximately to the right.</text>']
q=px((-420,-60));a.append(f'<line x1="{q[0]}" y1="{q[1]}" x2="{q[0]+115}" y2="{q[1]}" stroke="#173031" stroke-width="4"/><text x="{q[0]}" y="{q[1]+23}" class="small">100m</text>');a.append('</svg>');(P/'renders'/'12_Labelled_coverage_plan.svg').write_text('\n'.join(a))
# Native PNG rendition of our vector diagram, without external dependencies.
from PIL import Image,ImageDraw,ImageFont
import xml.etree.ElementTree as ET
im=Image.new('RGB',(1700,780),'#f5f3ed');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for e in ET.fromstring('\n'.join(a)):
 tag=e.tag.split('}')[-1];q=e.attrib;fill=q.get('fill','#173031');stroke=q.get('stroke');sw=max(1,round(float(q.get('stroke-width','1'))))
 if tag=='rect':
  x=float(q.get('x',0));y=float(q.get('y',0));w=float(q['width']);h=float(q['height']);d.rectangle((x,y,x+w,y+h),fill=fill)
 elif tag in ['polygon','polyline']:
  pts=[tuple(map(float,p.split(','))) for p in q['points'].split()]
  if tag=='polygon':d.polygon(pts,fill=fill)
  if stroke:d.line(pts+(pts[:1] if tag=='polygon' else []),fill=stroke,width=sw)
 elif tag=='line':d.line(tuple(float(q[k]) for k in ['x1','y1','x2','y2']),fill=stroke,width=sw)
 elif tag=='circle':
  x=float(q['cx']);y=float(q['cy']);r=float(q['r']);d.ellipse((x-r,y-r,x+r,y+r),fill=fill)
 elif tag=='text':
  size={'title':30,'label':19,'small':15}.get(q.get('class'),19);f=ImageFont.truetype(font,size);d.text((float(q['x']),float(q['y'])-size),e.text or '',font=f,fill='#173031')
im.save(P/'renders'/'12_Labelled_coverage_plan.png')
