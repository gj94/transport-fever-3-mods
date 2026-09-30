"""Original low-poly entrance boards for TF3's custom-entity API.

The boards are visual markers. Track templates continue to enforce the caps.
"""
from pathlib import Path
import math
import struct

from PIL import Image, ImageDraw, ImageFont

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def board_texture(speed):
    image = Image.new("RGB", (512, 512), "#727a80")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 447, 447), fill="#f9d33e")
    draw.rounded_rectangle((12, 12, 435, 435), radius=16, outline="#171a19", width=12)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 224 if speed < 100 else 182)
    small = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 50)
    draw.text((224, 203), str(speed), anchor="mm", font=font, fill="#171a19")
    draw.text((224, 354), "km/h", anchor="mm", font=small, fill="#171a19")
    return image


def geometry():
    """The +X face has the number; the -X back and edges are blank grey."""
    vertices, indices = [], []
    face_uv = [(4/512, 1-443/512), (443/512, 1-443/512),
               (443/512, 1-4/512), (4/512, 1-4/512)]
    grey_uv = [(480/512, 1-480/512)] * 4

    def box(lo, hi, numbered=False):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        faces = [
            ([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)], (1,0,0)),
            ([(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)], (-1,0,0)),
            ([(x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1)], (0,1,0)),
            ([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)], (0,-1,0)),
            ([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)], (0,0,1)),
            ([(x0,y1,z0),(x1,y1,z0),(x1,y0,z0),(x0,y0,z0)], (0,0,-1)),
        ]
        for face_index, (points, normal) in enumerate(faces):
            uv = face_uv if numbered and face_index == 0 else grey_uv
            tangent = (0, 1, 0) if normal[0] else (1, 0, 0)
            if normal[0] < 0:
                tangent = (0, -1, 0)
            start = len(vertices)
            vertices.extend((*p, *normal, *xy, *tangent, 1) for p, xy in zip(points, uv))
            indices.extend(start + i for i in (0, 1, 2, 0, 2, 3))

    box((-0.07, -0.035, -0.3), (-0.01, 0.035, 2.0))
    box((-0.10, -0.13, -0.05), (0.10, 0.13, 0.09))
    box((-0.04, -0.43, 1.62), (0.04, 0.43, 2.40), numbered=True)
    return vertices, indices


def write_mesh(path, dump):
    vertices, indices = geometry()
    attrs, blob = {}, bytearray()
    for name, start, width in (("position",0,3),("normal",3,3),("uv0",6,2),("tangent",8,4)):
        values = [v for vertex in vertices for v in vertex[start:start+width]]
        block = struct.pack("<" + str(len(values)) + "f", *values)
        attrs[name] = {"count": len(block), "numComp": width, "offset": len(blob)}
        blob.extend(block)
    index_desc = {"count": len(indices)*4, "offset": len(blob)}
    blob.extend(struct.pack("<" + str(len(indices)) + "I", *indices))
    dump(path, {"subMeshes": [{"indices": {name: index_desc for name in attrs}}], "vertexAttr": attrs})
    Path(str(path) + ".blob").write_bytes(blob)


