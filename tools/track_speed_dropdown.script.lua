-- Attach a speed selector to the six stock track definitions. Existing speed
-- variant resources stay registered for save compatibility but leave the menu.
-- Lua-backed script resources export their entry points through data().
function data()
local react = ug_require "::/gui/main/react.lua"
local builtin = ug_require "::/gui/main/builtin.lua"
local construction = ug_require "::/gui/construction/construction_react_util.tl"

local owner = getOwningModId()
local variantPrefix = owner .. "::/track/"
local paramKey = "gj94_track_speed_kmh"
local speeds = { 0, 15, 25, 40, 60, 80, 100, 120, 130, 160 }
local stockTracks = {}
for _, style in ipairs({ "simple", "standard", "high_speed" }) do
    for _, suffix in ipairs({ "", "_catenary" }) do
        local name = "::/infrastructure/track/" .. style .. "/" .. style .. suffix .. ".street_template"
        stockTracks[name] = { style = style, suffix = suffix }
    end
end

local function makeSpeedParam()
    local labels = { "Default" }
    for i = 2, #speeds do
        labels[i] = tostring(speeds[i]) .. " km/h"
    end
    return {
        key = paramKey,
        name = "Speed limit",
        tooltip = "Cap the selected track section. Entrance boards face approaching trains at its boundaries. Default restores the normal speed and removes custom-speed boards. Curves and bridges may impose lower limits.",
        values = labels,
        numbers = speeds,
        defaultIndex = 1,
        uiType = api.type["enum"].ScriptParamType.ComboBox,
        location = api.type["enum"].ScriptParamLocation.Toolbar,
        group = "gj94_track_speed",
        id = "gj94.trackBuilder.speedLimit",
        yearFrom = 0,
        yearTo = 0,
        resetOnDefinitionChange = false,
        resetOnCategoryChange = true,
        resetOnMenuClose = false,
        stepValueFn = function(value, direction)
            local index = 1
            for i, speed in ipairs(speeds) do
                if speed == value then index = i; break end
            end
            return speeds[math.max(1, math.min(#speeds, index + direction))]
        end,
    }
end

local function getVariant(definition, params)
    if not definition or definition.action ~= "ACTION_TRACK_BUILDER_UPGRADER" then
        return nil
    end
    local stock = stockTracks[definition.resName]
    local speed = params and params[paramKey] or 0
    if not stock or speed == 0 then return nil end
    local allowed = false
    for i = 2, #speeds do
        if speed == speeds[i] then allowed = true; break end
    end
    if not allowed then return nil end
    local variant = variantPrefix .. stock.style .. "_" .. string.format("%03d", speed)
        .. stock.suffix .. ".street_template"
    -- If resources are unavailable, delegate to the unmodified stock action.
    if api.res.streetTemplateRep.find(variant) < 0 then return nil end
    return variant
end

-- Wrap exported functions rather than copying or replacing the base GUI script.
-- The base action still handles mode, slope, bridges, signals and decorations.
if not construction.__gj94_speedDropdownInstalled then
    local originalDefinitions = construction.getTrackDefinitions
    local originalActionParams = construction.getActionParams

    construction.getTrackDefinitions = function(...)
        local result = {}
        for _, definition in ipairs(originalDefinitions(...)) do
            if definition.resName:sub(1, #variantPrefix) ~= variantPrefix then
                if stockTracks[definition.resName] then
                    local hasParam = false
                    definition.params = definition.params or {}
                    for _, param in ipairs(definition.params) do
                        if param.key == paramKey then hasParam = true; break end
                    end
                    if not hasParam then
                        table.insert(definition.params, 2, makeSpeedParam())
                    end
                end
                result[#result + 1] = definition
            end
        end
        return result
    end

    construction.getActionParams = function(definition, params, ...)
        local variant = getVariant(definition, params)
        local selected = definition
        if variant then
            -- Do not mutate the menu's selected definition or shared stock data.
            selected = {}
            for key, value in pairs(definition) do selected[key] = value end
            selected.resName = variant
        end
        local result = originalActionParams(selected, params, ...)
        return result
    end
    construction.__gj94_speedDropdownInstalled = true
    debugPrint("[Track Speed Restrictions] Speed limit dropdown installed on stock tracks")
end

local EntryPoint = react.RegisterRecipe("Gj94TrackSpeedDropdown", function()
    react.setMouseTransparent(true)
    react.setDisableFocusable(true)
    return builtin.BoxLayout { children = {} }
end)

return { EntryPoint = EntryPoint }
end
