# Independent topology and coverage review
Status: IN PROGRESS. Review of authored plans/source data, not final rendered scene acceptance.

## Source-grounded layout expectations
- TVC:5 numbered faces,3 physical platform bodies(side1,island2/3,island4/5), distinct service yard fans. Historical2022 facade/platform appearance with current cartographic rail geometry explicitly mixed-date.
- NCJ:side1,island2/3,terminal1A bay; two principal platform-body outlines are not evidence for four through platforms. Large east-side service yard, north triangle and southern curved approach. Later remodelling proposals not silently included as built.
- ERS:6 numbered faces,4 bodies(side1,island2/3,island4/5,side6), unequal lengths/staggering. Separate ERSD marshalling/coaching yard must not be moved into station footprint.2017 appearance/current-map geometry mix disclosed.

## Graph audit
`raw_graph_topology_review.json` derives node adjacency from every rail-way segment in each worker's raw OSM bbox. © OpenStreetMap contributors, ODbL1.0; see THIRD_PARTY_NOTICES.md and https://www.openstreetmap.org/copyright . This JSON contains derived OSM metadata.

Raw-bbox degree>=3 branch nodes: TVC50,NCJ34,ERS67. These are not certified station turnout counts. Some lie outside final model extents. An endpoint-only algorithm misses45,33,59 respectively because a branch endpoint commonly meets an interior vertex of a through-way.

Issue R01, reported to ERS and preventative warning to TVC/NCJ: ERS initial builder counted only way endpoints. Consequence: missed switches and false buffer stops across connected tracks. Required correction: full segment-adjacency degree; retain true dead ends, distinguish crop-boundary endpoints. Fix awaiting verification.

Issue R02, reported to ERS: west hall ramp originally ended y15,z1.12; P1 polygon at x0 starts y15.838 with surface1.16. Approx0.84m physical gap and4cm lip. Required correction: extend ramp into polygon and match top height. Fix awaiting verification.

## Coverage plan review
TVC modelling plan explicitly covers real entrance openings, booking block, waiting lounge, offices,toilets,pantry/store, two covered FOBs and stairs to all three bodies, full paths with track structure/points/maintenance detail. This is planned coverage, not verified model coverage.
ERS initial source includes furnished ticket hall/clerks aisle, waiting hall, enquiry/office/lounge, sanitary cubicles/fixtures, rear circulation and ramp. Doors built as openings; room floor plans intentionally reconstructed. East-entry interiors and FOB/canopy implementation not yet reviewed in final source.
NCJ current data has two traced platform outlines, tagged railways, contemporary approach graph and historical facade module; interior build not yet available for review.

## Acceptance checks still required
- All platform/bay faces remain present and correctly labelled in final scene.
- True connected rail graph; turnout hardware at included branch nodes; no buffers on joins or cropped through lines.
- All cartographic paths labelled map-derived; operational siding identities only where actually supported; no invented exact numbering.
- Traversable entrance-to-platform routes, stairs/bridges reach each body; floors overlap without gaps; doorways physically open.
- Furnished interior coverage visible in cutaway and interior renders; roofs removable by coherent collection/object selection.
- No rolling-stock/train objects or rendered trains. Current source intent is train-free; final scene inventory not yet verified.
- Final render and inventory totals kept separate from mapping-way counts and engineering accuracy.

## ERS source geometry review, 13:53 UTC
Worker reports R01 all-vertex adjacency and R02 west ramp changes applied to source; rebuilt scene pending.
- Canopy column centres pass point-in-platform cross-section checks for all generated x locations. Roof edges overhang tapered ends by up to about1.6m; this does not mean columns stand off-platform, but shelter limits are inferred.
- Island/PF1 stair footprints fit the polygons at both proposed bridge positions(-60,120).
- R03: PF6 north bridge staircase ended x136 while mapped PF6 terminates x129.79. Required shortening/reversing or repositioning before scene acceptance. Reported to worker.
- R04: uninterrupted low longitudinal bridge beam at z7.85 crosses the otherwise-open staircase entry. Required segmentation at access openings. Reported.
- R05: east hall floor starts y101.8 while PF6 east boundary at central door is101.627, leaving~0.17m gap. Threshold overlap and matching top level requested.

