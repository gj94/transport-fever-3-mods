# Outdoor lighting dependency

The render-only environment map is **Kloofendal 48d Partly Cloudy (Pure Sky)** by Greg Zaal (original capture) and Jarod Guest (sky edit), from [Poly Haven](https://polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky).

- License: [CC0](https://polyhaven.com/license)
- File: `kloofendal_48d_partly_cloudy_puresky_2k.hdr`
- Downloaded 2026-10-06 from the exact URL listed by Poly Haven's public asset API
- Byte size: 5,451,493
- Provider MD5: `2eba3a4d7eeb23cbfbeca364c97e7980` (verified)

This sky is used for physically based lighting and distant sky only. The vehicle, railway track, sleepers, ballast, plants and electrical support geometry are rendered from their actual meshes. No vehicle photograph, AI vehicle image or photographic ground backplate is used.

The map is an external relative render dependency. It is not part of the locomotive asset export and need not be packed into the geometry master.

## Ground material

The soil surface uses the [Dirt](https://polyhaven.com/a/dirt) scanned PBR material by Charlotte Baglioni, also CC0. Its photographed 2 m coverage is used for the repeat scale. Diffuse, roughness, OpenGL normal and displacement maps are external render-only dependencies. It is a surface material on real terrain geometry, not a ground backplate or projected vehicle image.

The background depot is original generic geometry, not an as-built depiction or location claim for Royapuram.

All five external environment files have been checked against the provider's byte count and MD5. SHA-256 values and exact download URLs are recorded in `dependency_manifest.json`.
