# WAP-7 surface treatment, v02

## What changed

- Opaque locomotive enamel, rubber, dust, oxide and grease use dielectric response. Exposed metal remains conductive. Cast hardware blends physically different exposed-metal and dry-film regions instead of making all surfaces partly metallic.
- Body paint keeps flat, quiet colour at normal viewing distances. Original 6144 × 1536 side maps put runoff beneath roof gutters, around the known filter arrangement and door joints, plus a thin lower-sill dust gradient. The nose has its own original 2048 × 2048 map.
- Microscopic enamel finish is measured in metres. Enamel bump height is 40 micrometres before the strength multiplier, plus a very low-amplitude broad pressed-sheet normal. There is no silhouette displacement, heavy concrete texture or generic centimetre-size noise.
- Wheel tread is a separate polished-steel role, with fine circumferential machining/scoring lines and no rust on the contact band. The rest of the wheel is owned by the running-gear module.
- Buffer faces use original 2048 × 2048, 16-bit wear, roughness and grease masks. Wear is concentrated in an irregular annulus; the centre has a dark contact grease smear. This material requires its dedicated UV layer.
- Glass uses full physical transmission, IOR 1.52, restrained tint and low roughness. It requires real pane thickness and outward-facing normals. It is not opaque blue paint or an alpha-transparent plane.

These are physically plausible artistic parameters, not measurements from a specific depot paint sample or a claim of unit-exact service wear.

## Integration contract

`components/materials.py` remains the stable entry point. `apply(context=None)` preserves the 24 role keys expected by exterior geometry; `setup()` builds the library without assigning it. The implementation is in `components/surface_materials.py`.

Optional added roles:

- `tread`: Y-axle wheel-tread steel, intended only for the actual running/contact surface
- `buffer`: scuffed buffer contact face. Call `assign_buffer_uv(object, axis='X')` for a buffer whose face normal is X; assign the material only to its contact-face polygons

All new material datablocks use the `SURFV02_` prefix. Construction-paint coordinate nodes reference `WAP7_ROOT`, so the wear stays with the locomotive during root translation/rotation. Hardware microfinish uses each object’s metric local coordinates, avoiding texture swimming on animated pantographs, wheels and other moving parts. Shared pre-existing materials are not edited. Cab and running-gear owner objects/collections are excluded from legacy slot replacement, including `CABV02_`, `CAB_INTERIORS_V02`, and `V02_RG_`.

Running-gear material-role overrides:

`{'tread': M['tread'], 'rubber': M['rubber'], 'grease': M['grease']}`

Interior finishes, gauges and displays remain owned by the cab module.

## Rebuild and validation

1. Run `python scripts/make_service_wear_maps.py` for the current construction-directed body/nose/roof/windscreen maps
2. Run `python scripts/make_surface_detail_maps.py` for the buffer masks
3. Run `blender -b -t 1 --python scripts/validate_surface_materials.py`
4. Render the integrated master with `scripts/render_detail_gallery.py`; see `docs/BUILD_AND_RENDER.md`

The neutral probes are actual Cycles renders. They use 96 samples, two CPU threads, AgX Medium High Contrast and neutral area lights. Denoising is disabled because the installed Blender build does not include OpenImageDenoise. They contain modelled sample geometry, no photographic backplate and no generated replacement render.

The focused library audit checks role names, rooted metric coordinates, packed/valid images, scalar-map colourspaces, dielectric paint and soft materials, genuine glass transmission, bounded bump scale, protected owner slots and non-mutation of shared legacy material nodes. Passing this audit does not replace final integrated locomotive visual review.

## Reference and provenance

All shader networks, source code and surface masks are original project work. No source photograph pixels, scanned commercial material or third-party material library is redistributed as a texture. The buffer map generator uses fixed seed 3900206 and records dimensions and SHA-256 digests in `textures/surfaces/SURFV02_MAP_PROVENANCE.json`.

