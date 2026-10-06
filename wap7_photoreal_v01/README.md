# WAP-7 39002 · high-detail visual refinement

A new editable, photo-led refinement of the repository's WAP-7 master, with a consistent **Royapuram 39002 white/vermilion livery**. This package is a modelling/rendering handoff. It does not replace, rebuild or install the existing TF3 pack.

![Trackside hero](previews/01_hero_trackside.png)

[Full side elevation](previews/02_side_elevation.png) · [Cab detail](previews/03_cab_detail.png) · [Bogie detail](previews/04_bogie_detail.png) · [Roof detail](previews/05_roof_detail.png) · [Front portrait](previews/06_front_portrait.png)

## Open the master

Open **WAP7_photoreal_v01.blend** in Blender 4.3.2. The file is internally compressed; all 19 image textures are packed. The compact, self-contained vehicle-only file is about 4.6 MB. It contains editable, individually named components, both furnished cabs and the existing independent pantograph controls. Both collectors are folded in the saved authoring state; no scenery libraries are needed to open the locomotive.

The render script reconstructs the procedural track, ballast, boundary wall, cameras and lighting in a temporary `PRESENTATION_ONLY` collection. That scenery is kept out of the compact authoring master. Never include presentation geometry in a game export. The source is X-longitudinal, Y-lateral, Z-up in metres, with rail tread contact at Z=0.

## What changed

- Curved dark cab roof crowns, a roof searchlight, revised horns and vented cooling modules
- Continuous vermilion belt across the cab corner facets, large condensed railway lettering, numbered markings and representative bilingual opposite-side lettering
- Asymmetric, recessed side filters with actual fine screen geometry, formed rims and fasteners
- Rounded stand-off windscreen cages, separate wipers, transmissive laminated glazing, twin centre headlights and stacked white/red corner markers
- An inherited cab-corner Boolean opening is closed with an exterior welded skin; the furnished interiors are unchanged
- Cast-profile bogie cheeks, axlebox lids and bolts, wheel-web and tread finishes, brake cylinders/rods, dampers, sand pipes and pneumatic lines
- Refined closed-knuckle casting radii, release linkage, jumpers, hoses and rubbed buffer contact faces
- Open pantograph mounting frames, porcelain stacks, shaped copper busbars, mounting plates, roof seams, lifting eyes and panel fasteners
- Packed, original enamel/wear maps and decal art, with differentiated paint, metal, porcelain, glass, rubber, grease, dust and oxidised surfaces
- Actual profiled rails, concrete sleepers, spring clips and individual angular ballast stones in a separate photographic presentation scene

All previews are **Cycles renders of this geometry**. No AI-generated locomotive pictures, photographic backplates or photograph-projected textures are used.

## Preserved authoring contracts

The accepted baseline is `pantograph_v04/WAP7_pantograph_v04.blend` at repository commit `4c4f0be85edbf4468bca22f2d1285fec72343bd5`.

- Original `WAP7_ROOT` and `BODY` transforms and metre scale
- `COUPLING_FRONT` = (+10.2, 0, 1.105) m and `COUPLING_REAR` = (−10.2, 0, 1.105) m; 20.400 m model mating-plane span
- Both bogie yaw pivots, all six axle roll pivots, original parent links and transforms
- `PANTO_FRONT_CTRL` and `PANTO_REAR_CTRL`, their independent `extension` properties, pivot hierarchy and driver expressions
- All **478 objects** in `CAB_INTERIORS_V02`, with unchanged geometry and transforms

The validation script compares **500 protected source objects**. Its checks and an 11-position sample of each pantograph are recorded in [geometry and rig validation](qa/geometry_and_rig_validation.json). The trackside render's trailing contact strip is posed at **5.530 m**, matching the presentation wire to under one micrometre numerically. This is a presentation pose, not a TF3 wire-height configuration.

The folded visible vehicle has about **407,000 evaluated triangles**. Its evaluated envelope is approximately **20.560 × 3.183 × 4.281 m**, including the 24 mm flange projection below Z=0. Its highest point is about **4.257 m above rail**. These evaluated mesh bounds are distinct from the 20.400 m coupling-datum span and nominal prototype dimensions. The inherited small accessory width overrun remains; see the numerical report rather than treating nominal width as a clearance guarantee.

## Identity, references and limits

The primary visual anchor is WAM4ajj's original photograph of **39002 / SR / RPM / ROYAPURAM**, taken on 21 November 2020. [Reference notes and primary dimensional sources](REFERENCES.md) identify the inspected photos and what each supports.

This is a **representative high-detail reconstruction**, not a measured, manufacturer-certified or exact as-built replica of 39002. The opposite-side equipment placement and lettering, shed crest artwork, some roof apparatus, brake arrangement, hoses, service stencils and small hardware are interpreted. The source's simplified pantograph kinematics remain; no new physical actuator simulation or swept collision certification is claimed. The existing coupling planes and closed mating outline are preserved, but cosmetic casting details do not establish coupling safety or curve clearance.

Hidden legacy straight bogie side beams are retained for comparison and must remain excluded from a visual export. The high object count and layered procedural materials are intended for source editing and close-up rendering. Native TF3 conversion, material/texture baking, consolidation, LOD optimisation, collision work, animation binding and a fresh in-game test are separate work. No FBX, game resources or new game-ready release is supplied in this pass. Existing `tools/`, `dist/` and earlier source folders are untouched.

## Reproduce

Requirements: Blender 4.3.2 with Cycles CPU; Python 3 with Pillow and NumPy for original texture generation. The typography generator uses the Linux DejaVu Sans Condensed Bold and Noto Sans Devanagari Bold fonts, with Pillow's Raqm shaping support. The already-generated packed textures allow the Blender master to open without those Python/font dependencies.

From this package directory:

```sh
python scripts/make_textures.py
blender -b -t 8 --python scripts/build_refinement.py -- ../pantograph_v04/WAP7_pantograph_v04.blend
blender -b -t 2 --python scripts/package_master.py
blender -b -t 2 --python scripts/validate_refinement.py -- ../pantograph_v04/WAP7_pantograph_v04.blend
blender -b -t 9 --python scripts/render_previews.py -- hero 512 1920
blender -b -t 9 --python scripts/render_previews.py -- side 256 2200
blender -b -t 9 --python scripts/render_previews.py -- cab,bogie,roof 256 1600
blender -b -t 9 --python scripts/render_previews.py -- front 256 1280
python scripts/finish_package.py
```

Rendering uses AgX, real geometry, CPU path tracing and restrained indirect-firefly clamping. The installed renderer has no OpenImageDenoise backend, so no denoiser is used. The side elevation intentionally hides the presentation geometry and uses a neutral camera background; the other views use the authored track setting. Final per-view dimensions, samples and measured wall times are in `qa/render_*.json`.

Building first creates a complete local render scene; the packaging command then writes the compact vehicle-only master and proves that every vehicle mesh, transform, material graph and packed image is unchanged. `render_previews.py` automatically restores the deterministic setting. Building replaces this package's master and generated maps. Back up manual edits first. The baseline is read-only. Generated previews are re-encoded losslessly only to strip machine-path metadata; their image pixels are not sharpened, retouched or AI-redrawn.

See [visual and technical QA](VISUAL_QA.md), `FILE_MANIFEST.json` and `SHA256SUMS.txt`. This package does not change the repository's existing licensing terms.
