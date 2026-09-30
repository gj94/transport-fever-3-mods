# Track Speed Restrictions for Transport Fever 3

A separate local mod, `gj94_track_speed_restrictions`, adds a **Speed limit**
dropdown to the existing six stock track options. Choose **Default** or
**15, 25, 40, 60, 80, 100, 120, 130 or 160 km/h**. The 54 underlying variants
remain registered for saved-game compatibility, but their repeated menu entries
are filtered out. The Indian Rail vehicle pack remains independent of this mod.

## Use it

1. Enable **Track Speed Restrictions** when starting a game or through the
   mod selection for a saved game. Reload the game/save to discover the resources.
2. In the railway track menu choose your usual track style, then choose the cap
   from **Speed limit** in the construction toolbar. Stock availability years
   still apply. Select the electrified stock option for electric trains.
3. Lay that track, or use **Replace Track** on the section you want restricted.
   **Default** restores that stock track type's normal cap when applied.
4. Use TF3's speed-limit overlay to inspect the resulting section, then run a train
   through it. For an initial test, apply a 40 km/h electrified variant to a long
   straight stretch of the WAP-7's route, followed by unrestricted stock track.

The restriction applies in both directions. Adding or removing electrification
switches to the matching variant with the same speed and style. Curves, bridges,
tunnels and the train's own rating can impose a lower limit. The mod uses the
native speed-cap mechanism, rather than changing locomotive ratings.

The mod adds **automatic entrance boards**. At each boundary of a custom-speed
section, a yellow numbered board sits slightly inside the restricted track and
faces **outward toward approaching trains**. Its reverse face is blank, so a train
leaving an 80 km/h section does not see an 80 on that exit board. Default-speed
track has no custom-speed boards. On an 80-to-40 transition, the incoming face
for the 40 section shows 40; the 80 board faces the other approach.

Contiguous pieces with the same selected cap form one section, including changes
of track style or electrification. There are no repeated boards at internal
segment joins. Extending, splitting, replacing or bulldozing track updates the
boundaries. Restoring Default removes the old numbered boards. Existing restricted
track is detected when loading a save; it does not need to be rebuilt. The script
refreshes after construction events and periodically during simulation.

Boards are passive visual custom entities, separate from operational signals.
They never modify track edges, train routing, existing signals or noise barriers.
Tunnel interiors are omitted; bridge boards use the track's height. Revision 5's
board rendering and section updates are user-confirmed in game. The further
regression checklist below covers additional layouts and save/reload behavior.

The dropdown uses the existing track menu/replacement tool. It does
not add sign-controlled zones, directional restrictions,
temporary restrictions or passenger/freight-specific limits. Signs alone have
no effect on the cap.

## Installation and removal

The ZIP contains one top-level folder. Extract it into:

`<Steam>/userdata/<Steam user ID>/3493540/local/mods/`

For this installation, the intended destination is:

`C:/Program Files (x86)/Steam/userdata/312521856/3493540/local/mods/gj94_track_speed_restrictions`

Revision 1 was installed on 30 September 2026 and the user confirmed that it
worked in game. Revision 3 updated the same mod ID, retaining all existing track
resource names and caps. It corrects revision 2's startup failure by exporting
the Lua script's entry point through the required `data()` function. No staging copy is
installed. The previous installed version is backed up at
`D:/TF3Mods/Track-Speed-Restrictions-before-dropdown.zip`.
The failed revision 2 is backed up at
`D:/TF3Mods/Track-Speed-Restrictions-before-startup-fix.zip`.
Revision 3's 168 installed files were verified against the build by SHA-256.
During the later vehicle-pack check, TF3 reloaded successfully and logged
`[Track Speed Restrictions] Speed limit dropdown installed on stock tracks`.
The user subsequently confirmed the speed mod works well. Revision 4 retains all
existing resource names and caps and adds the entrance-board models and game script.
Revision 4's 219 installed files were verified against the build by SHA-256.
The previous working version is backed up
at `D:/TF3Mods/Track-Speed-Restrictions-before-entrance-boards.zip`.
The exported mesh's front/back render was inspected to confirm incoming-only
numbering; this is an offline preview, not an in-game screenshot.

The initial `Modtest2` load at **22:43 on 30 September 2026 (Singapore time)**
confirmed revision 4 was active, its `.gs` resource was created, and no resources
were missing. Its board script then failed before placement with
`Cannot loop over this component type`: TF3 does not permit enumerating
`BASE_EDGE` through `getEntitiesWithComponent`. The earlier permissive mock
missed this native restriction. The failed deployed script and complete log are
preserved under `game_build/speed_board_runtime_failure/`.

Revision 5 reads edge IDs from the native
`api.engine.system.streetSystem.getNode2TrackEdgeMap()` instead. It persists scan
throttling and warning state across simulation Lua contexts and reports track,
capped-segment, entrance, board and missing-model counts in the game log. It keeps
the same model and track resource names and speeds. Revision 5 is installed at the
destination above with all 219 files verified by SHA-256; revision 4 is backed up
at `D:/TF3Mods/Track-Speed-Restrictions-before-track-scan-fix.zip`.

The subsequent `Modtest2` load at **22:52 on 30 September 2026 (Singapore time)**
loaded revision 5 with no missing resources or entrance-board scan errors. Its
log recorded two boards for one capped segment, zero after the cap was removed,
and two boards for two joined capped segments. Later it recorded four entrances
and four boards across 26 capped segments, with no missing board models. The user
confirmed that the boards render and work in game.

Package: [Track-Speed-Restrictions-TF3.zip](dist/Track-Speed-Restrictions-TF3.zip).

