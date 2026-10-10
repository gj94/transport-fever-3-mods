# Downloads

All 24 ZIP archives preserve the approved delivery bytes. Each ZIP is an independent pack. Most are stored as lossless parts because the authenticated publication API rejected a full large ZIP. The parts must be joined before extracting. Smaller ZIPs remain whole.

## Easiest download

Save [download_collection.py](download_collection.py?raw=true) and [ARCHIVES.json](ARCHIVES.json?raw=true) in the same folder. With Python 3 installed, run:

```sh
python download_collection.py --native
```

For every archive, use `--all`. For one archive, use `--archive Kerala_Trackside_06_Road_Crossing_Example.zip`. Use `--list` to see all choices. The script fetches only selected files, checks every part, joins them, and checks the complete archive SHA-256 before retaining the ZIP. It needs no GitHub credentials for this public repository.

If you downloaded the repository or the parts manually, run the same command with `--offline`; keep the parts under their `downloads/` paths next to the script. Completed ZIPs are written to `restored_archives/` by default.

## Archive files

The source packs include maps, generators, dependencies and reference ledgers. GLB packs contain standalone portable models with embedded textures. Native libraries include their own catalogs and packed maps.

| Archive | Size | Download file(s) |
| --- | ---: | --- |
| Kerala_Trackside_01A_Buildings_Blender.zip | 27.7 MiB | [Part 1](downloads/Kerala_Trackside_01A_Buildings_Blender.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_01A_Buildings_Blender.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_01B_Buildings_Source.zip | 21.5 MiB | [Part 1](downloads/Kerala_Trackside_01B_Buildings_Source.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_01B_Buildings_Source.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_01C_Buildings_GLB_01.zip | 33.9 MiB | [Part 1](downloads/Kerala_Trackside_01C_Buildings_GLB_01.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_01C_Buildings_GLB_01.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_01C_Buildings_GLB_01.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_01D_Buildings_GLB_02.zip | 34.7 MiB | [Part 1](downloads/Kerala_Trackside_01D_Buildings_GLB_02.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_01D_Buildings_GLB_02.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_01D_Buildings_GLB_02.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_01E_Buildings_GLB_03.zip | 32.0 MiB | [Part 1](downloads/Kerala_Trackside_01E_Buildings_GLB_03.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_01E_Buildings_GLB_03.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_01E_Buildings_GLB_03.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_02A1_Landscape_Plants_Blender.zip | 37.9 MiB | [Part 1](downloads/Kerala_Trackside_02A1_Landscape_Plants_Blender.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_02A1_Landscape_Plants_Blender.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_02A1_Landscape_Plants_Blender.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_02A2_Landscape_Water_Blender.zip | 14.6 MiB | [ZIP](downloads/Kerala_Trackside_02A2_Landscape_Water_Blender.zip?raw=true) |
| Kerala_Trackside_02B_Landscape_Source.zip | 22.1 MiB | [Part 1](downloads/Kerala_Trackside_02B_Landscape_Source.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_02B_Landscape_Source.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_02C_Landscape_GLB_01.zip | 40.9 MiB | [Part 1](downloads/Kerala_Trackside_02C_Landscape_GLB_01.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_02C_Landscape_GLB_01.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_02C_Landscape_GLB_01.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_02D_Landscape_GLB_02.zip | 33.1 MiB | [Part 1](downloads/Kerala_Trackside_02D_Landscape_GLB_02.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_02D_Landscape_GLB_02.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_02D_Landscape_GLB_02.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_02E_Landscape_GLB_03.zip | 30.2 MiB | [Part 1](downloads/Kerala_Trackside_02E_Landscape_GLB_03.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_02E_Landscape_GLB_03.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_03A_Railside_Blender.zip | 32.7 MiB | [Part 1](downloads/Kerala_Trackside_03A_Railside_Blender.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_03A_Railside_Blender.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_03A_Railside_Blender.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_03B_Railside_GLB_01.zip | 42.0 MiB | [Part 1](downloads/Kerala_Trackside_03B_Railside_GLB_01.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_03B_Railside_GLB_01.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_03B_Railside_GLB_01.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_03C_Railside_GLB_02.zip | 40.4 MiB | [Part 1](downloads/Kerala_Trackside_03C_Railside_GLB_02.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_03C_Railside_GLB_02.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_03C_Railside_GLB_02.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_03D_Railside_GLB_03.zip | 38.5 MiB | [Part 1](downloads/Kerala_Trackside_03D_Railside_GLB_03.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_03D_Railside_GLB_03.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_03D_Railside_GLB_03.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_03E_Railside_Source.zip | 29.6 MiB | [Part 1](downloads/Kerala_Trackside_03E_Railside_Source.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_03E_Railside_Source.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_04A_Showcase_Blender.zip | 42.9 MiB | [Part 1](downloads/Kerala_Trackside_04A_Showcase_Blender.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_04A_Showcase_Blender.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_04A_Showcase_Blender.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_04B_Showcase_Gallery.zip | 41.5 MiB | [Part 1](downloads/Kerala_Trackside_04B_Showcase_Gallery.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_04B_Showcase_Gallery.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_04B_Showcase_Gallery.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_04C_Detail_Gallery.zip | 40.8 MiB | [Part 1](downloads/Kerala_Trackside_04C_Detail_Gallery.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_04C_Detail_Gallery.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_04C_Detail_Gallery.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_05A_Utilities_Blender.zip | 12.9 MiB | [ZIP](downloads/Kerala_Trackside_05A_Utilities_Blender.zip?raw=true) |
| Kerala_Trackside_05B_Utilities_Source.zip | 29.6 MiB | [Part 1](downloads/Kerala_Trackside_05B_Utilities_Source.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_05B_Utilities_Source.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_05C_Utilities_GLB_01.zip | 24.8 MiB | [Part 1](downloads/Kerala_Trackside_05C_Utilities_GLB_01.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_05C_Utilities_GLB_01.zip.parts/part002.bin?raw=true) |
| Kerala_Trackside_06_Road_Crossing_Example.zip | 45.0 MiB | [Part 1](downloads/Kerala_Trackside_06_Road_Crossing_Example.zip.parts/part001.bin?raw=true) · [Part 2](downloads/Kerala_Trackside_06_Road_Crossing_Example.zip.parts/part002.bin?raw=true) · [Part 3](downloads/Kerala_Trackside_06_Road_Crossing_Example.zip.parts/part003.bin?raw=true) |
| Kerala_Trackside_07_Dusk_Lighting_Preset.zip | 4.0 MiB | [ZIP](downloads/Kerala_Trackside_07_Dusk_Lighting_Preset.zip?raw=true) |

Complete-archive hashes: [ARCHIVE_SHA256SUMS.txt](ARCHIVE_SHA256SUMS.txt). Part hashes and exact sizes: [ARCHIVES.json](ARCHIVES.json).
