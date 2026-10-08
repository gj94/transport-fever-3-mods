# Final geometry QA — TVC v02

Authoritative scene SHA256: `e724b331bf99cfdc7cbd06ec7349e6314d4f551c25f80da530817437cb849261`.

- 6,709 objects; 3,727,944 editable mesh vertices, in metres.
- 46 mapped railway ways; 16,562.10 m summed route length within the full 1.64 km model envelope. Three physical platform bodies, five passenger faces.
- Complete-node graph recognises 50 junctions and 25 genuine dead ends; crop-boundary approaches do not receive buffers.
- Nominal clear gauge 1.676 m, head centres ±0.872 m / head width 0.068 m. Actual 45 mm flange-channel cuts and separately editable tongue regions; 45 off-node crossing assemblies have checkrails.
- Independent geometry review found zero rail-head/blade overlap with the generated flange-channel interiors (2 µm rounding tolerance), and zero overlapping head/blade areas. This verifies the generic visual construction, not an approved railway switch design.
- Angular ballast pieces use 30–60 mm XY sizes and are rejected against every rail/flangeway, PSC sleeper and timber-bearer footprint. Single-grid timber supports replace overlapping tie arrays. The ballast bed is a unioned footprint, eliminating coplanar formation overlaps.
- Portal legs use ≥2.9 m all-route centreline clearance. Signal/marker/cabinet/vegetation placements use explicit clearance helpers; maintenance water pipes/walkways follow the map and reject track conflicts.
- Six full stair flights passed 684 actual evaluated-mesh headroom samples at centre and ±0.9 m across the flight, with 2.0 m vertical test height and zero hits. An overlong landing was caught and corrected. See STAIR_CLEARANCE_QA.json for scope.
- Earlier actual-scene entry/landing tests passed all eight tested circulation rays. New front ramps connect the heritage entry and separate booking block to their .85 m floor level; the booking ramp has a clear forecourt-fence opening.
- No trains or other rolling-stock objects. Road autorickshaws remain as forecourt context.
- Packed original trilingual signage and fonts; procedural materials need no external photographic maps. Rail caps/platform tops/roof sheets use corrected outward winding.

## Visual corrections made during review
The review removed floating interior clerestory panels, separated the lounge TV from its information board, moved the receiver above the doorway, relocated an overlapping office roster board, opened the footbridge side rails at every landing, cut shelter roofs/purlins around whole stair flights, relocated workshops and OHE legs away from rails, removed a crossing cable trough, and removed duplicate turnout bearers.

## Honest limits
Railway XY is mixed-date OSM-derived, not a 2022 as-built. Heritage detail is photo-derived; unknown room plans, room sizes, structures, platform Z, signal identities and service-building siting are reconstructed. This is not a train-clearance or civil-engineering certification.

## Gallery provenance
All pictures are actual Blender renders or the separately labelled map/mesh diagrams. Per-image JSON records source blend hashes, renderer and any presentation-only exclusions. Some accepted component previews predate unrelated final changes; their original hashes are retained rather than rewritten. Camera-local Eevee interior views hide listed distant yard/urban collections for efficient review; the saved blend retains the complete station. Full campus/exterior views use the complete scene in Cycles. Denoising was disabled; Cycles images can retain visible grain.

Exchange validation and the final delivery manifest are generated after the export step.
