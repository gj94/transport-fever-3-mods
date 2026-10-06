# Visual and technical QA

## Verified

- Opened, modified, rendered and re-opened with Blender 4.3.2
- All 500 protected source objects pass the baseline comparison: root/metre scale, original empties, parent links, pantograph driver expressions and all 478 furnished-cab objects
- Coupling empties remain at X ±10.2 m, Y 0, Z 1.105 m; all bogie/axle transforms remain unchanged
- Both live pantographs pass 11 sampled extension values; the head stays level within floating-point tolerance. Render contact height is 5.530 m with sub-micrometre numerical error
- Evaluated visible vehicle geometry contains no non-finite coordinates
- All 19 image maps are packed. Delivered image paths are relative to `textures/`
- Packaging removes scenery only. Fresh-open comparison proves identical vehicle topology, coordinates, transforms, material graphs and packed image bytes
- Preview generation uses actual Blender geometry and Cycles CPU. No image generation, photographic backplate or photo texture projection is involved
- Lossless PNG metadata cleanup verifies that every decoded preview pixel is unchanged

See `qa/geometry_and_rig_validation.json`, `qa/packaging_validation.json`, `qa/render_*.json` and `qa/preview_pixel_validation.json` for machine-readable scope and measurements.

## Visual iteration

The asset was compared against the original 39002 reference and reviewed through repeated real Cycles drafts. Corrections included:

1. Replacing duplicated decorative side intakes with asymmetric screened filters
2. Rebuilding the dark curved cab crown, guarded windows, stacked markers, bogie cheek profiles and roof fittings
3. Removing an inherited cab-corner Boolean leak, diagnosed by camera-ray intersection with the rear bulkhead
4. Extending the red belt across the complete cab bevel, without an intervening white gap
5. Replacing the original solid pantograph plinth with an open fabricated frame while retaining the live mechanism
6. Reducing coarse roof/buffer bump response; separating enamel, cast steel, scuffed contact steel, rubber and glazed porcelain
7. Correcting collector dependency updates so the raised contact strip meets the authored wire
8. Tapering and scattering the ballast boundary, removing distracting crude tree geometry from the final composition, and using a subdued boundary wall
9. Adjusting the hero toward a long-lens front three-quarter photograph, with low reflected fill for the undergear
10. Providing a clean orthographic full-vehicle elevation separately from the trackside and close-up views

Final images are inspected at their delivered resolution. Measured per-view samples, dimensions and rendering times are retained; rendering time varies by hardware.

## Not established by these checks

- An exact as-built survey or manufacturer-certified reconstruction of 39002
- Correct placement of every hidden-side fitting, service stencil, brake part or roof accessory
- Physical pantograph actuator simulation or a certified swept-clearance test of the added cosmetic details
- Dynamic coupling clearance, operating clearances or engineering suitability
- Native TF3 conversion, baked game textures, optimised LODs, runtime animations or a new in-game play test

The existing game pack and its conversion/install tools were not changed. This is a high-detail source refinement with explicitly documented approximations.
