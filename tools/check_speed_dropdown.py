"""Exercise the dropdown Lua against the shipped templates and GUI API contract.

Requires lupa in Python, or in D:/TF3Mods/lua-validation-deps. This verifies the
Lua behavior with mocked GUI objects; it cannot substitute for an in-game test.
"""
from pathlib import Path
import json
import hashlib
import math
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "lua-validation-deps"))
from lupa.lua54 import LuaRuntime
from build_speed_restrictions import MOD_ID, SPEEDS, STYLES, REVISION

MOD = ROOT / "game_build" / MOD_ID
GAME = Path("D:/SteamLibrary/steamapps/common/Transport Fever 3")
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("_ = function(s) return s end; resolve = function(s) return '" + MOD_ID + "::/gui/' .. s end")
lookup = {}

with zipfile.ZipFile(GAME / "base/content/infrastructure/track.zip") as archive:
    for style in STYLES:
        for electric in (False, True):
            stem = style + ("_catenary" if electric else "")
            ref = f"::/infrastructure/track/{style}/{stem}.street_template"
            lua.execute(archive.read(f"track/{style}/{stem}.street_template.lua").decode())
            lookup[ref] = lua.globals().data()

for path in (MOD / "content").rglob("*.street_template.lua"):
    lua.execute(path.read_text(encoding="utf-8"))
    data = lua.globals().data()
    name = MOD_ID + "::/" + path.relative_to(MOD / "content").as_posix()[:-4]
    lookup[name] = data

lua.globals().trackResources = lua.table_from(lookup)
lua.globals().modOwner = MOD_ID
lua.execute("""
local definitions = {}
for name, track in pairs(trackResources) do
    definitions[#definitions + 1] = {
        resName = name, action = "ACTION_TRACK_BUILDER_UPGRADER",
        params = { { key = "mode", numbers = { 1, 2 } } },
        builderAudioRes = { "stock_audio" },
    }
end
definitions[#definitions + 1] = { resName = "other_mod::/custom_track.street_template", action = "ACTION_TRACK_BUILDER_UPGRADER", params = {} }
definitions[#definitions + 1] = { resName = "stock_road", action = "ACTION_STREET_BUILDER_UPGRADER", params = {} }

originalDefinitions = definitions
construction = {
    getTrackDefinitions = function() return definitions end,
    getActionParams = function(definition, params, ...)
        local forwarded = {...}
        local key = params.mode == 2 and "trackEdgeModifier" or "trackEdgeBuilder"
        return { constructionActionParams = { [key] = {
            resName = definition.resName,
            slope = params.slope, bridgeTypeId = params.bridgeType,
            undergroundMode = params.undergroundMode,
            builderAudioRes = definition.builderAudioRes,
            overrideEdgeDecorations = false,
        } }, forwarded = forwarded }
    end,
}
react = {
    RegisterRecipe = function(name, fn) return fn end,
    setMouseTransparent = function() end,
    setDisableFocusable = function() end,
}
builtin = { BoxLayout = function(params) return params end }
api = {
    type = { ["enum"] = {
        ScriptParamType = { ComboBox = "ComboBox" },
        ScriptParamLocation = { Toolbar = "Toolbar" },
    } },
    res = { streetTemplateRep = { find = function(name)
        return trackResources[name] and 1 or -1
    end } },
}
ug_require = function(name)
    if name == "::/gui/main/react.lua" then return react end
    if name == "::/gui/main/builtin.lua" then return builtin end
    if name == "::/gui/construction/construction_react_util.tl" then return construction end
    error("Unexpected require: " .. name)
end
getOwningModId = function() return modOwner end
debugPrint = function(message) hookMessage = message end
""")

script = (MOD / "content/gui/track_speed_dropdown.script.lua").read_text(encoding="utf-8")

def load_script_entry(source, name):
    # TF3 ignores the chunk return for Lua-backed resources and invokes data().
    # Reset it first: a template's leftover data() must not mask a missing export.
    lua.execute("data = false")
    lua.execute(source)
    if lua.eval("type(data)") != "function":
        raise ValueError("function data() not defined")
    exports = lua.globals().data()
    entry = exports[name]
    assert lua.eval("type")(entry) == "function", f"Missing script entry {name}"
    return entry

entry = load_script_entry(script, "EntryPoint")
assert entry()["children"] is not None
lua.execute("""
visible = construction.getTrackDefinitions()
assert(#visible == 8, "Expected six stock choices and two unrelated choices")
for _, definition in ipairs(visible) do
    local stock = definition.resName:match("^::/infrastructure/track/") ~= nil
    if stock then
        assert(#definition.params == 2)
        local param = definition.params[2]
        assert(param.key == "gj94_track_speed_kmh" and param.uiType == "ComboBox")
        assert(param.defaultIndex == 1 and param.numbers[1] == 0 and param.values[1] == "Default")
        assert(#param.numbers == 10 and #param.values == 10)
        assert(param.stepValueFn(0, 1) == 15)
        assert(param.stepValueFn(160, 1) == 160)
        assert(param.stepValueFn(0, -1) == 0)
    else
        assert(#definition.params == 0, "Unrelated definitions changed")
    end
end
-- Calling the source again must not accumulate controls on cached definitions.
assert(#construction.getTrackDefinitions()[1].params <= 2)
""")

