# NCJ final visual and technical QA

Completed 8 October 2026 using Blender 4.3.2.

## Final render provenance
All four delivered PNGs were rendered directly from the final `NCJ_2010_station.blend` with Cycles, 64 samples, four CPU render threads and denoising disabled (the installed Blender build has no OpenImageDenoise support). No AI image substitution, paint-over or generative retouch was used. The final source and every PNG are bound by SHA-256 in `MANIFEST.json`.

- `01_HERO_FORECOURT.png`, 1600 × 1000: lower left-oblique frontage view. Visually checked the twelve-column rhythm, eleven advertising bays, stepped capitals, rounded fascia, three correctly sized rooftop nameboards, wing relationship, forecourt steps and scale props.
- `02_FRONT_ELEVATION.png`, 1600 × 320: wide architectural strip. Visually checked the main/lower-wing/annex massing relationship and roof/column alignment. It includes the detached-looking covered link as an inferred composition, not a measured plan.
- `03_ENTRANCE_DETAIL.png`, 1600 × 1000: close facade view. Visually checked raised shaped lettering, corbels, recessed/barred windows, replaceable original advertising panels, chipped fascia paint and open ground-level passages. Some facade ends and the rightmost rooftop board are intentionally cropped by this detail camera; the full front is available in the elevation.
- `04_PLATFORM_CONTEXT.png`, 1600 × 1000: low rail-side view. Visually checked the corrected rear roof closure, corrugated canopy, benches, columns, platform edge and rail/sleeper rhythm. **This is a removable contextual module and simplified unseen rear elevation, not a verified view of the real 2010 station.**

The earlier English text transform issue was replaced with shaped mesh outlines; all final rooftop lettering is geometry. An unintended rear roof-edge gap was closed. Vehicle wheel contacts and scenic tree base placement were adjusted before the final four images were rerendered. Earlier previews are superseded by the manifest-bound frames.

## Automated checks
`QA.json` reports successful native-file reopen, metre scale, no nonfinite mesh vertices, packed editable font data and no unpacked image dependencies. The nominal rail-head inner-face gauge is 1.676001 m (floating-point tolerance), and the contextual platform top is 0.760 m above rail top. These are deliberately chosen conventional geometry values, not measurements of NCJ.

`EXPORT_QA.json` validates both GLB 2.0 headers, sizes and embedded buffers, and confirms all three shaped rooftop names are present as mesh nodes. The full-scene export has approximately 0.99 million triangles; the architecture-only export approximately 0.82 million. These are high-detail interchange exports, not claimed to be optimized game LODs. Procedural Blender weathering is not baked to glTF; base PBR materials are retained, and this limitation is documented in the README.

## Reference/fidelity boundary
Both dated 2010 facade photographs were actually inspected before modelling. They support the recognizable street architecture, not exact dimensions, rear layout, platform counts, track plans or current redevelopment. Photo-inferred dimensions and context choices are listed in `dimensions.csv`.

The hanging panels preserve the photographed rhythm but use newly drawn, unbranded artwork; actual jeweller ads, logos, photographs and portraits are not reproduced. Interiors, palm placement, forecourt lengths and the rail-side module are simplified/inferred. Source photo pixels are excluded from the final distributable. Third-party source/font notices do not grant a new licence for user-owned generated work.
