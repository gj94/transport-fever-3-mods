# Full-size passenger interior: reference and implementation

The current v02 is the prototype-length revision. The compact v01 remains a separate model; its shortened rows, 19.375 m car pitch and compact service rooms do not govern this source.

## Shared layout contract

`components/interior_layout.py:layout_for(kind)` supplies the same `seat_poses` and `windows` records to the structural shell, PAX markers and interior mesh builder. It also supplies saloon bounds, lining bounds, partition centres, toilet rooms, pantry/electrical zones and the DTC wheelchair bay.

- Intermediate car body: 23.100 m
- Explicit dimension chain: 3.950 + 0.165 + 15.570 + 0.165 + 3.250 = 23.100 m
- Ordinary intermediate clear saloon: X −8.135 to +7.435 m; 165 mm dividing partitions centred at −8.2175 and +7.5175 m
- NDTC/EC2 reverses the end arrangement, including pantry side
- DTC clear saloon: approximately X −7.860 to +3.330 m; cab partition +7.300 m
- Floor Z 1.320 m; unchanged chair cushion top Z 1.750 m; PAX pose datum Z 1.267 m

The body/saloon chain is explicitly dimensioned in the source drawing. Seat cushion-reference positions, DTC service-room outline and minor fittings are drawing-calibrated visual interpretations.

## Real seating counts and exceptions

There is one actual mesh object per seat, parented to its matching PAX anchor. All seats of one class share one detailed mesh datablock at unit scale. This preserves upholstery, frame, tray, mesh pocket, mounting, charging outlet and footrest sizes; a long train is not obtained by stretching seats.

- DTC: 44 CC seats. Ten pairs total 20. The opposite bank, from pantry toward WC, contains 2, 3, 3, 3, 3, 3, 3, 3, 1, 0 seats, total 24. The companion seat and physically empty wheelchair bay are present
- MC, MC2, TC_CC: 78 CC seats. Sixteen pairs total 32; fourteen triples plus an end pair at each extreme total 46
- TC_EC, NDTC_EC, NDTC_EC2: 52 EC seats in thirteen 2+2 rows. TC_EC is the disclosed eight-car derivative interpretation, not a directly traced factory layout

CC actual seat mesh width across individual armrests is 0.494 m. A 0.499 m transverse reference spacing leaves about 5 mm between them, with a 0.530 m armrest-clear aisle. EC mesh width is 0.599 m; 0.610 m transverse spacing leaves about 11 mm and a 0.541 m aisle. CC row rhythm is 0.944 m plus a larger 1.460 m face-to-face interval; EC pitch is 1.180 m. These reference-point choices are fitted to the drawing while preserving actual mesh clearance. CC/DTC central snack tables are separately modelled.

## Service areas

Standard intermediate cars have two European-style WC rooms at one end, each 1.890 × 1.005 m, with separate full-size plumbing fixtures. The opposite pantry is approximately 2.52–2.53 m long and uses fixed-size oven, freezer, boiler, soup warmer and trolley modules with added storage and preparation counter. Electrical cabinets are separate, rather than a scaled miniature pantry.

DTC has **one** curved WC, not two. The opposite large circle on the source plan represents maneuvering space. Its inferred WC envelope is X −10.225 to −7.860 m and Y −1.500 to +0.280 m. The rear entry vestibule X −11.550 to −10.225 m remains a through-access area. The curved inward wall uses 0.600 m corners, a separate closed sliding-door leaf and real jambs. A clear 1.500 m turning footprint is placed at X −10.620, Y +0.700 m and checked against actual integrated meshes.

The pantry/crew area occupies X +4.600 to +7.150 m. It includes galley storage, CCMS/crew enclosure, folded crew seats and a separate electrical panel while retaining the central passage.

WC and cupboard doors, seat recline, rotary bearings, trays and catering appliances are static visual geometry. The moving passenger entry-door interiors remain parented to their exterior door pivots. WC opening dimensions describe the doorway with its closed leaf slid aside or removed for inspection; no runtime opening animation is claimed. Geometric clearances are not accessibility certification.

## Finish and detail

The CC royal-blue fabric uses original metre-scaled orthogonal warp/weft relief, subtle roughness variation, restrained cloth sheen and a fine regular yarn-fleck motif. Real submillimetre lockstitch geometry follows the back piping and corrected cushion contour. The existing chair proportions are preserved. EC retains original multicolour broken jacquard and separate light-blue headrest cloth.

Ceilings, continuous light coves, aqua luggage shelves, panel seams and wall finishes follow the full-size saloon. Row service units and numbered plaques use actual PAX records, including incomplete end rows and the companion single. Window blinds use the same dimensioned aperture records as the exterior. The DTC has one emergency main window per side; intermediate cars have two per side. DTC service glazing is side-specific beside the WC.

No reference photograph is used as an asset texture. Procedural Blender cloth nodes need baking for a downstream format that does not preserve Blender shader graphs; nets, seams, stitchwork and hardware are real geometry.

## Sources inspected

- CAMTECH, September 2022, [Vande Bharat 2.0 System Documentation](https://rskr.irimee.in/forum/wp-content/uploads/2023/07/Vande%20Bharat%20Trainset_Maintenance_Manual_Volume_II_System_Documentation.pdf), layout drawings pp 28–33
- [Second-generation CC interior, Sameer2905, 29 November 2023](https://commons.wikimedia.org/wiki/File:Vande_Bharat_Chair_Car_interior_layout.jpg)
- [Second-generation EC interior, Sameer2905, 29 November 2023](https://commons.wikimedia.org/wiki/File:Vande_Bharat_Executive_Chair_Car_interior_layout.jpg)

Original artwork and inferred fitting details are not a production installation drawing. See `interior_qa.md` for actual mesh checks and numeric results.
