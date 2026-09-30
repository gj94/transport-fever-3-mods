import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));import build_icf_family as b
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['1A']
stills='--stills' in args;args=[a for a in args if a!='--stills']
for v in (list(b.VARIANTS) if args[0]=='all' else args):
 bpy.ops.wm.open_mainfile(filepath=str(P/v/f'ICF_{v}_master.blend'))
 b.V=v;b.STUDIO=bpy.data.collections['STUDIO_render_only'];b.render_views(P/v,include_aisle=not stills)
 print('RENDERED',v,flush=True)
