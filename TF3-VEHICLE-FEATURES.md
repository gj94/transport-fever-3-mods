# What can be modded on TF3 locomotives and coaches

Research date: 30 September 2026. This guide separates capabilities verified in
the installed TF3 resources from features already implemented in our pack.
This guide is updated as subsequent integrations are installed.

Subsequent v02 integration: updated interiors and instrument textures are now
exported; WAP-7/LHB glass is separate and transparent; two locomotive crew
seats and 72 seats per coach are configured. Their runtime placement and cockpit
behaviour still require testing. Driver placement was corrected using the stock
character's posed hip offset.

Subsequent coupling-v03 integration: the active ICF model is a CBC-retrofit
visual variant, with matching WAP-7 heads. Their exported spacing uses named
mating planes, while rendering bounds include the projecting head tips. Dynamic
coupler yaw/compression is still not implemented; in-game curve checks remain.

Pantograph-v04 integration adds six rigid joint animation tracks, independent
front/rear selection by direction, and live catenary-height sampling. Our
conversion extends the illustrative raised angle from 36 to 45 degrees to reach
TF3 standard wire height. The extended geometry passed a 103-pose roof-clearance,
arm-length and head-level check. Both animations preview correctly in Model
Editor. After the `.trf.lua` packaging correction and restart, the user confirmed
the result looks good in game. Exact wire contact and direction switching have
not been individually reported as tested.

## Feature map

| Area | What can be changed | Our current pack / next step |
|---|---|---|
| Geometry and appearance | Exterior/interior meshes, UVs, materials, glass, liveries, normal maps and LODs | Updated interiors, instrument textures, colour palettes, and separate transparent glass implemented |
| Liveries and ageing | Native material examples include colour blending, dirt/rust masks and associated textures | Not implemented; requires intentional masks and material setup |
| Driver and passengers | Crew seats, seated-character animations, group-relative transforms and passenger compartment seat indices | Two driver anchors and 72 passenger anchors per coach; passenger placement still needs a play test |
| Animation | Door opening/closing, wheels/bogies, pantographs and direction-dependent visible parts | Independent pantographs implemented with wire-height sampling; stock train behaviour retained; custom door animations pending |
| Lights | Head/tail lights and light-emitting or illuminated materials; native models have timed and direction-sensitive light setups | No complete lighting setup yet |
| Sounds | Continuous tracks, event clips, volume/pitch curves, custom update scripts and distance settings | Private approved horn shared by WAP-7/WAG-9/WAG-12B; stock electric layers and wagon sound sets referenced |
| Performance | Speed, empty/payload weight, engine type, power, tractive effort and friction; native train setup also includes braking | Initial prototype gameplay values; tune against intended gameplay and verified vehicle specs |
| Passenger/cargo handling | Capacity, cargo class/type filters, compartments, seat assignments, load speed and visible load configuration | ICF/LHB configured for 80/88 places (20/22 at standard game scale), retaining 72 physical passenger locators; boarding/unloading and seats need testing |
| Service and economics | Purchase price/scales, running cost/scales, lifespan, maintenance factors, noise/pollution and availability dates | Basic automatic prices/costs and prototype values |
| Vehicle identity and UI | Names/descriptions, filter tags, icons, release/retirement years and availability notifications | Names, dates, tags, rendered icons and a default Indian Railways purchase tab implemented; purchase-tab appearance user-confirmed in game |
| Physical/visual fit | Colliders, bounds, wheel/axle metadata and bogie behaviour | Box colliders and original axle pivots; curve/coupling tests pending |

Visible couplers, hoses and buffers can be modelled or animated. Do not assume
TF3 enforces real-world coupler compatibility from their appearance. Test the
LHB and ICF families as separate rakes; v03 directly addresses the WAP-7/ICF pair.

## Sounds: yes, including custom recordings

Local revision 11 points WAP-7, WAG-9 and both WAG-12B sections to one resource
`gj94_indian_rail_pack::/vehicle/train/wap7/sound/wap7.snd`.
Its `horn` event directly references `wap7_horn.wav`: the approved two-second
section of the user's HornSample, in mono PCM16 at 48 kHz. Stock traction,
wheel and brake tracks use explicit references to the base game's audio with
the original gain/pitch curves. The local recording is excluded from
tracked release archives; package this build with `--private`, or use
`--stock-audio` to create the public package with stock horn references.
The user confirmed revision-10 WAP-7 horn playback works. New-engine horn
playback still needs a runtime check.
The shipped vehicle window invokes `letVehicleHorn` through a normal
`react.iaHandler` without accepting held-key repeats. Each key press triggers
the full clip; holding/releasing the key does not sustain/stop it. A true
hold-to-sound control would require additional scripting and runtime testing.
The coaches point to
`::/vehicle/waggon/shared/sound/waggon_modern.snd`.
These references reuse the installed game's resources; no native recordings
have been copied into our distributable pack.

The shipped electric sound set demonstrates:

- Separate idle, drive and acceleration recordings.
- Volume and pitch curves driven by `vehicle.speed01`.
- Wheel squeal and braking tracks.
- A collection of rail-clack samples.
- A `horn` event.