def build_speed_boards(mod, speeds, lua):
    folder = mod / "content/boards"
    (folder / "msh").mkdir(parents=True, exist_ok=True)
    (folder / "mat/tex").mkdir(parents=True, exist_ok=True)

    def dump(path, data):
        path.write_text("function data()\nreturn " + lua(data) + "\nend\n", encoding="utf-8")

    write_mesh(folder / "msh/speed_board.msh", dump)
    Image.new("RGB", (4, 4), (128,128,255)).save(folder / "mat/tex/normal.tga")
    Image.new("RGB", (4, 4), (0,70,255)).save(folder / "mat/tex/metal_gloss_ao.tga")
    for speed in speeds:
        key = f"speed_{speed:03d}"
        # Remove the unused repeating-decoration prototype from build output.
        obsolete = folder / f"{key}.edge.lua"
        if obsolete.exists():
            obsolete.unlink()
        image = board_texture(speed)
        image.save(folder / f"mat/tex/{key}.tga")
        icon = image.crop((0,0,448,448)).resize((80,80), Image.Resampling.LANCZOS)
        icon.save(folder / f"{key}.tga")
        icon.resize((160,160), Image.Resampling.LANCZOS).save(folder / f"{key}@2x.tga")
        params = {"light_receiver": {"fragmentProperties": [{"isLegacyMaterial": True, "lightMask": 2}]}}
        for name, sampler, filename in (("albedo","albedoTex",f"{key}.tga"),
                                        ("normal","normalTex","normal.tga"),
                                        ("metal_gloss_ao","metalGlossAoTex","metal_gloss_ao.tga")):
            params["map_" + name] = {"fragmentSamplers": {sampler: {
                "fileName": "tex/" + filename, "type": "TWOD", "wrapS": "REPEAT", "wrapT": "REPEAT"}}}
        dump(folder / f"mat/{key}.mtl", {"order": 0, "params": params, "type": "PHYSICAL_NRML_MAP"})
        dump(folder / f"{key}.mdl", {
            "boundingInfo": {"bbMin": [-0.10,-0.43,-0.30], "bbMax": [0.10,0.43,2.40]},
            "collider": {"type": "BOX", "params": {"halfExtents": [0.10,0.43,1.35]},
                         "transf": [*IDENTITY[:12], 0,0,1.05,1]},
            "lods": [{"visibleFrom": 0, "visibleTo": 800,
                      "node": {"name": "RootNode", "transf": IDENTITY,
                               "children": [{"name": "SpeedBoard", "transf": IDENTITY,
                                             "mesh": "msh/speed_board.msh", "materials": [f"mat/{key}.mtl"]}]}}],
            "metadata": {}, "version": 2})


def validate_speed_boards(mod, speeds, parse):
    folder = mod / "content/boards"
    descriptor = parse((folder / "msh/speed_board.msh").read_text())
    blob = (folder / "msh/speed_board.msh.blob").read_bytes()
    attrs = descriptor["vertexAttr"]
    arrays = {}
    for name, attr in attrs.items():
        start, count = attr["offset"], attr["count"]
        assert count % (4 * attr["numComp"]) == 0 and start + count <= len(blob)
        arrays[name] = struct.unpack("<" + str(count//4) + "f", blob[start:start+count])
        assert all(math.isfinite(v) for v in arrays[name])
    vertices = list(zip(*[iter(arrays["position"])]*3))
    normals = list(zip(*[iter(arrays["normal"])]*3))
    uv = list(zip(*[iter(arrays["uv0"])]*2))
    # Last box is the board. Only its outward +X face samples the number tile.
    assert all(xy[0] < 448/512 for xy in uv[48:52])
    assert all(xy[0] > 448/512 for xy in uv[52:72])
    index_desc = descriptor["subMeshes"][0]["indices"]["position"]
    indices = struct.unpack("<" + str(index_desc["count"]//4) + "I", blob[index_desc["offset"]:])
    assert len(indices) % 3 == 0 and max(indices) < len(vertices)
    for start in range(0,len(indices),3):
        a,b,c = (vertices[indices[start+i]] for i in range(3))
        ab,ac = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
        cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
        assert sum(cross[i]*normals[indices[start]][i] for i in range(3)) > 0
    for speed in speeds:
        key = f"speed_{speed:03d}"
        assert not (folder / f"{key}.edge.lua").exists()
        model = parse((folder / f"{key}.mdl").read_text())
        assert model["metadata"] == [], "Boards must have no signal or simulation metadata"
        node = model["lods"][0]["node"]["children"][0]
        assert (folder / node["mesh"]).is_file()
        for point in vertices:
            assert all(model["boundingInfo"]["bbMin"][i]-1e-6 <= point[i] <= model["boundingInfo"]["bbMax"][i]+1e-6 for i in range(3))
        material_path = folder / node["materials"][0]
        material = parse(material_path.read_text())
        for name in ("albedo","normal","metal_gloss_ao"):
            for sampler in material["params"]["map_"+name]["fragmentSamplers"].values():
                assert (material_path.parent / sampler["fileName"]).is_file()
        with Image.open(folder / f"mat/tex/{key}.tga") as image:
            assert image.size == (512,512) and image.tobytes() == board_texture(speed).tobytes()
    return {"numberedBoards": len(speeds), "trianglesPerBoard": len(indices)//3,
            "numberedFace": "+X", "blankBack": True,
            "checks": ["mesh byte ranges, indices and outward winding", "bounding boxes",
                       "model, material and texture references", "matching number textures",
                       "numbered front and blank back UVs", "no signal or simulation metadata"]}
