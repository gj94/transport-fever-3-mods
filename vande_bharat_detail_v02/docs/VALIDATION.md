# Validation scope

Saved full-size sources are the validation inputs. `qa/validation_sources.json` records source SHA-256 values and 153 checks covering metric scale, root/control placement, hierarchy, finite geometry, glazing closure, prototype dimensions and actual detailed chair meshes.

The assembly reports measure evaluated geometry independently from mating datums. The 8/16-car sources contain 530/1,128 physical chairs. Closed-fairing visible lengths are 191.560150/383.560150 m; nominal coupling spans are 192/384 m. These do not certify curves or operational coupling.

- `qa/pantograph_clearance.json`: 101 evaluated poses per TC type, including flexible meshes, against stationary roof/HVAC/VCB/bus surfaces. The output terminal is behind the hinge to clear the guide rod. Internal joint contacts and the pneumatic mechanism are outside this roof-clearance check.
- `qa/panto_micro_*.json`: component attachment/envelope tests, including Hook-deformed shunts and air lines. Component construction checks do not certify OEM kinematics.
- `qa/roof_end_closure.json`: upper end-cap rays closed, central gangway passage clear. Not whole-vehicle watertightness certification.
- `qa/DTC_accessibility_mesh_clearance.json`: actual saved DTC triangles against a1.500m turning footprint and physical WC jamb/corridor boundaries. Minimum obstacle margin is about34mm; doorway1.130m; corridor including WC handle about1.164m. Static WC leaf must move for passage. No accessibility/evacuation certification.
- `qa/portability.json`: all7 cars and2 assemblies opened from an independent directory; relative libraries, images and fonts checked. Model materials are image-free. Render scenery uses separately credited WAP7v02 assets.
- `qa/frozen_source_hashes.json`: exact recovered source freeze, including all7 cars and both assemblies. Earlier renders are excluded from this checkpoint; final gallery will be regenerated against these hashes.

A14:34UTC execution-environment interruption restored an older filesystem snapshot. Three final car files survived byte-identically; the remaining four and both linked assemblies were rebuilt from the surviving modules after restoring the terminal relocation. Geometry, pantograph, roof and accessibility checks were repeated on the recovered bytes. The current branch is a source checkpoint while final rendering resumes.

No TF3 conversion, LOD/performance optimization, material baking, independent per-car controls, dynamic directional lighting, real character fit, curve clearance or in-game validation is included.
