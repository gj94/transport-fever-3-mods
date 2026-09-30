# Indian Rail Prototype Pack release notes

## v1.0 — 1 October 2026

TF3 resource revision **14**; stable mod ID `gj94_indian_rail_pack`.

- Includes WAP-7, WAG-9, paired WAG-12B, Vande Bharat 8/16-car sets and all fourteen ICF/LHB coaches: 1A, 2A, 3A, 2S, CC, SL and GS per family.
- All available vehicles appear in **Indian Railways**. The new ICF SL and LHB 3A replace the old models using the same resource IDs, avoiding duplicate entries.
- Uses the agreed doubled normalized capacities. ICF 1A/2A/3A/2S/CC/SL/GS carry 10/26/36/60/40/40/60 game passengers; LHB carries 14/32/44/62/48/48/62. SL and 3A exceed 2A; 1A has the least capacity.
- Keeps normal fare factor 0.5, maintenance factor 1 and automatic purchase/upkeep. Every ICF class uses 1980 / 110 km/h; every LHB class uses 2000 / 200 km/h.
- Includes class-specific interiors, transparent glazing, exact source seated-root transforms, four LODs and matching CBC visual datums. Every vehicle store/construction PNG is a straight side view.
- Public ZIP uses stock audio. The private local package retains the approved shared locomotive horn.
- Refreshes installation, editor DLL setup, feature, source-handoff and QA documentation. Historical source folder names and original masters are preserved.

All fourteen coaches passed automated resource, seating, capacity, stock Lua cost
and introduction-year purchase-section checks. ICF 1A/2A passed Model Editor
validation. Earlier WAP-7, Vande Bharat and purchase-tab play tests were confirmed
by the user. New coach boarding, passenger fit, curves, saved-rake appearance
and freight-engine runtime checks await user play testing.

The v1.0 native pack changes only release metadata from installed revision 13;
all vehicle resources are unchanged. The running game keeps revision 13 until
the user saves and exits, after which v1.0 can be installed. The release label
does not imply that the pending checks have passed.

See [installation, capacity table and validation history](TF3-INSTALL.md) for the
build commands and detailed evidence.
