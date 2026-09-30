# WAP-7 + ICF sleeper: matched visual CBC coupling v03

## Current TF3 integration — pack v1.0

Native conversion is included in **pack v1.0 (TF3 revision 14)** alongside fourteen ICF/LHB coaches. The installed revision 13 has identical vehicle content; v1.0 installation follows the running play test. Existing locomotive/trainset geometry, gameplay, rigs and the approved private horn are retained. All vehicle store/construction PNGs use straight side views. The modelling and QA below document these original authoring files. See [current installation, integration and remaining checks](../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

Two editable Blender/FBX assets built from the delivered interior-v02 models. The coach is explicitly a **conventional ICF sleeper, CBC-retrofit visualization variant**. The unchanged screw-coupled v02 remains in `../interiors_v02/icf`. This package does not turn all conventional ICF coaches into factory CBC coaches.

## Use these assets

- `wap7/WAP7_coupling_v03.blend` and `.fbx`
- `icf/ICF_sleeper_CBC_retrofit_v03.blend` and `.fbx`
- `paired_straight_QA.blend`: separately staged inspection fixture, not a combined vehicle export
- `paired_connection_closeup.png`, `paired_connection_top.png`, `paired_straight_overview.png`
- `geometry_validation.json` and `fbx_validation.json` in each folder; `paired_alignment_validation.json` for the fixture

## Exact authoring datums (metres)

Both asset origins remain at their original `(0, 0, 0)` with identity root transforms. X is longitudinal, +X is FRONT, Z is up. Scene unit scale is 1.0 m. Original wheel-tread rail datum is Z=0; wheel flanges extend below it and are not the height datum.

| Model | COUPLING_FRONT world XYZ | COUPLING_REAR world XYZ | Span between points |
|---|---|---|---|
| WAP7 | `(10.2000, 0, 1.105)` | `(-10.2000, 0, 1.105)` | 20.4000 m |
| ICF CBC visual variant | `(11.1485, 0, 1.105)` | `(-11.1485, 0, 1.105)` | 22.2970 m |

The empties are direct children of each asset root and are included in FBX. FRONT has identity rotation; REAR has 180 degrees around Z. Each empty's local +X points outward, local +Z points up, and local +Y completes its right-handed frame. To pair them, make the positions coincident and outward X directions opposite.

These are **chosen model mating datums**, not outermost nose limits or certified RDSO pull-face coordinates. The matched closed heads extend 0.080 m past each datum and 0.300 m inward from it. Thus the head-tip extrema are WAP7 X=±10.2800 m (20.5600 m over tips), and ICF X=±11.2285 m (22.4570 m over tips). Do not use these tip spans as the anchor spans. Their opposed stepped profiles interleave 0.160 m in X; the full solid heads do not overlap. Small cast-edge bevel relief remains along their seam. Pivot, supported shank, draft pocket, closed knuckle casting, pin and lock-lifter details provide a continuous visual load path rather than floating head boxes. They are simplified static visual meshes, not an engineered functional H-head mechanism.

At the straight proof pose, WAP7 stays at the original origin and ICF is translated +21.3485 m along X. Measured body-shell/end-wall clearance is approximately **1.160 m**. This preserves a normal intervehicle body gap; reducing the body gap to make couplers meet is not the fix. Anchor coincidence residual is under 0.00001 m. Use the JSON values for measured float precision.

## Heights and side buffers

The cited RDSO dimensional reference lists nominal CBC heights of **1.090 m for locomotive** and **1.105 m for coach** above rail. This package deliberately uses a **common 1.105 m static visual height** for both, including the locomotive head/shank assembly, so the authored mating datums align without changing vehicle origins or running gear. It is an artistic 15 mm locomotive-height normalization relative to that nominal reference, not a claim that both fleet standards are identical.

Side buffers are retained. Their axes are now at world Y=±0.978 m (1.956 m separation), Z=1.105 m. Original WAP7 axes were approximately ±0.941171 m/Z=1.120 m; original ICF axes were ±0.875 m/Z=1.105 m. The original ICF buffer rods ended roughly 69 mm short of their plates; rods are lengthened to enter the plates. The WAP7 buffer face is at |X|=10.110 m; ICF buffer face is at |X|=11.1485 m. The paired buffer-face gap is **90 mm**: CBC heads make the intended visual connection, while the retained buffers are not artificially stretched until they touch. No claim about specific operational buffer compression or curve behavior is made.

CBC-retrofitted ICF coaches and soft side buffers are documented, but this visualization does not identify a surveyed coach serial, approved complete retrofit drawing revision, or certify its detailed buffer/draft-gear configuration. The 22.297 m span uses the source conventional-coach over-buffer dimension as a modeling convention; it is not a verified retrofit CBC mating length. Exact longitudinal nose/plane offsets and simplified casting shapes are artistic choices.

## What was preserved

Source files matched public repository main commit `e346a0e68f25af458eb9ef6ab5c69e94718b51db` byte-for-byte before work; see `source_verification.json`. No intervening main change was found. Original v02 files are untouched.

Only old coupling hardware was replaced and the listed side-buffer objects adjusted. Unrelated object mesh geometry, parent names and world matrices are checked unchanged, including body, interiors, bogies and axle pivots. The existing origin, metre units, bogie/axle hierarchy and all interior content remain. New CBC pivots and connection empties are root-parented to avoid inheriting the locomotive BODY's preexisting non-uniform width scale. Original root dimension metadata is retained with a warning; the new `length_between_coupling_points_m` is the v03 anchor span.

Fresh FBX reimport checks both root-parented named empties, frames, origin/root matrices, and all bogie/axle names, parent relationships and world transforms within 0.00001 m/matrix-element tolerance. FBX excludes presentation lights/cameras. Original WAP7 instrument textures are packed/embedded.

## User's TF3 integration

The user reports interior v02 is working in TF3. This v03 package has been checked in Blender and by fresh FBX import, **not run in TF3**. The user handles vehicle spacing/configuration, straight-track and curve testing. No runtime coupling binding, automatic yaw, dynamic compression or animation is implemented. The named pivots/empties are authoring guides and do not automatically configure TF3. The static straight fixture proves its stated pose only.

## Rebuild

Keep this directory next to the repository's `interiors_v02`, or supply that source directory explicitly:

    blender -b -t 2 --python build_coupling.py
    blender -b -t 2 --python verify_and_render.py
    blender -b -t 2 --python verify_mesh_dimensions.py

Alternative input:

    blender -b -t 2 --python build_coupling.py -- /path/to/interiors_v02

Blender 4.3.2, CPU two threads, 32 samples, denoising off. The build does not change source files. The render script creates a separate paired fixture, leaving individual asset origins untouched.

## Primary references and limits

- [RDSO web drawings list](https://rdso.indianrailways.gov.in/works/uploads/File/List%20of%20web%20drawings%202017.pdf): CG-17002 retrofit CBC headstock and CG-17013–16 ICF GSCN entries
- [Ministry of Railways retrofit announcement](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1492669&lang=2&reg=48): 24 retrofitted ICF coaches in Manduadih–Rameswaram service from 23 April 2017
- [RDSO CG-03 Rev04, Annexure B](https://rdso.indianrailways.gov.in/uploads/files/Rev%2004%20dt%2001%2002%2023.pdf): locomotive/coach nominal CBC heights 1.090/1.105 m
- [Indian Railways Schedule of Dimensions, reproduced in RDSO TRT specification](https://rdso.indianrailways.gov.in/uploads/files/Final%20Draft%20spec%20TRT%20with%20annxures%20dt%2025-06-2021.pdf#page=76): vehicle buffer clauses 12–14, 1.956 m transverse centre separation; locomotive clauses also at PDF page 82
- [IRIMEE, Buffers fitment in coaches](https://rskr.irimee.in/buffers-fitment-coaches-0): soft side buffers with CBC-fitted ICF coaches
- [East Coast Railway WTT 2019](https://eastcoastrail.indianrailways.gov.in/uploads/files/1625144406231-SBP%20WTT%20NEW%202019%20%282%29.pdf): conventional WGSCN over-buffer length 22.297 m

This is an asset-art coupling correction supported by prototype context, not manufacturing data or a certified fleet configuration.
