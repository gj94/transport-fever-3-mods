# Exterior, roof and dimensional evidence

This is an editable, high-detail, photo-led model of Royapuram WAP-7 39002. It is not a laser scan, a certified manufacturing model, or a claim that every unseen fitting matches that individual locomotive. Fine hardware is reconstructed from photographs and documented equipment families where unit-specific drawings were unavailable.

## Main evidence and its limits

- The primary identity/livery reference is [WAM4ajj’s actual photograph of Royapuram 39002, 21 November 2020](https://commons.wikimedia.org/wiki/File:RPM_WAP-7.jpg) (CC BY-SA 4.0). It establishes the white body, orange/vermilion belt, front legends and flag, two HOG receptacles and cable brackets, windscreen guards, lamp arrangement and general service condition. Research photographs are not embedded in the vehicle textures or distributed as original artwork.
- The WAP-7 general arrangement, RDSO **SKEL-4490**, appears on PDF page 24 / printed page 16 of [ACTM Volume III](https://mysonpurdivision.com/files/67b8412b83a17.ACTM%20VOLUME-III_Final.pdf). Its specific front-view arrow and row 16 identify **3152 mm overall width of body**. A generic table in the same wider reference family gives 3100 mm. This model follows the WAP-7-specific drawing, while retaining that source conflict rather than claiming a certified as-built section.
- [Frontier Alloy's coupler catalogue](https://www.frontieralloy.com/couplers) identifies the H-type locomotive coupler for diesel and three-phase locomotives. Its manufacturer-rendered views ground the separate curved knuckle, deep throat, anti-climber wings, pin bosses and cast-web transitions. They are equipment-family morphology references, not a dimensioned mating drawing. The closed position is checked against the actual locomotive photograph, rather than copying the more-open manufacturer display pose.
- The [Stone India AM-92 listing](https://www.exportersindia.com/product-detail/am-92-pantographs-3229706.htm) supplies a manufacturer-attributed form reference: substantial lower arm, slim control link, paired upper arms, open I-like mounting assembly, spring housings and collector hardware. The model retains the existing level-head control rig. It is a representative AM-92-form visual assembly, not a certified kinematic reconstruction.
- The official [CR/ZRTI three-phase locomotive training book](https://cr.indianrailways.gov.in/cris/uploads/files/1383198951757-ABB%20Loco%20in%20English.pdf), roof and power layout pages, grounds the distinction between common pantograph roof conductor, circuit-breaker input, circuit-breaker output and transformer roof entry. The two breaker sides are not joined by an unbroken bypass conductor in the new model.
- The actual [CNB WAP-7 37097 photograph, Howrah, 3 October 2019](https://indiarailinfo.com/blog/post/4446957) is a class comparator for the entry ladder. It shows two lower treads and a separate sill recess. The official [CLW category book](https://clw.indianrailways.gov.in/works/uploads/File/CAT%20BOOK%20G9H%26%20P7%289%20files%20merged%29.pdf), page 22, identifies a WAP-7-specific footstep assembly 1209-00.240-202 with chequered-plate references 1/2. A WAG-9 three-rung photograph was deliberately rejected as an exact WAP-7 template.

## Substantive dimensional correction

The inherited authoring file had globally scaled the BODY branch in Y by 0.9227166 to fit projecting accessories into an aggregate 3152 mm envelope. That reduced the actual body skin to about 2908 mm. Revision 02 removes that unsupported squeeze and restores the main body skin to **3.152 m**. Door, filter, handrail and step placement is corrected independently. Round fasteners and lamps are not elliptically scaled to hide the width issue.

Main-skin width and the complete accessory envelope are reported separately by final QA. Real handles and handrails project beyond the skin. An accessory projection is not silently relabelled as a body-width failure or flattened solely to hit a target number.

The visible closed-coupler mesh endpoints are set to X = ±10.281 m, giving **20.562 m** overall visible length. Existing coupling anchors remain X = ±10.200 m and CBC pivots remain at their inherited functional datums. These are authoring/animation interfaces, not certified railway coupling-contact planes. Preserving those anchors does not prove mating contact with the prior ICF/LHB coach heads. New-head contact, curve clearance and in-game compatibility still require explicit conversion-stage tests. The 1 mm per-end correction from revision 01 does not establish photogrammetric precision.

The folded carbon contact strip remains at **4.254758 m**. The former slight overheight of a busbar and contact-guide horns is corrected in mesh geometry without moving functional pantograph pivots or changing the driver mechanism. QA also tests the actual new collector geometry through representative extension poses.

## Visible construction work

- Continuous, sub-millimetre-offset livery surfaces follow the nose, corner chamfers and body sides. The front flag and text no longer sit on thick projecting plaques, and the stripe no longer leaves a broad white gap at the corner.
- Separate closed glazing panes, inner/outer EPDM lips, narrow welded guard rods, offset supports, multi-part wipers, blades and washer jets give the windscreens real depth. Glass is transmissive; broad white patches in an early studio image were reflections of a light card, not opaque panes.
- Headlights have service plates, bezels, concave reflectors, bulbs and convex prismatic lenses. Corner markers, roof searchlight pedestal and hollow horn mouths are separately modelled.
- The two HOG receptacles have angled bodies, hinged covers, bail hardware, cable brackets, strain reliefs and curved heavy cables. Air cocks, uncoupled hoses and retaining chains are separate objects.
- The CBC head has a curved knuckle, hollow throat, tapered cast contours, relieved guard web, pin bosses and operating hardware. Contact material is assigned to actual contact-face polygons. Convex buffer discs have individual local wear maps rather than flat silver discs.
- The underframe is a perimeter/channel structure with diaphragms and local secondary-spring pockets. It is no longer a solid full-width slab passing through the suspension.
- Entry treads are thin chequered steel with folded edges and brackets. Their heights and stand-offs are photographically estimated, not certified. The lower ladder is attached to the corresponding bogie as an explicitly inferred mounting choice; the sill tread remains body-fixed. Representative ±8° bogie-yaw intersection checks are supplied, without a claim of certified curve clearance.
- The cab crown is a continuous formed surface with real panel seams rather than a stack of faceted cover wedges. Roof electrical equipment has porcelain shed profiles, flanges, clamps and distinct conductor routes. Pantograph spring housings, clevises, bushes, collector supports and copper braids are visible geometry.

## Artwork, materials and presentation

The small Royapuram crest is original vector-like artwork inspired by the visible layout. It is an approximation, not an official logo asset. No source-photo pixels are used as vehicle geometry substitutes. Surface atlases and instrument artwork are original procedural/painted assets; separate component notes document their construction and limitations.

The outdoor gallery uses actual Cycles rendering of the same vehicle meshes. The sky and soil material are separately credited CC0 Poly Haven assets; track, sleepers, ballast stones, overhead wiring and generic depot buildings are real scene geometry. The depot is not claimed to be an as-built reconstruction of Royapuram. See `environment/README.md`.

The delivery is a **source-only authoring model**. It has not been converted, optimized, packaged or tested as a Transport Fever 3 runtime vehicle. No native game resources are changed by this revision.
