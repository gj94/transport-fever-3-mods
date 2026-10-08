# LHB detail revision 02: review history

This is an authoring/visual QA log, not a railway engineering certification or TF3 runtime validation.

## Recovery review, 7 October 2026

- Preserved the first working 3A checkpoint as immutable WIP before further changes
- Inspected CAMTECH AC three-tier general arrangement pixels: nine main saloon windows, rounded apertures, compact roof-end AC equipment, central side-berth aisle and distinct end-service areas
- Found local-scale defect in service-fixture lathes: world-coordinate vertices were scaled about the global origin. Corrected these to local-coordinate geometry with explicit object positions. Independent evaluated bounds confirmed the pre-fix protrusion
- Removed duplicate original extinguisher cylinders by evaluating their true mesh centre rather than assuming object origins equal placement
- Replaced repeated presentation-only Blender operators with direct mesh creation; this avoids a costly full-scene dependency update per sleeper or fastener
- First corrected 3A exterior preview rendered with CPU Cycles at 1000×600/24 samples. Low-sample grain is expected in this proof. Final image review and higher-quality renders remain pending

## Known scope boundaries

All seven selected accommodation types require class-specific source and export QA. Exact furniture sizes, equipment placement, casting shapes, coil dimensions and service fittings remain representative interpretations. These procedural shaders are editable authoring materials; FBX transparency uses an explicitly documented fallback. Native TF3 conversion, baked game materials, LODs, collision/seat-pose runtime validation and universal locomotive coupling compatibility are not implied.

## All-class geometry checkpoint

All seven current source and portable-FBX files pass the independent source/export verifier, including actual dimensions, closed fabricated topology, winding, positive volume, fixture envelopes, class capacities, cushion-supported seated roots, berth references, hierarchy and export bounds. The verifier's four fault-injection tests demonstrate detection of misplaced passenger roots, escaped fixtures, wrong wheelbase and missing roots. Editable font tessellation warnings remain explicitly reported and occur in both source and export.

Visual review remains open. The next pass will extend the grey end paint wedge across local-origin shell pieces, close the small door-portal header gap, give WC glazing its own privacy material, and replace the HVAC top cover with real recessed condenser openings. No final-render or native-game readiness claim is made by this checkpoint.

## Recovered reference and attachment pass, 7 October 2026, 19:50 UTC

Integrated the CAMTECH-informed RMPU, CC furniture and soft cabin work across all seven sources/exports. A fixture audit caught floating 1A step/stile and wall fittings, plus unmounted CC bottle cages; corrected their actual geometry rather than concealing gaps in the camera. Added 1A attachment measurements and corresponding fault injections. GS's deeper crowned cushion retains its 1.840 m top; corrected the independent centre datum to 1.776 m for its 128 mm thickness. All eight current module hashes agree across all seven manifests. Current source and FBX checks pass with the existing explicitly reported font-tessellation warnings. New close proofs and final-resolution rendering remain active work.

## Current-source final 1A interior, 7 October 2026 22:43 UTC

Completed and inspected actual 1400×840 CPU Cycles pixels, using eight independently seeded uniform64-sample scene-linear EXRs (512 total), no denoising, one final AgX display transform. The patched LIGHT / SOCKET legend is now correctly facing into the cabin. Burgundy cushions/piping, curtain gathering/ties, wall nets, reading lamps and bottle holders remain visible with no newly observed attachment or collision defect in this view. Fine no-denoise grain remains; this single camera does not establish complete geometric or runtime correctness. Source hash12dfa0eb remains unchanged. Source/image/sampling/dependency identities are in qa/render_1A_interior.json. Completed duration1368.4seconds.

Recovery renderer identity now includes relocated helper files and actually loaded external texture content. The initial old-filter cache was preserved and excluded from final delivery. Evidence JSON is frozen byte-exact rather than rewriting execution paths inside its hashed fingerprint specification. The optional depot dependency-root check was corrected at a completed-frame boundary; previous helper bytes remain available under scripts/render_provenance for historical evidence.

## Current-source final 1A exterior, 7 October 2026 22:54 UTC

Actual 1400×840 uniform512 exterior completed in596.6seconds and visually inspected. Smooth roof/end transitions, HVAC recesses and fan assemblies, grey paint wedges, eight cabin-side window rhythm, underfloor boxes, bogies and rail contact are visible without a newly observed silhouette or attachment defect. Exterior is appreciably cleaner than interior at equal sample count. Original source remains locked. CC interior starts next; final gallery2/20 completed.

## Current-source final CC interior, 7 October 2026 23:23 UTC

Actual 1400×840 uniform512 interior completed in1739.8seconds and visually inspected by worker and parent. The3+2 chair layout, thin draped headrest linen/hem, refined shoulder profile, seat-back nets and mounted cages, roller blinds, shelves and reading lights are coherent. No new visible collision/attachment issue in this camera. Grain persists in ceiling/shadows without denoising. Root accepted the genuine gallery view without source edits. CC exterior is next, followed by immutable two-pair checkpoint.

## Current-source final CC exterior, 7 October 2026 23:34 UTC

Actual 1400×840 uniform512 exterior completed in630.3seconds and visually inspected. Continuous chair-car window rhythm and seating visible through glazing distinguish CC from cabin coaches; the blue/grey livery, crown, HVAC, door hardware and underframe remain coherent with the locked source. No newly observed silhouette or attachment defect. Four final gallery views are complete (1A and CC interior/exterior). 3A interior starts next.

## Current-source final 3A interior, 7 October 2026 23:57 UTC

