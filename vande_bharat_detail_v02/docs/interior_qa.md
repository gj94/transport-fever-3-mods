# Full-size interior geometry QA

Verified in Blender 4.3.2 on 2026-10-07. This replaces the superseded compact-interior report.

## Source hashes

- `interiors.py`: `d5a6d5f23c156c187976596622cdeda1c04ffe684b62de83dbe9c8d145c11c90`
- `interior_layout.py`: `debce65ba3a710fe418534764444176196cbfa86c69fac998bd16fa8368f7a5b`

## Actual seating and clearances

| Car | Actual seat mesh instances | Class | End-wall minimum | Minimum fore/aft mesh gap | Minimum adjacent armrest gap | Armrest-clear aisle |
|---|---:|---|---:|---:|---:|---:|
| DTC | 44 | CC | 0.223 m | 0.319 m | 0.005 m | 0.530 m |
| MC | 78 | CC | 0.030 m | 0.273 m | 0.005 m | 0.530 m |
| MC2 | 78 | CC | 0.030 m | 0.273 m | 0.005 m | 0.530 m |
| TC_CC | 78 | CC | 0.030 m | 0.273 m | 0.005 m | 0.530 m |
| TC_EC | 52 | EC | 0.288 m | 0.509 m | 0.011 m | 0.541 m |
| NDTC_EC | 52 | EC | 0.288 m | 0.509 m | 0.011 m | 0.541 m |
| NDTC_EC2 | 52 | EC | 0.288 m | 0.509 m | 0.011 m | 0.541 m |

These are measurements of actual mesh envelopes, not counts of empty markers. Each car uses one detailed mesh datablock instanced at unit scale, with one object parented to each matching PAX marker. Incomplete end rows, companion seat and empty wheelchair bay were checked. All new objects are parented and collection-owned, all vertex coordinates are finite, PAX transforms remain unchanged by the interior component, and DTC/EC2 repeat applications have stable geometry counts.

The CC end clearance is the minimum including the folded footrest; the main backrest has more clearance. Envelope gaps do not certify passenger-animation poses or dynamic movement.

## DTC service-area geometry

The final curved-room revision was tested against the integrated DTC, with the latest interior regenerated in memory. The test did not overwrite the car file; the integrated builder must rebuild from the final source hashes above.

- One WC in the 2.365 × 1.780 m interpreted envelope
- Actual clear opening between the modeled jambs: **1.1300001 m**
- Door is a static closed visual leaf. Opening measurement applies with that leaf slid aside or removed for inspection; runtime door operation is not provided
- Actual sidewall inner Y: **1.52400005 m**
- Maximum WC/handle lateral projection: **0.35992557 m**
- Remaining corridor including the handle: **1.16407448 m**
- Unoccupied circular turning footprint: **1.500 m diameter**, centre **X −10.620, Y +0.700 m**
- All actual integrated mesh triangles intersecting Z **1.350–2.670 m** were projected and distance-checked against that footprint
- Collision hits: **0**
- Minimum radial obstacle margin: **0.03414716 m**, at the entry-door grab rail
- Curved WC wall margin: **0.06302939 m**
- Rear through-entry X −11.550 to −10.225 m remains open around the turning area

The turning mark is flush floor detail, not a physical object occupying the space. These are geometric visual-layout checks only, **not accessibility certification** or a regulatory compliance claim. A production design would require engineering verification, swept paths and functional door motion.

## Visual QA

A top-down DTC proof was inspected for the 44-seat exceptions, central tables, companion seat, separate wheelchair bay, WC and pantry/crew arrangement. An isolated CC chair proof was inspected for upholstery and seam detail; this exposed excessive broad cloth sheen, which was reduced. Cushion piping and stitches were fitted back onto the original cushion contour. Entry-door inner panels now use the actual 1.320 m floor/pivot datum and match the exterior window opening.

Procedural textile shading requires baking for export formats that do not preserve Blender nodes. All geometry is original; reference photographs are not embedded as textures.

Detailed machine-readable results: `qa/interior_fullscale_component_checks.json` and `qa/DTC_accessibility_mesh_clearance.json`. Full-car/formation QA remains the integrated builder's responsibility.

## Final integration

The complete car builder subsequently rebuilt all seven sources with the corrected900mm emergency-window assemblies and765mm saloon sill. See `../qa/validation_sources.json` for final saved-source hashes and explicit window assertions, and `../qa/DTC_accessibility_mesh_clearance.json` for the saved full-car physical-clearance audit. Component-only reports retain their own tested source hashes.
