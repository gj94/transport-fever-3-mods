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
worked in game. Revision 3 updates the same mod ID, retaining all existing track
resource names and caps. It corrects revision 2's startup failure by exporting
the Lua script's entry point through the required `data()` function. No staging copy is
installed. The previous installed version is backed up at
`D:/TF3Mods/Track-Speed-Restrictions-before-dropdown.zip`.
The failed revision 2 is backed up at
`D:/TF3Mods/Track-Speed-Restrictions-before-startup-fix.zip`.
Revision 3 is installed at the destination above; all 168 installed files were
verified against the build by SHA-256.
During the later vehicle-pack check, TF3 reloaded successfully and logged
`[Track Speed Restrictions] Speed limit dropdown installed on stock tracks`.
This confirms the GUI extension initializes; applying the dropdown's caps still
needs the track-specific checks below.

Package: [Track-Speed-Restrictions-TF3.zip](dist/Track-Speed-Restrictions-TF3.zip).

Before removing the mod from a save, replace **every** mod track with stock track
and save again. Saves using these resources need the mod; its removal severity
is deliberately marked `Critical`. A mod in `staging_area` with the same ID takes
priority over `mods`, so install only one copy.

## Build and verification

Run `tools/build_speed_restrictions.py` with Python and Pillow. The optional
`--game-root` argument locates a different TF3 installation. It reads six stock
track templates from `base/content/infrastructure/track.zip`, adapts their lane
speeds and menu entries, generates original numbered icons, and writes a separate
package under `game_build/` and `dist/`. It also includes a GUI extension registered
through the native `ModEntryPointExtension`.

`tools/track_speed_dropdown.script.lua` wraps the exported
`construction_react_util.getTrackDefinitions` and `getActionParams` functions. It
filters only this mod's repeated entries, adds a ComboBox to the six stock
definitions, and delegates build/replacement to the native action using the
chosen variant resource. It does not edit the base GUI script, mutate the stock
track resources, or alter third-party track choices. The chosen cap persists
when switching stock track options. Unsupported choices or missing resources
fall back to the original action.

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

**Validation status:** revision 1 track behavior was user-confirmed. Revision 2
failed during startup because its Lua script lacked `data()`; the earlier mocks
missed that loader requirement. Revision 3 passed static resource, loader contract
and 120 Lua behavior checks; actual dropdown display and
application still require this in-game play test:

- Restart TF3 and load the existing mod-enabled save. Confirm the repeated
  numbered entries are gone and **Speed limit** appears on stock tracks.
- Replace a long straight electrified section with **40 km/h** selected; inspect
  the speed overlay and observe a faster-rated train slow for that section.
- Add/remove wires and verify the overlay retains 40 km/h.
- Test reverse-direction running, a curve, a bridge and a section with a signal.
- Save and reload; confirm track limits remain and the log reports no unresolved
  resources for `gj94_track_speed_restrictions`.
- Choose **Default**, replace the section again, and confirm the stock cap returns.
