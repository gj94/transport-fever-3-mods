# Independent read-only validation

Requires Blender 4.3 or later. No Python packages beyond Blender's bundled environment are needed. The script reads the master and writes a JSON report. It never saves a `.blend` file.

## Delivered asset

Keep `functional_interface_baseline.json` beside `validate_integrated_readonly.py`, or pass its location explicitly:

```sh
blender --background --threads 1 --python-exit-code 1 \
  --python validate_integrated_readonly.py -- \
  --master WAP7_detail.blend \
  --baseline functional_interface_baseline.json \
  --report independent_validation.json
```

Use the actual master filename. The master, reference JSON and output report may be in any directories. No working-folder path or old source `.blend` is required once the reference JSON is supplied.

## Reference-contract capture

For rebuilding the baseline from the original v01 source:

```sh
blender --background --threads 1 --python-exit-code 1 \
  --python validate_integrated_readonly.py -- \
  --source WAP7_photoreal_v01.blend \
  --export-baseline functional_interface_baseline.json \
  --master WAP7_detail.blend \
  --report independent_validation.json
```

For a baseline-only capture, omit `--master` and `--report` and add `--capture-only`.

The combined command opens the source and master serially. Run only one full-model Blender process at a time on a memory-constrained machine.

## Checks and interpretation

- Records source/master SHA256 hashes and Blender version
- Compares the original functional root, coupling, bogie, axle and pantograph world frames, hierarchy, driver expressions/targets and default extension properties
- Separately records the approved BODY Y-scale restoration to 1.0 and resulting cab-frame refit
- Records coupling attachment datums, axle span and bogie wheelbases separately from visible over-coupler length
- Checks metre units and non-finite geometry
- Reports main body skin, fixed body accessories and the full visible asset envelope separately
- Measures length and height above rail with both pantographs temporarily folded; negative wheel-flange Z is not included in the above-rail height
- Samples eleven extensions for each pantograph using the actual two visible rebuilt carbon strips and checks both the level-head control and the actual carbon contact-face levels and coplanarity
- Restores the in-memory saved extension values before exit
- Reports packed-image status and evaluated per-object bounds

The pass flag covers functional-interface, metre-unit, finite-geometry and collector-level checks. A successful pass does not certify an exact manufactured WAP7 or locomotive 39002. Nominal length 20.562 m, body width 3.152 m and locked-down height 4.255 m are reference comparisons. Some railway tables give 3.100 m width; physical accessory projections are reported explicitly and require reference judgement. They are not silently flattened to force one aggregate number.

Cabinet construction, hidden apparatus, exact stair stand-offs and other unsurveyed details remain representative. This script does not certify operational safety, dynamic loading, physical coupling performance or all moving-part clearances.
