# Roof-mounted AC package: reference and interpretation

The railway-authored CAMTECH *Maintenance Manual of LHB Coaches*, chapter 6, printed pages 8–9, figures 6.9–6.11, was inspected as actual rendered page pixels on 7 October 2026. It shows two condenser fans in one bank beside a large four-section mesh intake bank. The text specifies six maintenance covers. The open-cover photograph identifies mounting brackets, flexible electrical conduit, a junction box on each side, fresh/return ducts and an earthing cable. This is the basis of `lhb_hvac_detail.py`.

Official source: https://secr.indianrailways.gov.in/uploads/files/1622203445123-MMLHB.pdf

The same railway-authored manual was obtained earlier through its documented distribution mirror when the official download failed. Only reference links are redistributed; no page photograph becomes a texture or model component.

The model uses actual recessed fan and intake openings, mesh guards, a fin-core indication, separate flush cover joints, mounting channels, electrical boxes and conduit. The overall envelope, well depth, fan-blade profile, gauge, junction-box and bracket placement are representative modelling choices, not measured manufacturer CAD. The editable RMPU 1/2 label identifies the two modelled units; it is not an invented manufacturer serial or certification plate. No arbitrary decorative bolt grid is added.

The roof mounting region is lowered to an actual platform so it does not intersect the fan wells. The platform, package base and ceiling have separate levels, and the fans remain below the selected 4.039 m roof crown. These are authoring clearance checks, not an engineering qualification.
