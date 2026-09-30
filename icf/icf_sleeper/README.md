# ICF conventional sleeper coach — dimensioned visual prototype

## Current TF3 integration — pack v1.0

This directory preserves an earlier source prototype. Pack **v1.0 (TF3 revision 14)** uses the new ICF/LHB family masters while keeping the existing ICF SL and LHB 3A resource IDs. The native pack contains seven classes per family with doubled normalized capacity, normal fares and established family speeds/years. Original geometric reports below retain their source-specific scope. See [current installation, integration and remaining checks](../../TF3-INSTALL.md).

## Original source handoff

The following describes the original authoring files and source-only validation. Native conversion status is recorded above and in the linked installation guide.

Original Blender geometry, created with Blender 4.3.2. This is a first detailed visual baseline for review, **not a finished Transport Fever 3 mod**. No real coach serial, train number or operator route has been invented. Asset labels explicitly identify a generic 72-berth sleeper.

## Files
- `icf_sleeper_prototype.blend`: editable source scene, model collection plus separately grouped studio
- `icf_sleeper_prototype.fbx`: model-only export (no camera, lights, ground or rails)
- `build_icf.py`: reproducible original generation script; run `blender -b -t 2 --python build_icf.py`
- `icf_preview.png`: three-quarter full coach
- `icf_detail.png`: close view of one entrance and bogie
- `validation.json`: actual generated object/triangle counts, dimensions and berth count

## Dimensions and coordinates
Meters; X longitudinal, Y across coach, Z up. Rail running surface Z=0. Coach midpoint is the origin. Overall nominal body length 21.337 m; extreme buffer heads 22.297 m apart; nominal shell width 3.245 m; roof crown 4.025 m above rail; bogie pivots X=±7.3915 m; bogie wheelbase 2.896 m; new tread diameter 0.915 m; nominal track gauge 1.676 m. The separate display track measures gauge between the inner rail-head faces. Flanges legitimately extend below the rail running surface. The nominal 3.245 m shell width excludes projecting entrance steps and rails; the full attachment envelope is wider (see actual measured bounds in validation.json).

`ICF_ROOT_metres_X_forward` contains `BODY` and `BOGIE_1_PIVOT` / `BOGIE_2_PIVOT`. Each bogie contains two `AXLE_*_ROTATE_Y` empties located on the axle axis. Body, bogies, and wheelsets are distinct transform groups for future animation. Bogie rotation is around local Z; wheelset rotation around local Y. The model is unrigged; no suspension or coupler animation is implemented.

## Represented details
- Deep-blue bodyside, pale cyan window band, curved silver roof and pressed-panel seams
- Eighteen main window apertures per side arranged in nine two-window bays; rounded surrounds, five security bars, split shutter spines and raised slats; varied shutter positions
- Emergency-window markings/latches, berth-range labels, blank destination boards, non-specific sleeper lettering
- Four external entrance doors, barred door windows, handrails, thresholds and four-step ladders; four narrow toilet windows
- Recessed end vestibule door, black rubber bellows folds and gangway tread
- Traditional side buffers, central draw hook and simplified screw coupling; brake pipes/hoses
- All-coil ICF-style bogies with axlebox covers/bolts, paired primary coil springs, secondary bolster coils, swing hangers, side bearers, dampers, brake blocks, beams and pull rods
- Underframe solebars, cross-bearers, tanks, battery boxes, access lids, retaining brackets, air reservoir, electrical box
- A simplified nominal 72-berth arrangement (nine bays × eight berths), aisle ladders, partitions and ceiling-light shapes

## Sources and reference use
1. Indian Railways, South Central Railway, *Maintenance Manual for BG Coaches of ICF Design*, Chapter 3, Bogies: https://scr.indianrailways.gov.in/uploads/files/1341833527005-Bogies.PDF — text verified through the official document. Table 3.1 gives 2896 mm wheelbase and 915 mm new wheel diameter; all-coil primary/secondary springs, axle guides, side bearers and swing hangers informed the mechanical layout. The PDF image endpoint returned HTTP 502 during work, so no claim is made to tracing its drawing.
2. Western Railway ICF maintenance-manual reference supplied for the project: https://wr.indianrailways.gov.in/cris/uploads/files/1738062864681-1.%20ICF%20Coach%20Maintenance%20%20Manual.pdf — endpoint also returned HTTP 502 during this pass. The separate official working timetable below independently corroborates the selected nominal envelope dimensions.
3. Ravi Dwivedi, *Blue colored ICF Rail Coaches in India 01.jpg*, 13 April 2022, Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Blue_colored_ICF_Rail_Coaches_in_India_01.jpg — viewed at actual image pixels before modeling. Used only as visual reference for blue/cyan band, rounded shuttered windows, vertical entrance rails and steps, end treatment and bogie appearance. No photograph pixels are used in asset textures. Reference photo is CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . The reference photograph is not included in this repository and is not required by the Blender scene.

4. East Coast Railway, Sambalpur Division Working Time Table 2019, PDF page index 131 / printed page 101, WGSCN row: https://eastcoastrail.indianrailways.gov.in/uploads/files/1625144406231-SBP%20WTT%20NEW%202019%20%282%29.pdf — official published table verifies 22297 mm over buffers, 21337 mm body, 4025 mm height, 3245 mm width, 72 berths, 2896 mm wheelbase, 14783 mm bogie centres, 1676 mm track gauge, 1105 mm buffer centre height, and SC (screw coupling).

## Assumptions and remaining work
This chooses a traditional screw-coupled, side-buffer-equipped conventional ICF sleeper. ICF fleets vary by build/rebuild era; CBC-converted coaches exist. This coach is not a mechanically compatible assertion about a mixed LHB/ICF operational rake. Coupler geometry, exact window stationing/radii, roof profile, panel widths, tank arrangement, ventilation details, brake rigging, berth thicknesses and small hardware are visual approximations, not manufacturing dimensions. The model does not represent a selected numbered vehicle or revision-controlled GA drawing. Roof vents currently have low-profile base plates; full torpedo-vent shape, toilet partitions/fixtures, fans, bilingual markings, accurate decals, dirt/paint wear and fine welds remain to refine.

No UV atlas, baked textures, levels of detail, collision mesh, game materials, game manifests, validated exporter/importer integration or gameplay behavior is supplied. High-density modeling emphasizes reviewable shape and component separation. FBX export is performed, but target-game import is untested. Original Blender materials are simple physically based materials; their target application appearance can vary.

## Validation performed
Blender 4.3.2 source save and model-only FBX export were successful. The asset has 72 berth meshes, two bogie pivots and four axle pivots. Preview pixels were inspected; the initial open roof-end cap and occluded display sleepers were corrected, buffer centers set to the official 1.105 m height, and roof seam height adjusted to keep the 4.025 m crown envelope. Final previews use CPU Cycles, 64 samples at 1280×720, no denoiser. See validation.json for measured bounds and the separate FBX round-trip import result. Export/import validation here is Blender-to-Blender only, not a game-engine test.
