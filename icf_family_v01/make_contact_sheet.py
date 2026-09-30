"""Create a labeled PDF review sheet from unmodified Blender render files."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSansBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
from PIL import Image
from reportlab.lib.colors import HexColor,Color
P=Path(__file__).resolve().parent
classes=['1A','2A','3A','2S','CC','SL','GS']
W,H=1190.55,841.89  # A3 landscape points
c=canvas.Canvas(str(P/'ICF_family_contact_sheet.pdf'),pagesize=(W,H))
c.setTitle('ICF conventional coach family - source model review')
c.setAuthor('Indian Railways asset-development project')
for page,view,title in [(1,'exterior','Exterior family'),(2,'interior_cutaway','Interior layouts - cutaway review')]:
 c.setFillColor(HexColor('#101923'));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor('#e8edf3'));c.setFont('DejaVuSansBold',28);c.drawString(34,H-49,'ICF | '+title)
 c.setFont('DejaVuSans',12);c.setFillColor(HexColor('#aebecb'));c.drawString(34,H-72,'Full-size source models | 21.337 m body | CBC retrofit visual adaptation | Blender 4.3.2')
 cw,ch=365,218;gapx,gapy=12,18
 for i,v in enumerate(classes):
  col=i%3;row=i//3;x=34+col*(cw+gapx);y=H-108-(row+1)*ch-row*gapy
  c.setFillColor(HexColor('#192633'));c.roundRect(x,y,cw,ch,8,fill=1,stroke=0)
  man=json.loads((P/v/'manifest.json').read_text());p=P/v/'renders'/f'{view}.png';assert p.exists(),p
  c.drawImage(ImageReader(Image.open(p).resize((720,432),Image.Resampling.LANCZOS)),x+7,y+27,width=cw-14,height=179,preserveAspectRatio=True,anchor='c')
  c.setFillColor(HexColor('#f0f4f7'));c.setFont('DejaVuSansBold',14);c.drawString(x+12,y+10,v)
  c.setFont('DejaVuSans',10);c.setFillColor(HexColor('#b7c9d7'));word='berths' if man['physical_berths'] else 'seats';c.drawString(x+55,y+12,f'{man["physical_capacity"]} physical {word} | {man["PAX_marker_count"]} seated roots')
 # Last panel holds honest scope notes.
 x=34+377;y=H-108-3*ch-2*gapy
 c.setFillColor(HexColor('#203545'));c.roundRect(x,y,2*cw+gapx,ch,8,fill=1,stroke=0)
 c.setFillColor(HexColor('#a9dce9'));c.setFont('DejaVuSansBold',16);c.drawString(x+18,y+ch-31,'Distinct interiors, documented representative subtypes')
 lines=[
  '1A: 3 cabins + 3 coupes. 2A: 7 full bays + 4-berth end bay.',
  '3A: 8 eight-berth bays. SL: 9 eight-berth bays.',
  'CC: 3+2 chairs, 73 seats. 2S: 3+3 individual seats, 108 seats.',
  'GS: related 108-seat second-class shell with bench seating.',
  'The cutaway hides roof and near-side wall for review only.',
  'Counts above are physical capacity; gameplay scaling remains separate.',
  'Original geometry. No redistributed photos. No TF3 conversion/runtime claim.'
 ]
 c.setFont('DejaVuSans',12);c.setFillColor(HexColor('#d9e3ea'))
 for j,line in enumerate(lines):c.drawString(x+18,y+ch-59-j*21,line)
 c.setFont('DejaVuSans',9);c.setFillColor(HexColor('#91a8bb'));c.drawString(34,14,'ICF family v0.1 | Reference/QA details in package README and per-variant manifests');c.drawRightString(W-34,14,str(page));c.showPage()
c.save()
print(P/'ICF_family_contact_sheet.pdf')
