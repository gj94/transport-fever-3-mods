"""Resolve explicitly versioned gallery sources; never rewrite render records."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
H=P/'revisions/pre_wc_repair_20261008'
def resolve(record):
 current=P/record['source']
 if sha(current)==record['source_sha256']:return current,'current_corrected_source'
 # Only the explicitly accepted twenty pre-repair views can carry forward.
 if (record['variant'],record['view'])==('3A','toilet'):return None,None
 prior=H/record['source'];old=H/'qa'/f"render_{record['variant']}_{record['view']}.json"
 if not prior.exists() or not old.exists():return None,None
 original=json.loads(old.read_text())
 if record!=original or sha(prior)!=record['source_sha256']:return None,None
 for name in ['wc_seat_ring_patch.json','wc_paper_mount_patch.json']:
  evidence=json.loads((P/'qa'/name).read_text());assert evidence['status']=='pass'
  item=next(x for x in evidence['classes'] if x['variant']==record['variant'])
  if name=='wc_seat_ring_patch.json':assert item['source_sha256_before']==record['source_sha256'];intermediate=item['source_sha256_after']
  else:assert item['source_sha256_before']==intermediate and item['source_sha256_after']==sha(current)
 return prior,'accepted_pre_repair_source'
