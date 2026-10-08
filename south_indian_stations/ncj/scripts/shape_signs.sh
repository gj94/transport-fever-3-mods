#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../assets"
for script in tamil hindi; do
  inkscape "$script.svg" --export-text-to-path --export-plain-svg --export-filename="${script}_outlined.svg"
done
