"""Execute native Lua tables and check exported freight motion/crew placement.

Requires Pillow for the separate pack check and lupa for this Lua check. Runtime
script tests strip the known Teal annotations and stub the stock updater; they
check our logic, not the game's Teal compiler or in-game wire/curve behaviour.
"""
import argparse, json, re, zipfile
from pathlib import Path
from lupa import LuaRuntime
from freight_locomotives import SPECS
from wap7_audio import SOUND_SET_REF,STOCK_SOUND_SET


def sequence(value):
    return [value[i] for i in range(1, len(value)+1)]


def matrix(values):
    values=sequence(values)
    return [[values[c*4+r] for c in range(4)] for r in range(4)]


def multiply(a,b):
    return [[sum(a[r][k]*b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--game-root',type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    mod=root/'game_build/gj94_indian_rail_pack'
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute('math.pow=function(a,b) return a^b end; math.round=function(a) return math.floor(a+.5) end; _=function(s) return s end')
    with zipfile.ZipFile(args.game_root/'base/content/scripts.zip') as z:
        scripts={n:z.read(n).decode() for n in z.namelist() if n.endswith('.lua')}
    cache={}
    def require(name):
        assert name.startswith('::/scripts/'),name
        if name not in cache:cache[name]=lua.execute(scripts[name[3:]])
        return cache[name]
    lua.globals().require=require
    def load(path):
        lua.execute(path.read_text())
        return lua.globals().data()
    # Parse every native table, including meshes/materials and the private sound
    # set through the installed base helpers. No copied game code in the pack.
    resources=[p for p in mod.rglob('*') if p.is_file() and p.suffix in {'.mdl','.msh','.mtl','.ani','.lua'}]
    for path in resources:load(path)
    report={'lua_tables_executed':len(resources),'models':{}}
    with zipfile.ZipFile(args.game_root/'base/content/characters.zip') as z:
        driver=lua.execute(z.read('characters/era_c_driver_rail/era_c_driver_rail.mdl').decode()+'\nreturn data()')
        pose=lua.execute(z.read('characters/shared/ani/man01/driving_upright/pelvis.ani').decode()+'\nreturn data()')
    def find(node,name):
        if node['name']==name:return node
        for child in sequence(node['children'] or lua.table()):
            result=find(child,name)
            if result is not None:return result
    driver_root=driver['lods'][1]['node']
    posed=multiply(matrix(driver_root['transf']),multiply(matrix(find(driver_root,'man01')['transf']),multiply(matrix(find(driver_root,'pelvis')['transf']),matrix(pose['transfs'][1]))))
    hip=posed[2][3]
    identity=[[int(r==c) for c in range(4)] for r in range(4)]
    for key,spec in SPECS.items():
        folder=mod/f'content/vehicle/train/{key}'
        model=load(folder/(key+'.mdl'))
        tracks={}
        def worlds(node,parent,state=None,index=1,result=None):
            result={} if result is None else result
            local=matrix(node['transf'])
            anim=node['animations'] and node['animations'][state] if state else None
            if anim:
                ref=anim['params']['id']
                if ref not in tracks:tracks[ref]=load(folder/ref)
                local=multiply(local,matrix(tracks[ref]['transfs'][index]))
            world=multiply(parent,local)
            result[node['name']]=world
            for child in sequence(node['children'] or lua.table()):worlds(child,world,state,index,result)
            return result
        error=0.0
        dual=key=='wag9'
        for lod in sequence(model['lods']):
            for end in ('front','rear') if dual else ('',):
                state='pantograph_'+end if dual else 'pantograph'
                head='panto_'+end+'_head_level_pivot' if dual else 'panto_head_level_pivot'
                for i in range(101):
                    world=worlds(lod['node'],identity,state,i+1)[head]
                    top=world[2][3]+(.044 if dual else .032)
                    expected=spec['panto_low']+(spec['panto_high']-spec['panto_low'])*i/100
                    error=max(error,abs(top-expected))
                    assert abs(top-expected)<2e-5,(key,i,top,expected)
                    assert abs(world[0][2])+abs(world[1][2])+abs(world[2][2]-1)<1e-5
        groups=worlds(model['lods'][1]['node'],identity)
        cushion=2.302 if dual else 2.085
        crew=[]
        for seat in sequence(model['metadata']['seatProvider']['seats']):
            world=multiply(groups[seat['group']],matrix(seat['transf']))
            assert abs(world[2][3]+hip-cushion)<.01,(key,world[2][3],hip,cushion)
            crew.append(dict(group=seat['group'],forward=seat['forward'],hip_z_m=world[2][3]+hip))
        horn=mod/'content/vehicle/train/wap7/sound/wap7_horn.wav'
        assert model['metadata']['soundConfig']['soundSet']['name']==(SOUND_SET_REF if horn.is_file() else STOCK_SOUND_SET)
        family='wag9' if dual else 'wag12b'
        source=(folder/(family+'_transformator.script.tl')).read_text()
        source=source.replace(' as any','')
        for typename in ('NativeLuaTable','TransformatorParams','Transformator.TransfOutput'):
            source=source.replace(': '+typename,'')
        lua.execute('stockCalls=0; function ug_require(name) assert(name=="::/vehicle/train/shared/transformator_train.script.tl"); return {train={updateFn=function() stockCalls=stockCalls+1 end}} end')
        update=lua.execute(source)[family]['updateFn']
        cases=0
        for reversed_ in (False,True):
            for height in [spec['panto_low']-1,spec['panto_high']+1]+[spec['panto_low']+(spec['panto_high']-spec['panto_low'])*i/100 for i in range(101)]:
                states={}
                def record(_self,name,start,frame,loop,reverse):
                    assert start==-1 and not loop and not reverse
                    states[name]=frame
                params=lua.table_from({'currentInfo':lua.table_from({'landVehicle':lua.table_from({'reversed':reversed_})}),'landVehicleApi':lua.table_from({'getAverageCatenaryHeight':lambda *_:height})})
                update(lua.table(),params,lua.table_from({'addAnimationState':record}))
                expected=max(0,min(1000,(height-spec['panto_low'])/(spec['panto_high']-spec['panto_low'])*1000))
                wanted={'pantograph_front':expected if reversed_ else 0,'pantograph_rear':0 if reversed_ else expected} if dual else {'pantograph':expected if reversed_ else 0}
                assert states.keys()==wanted.keys() and all(abs(states[s]-v)<1e-8 for s,v in wanted.items())
                cases+=1
        states=[]
        update(lua.table(),lua.table_from({'currentInfo':lua.table()}),lua.table_from({'addAnimationState':lambda *v:states.append(v)}))
        assert not states and lua.globals().stockCalls==cases+1
        report['models'][key]={'native_max_contact_height_error_m':error,'native_lods_checked':4,'script_logic_cases':cases+1,'crew':crew}
    (root/'game_build/freight_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
