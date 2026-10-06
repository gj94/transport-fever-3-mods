"""Render machinery gallery views from an explicit, already-integrated master.

This script NEVER rebuilds components, edits mesh data, or saves a .blend file.
All presentation changes are transient and are restored in memory afterwards.

Usage (the owner must release the central render slot before running):
  blender -b -t 2 --python scripts/render_machinery_gallery.py -- \
    /absolute/delivery/WAP7_detail_v02.blend through_door 256 1600 2
  blender -b -t 2 --python scripts/render_machinery_gallery.py -- \
    /absolute/delivery/WAP7_detail_v02.blend cutaway 256 1800 2

Optional flags: --output-dir DIR, --expected-master-sha256 HASH, --stage-only
The cutaway is the approved central-machinery isolation, not a new shell Boolean.
It hides all non-MACHV02_ render geometry, then the machinery roof, trays, side
lining and ribs. Through-door keeps the intact vehicle and opens cab1 to84deg.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VIEWS = {
    "through_door": {
        "camera": (7.64, -0.02, 2.95),
        "target": (-3.2, 0.0, 2.66),
        "lens_mm": 21.0,
        "height_ratio": 0.72,
    },
    "cutaway": {
        "camera": (12.9, -12.8, 10.9),
        "target": (0.0, 0.0, 2.20),
        "lens_mm": 38.0,
        "height_ratio": 650 / 1200,
    },
}
GEOMETRY_TYPES = {
    "MESH", "CURVE", "FONT", "SURFACE", "META", "VOLUME", "CURVES",
    "POINTCLOUD", "GREASEPENCIL", "GPENCIL",
}
PRESENTATION_COLLECTIONS = {
    "V02_PRESENTATION_ONLY", "ENV02_PHOTOGRAPHIC_RAILWAY", "PRESENTATION_ONLY",
    "CABTEST_PRESENTATION", "MACHTEST_PRESENTATION",
}
CUTAWAY_PREFIXES = (
    "MACHV02_Ceiling_", "MACHV02_Cabletray_",
    "MACHV02_Inner_sidewall_panel", "MACHV02_Body_inner_channel_rib",
)


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Value must be positive")
    return number


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", type=Path, help="Explicit integrated delivery .blend")
    parser.add_argument("view", choices=tuple(VIEWS))
    parser.add_argument("samples", nargs="?", type=positive_int, default=256)
    parser.add_argument("width", nargs="?", type=positive_int, default=1600)
    parser.add_argument("threads", nargs="?", type=positive_int, default=2)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--expected-master-sha256")
    parser.add_argument("--stage-only", action="store_true",
                        help="Validate and stage transiently; write JSON, not an image")
    args = parser.parse_args(argv)
    if args.width < 128 or args.width > 8192:
        parser.error("Width must be between 128 and 8192 pixels")
    if args.threads > 64:
        parser.error("Threads must be at most 64; follow the owner's render-slot limit")
    if args.expected_master_sha256:
        args.expected_master_sha256 = args.expected_master_sha256.lower()
        if len(args.expected_master_sha256) != 64 or any(
                c not in "0123456789abcdef" for c in args.expected_master_sha256):
            parser.error("Expected master SHA256 must contain 64 hexadecimal characters")
    return args


def sha256_file(path: Path) -> str:
    """Stream large masters rather than allocating a second full file in RAM."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matrix_rows(matrix):
    return [list(row) for row in matrix]


def matrix_error(matrix, rows):
    return max(abs(value - rows[i][j])
               for i, row in enumerate(matrix) for j, value in enumerate(row))


