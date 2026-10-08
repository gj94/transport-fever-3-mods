# Ernakulam Junction (ERS) • 2017 station asset

A richly detailed modular visual reconstruction of Ernakulam South before major redevelopment. Designed to accompany full-size Indian rolling stock, without pretending to be a surveyed full station or reproducing a proposed new terminal.

## Open the asset
- `ERS_2017_station.blend`: editable named geometry, packed sign artwork, procedural materials, four cameras, metre units.
- `exports/ERS_2017_station.glb`: portable geometry/material exchange asset. Does not include cameras or lighting. Import into a metre-based scene; test simulator requirements separately.
- `renders/`: four actual Blender renders, generated from the saved model.
- `build_ers.py`: reproducible Blender 4.3+ source.
- `make_signs.py`: original multilingual signs, with correctly shaped Malayalam/Devanagari using Pillow/RAQM and Noto fonts.

Run from any directory:

```sh
blender -b -t 4 --python /path/to/ers/build_ers.py -- --render
```

The distributed textures are sufficient for rebuilding. `make_signs.py` only needs to run to change text; it expects Noto Sans fonts at standard Linux font paths. It does not need reference photographs to build. Every image used by the `.blend` is packed. Rendering uses Cycles CPU, four threads and 64 samples (this Blender build lacks OpenImageDenoise) at 1600 × 1000.

## What is recognizably ERS
2017 white/blue portal with clock, trilingual roofline and yellow awning signs; low left wing; taller screened right gallery with strong fins and shallow curved parapets. Trackside modules reproduce the silver lattice pedestrian bridge, blue hooded stair, low steel/corrugated canopy, red platform wall, pointed yellow nameboard, blue service pipe and green/yellow catering stall observed in the paired November 2017 photos.

The six numbered platforms are **not** reconstructed as six invented islands. The model includes one shortened platform and two sample broad-gauge tracks solely to demonstrate component scale and rolling-stock placement. Platform 13 is not invented: the sign marked 13 is labelled coach position, as in the photograph.

## Collections / editing
1. WEST FRONTAGE: photo-inspired frontage and open portal, main building shells, genuine doorway voids, gallery glazing/mullions.
2. FORECOURT: configurable parking marks, benches, bollards, planters/palms, lamps.
3. PLATFORM KIT: configurable 96 m demonstration, 8 m canopy bays, furniture, kiosk and nameboards.
4. TRACK MODULES: two 1.675 m gauge sample lines with rail head/web/foot, sleepers, plates, ballast and utility pipe.
5. OHE MODULE: indicative configurable electrification masts, cantilevers, insulators, contact/catenary wires.
6. FOOTBRIDGE KIT: individual truss chords, X members and railings, tread/riser staircase, handrails and blue hood.
90. PRESENTATION: cameras and lights; removable for game import.

Move/duplicate collections as modules. The source constants define platform length and member spacing. Geometry is editable and named, with lightweight bevel/solidify modifiers where useful. GLB is an exchange asset, not engine-specific optimized LOD, collision or route signalling. No proprietary textures, train assets or external image dependencies.

## Accuracy and limits
All dimensions except units and nominal broad gauge are inferred or adjusted for the scene. Rear walls, depths, interior ticket windows, furniture distribution, ornamental planting and demo track alignment are artistic completion. No survey, route-ready yard, present-day redevelopment, passenger simulation, working signalling, or safety-critical clearance claim. Refer to `DIMENSIONS.csv`, `SOURCES.md` and `QA.md` before reuse.

## Licence
CC BY-SA 4.0 for original model/artwork and included reference photos; credit the original photo authors when redistributing the reference bundle. See `SOURCES.md`. No official railway endorsement.
