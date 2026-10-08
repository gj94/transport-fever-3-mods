# QA scope

## What the numeric tests establish
The scene uses metric1:1 scale, finite mesh vertices, packed font data and zero rolling-stock objects. The gauge is explicitly constructed from1.741m rail-head-centre spacing minus65mm head width. Full platform geometry spans841.63m and563.79m. A source-derived polyline graph covers the yard plus the three directional approaches, with an explicit approach clip envelope rather than silently shortened platforms.

Actual Blender ray casts check access through the main entrance, hall-to-platform portal, waiting room entrance, toilet entrance and both footbridge stair entrances. An independent source/scene review additionally checked the parcel-office and station-manager doorways. These checks test these specific clear lines, not a complete human navigation simulation or accessibility certification.

## What visual review must establish
Every delivered render is generated from the actual Blender scene. Interiors are reviewed separately from the facade. The top-down overview has review-only labels; closeups cover platform fixtures, inspection pits and crossing/rail-fastening detail. Low-sample draft images are replaced by final renders, not presented as the finished preview set.

## Limits
No certified NCJ signalling plan, interior measured survey or station-wide as-built engineering drawing was obtained. Therefore point names/numbers, signal positions, pit assignments, inferred missing connections and interior layouts are explicit original reconstructions. Neither route geometry nor visual equipment is suitable for operational railway design, interlocking validation or engineering construction.

The environment has no OIDN support; denoising is disabled. Final image sample counts are128 indoors and48 outdoors at1400×900. Four CPU threads are used. Memory-constrained processes are run sequentially. The packed editable Blender file is the primary deliverable; the GLB is a large portable alternative distributed compressed.
