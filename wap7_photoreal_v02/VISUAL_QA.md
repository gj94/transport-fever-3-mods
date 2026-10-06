# Visual QA and release scope

## Frozen source

The gallery is rendered from the delivered `WAP7_detail_v02.blend`, SHA256 `25aa1f264f7dbab9f25e9e2fe27ff2f2e9d6b8ab513133d374717fcff0e24930`. Each completed image has a provenance record identifying the source, producer script, camera/presentation settings, render result and image hash. The render scripts do not save changes back to the master.

All images use Blender 4.3.2 Cycles CPU. Denoising is disabled. Sampling figures below are maxima, rather than a claim that adaptive renders sample every pixel equally. Fine residual sampling grain is visible in some inspection views but does not conceal the modelled features. The hero uses an original geometric track/depot setting with credited CC0 environment lighting and ground material. No AI-generated vehicle image or photographic vehicle backplate is used.

## Final gallery

All ten completed images were inspected at their delivered resolution. No blocking clipping, missing geometry, disconnected roof feed or material regression was identified within the views listed below. The independent reference and surface reviews cover the same frozen source; their scope is visual consistency, not an as-built certification.

| View | Resolution | Maximum samples | Pixel-review scope |
|---|---:|---:|---|
| [Outdoor hero](previews/outdoor_hero.png) | 1920 × 1114 | 512 | Complete silhouette, corrected body width, roof transition, continuous stripe, glazing, entry hardware and restrained finish |
| [Cab Panel A](previews/cab/panel_A.png) | 1600 × 1000 | 256 | Readable switch legends, gauge scales and needles, indicator optics, controls, fasteners and flexible lanyard |
| [Coupler and front connections](previews/probe_coupler_top.png) | 1600 × 1104 | 256 | Curved knuckle and guard relief, separate contact surfaces, pin bore, buffer contact wear, HOG sockets and seated hoses |
| [Machinery corridor](previews/machinery_gallery/machinery_through_door.png) | 1400 × 1008 | 192 | Continuous aisle through the real rear cab doorway; cabinets, upright reservoirs, blowers, ducts, fittings and overhead trays |
| [Wheel and entry detail](previews/details/wheel.png) | 1600 × 1312 | 192 | Wheel forging/tread, axlebox, springs, brake hardware and two chequered lower steps with a separate sill tread |
| [Pantograph](previews/probe_pantograph.png) | 1600 × 1104 | 192 | Collector/frame/spring hierarchy, hinge hardware, ceramic and metal separation, and terminated short flexible braids |
| [Cab overview](previews/cab/overview_A.png) | 1400 × 1050 | 192 | Instrument grouping, desk, throttle, fan guards, blinds, seats, pedals and heater |
| [Underfloor equipment](previews/details/underfloor.png) | 1600 × 832 | 128 | Transformer, compressor/motor equipment, battery case, hangers, pipe unions and cable routing; no duplicate external main reservoirs |
| [Machinery-compartment cutaway](previews/machinery_gallery/machinery_cutaway.png) | 1600 × 867 | 192 | Isolated two-row equipment layout, upright reservoirs and raised cabinet supports |
| [Technical side elevation](previews/probe_side.png) | 2200 × 616 | 128 | Uncropped folded-pantograph side silhouette and complete visible bounds within the 22.4 m orthographic frame |

The corridor image temporarily opens one existing rear cab door. Pantograph presentation poses are set in memory. The machinery-compartment cutaway temporarily hides the exterior and selected roof/lining components, as listed in its provenance; it is an isolated inspection, not a transparent or incomplete saved locomotive. Neutral close-ups use inspection lighting and are distinct from the outdoor hero's modelled setting and daylight.

The final gallery excludes incomplete renders, superseded component probes and earlier underfloor layouts. The uniform-sampling producer used for Panel A is retained as `scripts/render_cab_gallery_uniform.py`; later cab-overview sampling changes are recorded separately.

## Source and fit checks

The [independent validation summary](qa/reference_audit/FINAL_VALIDATION_SUMMARY.md) records the following evaluated model measurements and tests:

- Main body skin width: **3.152000 m**; complete accessory width: **3.317727 m**, set by projecting door handles
- Visible closed-coupler mesh length: **20.562000 m**; preserved coupling-anchor separation: **20.400000 m**
- Folded contact-strip height above the rail datum: **4.254758 m**
- All 24 protected functional interfaces checked within the documented contract; the restored transverse BODY scale and associated cab-frame refits are intentional corrections
- Actual carbon contact faces remain level and coplanar through eleven sampled poses per pantograph

Additional focused checks cover selected entry-ladder/bogie yaw poses, roof-braid connection seating, side-view framing, component integrity and cab-to-machinery doorway clearance. They are scoped geometry checks, not a complete mechanical or swept-volume certification.

The compact delivery was reopened from a fresh copied directory. All 40 relative images resolved, and exact source comparisons preserved 110 materials, one world, image bytes/color spaces/alpha settings, the built-in font and 230 live text objects. See the portability and material/font reports linked from the [package README](README.md).

[Gallery consistency validation](qa/final_gallery_validation.json) checks the ten finished PNG/provenance pairs against the immutable master, their producer scripts, dimensions and image hashes. Run `python scripts/verify_gallery.py .` from this package to repeat that file-level check. Pixel inspection remains a separate visual judgement.

Published PNG files have only ancillary metadata removed. The [metadata-cleanup report](qa/preview_metadata_cleanup.json) records raw-render and published-file hashes and verifies identical compressed image data and decoded pixels. The package checksums describe the published files.

## Interpretation and limits

This is a substantially detailed, editable source reconstruction of a conventional white/orange Royapuram WAP-7, informed by prototype photographs, official layouts and available manufacturer evidence. It is not a measured as-built survey of 39002. Unseen cabinet surfaces, vendor-specific fittings, wheel profiles and some mounting/routing details remain representative. The rendered maintained-service finish is cleaner and more regular than the heavily weathered 2020 reference photograph.

No fresh operational CBC mating, full curve-clearance or in-game compatibility claim follows merely from preserved anchors. The new casting needs a mating/clearance check when paired with the ICF/LHB game assets. This source has not been converted, optimized or tested as a Transport Fever 3 runtime replacement; LODs, game materials, performance and runtime validation remain separate work.
