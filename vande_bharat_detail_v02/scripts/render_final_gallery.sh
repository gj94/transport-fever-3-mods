#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
B=blender
export VB_RENDER_THREADS=${VB_RENDER_THREADS:-6}
# Run sequentially: full-rake scenes can use several GiB. No denoising.
gallery() { "$B" -b -t "$VB_RENDER_THREADS" --python-exit-code 1 --python vande_bharat_detail_v02/scripts/render_gallery.py -- "$@"; }
"$B" -b -t "$VB_RENDER_THREADS" --python-exit-code 1 --python vande_bharat_detail_v02/scripts/render_rakes.py -- rake8 256 1800
"$B" -b -t "$VB_RENDER_THREADS" --python-exit-code 1 --python vande_bharat_detail_v02/scripts/render_rakes.py -- rake16 192 1800
gallery nose 128 1200
gallery bogie 192 1400
gallery roof 128 1400
gallery pantograph 128 1400
gallery panhead 128 1200
gallery vcb 128 1200
gallery cc 256 1400
gallery ec_front 256 1400
gallery cab 192 1400
gallery cab_controls 128 1000
gallery cab_seats 96 1000
gallery toilet 128 1200
gallery pantry 128 1200
gallery side 64 1600
"$B" -b -t "$VB_RENDER_THREADS" --python-exit-code 1 --python vande_bharat_detail_v02/scripts/render_length_proof.py
