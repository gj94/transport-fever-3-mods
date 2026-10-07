# LHB source and portable-export QA

Run the complete verifier from the revision directory:

```sh
blender -b -t 1 --python scripts/verify_lhb_detail.py -- --classes 1A 2A 3A 2S CC SL GS --fbx --output qa/source_geometry/final
```

Omit `--fbx` for source-only inspection. `--skip-topology` is available for fast placement checks, but is not a complete geometry pass. The verifier loads each source and optionally reimports the portable FBX into a clean scene. It never saves a model or uses rendering. It writes JSON reports plus an aggregate and readable summary in the requested output directory.

## What is measured

- Actual evaluated geometry bounds and overall envelope, separately from declared body dimensions
- Body length, width, roof-skin crown and floor top
- Two bogie centres, four axle heights/wheelbases, eight nominal tread rings/back-to-back placement, eight physical brake-disc diameters/widths, and two CBC mating anchors
- Asset ownership, hierarchy, presentation exclusion, finite transforms, scale signs and embedded source module hashes
- Exact class-specific PAX/BERTH counts and berth-type distribution
- Every seated root's actual lower-cushion support, seated height/yaw, unique location and fixed-partition torso sample
- Every lower/upper sleeping reference and folded-middle reference matched to actual furniture
- Floor-to-seat support leg clearances, fixture positions and lavatory counts
- Rays through actual window openings, separately modelled glazing, source transmission and portable alpha fallback
- Every evaluated fabricated mesh's manifold closure, face winding, degenerate faces/edges, finite coordinates, loose vertices and signed volume
- Actual evaluated text vertices, with editable-font seams/degeneracies reported separately
- FBX membership/names, parentage, actual bounds, empty transforms, markers, dimensions and topology
- Manifest/marker values against actual source objects; input file hashes checked for concurrent changes

## Interpretation

`pass_with_warnings` means every strict geometry/contract/export check passed while editable text retained Blender font-tessellation warnings. Font cap seams use coincident vertices; their geometric closure is inspected after a disposable 0.1 µm weld. Some stock glyphs have collinear triangles or touching outline edges. These text warnings are present in both source and FBX and are not exporter damage. Mesh objects used for manufactured components receive strict topology checks without welding away defects.

The 23.540 × 3.240 m contract describes the coach body, not its complete accessory envelope. Handrails and CBC hardware project outward. Wheel flanges project below the railhead, whereas the nominal rolling tread touches Z=0. The 4.039 m crown is the roof skin; seams and non-AC ventilation hoods rise above it.

These tests do not certify engineering accuracy, a manufacturer design, all solid-solid clashes, realistic full-character posing, comfort, accessibility, egress, rendered appearance, procedural material baking or native TF3/runtime compatibility. Separate visual inspection remains necessary. Reference-informed modelling assumptions are not promoted to measured prototype facts.

## Verifier self-test

```sh
blender -b -t 1 --python-exit-code 2 --python scripts/test_verify_lhb_detail.py
```

The self-test changes a disposable scene in memory and proves that the verifier catches an upper-height seated root, a fixture outside the body, an incorrect actual wheelbase even with correct metadata, and a missing passenger root. It never saves the damaged scene.
