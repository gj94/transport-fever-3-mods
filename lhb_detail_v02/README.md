# LHB detailed coach family v0.2 — work in progress

This isolated revision is being developed from the seven class-specific v0.1 masters. It does not replace earlier sources or the native TF3 pack. All seven class sources and FBX exports have been rebuilt from matching current modules. Geometry, hierarchy, capacity and furnishing-placement checks pass for all seven classes, with separately reported editable-font tessellation warnings. Visual proofs are being reviewed and refined. The first published checkpoint remains explicitly WIP. Do not treat this checkpoint as a final release or runtime-ready asset.

## Prototype and coordinate contract

Selected conventional LHB types: 1A 24 berths, 2A 52 berths, 3A 72 berths, 2S 102 seats, CC 78 seats, SL 80 berths and legacy centre-entry GS 100 seats. The physical capacities are separate from gameplay payload.

Metres; X longitudinal, Y lateral, Z up; railhead Z=0. Body 23.540 m ×3.240 m, crown 4.039 m, floor 1.303 m, bogie centres 14.900 m, wheelbase 2.560 m, new wheel diameter .915 m. CBC mating anchors at X ±12.000 m and Z1.105 m. Authoring geometry, furniture dimensions and equipment placement remain reference-informed interpretations, not manufacturer CAD.

`PAX_*` EMPTY objects are seated character roots, parented to the body, with explicit yaw. `BERTH_*` EMPTY objects are sleeping references only. No seated passenger roots are on upper/middle beds. Native TF3 conversion and runtime validation are outside this source revision.

## Initial changes

- Original rounded through-window wall apertures and separately closed glazing
- Smooth curved roof with recessed HVAC-end wells and raised end structure, rain gutters, HVAC fan blades/grilles, door seals/hinges/steps
- FIAT running gear rebuilt around two 640 mm brake discs per axle, nested coils, profiled frame, calipers, control arms and pipework
- Detailed equipment enclosures, reservoirs, CBC castings and service hoses
- Upholstery piping, stitched panels, folded upper-berth linen, pleated curtains, berth hinges, reading lights, sockets and hollow wire bottle holders
- Detailed end-service fittings, washbasins, lavatory fixtures and electrical control cubicles

## Rebuild

With Blender 4.3.2, run `blender -b -t 2 --python build_lhb_detail.py -- 3A` from this directory. Omit the class argument to rebuild all classes. The builder writes its own models; preserve hand edits before rerunning. `render_lhb_detail.py` creates actual CPU Cycles views. No generated-image previews or vehicle photographs are used. Outdoor review lighting and terrain use the already credited Poly Haven CC0 sky and Dirt material under `../wap7_photoreal_v02/environment`; these are render-only dependencies, not exported vehicle assets.

## Sources and current limits

Reference basis: the railway-authored CAMTECH Maintenance Manual of LHB Coaches, chapter 1 class drawing plates and photographs, and the FIAT bogie maintenance chapter. The official source is [SECR's manual](https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf); when its download failed, the identical titled railway document was read from its [public distribution mirror](https://d2wuvg8krwnvon.cloudfront.net/media/user_space/cf19354d093c/ebook/ebook_1639504169_9471.pdf). Only links are redistributed. Drawing pixels were inspected, including distinct 1A cabin/corridor window rhythms and paired narrow SL windows.

Selected dimensions and capacities also follow the official [NWR 2025 technical data](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf) and [RDSO revised introduction](https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_II_Chapter_I_Introduction_Draft.pdf), with the same explicitly selected 1.303 m floor datum as v0.1. See the preserved earlier [reference ledger](../lhb_family_v01/references.md) for source conflicts and prototype-selection boundaries.

The current geometry passes independent source and FBX round-trip QA in `qa/source_geometry/aggregate.json`; complete visual review and final renders remain pending. Old nested QA directories retain historical checks and are not the current verdict. Previews are current only when the recorded source SHA-256 matches the corresponding current .blend; low-sample proofs and stale images are not final beauty renders. Fine furnishing and equipment fittings are representative approximations. Couplers are static visual models; no claim is made for operational articulation, certification, or compatibility with unrelated new locomotive couplers. Materials use editable procedural shaders; a game exporter must bake or adapt them.

## Review provenance

Each new source stores SHA-256 values for its eight build modules. Every rendered view records the source/image SHA-256, camera, samples, resolution and any temporarily hidden review geometry. The renderer refuses to mark provenance complete if the source changes during rendering. Formation-position boards (H1/A1/B1/D1/C1/S1/GS) and NR regional lettering are representative editable livery details, not a claim to reproduce a real numbered coach or verified train formation.

The CC variant now uses the manual’s 450 mm cushion height above the floor (world Z 1.753 m); its seated-root datum is 1.270 m with the retained 483 mm pose hip offset. This is an authoring pose datum, not a claim that a complete game character has passed runtime floor/foot clearance. Other class cushions retain the separately selected datum.

## Reference-informed furnishing milestone, 7 October 2026

- RMPU units use offset twin condenser fans, actual recessed wells, four mesh intake panels, six maintenance covers and paired electrical/conduit fittings; the underlying roof platform is flat to 1.27 m halfwidth and physically clear of the wells
- 1A uses rounded burgundy upholstery, gathered tied curtains, ivory returns, cabin reading/ceiling lamps, magazine nets, mirrors, switches and supported upper-berth access steps. Ladder stiles, coat-hook bases and magazine-frame mounting now meet the surfaces they attach to
- CC uses 450 mm cushion height, 17° upright backrest geometry, roller blinds, aluminium/glass shelves, individual reading lights, footrests, magazine nets and bracket-mounted bottle cages
- GS banks mirror across the centre doorway, with twenty transverse overhead racks. SL and GS each have thirty class-positioned ceiling fans
- Source module hashes, material conversion and PAX/BERTH contracts are measured independently. Fault-injection tests verify that wrong roots, dimensions, fixtures, fan/rack orientation and disconnected 1A attachments are detected

Fine hardware remains representative original modelling; neither reference fidelity nor source geometry QA constitutes railway certification, production CAD or in-game validation.
