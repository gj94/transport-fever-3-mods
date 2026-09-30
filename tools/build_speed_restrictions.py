"""Build and validate TF3 track variants from the installed stock templates.

Simulation templates and a GUI extension implement a dropdown on stock tracks.
Geometry, materials, and sounds remain references to the base game.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "gj94_track_speed_restrictions"
SPEEDS = (15, 25, 40, 60, 80, 100, 120, 130, 160)
STYLES = {"simple": "Wooden", "standard": "Standard", "high_speed": "Concrete"}
TOKEN = re.compile(r'\s+|--[^\n]*|"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[A-Za-z_]\w*|[{}=(),;]')


class ConstantLua:
    """Read the constant data() tables used by shipped track templates.

    This deliberately rejects executable expressions; it is not a Lua runtime.
    """
    def __init__(self, text):
        self.tokens = []
        pos = 0
        for match in TOKEN.finditer(text):
            if match.start() != pos:
                raise ValueError(f"Unsupported Lua at {text[pos:match.start()]!r}")
            pos = match.end()
            token = match.group()
            if not token.isspace() and not token.startswith("--"):
                self.tokens.append(token)
        if pos != len(text):
            raise ValueError("Unparsed Lua suffix")
        self.i = 0

    def take(self, expected=None):
        token = self.tokens[self.i]
        self.i += 1
        if expected is not None and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        return token

    def value(self):
        token = self.take()
        if token == "{":
            items, fields = [], {}
            while self.tokens[self.i] != "}":
                if self.i + 1 < len(self.tokens) and self.tokens[self.i + 1] == "=":
                    key = self.take()
                    self.take("=")
                    if key in fields:
                        raise ValueError(f"Duplicate field {key}")
                    fields[key] = self.value()
                else:
                    items.append(self.value())
                if self.tokens[self.i] in (",", ";"):
                    self.take()
                elif self.tokens[self.i] != "}":
                    raise ValueError("Missing table separator")
            self.take("}")
            if fields and items:
                raise ValueError("Mixed table not supported")
            return fields if fields else items
        if token == "_":
            self.take("(")
            result = self.value()
            self.take(")")
            return result
        if token.startswith('"'):
            return json.loads(token)
        if token in ("true", "false"):
            return token == "true"
        if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', token):
            return float(token) if any(c in token for c in ".eE") else int(token)
        raise ValueError(f"Unsupported value {token}")

    def data(self):
        for token in ("function", "data", "(", ")", "return"):
            self.take(token)
        result = self.value()
        self.take("end")
        if self.i != len(self.tokens):
            raise ValueError("Unexpected code after data()")
        return result


def lua(value, depth=0):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError("Non-finite number")
        return repr(value)
    if isinstance(value, (dict, list)):
        entries = [f"{k} = {lua(v, depth + 1)}" for k, v in value.items()] if isinstance(value, dict) else [lua(v, depth + 1) for v in value]
        if not entries:
            return "{}"
        return "{\n" + "\n".join("  " * (depth + 1) + entry + "," for entry in entries) + "\n" + "  " * depth + "}"
    raise TypeError(type(value))


def resource_name(style, speed, electric):
    suffix = "_catenary" if electric else ""
    return f"track/{style}_{speed:03d}{suffix}.street_template"


def make_icon(path, style, speed, electric, scale=1):
    width, height = 160 * scale, 90 * scale
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    color = {"simple": "#765339", "standard": "#44677e", "high_speed": "#566258"}[style]
    s = scale
    draw.rounded_rectangle((2*s, 2*s, 158*s, 88*s), 10*s, fill=color)
    for x in range(13, 150, 17):
        draw.line((x*s, 73*s, (x+12)*s, 84*s), fill="#a4a8aa", width=4*s)
    draw.line((12*s, 73*s, 148*s, 73*s), fill="#e0e4e6", width=3*s)
    draw.line((12*s, 83*s, 148*s, 83*s), fill="#e0e4e6", width=3*s)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38*s)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13*s)
    draw.text((80*s, 27*s), str(speed), font=font, anchor="mm", fill="white")
    draw.text((80*s, 56*s), "km/h" + ("  E" if electric else ""), font=small, anchor="mm", fill="white")
    image.save(path)


def build(game_root):
    source_zip = game_root / "base/content/infrastructure/track.zip"
    mod = ROOT / "game_build" / MOD_ID
    track_dir = mod / "content/track"
    track_dir.mkdir(parents=True, exist_ok=True)
    (mod / "_metadata").mkdir(exist_ok=True)
    native = {}
    native_hashes = {}
    with zipfile.ZipFile(source_zip) as archive:
        for style in STYLES:
            for electric in (False, True):
                stem = style + ("_catenary" if electric else "")
                source = f"track/{style}/{stem}.street_template.lua"
                raw = archive.read(source)
                native[style, electric] = ConstantLua(raw.decode("utf-8-sig")).data()
                native_hashes[source] = hashlib.sha256(raw).hexdigest()

    variants = []
    for style_index, (style, label) in enumerate(STYLES.items()):
        for speed_index, speed in enumerate(SPEEDS):
            for electric in (False, True):
                original = native[style, electric]
                data = copy.deepcopy(original)
                for lane in data["laneConfigs"]:
                    lane["speed"] = speed / 3.6
                key = Path(resource_name(style, speed, electric)).name.removesuffix(".street_template")
                data["description"] = {
                    "name": f"{label} track - {speed} km/h" + (" (electrified)" if electric else ""),
                    "description": f"{speed} km/h track speed cap. Curves, bridges and vehicle limits can reduce speed further. "
                        "Choose this cap from Speed limit on the stock track option. Electrification changes retain this cap.",
                    "icon": f"{key}.tga",
                    "previewIcon": original["description"]["previewIcon"],
                }
                # Pair by speed and appearance, so toggling wires never restores a stock limit.
                data.pop("catenaryAdd", None)
                data.pop("catenaryRemove", None)
                data["catenaryRemove" if electric else "catenaryAdd"] = resource_name(style, speed, not electric)
                data["availability"].pop("notificationGroup", None)
                data["availability"].pop("notificationSortKey", None)
                data["availability"]["notifyWhenAvailable"] = False
                for category in data["menuCategory"]["categories"]:
                    category["order"] = 10000 + style_index * 1000 + speed_index * 10 + int(electric)
                text = "-- Track Speed Restrictions: generated by tools/build_speed_restrictions.py\nfunction data()\nreturn " + lua(data) + "\nend\n"
                path = track_dir / (key + ".street_template.lua")
                path.write_text(text, encoding="utf-8")
                make_icon(track_dir / (key + ".tga"), style, speed, electric)
                make_icon(track_dir / (key + "@2x.tga"), style, speed, electric, 2)
                variants.append({"resource": resource_name(style, speed, electric), "style": style,
                                 "speedKmh": speed, "electrified": electric})

    gui_dir = mod / "content/gui"
    gui_dir.mkdir(exist_ok=True)
    (gui_dir / "track_speed_dropdown.script.lua").write_text(
        (ROOT / "tools/track_speed_dropdown.script.lua").read_text(encoding="utf-8"), encoding="utf-8")
    (gui_dir / "track_speed_dropdown.res.lua").write_text(
        'function data()\nreturn {\n  type = "react-plugin ::ModEntryPointExtension",\n'
        '  data = { filePath = resolve("track_speed_dropdown.script@EntryPoint"), order = -100 },\n}\nend\n',
        encoding="utf-8")
    metadata = {"name": "Track Speed Restrictions", "summary": "Speed dropdown on the existing track options",
                "description": "Choose Default or a 15-160 km/h cap from Speed limit on the six stock track choices. Works for building and replacement. Old speed-limited tracks remain compatible without crowding the menu.",
                "authors": [{"name": "gj94", "role": "CREATOR"}], "tags": ["Track"],
                "url": "https://github.com/gj94/transport-fever-3-mods"}
    (mod / "mod.json").write_text(json.dumps({"modId": MOD_ID, "revision": 3, "severityAdd": "None",
                "severityRemove": "Critical", "visible": True, "cosmetic": False}, indent=2) + "\n")
    (mod / "_metadata/modinfo.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (mod / "README.txt").write_text(
        "TRACK SPEED RESTRICTIONS - TF3\n\nEnable this mod when starting or loading a game.\n"
        "In the track menu choose a stock track, then select Speed limit from its dropdown.\n"
        "Default uses the normal stock limit. Other choices are 15-160 km/h.\n"
        "Use track replacement/upgrade on an existing section, or lay a new section.\n"
        "For electric trains select the electrified variant; adding/removing wires preserves the cap.\n"
        "Stock availability years still apply. Curves, bridges and train ratings can impose lower limits.\n"
        "Both travel directions share the limit. Decorative signs do not enforce restrictions.\n"
        "Replace every restricted track with stock track before removing this mod from a save.\n"
        "Revision 1 tracks remain registered and keep their saved limits.\n"
        "Revision 3 corrects the Lua script data() export required at startup.\n"
        "Revision 1 track operation was user-confirmed; the dropdown still needs a play test.\n")
    report = validate(mod, native, game_root, variants)
    report["stockTemplateSha256"] = native_hashes
    (mod / "_metadata/build_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    output = ROOT / "dist/Track-Speed-Restrictions-TF3.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(mod.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(mod.parent).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Package integrity check failed")
        if len(archive.namelist()) != len([p for p in mod.rglob("*") if p.is_file()]):
            raise ValueError("Package file count differs")
    print(json.dumps({"mod": str(mod), "zip": str(output), "variants": len(variants),
                      "validation": report["result"]}, indent=2))


def validate(mod, native, game_root, variants):
    # Resolve all virtual base resources, including .lua-backed resources and @2x icons.
    base_resources = set()
    for source_zip in (game_root / "base/content").rglob("*.zip"):
        prefix = source_zip.relative_to(game_root / "base/content").parent.as_posix()
        with zipfile.ZipFile(source_zip) as archive:
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                full = ("" if prefix == "." else prefix + "/") + name
                base_resources.add(full)
                if full.endswith(".lua"):
                    base_resources.add(full[:-4])
                if "@2x" in full:
                    base_resources.add(full.replace("@2x", ""))
    expected_resources = {v["resource"] for v in variants}
    actual_resources = {p.relative_to(mod / "content").as_posix().removesuffix(".lua")
                        for p in (mod / "content").rglob("*.street_template.lua")}
    if actual_resources != expected_resources:
        raise ValueError("Unexpected or missing track variants")
    for variant in variants:
        path = mod / "content" / (variant["resource"] + ".lua")
        data = ConstantLua(path.read_text(encoding="utf-8")).data()
        original = native[variant["style"], variant["electrified"]]
        for lane, stock_lane in zip(data["laneConfigs"], original["laneConfigs"], strict=True):
            if not math.isclose(lane["speed"] * 3.6, variant["speedKmh"], abs_tol=1e-10):
                raise ValueError(f"Wrong cap: {path}")
            if {k: v for k, v in lane.items() if k != "speed"} != {k: v for k, v in stock_lane.items() if k != "speed"}:
                raise ValueError(f"Track lane geometry or transport modes changed: {path}")
        mutable = {"laneConfigs", "description", "catenaryAdd", "catenaryRemove", "availability", "menuCategory"}
        if {k: v for k, v in data.items() if k not in mutable} != {k: v for k, v in original.items() if k not in mutable}:
            raise ValueError(f"Stock geometry, curves, costs or other fields changed: {path}")
        if (data["availability"]["yearFrom"], data["availability"]["yearTo"]) != (original["availability"]["yearFrom"], original["availability"]["yearTo"]):
            raise ValueError(f"Stock availability changed: {path}")
        pair_key = "catenaryRemove" if variant["electrified"] else "catenaryAdd"
        expected_pair = resource_name(variant["style"], variant["speedKmh"], not variant["electrified"])
        if data[pair_key] != expected_pair or expected_pair not in expected_resources:
            raise ValueError(f"Electrification changes speed: {path}")
        for ref in re.findall(r'"(::/[^"\n]+)"', path.read_text(encoding="utf-8")):
            if ref[3:] not in base_resources:
                raise ValueError(f"Unresolved stock resource {ref}: {path}")
        for scale, suffix in ((1, ""), (2, "@2x")):
            icon_path = path.parent / data["description"]["icon"].replace(".tga", suffix + ".tga")
            with Image.open(icon_path) as icon:
                if icon.size != (160 * scale, 90 * scale) or icon.mode != "RGBA":
                    raise ValueError(f"Invalid icon: {icon_path}")
    return {"result": "PASS: static resource validation", "variants": len(variants),
            "checks": ["constant Lua syntax", "exact speed caps", "stock lane geometry and transport modes",
                       "stock curve rules and costs", "availability years", "paired electrification resources",
                       "all referenced base assets exist", "regular and high resolution icons"],
            "runtimePlayTest": "Pending", "variantList": variants}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=Path("D:/SteamLibrary/steamapps/common/Transport Fever 3"))
    build(parser.parse_args().game_root)
