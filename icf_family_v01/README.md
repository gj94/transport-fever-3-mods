# ICF conventional coach family v0.1

Seven editable, original procedural models for the Indian Railways project. These are full-size conventional ICF-derived source assets, not compact Vande Bharat cars and not TF3-native resources.

## Variants

| Folder | Representative subtype | Physical accommodation | Interior built |
|---|---|---:|---|
| `1A` | WGFAC first AC | 18 berths / 18 daytime seated roots | Three four-berth cabins and three two-berth coupes, partitions, parked sliding doors, side corridor, lower/upper berths, folding tables, mirrors, controls and room fans |
| `2A` | WGACCW older square-window AC two-tier | 46 berths / 46 daytime seated roots | Seven six-berth bays plus one four-berth end bay, gathered privacy curtains, linen locker and two berth tiers |
| `3A` | WGACCN AC three-tier | 64 berths / 64 daytime seated roots | Eight wide-window eight-berth bays, middle berths folded vertically as daytime backrests, side berths, ladders and racks |
| `2S` | WGSCZ second-sitting day coach | 108 seats | Eighteen rows of 3+3 individual low-back seats, open luggage racks, fans and barred windows |
| `CC` | WGSCZAC AC chair car | 73 seats | Fourteen rows of 3+2 upholstered high-back chairs plus a three-seat end row, individual armrests, headrest covers and rear tables |
| `SL` | WGSCN non-AC sleeper | 72 berths / 72 daytime seated roots | Nine eight-berth bays, folded middle berths, barred windows, raised shutters, fans and roof ventilators |
| `GS` | GS/WGS 108-seat representative | 108 seats | Related 3+3 second-class layout with three-person benches and open luggage racks |

GS and 2S are deliberately related, not invented as unrelated coach technologies. Reservation designation alone does not determine a different shell. The East Coast Railway stock table lists 90/108-seat GS/WGS and WGSCZ variants; this package selects the 108-seat branch, while the NWR table's GS entry is 90. It does not claim all GS coaches seat 108. This is not the 102-seat Jan Shatabdi 2S variant.

All variants include a finished floor, lining matched to the actual window apertures, physically closed transparent panes, detailed two-axle bogies, tread brakes, suspension coils, underfloor equipment, four simplified furnished toilet compartments, washbasins, electrical cabinets, entrance grab rails/steps and vestibules. AC models represent an older underslung self-generating AC arrangement with internal distribution ducting, not modern roof-mounted package AC. Exact equipment locations and furniture dimensions remain modelling interpretations.

## Open and rebuild

Each class folder contains `ICF_<class>_master.blend`, `ICF_<class>.fbx`, `manifest.json`, `dimensions.json`, `references.md`, `qa/` and `renders/`.

Blender 4.3.2, CPU, two render threads, no denoiser:

```
blender -b -t 2 --python build_icf_family.py -- all
blender -b -t 2 --python validate_icf_family.py
blender -b -t 2 --python validate_straight_join.py
blender -b -t 2 --python render_icf_family.py -- all --stills
```

Or substitute one class, for example `-- 2A`. Omit `--stills` to generate an additional high-sample passenger aisle view for each selected class. The builder is self-contained and generates all geometry and materials; it reads no original pack files and bundles no third-party photography. It writes only inside this package. Back up edits before rebuilding.

## Coordinate and conversion contract

- Metres, X longitudinal, Y lateral, Z up, rail tread datum Z=0; wheel flanges intentionally extend below it
- Each identity root is an EMPTY, named `ICF_<class>_ROOT`; `BODY` and `INTERIOR` are identity EMPTY descendants
- Two `BOGIE_n_PIVOT` empties at X=±7.3915, Z=1.0; two correctly parented `BOGIE_n_AXLE_m_ROTATE_Y` empties per bogie, wheel centres at Z=0.4575
- Full body is 21.337 m long, selected ICF/RCF nominal width 3.245 m; roof crown 4.025 m excluding small seams/vent covers and entrance fittings. Measured complete envelope is in every manifest. The technical tables vary slightly by builder/revision; see references
- Four entrance door groups remain separated. Static doors/cushions do not yet provide game animations
- `COUPLING_FRONT` = (11.1485,0,1.105), `COUPLING_REAR` = (-11.1485,0,1.105); rear yaw=180 degrees, both local +X axes outward

