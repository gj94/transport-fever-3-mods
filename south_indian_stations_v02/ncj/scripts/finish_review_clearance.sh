#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
while ! grep -q 'READY_FRAME 04' "$ROOT/essential_gallery.log"; do sleep 5; done
blender -b -t 4 --python-exit-code 1 --python "$ROOT/scripts/repair_ncj_stair_canopies.py" > "$ROOT/repair_ncj_stair_canopies.log" 2>&1
blender -b -t 4 --python-exit-code 1 --python "$ROOT/scripts/validate_ncj_full.py" > "$ROOT/validate_ncj_full.log" 2>&1
for view in 06 05 10; do
  python "$ROOT/scripts/render_monitored.py" "$view"
done
