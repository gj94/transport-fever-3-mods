# ICF running gear focused audit

## Scope

Original procedural conventional ICF all-coil, tread-braked self-generating coach equipment. Both non-AC and underslung split-AC branches were tested in Blender 4.3.2. No old source assets, native game packages, main shell, core helper, or build script were edited by this component audit.

## Repairs in v02.3

- Replaced duplicated pressure-vessel pole rings with single shared vertices and triangle fans. The baseline auxiliary and control reservoirs each had 80 non-manifold edges; both now have closed manifold surfaces.
- Seated all primary and secondary coil springs against the matching rubber pads and upper seats. The lower secondary pads now contact the spring trays.
- Moved brake block working width clear of the wheel flange-root transition.
- Corrected the non-AC four-groove pulley face from 76 mm to the reference 136.5 mm. Kept the 572.6/200 mm pitch diameter pair and four-belt versus double-ended six-plus-six belt configurations. AC face width and small groove profiles remain visual interpretations.
- Replaced round-tube belt sections with continuous trapezoidal V-sections while retaining true external tangent paths.
- Moved alternators away from intersecting the lower spring cradle. End-shield clearance to the nearest transverse plank is now at least 48 mm. AC pulley placement remains inside the wheels.
- Connected alternator suspension arms to a transom-mounted crossbar and added a vertical tension-bracket support.
- Added separate alternator rotor roots. Driven pulleys can rotate without turning the barrel, cooling fins, belts, or axleboxes. No runtime animation is claimed.

## Verification

Run from the package root:

    blender -b -t 1 --python scripts/qa_icf_running_gear.py
    blender -b -t 1 --python scripts/qa_icf_running_gear.py -- --ac

Optional `--render` creates a small exposed first-bogie proof. The test writes `gear_audit_nonAC.json` and `gear_audit_AC.json`, each tied to the component source SHA-256. The saved baseline is `gear_audit_baseline_nonAC.json`.

Tests measure mesh geometry and transform sampled vertices. Coverage includes pivot spacing, wheelbase, axle height, 915 mm tread diameter, side bearer spacing, frame length, actual spring-seat contact, alternator/plank clearance, pulley groove counts and widths, independent wheel and alternator rotation, bogie yaw isolation, counts of wheels/springs/brake blocks/belts, manifold edges, zero-length edges, degenerate faces, finite coordinates and outward closed-surface signed volumes.

Passing component surface/parenting checks do not certify every pairwise assembly clearance, operational suspension travel, manufacturing drawing conformity, complete-coach appearance, or game conversion.

## Public railway references reviewed

- [ICF maintenance manual, bogies](https://scr.indianrailways.gov.in/uploads/files/1341833527005-Bogies.PDF): Figure 3.1 nominal bogie layout and leading dimensions. The official indexed drawing excerpt was available; direct PDF retrieval timed out in this audit.
- [CAMTECH BVZI IOH, 2012](https://indianrailways.gov.in/railwayboard/uploads/directorate/eff_res/camtech/mechanical/YearWise/Procedure%20for%20IOH%20of%20Broad%20gauge%20BVZI.pdf): ICF bogie component relationships, all-coil suspension, oil-bath side bearers, anchor links, BSS hangers, tread-brake rigging and safety ropes. It concerns a brake van; coach equipment dimensions were not inferred from its vehicle body.
- [RDSO V-belt specification, Appendix A](https://rdso.indianrailways.gov.in/works/uploads/File/New%20spec_v-belt_%20revesion1.pdf): official indexed table confirms four-belt non-AC drive, 136.5 mm face width, 572.6 and 200 mm pulley pitch diameters, and double-ended six-belt AC drive. Full direct retrieval failed; the inspected indexed table was sufficient for those narrow checks.
- Existing component references for [train lighting](https://scr.indianrailways.gov.in/uploads/files/1341896144130-Train%20Light.PDF) and [air conditioning](https://scr.indianrailways.gov.in/uploads/files/1341832085307-Air%20Conditioning.PDF) were attempted but direct retrieval failed. Their unavailable text was not treated as fresh verification.
