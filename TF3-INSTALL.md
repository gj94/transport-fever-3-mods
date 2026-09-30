# TF3 conversion, installation and update workflow

Last documented: 30 September 2026. Source baseline: repository commit
`7b6b23da96b839751c31faae5160f5a49e0424c1`.

Interior update source: `e346a0e68f25af458eb9ef6ab5c69e94718b51db`.
The `interiors_v02/` directory was extracted from that upstream revision without
overwriting our locally modified documentation or conversion tools.

Coupling update source: `f398592b3908ef205843d1e9b2211cb0189973f4`.
The separate `coupling_v03/` source directory supplies the corrected WAP-7
and ICF CBC-retrofit masters. LHB still uses its interior-v02 master.

Pantograph update source: `6f28461`, directory `pantograph_v04/`.
WAP-7 now uses this master, which retains the accepted coupling-v03 geometry.

The editable prototypes now have a locally generated TF3 pack containing WAP-7,
WAG-9, paired WAG-12B, LHB AC 3-tier, ICF Sleeper and Vande Bharat 8/16-car
trainsets. The Blender masters are unchanged. Current pack revision is **12**;
Vande Bharat source is upstream commit `644de22`; WAG sources are `6f45a50`.

For Steam installs, the pack folder belongs at:

`<Steam folder>\userdata\<your Steam user ID>\3493540\local\mods\gj94_indian_rail_pack`

An identical development copy is in `local\staging_area\gj94_indian_rail_pack`.
TF3 gives the development copy priority. Keep both copies synchronized while
developing, or move the development copy out of staging_area before installing
a later release.

## Try it

1. Start a new game and enable **Indian Rail Prototype Pack** in mod selection.
2. Choose year **2000 or later** to make all three vehicles available.
3. Build an electrified railway and a connected train depot.
4. Buy **Indian Railways WAP-7** and add either **LHB AC 3-tier** or **ICF Sleeper** coaches.
5. Assign the train to a passenger route and check departure, curves and loading.

WAP-7 and LHB are available from 2000, and ICF from 1980. ICF has 80
configured passenger places (20 at standard game scale); LHB has 88 (22 in game).
These gameplay capacities are normalized above the 72 physical berth locators.
The two coach families are intended as separate rakes.

For Vande Bharat, use **2019 or later** and buy **Vande Bharat Express (8 cars)**
or **Vande Bharat Express (16 cars)** from the electric trainset list.

## What is established so far

- Revision 12's Indian Railways purchase-tab appearance is user-confirmed. The
  23:19 Singapore-time `Modtest2` load on 30 September 2026 used revision 12,
  reported no missing resources and initialized the new purchase section.
- Earlier play-test result (30 September 2026): after correcting the pantograph
  control resource filename and restarting TF3, the user reported "Looks good".
  This confirms the corrected update's in-game appearance is acceptable. Exact
  wire contact through curves/slopes, switching after reversal, passenger loading
  and a complete sound/LOD test have not been individually confirmed.
- The user confirmed the revision-10 WAP-7 horn works. Revision 11 applies that
  same sound set to the newly converted freight engines; their runtime check is pending.
- Current local pack version is revision 12. The entries below also preserve
  the earlier problems and fixes; pending checks recorded during those stages
  should be read with the latest result above.
- The user confirmed the pack loads, WAP-7 appears in the vehicle manager and
  the model appears on track. Full route operation and passenger loading are
  not yet recorded as verified.
- The initial build appeared white. The exporter compared evaluated Blender
  material objects against original material objects; every comparison failed,
  so every face selected palette tile zero. Matching material names fixed this.
- The corrected WAP-7 was visually checked in Model Editor against the original
  preview: red stripe, dark windows, grey roof and underframe are present. The
  editor reported `Validation: no errors!` after the correction.
- Icons were initially absent. All three vehicles now have store, small and
  20-pixel icons at regular and high-resolution sizes. These were rendered from
  the original masters on transparent backgrounds.
- The corrected colours and icons are installed and included in the ZIP.
  Their appearance in the restarted game still needs confirmation.
- The v02 interiors are now integrated. WAP-7 has both complete cabs,
  preserved gauge/display textures and two crew-seat entries. LHB and ICF have
  updated interiors and 72 passenger-seat entries each. WAP-7 and LHB glazing
  uses a separate sorted transparent material with DXT5 alpha; ICF retains the
  author's original window/shutter geometry.
- Updated WAP-7 loads in Model Editor with no validation errors. In-game cockpit
  positioning, driver/passenger placement and loading still need checking.
- The first cab play test showed a floating driver. Both crew anchor heights
  were corrected from 2.22 m to 1.80 m: the stock `driving_upright` character
  has approximately 0.483 m of posed hip offset above its root, while the
  WAP-7 cushion top is 2.215 m. The lowered placement needs a fresh in-game
  check. The correction is retained in the exporter for future builds.