def run(args):
    import bpy
    from mathutils import Vector

    master = args.master.expanduser().resolve()
    if not master.is_file() or master.suffix.lower() != ".blend":
        raise FileNotFoundError("Supply the actual integrated delivery .blend: " + str(master))
    before_sha = sha256_file(master)
    if args.expected_master_sha256 and before_sha != args.expected_master_sha256:
        raise ValueError("Master SHA256 does not match the expected delivery file")
    output_dir = (args.output_dir or master.parent / "previews" / "machinery_gallery").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = "machinery_" + args.view
    png_path = output_dir / (stem + ".png")
    json_path = output_dir / (stem + ("_stage_only.json" if args.stage_only else ".json"))
    report = {
        "status": "initializing",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "master_path": str(master),
        "master_sha256": before_sha,
        "master_bytes": master.stat().st_size,
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "view": args.view,
        "samples": args.samples,
        "width": args.width,
        "threads": args.threads,
        "stage_only": args.stage_only,
        "geometry_reapplied": False,
        "mesh_data_edited": False,
        "master_saved": False,
        "image_path": None,
        "visibility_changes": [],
        "door_pose_changes": [],
        "presentation_geometry_changes": [],
    }
    error = None
    original = {}
    saved_settings = []
    stage = None
    added_objects = []
    added_world = None
    old_world = None
    old_camera = None
    hinge = None
    hinge_angle = None
    scene = None

    def set_setting(owner, attribute, value):
        saved_settings.append((owner, attribute, getattr(owner, attribute)))
        setattr(owner, attribute, value)

    def hide(obj, reason):
        if not obj.hide_render:
            report["visibility_changes"].append({
                "object": obj.name, "before_hide_render": False,
                "after_hide_render": True, "reason": reason,
            })
            obj.hide_render = True

    try:
        bpy.ops.wm.open_mainfile(filepath=str(master))
        scene = bpy.context.scene
        old_world, old_camera = scene.world, scene.camera
        bpy.context.view_layer.update()
        machinery = [o for o in bpy.data.objects if o.name.startswith("MACHV02_")
                     and o.type in GEOMETRY_TYPES]
        if not machinery:
            raise RuntimeError("This master has no integrated MACHV02_ machinery geometry")
        root = bpy.data.objects.get("WAP7_ROOT")
        if root is None:
            raise RuntimeError("The integrated master is missing WAP7_ROOT")
        report["asset_root_matrix"] = matrix_rows(root.matrix_world)
        report["machinery_geometry_objects"] = len(machinery)
        report["source_object_count"] = len(bpy.data.objects)
        for obj in bpy.data.objects:
            original[obj.name] = {
                "hide_render": bool(obj.hide_render),
                "matrix": matrix_rows(obj.matrix_world),
                "parent": obj.parent.name if obj.parent else None,
                "data": obj.data.name if obj.data else None,
            }
        dependencies = []
        missing = []
        for image in bpy.data.images:
            if image.source != "FILE":
                continue
            path = Path(bpy.path.abspath(image.filepath)) if image.filepath else None
            exists = bool(image.packed_file) or bool(path and path.is_file())
            dependencies.append({"image": image.name, "path": str(path) if path else None,
                                 "packed": bool(image.packed_file), "readable": exists})
            if not exists:
                missing.append(image.name)
        report["image_dependencies"] = dependencies
        font_dependencies = []
        for font in bpy.data.fonts:
            if font.filepath in {"", "<builtin>"}:
                continue
            path = Path(bpy.path.abspath(font.filepath))
            exists = bool(font.packed_file) or path.is_file()
            font_dependencies.append({"font": font.name, "path": str(path),
                                      "packed": bool(font.packed_file), "readable": exists})
            if not exists:
                missing.append("font:" + font.name)
        report["font_dependencies"] = font_dependencies
        if missing:
            raise FileNotFoundError("Missing delivery dependencies: " + ", ".join(missing))

        old_world, old_camera = scene.world, scene.camera
        report["replaced_world"] = old_world.name if old_world else None
        report["replaced_camera"] = old_camera.name if old_camera else None
        for obj in list(bpy.data.objects):
            if obj.type == "LIGHT":
                hide(obj, "Replace existing lights with the approved neutral machinery lighting")
            is_stage = (any(c.name in PRESENTATION_COLLECTIONS for c in obj.users_collection)
                        or obj.name.startswith(("V02_STAGE ", "ENV02_", "MACHTEST_", "CABTEST_")))
            if is_stage and obj.type != "EMPTY":
                hide(obj, "Remove unrelated presentation from this neutral machinery view")
            if args.view == "cutaway":
                is_geometry = (obj.type in GEOMETRY_TYPES or
                               (obj.type == "EMPTY" and obj.instance_type != "NONE"))
                if is_geometry and not obj.name.startswith("MACHV02_"):
                    hide(obj, "Central-machinery isolation: hide non-machinery geometry")
                elif obj.name.startswith(CUTAWAY_PREFIXES) or obj.get("cutaway_hide", False):
                    hide(obj, "Roof-off review: hide machinery ceiling, trays, side lining and ribs")

        if args.view == "through_door":
            hinge = bpy.data.objects.get("CABV02_1_Rear_door_hinge")
            if hinge is None or "open_angle_deg" not in hinge:
                raise RuntimeError("The delivery master lacks the integrated cab1 rear-door hinge")
            hinge_angle = float(hinge["open_angle_deg"])
            before_angle = float(hinge.rotation_euler.z)
            before_matrix = matrix_rows(hinge.matrix_world)
            hinge["open_angle_deg"] = 84.0
            hinge.update_tag(refresh={"OBJECT"})
            bpy.context.view_layer.update()
            delta = float(hinge.rotation_euler.z) - before_angle
            expected = math.radians(84.0 - hinge_angle)
            if abs(delta - expected) > 1e-4:
                raise RuntimeError("Existing rear-door driver did not evaluate; no substitute geometry was created")
            report["door_pose_changes"].append({
                "object": hinge.name, "property": "open_angle_deg", "before": hinge_angle,
                "after": 84.0, "before_world_matrix": before_matrix,
                "after_world_matrix": matrix_rows(hinge.matrix_world),
                "reason": "Presentation-only view through the existing hinged door",
            })

        stage = bpy.data.collections.new("MACHGALLERY_PRESENTATION_" + args.view)
        scene.collection.children.link(stage)
        added_world = bpy.data.worlds.new("MACHGALLERY_NEUTRAL_WORLD")
        added_world.use_nodes = True
        background = added_world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (0.61, 0.64, 0.67, 1.0)
        background.inputs["Strength"].default_value = 0.35
        scene.world = added_world
        report["world"] = {"type": "constant neutral", "linear_rgb": [0.61, 0.64, 0.67],
                           "strength": 0.35, "external_environment_images": False}
        report["lights"] = []

        def world_point(point):
            return root.matrix_world @ Vector(point)

        def area(name, position, target, power, size, size_y, color):
            data = bpy.data.lights.new("MACHGALLERY_" + name, "AREA")
            data.energy, data.shape, data.size, data.size_y = power, "RECTANGLE", size, size_y
            data.color = color
            obj = bpy.data.objects.new("MACHGALLERY_" + name, data)
            stage.objects.link(obj)
            added_objects.append(obj)
            obj.location = world_point(position)
            obj.rotation_euler = (world_point(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
            report["lights"].append({"object": obj.name, "asset_position": position,
                                     "asset_target": target, "power_w": power,
                                     "size_m": [size, size_y], "linear_rgb": color})

        for index, x in enumerate((-6.0, -3.6, -1.2, 1.2, 3.6, 6.0)):
            area("practical_" + str(index), (x, 0, 3.498), (x, 0, 1.7),
                 24, 0.62, 0.12, (0.95, 1.0, 0.95))
        area("door_soft_fill", (7.0, 0, 2.8), (3.8, 0, 2.3),
             38, 0.62, 0.12, (0.91, 0.95, 1.0))
        if args.view == "cutaway":
            area("cutaway_softbox", (0, -4, 9), (0, 0, 2.4),
                 1800, 10.0, 3.5, (0.96, 0.98, 1.0))

        preset = VIEWS[args.view]
        camera_data = bpy.data.cameras.new("MACHGALLERY_" + args.view)
        camera = bpy.data.objects.new("MACHGALLERY_" + args.view, camera_data)
        stage.objects.link(camera)
        added_objects.append(camera)
        camera.location = world_point(preset["camera"])
        camera.rotation_euler = (world_point(preset["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.lens, camera_data.clip_start, camera_data.clip_end = preset["lens_mm"], 0.012, 100.0
        camera_data.dof.use_dof = False
        scene.camera = camera
        report["camera"] = dict(preset, object=camera.name,
                                world_matrix=matrix_rows(camera.matrix_world), clip_start_m=0.012)
        report["height"] = max(1, round(args.width * preset["height_ratio"]))
        report["blender_version"] = bpy.app.version_string
        settings = [
            (scene.render, "engine", "CYCLES"),
            (scene.cycles, "device", "CPU"),
            (scene.cycles, "samples", args.samples),
            (scene.cycles, "use_adaptive_sampling", True),
            (scene.cycles, "adaptive_threshold", 0.02),
            (scene.cycles, "adaptive_min_samples", 32),
            (scene.cycles, "use_denoising", False),
            (scene.cycles, "max_bounces", 7),
            (scene.cycles, "transmission_bounces", 6),
            (scene.cycles, "transparent_max_bounces", 10),
            (scene.cycles, "sample_clamp_indirect", 4.0),
            (scene.render, "threads_mode", "FIXED"),
            (scene.render, "threads", args.threads),
            (scene.render, "resolution_x", args.width),
            (scene.render, "resolution_y", report["height"]),
            (scene.render, "resolution_percentage", 100),
            (scene.render, "film_transparent", False),
            (scene.render, "filepath", str(png_path)),
            (scene.render.image_settings, "file_format", "PNG"),
            (scene.render.image_settings, "color_mode", "RGB"),
            (scene.render.image_settings, "color_depth", "8"),
            (scene.view_settings, "view_transform", "AgX"),
            (scene.view_settings, "look", "AgX - Medium High Contrast"),
            (scene.view_settings, "exposure", 0.0),
        ]
        for owner, attribute, value in settings:
            set_setting(owner, attribute, value)
        report["render_settings"] = {
            "engine": "Cycles CPU", "maximum_samples_per_pixel": args.samples,
            "adaptive_sampling": True, "adaptive_min_samples": 32, "noise_threshold": 0.02, "denoising": False, "max_bounces": 7,
            "transmission_bounces": 6, "indirect_clamp": 4.0,
            "view_transform": "AgX", "look": "AgX - Medium High Contrast", "exposure": 0.0,
        }
        bpy.context.view_layer.update()
        report["staged_visible_geometry_count"] = sum(
            o.type in GEOMETRY_TYPES and not o.hide_render for o in bpy.data.objects)
        report["visibility_change_count"] = len(report["visibility_changes"])
        report["status"] = "staged_not_rendered" if args.stage_only else "rendering"
        json_path.write_text(json.dumps(report, indent=2))
        print("MACHINERY_GALLERY_STAGED", args.view, before_sha, flush=True)
        if not args.stage_only:
            started = time.monotonic()
            bpy.ops.render.render(write_still=True)
            report["render_seconds"] = time.monotonic() - started
            if not png_path.is_file():
                raise RuntimeError("Blender returned without the requested PNG")
            report["image_path"] = str(png_path)
            report["image_sha256"] = sha256_file(png_path)
            report["image_bytes"] = png_path.stat().st_size
            report["status"] = "rendered"
    except Exception as exc:
        error = exc
        report["status"] = "failed"
        report["error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        # Restore original object visibility, the existing door, world, camera and settings.
        if hinge is not None and hinge_angle is not None:
            hinge["open_angle_deg"] = hinge_angle
            hinge.update_tag(refresh={"OBJECT"})
        for name, state in original.items():
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render = state["hide_render"]
        if scene is not None:
            scene.world, scene.camera = old_world, old_camera
            view_settings = {}
            for owner, attribute, value in reversed(saved_settings):
                if owner == scene.view_settings:
                    view_settings[attribute] = value
                else:
                    setattr(owner, attribute, value)
            # Looks depend on the active transform; restore that enum first.
            for attribute in ("view_transform", "look", "exposure"):
                if attribute in view_settings:
                    setattr(scene.view_settings, attribute, view_settings[attribute])
        for obj in reversed(added_objects):
            data, object_type = obj.data, obj.type
            bpy.data.objects.remove(obj, do_unlink=True)
            if data and data.users == 0:
                if object_type == "LIGHT":
                    bpy.data.lights.remove(data)
                elif object_type == "CAMERA":
                    bpy.data.cameras.remove(data)
        if stage is not None:
            bpy.data.collections.remove(stage)
        if added_world is not None and added_world.users == 0:
            bpy.data.worlds.remove(added_world)
        if original:
            bpy.context.view_layer.update()
            changed = []
            for name, state in original.items():
                obj = bpy.data.objects.get(name)
                if (obj is None or obj.hide_render != state["hide_render"]
                        or (obj.parent.name if obj.parent else None) != state["parent"]
                        or (obj.data.name if obj.data else None) != state["data"]
                        or matrix_error(obj.matrix_world, state["matrix"]) > 1e-5):
                    changed.append(name)
            report["original_objects_restored_in_memory"] = not changed
            report["unrestored_original_objects"] = changed
            if changed and error is None:
                error = RuntimeError("Original in-memory state failed restoration: " + ", ".join(changed[:12]))
        try:
            after_sha = sha256_file(master)
        except OSError as exc:
            after_sha = None
            if error is None:
                error = exc
        report["master_sha256_after"] = after_sha
        report["master_file_unchanged"] = after_sha == before_sha
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if after_sha != before_sha and error is None:
            error = RuntimeError("The master changed on disk during staging/rendering; check concurrent work")
        if error is not None:
            report["status"] = "failed"
            report["error"] = type(error).__name__ + ": " + str(error)
        json_path.write_text(json.dumps(report, indent=2))
    if error is not None:
        raise error
    print("MACHINERY_GALLERY_COMPLETE", args.view, report["status"], str(json_path), flush=True)
    return report


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    run(parse_args(arguments))