## NCJ source review,13:55 UTC
- Buffer classification checks distance from endpoint to every segment of other paths, correctly handling joins to interior vertices. Cut-boundary filters present. Inferred links for wholly isolated pit roads are explicitly tagged in path basis; these are reconstructed connectivity, not official topology.
- Central hall top step overlaps the mapped platform at x0: step ends y11.495, platform begins11.274; height difference~0.015m. This central connection is acceptable geometrically.
- R06: hardcoded dense tiling extends outside P1 polygon (near x166, body ymax24.27 but tiles extend~26.98). Polygon clipping requested to avoid paving through track space.
- R07: point boards101+k and chosen five pit-road assignments are generated/inferred; requested explicit object/ledger labelling, not claimed operational identities.
- Source has waiting hall, booking counters, offices,toilets/stalls,electrical/staff rooms, upper rooms with internal stairwell. Final scene/door clearances not yet verified.

## ERS further static geometry review,13:56 UTC
Worker source corrections R03/R04/R05 reported: second bridge moved x100, roof gaps adjusted; bridge lower beam segmented; east threshold supplied. Rebuilt scene pending.
- R08: bridge deck underside7.58 versus OHE messenger7.4–7.7 implies wire/slab intersection. Requested consistent vertical/placement clearance for wires and masts, not a claim of code-compliant engineering clearance.
- R09: independent line/rectangle test confirms mapped rail285881579 intersects reconstructed workshop rectangle x505–535,y86–100. Relocation clear of rail requested. East and west station-building rectangles test clear of rail centrelines.

## ERS corrected scene inspection,13:59 UTC
Independent Blender4.3.2 read of `ERS_full_station_v02.blend` completed successfully.19948 scene objects. Confirmed four retaining platform bodies(1,2/3,4/5,6), bridge decks atx−60 and100, workshop centre(520,168), mixed-date/non-survey scene metadata. No object-name candidates for train,locomotive,wagon,bogie,railcar or rolling stock; this complements source inspection and does not replace image review.
R01–R05,R08,R09 accepted at source/geometry level. Safe workshop footprint(505–535,161–175) and5m-expanded rectangle(500–540,156–180) independently tested clear of all raw mapped rail centrelines. OHE messenger source reduced to6.9–7.2, beneath deck underside7.58; masts excluded near bridges. Final render appearance remains a separate acceptance step.
`ers_scene_review.json` records scene inventory/locations; it contains original analysis, no source pixels.

## TVC source review,14:05–14:07 UTC
R11: narrow platform-end furniture spill found; worker moved benches and fixtures beyond taper and clear of stair zones. Full-node graph adjacency correct. Main hall arcade overlaps P1 atx0. Front/rear room openings implemented.
R13: stair-side FOB truss/chords/grilles initially continuous across landings. Requested access openings retaining upper structure.
R14: kiosk(170,18.8) overlapped north FOB stair envelope. Relocation requested.
R15: three reconstructed workshops initially crossed rails. Independently safe replacement centres(350,120),(−250,130),(−300,145), each checked with expanded footprint±17.5x±11y against all mapped rails; no intersections. Reported for relocation.
R16: bridge piers at y72 inside rail gauge (distance to641650016 centreline0.587m and0.496m at the two bridges). Move supports onto actual platform bodies. Reported.
TVC long boundary lines y225 and140 checked against raw rail segments: no centreline crossings.

## NCJ corrected scene,14:03 UTC
Independent Blender read:11572 objects,two mapped platform bodies,FOB x−90,no rolling-stock name candidates,explicit mixed-date+inferred-links metadata. R06 paving clipping and furniture-midline changes verified in source. R07 source ledger now identifies point101+ labels as fictional review IDs and pit assignments as inferred. R10 bridge stair-side openings verified in source.
R12: old dark facade doorway proxy boxes partially obstruct actual station-manager/parcel-office openings. Requested removing legacy `Annex ground doorway` proxies. Final patched scene pending.