- Coupling v03 is integrated and installed as pack revision 3. WAP-7 and ICF
  now have matching CBC geometry and root-parented front/rear mating markers.
  ICF is labelled **ICF Sleeper (CBC retrofit)**. The original screw-coupled
  source remains in `interiors_v02/icf` but is not the current game model.
- TF3 `metadata.extent` longitudinal endpoints now use those mating planes:
  WAP-7 ±10.2000 m and ICF ±11.1485 m. Render bounds independently include
  the projecting heads, rather than treating their outer tips as spacing points.
  Export validation checks each frame, height, direction and spacing span.
- The expected straight-track centre separation is 21.3485 m, with approximately
  1.160 m body clearance and a deliberate 90 mm buffer-face gap. The CBC heads
  make the connection; buffers are not meant to be stretched until they touch.
  These are the author's visual fixture values, not a recorded TF3 result.
  Straight/curve runtime checks are still required; couplers are static.

## Build

From the repository root, with Blender 5.2 and Python/Pillow/Lupa available:

```powershell
blender --factory-startup -b -t 2 --python-exit-code 1 --python tools/check_tf3_pantograph_rig.py
if ($LASTEXITCODE -ne 0) { throw 'Pantograph rig check failed' }
blender --factory-startup -b -t 2 --python-exit-code 1 --python tools/prepare_tf3.py
if ($LASTEXITCODE -ne 0) { throw 'Vehicle conversion failed' }
python tools/compress_textures.py
if ($LASTEXITCODE -ne 0) { throw 'Texture conversion failed' }
blender --factory-startup -b -t 2 --python-exit-code 1 --python tools/render_tf3_icons.py
if ($LASTEXITCODE -ne 0) { throw 'Icon rendering failed' }
python tools/package_tf3_icons.py
if ($LASTEXITCODE -ne 0) { throw 'Icon packaging failed' }
python tools/check_tf3_pack.py
if ($LASTEXITCODE -ne 0) { throw 'Pack validation failed' }
python tools/check_tf3_balance.py --game-root 'D:\SteamLibrary\steamapps\common\Transport Fever 3'
if ($LASTEXITCODE -ne 0) { throw 'Stock balance comparison failed' }
python tools/check_vb_character_fit.py --game-root 'D:\SteamLibrary\steamapps\common\Transport Fever 3'
if ($LASTEXITCODE -ne 0) { throw 'Character-height check failed' }
python tools/check_tf3_freight.py --game-root 'D:\SteamLibrary\steamapps\common\Transport Fever 3'
if ($LASTEXITCODE -ne 0) { throw 'Freight Lua/motion/character-height check failed' }
python tools/package_tf3_pack.py --stock-audio
if ($LASTEXITCODE -ne 0) { throw 'Public pack verification failed' }
python tools/package_tf3_pack.py --private --copy-to D:\TF3Mods
if ($LASTEXITCODE -ne 0) { throw 'Pack archive verification failed' }
```

The installable folder is `game_build/gj94_indian_rail_pack`. Copy that entire
folder into TF3's `local/mods`. FBX intermediates are in `game_build/imports`.
Native models have four LODs, consolidated meshes, palette DDS textures,
vehicle metadata, box colliders and original axle/bogie pivots.

Current inputs are listed in `tools/model_sources.py`: WAP-7 under
`pantograph_v04/`, ICF under `coupling_v03/`, LHB under `interiors_v02/`, and seven
Vande Bharat masters under `vande_bharat_v01/cars/`, WAG-9 under `wag9_v01/` and
both WAG-12B sections under `wag12_v01/sections/`. To rebuild only the freight
engines, append `-- --only wag9,wag12b_a,wag12b_b` to preparation and icon rendering.
To rebuild only Vande Bharat,
append `-- --only vb` to the preparation and icon-rendering commands.
Geometry comes from the root's complete descendant
hierarchy, including interiors in separate collections. Paint, glass and textured
instruments are consolidated separately. Instrument UVs are preserved; small
instrument meshes are protected from being reduced to empty LODs.

### How the tools fit together

| Tool | Input and responsibility | Output |
|---|---|---|
| `tools/pantograph_rig.py` | Adjusts joint driver travel in memory to TF3's operating height, preserving the source master | Shared height range and adapted live rig |
| `tools/check_tf3_pantograph_rig.py` | Sweeps the adapted rig; checks rigid arm lengths, head level and nearby roof intersections | `game_build/pantograph_validation.json` |
| `tools/prepare_tf3.py` | Opens the registered source `.blend` files; excludes presentation objects; consolidates by original pivot; assigns per-face palette UVs; retains stable hierarchy names | FBX intermediates, preparation report and native pack |
| `tools/native_tf3.py` | Called by preparation; writes TF3 mesh buffers, hierarchy, materials and gameplay metadata | `.mdl`, `.msh`, `.msh.blob`, `.mtl`, intermediate TGA textures and manifests |
| `tools/wap7_transformator.script.tl` | Retains stock train behaviour; selects the active pantograph and samples wire height | Copied runtime script, referenced by `wap7.trf.lua` |
| `tools/compress_textures.py` | Converts TGA to DDS, writes full mip chains and changes material references | DXT1 opaque/instrument textures, DXT5 glass; corrected vertical orientation |
| `tools/render_tf3_icons.py` | Renders only vehicle geometry; construction icons use side profiles, stock physical scale and wheel baseline | Store and small PNG renders |
| `tools/package_tf3_icons.py` | Resizes those renders to the native vehicle UI sizes | Required TGA icon variants |
| `tools/check_tf3_pack.py` | Checks buffers, indices, finite numbers, references, DDS headers/mips, palette diversity and icon dimensions/alpha | Console validation result |

