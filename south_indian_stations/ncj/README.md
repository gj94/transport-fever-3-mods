# Nagercoil Junction · NCJ · 2010 architectural asset

An editable, metre-scale Blender reconstruction of the distinctive peach-and-ivory street frontage, based on two dated, visually inspected photographs. **This is a photo-informed historical visualization, not an as-built survey or the redeveloped 2026 station.**

## Files and use
- `NCJ_2010_station.blend`: portable master, editable meshes, fonts packed, procedural materials, four cameras.
- `exports/NCJ_2010_station.glb`: portable mesh/material interchange. Blender procedural weathering has no exact glTF equivalent; the export retains base PBR material values.
- `scripts/build_ncj.py`: deterministic reproducible geometry/material/export builder, Blender 4.3+.
- `renders/`: four real Blender Cycles views (40 samples, denoised, four CPU threads).
- `dimensions.csv`: chosen dimensions with confidence and provenance.
- `QA.json`: automated scene checks. `VISUAL_QA.md` records pixel inspection.
- `references/`: source photographs and source credits. The reference photos are not pasted onto the model.

Run from any directory: `blender -b -t 4 --python scripts/build_ncj.py -- --render`. The script resolves paths relative to itself. Noto Sans Tamil, Noto Sans Devanagari and DejaVu fonts are used; install the matching system fonts before rebuilding on a different computer. The supplied master packs its fonts.

## Architectural reading
The January main photograph shows a tall two-storey portico with twelve visible slender rectangular columns and eleven principal advertising bays, stepped bracket capitals, a salmon entablature, a broad white cornice, and a rounded roof-front silhouette. Separate rooftop boards carry English in red, Tamil and Hindi in blue. A bare flagpole rises behind them. The lower left wing uses smaller columns and similar stepped capitals at two levels, with barred windows and a red-oxide veranda floor.

The October side photograph confirms the lower veranda, striped kerbs, the peach annex with dark horizontal upper windows, raised roof fins and a covered link. It is a **street/forecourt side view**, not a platform-side photograph. Consequently the rear facade, building depths, interiors, track and platform canopy in this asset are explicitly inferred/contextual. The model does not claim to reproduce the station yard, its full platform length or a platform count.

The advertising panel rhythm is a major identifying feature. The geometry reproduces the physical panel arrangement, while the artwork is newly drawn, unbranded geometric jewellery-inspired design. It does not reproduce the photographed Shajahans advertisement artwork, logos or portraits. Road vehicles are original simplified auto-rickshaw meshes, included as scale/context props.

## Collections
- `01_MAIN_2010_PHOTO`: primary portico, true entrance openings, mezzanine, columns/corbels, roof and replaceable advertisement panels.
- `02_LEFT_VERANDA_2010_PHOTO`: lower two-storey wing and barred openings.
- `03_ANNEX_PHOTO_INFERRED`: photo-supported annex form; dimensions/attachment inferred.
- `04_SIGNAGE`: three nameboards and pole.
- `05_FORECOURT`: steps, access ramp/rails, paving, drains and kerbs.
- `06_PLATFORM_CONTEXT_NOT_SURVEYED`: removable 84 m platform/canopy scene module.
- `07_TRACK_CONTEXT`: removable 92 m straight illustrative broad-gauge track. No turnouts or invented yard.
- `08_SET_DRESSING`: original props, palms and lamps.
- `09_LIGHTS_CAMERAS`: presentation setup, safe to exclude from downstream exports.

The X axis follows the frontage/illustrative track; negative Y is the street. Z is up. Forecourt grade is Z≈0. Rail top is Z=0.571 m and platform top is Z=0.87 m in the contextual scene; their relative offset is a visualization choice, **not a verified NCJ platform height**. Move/rebuild these modules for operational simulation.

## Limits and licences
Read `SOURCES_AND_LICENCES.md`. All building dimensions are proportional estimates or composition choices, with no surveyed measurements. The photos span January to October 2010 and show changing advertisements; the asset's unbranded panels make this mixed seasonal evidence explicit. Unseen right/rear walls are simplified. No current electrification/FOB/yard renewal is imported into this historical scene. Terrain and palms are scenic placement rather than topographic reconstruction.