Before removing the mod from a save, replace **every** mod track with stock track,
wait for its boards to disappear, and save again. Saves using these resources need
the mod; its removal severity is deliberately marked `Critical`. A mod in
`staging_area` with the same ID takes
priority over `mods`, so install only one copy.

## Build and verification

Run `tools/build_speed_restrictions.py` with Python and Pillow. The optional
`--game-root` argument locates a different TF3 installation. It reads six stock
track templates from `base/content/infrastructure/track.zip`, adapts their lane
speeds and menu entries, generates original numbered icons, and writes a separate
package under `game_build/` and `dist/`. It also includes a GUI extension registered
through the native `ModEntryPointExtension` and a native `.gs` game script.

`tools/track_speed_dropdown.script.lua` wraps the exported
`construction_react_util.getTrackDefinitions` and `getActionParams` functions. It
filters only this mod's repeated entries, adds a ComboBox to the six stock
definitions, and delegates build/replacement to the native action using the
chosen variant resource. It does not edit the base GUI script, mutate the stock
track resources, or alter third-party track choices. The chosen cap persists
when switching stock track options. Unsupported choices or missing resources
fall back to the original action.

`tools/track_speed_boards.py` generates original 36-triangle board models with a
number only on the local +X face and a blank grey back. The nine models use one
shared mesh and a separate numbered texture/material for each speed.
`tools/track_speed_boundaries.script.lua` reads the native `BaseEdge` graph and
recognizes only this mod's speed variants. It groups adjacent same-cap segments,
finds their boundary ends, samples the local spline and faces +X outward. Boards
stand on the incoming train's right, 2.8 m from the centreline, with their bases
slightly inside the capped edge. It creates, moves or destroys only its own visual
custom entities, using the same commands as the stock `custom_entity_util`.
The game's script state stores the board entity IDs for save/reload continuity.
It obtains track edge IDs from the street system's node-to-track-edge map; it does
not use generic component enumeration, which rejects this component in TF3.

The lane speeds are in metres per second, so each cap uses `km/h / 3.6`.
All native lane dimensions, transport modes, track styles, curvature coefficients,
costs, slope settings and availability years are preserved. Paired electrification
references are relative to the sibling template. Native geometry, textures and
sounds are referenced from the installed game and are not bundled.

The build validates the constant Lua tables, all 54 caps, transport modes,
unchanged geometry/curve/cost settings, both directions of each electrification
pair, referenced base resources, icon dimensions and ZIP integrity. A report with
source hashes is saved to `_metadata/build_validation.json` inside the mod.

`tools/check_speed_dropdown.py` executes the actual Lua extension and templates
using Lua 5.4 (Lupa), with a mocked native GUI interface. It verifies 120 combinations
of stock track, selected speed and build/replacement mode, plus menu filtering,
Default restoration, preservation of electrification and native action arguments,
safe fallbacks, and repeated initialization. The script loader check clears any
previous resource's `data`, ignores the Lua chunk's return, calls `data()` and
resolves `EntryPoint`. It also reproduces and rejects revision 2's missing-`data`
export. The report is
`game_build/speed_dropdown_validation.json`.

`tools/check_speed_boundaries.py` executes the actual board Lua in 32 scenarios,
covering Default/80/40 transitions, outward facing, same-cap segment joins,
electrification/style changes, extending, splitting, removing caps, bulldozing,
junctions, parallel tracks, curves, short sections, bridges, tunnels, missing
resources and save-state reload. It also checks the installed game's `.gs`
registration, `BaseEdge` fields and custom-entity command contract. It now rejects
`BASE_EDGE` enumeration, checks deduplication of track graph edges and uses sixteen
fresh Lua contexts to verify that throttling persists in game state. When the
archived revision 4 script is available locally, a 33rd scenario reproduces its
actual deployed failure. Its report is
`game_build/speed_boundary_validation.json`.

**Validation status:** track speeds, the dropdown and revision 5's entrance boards
are user-confirmed in game. Static asset/resource validation, 120 dropdown cases
and all 33 locally available boundary scenarios pass. The latest game log also
confirms native script execution, board creation, removal and grouping. The
following is a further in-game regression checklist; the user confirmation does
not establish that every layout and save/reload case below has been exercised:

- Restart TF3 and load the existing mod-enabled save. Confirm the repeated
  numbered entries are gone and **Speed limit** appears on stock tracks.
- Replace a long straight electrified section with **40 km/h** selected; inspect
  the speed overlay and observe a faster-rated train slow for that section.
- Add/remove wires and verify the overlay retains 40 km/h.
- Test reverse-direction running, a curve, a bridge and a section with a signal.
- Save and reload; confirm track limits remain and the log reports no unresolved
  resources for `gj94_track_speed_restrictions`.
- Choose **Default**, replace the section again, and confirm the stock cap returns.
- Build Default track, an 80 km/h section and Default track in sequence. Confirm
  only the two entrances of the 80 section have boards, with 80 facing toward
  approaching trains and blank backs facing departing trains.
- Join an adjoining 40 km/h section. On leaving 80 toward 40, confirm the board
  facing the train shows 40. On leaving a restricted section toward Default,
  confirm no old cap is displayed on the exit board's reverse face.
- Extend the 80 section, then restore part or all of it to Default. Confirm boards
  move to the new boundaries and old 80 boards disappear; signals and noise
  barriers should retain their previous behavior.
- Save and reload; confirm no duplicate or orphaned boards appear. Check the log
  for `Entrance boards initialized` and any entrance-board scan errors.