The mesh writer was based on the installed TF3 descriptors: attribute and index
offsets/counts are **bytes**, with float32 attributes and uint32 triangle indices.
The validator verifies resource integrity; it does not prove gameplay correctness.

Close geometry is still heavy. There are four distance bands: 0–100 m,
100–400 m, 400–1000 m and 1000–2500 m. The last band uses box silhouettes to
stay below the editor's 256 KiB recommendation. Improve geometry deliberately
rather than assuming the current distant silhouette is the final visual quality.

### Install a rebuilt pack

1. Save your game, then fully exit TF3. Do not force-close an unsaved game.
2. Run the complete build sequence above. Stop if any command fails.
3. Copy the complete `game_build/gj94_indian_rail_pack` folder into `local/mods`.
   With the current setup, copy it into `local/staging_area` too, because that
   development copy takes priority. Avoid leaving an older development copy active.
4. Start TF3 and load the test save. A restart is required to test changed resources;
   a Model Editor reload alone does not refresh the running game.
5. When distributing a build, ZIP the entire mod folder, including `mod.json`,
   `_metadata` and `content`. Keep the stable mod ID so existing saves resolve it.

The private horn ZIP is `D:\TF3Mods\Indian-Rail-Prototype-Pack-TF3-Private.zip`.
The tracked revision-11 ZIP includes the freight engines and corrected icons
with stock audio. `--stock-audio` removes the private audio files and replaces
their model references inside that archive without altering the local build.
The revision-11 local build uses seconds 2–4 of the user's `HornSample.mp4`,
converted to `D:\TF3Mods\WAP7-Horn-Preview.wav` with short edge fades.
WAP-7, WAG-9 and both WAG-12B sections share one copy of the sound set/recording.
The exporter automatically uses that local WAV when present; set
`TF3_WAP7_HORN` to use a different prepared two-second mono PCM16/48 kHz WAV.
`python tools/wap7_audio.py` applies it to an existing build without rebuilding
geometry. The recording and private package remain in ignored/local locations.
The default horn key triggers the complete two-second sound once per press;
the shipped handler does not accept repeated presses from a held key and does
not have a release-to-stop callback. In-game playback remains to be checked.
Generated `game_build/` files are ignored by Git; the scripts and documentation
are the reproducible source. Original `.blend` and FBX assets remain unchanged.
The pre-interior rollback ZIP is
`D:\TF3Mods\Indian-Rail-Prototype-Pack-before-interiors.zip`.
The pre-CBC rollback ZIP is
`D:\TF3Mods\Indian-Rail-Prototype-Pack-before-CBC-v03.zip`.
The pre-pantograph rollback ZIP is
`D:\TF3Mods\Indian-Rail-Prototype-Pack-before-pantograph-v04.zip`.

## Bring in the owner's updated models

1. Record the upstream commit and review what changed before updating. Preserve
   our local scripts and documentation; do not reset the checkout over local work.
2. Compare each new master with its repository preview. Check dimensions, metre
   scale, X along the vehicle, Y across it and Z upward, plus wheel contact height.
3. Inventory mesh names, parent hierarchy, materials and animation pivots. Update
   the exporter if the root collection, filenames or pivot names changed.
4. For interiors, preserve separate cab/interior and glass meshes. Extend the
   exporter to retain multiple materials instead of merging everything into a
   single opaque palette material. Use transparent glass with correct normals
   and visible interior faces on both cabs where appropriate.
5. Add driver/crew seat metadata and passenger seats, with transforms attached
   to the correct model groups. Associate passenger seats with cargo compartments.
   Test the game's interior/cockpit camera behaviour; a separate arbitrary camera
   metadata field has not been verified in this workflow.
6. Connect door, pantograph and light animations to game state. Geometry with a
   pivot is not sufficient to create an operating animation.
7. Rebuild, regenerate icons and run the file checks. Load **each** model in the
   Model Editor and inspect colours, transparency, dimensions and all LODs.
8. Run the play-test checklist below and record results before calling it complete.

Useful assets from the owner: editable masters, separate glass and interiors,
named driver/passenger seat markers, door/pantograph pivots, stable bogie/axle
hierarchy, material assignments and updated previews. Our TF3 metadata, sound
configuration and resource export remain integration work.

## Play-test checklist

- Mod list: pack appears, map/save loads, all three vehicles are available in
  their configured years, and vehicle-manager/store icons render.
- Exterior: colours match the source previews at close and medium distances;
  zoom through all LODs; check windows, wheels and coupling spacing.
