# Validation scope

Saved full-size sources are the validation inputs. `qa/validation_sources.json` records source SHA-256 values and 153 checks covering metric scale, root/control placement, hierarchy, finite geometry, glazing closure, prototype dimensions and actual detailed chair meshes.

The assembly reports measure evaluated geometry independently from mating datums. The 8/16-car sources contain 530/1,128 physical chairs. Closed-fairing visible lengths are 191.560150/383.560150 m; nominal coupling spans are 192/384 m. These do not certify curves or operational coupling.

- `qa/pantograph_clearance.json`: 101 evaluated poses per TC type, including flexible meshes, against stationary roof/HVAC/VCB/bus surfaces. The output terminal is behind the hinge to clear the guide rod. Internal joint contacts and the pneumatic mechanism are outside this roof-clearance check.
- `qa/panto_micro_*.json`: component attachment/envelope tests, including Hook-deformed shunts and air lines. Component construction checks do not certify OEM kinematics.
- `qa/roof_end_closure.json`: upper end-cap rays closed, central gangway passage clear. Not whole-vehicle watertightness certification.
- `qa/DTC_accessibility_mesh_clearance.json`: actual saved DTC triangles against a1.500m turning footprint and physical WC jamb/corridor boundaries. Minimum obstacle margin is about34mm; doorway1.130m; corridor including WC handle about1.164m. Static WC leaf must move for passage. No accessibility/evacuation certification.
- `qa/portability.json`: all seven cars and2 assemblies opened from an independent directory; relative libraries, images and fonts checked. Model materials are image-free. Render scenery uses separately credited WAP7 v02 assets.
- `qa/frozen_source_hashes.json`: final source freeze, including all seven cars and both assemblies. Each `qa/render_*.json` report identifies the exact source and image; `scripts/validate_release.py` requires every final frame to match current source bytes.


No TF3 conversion, LOD/performance optimization, material baking, independent per-car controls, dynamic directional lighting, real character fit, curve clearance or in-game validation is included.

## Reviewed EC upholstery refinement

`qa/ec_upholstery_refinement.json` records the three EC source changes. Only the four cloth solids per linked chair were refined. All original per-part and whole-chair envelopes match, every non-cloth hardware vertex/face stamp is unchanged, and all passenger/control transforms remain intact. EC armrest-clear aisle remains0.541m. Cushion/back/wing surface points shift within their original bounds by at most about16.4mm; this improves surface curvature without a relayout or material-style change. The other four car files remain byte-identical to the pre-refinement checkpoint.

The earlier complete WIP checkpoint remains available at commit5322f1ca301c0d8832eccd84c779904f8e4f00f3. Final source hashes, regenerated preview inputs, fresh-directory portability and PNG pixel-preserving metadata cleanup are checked before release.

`qa/ec_rebuild_smoke.json` independently rebuilds the current TC_EC generator and verifies an identical chair vertex/topology/shading/material-slot stamp against the saved refined source. All17 final preview files must pass exact current-source hashes before the release manifest is written.
