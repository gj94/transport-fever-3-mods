# Turnout visual-dimension guidance
Verified primary references,2026-10-08. For credible generic visual geometry, not certification or proof of station-specific design.

## Primary dimensional basis
IRISET *Signalling General*,section4.6.4,printed46, specifies44–48mm for checkrail opposite crossing nose and wingrail at crossing nose on1676mm gauge; its1673mm turnout note uses41–45mm.
https://nfr.indianrailways.gov.in/uploads/files/1567770997122-S8.pdf

RDSO-hosted CAMTECH *Do's and Don'ts on Points and Crossings*,March2000,printed9, independently lists BG44–48mm crossing/check clearance. It stresses applicable SOD and relevant drawing rather than one universal station construction.
https://rdso.indianrailways.gov.in/works/uploads/File/Handbook%20on%20Dos%20and%20Donts%20on%20Points%20and%20crossings%281%29.pdf

Use0.045m clear normal face-to-face gap as a visual nominal for these scenes' chosen1.676m gauge. A0.150m actual crossing flangeway is excessive. Open-switch toe throw is a different dimension and must not be substituted for frog/checkrail clearance.

## Computation checks
- Measure clear passage perpendicular to appropriate running/guiding faces, not between their centrelines.
- An oblique rail intersection requires a longer along-rail cut; its length depends on the obstructing rail-head width, intended gap and intersection angle. A45mm along-rail deletion does not guarantee45mm transverse wheel passage. Use planar channel subtraction or explicit face offsets and validate cross-sections.
- TVC current nominal head centres±0.872m,halfhead0.034m give innerfaces±0.838m. A45mm channel immediately inward from a positive railface spans0.793–0.838m,centre0.8155,halfwidth0.0225. Reflect for negative side.
- With checkhead halfwidth0.031m, opposite checkrail centre magnitude0.762m gives .838−(.762+.031)=.045m clearance. A0.70m centre gives107mm, not45mm.
- Flare checkrail ends AWAY from adjacent stockrail,toward track centre, increasing entry clearance. Flared ends must never converge across the runningrail.
- Merge duplicate coincident stockrail footprints. Trim underlying independent gauge pairs where a coherent switch replaces them. Do not leave two stockheads or intersecting full-width bars in the flange passage.
- A fixed unioned crossing nose is not a moving switch: explicitly model tapered tongue rails with a believable toe/heel transition, one closed path and one open tongue; correct stretcher/drive relationship; aligned/extended bearers.
- Keep complex slip geometry labelled simplified where actual engineering plan is unavailable. Maintain coherent wheel paths rather than pretending exact survey.

## Current review status
TVC diagnostic of641863869/641863876 shows unioned heads and cut crossing channels, an improvement over overlays.45mm channel placement,checkrail offset/flare and switch tongues requested for correction before acceptance. Representative actual Blender close-ups required for all stations. Graph connectivity and architectural circulation passes do not constitute physical pointwork acceptance.
