# FIAT running gear: dimensional authority and interpretation

Research and original procedural geometry: 7 October 2026. Sources are linked, not redistributed. Module: `../../lhb_running_gear.py`.

## Sources inspected

- Indian Railways, Maintenance Manual of LHB Coaches, chapter 4, printed pages 6–11, 19–26. Official [SECR document](https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf); the same railway-authored document was retrieved using its existing [distribution mirror](https://d2wuvg8krwnvon.cloudfront.net/media/user_space/cf19354d093c/ebook/ebook_1639504169_9471.pdf). Actual drawing pixels inspected: Fig 4-1 general arrangement, Fig 4-2 welded frame, Fig 4-3 primary suspension, Fig 4-4 secondary suspension. Printed pp 6, 10, 11, 20, 21, 23, 24 and 26 extracted and read directly.
- Rail Coach Factory, Kapurthala, *Bogie Design Parameters & FIAT Bogie*, Ravi Narula, hosted by [Indian Railways Institute of Mechanical and Electrical Engineering](https://rskr.irimee.in/sites/default/files/6.%20Design%20Features%20of%20LHB%20Fiat%20Bogie.pdf). Direct official PDF text verified. Slides 14–16 confirm four nested primary assemblies per bogie and two brake discs per axle, 640 mm diameter ×110 mm width. Slides 21–26 corroborate nested secondary coils, dampers, anti-roll bar and traction mechanism. Fine component dimensions are not inferred as certified dimensions from this presentation.
- [IRICEN Monograph on FIAT Bogie](https://iricen.gov.in/iricen/books_jquery/LHB%20Monogram.pdf): official search-indexed table independently corroborated wheelbase 2,560 mm, wheel diameter 915 mm, distance between wheel backs 1,600 mm, brake diameter 640 mm and nominal bogie 3,534 ×3,030 mm. Direct fetch timed out; no additional drawing inspection is claimed from this PDF.
- Parent family baseline uses the official [NWR 2025 coaching technical data](https://nwr.indianrailways.gov.in/uploads/files/1742970525725-9%20-%20Working%20Time%20Table.pdf) and family references for 14,900 mm bogie centres, 24,000 mm coupling span and 1,105 mm empty coupling datum.

## Sourced dimensions implemented

- Bogie pivots X ±7.450 m; axle positions ±1.280 m per bogie
- Axle world Z .4575 m, 915 mm new tread diameter at the nominal tread circle; visible flanges extend below nominal rail contact level, as expected
- Wheel back-to-back 1.600 m; Indian broad gauge 1.676 m is the rail gauge, a separate datum
- Two 640 mm diameter, 110 mm nominal width ventilated brake rotors per axle
- Sideframe longitudinal endpoint span 3.534 m; 3.030 m nominal bogie width is source metadata, not a claim that every individual represented bracket reaches that exact envelope
- Coupling anchors X ±12.000 m, world Z1.105 m; +X points outward at either end

## Geometry and mechanism choices

The conventional steel-coil FIAT family is represented. Newer air-spring conversions and class-specific spring part numbers/rates are not reproduced. Each bogie has four nested primary pairs, two nested secondary pairs, four primary vertical dampers, two secondary vertical dampers, one lateral damper, two yaw dampers, four safety cables, anti-roll linkage, traction centre/rods and four bump stops. Spring wire and winding are actual meshes with open spaces between turns.

The welded frame silhouette follows the inspected railway drawing. Plate gauge, coil wire/pitch, casting contours, bolts, mounting locations, pipe bends, clearances and material wear are original representative modelling. The axlebox/control-arm assemblies do not spin with the wheels. Wheelsets, wheels and brake rotors are nested under four local-Y rotating pivots. Fixed brake calipers stay with the bogie. The complete bogie yaws from its root pivot. This is an editable visual hierarchy, not a dynamically solved suspension or certified railway mechanism.

The CBC contact envelope intentionally preserves the old family’s complementary eight-point XY profile without outward bevel, with separate rear cast collar, pivot pin, lock block, carrier, draft pack, pocket, lever, pneumatic hoses and EOG connections. The contact silhouette remains stylized. Matching anchors and this shared ICF profile are a visual alignment convention only. WAP-7’s newer CBC has not been validated by this module, and no universal mechanical interoperability is claimed.

Underframe battery/electrical cabinets, transformer fins, brake container, reservoirs, fresh-water vessel, waste chambers, hangers, valves, glands, conduits and jumper arrangements are representative. AC and non-AC enclosures differ. No certified equipment schedule or tank volume is claimed.

## QA scope

Blender 4.3.2 builds the module with the direct data API. Review renders are made from the geometry, using Cycles without denoising because this Blender build lacks OpenImageDenoise. Base/evaluated topology, datums, bogie and axle hierarchy, stationary calipers and complementary contact area are checked by the companion validation script. These checks do not establish suspension travel clearances, complete physical interference-free design, or game runtime support.
