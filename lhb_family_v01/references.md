# Research provenance and modelling decisions

Research performed 30 September 2026. Sources are linked, not redistributed. Geometry, materials and rendered views in this package are original.

## Primary railway references

1. **RDSO/CAMTECH Revised LHB Maintenance Manual, introduction (2022–23)**: [official PDF](https://rdso.indianrailways.gov.in/uploads/files/Revised_LHB_Manual_Vol_II_Chapter_I_Introduction_Draft.pdf). Search-indexed official text verified LWFAC 24, LWACCW 52 (LW90023 Alt a), LWACCN 72 (LE90009), AC chair 78, body 23,540 mm, CBC 24,000 mm, width 3,240 mm and roof 4,039 mm. The direct file repeatedly returned HTTP 502; no claim is made that its drawing pixels were inspected.

2. **Indian Railways Maintenance Manual of LHB Coaches**, official [SECR mirror](https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf). The official download also returned 502. A complete railway-authored manual was obtained from this [public distribution mirror](https://d2wuvg8krwnvon.cloudfront.net/media/user_space/cf19354d093c/ebook/ebook_1639504169_9471.pdf). The railway document remains the primary underlying source; the mirror is only a retrieval route. Chapter 1 printed pages 17–22 drawings were inspected as actual pixels: 80-berth sleeper, 100-seat three-door GS, 1A cabin/coupé layouts, 3A and the wider-bay 2A. Printed pages 27–29 include actual exterior photographs, visually inspected for window/door/bellows/step and AC-roof treatment. Page 27 independently specifies four four-berth cabins plus four two-berth coupés and three lavatories. The old summary also includes 54-berth 2A and 78-berth SG sleeper, illustrating why capacities must be tied to a chosen layout.

3. **North Western Railway Working Time Table 2025, technical data of coaching stock**: [official PDF](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf). Distinguishes LWSCZ1 102-seat non-AC chair car, LWSCZ 106-seat chair car, LWSCN 80-berth sleeper and LS 100-seat second class. It corroborates 23,540 mm body / 24,000 mm CBC / 3,240 mm width / 4,039 mm roof, 14,900 mm bogie centres, 1,303 mm floor, 915 mm new wheels and 1,105 mm empty CBC datum. This package selects the 102-seat chair and 100-seat GS representatives, not the 106-seat alternative.

4. **RDSO specification RDSO/2013/CG/B/01 Rev 01, Appendix C**: [official PDF](https://rdso.indianrailways.gov.in/works/uploads/File/Al_coach_spec_RDSO_CG_B_01_rev01_changes_jan16_upload15days_PRINT.pdf). Independent class-capacity corroboration: 24/52/72 berths and 78 chair seats; body 23,540 mm, width 3,240 mm and roof 4,039 mm. Its 1,320 mm floor differs from the maintenance/timetable datum; this package explicitly uses the 1,303 mm tare reference instead.

5. **CAMTECH/IRICEN Monograph on FIAT Bogie**: [official PDF](https://iricen.gov.in/iricen/books_jquery/LHB%20Monogram.pdf), Annexure III. Distinguishes conventional LWSCZAC AC chair-car code from LSCZAC Tejas code. The model uses LWSCZAC and does not claim Tejas stock despite an abbreviated code in the revised introduction table. Equipment is simplified FIAT-inspired geometry rather than a bolt-exact bogie reproduction.

## Photographic reference scope

Actual primary-manual exterior photographs on printed pages 26–29 were rendered and inspected; no pixels from those pages are embedded in any asset. Image-search discovery also identified [LHB First AC coupe photograph/article](https://www.team-bhp.com/news/travelling-first-ac-indian-railways-lhb-coach-first-time) and [LHB 2018 non-AC chair-car coverage](https://indiarailinfo.com/blog/post/3951615). Their direct image downloads returned 403; the actual large image files could not be inspected and no exact detail is claimed from them. The authoring decisions primarily follow the inspected railway drawings and primary-manual photographs, with generic furniture detailing.

## Explicit interpretation boundaries

- Class/service labels and shell designs are not one-to-one. A 2S reservation can use different second-class stock; the separately modelled GS is the inspected legacy three-entry layout, not an invented universal counterpart to every 2S.
- 1A/2A/3A/SL/GS compartment topology follows inspected official-manual layouts at representative spacing. Chair-car physical capacity is official; 3+3 versus 2+3 seating and the final partial CC row are a representative visualization, not a traced certified furnishing drawing. Exact chair pitch and fore/aft orientation remain provisional.
- Body height deliberately follows the selected 4,039 mm specification. The earlier repository 3A master used a 4,250 mm interpretation; it is untouched and is not the dimensional baseline of this new family.
- AC/non-AC window construction, fans versus vents, seating type and electrical equipment visibly differ. Roof and underframe component sizes and positions are approximations.
- Physical capacities, seated character roots and sleeping markers are listed separately. Gameplay capacity, speeds, dates and fares are outside this modelling scope.
