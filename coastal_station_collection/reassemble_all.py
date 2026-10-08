from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
scripts=sorted(root.glob("**/*.parts/reassemble.py"))
for script in scripts:
    subprocess.run([sys.executable,str(script)],check=True)
print(f"Verified {len(scripts)} split model/export files.")