### CBC adaptation

The original conventional ICF fleet commonly used screw coupling with side buffers. This package deliberately uses the project's simplified CBC-retrofit visual arrangement to mate with its locomotives. Side buffers are retained at Y=±0.978 m. The 22.297 m point span and 1.105 m height are project mating datums, not a claim that each historical class used this hardware. Head tips extend 80 mm beyond the mating plane. The opposing eight-point head outlines are complementary and deliberately left unbeveled at the contact profile; beveling the concave interface introduced a tiny real overlap caught and removed during QA. No coupler yaw/compression simulation or prototype retrofit certification is claimed.

### Passenger and berth markers

`PAX_SEATED_nnn` empties are parented to `INTERIOR`, with their actual facing yaw encoded. They are sitting-character roots at lower-cushion top minus **0.483 m**, not cushion-top locators. This follows the latest project stock-character fit check. All markers belong to coherent daytime seating; none put a seated person on an upper berth. Do not apply the old `icf_sleeper` slot-based yaw override to these new variants.

`BERTH_nnn_*` references describe sleeping accommodation, including folded middle berths. They remain in the Blender masters and are explicitly excluded from FBX. They are not additional passenger seats.

Physical seats/berths, daytime roots and commercial game capacity are separate fields. This package leaves game capacity unset. The earlier project's ICF72 was balanced to20 passengers; a later converter should choose consistent per-class scaling and verify fares/costs rather than blindly use physical capacity or count all empties.

### Glazing and material portability

Original glass uses Principled transmission0.92 and alpha0.22; toilet glass uses transmission0.40 and alpha0.58. The Blender FBX roundtrip drops transmission, so the independent validator checks that nonopaque alpha survives. Apply the target game's glass shader during conversion. There are no opaque backing planes behind saloon glazing. Source cloth/floor procedural noise is an authoring detail and is not baked to a redistributed texture atlas.

## Preview and validation scope

`exterior.png` is the intact coach. `interior_cutaway.png` hides the roof and near-side wall only for inspection; the representative `1A/renders/passenger_aisle.png` uses the complete geometry. Every class has exterior and cutaway coverage. The source master stays intact. Some CPU preview sampling noise is visible.

Every class is checked from its saved master and then a separate, empty-scene FBX import for:

- Physical accommodation vs PAX/BERTH counts
- Identity EMPTY root, metre scale, complete mechanical hierarchy, transformed anchors and marker facing
- Every seated pelvis landing on a lower cushion at root+0.483 m
- Rays through every saloon window against opaque body and lining meshes
- Fresh-FBX envelope, absence of cameras/lights and BERTH refs, alpha transparency fallback and fewer than64 materials
- Actual solid two-coach straight joins: every near-end mesh pair is broad-phase checked, positive AABB candidates tested with Blender exact Boolean intersection; only zero-thickness buffer mating contacts remain

Reports are in each `qa/` and aggregated in `qa_summary.json`. These geometric checks do not replace game editor/runtime character-limb fit, boarding, door triggers, curve clearance or coupled-rake testing. No TF3 conversion, LODs, collision proxies, animation rig, texture atlas or new playable ZIP is included. Existing original assets, tools and distribution pack were not modified.

## Two-coach inspection fixture

`qa/two_coach_straight_fixture.blend` and `renders/two_coach_CBC_connection.png` show an actual full-size pair at22.297m pitch. Per-variant and family solid-intersection reports accompany it. The body-end clearance is0.960m. This fixture does not claim dynamic curve/compression clearance.

The Blender masters use native lossless compression. `qa/compressed_master_roundtrip.json` verifies identical reopened geometry and hierarchy signatures. To repeat that check, run `blender -b -t 2 --python compress_masters.py`.
