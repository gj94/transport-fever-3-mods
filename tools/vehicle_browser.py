"""Add the purchase-browser extension without rebuilding vehicle geometry."""
from pathlib import Path
import hashlib
import json
from pack_settings import REVISION
from release_metadata import write_release_metadata

ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "gj94_indian_rail_pack"
MOD = ROOT / "game_build" / MOD_ID


def write_vehicle_browser(mod):
    folder = mod / "content/gui"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "indian_rail_vehicle_section.script.lua").write_text(
        (ROOT / "tools/indian_rail_vehicle_section.script.lua").read_text(encoding="utf-8"), encoding="utf-8")
    (folder / "indian_rail_vehicle_section.res.lua").write_text(
        'function data()\nreturn {\n  type = "react-plugin ::ModEntryPointExtension",\n'
        '  data = { filePath = resolve("indian_rail_vehicle_section.script@EntryPoint"), order = -100 },\n'
        '}\nend\n', encoding="utf-8")


def main():
    metadata = json.loads((MOD / "mod.json").read_text())
    assert metadata["modId"] == MOD_ID
    write_vehicle_browser(MOD)
    write_release_metadata(MOD)
    report = {"revision": REVISION, "modId": MOD_ID,
              "extensionSha256": hashlib.sha256((MOD / "content/gui/indian_rail_vehicle_section.script.lua").read_bytes()).hexdigest(),
              "changedResources": ["mod.json", "_metadata/modinfo.json", "content/gui/indian_rail_vehicle_section.script.lua",
                                   "content/gui/indian_rail_vehicle_section.res.lua"]}
    (ROOT / "game_build/vehicle_browser_build.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