- Movement: buy WAP-7 with each coach family separately, leave an electrified
  depot, traverse curves and slopes, reverse and enter a station.
- Passengers: serve a real passenger route; confirm boarding, capacity and
  unloading. Later, check seat placement and opening doors on the platform side.
- Interior: enter both driving directions; check driver, eye height, glass,
  dashboard visibility and clipping. Later, inspect passenger interiors too.
- Sound: listen at idle, acceleration, cruise, braking, curves, departure and
  the horn action. Test multiple coaches together so volume does not overwhelm.
- Save/reload: verify the same consist and resources survive restarting TF3.

For errors, inspect
`<Steam folder>\userdata\<your Steam user ID>\3493540\local\crash_dump\stdout.txt`.
Search for the mod ID, missing textures and warnings around the test time.
The game log identified the exact missing `_store`, `_icon_small` and `_icon20`
filenames during the first icon test.

## Editor DLL fix

Run `tools/open_model_editor.ps1`. It adds both the game root and the editor's
plugins folder to the editor process's DLL search path. OpenAL32.dll and the
other required libraries already ship with the game; no third-party DLL
downloads are needed. Edit its game path if TF3 is moved.

## Validation and remaining polish

WAP-7 loads with proper colours in Model Editor version 13 and reports
**Validation: no errors!** All native mesh buffers, local resource references
and DDS mip chains are checked by `check_tf3_pack.py`.

The initial play test confirmed registration and appearance on track. A corrected
build fixes evaluated-material palette mapping and adds vehicle-manager icons.
This is an initial playable conversion, not a finished release:
door animations, lights, verified passenger placement, weathering and
more efficient close-up geometry remain. The final distant LOD uses simple
silhouettes beyond 1 km.

## Pantograph v04 integration (30 September 2026)

WAP-7 now uses `pantograph_v04/WAP7_pantograph_v04.blend` from upstream
`6f28461`. The source has independent front/rear live controls; FBX does not
preserve their drivers, so `prepare_tf3.py` samples the three local pivot
transforms per end into six native `.ani` files. Samples are evenly spaced in
contact-strip height, using the inverse angle formula, over
4.254758–5.944412 m above rail. The source's 36-degree sample endpoint is
adapted in memory to 45 degrees by `tools/pantograph_rig.py`; the original
Blender file is untouched. Standard track defines catenary base 6.447 m and
rail lane height 0.53 m, giving an inferred operating height of 5.917 m.
Native animations contain relative transforms
from the folded rest pose and remain attached to all four LOD hierarchies.

`tools/wap7_transformator.script.tl` delegates ordinary train behaviour to the
installed game's stock train script, then reads the average catenary height.
It raises the rear pantograph when running forward and the front one when
reversed. The inactive end remains folded. Requested heights are clamped to
our checked 1–45-degree range; a higher wire needs a revised mechanical range
from the author, not scaling the whole locomotive.

Pack revision is 4. The driver root remains at Z=1.80 m and coupling mating
planes remain at ±10.2 m for WAP-7 and ±11.1485 m for the CBC ICF coach.
Both installed `mods` and `staging_area` copies were updated. The preceding
working ZIP is saved as `D:/TF3Mods/Indian-Rail-Prototype-Pack-before-pantograph-v04.zip`.
Restart TF3 to reload resources. In-game wire contact and direction switching
still require a play test; Model Editor animation previews alone do not verify
the live train transformator.

First in-game test loaded revision 4 but logged `Referenced transformator not
found: .../wap7.trf`. The source was incorrectly packaged as `wap7.trf`;
TF3 discovers this Lua-backed resource from `wap7.trf.lua`, while the model
continues to reference the virtual `wap7.trf` name. This packaging correction
is installed in both copies and is now required by `check_tf3_pack.py`.
After that correction and restart, the user reported the result looks good
in game. Detailed wire contact and reversal checks remain separate items.

`check_tf3_pantograph_rig.py` checks 101 travel positions plus both independent
one-up poses. The extended range retained rigid arm lengths, level heads
(maximum measured tilt 0.000006 degrees), and no unintended triangle surface
intersections with preserved nearby roof equipment. The result is saved to
`game_build/pantograph_validation.json`. This checks geometry, not physical
actuator limits or manufacturer tolerances.

For the supported vehicle features and a sound-design plan, see
[TF3 vehicle features](TF3-VEHICLE-FEATURES.md).

