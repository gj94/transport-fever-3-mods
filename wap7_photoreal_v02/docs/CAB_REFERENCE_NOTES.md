# WAP-7 cab detail: evidence and limits

## Visual references actually inspected

- Factory WAP-7 30221 cab, photographed without seats. The continuous folded grey desk, distinct A/C/D faces, small monochrome display, keypad layout, narrow central pedestal, three foot switches, broad inner windscreen reveals, blinds and ceiling housings informed geometry. [Reference image](https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/5/9/4/1593594/16557400/wap7seatless134598.jpg)
- Real WAP-7 Panel A photograph credited by the source discussion to Khalid Kagzi / Abhishek Nair. The four meters, lamp row, key switch, spring paddles, colored pushbuttons and emergency-stop ring were visually inspected. Readable designators were used rather than fabricated safety legends. [Reference image](https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/6/3/6/1366636/0/detailedviewpanelawap7loco147148.jpg), [source discussion](https://indiarailinfo.com/blog/post/1366636/10)
- WAP-7 machinery-room photograph was inspected to establish the existence of a narrow metal equipment corridor. No complete room was inferred from that single image. The cab module supplies real framed openings and a single hinged door at each end, default closed; it makes no additional exterior body-shell cuts. A separately authored machinery-room module can join those openings. [Reference image](https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/6/3/6/1366636/0/machineroomofawap7227181.jpg)

- Additional real WAP-7 Howrah cab photo verifies the ball-topped throttle and small reverser sharing a slotted plate at the A/C boundary, left-hand brake hardware and red horn knob. The large later DDU visible in this photograph is not copied onto the representative older display arrangement. [Control hardware reference](https://st2.indiarailinfo.com/kjfdsuiemjvcya3/0/4/5/5/4754455/0/261520628022987966304045923174524441853952n85478.jpg), [source discussion](https://m.indiarailinfo.com/blog/post/4754455/0)

These downloaded pictures are working research only. They are not textures, are not embedded in the Blender model, and must not be included in the delivered package.

## Primary equipment corroboration

The Railway Board's 18 November 2024 WTA-554 corrigendum, Annexure E (PDF pages 190–192; printed pages 124–126), identifies conventional WAP7/E70 equipment: A/B/C/D panels, UBA/OHE/TE-BE meters, pressure gauges, DDU, master controller, train and direct brakes, crew fans, desk illumination, foot switches, blinds, floor covering and door/window fittings. Its list is expressly tentative and is not a precise numbered-locomotive layout survey.

[Railway Board document](https://indianrailways.gov.in/railwayboard/rb/corrigendum/1731932781388_Corrig%20No-4_Bid%20Doc%20Ver-1_%20Revised%20Spec_Anned-13_Annex-14.pdf)

[Official minor maintenance schedule](https://rdso.indianrailways.gov.in/works/uploads/File/Revised%20minor%20maint%20schedule%281%29.pdf) also corroborates the relevant equipment classes. The inspected photograph, rather than a contemporary equipment shopping list, determines the visible conventional control layout.

## Exactness boundary

This is a detailed representative conventional WAP-7/E70 cab, not a measured 39002 survey. Hardware dimensions are estimated within the preserved model cavity. The pressure-gauge distribution, chair upholstery and suspension, rear bulkhead furniture, lamp/fan construction and hidden mounting structure are informed visual interpretations. Cab 2 is rotated, not geometrically reflected; left/right handedness is retained. An inactive key switch and recorder cover provide restrained cab-specific differences.

Instrument faces are original artwork. Equipment abbreviations are factual; scale calibration, needle position, dial typography and screen illumination are representative. The screen deliberately contains no fictitious train condition or operational instruction. The controls are static visual assemblies, not working train logic. Rear door hinges can be posed for review; both closed and 90-degree poses preserve rigid dimensions despite the inherited model scale. No new KAVACH, DPWCS or EOTT display was added without unit-specific evidence.

The Flickr image titled “Wap-7 Cab View” by Gaurav Virdi (3654335822) was visually checked and excluded: it is a train-simulator rendering rather than a real cab photograph.

## Integration boundaries

- `components/cab_interiors.py`: `apply(context=None)`
- New objects/materials start with `CABV02_`
- Uses preserved `CAB_A_INTERIOR` / `CAB_B_INTERIOR` parents
- Hides 476 legacy visible furnishing objects reversibly; neither original cab root is changed
- Makes no exterior shell cuts, saved-master writes, camera changes, stage changes or environment changes
- Physical rear door control: `cab_interiors.set_rear_door_angle(1, 80)` (or cab 2). This also tags the object for driver reevaluation. Hinges are `CABV02_1_Rear_door_hinge` / `CABV02_2_Rear_door_hinge`
- Textures are original; the authoring component packs them, while the delivery master uses exact external bytes at relative `//textures/cab/` paths
- Integrated-master render reproducer: `scripts/render_cab_gallery.py`
- Both original driver roots, couplings, bogie/axle and pantograph roots remain untouched
