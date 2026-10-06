# Independent final validation

Audited 6 October 2026, using Blender 4.3.2 in background mode with one thread. The delivered portable validator opened the cleaned master, tested it in memory and exited successfully without saving the model.

- Master: `WAP7_detail_v02.blend`
- SHA256 before and after: `25aa1f264f7dbab9f25e9e2fe27ff2f2e9d6b8ab513133d374717fcff0e24930`
- Detailed evidence: `final_integrated_validation.json`
- Original reference SHA256: `7d6bd12ed30ff6f9837bbbb246fe1b12c700eec89f6edc3697280840664ff86b`

## Result

**Pass for the defined functional-interface and geometry checks.** The 24 baseline interface objects are present. No unapproved transform, parent, driver or extension-property changes were found. The only recorded frame differences are the approved BODY Y-scale restoration from 0.9227166 to 1.0 and the two associated cab-frame refits. Root, coupling, bogie, axle and pantograph functional world frames remain preserved.

Metre units are retained. No non-finite evaluated vertices or objects above the nominal folded-height ceiling were found. Each pantograph was sampled at eleven extensions from 0 to 1: its two actual visible carbon contact faces remained level and coplanar, with zero measured contact-face Z spread and zero measured head-level error at the stored precision. Folded contact height is 4.254758 m; fully extended contact height is 5.652074 m.

## Separate dimensions

| Quantity | Evaluated result | Interpretation |
|---|---:|---|
| Main welded body skin width | 3.152000 m | Restored nominal body width |
| Complete visible accessory width | 3.317727 m | Set by the four cast door handles |
| Lower stair outer limits | Y = ±1.620500 m | Photographically fitted; no longer the width extrema |
| Visible length over closed coupler meshes | 20.562000 m | Nominal class-scale comparison |
| Folded height above rail, Z = 0 | 4.254758 m | Compare with nominal 4.255 m |
| Raw vertical bounds extent | 4.283758 m | Includes wheel flanges down to Z = −0.029 m |
| Total axle longitudinal span | 15.700000 m | Preserved axle datums |
| Each bogie wheelbase | 3.700000 m | Preserved axle datums |
| Coupling-anchor separation | 20.400000 m | Attachment interface, not the visible over-coupler length |

The WAP-7-specific SKEL-4490 GA supports 3152 mm **body** width; other general tables give 3100 mm. Exact accessory stand-offs are not established by the retrieved section. The full mesh must therefore not be described as having an overall width of 3152 mm. Door handles are seated against the revised door assembly; their projection remains representative rather than manufacturing-certified.

## Asset integrity and visual scope

The clean asset contains 12,331 render-visible geometric objects and 2,885,744 evaluated triangles in this audit. These counts describe complexity, not authenticity or quality. All 40 external image datablocks use relative paths, and a post-run filesystem check found every referenced image inside the delivery bundle.

The final 1920 × 1114, 512-sample outdoor hero was inspected from this exact immutable master (raw render SHA256 `d3149fef8427e633465bd1d84369781461f8f116db54e95f80083d449365b4b7`; the metadata-cleanup report records the identical-pixel published PNG). It preserves the corrected body, roof, glazing and two-tread entry silhouette without an obvious new collision from that angle; cages, lamps, HOG brackets, springs and wheel treads resolve cleanly. Its finish represents a cleaner service condition than the heavily weathered 2020 reference photograph. The final orthographic side, CBC, pantograph, wheel/entry, underfloor, cab Panel A, cab overview, machinery-through-door and machinery-cutaway views were also inspected against their matching master provenance. All ten final images are recorded with hashes and scoped observations in `final_gallery_review.json`. Dedicated connection and ladder-yaw tests are supplied elsewhere in the QA folder. Preview inspection is not a full collision proof.

Cab vendor details, hidden machinery construction, exact stair attachment/stand-off, wheel profile and minor hardware remain explicitly representative. The model is not an as-built survey of 39002, a manufacturer-certified reconstruction, or evidence of operational coupling or curve-clearance compatibility. See the delivered reference notes for source-specific limits.
