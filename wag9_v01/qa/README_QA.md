# WAG-9 validation summary

The package is a modelling handoff. No native TF3 conversion, install, in-game test or performance claim is included.

## Passed source and interchange checks

- Identity sole parentless `WAG9_ROOT`; metre units; no non-identity object scales
- 1,779 meshes, 147,932 triangles, 26 used material slots in the palette
- Two independently yawable bogies and six rollable axle groups at the reference pivots
- Coupling markers remain root-parented, Z=1.105 m, 20.562 m apart, with opposite outward normals
- Visible mesh extent is measured separately: X=±10.321 m; CBC locking knuckle tips protrude 40 mm beyond the mating planes
- Twelve thin glazing meshes have zero non-manifold edges in source and FBX
- Twelve representative window-aperture rays meet no opaque backing, with side-window samples offset from their intentional central sliding mullion
- Eighteen forward cab sightlines (nine per cab) meet no structural obstruction; intentional narrow stone guards and wipers are reported separately
- 101 independent paired pantograph configurations / 202 linkage measurements maintain 1.38 m and 1.15 m arms, level heads and 4.255–5.917 m contact heights
- Minimum conservative vertical clearance to roof sheets is 0.1280248 m
- 202 mesh-surface intersection tests against fixed high roof equipment find no interference. An initial bus-end/crossbrace collision was corrected before delivery
- All three final FBXs fresh-imported in empty Blender scenes. Roots, parent chains, six axles, coupling span, dimensions and glass topology pass
- Nine animation sample frames verify the independent sequence and both endpoints, with `anim_offset=0`
- Blender’s FBX transmission loss is handled by export-only 0.25 alpha glass fallback; all fresh FBX imports verify that fallback. Blender masters keep transmission 0.96 / alpha 1
- `WAG9_motion.fbx.zip` was extracted in memory and the member SHA-256 was verified identical to the original motion FBX

## Reports

- `mesh_rig_validation.json`: source datum, exact bounds, counts, coupling/driver markers and initial linkage sweeps
- `master_aperture_validation.json`: window rays, both cab sightlines, complete 101-configuration sweep and refreshed final counters
- `roof_interference_validation.json`: fixed roof surface-intersection check
- `fbx_fresh_import_validation.json`: each interchange artifact and motion samples
- `motion_archive_validation.json`: lossless archive evidence

## Deliberate limits

No surveyed small-part blueprint accuracy, exact cab instrument functionality, native driver pose fit, native rear-facing driver mapping, native cameras/lights, runtime wire binding, UV atlas, authored LODs or game draw-call performance is asserted. See the main README and references for approximations. The source mesh’s maximum lowered envelope is about 4.25698 m due to rounded roof electrical fittings; the pantograph contact surface is exactly 4.255 m within floating-point tolerance.
