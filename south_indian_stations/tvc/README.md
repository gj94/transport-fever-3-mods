# TVC — Thiruvananthapuram Central heritage study

Editable architectural asset in metres, reconstructing the distinctive heritage entrance photographed on **14 November 2022**, before major redevelopment. This is a photo-derived model, not a measured survey or a reconstruction of the entire station campus.

## Deliverables
- `TVC_heritage_2022_v1.blend`: separately organized heritage pavilion, gallery/end-pavilion kit, contextual forecourt, independent platform/canopy demonstration, cameras and lighting.
- `scripts/build_tvc.py`: deterministic, reusable Blender construction script. Run `/usr/bin/blender -b -t 4 --python scripts/build_tvc.py -- --render` from any directory.
- `scripts/audit_asset.py`: reopen audit, resource/gauge checks and Asset Browser collection tags.
- `scripts/add_return_detail.py`: three-bay central return refinement from the wider reference.
- `scripts/finalize_tvc.py`: packed trilingual graphic, nominal inner rail gauge correction, QA and render pass. Automatically called by `build_tvc.py -- --render`.
- `scripts/make_sign.py`: original trilingual platform sign texture, Pillow with RAQM text shaping. Run before building.
- `renders/`: actual Blender Cycles renders, not AI-generated images.
- `qa_geometry.json`: scene inventory and accuracy metadata.
- `textures/`: portable original sign graphics; other materials are procedural and require no third-party image maps.

## What was observed and reproduced
The 2022 exterior shows **three tall arched upper front windows** on the raised central pavilion, with the middle opening wider than its neighbours, four full-height pale pilasters, two stacked shutter tiers and an arched fanlight. The central lower entrance is arched. Dressed dark granite, stepped pale cornices, a parapet, red raised rooftop English lettering, rainwater pipes and lower pitched-roof veranda wings are the identifying details. Individual dressed-stone blocks, louvre blades, frames and hinges are editable geometry rather than a facade photo pasted on a block.

The broader 2010 comparison reveals the pavilion's return elevation and a smaller single-upper-bay secondary pavilion beyond a veranda. This version limits the building to the central pavilion, two short gallery study modules and two secondary pavilions; gallery repetition and symmetry outside the close 2022 view are reconstruction choices, not verified complete opening counts. The central return repeats three observed narrow upper bays; the rear elevation remains simplified. The full far wings, hidden rooms and operational circulation are not surveyed.

The 2022 platform photo shows a sloped corrugated canopy, built-up steel columns, diagonal brackets, light fittings, reddish edge paving, a yellow trilingual nameboard and electrified railway surroundings. The 36 m detached canopy/platform demonstration reproduces that structural character; it is not claimed as an exact platform segment or geographical placement. No five-island arrangement or invented full yard ladder is supplied.

## Dimension ledger
No station-specific dimensions are source-measured.

| Item | Model value | Status |
|---|---:|---|
| Central facade | 14.4 m wide × 14.9 m cornice height | Photo-inferred, scale-adjusted |
| Main pavilion depth | 8 m | Game-adjusted; rear unverified |
| Central upper openings | 3; centres −4.35 / 0 / +4.35 m | Count observed; positions photo-inferred |
| Upper opening spring | 10.85 m | Photo-inferred |
| Outer / central arch radius | 0.74 / 1.18 m | Photo-inferred |
| Central entrance radius | 1.65 m | Photo-inferred |
| Gallery study width | 13.4 m each | Game-adjusted |
| Secondary pavilion | 6.5 m wide × 11.4 m high | Photo-inferred |
| Canopy module length / width | 36 / 7 m | Game-adjusted modular sample |
| Platform height | 0.68 m | Game-adjusted; not a TVC survey |
| Illustrative track gauge | 1.676 m clear inner head gap | Indian broad-gauge nominal, not a surveyed TVC track |

Front is negative Y, up Z, central entrance X=0. The canopy is offset to Y=19 for kit presentation, not true surveyed station siting. Forecourt autos, trees, road dashes and railings supply scale/context and are not an inventory of objects present on the date. Political flags and advertising images in the reference are omitted. This avoids borrowing commercial advertisement pixels and obstructing architectural review.

## References and licences
Reference images were downloaded for visual inspection only. They are not mapped onto the building or included in its packed data.
1. Ravi Dwivedi, 14 November 2022, exterior. CC BY-SA 4.0. https://commons.wikimedia.org/wiki/File:Thiruvananthapuram_Central_railway_station.jpg
2. Ravi Dwivedi, 14 November 2022, platform interior. CC BY-SA 4.0. https://commons.wikimedia.org/wiki/File:Inside_view_of_Thiruvananthapuram_Central_railway_station.jpg
3. sabu-mampallil-kottayam, Commons date 5 June 2010 (EXIF differs), broader comparison. CC BY-SA 3.0 selected from dual licence. https://commons.wikimedia.org/wiki/File:Thiruvananthapuram_Central_Railway_Station.jpg

Photograph licences: https://creativecommons.org/licenses/by-sa/4.0/ and https://creativecommons.org/licenses/by-sa/3.0/ . Originals remain unchanged in the local `references/` research folder. **Exclude that folder from asset-only publication** unless publishing it with the attribution and applicable photograph licences. Original procedural geometry, scripts and generated labels use no copied photo pixels.

Primary station context: KMRL-hosted Comprehensive Mobility Plan, section 2.11.1, printed p42, Figure 40, confirms five platforms (not five islands): https://kochimetro.org/kmrl_content/uploads/2024/03/Final_CMP_Report_TVM-31082023.pdf . Exact platform-face pairing and yard alignment were not verified.

2025 ongoing redevelopment is outside this model's era: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2104714&lang=2&reg=48 . New terminal proposals, multilevel parking and later concourses are deliberately excluded.

## Limits and use
Suitable as an editable visual heritage/railway scene asset. Not engineering, surveying, train-clearance or safety infrastructure data. Materials use Blender shader nodes; exchange formats may not reproduce procedural bump/colour without baking. The .blend is the authoritative editable source. Use collection visibility to isolate the building or the separate canopy study.

## Typography
The original platform graphic uses Noto Sans Malayalam, Noto Sans Devanagari and DejaVu Sans. Generated lettering is not copied from a photograph. Relevant font redistribution notices are preserved under `licenses/`; the packed Blender rooftop type uses DejaVu Sans Condensed.

## Final visual review
The reviewed version narrows the two outer central-pavilion upper openings to 0.74 m radius while preserving the 1.18 m centre, matching the photographed wider central bay. Front pilaster spacing is unchanged. Four collection assets can be appended independently; the canopy collection has its asset placement offset at its study-module centre. No furnished station interior, ticket-office plan or passenger concourse is included. Dark backing planes represent unlit openings. Stone coursing and reveal-edge cutting remain visual approximations.

The CC notices above apply only to the reference photographs, and the font notices only to their respective fonts. No new open-source or Creative Commons licence is granted here for generated geometry, scripts or renders; the repository's existing licensing default is unchanged.
