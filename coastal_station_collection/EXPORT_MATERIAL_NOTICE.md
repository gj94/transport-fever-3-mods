# Portable GLB material colour correction

Status: correction in progress, 8 October 2026.

Packed Blender scenes and their rendered previews retain the intended appearance. A targeted review found that some portable GLB materials omit explicit fallback base colours, leaving surfaces white. This affects overnight export families in the northern, middle and southern coastal collection. Earlier rich-v02 assets are not reassessed by this notice.

Use the packed `.blend` for the intended materials while corrected portable exports are prepared. This finding concerns portable appearance; source, image and geometry checks remain available with their station-specific limitations. Existing scene, export, manifest and prior-review bytes are preserved. Earlier full-export acceptance does not cover this newly identified colour finding.

Colour-only replacements require new exact hashes and independent verification that geometry buffers, transforms, embedded resources and previously checked routes are unchanged. New full portable-release claims are held until those checks pass. Corrected archives will be explicitly identified instead of silently replacing historical bytes.

Lossless archives and transport parts still recover the exact recorded export bytes. Byte-identical recovery does not guarantee that exported materials match the Blender scene. Full procedural effects remain authoritative in Blender even after corrected GLB base colours are supplied.

[Material-table evidence snapshot](qa/reports/EXPORT_MATERIAL_SCAN_20261008.json) · [Open models](OPEN_MODELS.md) · [Station status](ROUTE_INDEX.md)
