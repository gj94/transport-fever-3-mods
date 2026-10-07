# Cab component: reference, model scope and review

## Primary detail reference

The **18 August 2022 Medha MAE675UV2 Driver Console maintenance manual, SD-8627**, is the strongest available generation-appropriate reference:

https://rskr.irimee.in/forum/wp-content/uploads/2023/07/Maintenance%20Manual%20for%20DD_MAE675UV2.pdf

- PDF page 3: cab/driver-seat overview
- PDF page 4, Figure 2: front console equipment order
- PDF page 5, Figure 3: seven front access-cover positions
- PDF pages 9–12: controllers, displays, speed recorder and pressure instruments
- PDF pages 16–18: equipment and operation/indication panels

The component uses the documented **left-to-right equipment order when looking forward**: paired pressure instruments, TCMS display, reserved TCAS panel, speed recorder, indication panel, MCP/PIS communications display, CCTV display, single brake-pipe gauge. The TCAS bay is represented as an unpopulated dark plate, matching the manual illustration rather than inventing a Kavach screen.

## Photographic finish reference

Sameer2905, *Cabin of Vande Bharat Express*, photographed 27 December 2023:

https://commons.wikimedia.org/wiki/File:Cabin_of_Vande_Bharat_Express.jpg

The photograph was inspected at its full available resolution. Its exact rake/build is not identified by the file page, so it supports the VB2-family visual treatment rather than proving a particular 2022 unit. It corroborates the moulded blue-grey horseshoe desk, dark removable upper instrument tiles, ivory lining, black seats with separate rounded headrests, steel headrest supports, retracted front roller blind, switch banks and central underdesk covers.

Neither reference image is embedded in the model or redistributed. All mesh geometry, text, dial marks, screen graphics and materials are original procedural constructions. There are no photographic texture dependencies or fabricated render images.

## Added model detail

- Sculpted wraparound desktop and raised instrument binnacle, separate anti-glare brow and real removable-panel boundaries
- TCMS layout with eight train blocks, status fields, bezel softkeys and buttons; original static mesh lettering
- Reserved TCAS blanking bay; analogue speed-recorder face with numbers, ticks, needle, small LCD and keypad
- Central 4 × 4 indication bank, coloured recessed lenses, plated bezels, inscriptions and captive screws
- MCP/PIS crew-communication display; CCTV screen with labelled schematic standby quadrants
- Paired left and single right pressure instruments, white faces, graduated scales and independently modelled needles
- Horizontal T-grip controller, detented gate, paired left-hand brake controls, boots, grip and selector hardware
- Two thin gooseneck microphones alongside the MCP; auxiliary wing switches, radio handset/cradle/keypad/screen and a three-dimensional helical handset cable
- Emergency mushroom control, lower cabinet covers, socket faces, hinges and latches
- Two high-back driver/guard chairs: cushion and bolsters, separate lumbar/shoulder panels, sewn grooves and stitching, headrests on plated posts, adjustable padded arms, suspension boots, swivel bases, slide rails and fixing bolts
- Floor mats, deadman-style pedals and tread strips
- Demister outlets, roller-blind hardware, back-wall service panels, grab rails, speaker, hooks, fire extinguisher and shallow ceiling light

## Prototype-length cabin fit

The full-size revision supersedes the earlier compact working model. The primary overall layout is CAMTECH's September 2022 VBE Trainset V2.0 maintenance manual, DTC drawing **TS/DTC-9-0-001, page 28**:

https://rskr.irimee.in/forum/wp-content/uploads/2023/07/Vande%20Bharat%20Trainset_Maintenance_Manual_Volume_II_System_Documentation.pdf

The drawing explicitly dimensions a **24,000 mm coupling pitch, 14,900 mm bogie-center spacing, 3,240 mm body width and 1,676 mm gauge**. These dimensions constrain the parent vehicle. They do not establish millimetre-accurate cab component positions.

The nose fairing tip near X = +11.778 m, removable cab partition near +7.30 m and cab side-entry center near +8.25 m are drawing-read stations, with approximately 50–100 mm graphical uncertainty. The nose/shell shape transition is a different line from the removable cab partition: the cab includes the aft entrance area. Its roughly 4.48 m partition-to-tip length must not be confused with the shorter nose taper length.

The following cabin stations are coordinated visual/ergonomic fits within that drawing-led shell, rather than factory dimensions:

