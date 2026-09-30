"""Exercise the GUI extension against the shipped rail filter and tab recipe."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "lua-validation-deps"))
from lupa.lua54 import LuaRuntime
from pack_settings import REVISION

GAME = Path("D:/SteamLibrary/steamapps/common/Transport Fever 3")
MOD = ROOT / "game_build/gj94_indian_rail_pack"
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
store, builtin, react = {}, {}, {}
table_util = {arrayContains=function(a,v) for _,x in ipairs(a) do if x==v then return true end end return false end}
lang_util = {stringContains=function(a,b) return a:lower():find(b:lower(),1,true)~=nil end}
store.depotMatchesVehicleFilterTags=function(vehicle,depot)
    for _,tag in ipairs(depot) do if not table_util.arrayContains(vehicle,tag) then return false end end
    return true
end
store.depotMatchesVehicleTransportModes=function(vehicle,depot)
    for mode in pairs(depot) do if vehicle[mode] then return true end end
    return false
end
api = {util={getInputMode=function() return inputMode end},type={enum={InputMode={Gamepad=1},VehicleEngineType={STEAM=1,DIESEL=2,ELECTRIC=3}}}}
inputMode=0
getOwningModId=function() return "gj94_indian_rail_pack" end
debugPrint=function(text) lastMessage=text end
ug_require=function(path)
    if path:find("react.lua",1,true) then return react end
    if path:find("builtin.lua",1,true) then return builtin end
    if path:find("vehicle_store_util",1,true) then return store end
    error(path)
end
nodeData=setmetatable({}, {__mode="k"})
local function node(kind,params)
    local result=setmetatable({}, {__index=function() error("TreeNodeId is opaque") end})
    nodeData[result]={kind=kind,params=params}; return result
end
for _,kind in ipairs({"TabWidgetChild","TabWidget","TextView","Component","BoxLayout","ImageView","ToggleButton"}) do
    builtin[kind]=function(...)
        local args=table.pack(...); return node(kind,args[args.n])
    end
end
builtin.type={Orientation={Horizontal=1},TabOrientation={North=1},ImageViewScaling={AutoFit=1}}
react.RegisterRecipe=function(name,fn) return function(params) return node(name,{fn=fn,params=params}) end end
react.RegisterWrapperRecipe=function(name,wrapped,fn)
    return function(...)
        local args=table.pack(...); enhancedCall={name=name,wrapped=wrapped,args=args,fn=fn}
        return node(name,args[args.n])
    end
end
react.useState=function(initial)
    ctx.hook=ctx.hook+1
    local state=ctx.states[ctx.hook]
    if not state then
        state={value=initial,old=function(s) return s.value end,set=function(s,v) s.value=v end}
        ctx.states[ctx.hook]=state
    end
    return state
end
react.useMirrorState=function(ref) return {old=function() return ref:get() end} end
react.useNodeRef=function() return {} end
react.ref=function(ref) return {is_react_ref_info=true,data=ref} end
react.onMount=function(fn) ctx.mounts[#ctx.mounts+1]=fn end
react.onStep=function(fn) ctx.steps[#ctx.steps+1]=fn end
react.useInputAction=function() end
react.iaForward=function() return {} end
react.setMouseTransparent=function() end
react.setDisableFocusable=function() end
engine_react_util={useStepState=function(fn) return react.useState(fn()) end}
isGamepadInputMode=function() return inputMode==1 end
gui_react_util={makeHorizontalSpacer=function() return node("Spacer",{}) end}
VehicleSearch=function(param) searchParam=param; return node("Search",param) end
_=function(s) return s end
function newCtx() return {states={},hook=0,mounts={},steps={}} end
function invoke(context,fn,param)
    ctx=context; ctx.hook=0; ctx.mounts={}; ctx.steps={}; return fn(param)
end
''')


def untype(code):
    # Only remove declarations from these three shipped, pure Teal functions;
    # their executable bodies are retained, rather than reimplemented as mocks.
    code = code.replace("<const>", "")
    code = re.sub(r"\s+as\s+(?:ReactStateT<[^>]+>|[\w.]+)", "", code)
    code = re.sub(r"\s*:\s+(?:\{[^{}]*\}|ReactStateT<[^>]+>|[\w.]+)", "", code)
    return code


with zipfile.ZipFile(GAME / "base/content/gui.zip") as archive:
    native_util = archive.read("gui/line_vehicle_mgmt/vehicle_store_util.tl").decode()
    native_window = archive.read("gui/line_vehicle_mgmt/vehicle_store_window.tl").decode()
    for start, end in (("vehicle_store_util.vehicleFilter = function", "vehicle_store_util.makeVehicleData = function"),
                       ("vehicle_store_util.showCargoFilters = function", "vehicle_store_util.handleTramCarrier = function")):
        code = native_util[native_util.index(start):native_util.index(end)]
        lua.execute(untype(code.replace("vehicle_store_util", "store")))
    topbar = native_window[native_window.index('local TopBar = react.RegisterRecipe("TopBar", function'):
                           native_window.index("local record MidBarParam")]
    topbar = topbar.replace('local TopBar = react.RegisterRecipe("TopBar", function', "nativeTopBar = function")
    topbar = topbar.rstrip().removesuffix("end)") + "end"
    lua.execute(untype(topbar))

source = (MOD / "content/gui/indian_rail_vehicle_section.script.lua").read_text(encoding="utf-8")
lua.execute(source)
extension = lua.globals().data()
assert extension.EntryPoint is not None
lua.execute(r'''
id2index={locomotive=1,waggon=2,multiple_unit=3}
function freshFilter()
    return {carrier=1,transportModes={TRAIN=true},filterTags={"default"},text="",cargoFilters={},engines={}}
end
function railTabs(gamepad)
    inputMode=gamepad and 1 or 0
    rootCtx,enhancedCtx=newCtx(),newCtx()
    currentFilter=store.handleRailCarrier(freshFilter(),id2index,1)
    topbarParams={
        layoutStyleRef={get=function() return "TwoPaneSplit" end},
        tabConfig={{text="Locomotive",id="locomotive"},{text="Wagon",id="waggon"},{text="Multiple Unit",id="multiple_unit"}},
        filter=currentFilter,sort={},setFilterSort=function() end,
        onTabChanged=function(index)
            currentFilter=store.handleRailCarrier(currentFilter,id2index,gamepad and index+1 or index)
        end,
    }
    frame()
    for _,fn in ipairs(rootCtx.mounts) do fn() end
    for _,fn in ipairs(enhancedCtx.mounts) do fn() end
    frame()
end
function frame()
    invoke(rootCtx,nativeTopBar,topbarParams)
    local call=enhancedCall
    local tabNode=invoke(enhancedCtx,call.fn,call.args[call.args.n])
    widget=nodeData[tabNode].params
end
function selectTab(value) widget.onValueChange(value); frame() end
function element(path,engine,capacity,year,mu)
    return {path=path,name="Example",multipleUnit=mu or false,filterTags={"default"},
        carriersMap={[1]=true},transportModes={TRAIN=true,ELECTRIC_TRAIN=true},engineTypes=engine and {[3]=true} or {},
        hasEngine=engine,vehicleData={yearFrom=year or 1980,yearTo=0,totalCapacity=capacity,allCargoTypes={}}}
end
params={year=2026,anyCargoFilterSet=false}
indian="gj94_indian_rail_pack::/vehicle/"
loco=element(indian.."train/wap7/wap7.mdl",true,0)
coach=element(indian.."train/lhb_3a/lhb_3a.mdl",false,22)
set=element(indian.."train/vande_bharat/vande_bharat_8.mu",true,420,2019,true)
stock=element("::/vehicle/train/br185/br185.mdl",true,0)
''')

checks = []


def check(name, code):
    lua.execute(code)
    checks.append(name)


check("Default section contains engines, coaches and multiple-unit trainsets", '''
railTabs(false)
assert(widget.value==9401 and widget.initialValue==9401 and #widget.tabs==5)
assert(store.vehicleFilter(loco,params,currentFilter))
assert(store.vehicleFilter(coach,params,currentFilter))
assert(store.vehicleFilter(set,params,currentFilter))
assert(not store.vehicleFilter(stock,params,currentFilter))
assert(currentFilter.withEngine==nil and currentFilter.withCapacity==nil)
''')
check("Native locomotive/wagon/MU tabs keep their stock behavior", '''
selectTab(1); assert(not currentFilter.gj94IndianRailways and currentFilter.withEngine)
assert(store.vehicleFilter(stock,params,currentFilter) and not store.vehicleFilter(coach,params,currentFilter))
selectTab(2); assert(currentFilter.withEngine==false and store.vehicleFilter(coach,params,currentFilter))
assert(not store.vehicleFilter(loco,params,currentFilter))
selectTab(3); assert(currentFilter.withEngine and currentFilter.withCapacity)
assert(store.vehicleFilter(set,params,currentFilter) and not store.vehicleFilter(loco,params,currentFilter))
''')
check("Returning to Indian Railways clears stale type, engine and search filters", '''
currentFilter.text="BR 185"; currentFilter.engines={[1]=true}; currentFilter.cargoFilters={[9]=true}
selectTab(9401)
assert(currentFilter.text=="" and next(currentFilter.engines)==nil and next(currentFilter.cargoFilters)==nil)
assert(store.vehicleFilter(loco,params,currentFilter) and store.vehicleFilter(coach,params,currentFilter))
''')
check("Closing and reopening defaults to Indian Railways again", '''
selectTab(2); railTabs(false); assert(widget.value==9401 and currentFilter.gj94IndianRailways)
''')
check("Controller defaults and stock tab indices remain correct", '''
railTabs(true); assert(widget.value==9401 and #widget.tabs==4)
selectTab(0); assert(widget.value==0 and currentFilter.withEngine and not currentFilter.gj94IndianRailways)
selectTab(1); assert(currentFilter.withEngine==false and store.vehicleFilter(coach,params,currentFilter))
selectTab(2); assert(currentFilter.withEngine and currentFilter.withCapacity)
selectTab(9401); assert(store.vehicleFilter(coach,params,currentFilter) and store.vehicleFilter(set,params,currentFilter))
''')
check("The native search field still searches the entire catalogue", '''
railTabs(false); searchParam.setSearchActive(); frame()
for _,fn in ipairs(enhancedCtx.steps) do fn() end
frame(); assert(widget.value==0 and not currentFilter.gj94IndianRailways)
assert(store.vehicleFilter(stock,params,currentFilter))
''')
check("Native availability and depot restrictions still apply", '''
railTabs(false)
params.year=1900; assert(not store.vehicleFilter(set,params,currentFilter)); params.year=2026
currentFilter.filterTags={"unmatched-depot"}; assert(not store.vehicleFilter(loco,params,currentFilter))
currentFilter.filterTags={"default"}; currentFilter.transportModes={TRAM=true}
assert(not store.vehicleFilter(loco,params,currentFilter)); currentFilter.transportModes={TRAIN=true}
currentFilter.vehicleFilter={enabledVehicles={},disabledVehicles={loco.path}}
assert(not store.vehicleFilter(loco,params,currentFilter))
''')
check("Unrelated and tram tab widgets are forwarded unchanged", '''
local c=builtin.TabWidgetChild{localKey="waggon",value=1}
local p={tabs={c},value=1}; local marker={}
local result=builtin.TabWidget(react.ref(marker),p)
assert(nodeData[result].kind=="TabWidget" and nodeData[result].params==p)
''')
check("Reinitialization does not install duplicate wrappers", '''
local oldRail,oldTabs,oldChild=store.handleRailCarrier,builtin.TabWidget,builtin.TabWidgetChild
data(); assert(store.handleRailCarrier==oldRail and builtin.TabWidget==oldTabs and builtin.TabWidgetChild==oldChild)
''')
check("Opaque native nodes and original tab refs are preserved", '''
railTabs(false)
assert(enhancedCall.args.n==2 and enhancedCall.args[1].is_react_ref_info)
for i=2,#widget.tabs do assert(nodeData[widget.tabs[i]]~=nil) end
''')

lua.globals().resolve = lambda name: "gj94_indian_rail_pack::/gui/" + name
lua.execute((MOD / "content/gui/indian_rail_vehicle_section.res.lua").read_text())
registration = lua.globals().data()
assert registration.type == "react-plugin ::ModEntryPointExtension"
assert registration.data.filePath == "gj94_indian_rail_pack::/gui/indian_rail_vehicle_section.script@EntryPoint"
report = {"result": "PASS", "revision": REVISION, "scenarioCount": len(checks), "checks": checks,
          "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
          "nativeSources": ["vehicleFilter", "handleRailCarrier", "showCargoFilters", "TopBar"],
          "runtimePlayTest": "Revision 12 purchase-tab appearance user-confirmed on 2026-09-30; see TF3-INSTALL.md for scope"}
(ROOT / "game_build/vehicle_browser_validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
