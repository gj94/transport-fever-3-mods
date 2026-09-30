"""Back up and install the validated local speed mod without removing files."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from build_speed_restrictions import REVISION

ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "gj94_track_speed_restrictions"
SOURCE = ROOT / "game_build" / MOD_ID
LOCAL = Path("C:/Program Files (x86)/Steam/userdata/312521856/3493540/local")
DESTINATION = LOCAL / "mods" / MOD_ID


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert SOURCE.resolve().parent == (ROOT / "game_build").resolve()
    assert DESTINATION.resolve().parent == (LOCAL / "mods").resolve()
    assert not (LOCAL / "staging_area" / MOD_ID).exists(), "A staging mod would override this installation"
    metadata = json.loads((SOURCE / "mod.json").read_text())
    assert metadata["modId"] == MOD_ID and metadata["revision"] == REVISION
    installed = json.loads((DESTINATION / "mod.json").read_text())
    assert installed["modId"] == MOD_ID
    for path in (SOURCE / "_metadata/build_validation.json", ROOT / "game_build/speed_dropdown_validation.json",
                 ROOT / "game_build/speed_boundary_validation.json"):
        assert json.loads(path.read_text())["result"].startswith("PASS"), str(path)
    for report_name, script_name in (("speed_dropdown_validation.json", "gui/track_speed_dropdown.script.lua"),
                                    ("speed_boundary_validation.json", "boards/boundaries.script.lua")):
        report = json.loads((ROOT / "game_build" / report_name).read_text())
        assert report["revision"] == REVISION, "Stale validation report: " + report_name
        source_text = (SOURCE / "content" / script_name).read_text(encoding="utf-8")
        assert report["sourceSha256"] == hashlib.sha256(source_text.encode("utf-8")).hexdigest(), report_name
    source = {path.relative_to(SOURCE): path for path in SOURCE.rglob("*") if path.is_file()}
    existing = {path.relative_to(DESTINATION): path for path in DESTINATION.rglob("*") if path.is_file()}
    assert not existing.keys() - source.keys(), "Unexpected installed files; preserve and inspect before updating"
    backup_stem = "Track-Speed-Restrictions-before-track-scan-fix"
    backup = ROOT.parent / (backup_stem + ".zip")
    index = 2
    while backup.exists():
        backup = ROOT.parent / f"{backup_stem}-{index}.zip"
        index += 1
    with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED) as archive:
        for relative, path in sorted(existing.items()):
            archive.write(path, MOD_ID + "/" + relative.as_posix())
    with zipfile.ZipFile(backup) as archive:
        assert archive.testzip() is None
        for relative, path in existing.items():
            assert hashlib.sha256(archive.read(MOD_ID + "/" + relative.as_posix())).hexdigest() == sha(path)
    for relative, path in sorted(source.items()):
        target = DESTINATION / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    for relative, path in source.items():
        assert sha(path) == sha(DESTINATION / relative), str(relative)
    assert len([p for p in DESTINATION.rglob("*") if p.is_file()]) == len(source)
    report = {"result": "PASS", "revision": REVISION, "installedFiles": len(source),
              "verifiedBy": "SHA-256", "destination": str(DESTINATION), "backup": str(backup),
              "runtimeBoardTest": "Not performed by installer; see TRACK-SPEED-RESTRICTIONS.md for the manual verification record"}
    (ROOT / "game_build/speed_board_install_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
