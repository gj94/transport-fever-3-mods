# Build, inspect and render

## Open the model

Open `WAP7_detail_v02.blend` in Blender 4.3.2 or a compatible newer version. Keep the complete `textures/` directory next to it. The compact delivery master uses relative image paths; it is not a self-contained single-file asset. Image pixels have not been recompressed or downsampled for packaging.

The model uses metres, with `WAP7_ROOT` as the vehicle root. Existing bogie, axle, coupling and pantograph controls remain available. The documented exception is the corrected `BODY` transverse scale, now 1.0 rather than the inherited width-fitting squeeze. The neutral inspection stage is a separate presentation collection and is not vehicle export geometry.

This is an authoring source, not a native Transport Fever 3 package. Runtime conversion, LOD work, texture baking, material conversion and in-game tests are separate work. The new CBC visual casting must also be checked against the intended ICF/LHB mating heads and curve poses; unchanged anchors alone are not a fresh compatibility test.

## Rebuild from the prior v01 source

The deterministic component build was tested with Blender 4.3.2 on CPU. It uses Blender's standard Python modules. Generated texture files are supplied, so no image-generation package is needed merely to rebuild the geometry.

From the revision folder:

```sh
blender -b -t 4 --python scripts/build_master.py -- ../wap7_photoreal_v01/WAP7_photoreal_v01.blend
```

The script loads the prior source without modifying it, applies the isolated components and writes a new authoring `WAP7_detail_v02.blend` in the revision folder. The authoring file retains hidden replaced parts and packed images for inspection. It will therefore be larger than the cleaned delivery copy. Do not run this command over a release you want to keep unchanged without making a working copy first.

The component order is body correction, material setup, exterior, coupler/underframe, roof, running gear, cab interiors and machinery room. `qa/build_report.json` records the executed component hashes and protected control matrices.

Optional texture regeneration scripts use Python, Pillow and NumPy. The final wear generators are `scripts/make_service_wear_maps.py` followed by `scripts/make_surface_detail_maps.py`; the earlier starter-map generator is superseded. The original instrument and crest generators use DejaVu fonts from the shown Linux paths; choose equivalent installed paths if regenerating on another operating system. Existing supplied images do not depend on those fonts at open/render time.

## Make the compact portable copy

```sh
blender -b -t 1 --python scripts/prepare_delivery_master.py -- /absolute/authoring/WAP7_detail_v02.blend /absolute/clean_delivery
```

This creates a separate directory. It removes only hidden superseded visual objects that are not graph targets or parents, retains all control empties, and externalizes image bytes without resampling. It asserts unchanged visible mesh coordinates, topology, transforms and material assignments. The manifest records source/delivery hashes and every image dependency. The published copy additionally undergoes a fresh-directory reopen audit.

## Render the actual delivered model

The image drivers open an explicitly selected master and never save presentation changes into it. Use one heavy render at a time on memory-limited systems. This tested Blender build lacks OpenImageDenoise, so gallery renders intentionally disable denoising and retain genuine Cycles samples.

The complete supplied ten-view gallery can be reproduced with `bash scripts/render_final_gallery.sh`, optionally followed by a master path and CPU thread count. The batch records the chosen per-view sample ceilings and resolutions; view-specific JSON reports record the settings actually executed. The Panel A image uses the byte-preserved uniform-sampling driver `scripts/render_cab_gallery_uniform.py`; the later cab overview uses the adaptive-sampling driver.

Outdoor gallery example:

```sh
blender -b -t 5 --python scripts/render_outdoor.py -- HERO 512 1920 5 /absolute/clean_delivery/WAP7_detail_v02.blend
```

Available outdoor cameras include `HERO`, `FRONT`, `CAB`, `SIDE`, `BOGIE`, `COUPLER_TOP`, `ROOF` and `PANTOGRAPH`. The driver builds the rail/depot environment from source and reads the separately credited files in `environment/`. The rear pantograph is raised for the outdoor wire; the saved asset remains in its normal default pose. Images go to the revision folder's `previews/` directory and source-hash provenance goes to `qa/`.

Neutral inspection example:

```sh
blender -b -t 5 --python scripts/render_probe.py -- COUPLER_TOP 512 1600 5 /absolute/clean_delivery/WAP7_detail_v02.blend
```

This uses the neutral stage stored in the master. `WINDOW`, `CAB`, `BOGIE`, `ROOF`, `PANTOGRAPH`, `SIDE` and the other named inspection cameras expose actual geometry without a photographic vehicle backplate.

Machinery gallery example:

```sh
blender -b -t 5 --python scripts/render_machinery_gallery.py -- /absolute/clean_delivery/WAP7_detail_v02.blend through_door 256 1600 5
```

Use `cutaway` for the machinery-compartment isolation. That view hides roof/lining and exterior geometry transiently; it does not represent a naturally transparent or missing shell. The through-door view keeps the intact locomotive and opens an existing rear cab door. Every visibility and pose change is logged, and the input file hash is checked before and after.

Cab gallery example: `blender -b -t 5 --python scripts/render_cab_gallery.py -- --master /absolute/clean_delivery/WAP7_detail_v02.blend --view panel_A --samples 384 --width 1600 --threads 5 --output previews/cab/panel_A.png`. Cameras and detailed usage are documented in the cab implementation notes. These gallery drivers also accept stage-only validation without rendering.

Additional neutral running-gear/roof views use `scripts/render_detail_gallery.py -- MASTER wheel 384 1600 5` (with Blender’s `--python` launcher as above). Views include `wheel`, `compressor`, `underfloor`, `bogie` and `roof_electrics`; these use a restrained low inspection fill and do not rebuild the model.

## Prepare gallery PNGs for distribution

After rendering, run `python scripts/strip_preview_metadata.py` from the revision folder. This requires Pillow and removes PNG text/EXIF metadata, including machine-specific paths and timestamps, without recompressing the image. Original compressed IDAT chunks and decoded pixels are checked for exact equality. Per-view provenance retains the raw-render hash and records the published image hash; `qa/preview_metadata_cleanup.json` contains the complete link between them.

## Validation scope

The supplied QA includes protected-control comparisons, representative pantograph poses, bogie/axle motion isolation, lower-ladder yaw checks, open rear-door passage rays, machinery aisle/pocket checks, material-role checks and portable image dependencies. These are model-quality tests, not railway certification or proof of exact unit-specific dimensions for unseen hardware. See the reference notes for evidence grades and unresolved interpretation limits.
