# Research and model interpretation

Accessed 30 September 2026. Source links are references only; original photographs/manual pages are not bundled.

## Primary technical sources

1. North Western Railway, Working Time Table 2025, PDF page167 (printed iii), conventional coaching-stock data: https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf#page=167
   Supports 1A18, 2A46, 3A64, 2S108, CC73, SL72 and a90-seat GS entry. It lists body/headstock length21.337m, buffer length22.297m, bogie spacing14.783m, wheelbase2.896m, wheel diameter.915m and floor heights1.313m AC/1.278m non-AC. Not a cabin/window arrangement drawing.
2. East Coast Railway, Sambalpur Working Time Table2019, PDF page132 (printed101), coaching stock dimensions table: https://eastcoastrail.indianrailways.gov.in/uploads/files/1625144406231-SBP%20WTT%20NEW%202019%20%282%29.pdf
   Confirms selected conventional capacities; explicitly lists GS/WGS and WGSCZ seating as90/108. Records screw couplings for those stock entries. Several dimensions vary by coach/builder; its main ICF/RCF width3.245m matches the pre-existing project source.
3. Railway/RDSO, Maintenance Manual for BG Coaches of ICF Design, shell/bogie chapters: https://rdso.indianrailways.gov.in/works/uploads/File/Maintenance%20Manual%20for%20BG%20Coaches%20of%20ICF%20Design.pdf
   Shell table supports ICF/RCF body21.337m, width3.245m, roof4.025m. Bogie chapter distinguishes AC/non-AC braking arrangements. Full PDF fetch was unavailable in this environment; indexed source passages used for these limited facts. No claim to have traced inaccessible diagrams.
4. RDSO correction slip02(09.2006), AppendixA-2, conventional transportation codes: https://rdso.indianrailways.gov.in/uploads/files/Correction%20Slips%20%281st%20to%2010th%29%20for%20maintenance%20manual%20%20ICF%20BG%20Coaches.pdf
   Distinguishes SG WGFAC/WGACCW/WGACCN/WGSCZAC/WGSCN/GS/WGSCZ from EOG variants.
5. ICF/MD/SPEC-148, issue02 revision04, seats and berths complete: https://icf.indianrailways.gov.in/works/uploads/File/148%20REV-04.pdf
   Supports the equipment categories and makes production drawings authoritative. Exact production seat-installation drawings were not obtained; detailed spacing in this deliverable is intentionally described as a representative interpretation.

## Inspected visual and layout references

- Prateek Karandikar, 2010 first-class four-berth cabin photograph. Actual image pixels inspected: maroon lower/upper upholstery, individual lamp/control fittings, mirror, folding table, window curtains, fans and upper guard rails. https://commons.wikimedia.org/wiki/File:Indian_Railways_AC_first_class_4-berth_cabin.JPG
- Aloke Mukherjee/Trainstuff.in ICF2S layout diagram, viewed through its public Scribd preview. Actual image pixels inspected. Layout1 shows108 seats in3+3 rows, end toilets/washbasins and distinct102-seat Jan Shatabdi alternative. Only layout1 capacity/class family is selected here; exact drawing geometry is not copied. https://www.scribd.com/document/347707293/2S-ICF
- Chair-car interior photo, actual image inspected for high-back blue3+2 seating, open racks, ceiling fans, sealed windows and end saloon doorway. The publishing page is not used as a dimensional authority: https://findingbeyond.com/indian-railway-guide-trains-in-india/ (image https://findingbeyond.com/app/uploads/2016/07/ac-chair-car.jpg)
- Second-sitting interior photo, actual pixels inspected for low-back individual3+3 seats, bar/shutter windows, metal racks and dense ceiling fan arrangement: https://irctcnews.in/2s-second-seating-class-indian-railway/ (image https://irctcnews.in/wp-content/uploads/2018/02/main-qimg-f7df36780e80440c1401f7914893141e-c.jpg)
- Older square-window ICF2A coach900514, photographed February2014. Actual pixels inspected; shows the older closely spaced square sealed-pane rhythm selected for this2A. https://d.indiarailinfo.com/blog/post/998127/6 (image https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/1/2/7/998127/15695669/20140214123845.jpg)
- Later ICF2A exterior, Barauni2017, actual pixels inspected. Its widely spaced horizontal windows demonstrate a different generation, deliberately not silently mixed with the selected older2A sidewall. https://m.indiarailinfo.com/blog/post/2393838
- ICF3A WR071426 exterior, May2014, actual pixels inspected. Wide horizontal sealed panes, underfloor SG/AC equipment and the bay rhythm informed the3A shell refinement to eight broad saloon windows per side. https://m.indiarailinfo.com/blog/post/1111820/2 (image https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/8/2/0/1111820/0/img20140524111136.jpg)
- Existing original ICF sleeper/interior/CBC modelling scripts and assets, read-only repository baseline `baf66cb5c267125ce2c6e82bf03c0fc6986bf786`: https://github.com/gj94/transport-fever-3-mods/tree/baf66cb5c267125ce2c6e82bf03c0fc6986bf786

The first-AC3-cabin/3-coupe arrangement, two-tier7×6+4 arrangement, three-tier8×8 and sleeper9×8 arrangements are explicit representative layout choices consistent with the capacities and established class topology. Seat/berth number placement, windows, partitions and aisle spacing are authoring interpretations, not a selected numbered coach or dimensionally traced approved drawing. GS108 uses the officially listed larger-capacity branch. Do not use these meshes for manufacturing, clearance or safety engineering.

## Project-specific facts, not railway prototype claims

- CBC mating planes and common1.105m height follow the existing pack coupling_v03 convention; this is an adapted hardware choice
- The .483m seated pelvis/root offset follows the current repository stock-character check (`tools/check_vb_character_fit.py` and installation notes). Actual full-body animation fit remains to be tested for each class
- Gameplay speed/year/capacity/cost policy belongs to the existing conversion project and is deliberately not changed here
