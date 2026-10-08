# CC furnishing refinement: evidence and integration

## Reference

Railway-authored CAMTECH *Maintenance Manual of LHB Coaches*, chapter 1, sections 1.6, 1.7 and 1.9; PDF pages 34–35 (printed labels are 35 and 36). [Official SECR manual](https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf#page=34). The already recorded public distribution mirror supplied the local copy when the official download failed. Both full pages were visually inspected, including the rack cross-section/reading-light photographs and the front/rear seat photographs. No image pixels are incorporated in the model.

Source-supported facts applied only to the selected 78-seat CC:

- Roller blinds replace curtains; manual full-open, half-open and full-closed positions; wire tension holds the fabric taut
- Luggage shelves use anodised aluminium extrusion and tempered safety glass, with powder-coated cast aluminium side cheeks
- Individual reading lights, switches/focus adjustment and a polycarbonate wiring cover are in the outer rack extrusion; movable coat hooks attach to the rack
- Seat cushion height is 450 mm above the floor; clear width between armrests is 420 mm
- Upright backrest angle is 17°; the stated rest position is 37°, recorded as reference metadata but not activated
- The chair inventory includes a welded seat frame, upholstered cushion/backrest, armrests, folding table with bottle holder, footrest and magazine net

Source photographs support the broad shelf and open cast-cheek profile, a shallow underside lamp strip, stowed rear table, wire magazine net and associated rear bottle cage. Hardware dimensions, shelf segmentation, blind placement within the existing shell and small fabrication details remain representative original geometry, not manufacturer CAD. No inference is applied to non-AC 2S seating.

## Integration

Include `lhb_chair_detail.py` in the builder's source hashes. Reset `TOP = 1.840` before each variant's `common(k,c)` to prevent CC state leaking into subsequent builds.

Call `lhb_chair_detail.refine_core(globals(), k, c)` immediately after the class furniture call, before `lhb_finish_detail.refine`. Call `lhb_chair_detail.refine_finish(globals(), k, c)` immediately after `lhb_finish_detail.refine` and before `lhb_soft_finish.apply`. Both hooks return without altering anything when the class is not CC; both guard against repeated application.

For CC the core hook sets `TOP = FLOOR + .450 = 1.753`. All 78 PAX names, parents, X/Y positions and yaws are preserved; marker Z becomes `1.753 - .483 = 1.270`. Cushions remain level, centred local meshes. The pedestal is shortened from its upper end so it still meets the 1.303 m floor. The cushion maximum remains 1.753 m after the soft-finish crown; the inherited raised centre-sewn patches are removed because their tops exceeded that datum.

The shared soft-finish helper must use unrotated local mesh extents when refining tilted chair backs, not `ob.dimensions`, which is a rotated bounding box. Shared finish's axis-aligned back seams, lumbar blocks, tray hardware and headrest embroidery are removed for CC; the sourced rear hardware follows the 17° seat frame. General soft upholstery work remains exclusively in `lhb_soft_finish.py`.

Curtain rail positions are captured directly from the constructed shell, then the CC rails and rod shelves are removed before the common curtain generator can run. Blinds default to 22 full-open, six half-open and two full-closed examples. The caller may override all blinds with `CC_BLIND_STATE`, or individual sorted-window indices with the dictionary `CC_BLIND_STATES`. Valid strings are `full_open`, `half_open`, and `full_closed`. Full-open fabric is wound inside the closed roller housing, avoiding zero-height meshes.

The new glass shelves reuse the builder's transmitting glass material, so its existing source-transmission/FBX-alpha conversion also applies to them. All rods are capped; fabric has explicit thickness; the cast-cheek openings are real closed ring extrusions. No boolean or external mesh assets are required.

## Verification

`../scripts/test_lhb_chair_detail.py` runs only against module copies in a disposable `LHB_CC_TEST_DIR` (default `lhb-cc-test` under the system temporary directory). It builds a CC scene, verifies names/positions/counts, the actual cushion/armrest/pedestal geometry, all three blind states, all 78 per-seat fittings, exact non-CC no-op behavior, re-entry behavior and both base/evaluated manifold positive-volume meshes for all affected components. A successful run saves only the isolated test model/export and JSON report.

The general verifier's PAX transform check must expect Z 1.270 for CC and 1.357 for the other classes. Native TF3 conversion, animated recline/blinds and full-character runtime clearance remain untested and outside this source refinement.

## Focused test result

The current isolated Blender 4.3.2 build passed all 15 checks, including the thin textile and bounded chair-shoulder refinement. All affected base meshes and evaluated meshes were closed/manifold with positive volume; no component topology errors were reported. The 78 seat-root contracts, measured 450 mm cushion height and 420 mm clear armrest width passed. Module SHA-256: `29c0649b3c0b7df1a45d0d94bd986cacbcd4c258a878aebcf4643c19dce178c6`. Current results are in `../qa/cc_furnishing_checks.json`; these are focused furniture tests, not the complete family or runtime certification.

## Textile refinement review

The white antimacassar is modelled as a closed 1.2 mm woven-cotton sheet draped over the reclined chair crown, with shallow gravity-led wrinkles and a sewn perimeter hem. It replaces the former thick head pad proxy. Thickness and stitch dimensions are representative modelling choices, not manufacturer dimensions. The blue chair shoulders use a bounded 25-ring profile while preserving their prior maximum dimensions and the 450 mm cushion datum. All component checks and actual-Cycles visual review must be repeated against the rebuilt source before release.
