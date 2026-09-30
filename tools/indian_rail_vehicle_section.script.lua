-- A default Indian Railways tab in the native rail purchase browser.
-- Native filtering still controls years, depot compatibility and buying.
function data()
local react = ug_require "::/gui/main/react.lua"
local builtin = ug_require "::/gui/main/builtin.lua"
local store = ug_require "::/gui/line_vehicle_mgmt/vehicle_store_util.tl"
local owner = getOwningModId()
local prefix = owner .. "::/vehicle/"
local sectionKey = "gj94IndianRailways"
local sectionValue = 9401

local function isIndianRailway(element)
    local path = element.path or ""
    return path:sub(1, #prefix) == prefix
end

if not store.__gj94IndianRailSection then
    local originalFilter = store.vehicleFilter
    local originalRail = store.handleRailCarrier
    local originalTabs = builtin.TabWidget
    local originalTabChild = builtin.TabWidgetChild
    -- TreeNodeIds are opaque. Remember just the native rail tab identities
    -- while their parent builds its children; weak keys avoid retaining nodes.
    local railTabNodes = setmetatable({}, {__mode = "k"})
    local explicitChoice = nil

    store.vehicleFilter = function(element, params, filter, ...)
        if filter and filter[sectionKey] and not isIndianRailway(element) then
            return false
        end
        return originalFilter(element, params, filter, ...)
    end

    store.handleRailCarrier = function(filter, id2index, index, ...)
        local indian = filter[sectionKey]
        local initial = indian == nil
        if explicitChoice ~= nil then
            indian = explicitChoice
        elseif indian == nil then
            -- The native browser initially selects Locomotive. Start with all
            -- Indian vehicle types instead, on every newly opened browser.
            indian = true
        elseif index == 0 then
            -- The native text-search tab searches the entire rail catalogue.
            indian = false
        end
        if indian and (initial or explicitChoice == true) then
            filter.engines, filter.cargoFilters, filter.text = {}, {}, ""
        end
        local result = originalRail(filter, id2index, indian and -1 or index, ...)
        result[sectionKey] = indian
        return result
    end

    local function choose(callback, value)
        local previous = explicitChoice
        explicitChoice = value == sectionValue
        local ok, result = pcall(callback, value)
        explicitChoice = previous
        if not ok then error(result) end
        return result
    end

    local IndianRailTabs = react.RegisterWrapperRecipe("Gj94IndianRailTabs", originalTabs, function(params)
        local active = react.useState(sectionValue)
        local isGamepad = api.util.getInputMode() == api.type["enum"].InputMode.Gamepad
        local enhanced = {}
        for key, value in pairs(params) do enhanced[key] = value end
        enhanced.tabs = {
            originalTabChild {
                localKey = "gj94-indian-railways",
                value = sectionValue,
                indicator = builtin.TextView {
                    meta = {class = "font-scale-tab-widget-indicator",
                        tooltip = "Indian Railways locomotives, coaches and trainsets",
                        id = "vehiclestore.tab-indian-railways"},
                    text = "Indian Railways",
                },
                item = builtin.Component {},
            },
        }
        for _, tab in ipairs(params.tabs) do enhanced.tabs[#enhanced.tabs + 1] = tab end
        enhanced.initialValue = sectionValue
        enhanced.value = active:old()
        enhanced.onValueChange = function(value)
            active:set(value)
            return choose(params.onValueChange, value)
        end
        react.onMount(function()
            choose(params.onValueChange, sectionValue)
        end)
        -- Clicking the search field activates it through the parent, rather
        -- than through TabWidget.onValueChange. Keep that native path intact.
        react.onStep(function()
            if not isGamepad and params.value == 0 and active:old() ~= 0 then
                active:set(0)
            end
        end)
        return originalTabs(enhanced)
    end)

    builtin.TabWidgetChild = function(...)
        local args = table.pack(...)
        local params = args[args.n]
        local node = originalTabChild(...)
        if type(params) == "table" and
            (params.localKey == "locomotive" or params.localKey == "waggon" or params.localKey == "multiple_unit") then
            railTabNodes[node] = params.localKey
        end
        return node
    end

    builtin.TabWidget = function(...)
        local args = table.pack(...)
        local params = args[args.n]
        if type(params) == "table" and params.tabs then
            local ids = {}
            for _, node in ipairs(params.tabs) do
                local id = railTabNodes[node]
                if id then ids[id] = true end
            end
            if ids.locomotive and ids.waggon and ids.multiple_unit then
                -- Forward original refs/styles so keyboard and controller tab
                -- navigation still target the native TabWidget API.
                return IndianRailTabs(...)
            end
        end
        return originalTabs(...)
    end
    store.__gj94IndianRailSection = true
    debugPrint("[Indian Railways] Default purchase-browser section installed")
end

local EntryPoint = react.RegisterRecipe("Gj94IndianRailSectionEntryPoint", function()
    react.setMouseTransparent(true)
    react.setDisableFocusable(true)
    return builtin.BoxLayout {children = {}}
end)

return {EntryPoint = EntryPoint}
end