Visual interpretation uses the already-selected [WAP-7 39002 photograph by WAM4ajj](https://commons.wikimedia.org/wiki/File:RPM_WAP-7.jpg), dated 21 November 2020 and licensed CC BY-SA 4.0. It supports the broad material relationships, selective runoff, lower-body dust, dark rubber and rubbed buffer faces. It does not determine numerical shader constants; no photo pixels were sampled into the material maps.

The [Blender 4.3 Principled BSDF manual](https://docs.blender.org/manual/en/4.3/render/shader_nodes/shader/principled.html) describes the dielectric/metal distinction, roughness, layered surface response and IOR. The implementation is matched to the installed Blender 4.3.2 socket names, which were checked at runtime.

Additional class-level finish evidence: [CLW shell specification, CLW-MS-3-152 Alt-13](https://clw.indianrailways.gov.in/uploads/FINAL%20DRAFT%20CLW-MS-3-152%20ALT-13.pdf), §7.4, specifies Poly-U400 finish and WAP-7 signal white RAL 9003 with a red border. Section 6.5 permits only limited side-wall waviness in new construction. The shader treats the exterior as a polyurethane-type opaque dielectric finish without an added automotive clearcoat. This modern specification is construction context, not proof of 39002's measured colour or condition on the photograph date.

Glazing type is supported by the [Railway Board 2025 mandatory-spares list](https://indianrailways.gov.in/railwayboard/uploads/directorate/stores/2025/List%20of%20must%20change%20items%20from%20Electric%20Dte%20%283%29.pdf), which identifies laminated windscreen glass for WAP-7/WAG-9. A reliable WAP-7-specific pane thickness was not established. The 8 mm neutral-probe pane is a representative modelling choice, not a certified thickness; the optical shader does not claim to reproduce individual laminate layers.

## Optional running-gear paint/oxide extension

`components/surface_running_gear.py` supplies three opt-in roles through its own `setup()` factory: `gear_frame`, `gear_cast` and `gear_wheelweb`. It never assigns objects or alters geometry. The running-gear component explicitly maps the existing material roles.

The frame and cast-housing materials use dark dielectric enamel with a thin dielectric dust deposit weighted toward upward-facing local normals. The grain remains submillimetre and object-local. Exposed conductive steel appears only where the geometry author explicitly supplies the `SURFV02_Wear` attribute; its absence means zero artificial edge wear. Existing separate pins, fasteners and rubbed contact geometry retain their own metal roles.

The wheel-web material combines a mostly dielectric brown oxide/dust film with a small exposed-metal fraction, separate from the polished running band. Its grain uses the wheel object's metric coordinates, so it stays attached during axle roll. `scripts/validate_gear_surfaces.py` checks this extension without changing a scene; its result is `qa/surfaces/gear_surface_validation.json`. The final running-gear gallery uses these roles in the integrated model.


## Stripe colour correction and matched colour pipeline

An integrated, same-camera/same-light A/B identified an overly red-brown starting pigment. The stripe is a scene-linear constant/ramp, not an image texture: there was no double sRGB decoding. The accepted base colour is now linear RGB `(0.46, 0.080, 0.010)` in place of `(0.46, 0.058, 0.020)`. The measured lit side/corner hue moved from about 14–16 degrees to about 21–24 degrees, near the selected photograph's roughly 22-degree orange/vermilion appearance. This is a visual match under non-calibrated photographic conditions, not a measured RAL specimen.

The controlled pigment comparison used matching camera and lighting settings. White paint, camera and lighting remained unchanged between the two pigment renders. The red channel and physical roughness were kept constant; changing green/blue naturally changes luminance slightly.

Material-QC renders now use the same AgX Medium High Contrast view as integration. The main paint softbox was moved away from the colour patch's mirror direction; the narrow grazing light remains for finish inspection. The former Base Contrast probe and near-specular softbox made the stripe appear more pastel. This was corrected in scene/source settings rather than by repainting an output image or weakening physical Fresnel reflection.

The [Blender 4.3 colour-management manual](https://docs.blender.org/manual/en/4.3/render/color_management.html) distinguishes scene-linear rendering from display transforms and describes AgX's handling of highly exposed colour.


The width-corrected build passes `materials.apply({'body_width_factor': body_geometry.WIDTH_FACTOR})`. Only the nose atlas's Y offset/extent scales with that factor, keeping window/washer runoff positioned with widened front fittings. Sidewall X/Z atlases and roof/hardware positions remain unchanged. The default `setup()`/`apply()` factor is 1 for standalone probes or the original geometry.

## Outdoor-lighting colour checks

The Poly Haven pure-sky HDRI used by presentation was inspected without changing it: Blender loads it as floating-point Linear Rec.709, with a maximum radiance of 73,216. It is not being passed through sRGB decoding or clipped to an 8-bit colour image.

A separate RGBE analysis locates the sun peak at approximately 47.9 degrees elevation and texture azimuth −34.2 degrees. With Cycles' equirectangular axes and the presentation Mapping node, the initial 115-degree and proposed 75-degree rotations both place the sun behind the +X nose. A rotation near 10.8 degrees predicts a world sun azimuth of −45 degrees, lighting the front and visible flank together. The presentation uses an 11-degree mapping rotation. This analytical orientation estimate controls light direction without altering the HDRI radiance or vehicle pigment.

See `qa/surfaces/environment_colourspace_validation.json` and `qa/surfaces/environment_sun_direction.json` for the recorded inputs and assumptions. The equirectangular convention is documented in [Blender's Cycles projection implementation](https://github.com/blender/blender/blob/main/intern/cycles/kernel/camera/projection.h).


## Maintained-service wear pass, v2.4

One source-map iteration was prepared after the 11-degree outdoor inspection. The clean white and orange pigment values remain unchanged. Original masks now provide:

- Warm road dust restricted to the lower side paint, with stronger deposition near the bogie regions and a cleaner front face
- Narrow irregular filter-rim grime and tapered runoff from the actual lower ledges; localized seal, hinge, drain-slot and door-latch dirt at the model's recorded coordinates
- Sparse roof runoff originating at the actual horn feet `(±8.40, ±0.56, 3.979)` and the central searchlight pedestal near `x=±8.575`; no generic streak band or roof-wide cloudy colour noise
- The same feature-directed film continuing very lightly over the orange stripe, so drips do not stop at an arbitrary paint-colour boundary
- Broader asymmetric buffer scuff islands and a slightly off-centre contact smear, with darker perimeter deposits; per-object UV rotation prevents four identical faces

The front-windscreen service role adds only a small exterior residue fraction outside a representative swept field. It retains the clear glass optical model; dust coverage is capped at 2.5 percent and roughness varies from 0.026 to 0.054. `assign_windscreen_service(pane, M['windscreen'])` creates the named Y/Z UVs, mirrors the outboard pivot convention, and assigns this role only to outward-facing front polygons. Keep the mesh's original `glass` material for its inner and edge surfaces. Side windows remain on clear glass. This is a plausible service sweep, not a measured reproduction of the precise wiper motion.

The generic coupler casting received a small object-local microfinish adjustment: about 58 micrometres effective bump height at roughly 1.4 mm spatial scale, a more matte exposed-steel lobe and a slightly stronger dry oxide film. The separately assigned rubbed-knuckle contact material, cast silhouette and topology remain unchanged. Grease stays on the existing modeled contact/slide regions.

Reproducibility is recorded in `textures/surfaces/SURFV02_SERVICE_WEAR_PROVENANCE.json` and `textures/surfaces/SURFV02_MAP_PROVENANCE.json`. Albedo soil mixing is performed in linear light before sRGB encoding. Scalar maps are loaded as Non-Color. The v2.4 material-only audit passes 24 checks, including front/rear exterior-face-only windscreen assignment. Final acceptance of the stronger service wear is based on the serialized integrated A/B, not merely these map/node checks.

### Final bounded strength calibration

The identical-stage whole-vehicle A/B showed correct placement but only about 3–5 display-RGB levels of change on the lower side panel. The final adjustment is therefore limited to lower-side dust ×1.5 and the already placed narrow filter/door grime ×1.25. Its distribution, clean pigment and shader settings do not change. Eight exact file hashes confirm that the nose, roof, buffer and windscreen maps are unchanged; see `qa/surfaces/bounded_gain_validation.json`. The six side albedo/roughness/mask files carry the stronger coverage. The supplied source retains this bounded adjustment.
