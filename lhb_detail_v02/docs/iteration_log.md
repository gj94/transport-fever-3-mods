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
