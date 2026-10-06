# Cab component handoff

## Integration

Load the accepted full-width WAP-7 scene, then import `components/cab_interiors.py` and call `apply()`.

The function finds the preserved `CAB_A_INTERIOR` and `CAB_B_INTERIOR` parents. It adds only `CABV02_` objects and hides the 476 superseded visible furnishing objects reversibly. It does not save, render, change the outer shell, change an existing controller/anchor, create lighting or change the environment.

Optional context keys are `texture_dir`, `roots` (the two original cab objects), and `material_overrides` (role-keyed materials). Textures otherwise load from `textures/cab/` beside the component directory, and are packed.

## Principal modeled details

- A: rectangular battery/OHE/TE-BE instruments, engraved-style designators, four colored indicator lenses, a separate vigilance indicator, the observed key and spring-paddle pattern, three lower pushbuttons and emergency-stop collar
- B: angled pressure instrument assembly with recessed original dial artwork, separate needles/spindles, cover lenses, seal rings and clamp fasteners; separate small PB instrument
- C: recessed monochrome display, individual navigation keys, separate lighting switches, fault buttons, three-frequency sounder grille and controlled lamp hardware
- D: a deliberately smaller assistant-side panel, hand-lamp socket, illumination and vigilance controls
- Controller: the inspected ball-topped throttle and short reverser share a slotted plate at the A/C boundary; distinctly different brake controls are at the driver's left
- Two crew seats per cab: formed pans, compound-curved upholstery, perimeter piping, stitch geometry, suspension bellows, slides, arm pivots and adjustment hardware
- Three raised foot-switch assemblies on the inclined footboard; physical pedal ribs and screws
- Layered inner window reveals, seals and locking strips, blinds/spindles/brackets/cords, two guarded fans with blades/motors/supports, task and ceiling light housings, real ventilation slots
- Segmented back/side linings, handles, thresholds and a physically openable rear door with an actual glazed aperture

## Geometry fit

The module works at the historical inherited Y scale and at the corrected `BODY.scale.y=1`. It never imposes that correction itself. The full-width test establishes a maximum cab-lining envelope of Y ±1.463 m. The forward ceiling is clipped and tapered: its front top is at most 3.524 m; the rear lining reaches 3.604 m. This eliminates the former rectangular plate protruding through the tapered nose crown.

Rear doorway: the bulkhead cut is 0.748 m wide and reaches Z 3.515 m. The gasket leaves 0.694 m clear width; underside of the upper gasket is Z 3.486 m, over a threshold top at Z 1.6495 m, giving 1.8365 m clear height. The leaf clears that threshold. These are modeled practical dimensions, not a certified prototype survey.

The central machinery component should overlap the original exterior-shell cavity starting at |X| 7.16 m. The cabin module itself makes no extra exterior shell cut. Machinery-room authoring remains a separate component.

## Rear door control

Call `set_rear_door_angle(1, 80)` or `set_rear_door_angle(2, 80)`. Zero closes the door. The review control is limited to the tested 0–90° range. The helper sets `open_angle_deg` on `CABV02_1_Rear_door_hinge` or `CABV02_2_Rear_door_hinge` and tags the object for driver reevaluation.

The joint neutralizes the inherited nonuniform scale so that opening is rigid. Both 90-degree poses were checked by matching vertex distances before/after opening. Existing cab roots remain untouched.

## Materials

Wall, desk and instrument-panel coatings are dielectric paint. Their local metric microfinish uses approximately 0.667 mm spatial grain, 40 µm bump distance at 0.18 strength, ±0.015 roughness and ±1.2% color variation. The calibrated linear base colors are retained. A controlled before/after comparison confirmed a similar palette with a quieter paint highlight response.

Original dial/display artwork is separate from the painted surfaces. Other exposed-metal, vinyl, rubber, glass and optical roles remain separate. Small instrument covers use a restrained thin-cover transmission approximation so recessed scales remain illuminated without requiring expensive refractive-caustic simulation.

## Reproduction and evidence

- `scripts/make_cab_instruments.py` creates the 11 original images using Pillow and DejaVu Sans
- `qa/cab/component_validation.json` records isolated-component preservation, finite meshes, repeatability, paint physics and rigid door-motion tests
- `qa/cab/combined_join_validation.json` records the earlier combined doorway test, with its exact input SHA and test scope
- `scripts/render_cab_gallery.py` renders the integrated delivery master directly; see `docs/CAB_GALLERY_USAGE.md`
- `qa/portability_validation.json` and `qa/delivery_material_font_comparison.json` verify the final copied master, its image dependencies, font glyph source and material state

The delivered master uses external relative image files. Original component build functions pack images while constructing an authoring scene; the compact-delivery step preserves their exact bytes and removes that packing.

## Scope

The reference notes distinguish directly observed equipment from dimensional interpretation. This is a detailed conventional WAP-7/E70 visual cab, not an exact 39002 survey, an operational simulator, or a game-ready LOD/draw-call optimization. The machine-room component and exterior integration require their own checks. No photograph is projected onto geometry or embedded in any material.
