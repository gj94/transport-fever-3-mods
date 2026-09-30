# Visual QA

## Current TF3 integration — pack v1.0

Pack v1.0 uses the corrected WAP-7 geometry and the newer class-specific ICF/LHB family masters. Their CBC datums are preserved in native resources. The fixture below documents the older source pairing; runtime curves and dynamic clearance remain pending. See [current installation and validation](../TF3-INSTALL.md).

## Original source review

Reviewed final three PNG views: paired closeup, top and widened full straight overview. Both complete vehicles remain present; no body/gangway parts hidden to simulate a connection.

- Matching closed heads meet on a narrow stepped seam and interleave across the datum
- Shanks run into draft pockets; ICF rods meet buffer plates
- Side-buffer axes align, with the intentional 90 mm face gap
- Complete bodies retain approximately 1.160 m shell/end-wall clearance
- These are simplified matched CBC visual castings, not a functional or dimensionally certified H-type assembly
- Mathematical/static geometric checks and fresh FBX import pass; no TF3 runtime/curve test is claimed

CPU Cycles, two threads, 32 samples, denoising disabled. Grain is retained intentionally. The closeup is 1100×740; final overview 1100×580. The top view provides complementary plan-profile inspection.

The un-beveled opposed head outlines share a stepped boundary analytically. The 1 mm point-in-polygon test uses actual assembled mesh vertex positions and records zero interior-overlap samples; it is sampling, not an exact solid-intersection solver. Small bevel relief is visible at the seam.
