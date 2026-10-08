from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1]
items=[('02_Heritage_forecourt','Heritage / forecourt'),('17_Platform_amenities_service_side','Platform amenities'),('05_Waiting_lounge_local_eevee','Photo-informed waiting lounge'),('04_Booking_hall','Booking hall'),('07_Station_office_local_eevee','Office equipment'),('18_Washbasin_detail_local_eevee','Sanitary fittings'),('15_Frog_closeup','Running rail / frog / checkrail'),('13_Footbridge_detail','Platform links and stair flights'),('11_Maintenance_yard','Mapped service fan'),('12_Full_yard_top','Complete full-scale yard'),('16_Furnished_building_roof_off','Furnished wing cutaway'),('00_Labelled_yard_coverage','Labelled coverage register')]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';title=ImageFont.truetype(bold,35);label=ImageFont.truetype(bold,17);small=ImageFont.truetype(font,17)
W=1800;pad=24;cw=568;ih=340;rh=384;H=140+rh*4+70
sheet=Image.new('RGB',(W,H),'#e9ece8');d=ImageDraw.Draw(sheet)
d.text((pad,25),'TVC / FULL STATION v02',font=title,fill='#173331');d.text((pad,76),'Full-scale mapped campus • furnished reconstructed interiors • no trains',font=small,fill='#4a6060')
for i,(name,caption) in enumerate(items):
 x=pad+(i%3)*(cw+24);y=132+(i//3)*rh
 im=Image.open(R/'renders'/f'{name}.png').convert('RGB');im=ImageOps.contain(im,(cw,ih),method=Image.Resampling.LANCZOS);sheet.paste(im,(x+(cw-im.width)//2,y+(ih-im.height)//2));d.text((x,y+ih+11),caption,font=label,fill='#173331')
d.text((pad,H-50),'Actual Blender renders and labelled map diagram. Hidden plans/fixtures reconstructed; not an as-built survey.',font=small,fill='#4a6060')
sheet.save(R/'TVC_v02_review_contact_sheet.png')
