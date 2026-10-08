# MQO footbridge correction record

Resolved in the [corrected revision_02 model](../revision_02/mqo/README.md). Use that model and its [current gallery](../revision_02/mqo/GALLERY.md). The original source/export and earlier reviews remain preserved as historical checkpoints.

## Finding in the original checkpoint

Exact published mesh measurements found an approximately 0.702 m final rise from both stair approaches to the deck. Earlier high headroom rays had missed this lower-body and foot-level transition. [Superseding review](../../qa/reports/MQO_SUPERSEDING_REVIEW.json) and [original-mesh evidence](../../qa/reports/MQO_exact_deck_transition.json) document the defect.

## Accepted correction

The narrow bridge patch moves the stair endpoints to the deck edges and aligns the walking surfaces. Renewed independent checks passed all 24 low/waist/head clearance rays and confirmed matching 8.6000004 m surface probes immediately before and after both transitions. [Renewed acceptance](../../qa/reports/MQO_v02_ACCEPTED.json) records the exact final hashes and scoped limitations.

Corrected Blender SHA256: `180d186b075c31a44773fb855b73c4ab43c8b374d7ec7f4b0bb62c159f2ddb4d`. Corrected GLB SHA256: `b86fe0b6590c8c16096f9e838c68c49dcfeb08237baf07f17c64ad86eeefd9ee`. Original Blender SHA256: `950cf176f29fc8cb21420a3887f5d782801d77a390be513d24840c4cf4edb4b1`.

Views 01–03 were rerendered from the corrected scene. Facade/interior views 04–05 retain their explicitly recorded original source hash because their subjects, materials, cameras and lighting were unchanged. `BRIDGE_REVISION.json` and the exact repair script accompany the replacement. File basenames retain `v01`; the `revision_02` directory and authoritative hashes identify the corrected version.

KUMM is unaffected. These are visual reconstructions and scoped QA checks, not real-world engineering or safety certifications.
