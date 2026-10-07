# ICF detail v02 — evidence and modelling decisions

## Selected prototype family

Conventional blue self-generating ICF coaching stock, rather than a uniform generic coach carrying seven labels. Real fleet variants span multiple builders, dates, layouts and retrofits. This source chooses a coherent representative branch and records the choices instead of claiming a numbered-coach replica.

### Dimensions and capacities

The NWR conventional coaching-stock table is the authority for the selected dimensions and capacities: https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf#page=167 . It supports 21.337 m headstock length, 22.297 m over buffers, 14.783 m bogie centres, 2.896 m wheelbase and 0.915 m new wheels. Source floor elevations are 1.313 m AC and 1.278 m non-AC. Selected accommodation is 18/46/64/108/73/72 for 1A/2A/3A/2S/CC/SL.

The ECoR stock table includes a 90/108-seat GS/WGS branch; 108 is selected here. It also records screw-coupled stock: https://eastcoastrail.indianrailways.gov.in/uploads/files/1625144406231-SBP%20WTT%20NEW%202019%20%282%29.pdf . This does not assert every GS coach is 108 seats, or that every ICF coach retains screw coupling.

SCR Knowledge Bank supports the selected 3.245 m body width, all-coil ICF construction and nominal new roof height. NWR rounds body width to 3.250 m; this model uses the SCR/ICF width instead. Its table prints 21.336/22.296 m for headstock/buffer length, a 1 mm difference from the selected NWR figures: https://scr.indianrailways.gov.in/uploads/files/1623859353046-Knowledge%20Bank.pdf . Ventilator housings are above the nominal 4.025 m roof crown; the full model envelope therefore exceeds that crown dimension slightly.

### Class-specific layouts

- 1A: three four-berth cabins and three two-berth coupes, private sliding-door corridor, maroon upholstery, mirrors, controls and compartment tables
- 2A: seven six-berth bays and one four-berth end bay, upper/lower transverse and side berths, gathered privacy curtains and linen cupboard; no middle berth
- 3A: eight eight-berth bays, physically folded middle berths, broad sealed-window generation, supplementary fans and underslung SG/AC equipment
- SL: nine eight-berth bays, folded middle berths, paired barred windows, twin sliding shutters and low roof extractors
- CC: fourteen 3+2 chair rows and one three-chair end row, sealed broad windows, chair fittings, open luggage racks and fans
- 2S: eighteen 3+3 individual low-back rows, barred shutter windows, racks and dense ceiling fans
- GS: selected related 108-seat general subtype, full three-person benches instead of individual chairs, open racks and barred shutters

Those detailed layouts and spacing are original authoring interpretations consistent with class topology and selected capacity, not traced approved arrangement drawings. Toilet allocation is a representative mix of two Indian-style and two Western-style pans. Small sanitary/service equipment placement and exact seat numbering remain illustrative.

## Actual photographs inspected

Pixels were inspected locally during the October 7 refinement pass; photographs are reference only and are not included in the source package or applied as textures.

- Blue sleeper at Modinagar: five slender horizontal bars, dull window metal, twin louvred shutters at several heights, restrained panel irregularity and rounded end corners. https://commons.wikimedia.org/wiki/File:Blue_colored_ICF_Rail_Coaches_in_India_02.jpg
- First-AC four-berth cabin: maroon covered cushions, upper safety guards, fold-down armrests, mirror, individual fittings, table and bottle baskets. https://commons.wikimedia.org/wiki/File:Indian_Railways_AC_first_class_4-berth_cabin.JPG
- Conventional chair-car interior: blue high-backed 3+2 seating, curved shoulders, open metal racks, fans and saloon end doorway. https://findingbeyond.com/app/uploads/2016/07/ac-chair-car.jpg
- Second-sitting interior: individual 3+3 seats, dense fans, barred/shuttered windows and luggage racks. https://irctcnews.in/wp-content/uploads/2018/02/main-qimg-f7df36780e80440c1401f7914893141e-c.jpg
- Older square-window ICF 2A 900514: closely spaced dark square glazing. https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/1/2/7/998127/15695669/20140214123845.jpg
- ICF 3A 071426: broad horizontal sealed windows and substantial underfloor SG/AC equipment. https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/8/2/0/1111820/0/img20140524111136.jpg
- Conventional blue bench compartment and general-coach aisle: facing padded benches, connected standing handholds and overhead metal racks. These support fitting vocabulary, not the selected exact 108-seat spacing. https://st2.indiarailinfo.com/kjfdsuiemjvcya2/0/5/9/2/5360592/0/img202205281849502231601.jpg and https://st.indiarailinfo.com/kjfdsuiemjvcya24/0/5/9/9/3683599/0/capture85212.jpg
- Overhead non-AC roof photograph: low broad rectangular extractors with corner clips; supports visual form only, not exact dimensions. https://cdn.zeebiz.com/hindi/sites/default/files/styles/zeebiz_850x478/public/2022/10/07/104904-train.jpg

## Mechanical detail

The all-coil bogie uses actual wheel profiles, primary coil/dashpot assemblies, secondary spring seats, BSS hangers, side bearers, tread brake blocks/rigging, four-belt non-AC or paired six-belt AC alternator drives and fixed axleboxes. Detailed railway manual links, dimensions and test scope are in `scripts/icf_running_gear.py` and `qa/GEAR_AUDIT.md`.

Closed meshes are welded at micron tolerance, outward normals are checked, and authoring hierarchy separates rotating wheelsets from fixed axleboxes. These are source mesh checks, not certification of suspension travel or dynamic clearance. Screw-coupling hardware is drawn hanging in an uncoupled state. No coupled rake or WAP7 transition arrangement is validated by this package.

## Image and material policy

Every preview comes from the actual Blender scene. No image generation, photographed mesh projection or misleading stock photograph is used as a model preview. Cutaways are labelled and never replace intact source geometry. Procedural finish, small wear and sewing details are original. Blender shaders can use procedural textures that an FBX consumer will not reproduce without a separate bake/material conversion.
