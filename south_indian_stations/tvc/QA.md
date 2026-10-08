# TVC QA record

## Research checks
- Actual 4032×3024 November 2022 exterior and platform photos inspected before geometry work.
- Actual 3648×2056 2010 wider photograph inspected for the pavilion return and secondary pavilion.
- Front central upper opening count: 3 observed. Central return upper count: 3 observed in 2010 comparison; dimensions inferred.
- Entire station front/yard count is **not** represented as verified. Hidden gallery configuration is explicitly reconstruction rather than an as-built claim.
- No downloaded reference pixels are used as materials.
- Original trilingual label inspected for shaping and clipping before packing.

## Geometric / technical checks
See machine-readable `qa_geometry.json` for scene object counts, units, images and render settings. All editable model parts are grouped by role. Source uses deterministic random seed 1931 for material/course variations.

Final renders and visual review results are recorded below after render completion.

## Final checks (2026-10-08 UTC)
- Blender 4.3.2 saved and reopened the authoritative `.blend` successfully.
- 6,449 objects, 6,441 meshes, 89,791 source mesh vertices before modifier evaluation.
- Metre unit scale checked at 1.0.
- Rail-head clear inner gauge checked numerically at 1.676 m (floating-point difference below 1e-6 m).
- Original trilingual image is packed; no missing external image files. All loaded DejaVu font datablocks are packed. Built-in Bfont needs no file.
- Four content collections are marked as reusable Asset Browser assets. The canopy study placement offset is its own module centre.
- Central return block positions were checked after reopening; an intermediate collapsed-transform issue was corrected before final rendering.
- Final front opening radii are 0.74 / 1.18 / 0.74 m. This correction is present both in the saved source and the reusable construction recipe. The four front pilasters did not move.
- Real Cycles renders use 64 samples and four threads. Denoising is explicitly disabled because this Blender build lacks OpenImageDenoise support. Minor grain remains in shaded recesses.
- Hero framing was revised to show the whole building; the elevation was reframed to reduce empty foreground.
- Root review accepted the corrected hero facade proportions and framing. Hero, elevation and heritage detail were visually inspected for openings, shutters, frame continuity, clipping and material visibility.

This validates the asset as a reviewable photographic reconstruction and modular study, not measured as-built fidelity. Hidden galleries, exact station plan, complete interior and operational railway clearances remain unverified and are excluded from accuracy claims.

The canopy camera was moved outside the secondary pavilion after a black-frame test exposed the collision. Its final framing also widens the view to include the separate nameboard and canopy structure. No geometry or camera changes were left solely in transient render state; the saved `.blend` and construction recipe retain the fixes.

Final canopy image was visually inspected after rerender: canopy framing, knee braces, columns, baseplates, roof corrugation, bench, paving, rails and the full yellow signboard are visible. A support overlaps part of the board lettering in this structural detail view; the complete unobscured original trilingual graphic is also supplied as its own texture. This is a detached sample, not a claim about exact TVC track position.
