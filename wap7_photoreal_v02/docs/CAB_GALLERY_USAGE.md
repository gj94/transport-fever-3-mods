# Final integrated-master cab gallery

`scripts/render_cab_gallery.py` renders from an explicit, already-integrated delivery `.blend`. It never imports the cab authoring module, rebuilds furniture, changes a vehicle pose, or saves a `.blend`.

## Invocation

Run from the revision folder. On memory-limited systems, render one view at a time:

```bash
MASTER="$PWD/WAP7_detail_v02.blend"
SHA=$(sha256sum "$MASTER" | cut -d' ' -f1)
blender -b --python-exit-code 1 --python scripts/render_cab_gallery.py -- \
  --master "$MASTER" --expected-sha256 "$SHA" \
  --view panel_A --samples 96 --width 1600 --threads 2 \
  --output previews/cab/panel_A_final.png
```

Available views are `panel_A`, `overview_A` and `seats_rear`. Optional `--cab 2` applies the same framing to the other existing cab. Height follows the documented view aspect ratio: 1.6 for Panel A, 4:3 for the wider cabin views.

Use `--stage-only` to open, check and stage the master while writing provenance JSON without launching a render. Use a distinct output basename for a staging-only check. An optional `--provenance` argument controls the JSON path; otherwise it is beside the PNG as `name.provenance.json`.

## Provenance and safeguards

The JSON records:
- Input master path and SHA256 before/after, plus the renderer script SHA
- Original frame, unit settings, cab/vehicle controller matrices and door/pantograph properties
- Source geometry/topology/pose digests before/after presentation setup and after rendering
- Exact camera, lens, viewport dimensions, lighting positions/powers/colors and world settings
- Render samples, thread count, color management, elapsed time and output PNG SHA

Only new presentation cameras, lights and a neutral world are created. Original lights are muted in memory and listed in the record. Vehicle meshes, materials, modifiers, root transforms and poses are not reapplied or saved. Source object geometry, topology, material slots and poses must remain unchanged. Compositing/sequencer overlays are disabled so the PNG is a direct scene proof with the recorded color management.

A real render refuses a master with the old BODY Y scale, stale cab paint metadata or the angular pre-polish lanyard. `--stage-only` reports these as warnings, allowing setup review on the earlier master. A changed input SHA during rendering makes the run fail rather than claiming the image proves a newer master.

## Verification performed

All three camera setups, including a Cab 2 framing, passed staging-only tests on a tiny synthetic fixture. The fixture checked mesh, font and ordinary curve APIs, source geometry and file immutability, and confirmed no PNG was rendered. It is not a locomotive image or full-master rendering test.

The combined doorway validation was separately run against an immutable copy of master `81a59ac31ea6c1eba6732f8f8793889a9c5765b28b6fd70b9756954578337986`. All 78 passage/clearance reference rays passed at the two cab/room joins. See `qa/cab/combined_join_validation.json` for exact ray positions and test scope.