| Item | Prototype station / size |
|---|---|
| Removable rear partition | X = 7.30 m |
| Crew-chair centers | X = 9.35 m, Y = ±0.73 m |
| Main sloping fascia datum | X = 10.33 m, Z = 2.165 m |
| Horizontal control plane | X = 10.119 m, Z = 2.033 m |
| Finished cabin floor | Z = 1.32 m |
| Seat-cushion top | Z = 1.75 m, 430 mm above floor |
| Nominal driver eye | (9.39, −0.73, 2.49) m |
| Lower windshield center | (11.52169, 0, 2.30) m |
| Upper windshield center | (10.37169, 0, 3.22) m |

The chairs and complete instrument/control assemblies are moved rigidly by +2.96 m along X. Their local dimensions, cushion shapes, screws, labels, dials, microphones and controller hardware remain 1:1; no uniform longitudinal stretching is used. Rear fittings move separately to the partition. The floor mats/pedals move upward 10 mm to the finished floor. The mounting plates sit flush on it, while cushion height is retained.

The former deep forward shelf is replaced by a shorter curved demister shelf. Its leading perimeter sits 105 mm behind the shell's curved lower-windshield datum. The roller blind follows the windshield independently, with a 70 mm aft setback to clear the upper curved lining at its bracket tops. The full-size entrance zone remains behind the chair backs and clear of the side entry.

## Integration

`components/cab.py` exposes `apply(ctx)` and returns a JSON-safe report. It is a no-op for every kind except `DTC`. Prototype datums are read from `ctx['layout']`: `cab_partition_x`, `driver_x`, `floor_z` and `nose_dx`. The defaults are the agreed full-size values above.

The component removes its own `VB02_CAB_` objects before rebuilding and deletes only exclusively cab-owned baseline visual names. Legacy mixed seat-accessory meshes have only vertices with X > 5.9 m removed. The prototype saloon ends aft of the cabin, so this legacy cleanup does not target new passenger furniture.

All new geometry is parented below BODY and linked to the DTC asset collection. The cab component preserves its input empties and their transforms. The prototype base builder deliberately moves DRIVER_001, DRIVER_002 and CAB_EYE_CAMERA_REFERENCE to their full-size positions, with DRIVER Z = 1.267 m retained as the existing character-anchor convention. This is not a claim that the compact source marker transforms remain unchanged.

Structural floor, partitions, nose, windows, front lights, horns and exterior wipers remain under their existing component owners. Tiny UI lettering, ticks, fasteners and related pieces are consolidated into named logical mesh assemblies with preserved material slots. Larger shaped parts remain individually editable. Each assembly records its rigid fit zone and the cab report records the metre datums and unit ergonomic scale.

## Explicit approximation limits

This is a **prototype-length, photo- and OEM-informed visual model**, not a certified production-console replica or operational cab.

- Overall coach pitch, bogie spacing, width and gauge follow the dimensioned primary layout
- Cab partition and shell stations read from the drawing carry graphical uncertainty; desk, seat and eye positions are coordinated ergonomic placements
- Exact display contents, words, switch labels/allocations, pressure readings, dial scales and states are representative original artwork, not validated supplier software or maintenance instructions
- UI pages show static illustrative states and do not simulate real interlocking, brake or traction behaviour
- Latches, pedal assemblies, seat mechanisms, unseen underside hardware, radio and rear-wall accessories are detailed representative forms where references do not resolve production construction
- Neutral AUX labels avoid an unsupported equipment-voltage claim
- Seat cushion tops remain at Z = 1.75 m; runtime posed-character fit remains unverified

## Gallery camera recipes

Positions are in metres, with +X forward, +Y left when facing forward and +Z up. Point the camera's local −Z at the target and local +Y upward. The component report provides these recipes using the active layout datums.

| View | Position | Target | Lens |
|---|---|---|---|
| Overall cab | (7.82, 0, 2.89) | (10.61, 0, 2.03) | 19 mm |
| Cab entrance | (7.54, −0.88, 2.72) | (10.45, 0.15, 2.16) | 21 mm |
| Driver eye | (9.39, −0.73, 2.49) | (11.97169, −0.40, 2.42) | 20 mm |
| Instruments | (9.46, −0.18, 2.68) | (10.36, 0, 2.16) | 28 mm |
| Seats / suspension | (10.49, −1.02, 2.82) | (9.32, 0.18, 1.97) | 22 mm |
| Rear wall | (9.70, 0.02, 2.69) | (7.37, 0, 2.45) | 22 mm |
| Floor / pedals | (9.55, −0.73, 1.98) | (10.13, −0.73, 1.38) | 26 mm |
| Ceiling / rear lamp | (9.72, 0, 2.42) | (8.25, 0, 3.60) | 23 mm |

The overall view includes natural headrest occlusion, as in the reference photograph. Use the instrument-detail view to inspect the full fascia and mesh lettering. Lighting is presentation-only and must not be exported with the train. Final gallery review is a separate integration check; these recipes do not imply that every view has already been rendered.
