# WAP-7 HOG central machinery room: evidence and scope

## Inspected visual and layout evidence

- Signed RDSO/railway layout drawing SKEL-5051 Alt.2, “WAP7 WITH HOTEL LOAD CONVERTER”. Its complete plan was visually inspected in a publicly readable mirror and both end-to-end equipment rows were traced. It is marked NTS. [Official IRISET compilation](https://iriset.railnet.gov.in/content/CoE/docs/All%20Electrical%20Locos_Kavach%20Fitment_Interface%20drawings.pdf), [publicly readable drawing mirror](https://www.scribd.com/document/776476806/FINAL-KAVACH-DWGS-with-Covering-Letter-to-PUs). The later numbered/magenta Kavach retrofit overlay has deliberately been excluded.
- Actual WAP-7 machinery-corridor photograph credited by its discussion to Sundar Mukherjee / IRFCA. The narrow chequer-plate passage, pale-blue cylindrical blower bodies, folded eccentric ducts, bolted grey equipment cabinets, access doors, overhead fluorescent fixtures, cable trays and cable bundles were inspected. No unit number is visible. [Photo](https://st2.indiarailinfo.com/kjfdsuiemjvcya0/0/6/3/6/1366636/0/machineroomofawap7227181.jpg), [source discussion](https://indiarailinfo.com/blog/post/1366636/10)
- CLW transition-duct specification identifies two machine-room ventilation transitions and two OCU transitions. It distinguishes the machine-room blower's sidewall-filter feed from the oil-cooler roof-filter transition. [CLW primary specification](https://clw.indianrailways.gov.in/uploads/Draft%20Specification%20of%20_Transition%20Duct%20Assembly%281%29.pdf)

The photographs and drawing captures are research references only. None are image textures, embedded in the Blender source, or intended for redistribution with the deliverable.

## Documented external equipment envelopes

- RDSO's 2017 WAP-7 upgrade specification, printed p43, identifies the existing IGBT traction-converter external envelope as 3.000 × 1.100 × 2.087 m (L × W × H), with the existing GTO footprint unchanged. Both TC assemblies are geometrically constrained to that full envelope, including their mounting and lifting hardware. [Primary specification](https://rdso.indianrailways.gov.in/works/uploads/File/17042017_Final_draft_Specification_%20Upgradation_WAP7%281%29.pdf)
- RDSO auxiliary-converter specification 0071, draft Rev.6 (2023), p37, describes the existing BUR1 envelope as 1.160 × 1.020 × 1.860 m and BUR2 as 1.520 × 1.020 × 1.860 m. These are retained as full visual-assembly envelope constraints. The stated 50–100 mm roof clearance is a supplier envelope note, not proof of this particular locomotive's roof and floor geometry. [Primary specification](https://rdso.indianrailways.gov.in/uploads/files/Final%20Draft4_%20Comments%20included_Rev-6%20of%20RDSO%20specification%20No%2071_03-10-23.pdf)
- RDSO 2017/EL/SPEC/0128 Rev.1 §3.1.27 requires an upgraded WAP-7's continuous walkway to be at least 600 mm wide and 1.83 m high. This is an upgrade requirement and useful representative benchmark, not a surveyed 39002 measurement. [Primary specification](https://rdso.indianrailways.gov.in/uploads/files/20250501_128_Rev1_Approved%20Specification_WAP7_To%20be%20uploaded%20on%20RDSO%20website.pdf)

The inner wall clearance remains an inferred fit inside the accepted outer-body geometry. The module accepts `machinery_half_width` from the integration owner. It does not resize or cut the outside of the locomotive.

## Layout interpretation

The drawing's CAB1 (right) is mapped to world +X, CAB2 to world −X. Its upper equipment row is +Y.

From CAB1 toward CAB2, the +Y row contains hotel-load converter 1, C&T1/VCU, auxiliary converter 1, machine-room blower 1, traction converter 1, oil cooling unit 1, pneumatic panel / auxiliary compressor, traction-motor blower 1, and the AR / MR / scavenge group.

The −Y row contains PB / MR / scavenge, traction-motor blower 2, filter block 2, oil cooling unit 2, traction converter 2, machine-room blower 2, auxiliary converter 2, C&T2/VCU, and hotel-load converter 2. The central aisle is continuous.

The HOG plan, rather than the older shared WAG9/WAP7 training plan, governs equipment order. The older HB2 photograph informs cabinet construction only; it does not establish the exact C&T/VCU supplier fitted to 39002.

## Exactness boundary

This is a detailed representative HOG machinery room, not a measured survey of 39002 or an assertion that all vendor hardware is exact to its 2020 condition. Sourced external envelopes and plan sequence are distinguished from inferred door, latch, grille, manifold, pipe and bracket construction. CLW/ES/3/IGBT/0490 Alt.B (October2013), §8.18, provides available HLC installation bays, not measured cabinets: main1.400×1.075×1.750m and equipmentA0.300×1.075×1.750m. The model uses slightly smaller1.380×1.040×1.700m main cases, plus visibly lower0.290×0.700×0.435m companion boxes within those bays. These actual casing dimensions remain inferred. The CAMTECH2022 cabinet photographs support separate enclosure hierarchy, recessed latch hardware and lower ventilation panels, without establishing39002’s vendor. Gauge faces and labels are original geometry, with equipment identities but no invented serial numbers, operating claims or safety instructions.

The [official CR/ZRTI manual](https://cr.indianrailways.gov.in/cris/uploads/files/1383198951757-ABB%20Loco%20in%20English.pdf), printedp59, proves vertical WAP7/WAG9 reservoirs and450L main reservoirs. Its240L sentence concerns WAP5 main reservoirs and is not used for the WAP7 auxiliary vessel. WAP7/WAG9 AR240L is supported separately by the2021 railway-authored WAG9-GM manual, §8.2 printedp58, [public mirror](https://www.scribd.com/document/648240568/WAG-9-GM-open-18-10-21-1). MR diameter0.60m/height1.67m and AR diameter0.46m/height1.60m are capacity/bay-fit estimates, not dimensioned manufacturer drawings. Raised MR cradles bridge the spring pockets.

The running-gear integration supplies existing secondary-spring pocket boxes near x = ±6 ±0.255 m, y = ±1.12 m, top z = 1.915 m. The main HLC cases remain intact and sit on inferred raised installation frames at z = 1.945 m. Open crossmembers bridge above the spring pockets (lowest bridge z = 1.934 m), while frame legs sit outside their lateral footprint. This is a plausible integration allowance, not a manufacturer-certified mounting datum. No arbitrary cabinet-bottom cutouts are used. The center floor plate remains clear of these pockets. TC bases are atz1.545, below the raised aisle floor, so their full2.087m envelope fits below the restored body’s sloping roof shoulders. The machinery floor tread tops atabout1.645; a full600×1830mm central passage is checked against actual geometry. Rear doorway clear height is1.8365m after the separately modeled upper gasket and threshold. The final geometry regression measures640.1mm centered aisle width after all protruding machinery fittings and1.853m overhead clearance; it reports no spring-pocket or exterior-cavity intrusions.

Cabinet doors and equipment are static visual assemblies. This is not a functional high-voltage, pneumatic, traction or cooling simulation. The two actual cab rear doors are provided by the separate cab module; this module supplies only the aligned machinery-side end frames.

## Integration

- Entry point: `components/machinery_room.py`, `apply(context=None)`
- Optional context: `body`, `material_overrides`, `machinery_half_width`
- Integrate after restoring the documented 3152 mm body width (`BODY.scale.y = 1`). This module reads the existing body transform and never changes it. A narrow legacy body can still be inspected, but the600mm passage proof applies to the corrected body.
- Prefix and collection: `MACHV02_`
- No original roots, anchor transforms, external shell, camera, scene lighting or saved master are changed
- Manufacturer envelope metadata, inferred clearances, equipment sequence and build statistics are returned by `apply`
- No external textures or image assets are required
- Integrated-master render reproducer: `scripts/render_machinery_gallery.py`
- Neutral cameras: walkway `(6.88,0,2.96)` toward `(-3.2,0,2.67)`, lens 19.5 mm; reverse walkway `(-6.85,0,2.89)` toward `(3.5,0,2.62)`; cutaway `(12.9,-12.8,10.9)` toward `(0,0,2.20)`
- Cab rear-door controls: `cab_interiors.set_rear_door_angle(1,80)` and corresponding cab 2 call; default remains closed
- Cutaway rendering should hide only the nominated ceiling / trays / side lining in a presentation-only variant, then restore them. The source keeps a complete closed machinery compartment

[HLC primary-authored specification mirror](https://www.scribd.com/document/470581078/131008-001-Final-Specification-of-Hotel-load-IGBT-Alt), [CAMTECH booklet mirror](https://www.scribd.com/document/724195358/Booklet-on-Hotel-Load-Converter-Fitted-on-Electric-Locomotives-RDSO)

## Final QA and physical finishes

The isolated module creates1,228objects and298,708source mesh triangles. Its repeated application is deterministic. All4,175original source objects preserve their mesh-data identities, transforms and parenting. Existing TC/BUR external envelopes are matched to within0.5micrometre numerical tolerance; this numerical fit is not a claim of manufacturing accuracy or exact vendor hardware. See `qa/machinery/validation_report.json` for source hash and checks.

Painted enamel and lettering use a controlled dielectric finish: metallic0, IOR1.5, object-metric1500/m microtexture,40µm bump at0.18strength, roughness variation±0.015. Exposed steel, aluminium, brass and bare chequer plate are conductive. The control-cubicle viewport uses a genuinely transmissive3mm pane over modeled breaker forms; no photographic textures are used.

A final citation-only correction separates the AR240L source from the CR/ZRTI evidence. `validation_execution_module_sha256` records the executed file; current `module_sha256` includes that metadata correction. No geometry or material code changed after the passing regression or final renders.
