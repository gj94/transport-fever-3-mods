# Validation report

## Current TF3 integration — pack v1.0

The reports below document source geometry. Pack **v1.0 (TF3 revision 14)** includes native conversion with passing resource/Lua, LOD, texture, icon and economics checks. Coach seated-root transforms and introduction-year filters also pass. New coach boarding, full passenger anatomy and curve clearance await a game test. See [current installation, integration and remaining checks](../../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

Final source and all seven fresh FBX imports passed the automated checks in `all_variants_validation.json`.

|Class|Triangles|Used materials|PAX roots|BERTH empties|
|---|---:|---:|---:|---:|
|1A|65,156|10|24|24|
|2A|75,732|10|52|52|
|3A|72,564|10|72|72|
|2S|133,412|9|102|0|
|CC|128,536|9|78|0|
|SL|94,452|10|80|80|
|GS|106,756|9|100|0|

Each geometry envelope is X ±12.080 m, Y ±1.630 m and Z −0.0205 to 4.039 m. The X envelope includes CBC nose projections; wheel flanges extend below railhead. Nominal body width remains 3.240 m, while external window bars/frames explain 3.260 m total. Coupling mating span is 24.000 m. Fresh-FBX/source bounds differ by at most 0.000002 m.

Checks include identity root, metre-scale preserved frames, four child axle pivots and two bogie pivots, outward coupling axes at Z=1.105 m, correct PAX/BODY local transforms, physical berth versus seated-marker counts, roots below cushion by 0.483 m, glazing source transmission and FBX alpha, and no opaque bodyside/door crossing each sampled glass-centre aperture. All closed-volume geometry/panes are manifold; converted text outline meshes are explicitly exempt from the closed-volume check.

Straight paired CBC contact uses the identical unbevelled 8-point extrusion as the ICF CBC-retrofit family. A source/fresh-FBX vertex check verifies the exact outline, then triangle-clipped plan intersection measures zero positive overlap area when the second head is yawed 180 degrees. This is a static head-face check; no curve, yaw, compression or train-dynamics clearance is asserted.

Torso/head AABB probes cover 0.24×0.32 m horizontally and Z=1.90–2.80 m. All roots passed against non-cushion geometry. These are intentionally limited clearance probes, not actual passenger bodies, legs, hands or full animation. Referenced stock hip offset comes from the earlier converter's documented game-skeleton test; this team did not access or run TF3.

Review images are original CPU Cycles renders with no denoising. Cutaways deliberately remove the roof, near wall and upper cushions; geometry remains present in saved masters. Actual interior perspective views keep the complete model. Some low-sample noise remains; renders serve visual construction review rather than photographic quality.

This source report does not test native TF3 resources or gameplay. Subsequent v1.0 resource/LOD/cost checks and representative editor previews are recorded in the integration guide; full animated passenger fit and gameplay await the user's test.

## Actual cross-family evaluated-solid join

`LHB_ICF_straight_join.json` records the complete evaluated LHB 3A / ICF 3A straight pair at centre separation 23.148500 m. Both mating frames coincide at (12, 0, 1.105) m, with opposite outward axes. All 51 LHB and 106 ICF near-join meshes were screened; only the heads had positive AABB overlap, and their exact Boolean positive intersection volume was 0.0 m³. The test records both input hashes and uses a 1e-8 m³ failure threshold. Other LHB variants have the same head outline and anchors; curves, yaw, compression and runtime behavior remain outside scope. Re-run with `blender -b -t 2 --python validate_cross_family_join.py` when the sibling ICF family is present, or append `-- /path/to/ICF_3A_master.blend`.
