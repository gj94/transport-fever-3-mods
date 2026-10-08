# Portable base-colour revision

These archives replace the portable export links for: EVA, PVU. Keep using the existing packed Blender scenes and their galleries; they are unchanged.

Extract each corrected `.glb.zip` before opening. The revision restores missing, untextured base-colour factors from the exact authored Blender material palette. Existing explicit factors, alpha, textures, geometry/index buffers, embedded label images, transforms and other glTF properties are preserved. Procedural noise, bump and paving patterns still belong to the native Blender material system.

Each station folder includes `COLOUR_QA.json`, the exact source palette, original export QA and the repair script. Before/after hashes prove the change is limited to those missing material factors. Original portable archives remain preserved as superseded versions.

This is an additive export correction; native station geometry/gallery acceptance remains attached to its original immutable package and independent review.
