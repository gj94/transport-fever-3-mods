# Final geometric verification

## Current TF3 integration — pack v1.0

The reports below document source geometry. Pack **v1.0 (TF3 revision 14)** includes native conversion with passing resource/Lua, LOD, texture, icon and economics checks. Coach seated-root transforms and introduction-year filters also pass. New coach boarding, full passenger anatomy and curve clearance await a game test. See [current installation, integration and remaining checks](../../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

| Class | Triangles | Materials | PAX roots | BERTH refs (source only) | Fresh FBX | Solid straight join |
|---|---:|---:|---:|---:|---|---|
| 1A | 109,414 | 19 | 18 | 18 | PASS | PASS |
| 2A | 134,038 | 19 | 46 | 46 | PASS | PASS |
| 3A | 116,126 | 18 | 64 | 64 | PASS | PASS |
| 2S | 150,526 | 18 | 108 | 0 | PASS | PASS |
| CC | 161,894 | 19 | 73 | 0 | PASS | PASS |
| SL | 136,864 | 18 | 72 | 72 | PASS | PASS |
| GS | 135,166 | 18 | 108 | 0 | PASS | PASS |

## What passed

- Saved-source and fresh-empty-scene FBX checks for every variant
- Correct identity EMPTY roots, metre geometry and bogie/axle parenting
- Root-parented CBC anchors at +/-11.1485m X, 1.105m Z, opposite outward axes
- All489 daytime passenger roots aligned to lower cushions using0.483m pelvis convention
- All200 sleeping-berth references excluded from FBX passenger data
- No opaque shell/lining ray blockers at any modelled saloon aperture
- Both glass materials retain nonopaque FBX alpha, despite expected lost Principled transmission
- All seven full two-coach straight join tests have0.0m3 positive solid overlap and0.960m body clearance; two zero-thickness buffer contacts are intended

## QA-driven revisions

The initial CBC casting bevel rounded a concave interface into the opposite head. Exact Boolean intersection measured0.56cm3 of overlap. The final complementary8-point head is unbeveled at the contact profile; repeated solid tests returned empty intersection meshes. Entrance treads were also narrowed to give a3.496m complete lateral envelope. These changes are in the builder and the final saved/exported models.

## Not established

This is not game/editor runtime verification. Dynamic coupling, curve/compression clearance, full passenger body/limb fit and boarding remain runtime checks. The separate native conversion supplies LODs, textures/materials and stock-validated automatic economics; coach doors remain static. The .483m root convention is inherited from a validated stock sitting-pelvis reference; full animated bodies have not been fitted to these coaches in TF3.
