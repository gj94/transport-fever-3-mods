# Prototype-length cab component validation

Checked using Blender 4.3.2 on 7 October 2026. This report supersedes the compact working-model cab validation.

Cab source SHA-256: `64c04118dda988e44f2edd8fd524fab46e2b3f1d7ae3f488cf30f45bad16b0d6`

## Automated component checks

- The DTC cab builds successfully in an isolated BODY/asset-collection test context with prototype datums
- Applying the component twice produces identical sorted object names, object count, vertex count and face count
- All input context empties and their parent relationships/transforms remain untouched
- New cab objects are finite-coordinate meshes, parented below BODY and linked to the asset collection
- Calling the component for MC is a no-op; the same early-return branch handles every non-DTC kind
- No external image dependencies are used

The prototype base builder is responsible for deliberately relocating DRIVER_001/002 and CAB_EYE_CAMERA_REFERENCE. Preserving the component's input transforms is distinct from retaining the compact source's transforms.

## Geometry and dimensional checks

- 171 editable cab mesh objects / named assemblies
- 82,128 authored vertices
- 64,553 authored polygon faces
- 143 mesh inscriptions; no external fonts required at display/export time
- Both seat cushions remain 0.500 × 0.535 × 0.096 m, with top Z = 1.750 m
- Main desktop X extent = 9.600–11.370 m; its local length, width and thickness remain unchanged
- Sloping main fascia width = 2.660 m; no longitudinal/ergonomic scaling was applied
- Redrawn demister shelf X extent = 10.970–11.41669 m, depth approximately 0.447 m
- Roller-blind center X = 10.10169 m; length = 2.030 m
- Finished cabin floor datum = 1.320 m; chair-cushion top is 430 mm above it

These are authored component-mesh measurements before downstream triangulation and evaluation of remaining manufactured-edge modifiers on major shaped parts. Fine details are consolidated into named logical assemblies.

## Component visual review

Actual low-sample Cycles close-ups were inspected for the instruments, both chairs and the pedal/mat assembly. The rigid refit retains the mesh lettering, graduated dials, controller grip, microphone construction, sculpted upholstery, stitching, suspension details and floor treads. These are isolated component proofs on a neutral background, not completed in-car gallery images.

## Verification boundary

Standalone checks verify component placement, dimensions, idempotence, parenting, finite geometry and non-DTC behavior. The parent vehicle must additionally verify the final shell, floor, partition, side-door, glazing and other component clearances after integration. The prior compact gallery is not evidence of a completed prototype-length gallery.

The component report supplies separate overall/entrance, driver-eye, instrument, seat/suspension, rear-wall, floor/pedal and ceiling camera recipes. Final high-sample gallery rendering and shell-clearance review are integration checks. No runtime/game export, seated-character animation fit, switch interaction, brake behavior or operational certification is claimed.

See `cab_reference_and_scope.md` for the dimensioned primary layout, drawing-read cab stations, exact source links and approximation disclosures.