## ERS boundary follow-up,14:07 UTC
R17: east fencey121 crosses actual retained rails at x376.15,385.81,566.94,580,606.94,640.43. Requested omission/relocation of affected fence segments with clearance. Western fence clear. Earlier ERS acceptance covers R01–R05,R08,R09 (seven items); this new boundary issue remains pending.

## Final circulation checks and newly expanded pointwork review,14:10–14:14 UTC
- TVC independent actual-scene raycasts:8/8 clear(heritage entry,heritage-to-P1,and all6FOB stair entries).6596objects;3correct mapped platform bodies. Stock-name matches are maintenance signs only. R11/R13–R16 geometry fixes verified. One inherited scene README sentence still calls canopy a detached study; cleanup requested.
- NCJ independent actual-scene raycasts:4/4 clear(parcel/manager doors,2FOB stair entries).11701objects;2mapped platform bodies;legacy doorway proxies absent. Stock-name match is a review label saying no rolling stock. R12 resolved.
- ERS actual-scene follow-up confirms fencey160,workshop(520,168),4platform bodies,23074objects. R18:new raycasts hit stair-side vertical bridge uprights at y48/68 on both bridges. R19:new noticeframe obstructs central east door. Targeted fixes requested and worker implementing. West hall-to-P1 ray passes. See final_scene_review JSON files for actual observations.

### Pointwork fidelity is a separate unresolved acceptance gate
Parent pixel review correctly identified that mapped centreline adjacency does not establish coherent rail-level switch geometry. Independent source audit: TVC/ERS extrude separate gauge pairs then add heuristic hardware; NCJ cuts rail intersections but toe/blade/frog placement remains heuristic. Existing broad point views do not prove physical fidelity. All workers asked for representative close-ups with node/route IDs and coherent shared stockrails,blade transitions,frog/flangeways,checkrails,bearers; remove duplicate underlying rails/sleepers in repaired junction envelopes and smooth local route transitions. Complex slips may be explicitly simplified, never claimed surveyed.
ERS simple representative suggested:node1008213472 atlocal(563.817,37.329),ways1453154556/285881585/49015817;headings−6.168°,173.693°,166.775°. Nearly straight main pair and6.9° divergence. This coordinate choice is derived map evidence, not a measured switch design.
No final physical-pointwork acceptance yet. Earlier circulation/footprint passes must not be read as pointwork fidelity passes.

## Physical switch/OHE review,14:20–14:27 UTC
Primary dimension guidance in `turnout_dimension_guidance.md` shared with all workers.45mm normal crossing/check clearance used as visual target; longitudinal cuts must account for angle. TVC unioned plan geometry improves overlap handling; checkrail/flare offsets corrected before rebuild. ERS revised source has intersection-derived rail cuts,tapered replacement blades,and unified bearers;100mm centre inset yields45mm clear given60mm runninghead+50mm checkhead. Actual close-up pending,so physical pointwork not yet passed.

Analytic OHE footing clearance sweep generated `ers_ohe_clearance_review.json`, `tvc_ohe_clearance_review.json`, `ncj_ohe_clearance_review.json` (derived cartographic audit; OSM notice applies). Source-planned legs/masts were compared against ALL rail segments. Gross-conflict thresholds1.25/1.35m are intentionally only physical-interference flags,not approved loading gauges:
- ERS:37of175 candidate masts flagged; minimum0.103m from another railcentre. Fixed y+2.75 route offset is inadequate at convergence.
- TVC:3of64 portal legs flagged,at(65,120),(200,120),(245,120).
- NCJ:5of52 portal legs flagged,at(−396,−4),(−342,−4),(−180,−4),(360,75),(630,75).
All workers asked to move/select supports against complete local railway envelope or use shared portals beyond tracks. Final acceptance awaits corrected placements and close-up pointwork pixels.

