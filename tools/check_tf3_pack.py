"""Check native mesh bounds, resource references and DDS mip chains."""
from pathlib import Path
import re, struct, math
from PIL import Image
from model_sources import MODELS
from vande_bharat import CAPACITY
from tf3_resource_paths import resolve_model_ref

MOD = Path(__file__).resolve().parents[1] / 'game_build' / 'gj94_indian_rail_pack'
models = list((MOD / 'content').rglob('*.mdl'))
assert {m.stem for m in models} == {key for key,_ in MODELS}
for model in models:
    folder = model.parent
    text = model.read_text()
    meshes = set(re.findall(r'mesh="([^"]+)"', text))
    palette_tiles = set()
    for ref in meshes:
        path = folder / ref
        desc = path.read_text()
        blob = Path(str(path) + '.blob').read_bytes()
        blocks = re.findall(r'\{count=(\d+),(?:numComp=(\d+),)?offset=(\d+)\}', desc)
        assert blocks, path
        vertex_count = None
        for count, components, offset in blocks:
            count, offset = int(count), int(offset)
            assert offset + count <= len(blob), path
            assert count % 4 == 0
            if components:
                vertices = count // (4 * int(components))
                if vertex_count is None:
                    vertex_count = vertices
                assert vertices == vertex_count, path
                values = struct.unpack_from('<' + str(count // 4) + 'f', blob, offset)
                assert all(math.isfinite(v) for v in values), path
                if '_lod0.' in ref and int(components) == 2:
                    palette_tiles.update((int(values[i]*8),int(values[i+1]*8)) for i in range(0,len(values),2))
        for count, components, offset in blocks:
            if not components:
                indices = struct.unpack_from('<' + str(int(count) // 4) + 'I', blob, int(offset))
                assert len(indices) % 3 == 0 and max(indices) < vertex_count, path
    for ref in set(re.findall(r'materials=\{"([^"]+)"\}', text)):
        material = folder / ref
        for texture in re.findall(r'fileName="([^"]+)"', material.read_text()):
            dds = material.parent / texture
            data = dds.read_bytes()
            assert data[:4] == b'DDS ' and data[84:88] in (b'DXT1',b'DXT5'), dds
            image=Image.open(dds)
            assert struct.unpack_from('<I', data, 28)[0] == int(math.log2(max(image.size)))+1, dds
            if '_glass_' in dds.name:
                assert data[84:88]==b'DXT5' and image.getchannel('A').getextrema()[1]<255, dds
    far_bytes = sum((folder / (ref + '.blob')).stat().st_size for ref in meshes if '_lod3.' in ref)
    assert far_bytes < 256 * 1024
    assert len(palette_tiles) >= 8, f'{model.stem}: original material colours collapsed into one tile'
    seat_text=text.split('seatProvider=',1)[1].split('soundConfig=',1)[0]
    vb=model.stem.startswith('vb_')
    kind=model.stem[3:].upper() if vb else None
    if vb:
        assert 'multipleUnitOnly=true' in text
        transport_text=text.split('transportVehicle=',1)[1]
        assert 'filterTags={}' in transport_text, f'{model.stem}: individual car must be hidden from the depot'
    expected=CAPACITY[kind]+(2 if kind=='DTC' else 0) if vb else (2 if model.stem=='wap7' else 72)
    assert seat_text.count('animation=')==expected, f'{model.stem}: missing seats'
    node_text=text.split('metadata=',1)[0]
    for group in re.findall(r'group="([^"]+)"',seat_text):
        assert 'name="'+group+'"' in node_text, (model.stem,group)
    if model.stem in {'wap7','icf_sleeper'} or vb:
        anchor_x={}
        for label in ('front','rear'):
            match=re.search(r'name="coupling_'+label+r'",transf=\{([^}]+)\}',node_text)
            assert match, (model.stem,label)
            frame=[float(v) for v in match.group(1).split(',')]
            assert abs(frame[14]-(1.02 if vb else 1.105))<1e-5
            assert abs(frame[0]-(1 if label=='front' else -1))<1e-5
            anchor_x[label]=frame[12]
        extent=re.search(r'extent=\{bbMin=\{([^}]+)\},bbMax=\{([^}]+)\}',text)
        assert abs(float(extent.group(1).split(',')[0])-anchor_x['rear'])<1e-5
        assert abs(float(extent.group(2).split(',')[0])-anchor_x['front'])<1e-5
        expected_span=19.375 if vb else (20.4 if model.stem=='wap7' else 22.297)
        assert abs(anchor_x['front']-anchor_x['rear']-expected_span)<1e-5
        print(f'{model.stem}: coupling frames and spacing span {expected_span} m checked')
    if model.stem=='wap7':
        for end in ('front','rear'):
            assert node_text.count('pantograph_'+end+'=')==12
            for part in ('lower_pivot','elbow_pivot','head_level_pivot'):
                track=folder/'ani'/('panto_'+end+'_'+part+'.ani')
                ani=track.read_text()
                times=[float(v) for v in re.search(r'times=\{([^}]+)\}',ani).group(1).split(',')]
                frames=re.findall(r'\{([0-9.,e+\-]+)\}',ani.split('transfs=',1)[1])
                values=[[float(v) for v in frame.split(',')] for frame in frames]
                assert times==list(range(0,1001,10)) and len(values)==101
                assert all(len(v)==16 and all(math.isfinite(x) for x in v) for v in values)
                assert abs(values[-1][0]-values[0][0])>.1, track
                assert all(abs(v[a])<1e-5 for v in values for a in (12,13,14)), track
        assert 'name="wap7.trf"' in text and 'skipFromLod=4' in text
        assert (folder/'wap7_transformator.script.tl').is_file()
        assert (folder/'wap7.trf.lua').is_file(), 'TF3 requires a .trf.lua source for the virtual .trf resource'
        print('wap7: six sampled pantograph tracks across all four LODs checked')
    if vb:
        assert 'multipleUnitOnly=true' in text and 'reversible=true' in text
        assert 'yearFrom=2022' in text and f'capacity={CAPACITY[kind]}' in text
        assert 'cab_eye_camera_reference' not in seat_text
        assert text.count('crew=true')==(2 if kind=='DTC' else 0)
        for side in ('left','right'):
            assert node_text.count('open_doors_'+side+'=')==8
            assert node_text.count('close_doors_'+side+'=')==8
        for ref in set(re.findall(r'id="(ani/[^"]+)"',node_text)):
            ani=(folder/ref).read_text()
            times=[float(v) for v in re.search(r'times=\{([^}]+)\}',ani).group(1).split(',')]
            frames=re.findall(r'\{([0-9.,e+\-]+)\}',ani.split('transfs=',1)[1])
            values=[[float(v) for v in frame.split(',')] for frame in frames]
            assert len(times)==len(values) and all(len(v)==16 and all(math.isfinite(x) for x in v) for v in values)
            if 'pantograph' in ref:
                assert times==list(range(0,1001,10)) and abs(values[-1][0]-values[0][0])>.1
            else:
                assert times==list(range(0,2001,100))
                assert abs(values[-1][12]-values[0][12])==1
        if kind.startswith('TC'):
            assert node_text.count('pantograph=')==12
            assert (folder/'vb.trf.lua').is_file() and (folder/'vb_transformator.script.tl').is_file()
            bounds=re.search(r'boundingInfo=\{bbMin=\{([^}]+)\},bbMax=\{([^}]+)\}',text)
            assert float(bounds.group(2).split(',')[2])>=5.917
    for suffix,size in [('store',(414,286)),('icon_small@2x',(300,112)),('icon_small',(150,56)),('icon20@2x',(108,40)),('icon20',(54,20))]:
        icon=Image.open(folder/'icons'/(model.stem+'_'+suffix+'.tga'))
        assert icon.size==size and icon.mode=='RGBA'
        assert icon.getchannel('A').getextrema()==(0,255)
    print(f'{model.stem}: {len(meshes)} meshes checked; {len(palette_tiles)} original colours; final LOD {far_bytes:,} bytes; DDS/reference/icon checks passed')

import json
for count in (8,16):
    source=json.loads((MOD.parents[1]/f'vande_bharat_v01/assemblies/VB_{count}_formation.json').read_text())
    path=MOD/'content/vehicle/train/vande_bharat'/f'vande_bharat_{count}.mu.lua'
    entries=re.findall(r'name="([^"]+\.mdl)",forward=(true|false)',path.read_text())
    assert len(entries)==count and entries[0][1]=='true' and entries[-1][1]=='false'
    seats=0
    for (ref,facing),car in zip(entries,source['cars']):
        assert ref.startswith('gj94_indian_rail_pack::/vehicle/train/'),ref
        model=resolve_model_ref(MOD,path,ref)
        assert model.is_file() and model.stem=='vb_'+car['type'].lower()
        assert (facing=='true')==(car['rotation_z_deg']==180)
        seats+=CAPACITY[car['type']]
    assert seats==source['passenger_seats_compact_total']
    assert count*19.375==source['total_outer_anchor_span_m']
    print(f'Vande Bharat {count}: formation references, outward cabs, {seats} seats and {count*19.375} m spacing checked')