Completed and inspected current1400×840 uniform512 corridor pixels. Repeated partitions, ladders, folded daytime berth backs, lower cushions, upper berth undersides and ceiling equipment remain coherent, without a newly observed geometry defect. This longitudinal corridor framing hides much of the berth faces and does not by itself establish class-specific bay detail. Proposed adding the already supported bay-camera512 view after core gallery; no source/camera redesign. Exterior rendering follows.

## Current-source final 3A exterior, 8 October 2026 00:08 UTC

Actual1400×840 uniform512 exterior completed in619.8seconds. Nine saloon windows,3A identity, roof-end HVAC, livery transitions, bogies and equipment are visually coherent; no new visible defect. Six core frames now complete. Parent approved adding the existing3A bay camera as a21st final, after core views, because the corridor image does not show the berth faces clearly. Renderer and geometry remain unchanged; only supervisor queue changes. 2A interior is active.

## Current-source final 2A interior, 8 October 2026 00:35 UTC

Completed1400×840 uniform512 in1429.8seconds after recovering a transport interruption. Actual pixels inspected: corridor/ladder/partition rhythm and cushions remain coherent without newly observed geometry defect. This narrow camera remains layout proof and is not a strong inspection of berth faces. Source/renderer unchanged. Exterior is active; seven of21approved finals complete.

## Current-source final 2A exterior and recovery, 8 October 2026 01:00 UTC

Completed1400×840 uniform512 exterior inspected after environment replacement. Nine saloon windows,2A markings, shell/crown, HVAC, doors and underframe remain coherent; no newly visible defect. Eight current-source final frames now verified. Previous renderer session was lost during SL first batch; completed1A,CC,3A,2A pairs remain intact. Resumed gallery from actual completed hashes, preserving all finished frames and restarting only interrupted SL batch. Continue21-view gallery past requested minimum01:00UTC window.

## Current-source final SL interior, 8 October 2026 01:23 UTC

Actual1400×840 uniform512 completed in1344.1seconds and reviewed. Open non-AC arrangement, ceiling fans, ladder rails and berth supports are coherent without a newly observed collision. As with other sleeper corridor cameras, this is layout proof rather than detailed berth-face evidence. Source unchanged. SL exterior follows;9/21finals complete.

## Current-source final SL exterior, 8 October 2026 01:34 UTC

Actual1400×840 uniform512 exterior completed614.1seconds and inspected. Paired narrow barred windows and ventilated non-AC roof differentiate SL from the air-conditioned types; the livery, doors, running gear and underfloor equipment remain coherent without a newly visible silhouette defect. Ten final frames complete. 2S interior is active.

## Current-source final 2S interior, 8 October 2026 01:57 UTC

Actual1400×840 uniform512 completed1379.3seconds and inspected.3+3 upright chair rows, barred windows, longitudinal luggage racks and twin fan rows are legible and coherent. No newly visible collision or unsupported fixture in this camera. Eleven approved finals complete;2S exterior is running.

## Current-source final 2S exterior, 8 October 2026 02:08 UTC

Actual1400×840 uniform512 exterior completed620.0seconds and reviewed. Blue/grey second-sitting livery, barred window rhythm, non-AC roof vents, door hardware and underframe are visually coherent; no newly observed silhouette issue. Twelve core finals completed;GS pair is the remaining core type before7planned detail views.

## Current-source final GS interior, 8 October 2026 02:30 UTC

Actual 1400×840 uniform 512-sample frame completed in 1323.1 seconds and was inspected. Transverse bench banks, overhead racks and supports, barred windows and ceiling fans are visible and coherent. No newly observed attachment defect. The selected legacy centre-entry GS prototype remains explicit. Thirteen of 21 finals are complete; GS exterior is the last core frame before seven planned details.

## All seven core class pairs, 8 October 2026 02:40 UTC

GS exterior completed at 1400×840 uniform 512 samples in 606.4 seconds. Centre-entry arrangement, paired barred windows and non-AC roof are clearly distinguished; source remains the selected legacy GS type. All fourteen class interior/exterior frames are now complete and source-matched. Seven detail views remain, starting with the approved 3A bay camera. The gallery is not yet complete and native game conversion is still outside scope.

## 3A bay final, 8 October 2026 03:03 UTC

Completed actual 1400×840 uniform 512-sample bay view in 1408.7 seconds and inspected. Folded middle-berth backs, lower cushions, upper berths, ladders, curtains, reading lamps, table and bottle holders are visible. This view supplies berth-face detail obscured by the corridor camera. No source geometry or camera redesign was required, and no new visual defect was observed. Fifteen of 21 planned frames complete; CC chair close-up follows.

## CC chair close-up final, 8 October 2026 03:29 UTC

Actual 1400×840 uniform 512-sample close-up completed in 1625.1 seconds. Thin draped linen, upholstery piping, tray backs, nets, bracket-mounted bottle cages and footrests are legible. No newly visible attachment defect. Some bevel faceting is visible at this close range; the geometry remains the previously approved locked source. Sixteen of 21 frames complete, with 1A cabin-entry detail running next.

## 1A cabin-entry final, 8 October 2026 04:30 UTC

Actual 1400×840 uniform 512-sample cabin-entry image completed after recovery, reusing two valid 64-sample batches and spending 1049.5 seconds on the resumed run. Sliding doorway, burgundy upholstery, upper-berth access steps/stiles and mounted hooks are clearly visible without a newly observed attachment defect. Seventeen of 21 finals complete; HVAC detail follows. The stored resumed duration does not include earlier saved-batch time.