visible = lua.globals().visible
checks = 0
for i in range(1, len(visible) + 1):
    definition = visible[i]
    original_name = definition.resName
    if original_name not in lookup or not original_name.startswith("::/"):
        continue
    for speed in (0, *SPEEDS):
        for mode in (1, 2):
            params = lua.table_from({"gj94_track_speed_kmh": speed, "mode": mode,
                                     "slope": 0.01, "bridgeType": 7, "undergroundMode": 1})
            result = lua.globals().construction.getActionParams(definition, params, "repository", "gamepad", "paramsRef")
            action_key = "trackEdgeModifier" if mode == 2 else "trackEdgeBuilder"
            action = result.constructionActionParams[action_key]
            target = action.resName
            assert target in lookup, target
            if speed:
                assert target.startswith(MOD_ID + "::/track/")
                assert math.isclose(lookup[target].laneConfigs[1].speed * 3.6, speed, abs_tol=1e-10)
                assert ("ELECTRIC_TRAIN" in list(lookup[target].laneConfigs[1].transportModes.values())) == ("_catenary" in original_name)
                assert lookup[target].defaultEdgeDecorations is None, "Boards must use boundary script, not repeating decorations"
            else:
                assert target == original_name, "Default must restore the stock track"
                assert lookup[target].defaultEdgeDecorations is None, "Default must not inherit numbered boards"
            assert action.overrideEdgeDecorations is False, "Trackside decorations must be preserved"
            assert definition.resName == original_name, "Menu selection was mutated"
            assert action.slope == 0.01 and action.bridgeTypeId == 7 and action.undergroundMode == 1
            assert result.forwarded[1] == "repository" and result.forwarded[3] == "paramsRef"
            checks += 1

lua.execute("""
local def = {resName = "::/infrastructure/track/standard/standard.street_template", action = "ACTION_TRACK_BUILDER_UPGRADER", params = {}}
for _, speed in ipairs({-1, 14, 999}) do
    for mode = 1, 2 do
        local result = construction.getActionParams(def, {mode = mode, gj94_track_speed_kmh = speed})
        local action = result.constructionActionParams[mode == 2 and "trackEdgeModifier" or "trackEdgeBuilder"]
        assert(action.resName == def.resName and not action.overrideEdgeDecorations)
    end
end
local variant = modOwner .. "::/track/standard_040.street_template"
local saved = trackResources[variant]
trackResources[variant] = nil
assert(construction.getActionParams(def, {mode = 1, gj94_track_speed_kmh = 40}).constructionActionParams.trackEdgeBuilder.resName == def.resName)
trackResources[variant] = saved

""")
# Reinitializing the plugin must not wrap the functions again.
lua.execute("previousActionWrapper = construction.getActionParams")
load_script_entry(script, "EntryPoint")
assert lua.eval("construction.__gj94_speedDropdownInstalled")
lua.execute("assert(construction.getActionParams == previousActionWrapper); assert(#construction.getTrackDefinitions() == 8)")

# Reproduce revision 2's module-style export: it must fail this loader contract.
old_script = script.replace("function data()\n", "", 1).rstrip().removesuffix("end")
try:
    load_script_entry(old_script, "EntryPoint")
except ValueError as error:
    assert str(error) == "function data() not defined"
else:
    raise AssertionError("The missing-data regression was not detected")

lua.execute("data = false")
lua.execute((MOD / "content/gui/track_speed_dropdown.res.lua").read_text())
registration = lua.globals().data()
assert registration.type == "react-plugin ::ModEntryPointExtension"
assert registration.data.filePath == MOD_ID + "::/gui/track_speed_dropdown.script@EntryPoint"

report = {"result": "PASS", "revision": REVISION, "luaRuntime": lua.lua_version, "buildAndReplaceCases": checks,
          "sourceSha256": hashlib.sha256(script.encode("utf-8")).hexdigest(),
          "checks": ["Lua-backed script data() export and EntryPoint resolution",
                     "revision 2 missing-data startup regression reproduced and rejected",
                     "real Lua execution of all track templates and GUI extension",
                     "six stock menu options plus unrelated tracks preserved",
                     "speed dropdown on stock options only", "Default restores native speeds",
                     "all nine caps in build and replacement modes", "electrification preserved",
                     "unmodified selected menu definition", "native action arguments preserved",
                     "invalid and missing-resource fallbacks", "idempotent extension initialization",
                     "no repeating board decorations on custom or Default tracks",
                     "trackside decorations are preserved during replacement",
                     "native GUI entry-point registration"],
          "inGameDropdownTest": "User confirmed working on 2026-09-30", "revision1InGameTracks": "User confirmed working"}
report_path = ROOT / "game_build/speed_dropdown_validation.json"
report_path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