## Physical turnout proof review,14:27–14:31 UTC
NCJ actual render `17_PHYSICAL_TURNOUT_6045464001.png` inspected alongside repair source/QA. Clear improvement: source-fitted eased closure,tapered tongues,explicit V/wing/check assembly,one bearer array and common stock pair.46mm check clearance calculated correctly for65mm railheads. Asked for wider proof framing because part of toe/closure extent is cropped; floating registration hardware remains on worker's OHE correction list.
Important repair overreach found: rectangular batch deletion removed24sleepers on neighboring route514385390 outside new commonbearer reach. Atlocalu0 neighborv−5.087 while bearer reaches only−1.391; preserve unrelated-route ties or delete only within replacementbearer coverage. Sent before20-case rollout.14compound/short/degree4 exclusions require explicit coherent crossing treatment rather than silent retention of old overlays.
TVC source now partitions separately editable tongue heads instead of additive overlays,45mm directly-adjacent flange channels,corrected checkrail/flare placement,and OHE legs≥2.9m from all mapped centrelines. Rebuild/pixel proof pending.
ERS source now selects OHE mast sides/offsets by minimum2.35m all-route clearance,skipping unsolved placements. Asked to physically connect support stem/insulators/registration links to actual sagged messenger/contact to avoid floating detail. Physical turnout source has correct45mm checkclearance but final actualclose-up still pending.

## ERS actual pointwork render rejection,14:36 UTC
Inspected new `13_Turnout_frog_detail.png` and `05_Track_turnouts.png`. Full-width running rails terminate across large empty intervals at the crossing. Source cuts both rails over±(halfhead+gap)/sin(angle),then starts downstream V-nose at(halfhead+gap)/sin(angle/2),without wingrails restoring running support around continuous wheel channels. This is not accepted physical pointwork. Requested planar head union minus continuous normal-width flange channels or an explicit connected wing/V assembly. Further cosmetic narrowing alone is insufficient. OHE clearance source improved,but some registration still visibly disconnected in wide view. Parent andworker notified; revised proof required.

## ERS proposed casting channel interaction,14:39 UTC
Lightweight independent planar diagnostic of new local casting source found9of110 envelopes whose remaining solid overlaps a third route's flangechannel when only the two event channels are subtracted. Includes representative vicinity event108(563.966,38.186),pairs1453154556/49015817 affecting285881585 side+1. Exact hits in `ers_casting_channel_review.json`; file is derived map/geometry analysis with OSM provenance. Worker asked to subtract every locally intersecting flangechannel or use global union/difference before next proof. No Blender memory load used for this check.

## Actual union-mesh verification,14:44 UTC
ERS switched to global railhead union with all-route flangechannel subtraction. Independently reconstructed top-surface polygons from `ers/geometry/rail_solids.json` vertices/faces,including separate blade meshes,and intersected with every generated45mm channel. With2µm interior trim to accommodate six-decimal-metre quantization:channel intrusion area0.0m²;head/blade overlap2.2e−10m². PASS for generated runninghead/blade geometry. Earlier9localcasting failures superseded by this method.
Same actual-mesh test for `tvc/source/running_rails_mesh.json`:channel intrusion0.0m²;head/blade overlap0.0m². PASS.
Reports: `ers_union_mesh_verification.json`, `tvc_union_mesh_verification.json`. These are geometric checks of actual serialized meshes,not merely source assertions. Final scene must remove old overlays; checkrail/bearer/OHE assembly and actual rendered closeups remain separate acceptance steps. No new Blender process used.

