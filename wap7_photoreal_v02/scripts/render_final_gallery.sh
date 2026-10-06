#!/usr/bin/env bash
# Serialized, source-matched Cycles gallery. No vehicle geometry rebuild or save.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MASTER="${1:-$ROOT/WAP7_detail_v02.blend}"
THREADS="${2:-8}"
LOGS="$ROOT/qa/render_logs"
mkdir -p "$LOGS" "$ROOT/previews/cab" "$ROOT/previews/details" "$ROOT/previews/machinery_gallery"
SHA="$(sha256sum "$MASTER" | cut -d' ' -f1)"
run() {
  local label="$1" script="$2"; shift 2
  echo "$(date -u +%FT%TZ) START $label master=$SHA"
  blender -b -t "$THREADS" --python-exit-code 1 --python "$ROOT/scripts/$script" -- "$@" > "$LOGS/$label.log" 2>&1
  echo "$(date -u +%FT%TZ) DONE $label"
}
run 01_hero render_outdoor.py HERO 512 1920 "$THREADS" "$MASTER"
run 02_cab_panel_A render_cab_gallery_uniform.py --master "$MASTER" --view panel_A --samples 256 --width 1600 --threads "$THREADS" --output "$ROOT/previews/cab/panel_A.png" --expected-sha256 "$SHA"
run 03_coupler render_probe.py COUPLER_TOP 256 1600 "$THREADS" "$MASTER"
run 04_machinery_walkthrough render_machinery_gallery.py "$MASTER" through_door 192 1400 "$THREADS" --expected-master-sha256 "$SHA"
run 05_wheel render_detail_gallery.py "$MASTER" wheel 192 1600 "$THREADS"
run 06_pantograph render_probe.py PANTOGRAPH 192 1600 "$THREADS" "$MASTER"
run 07_cab_overview render_cab_gallery.py --master "$MASTER" --view overview_A --samples 192 --width 1400 --threads "$THREADS" --output "$ROOT/previews/cab/overview_A.png" --expected-sha256 "$SHA"
run 08_underfloor render_detail_gallery.py "$MASTER" underfloor 128 1600 "$THREADS"
run 09_machinery_cutaway render_machinery_gallery.py "$MASTER" cutaway 192 1600 "$THREADS" --expected-master-sha256 "$SHA"
run 10_side render_probe.py SIDE 128 2200 "$THREADS" "$MASTER"
test "$(sha256sum "$MASTER" | cut -d' ' -f1)" = "$SHA"
echo "$(date -u +%FT%TZ) GALLERY_COMPLETE master=$SHA"
