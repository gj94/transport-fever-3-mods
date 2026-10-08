#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for script in build_ncj_full add_review_labels repair_all_ncj_turnouts repair_ncj_compound_crossings repair_ncj_ohe repair_ncj_services repair_ncj_pits validate_ncj_full; do
  echo "NCJ stage: $script"
  blender -b -t 4 --python-exit-code 1 --python "$ROOT/scripts/$script.py" > "$ROOT/${script}.log" 2>&1
  echo "NCJ stage complete: $script"
done
blender -b -t 4 --python-exit-code 1 --python "$ROOT/scripts/render_ncj_full.py" -- 17 18 19 > "$ROOT/render_pointwork_review.log" 2>&1