The shipped modern wagon sound set demonstrates a rolling track, squeal,
brakes, clacks and `openDoors` / `closeDoors` events. Sound events do not
create door geometry or animations; those are configured separately.

### Suggested Indian Rail sound package

| Vehicle | Proposed layers | Needs a new Blender model? |
|---|---|---|
| WAP-7 | Distinctive horn, traction/motor acceleration, cruise/rolling, idle equipment/fan/compressor bed and brakes | No for sound clips and sound configuration |
| LHB | Rolling/rail clatter, braking and optional door sounds appropriate to the modelled coach | No; animated doors still need geometry/integration |
| ICF | A separately tuned rolling/clatter profile and braking, with suitable door sounds if desired | No; visual changes are separate |

These are design proposals, not a claim that every real train sound is an
independent built-in game event. Idle equipment can be a continuous layer;
special operating triggers may require a custom update script and testing.

### Implementation workflow for a future sound pass

1. Obtain usable recordings: isolated horn and rolling/braking/motor samples,
   without commentary or music. Record provenance and permission to redistribute.
   The shipped vehicle examples use WAV files; start with that proven format.
2. Trim one-shots, build seamless loops, remove unwanted background noise and
   balance levels before integration. Multiple coaches play simultaneously.
3. Add our own `sound/` folder and `.snd.lua` resource beside the vehicle.
   TF3 resource references use `.snd`; the editable Lua resource is `.snd.lua`.
4. Use the shipped `soundsetutil` helpers for speed-driven tracks, brakes,
   squeal, clacks and events. Reference our own clips relative to the sound set.
5. Point `metadata.soundConfig.soundSet.name` at the new resource. A sound set
   contains `tracks`, named `events`, attributes and an update script. The API
   also exposes `soundConfig.effects` for overriding supported clip keys in a
   selected sound set; verify those keys before choosing that smaller approach.
6. Tune gain/pitch curves and reference distance in the Model Editor where
   available, then test in-game at several speeds and camera distances.
7. Verify horn, departure, brakes, curves and doors separately; check pause,
   acceleration and a long rake. Keep the stock sound set as a comparison.

Useful confirmed helpers are `makeSoundSet`, `addTrackParam01`,
`addTrackCustom`, `addTrackSqueal`, `addTrackBrake`, `addEventClacks`,
`addEvent` and `addEventCustom`. The game also exposes a vehicle-horn action.
The revision-8 `soundConfig.effects.horn` attempt loaded without errors but
the user still heard the stock horn. The local sound set uses the direct event.
Its base helper import must include `::/scripts/`: a leading `/scripts/` alone
is resolved inside the mod namespace and caused revision 9's load error.
Custom scripts can alter gains, pitch and event triggers. Additional audio
formats or separate cockpit/exterior mixes have not been verified here.

## Interior view: model work plus integration

An attractive exterior does not automatically provide a usable cockpit.
The owner supplies the cab shell, interior surfaces, dashboard and furnishings.
Our conversion must preserve them, configure transparent glazing and register
driver seats. Native crew seats include an animation, a parent group, a
transform and `crew=true`; native coaches define passenger seats and map them
to their transport compartments.

The inspected native locomotive did not show a separate arbitrary camera-position
block. Verify the relationship between crew seats and TF3's cockpit view during
integration instead of inventing a camera field. Confirm eye height and both
driving directions in the game. Transparency and seated people can be added
locally; accurate missing interior geometry is what the upstream update helps with.

## Recommended next passes

1. Complete curve, slope, reversal, LOD and passenger-loading checks on the
   installed build; updated exterior, interiors, seats and pantographs are integrated.
2. Verify both cab views and passenger placement under actual service conditions.
3. Test the shared horn on the new freight engines, then consider a custom traction/rolling sound pass.
4. Add working doors and direction-dependent lights; pantographs are implemented.
5. Improve close-up mesh efficiency, distant LOD appearance and weathering.

## Evidence and reproducible sources

The online TF3 wiki could not be retrieved during this research pass. The claims
above were checked directly against the installed game's primary resources:

- `api/tealdef/api/type.d.tl`: `SoundSet`, `SoundConfig`, `SoundClip`,
  `SoundAttributes`, `TransportVehicle`, `LandVehicle`, costs and maintenance.
- `api/tealdef/api/type/transformator.d.tl`: vehicle state, door/wheel animation
  information, crew seats and script information.
- `api/tealdef/api/gui.d.tl`: vehicle-horn action.
- `base/content/scripts.zip` → `soundsetutil.lua`: sound helper signatures.
- `base/content/vehicle/train/shared.zip` →
  `shared/sound/train_electric_modern.snd.lua` and `shared/default_train.trf.lua`.
- `base/content/vehicle/waggon/shared.zip` →
  `shared/sound/waggon_modern.snd.lua`.
- Native `br_185_traxx.zip` and `china_type_25c.zip`: materials, lights, driver
  and passenger seats, entrances and transport configuration.

These paths are relative to `D:\SteamLibrary\steamapps\common\Transport Fever 3`.
They are inspected examples, not files to bundle with the mod. Recheck them
after a game update before relying on a particular signature or behaviour.