## Service infrastructure collision audit,14:47–14:52 UTC
Parent expanded acceptance to pipes,troughs and maintenance walks. Source-based reports:`service_collision_review.json`,`ncj_pit_services_review.json`.
- TVC legacytroughy72 crosses13mapped points;y121 crosses5. Worker already replacing with rail-clear segments and unioned ballast. Currentpoint pixels show credible unioned crossing,but oldtrough obstruction and overlapping sleeper/bearer arrays still require final cleanup.
- ERS initial exposedwatermain crossed railheads at3points. Worker changed to below-track ducts/drains and rail-distance-filtered exposed/buried water runs. Independent fullsegment check of updated source found minimum exposed/transition centreline clearance2.2399m,not guaranteed2.5m because2m discretization. No gross interference; report`ers_service_fix_verification.json`. Finalscene must useupdatedsource.
- NCJ six straight-chord pitwalkways cross own or neighboring railcentrelines.128wateringrisers within1.2m of tracks,one3mm from514385390centre. Source-chord placement is not equivalent to curving map alignment. Requested map-following segmented supports/services withall-route avoidance or genuinely straight clearpit spans. Raised trough/drain rows also cross routes; buried/culverted treatment or trimming needed.

## Revised NCJ pit/service plan verification,14:56 UTC
Independent analytic test of proposed `repair_ncj_pits.py` covers full3m walkway rectangles and hosehorizontalpaths,not justmidpoints. Minimum walkway edge distance to any mapped railcentre1.5055m; minimumhosepathdistance1.4999m. PASS gross interference. Allfive inferred maintenance assignments retain approximately414,300,408,279,312m clear pitsegments. `ncj_pit_plan_verification.json` records values. New service repair sinks affected lid/grate components and replaces raised continuous drainwalls with below-formation culvertsegments. Source assessment positive; actual scene application/pitcutaway stillpending.

## ERS new actual union-pointwork proof,15:03 UTC
Re-inspected freshly regenerated `13_Turnout_frog_detail.png` after globalunion loader. Prior longunsupported railgaps are resolved; supporting nose/wing geometry and continuouschannels are visibly coherent. Representative runninghead reconstruction accepted as generic visual pointwork,complementing actual JSONallchannel tests. Not engineering certification or a surveyed manufacturer turnout.
Remaining presentation/formation issue:darkrectangular ballast gaps appear between bearers. Source has oldper-route stripbedtop andnewsharedbedtop bothat0.32m,coplanar overlap; striptop winding also pointsinward for+X path. Worker/root notified to union/replace overlapping bed surfaces and orient caps outward. Railhead algorithm shouldnot be reopened for this separate issue.

## NCJ acceptance,15:12 UTC
Actual final17wide,18frog and19toe proof images independently inspected. Coherent V/wing/check assembly,tapered open/closed tongues,connecting hardware and aligned support are visible; prior voids/floating details resolved. NCJ accepted as a detailed generic visual reconstruction,with20simple and14explicitly approximatecompound treatments. FinalOHE/service/pit reports align with independent source checks. No remaining known NCJaudit blockers. Mixed-date,unmeasured-room,pit-assignment andexact-turnout-type limitations remain. Finalexport synchronization is owned by builder/publication.
Machine-readable currentstatus is `current_review_status.json`; older failures in this chronological ledger are retained for traceability,not current rejection.

## TVC acceptance,15:26 UTC
Updated15_Frog_closeup and10_Turnout_detail actual pixels independently inspected. Corrected foreground pointwork has open45mm channels,shared stock/wing/nose support,unobstructed trough alignment and a single bearer grid. Earlier foregroundformation voids are resolved. TVC accepted as a generic visual reconstruction. Worker confirms these are currentacceptedpoint proofs; a finalbake still incorporates scattertidy andall-route propclearance improvements without altering accepted pointwork. Export/scene synchronization remains toconfirm.
`current_review_status.json` now includes SHA-256 hashes of accepted NCJ/TVC proof images so image revisions are explicit.

## Review closed,15:32 UTC
Corrected ERS13 actual proof independently inspected and accepted. Unioned bed is continuous; earlier black formation voids are absent; coherent frog/channel detail retained. Image and frozen-scene hashes are recorded in current_review_status.json, with the actual blend independently hashed against the proof record.
All three core visual-reconstruction audits now pass. TVC staged scatter/prop-clearance final bake/export synchronization remains pending with its builder; no need to continue this audit for every gallery frame. FINAL_AUDIT.md is the concise current conclusion and states all source/survey limits.
