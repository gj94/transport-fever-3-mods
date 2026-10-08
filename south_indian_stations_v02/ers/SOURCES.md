# V02 evidence and reconstruction ledger
The v02 gauge is exactly 1.676m between inner rail-head faces on straight sections.

## Primary mapped geometry
OpenStreetMap contributors, API bbox76.285,9.960,76.300,9.980, retrieved2026-10-08: https://api.openstreetmap.org/api/0.6/map?bbox=76.285,9.960,76.300,9.980 . The local filtered `references/osm_rail.json` is a derivative geographic dataset. Attribution: © OpenStreetMap contributors; https://www.openstreetmap.org/copyright . Dataset licence: Open Database Licence1.0, https://opendatacommons.org/licenses/odbl/1-0/ . OSM last-edit dates are not construction dates. Platform polygons were edited2023–24; some route ways2025–26. No historical snapshot was verified. Consequently this model is explicitly a2017 photo-derived architectural reconstruction on a mixed-date mapped station yard, NOT a survey or verified2017 as-built asset.

Actual derived map pixels were inspected before building. Four distinct polygons retain six faces: west PF1, island PF2/3, island PF4/5, eastern PF6. Their staggered ends and curved southern PF6 are preserved; they are not normalized to identical lengths. Rail paths, sidings and crossover connections use all adjacent map vertices; graph branch degree is computed across internal vertices as well as way endpoints. The regional ERSD marshalling/coaching depot1.5km away is a separate facility and is not silently collapsed into the station.

## Independent primary historical / functional evidence
- Ministry of Railways, Lok Sabha question1047,8Feb2023, confirms ERS10 lines/6 platform lines and distinguishes coaching depot5 stabling/3 pit lines. https://eparlib.sansad.in/bitstream/123456789/1470550/1/AU1047.pdf . Supports track/face count and separate-depot distinction, not exact turnout plan.
- Southern Railway General Manager annual report2015–16: PF2/3 paired works, PF4/5 paired works, FOB extension toward Karshaka Road eastern entry. https://sr.indianrailways.gov.in/cris/uploads/files/1688799706975-gm%20report%202015%2016.pdf . Supports paired-island organization and east access pre2017.
- NTCA-hosted Sabarimala Master Plan, Vol2 Traffic and Transportation, surveys2005–06, printedp73/PDFp75: eastern second entry has booking counter/passenger waiting hall and forecourt parking. https://ntca.gov.in/assets/uploads/Reports/sabarimala/Vol2_Traffic_transportation.pdf . Supports east interior functions, not furniture locations or design details.
- Indian Railways Schedule of Dimensions: https://irimee.indianrailways.gov.in/instt/uploads/files/1454673172611-sod.pdf . Gauge standard1.676m.

## Excluded future proposals
2022+ redevelopment architecture is not used as the2017 facade. Platform extension proposals reported2026 are not implemented as if as-built. Contemporary map geometry has an explicit mixed-date limitation rather than implied historical fidelity.

## Explicit reconstruction
Counter count/layout, room partitions, washrooms, office furniture, waiting seating, signs other than photo-derived identity, lamp/canopy spacing, bridge locations, detailed point machines/blades/frogs/checkrails, signal placement, workshop, utility distribution and surroundings are purposeful complete-model reconstructions. The connected mapped route centreline geometry does not certify every turnout frog geometry or operational interlocking as an engineering asset. Track component dimensions are realistic modelling targets. No rolling stock is included.

## Rights
No new licence is granted to generated scene, scripts, signs or renders. Retained photo-source attribution remains. Raw third-party photos are not redistributed. OSM-derived data and trace-based geometry retain their stated provenance/licensing obligations; generated asset rights are not asserted to override them. No endorsement or legal clearance is implied.

# Retained architecture photography
These references ground the2017 architectural baseline, not a historical yard survey. Actual image pixels were inspected.

1. **Shady59**, *Ernakulam Junction Railway Station.jpg*, photographed 2 August 2017 21:19:11, own work, **CC BY-SA 4.0**. Main west frontage/night reference. https://commons.wikimedia.org/wiki/File:Ernakulam_Junction_Railway_Station.jpg
   - Local: `references/night.jpg` (unmodified original in the working research cache; omitted from the lightweight deliverable).
   - Observed: white rectangular entry spandrel, broad cobalt blue curved portal and diagonal legs; continuous top trilingual sign; yellow trilingual awning fascia; clock; low left wing and blue horizontal strip; taller asymmetrical right wing with white fins, curved parapet, dark screened gallery; paved forecourt, lamps, palms, parking.
2. **KannanVM**, *Ernakulam Junction Railway station.jpg*, photographed 19 November 2017 14:41:22, own work, **CC BY-SA 4.0**. https://commons.wikimedia.org/wiki/File:Ernakulam_Junction_Railway_station.jpg
   - Local: `references/day.jpg` (unmodified original in the working research cache; omitted from the lightweight deliverable).
   - Observed: weathered yellow station board with regional scripts and pointed posts; silver lattice pedestrian bridge, horizontal guardrails, covered stair flight; grey corrugated roofing; red platform retaining wall/pale coping; overhead traction equipment; blue water pipe; white relay cabinets; broad-gauge track.
3. **KannanVM**, *Ernakulam Junction Railway station Platform.jpg*, photographed 19 November 2017 14:40:49, own work, **CC BY-SA 4.0**. https://commons.wikimedia.org/wiki/File:Ernakulam_Junction_Railway_station_Platform.jpg
   - Local: `references/platform.jpg` (unmodified original in the working research cache; omitted from the lightweight deliverable).
   - Observed: low open steel platform canopy, corrugated grey sheet, blue covered stair hood, green/yellow catering kiosk with product shelves, red waste bin, silver bridge behind. The visible **13 is a coach-position board, not platform 13**.

Image licence: https://creativecommons.org/licenses/by-sa/4.0/
Photographs are reference documentation, not projected onto geometry or used as material textures. No endorsement by photographers, Wikimedia, Southern Railway or Indian Railways is implied.

## Generated asset rights and reference-use limits
No new open-source or Creative Commons licence is granted for the generated `.blend`, geometry export, scripts, renders or sign artwork. The repository's existing no-open-source-licence default is preserved. The CC BY-SA notices above apply to the named third-party photographs only, not automatically to these generated files.

The photographs were used as visual reference; no photograph pixels are projected onto geometry or included in the model materials. The model interprets visible architecture with simplified 3D assemblies, photo-inferred dimensions, reconstructed materials, typeset signs, full mapped platforms and artistic component placement. Whether any particular reconstruction constitutes an adaptation, or requires additional permission, has not been legally determined. Attribution is not a claim of legal clearance. Raw reference photographs and crops are excluded from the deliverable; the source URLs remain for research/provenance.

Sign textures are original Pillow/RAQM typesetting. Malayalam and Devanagari glyphs use installed Noto Sans fonts, SIL Open Font License 1.1. English uses Noto Sans Bold. Fonts are not redistributed; only rendered glyph artwork. Font reference: https://github.com/notofonts / https://openfontlicense.org/

