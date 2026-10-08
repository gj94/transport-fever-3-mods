#!/usr/bin/env python3
"""Reconstruct all three complete Blender scenes from checksum-verified Git parts."""
from pathlib import Path
import subprocess,sys,argparse
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--include-exports',action='store_true',help='Also reconstruct the compressed portable export archives; unpack them separately.')
a=p.parse_args();root=Path(__file__).resolve().parent
folders=[root/'tvc/TVC_full_station_v02.blend.parts',root/'ncj/NCJ_full_station_v02.blend.parts',root/'ers/ERS_full_station_v02.blend.parts']
if a.include_exports:folders += [root/'tvc/packages/TVC_v02_exchange_glb.zip.parts',root/'ncj/exports/NCJ_full_station_v02_GLTF.zip.parts',root/'ers/exports/ERS_full_station_v02.glb.gz.parts']
for folder in folders:
 script=folder/'reassemble.py'
 if not script.is_file():raise SystemExit('Missing downloaded folder: '+str(folder)+'\nDownload the complete repository tree, including every part.')
 subprocess.run([sys.executable,str(script)],check=True)
print('All requested complete files reconstructed and SHA256 verified. Open .blend files in Blender. Unpack export archives before import.')
