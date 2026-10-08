from pathlib import Path
import hashlib,json,os
root=Path(__file__).resolve().parent
m=json.loads((root/'manifest.json').read_text())
output=root.parent/m['filename'];tmp=output.with_name(output.name+'.reassembling')
if output.exists():
    if hashlib.sha256(output.read_bytes()).hexdigest()==m['sha256']:
        print('Already verified:',output);raise SystemExit(0)
    raise SystemExit('Refusing to overwrite different existing file: '+str(output))
h=hashlib.sha256();total=0
try:
    with tmp.open('xb') as w:
        for part in m['parts']:
            b=(root/part['filename']).read_bytes()
            assert len(b)==part['size'] and hashlib.sha256(b).hexdigest()==part['sha256'],part['filename']
            w.write(b);h.update(b);total+=len(b)
    assert total==m['size'] and h.hexdigest()==m['sha256'],'Reconstructed hash mismatch'
    os.replace(tmp,output)
except BaseException:
    if tmp.exists():tmp.unlink()
    raise
print('Reassembled and SHA256 verified:',output)
