#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
B=blender
# True CPU Cycles; no denoiser in tested Blender build. Run only after sources and QA are final.
$B -b -t 6 --python vande_bharat_detail_v02/scripts/render_rakes.py -- rake8 512 2000
$B -b -t 6 --python vande_bharat_detail_v02/scripts/render_rakes.py -- rake16 384 2000
for view in nose bogie underframe roof pantograph; do
 $B -b -t 6 --python vande_bharat_detail_v02/scripts/render_gallery.py -- "$view" 384 1600
done
for view in cc ec_front cab cab_controls cab_seats; do
 $B -b -t 6 --python vande_bharat_detail_v02/scripts/render_gallery.py -- "$view" 512 1600
done
for view in toilet pantry; do
 $B -b -t 6 --python vande_bharat_detail_v02/scripts/render_gallery.py -- "$view" 384 1400
done
$B -b -t 6 --python vande_bharat_detail_v02/scripts/render_length_proof.py
