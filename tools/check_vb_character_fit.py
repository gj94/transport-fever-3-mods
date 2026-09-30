"""Check VB seat roots against the installed male rail-driver skeleton/poses."""
import argparse,json,re,zipfile
from pathlib import Path
from check_tf3_balance import table

def matrix(values):return [[values[c*4+r] for c in range(4)] for r in range(4)]
def mul(a,b):return [[sum(a[r][k]*b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
def frame(text):return [float(v) for v in text.split(',') if v.strip()]

parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];report={}
with zipfile.ZipFile(args.game_root/'base/content/characters.zip') as z:
    text=z.read('characters/era_c_driver_rail/era_c_driver_rail.mdl').decode()
    # Persistent man01 and pelvis nodes have the rest frames after their children.
    def rest(name):
        match=re.search(r'name\s*=\s*"'+name+r'",(?:\s*skin\s*=\s*"[^"]*",)?(?:\s*skinMaterials\s*=\s*\{[^}]*\},)?\s*transf\s*=\s*\{([^}]+)\}',text)
        assert match,name
        return matrix(frame(match.group(1)))
    parent=mul(rest('RootNode'),rest('man01'));pelvis=rest('pelvis')
    for pose in ('driving_upright','sitting'):
        ani=z.read(f'characters/shared/ani/man01/{pose}/pelvis.ani').decode()
        deltas=[matrix(frame(v)) for v in re.findall(r'\{([^{}]+)\}',ani.split('transfs',1)[1])]
        points=[mul(parent,mul(pelvis,d)) for d in deltas]
        zs=[p[2][3] for p in points]
        report[pose]={'posed_hip_offset_z_m':[min(zs),max(zs)],'hip_with_vb_root_z_m':[1.267+min(zs),1.267+max(zs)],'cushion_top_z_m':1.75,'scope':'Skeleton hip alignment; full mesh fit and all passenger character variants remain runtime checks.'}
        tolerance=.01 if pose=='driving_upright' else .035
        assert all(abs(1.267+v-1.75)<tolerance for v in zs),report[pose]
for key in ('vb_dtc','vb_mc','vb_mc2','vb_tc_cc','vb_tc_ec','vb_ndtc_ec','vb_ndtc_ec2'):
    text=(root/f'game_build/gj94_indian_rail_pack/content/vehicle/train/{key}/{key}.mdl').read_text()
    seats=table(table(text,'metadata'),'seatProvider')
    for values in re.findall(r'transf=\{([^}]+)\}',seats):assert abs(frame(values)[14]-1.267)<1e-5
(root/'game_build/vande_bharat_character_fit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