Official references: [mod definitions](https://wiki.transportfever3.com/doku.php?id=modding:general:moddefinition),
[game file locations](https://wiki.transportfever3.com/doku.php?id=gamemanual:installation:gamefilelocations),
[Model Editor](https://wiki.transportfever3.com/doku.php?id=modding:tools:modeleditor).

## Vande Bharat v01 integration (30 September 2026)

Upstream `644de22` supplies seven unchanged Blender masters. Revision **5**
converts all seven into native resources and adds the 8/16-car multiple units.
Cab noses face outward, with 19.375 m coupling pitch, 155/310 m spacing lengths,
and the source's compact seating layouts. Each car has four LODs, evaluated
white/blue materials, transparent glazing, seat markers and four animated doors.
The motor cars each supply 1,200 kW and 90 kN. Availability starts in 2022,
top speed is 160 km/h, and electrification is required.

Purchase and upkeep use TF3's automatic calculation, with normal maintenance
and ticket-income factors. `check_tf3_balance.py` reads the installed stock
models and applies their `base/model_metadata_util.lua` cost formula. These
figures precede difficulty and global cost multipliers:

| Trainset | Configured seats | Power | Purchase | Annual upkeep | Purchase per configured seat |
|---|---:|---:|---:|---:|---:|
| Vande Bharat 8 | 420 | 4,800 kW | 23,936,766 | 3,989,461 | 56,992 |
| Vande Bharat 16 | 880 | 9,600 kW | 48,372,216 | 8,062,036 | 54,968 |
| Stock Lastochka | 460 | 2,550 kW | 15,669,510 | 2,611,585 | 34,064 |
| Stock Twindexx | 440 | 5,000 kW | 25,023,684 | 4,170,614 | 56,872 |
| Stock ETR 450 | 608 | 4,375 kW | 26,162,706 | 4,360,451 | 43,031 |

Vande Bharat's 2.71/2.84 seats per metre and cost per seat fall within the stock
express-train range. CC/EC comfort is 0.7/0.8 and ticket `priceFactor` is 0.5,
matching normal stock income. That field controls fares, not purchase price.
The full comparison is `game_build/vande_bharat_balance.json`.

TF3's stock gameplay scale divides configured capacity by four: the ordinary
depot capacities are **105/220** for these Vande Bharat formations, **115** for
Lastochka and **110** for Twindexx. The stock-scale comparison remains the same;
our earlier 420/880 figures describe the authored seat layouts and metadata.

Both TC pantographs have 101 rigid-joint samples, with level heads and contact
strip heights from 4.079122 to 5.917 m above rail. The native transformator
delegates normal train behaviour to the stock script and maps catenary height
onto that travel. Animation references persist in all four LOD hierarchies;
render bounds include the raised rig. Door tracks first plug outward 0.09 m,
then slide 1 m, with independent left/right and all-door states.

`check_vb_character_fit.py` checks the installed male rail-driver skeleton and
the full seated/driving pelvis animation against the source's cushion height.
With character roots at Z=1.267 m, the driver hips are within 6 mm of the
Z=1.75 m cushion top. Passenger hips stay within 22 mm. This verifies skeleton
height; full mesh fit, passenger variants and cab clipping require a runtime
preview. Source marker transforms retain their authored seat positions and
orientations.

The native resource checks pass for all ten vehicles and both formations.
Model Editor version 13 loads the driving trailer with blue bands, dark windows
and transparent glazing, and its validation reports no errors. Its occupied
passenger preview shows seated characters aligned with the saloon seats.
The TC_CC native animation preview raises the pantograph with a level head.
The cab preview shows the seated driver behind the windscreen; driver hip
height is also checked numerically. Full-body cab clipping, live boarding,
door triggers, pantograph wire contact and reversal still require an in-game
test. Headlight lenses have authored colours; functional light effects remain
future polish.

After TF3 was saved and closed, both installed `mods` and `staging_area` copies
were updated to the final revision 5 and every copied file was SHA256-verified.
The preceding revision 4 is preserved in the
`D:/TF3Mods/Indian-Rail-Prototype-Pack-before-Vande-Bharat-*-20260930-190243.zip`
backups. `tools/install_tf3_pack.ps1` repeats the guarded install, backs up both
copies and refuses to proceed while TF3 is running. Always launch Model Editor
through `tools/open_model_editor.ps1` so the game-root DLLs are found.

## Formation registration correction (revision 6)

The first depot test exposed invalid MU model references in revision 5. TF3's
resource lookup retained `vande_bharat/../vb_dtc/...` literally and replaced the
unresolved vehicles with placeholders. Filesystem checks had incorrectly
normalized those paths and accepted them. Revision 6 references the exact
`gj94_indian_rail_pack::/vehicle/train/vb_*/vb_*.mdl` identifiers. It also clears
the individual car `filterTags`, matching stock MU-only cars, while retaining
`default` on both formations so only the complete trains appear in the depot.

`tf3_resource_paths.py` rejects dot segments instead of normalizing them.
Both pack and balance checks use this resolver. The regression check rejects
the old reference even though the file exists through filesystem traversal.
Both installed copies and the ZIP have been updated and hash-verified.
The fresh game reload reports no missing resources. The user then confirmed
revision 6 works well in game, resolving the missing-consist purchase-menu issue.

## Conventional coach balance (revision 7, 30 September 2026)

ICF capacity increases from 72 to 80 configured places (18 to 20 in game), and
LHB from 72 to 88 (18 to 22 in game). The gameplay capacities normalize their
passengers per metre to within about 10% of ordinary stock seated coaches.
The 72 physical berth/seat locators in each source remain unchanged. Payload
weights follow the exporter's existing 80 kg per configured place rule.

WAP-7, ICF and LHB now use `transportVehicle.priceFactor=0.5`, matching normal
stock trains and Vande Bharat. The previous factor was 1. Purchase and annual
upkeep remain automatic, with no custom discounts. Increasing capacity also
increases the automatically calculated coach price and upkeep.

The comparison fills a 320 m spacing budget, includes the locomotive, and uses
the installed game's cost formula before difficulty/global/company modifiers:

| Rake | Coaches | Game capacity | Length | Speed | Purchase | Annual upkeep | Purchase per game passenger |
|---|---:|---:|---:|---:|---:|---:|---:|
| WAP-7 + ICF | 13 | 260 | 310.261 m | 110 km/h | 27,904,950 | 4,650,825 | 107,327 |
| WAP-7 + LHB | 12 | 264 | 308.400 m | 140 km/h | 31,273,116 | 5,212,186 | 118,459 |
| Stock TRAXX + China YZ22 | 12 | 288 | 310.503 m | 120 km/h | 27,932,376 | 4,655,396 | 96,987 |
| Stock TRAXX + EW IV | 11 | 286 | 308.584 m | 160 km/h | 33,302,286 | 5,550,381 | 116,442 |
| Stock OBB 1042 + EW II | 12 | 300 | 313.294 m | 140 km/h | 26,799,720 | 4,466,620 | 89,332 |

The updated ICF/LHB rakes are competitive but not the cheapest per passenger.
ICF is about 11% above TRAXX/YZ22 per passenger, while LHB is about 2% above
TRAXX/EW IV. The lighter, less powerful OBB/EW II combination remains cheaper.
The new capacities improve the locomotive cost shared by each passenger.

`tools/check_tf3_balance.py` now includes conventional rakes and ignores empty
cargo filters on locomotives, as the game does. It takes the maximum alternative
load configuration per compartment instead of adding mutually exclusive loads.
The full report remains `game_build/vande_bharat_balance.json`.

Validation: pack resource checks passed. An independent Lua execution of the
installed cost formula matched purchase/upkeep estimates for all ten pack car
types and five stock comparison vehicles. Only the requested fare factors,
coach capacities/payload weights and mod revision changed in the built pack;
all other packaged resources retain their previous hashes. Revision 7 still
needs an in-game check after restarting TF3.

Revision 7 was packaged, installed into both `local/mods` and
`local/staging_area`, and every copied file was SHA256-verified. The previous
installed copies are preserved in `D:\TF3Mods` under
`Indian-Rail-Prototype-Pack-before-capacity-fare-v06-*-20260930-203314.zip`.

## Local WAP-7 horn (revision 8, 30 September 2026)

The user previewed and approved seconds 2–4 of `D:\TF3Mods\HornSample.mp4`.
The installed WAV is exactly the preview: two seconds, mono PCM16 at 48 kHz,
with a 10 ms fade in and 20 ms fade out. It has no clipped samples. WAP-7's
`soundConfig.effects.horn` supplies this recording while its base electric
sound set supplies the other tracks and events. Coach/Vande Bharat sound
configuration and the revision-7 capacity/fare balance are retained.

Validation passed for pack resources, actual Lua metadata, clip format and
preview hash equality. Comparing WAP-7 against its revision-7 Lua table showed
only the horn override and cache-version marker changed. The private ZIP has
1,921 individually hash-verified files. It is outside the tracked release
archive, which remains the revision-7 balance update with stock audio.

Revision 8 was installed into both `local/mods` and `local/staging_area`;
every copied file was SHA256-verified. Previous installations are backed up
as `D:\TF3Mods\Indian-Rail-Prototype-Pack-before-WAP7-horn-v07-*-20260930-205510.zip`.
Restart TF3 to audition the installed horn; runtime playback/volume is pending.

## Direct horn sound set (revision 9, 30 September 2026)

The revision-8 play test still used the stock horn. The 20:57 SGT game log
confirmed revision 8 was active from staging and reported no missing resources
or horn/audio errors. Its `soundConfig.effects.horn` override did not change
the heard sound, so it has been replaced by a dedicated sound-set resource.

WAP-7 now uses
`gj94_indian_rail_pack::/vehicle/train/wap7/sound/wap7.snd`, whose `horn` event
directly references the approved WAV. The five continuous tracks and rail-clack
event use explicit base-game audio paths. Executing both sound sets with the
shipped Lua helpers produced identical attributes, curves and update functions
after rebasing clip paths and replacing the horn. All base audio and update
script references resolve. Actual WAP-7 metadata otherwise matches revision 7,
apart from its sound-set reference and cache-version marker.

Pack validation passed and the private archive contains 1,922 individually
hash-verified files. In-game playback of revision 9 still needs confirmation.
Both installed copies were updated and every file was hash-verified. Their
revision-8 backups are
`D:\TF3Mods\Indian-Rail-Prototype-Pack-before-WAP7-horn-v08-*-20260930-210243.zip`.

## Base helper import (revision 10, 30 September 2026)

The revision-9 play test reported no horn. At 21:04 SGT the log showed
`module 'gj94_indian_rail_pack::/scripts/soundsetutil.lua' not found`, followed
by a missing sound-set warning for WAP-7. A leading `/scripts/` in a mod's
`require` uses that mod's namespace. Revision 10 imports the helper explicitly
as `::/scripts/soundsetutil.lua`, keeping the direct local horn event.

The revision-9 failure was reproduced with the shipped `base/init.lua`
require implementation and a resolver modelling the namespaces observed in
the log. The corrected sound set loaded through the same code under the mod
namespace and configured the horn, five continuous tracks and ten clack clips.
The corrected private package has 1,922 hash-verified files. Runtime playback
still needs the next restart/test.
Both installed locations were updated to revision 10 and every copied file was
hash-verified. Revision-9 rollback archives are
`D:\TF3Mods\Indian-Rail-Prototype-Pack-before-WAP7-horn-v09-*-20260930-210733.zip`.

## WAG-9, WAG-12B and construction icons (revision 11, 30 September 2026)

Upstream `6f45a50` was pulled with a fast-forward. The conversion opens the live
WAG-9 master and the two reusable WAG-12B section masters; the source review
assembly is not imported as one rigid mesh. WAG-9 is a standalone depot engine.
WAG-12B is a two-member multiple unit, with B reversed so both cabs face outward.
Individual sections are hidden from standalone purchase. Attach freight wagons.

| Depot choice | Year | Speed | Power | Starting effort | Empty weight | Coupling span | Base purchase | Annual upkeep |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| WAG-9 | 1995 | 120 km/h | 4,500 kW | 460 kN | 123 t | 20.562 m | 18,830,442 | 3,138,407 |
| WAG-12B complete pair | 2017 | 120 km/h | 9,000 kW | 706 kN | 180 t | 38.400 m | 37,660,884 | 6,276,814 |
| Stock BR 185 TRAXX | Stock | 160 km/h | 4,200 kW | 300 kN | 84 t | 18.844 m | 16,363,056 | 2,727,176 |

Power, effort and weight basis: [NWR WTT 2025, PDF page 166](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf)
and [RDSO Electrical Directorate Handout, PDF page 7](https://rdso.indianrailways.gov.in/uploads/files/Handout.pdf).
WAG-9's 46.9 tonne-force is rounded to 460 kN. WAG-12B splits 4,500 kW,
353 kN and 90 t into each section; totals are not doubled. Power values are
rounded game settings. Speeds and dates are the explicit user overrides below.
Costs use the installed automatic formula before global
and difficulty scales; no custom purchase/upkeep discount is added. The balance
report also retains the previous passenger-rake comparisons and unchanged fares.

WAG-9 uses six pantograph joint tracks. WAG-12B uses three per section and the
reversed/trailing section's pantograph is selected. All tracks have 101 samples
at equal contact-height intervals. WAG-9 spans 4.255–5.917 m; WAG-12B spans
4.245–7.520 m and samples the current wire height within that range. All four
LOD bounds include raised travel. Standard rail behaviour is retained through
the explicit base-game transformer import.

The user confirmed revision-10 horn playback works. The private revision-11
build points all three locomotive classes at that same working sound set.
Its two-second WAV remains unchanged and is stored once in the WAP-7 folder.
The public archive contains stock electric audio references and no private clip.

All 13 car/engine types now have straight side-view construction icons. Their
widths follow visible vehicle length at approximately 16 pixels/metre at @2x,
with a common wheel baseline; regular and 20-pixel variants derive from those
profiles. This matches the stock builder's side-view convention and avoids
forcing unequal-length vehicles into a fixed 300-pixel perspective image.
Larger store previews retain the stock-style perspective view.

Validation passed: native mesh/material/texture/reference/formation/icon checks;
1,246 Lua resource tables executed, including the horn sound set through the
installed base helpers; 101 exported contact heights through every native LOD
(maximum error below 0.000002 m); 207 script-logic cases per freight section for
height clamping, direction selection and missing vehicle state; and actual
stock driver hip placement at each cushion (within 0.001 m). The script test
strips known Teal annotations and stubs the stock updater, so it does not prove
the game's Teal compilation or runtime operation. Full cab anatomy, new-engine
horn playback, MU purchase/wagon attachment, curves, reversal and wire contact
still need the first in-game check.

### Requested speeds and availability

After reviewing the difference between design/service speeds and family/variant
dates, the user explicitly chose the listed gameplay values. These supersede the
older speed/year settings recorded in the historical revision notes above.

| Vehicle | Maximum game speed | Available from |
|---|---:|---:|
| ICF Sleeper | 110 km/h | 1980 |
| LHB AC 3-tier | 200 km/h | 2000 |
| WAP-7 | 180 km/h | 2000 |
| WAG-9 | 120 km/h | 1995 |
| WAG-12B | 120 km/h | 2017 |
| Vande Bharat, both formations | 180 km/h | 2019 |

These are gameplay choices, not a claim that the standard fleet operated at
these limits from those dates. For context, the NWR table gives standard WAP-7
140 and WAG-9 100 km/h. [RDSO's WAG-12B handout](https://rdso.indianrailways.gov.in/uploads/files/Handout.pdf)
records 2020 approval for the B variant. [The Ministry of Railways](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2148364&lang=2&reg=48)
distinguishes Vande Bharat's 180 km/h design and 160 km/h operating speeds;
[its 2.0 introduction report](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1883511&lang=2&reg=48)
dates the modelled version to 2022, with the original family in 2019.
[The LHB maintenance manual](https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_I.pdf)
supports the family introduction in 2000. ICF 1980 is the user's approximate
gameplay date for this illustrative CBC-retrofit visual, not a certified variant
introduction date. Automatic prices/upkeep are recalculated for the chosen speeds.

At the chosen speeds, the 320 m budget comparisons are now 26,854,662 purchase /
4,475,777 annual upkeep for WAP-7 + 13 ICF (260 game passengers, 110 km/h), and
32,693,724 / 5,448,954 for WAP-7 + 12 LHB (264 passengers, 180 km/h).
Vande Bharat 8/16-car sets remain within the stock comparison range for automatic
cost per passenger. Capacity, fare and maintenance factors are retained.

Revision 11 was packaged and installed into both `local/mods` and
`local/staging_area`; all 2,515 local files were verified after copying.
Both previous copies are backed up in `D:\TF3Mods` as
`Indian-Rail-Prototype-Pack-before-freight-icons-v10-*-20260930-221135.zip`.
The public ZIP has 2,513 individually verified files (53,732,563 bytes), SHA256
`f4d272aae5878afaed67449a0438561ae45441f5f98fa7ec1908cc4cc142cf20`.
The private local ZIP has 2,515 files (53,908,896 bytes), SHA256
`3664adcced63649a9937f863c4e2d4dbef62a31786daaa4a483558bdfd84b1e3`.
Archive metadata checks confirmed every requested speed/year in both packages;
the private horn hash matches the approved preview and the public package
contains no private sound files/references. Restart TF3 for the first new-engine
and construction-panel play test.

## Indian Railways purchase tab (revision 12, 30 September 2026)

The rail **Buy Vehicles** window now opens on an **Indian Railways** tab each
time it is opened. It shows this pack's WAP-7, WAG-9, complete WAG-12B, LHB and
ICF coaches, and both Vande Bharat formations together. Native availability
years and depot compatibility still apply; individual trainset parts remain
hidden as before. The original Locomotive, Wagon, Multiple Unit and text-search
tabs retain their usual behaviour. Road, tram, water and air browsers are unchanged.
This change applies to the purchase browser, not the list of owned vehicles.

`tools/vehicle_browser.py` adds two GUI resources and updates the mod revision
without re-exporting the models. `tools/native_tf3.py` also includes the extension
in future full exports. The script is registered through the native
`ModEntryPointExtension`. It wraps only a tab widget containing the three native
rail tab identities, preserves original node references and styles, and augments
the exported rail filter. Filtering uses the owning mod's vehicle resource
namespace, so coaches and formations do not need to be renamed. No depot filter
tags or vehicle gameplay fields are changed.

`tools/check_vehicle_browser.py` runs the actual extension with the shipped
`TopBar`, `vehicleFilter`, `handleRailCarrier` and `showCargoFilters` bodies. Ten
scenarios pass: all vehicle types in the default section, normal stock tabs,
clearing stale filters, reopening, controller indices, text search, availability,
depot compatibility, unrelated tab widgets, repeat initialization and original
tab references. It treats native tree nodes as opaque. The report is
`game_build/vehicle_browser_validation.json`. These checks do not establish
native rendering or controller behaviour in the running game.

Before installation, SHA-256 comparison confirmed all 2,514 existing resources
apart from `mod.json` are unchanged in both installed copies. The local private
horn, geometry, animations, speeds, capacities, years and costs are preserved.
The update is installed in both `local/mods` and `local/staging_area` with each
copied file hash-verified; backups of revision 11 are in `D:/TF3Mods`, named
`Indian-Rail-Prototype-Pack-before-indian-rail-tab-v11-*-20260930-231659.zip`.

The public revision-12 ZIP contains 2,515 individually verified files (53,734,987
bytes), SHA-256 `2493934b0c30795bb7dee4a1391f2e27290a1fb4f67ada6844f98cd8c4e9b058`.
The private local ZIP contains 2,517 files (53,911,320 bytes), SHA-256
`604c34630b054154096e0b87b62b33a615e7f28af9a78121b9ede61d680ff5ad`.

The `Modtest2` load at **23:19 on 30 September 2026 (Singapore time)** used
revision 12 from the synchronized staging copy, reported no missing resources
and logged `[Indian Railways] Default purchase-browser section installed`.
The user then reported "looks good", confirming the new tab's in-game appearance.
Controller navigation, repeated reopening and each availability/depot case have
automated coverage but have not been individually reported as tested in game.
