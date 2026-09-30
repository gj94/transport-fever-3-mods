"""Execute the actual entrance-board Lua with a native API fixture.

Graph/edit and facing tests cover section scope. This does not confirm rendering
inside TF3; its native API declarations and registration are checked separately.
"""
from pathlib import Path
import json
import hashlib
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "lua-validation-deps"))
from lupa.lua54 import LuaRuntime
from build_speed_restrictions import MOD_ID, SPEEDS, REVISION

GAME = Path("D:/SteamLibrary/steamapps/common/Transport Fever 3")
MOD = ROOT / "game_build" / MOD_ID
lua = LuaRuntime(unpack_returned_tuples=True)
lua.globals().modOwner = MOD_ID
lua.execute("""
edges, entities, models, commands = {}, {}, {}, {}
nextEntity, graphCalls, componentCalls = 1000, 0, 0
messages = {}
for _, speed in ipairs({15,25,40,60,80,100,120,130,160}) do
    models[modOwner .. "::/boards/speed_" .. string.format("%03d", speed) .. ".mdl"] = speed
end
api = {
    type = {
        ["enum"] = {RoadType={TRACK="TRACK",STREET="STREET"}, BaseEdgeType={NORMAL="NORMAL",BRIDGE="BRIDGE",TUNNEL="TUNNEL"}},
        ComponentType = {BASE_EDGE="BASE_EDGE"},
        Vec2f = {new=function(x,y) return {x=x,y=y} end},
        Vec4f = {new=function(x,y,z,w) return {x,y,z,w} end},
        Mat4f = {new=function(a,b,c,d)
            local result={}; for _, col in ipairs({a,b,c,d}) do
                for _, value in ipairs(col) do result[#result+1]=value end
            end; return result
        end},
    },
    res = {modelRep = {find=function(name) return models[name] or -1 end}},
    engine = {
        getEntitiesWithComponent=function()
            error("Cannot loop over this component type")
        end,
        system = {streetSystem = {getNode2TrackEdgeMap=function()
            graphCalls=graphCalls+1
            local result={}
            for id, edge in pairs(edges) do
                if edge.roadType=="TRACK" then
                    for _,node in ipairs({edge.node0,edge.node1}) do
                        result[node]=result[node] or {}; result[node][#result[node]+1]=id
                    end
                end
            end
            return result
        end}},
        getComponent=function(id,kind) assert(kind=="BASE_EDGE"); componentCalls=componentCalls+1; return edges[id] end,
        entityExists=function(id) return entities[id]~=nil or edges[id]~=nil end,
        terrain={getHeightAt=function() return 0 end},
    },
    cmd = {
        makeCustomEntityCreateCmd=function(modelId) return {kind="create",modelId=modelId} end,
        makeCustomEntityDestroyCmd=function(entity) return {kind="destroy",entity=entity} end,
        makeCustomEntityUpdateTransformationCmd=function(entity,transf) return {kind="transform",entity=entity,transf=transf} end,
    },
}
api.cmd.sendCommand=function(command,callback)
    commands[#commands+1]=command
    local result={}
    if command.kind=="create" then
        nextEntity=nextEntity+1; entities[nextEntity]={speed=command.modelId}; result.resultEntity=nextEntity
    elseif command.kind=="destroy" then
        assert(entities[command.entity],"Attempted to destroy a non-board entity")
        entities[command.entity]=nil
    elseif command.kind=="transform" then
        assert(entities[command.entity]); entities[command.entity].transf=command.transf
    else error("Unexpected world mutation") end
    if callback then callback(result,true) end
end
getOwningModId=function() return modOwner end
debugPrint=function(message) lastMessage=message; messages[#messages+1]=message end
state={value={},subscriptions={}}
function state:get() return self.value end
function state:set(value) self.value=value end
function state:hasEventSubscriptions() return next(self.subscriptions)~=nil end
function state:subscribeToEvent(name) self.subscriptions[name]=true end

function addEdge(id,node0,node1,x0,y0,x1,y1,speed,style,kind)
    local name="::/infrastructure/track/standard/standard.street_template"
    if speed then name=modOwner.."::/track/"..(style or "standard").."_"..string.format("%03d",speed)..".street_template" end
    local length=math.sqrt((x1-x0)^2+(y1-y0)^2)
    edges[id]={roadType="TRACK",roadTemplate=name,type=kind or "NORMAL",node0=node0,node1=node1,
        position0={x=x0,y=y0,z=0},position1={x=x1,y=y1,z=0},
        tangent0={x=x1-x0,y=y1-y0,z=0},tangent1={x=x1-x0,y=y1-y0,z=0},
        distance=length,edgeDecorations={{"noise_barrier",false}},objects={{777,"SIGNAL"}}}
end
function reset()
    edges,entities,commands={},{},{}; state.value={dirty=true}
end
function tick(dt)
    local desired=script.update({},state,dt or 0)
    script.postUpdate({},state,dt or 0,desired)
end
function edit()
    script.handleEvent({},state,"builder","apply","builder.proposalApply",{})
    tick()
end
function countBoards()
    local n=0; for _ in pairs(entities) do n=n+1 end; return n
end
function board(key)
    local saved=assert(state.value.boards[key],"Missing board "..key)
    return assert(entities[saved.entity])
end
function assertFacing(key,normalX,normalY)
    local b=board(key); local t=b.transf
    assert(math.abs(t[1]-normalX)<1e-6 and math.abs(t[2]-normalY)<1e-6,"Numbered front faces the wrong direction")
    -- Incoming approach position is along +normal. Departing approach is -normal
    -- and must therefore see the blank -X face verified by mesh UV validation.
    assert(t[1]*normalX+t[2]*normalY>0.999)
end
""")

source = (MOD / "content/boards/boundaries.script.lua").read_text(encoding="utf-8")
def load():
    lua.execute("data=false")
    lua.execute(source)
    assert lua.eval("type(data)") == "function"
    script = lua.globals().data()
    for entry in ("update", "postUpdate", "handleEvent"):
        assert lua.eval("type")(script[entry]) == "function"
    lua.globals().script = script
load()

checks = []
def check(name, code):
    lua.execute(code)
    checks.append(name)

legacy_path = ROOT / "game_build/speed_board_runtime_failure/boundaries_revision4.script.lua"
if legacy_path.exists():
    # Replay the actual deployed script that failed in Modtest2, rather than a
    # permissive mock that assumes every declared component can be enumerated.
    lua.execute(legacy_path.read_text(encoding="utf-8"))
    lua.globals().legacyScript = lua.globals().data()
    check("Revision 4 reproduces the observed BASE_EDGE enumeration failure", """
reset(); addEdge(1,1,2,0,0,100,0,80)
assert(legacyScript.update({},state,0)==nil and countBoards()==0)
assert(lastMessage:find("Cannot loop over this component type",1,true))
""")
    load()
check("Native BASE_EDGE enumeration is rejected by the runtime fixture", """
local ok,error=pcall(api.engine.getEntitiesWithComponent,"BASE_EDGE")
assert(not ok and tostring(error):find("Cannot loop over this component type",1,true))
""")
check("Default track produces no boards", "reset(); addEdge(1,1,2,0,0,100,0); tick(); assert(countBoards()==0)")
check("Same-cap segments join across track style and electrification", """
reset()
addEdge(1,1,2,0,0,100,0)
addEdge(2,2,3,100,0,200,0,80)
addEdge(3,3,4,200,0,300,0,80,"high_speed")
edges[3].roadTemplate=modOwner.."::/track/high_speed_080_catenary.street_template"
addEdge(4,4,5,300,0,400,0)
tick(); assert(countBoards()==2)
assert(state.value.boards["2:0"] and state.value.boards["3:1"])
assert(not state.value.boards["2:1"] and not state.value.boards["3:0"])
assert(not state.value.boards["1:0"] and not state.value.boards["4:0"])
""")
check("Native graph edge IDs are deduplicated across their two nodes", """
state.value.dirty=true; local before=componentCalls; tick()
assert(componentCalls-before==4)
""")
check("Both entrance numbers face outward; boards remain inside capped edges", """
assertFacing("2:0",-1,0); assertFacing("3:1",1,0)
assert(board("2:0").transf[13]>100 and board("2:0").transf[13]<102)
assert(board("3:1").transf[13]<300 and board("3:1").transf[13]>298)
assert(board("2:0").transf[14]<0 and board("3:1").transf[14]>0)
""")
check("Idle updates do not duplicate or move unchanged boards", """
local n=#commands; tick(2); assert(#commands==n and countBoards()==2)
""")
load()
check("Saved board state survives script reload without duplicates", """
local n=#commands; tick(); assert(countBoards()==2 and #commands==n)
""")
before_graph = lua.globals().graphCalls
for _ in range(16):
    load()
    lua.globals().tick(0)
assert lua.globals().graphCalls == before_graph
checks.append("Sixteen fresh simulation Lua contexts share persistent scan throttling")
check("Extending a section removes its old exit board", """
edges[4].roadTemplate=modOwner.."::/track/standard_080.street_template"
edit(); assert(countBoards()==2 and not state.value.boards["3:1"])
assertFacing("4:1",1,0)
""")
check("Adjoining 80 and 40 sections show the number being entered", """
reset(); addEdge(1,1,2,0,0,100,0)
addEdge(2,2,3,100,0,200,0,80); addEdge(3,3,4,200,0,300,0,40)
addEdge(4,4,5,300,0,400,0); edit(); assert(countBoards()==4)
assert(board("2:1").speed==80 and board("3:0").speed==40)
assertFacing("2:1",1,0); assertFacing("3:0",-1,0)
""")
check("Default restoration removes the old 80 boards and preserves the 40 section", """
edges[2].roadTemplate=edges[1].roadTemplate; edit(); assert(countBoards()==2)
for _,b in pairs(entities) do assert(b.speed==40) end
assert(edges[2].edgeDecorations[1][1]=="noise_barrier" and edges[2].objects[1][1]==777)
""")
check("Bulldozing capped track removes orphaned boards", """
edges[3]=nil; edit(); assert(countBoards()==0)
""")
check("Splitting a capped section creates independent entrances", """
reset(); addEdge(1,1,2,0,0,100,0,80); addEdge(2,2,3,100,0,200,0)
addEdge(3,3,4,200,0,300,0,80); edit(); assert(countBoards()==4)
""")
check("Junction branches and disconnected parallel tracks keep section scope", """
reset(); addEdge(1,1,2,0,0,100,0,80); addEdge(2,2,3,100,0,200,100,80)
addEdge(3,2,4,100,0,200,0); addEdge(4,11,12,0,5,200,5)
edit(); assert(countBoards()==4)
for key in pairs(state.value.boards) do assert(key:sub(1,1)=="1" or key:sub(1,1)=="2") end
""")
check("A same-cap closed loop has no artificial section entrances", """
reset(); addEdge(1,1,2,0,0,100,0,80); addEdge(2,2,3,100,0,50,100,80)
addEdge(3,3,1,50,100,0,0,80); edit(); assert(countBoards()==0)
""")
check("Very short sections keep both boards within the capped segment", """
reset(); addEdge(1,1,2,0,0,2,0,25); edit(); assert(countBoards()==2)
assert(board("1:0").transf[13]>0 and board("1:1").transf[13]<2)
assertFacing("1:0",-1,0); assertFacing("1:1",1,0)
""")
check("Curved approaches use local spline tangent for outward facing", """
reset(); addEdge(1,1,2,0,0,100,100,60)
edges[1].tangent0={x=150,y=0,z=0}; edges[1].tangent1={x=0,y=150,z=0}
edit(); assert(countBoards()==2)
assert(board("1:0").transf[1]<-0.9 and board("1:1").transf[2]>0.9)
""")
check("Tunnel interiors are omitted and bridge height uses the track spline", """
reset(); addEdge(1,1,2,0,0,100,0,80,nil,"TUNNEL"); edit(); assert(countBoards()==0)
edges[1].type="BRIDGE"; edges[1].position0.z=10; edges[1].position1.z=10
edit(); assert(countBoards()==2 and math.abs(board("1:0").transf[15]-10)<1e-6)
""")
check("Deleted board entities are recreated from section boundaries", """
entities[state.value.boards["1:0"].entity]=nil; tick(2); assert(countBoards()==2)
""")
check("Failed scans preserve existing boards and recover", """
local original=api.engine.getComponent; api.engine.getComponent=function() error("fixture unavailable") end
local n=#commands; edit(); assert(#commands==n and countBoards()==2)
local count=#messages; tick(2); assert(#messages==count,"The same scan error was logged repeatedly")
api.engine.getComponent=original; edit(); assert(countBoards()==2)
""")
for speed in SPEEDS:
    check(f"Both entrances select the {speed} km/h model", f"""
reset(); addEdge(1,1,2,0,0,100,0,{speed}); edit(); assert(countBoards()==2)
for _,b in pairs(entities) do assert(b.speed=={speed}) end
""")
check("Missing model resources fail safely and retry", """
reset(); addEdge(1,1,2,0,0,100,0,80)
local name=modOwner.."::/boards/speed_080.mdl"; local model=models[name]; models[name]=nil
edit(); assert(countBoards()==0)
models[name]=model; tick(2); assert(countBoards()==2)
""")
check("Another mod's speed-named track is untouched", """
reset(); addEdge(1,1,2,0,0,100,0,80)
edges[1].roadTemplate="other_mod::/track/standard_080.street_template"
edit(); assert(countBoards()==0)
""")

lua.execute((MOD / "content/boards/boundaries.gs.lua").read_text())
registration = lua.globals().data()
for field, entry in (("updateScript","update"),("postUpdateScript","postUpdate"),("handleEventScript","handleEvent")):
    assert registration[field].fileName == "boundaries.script@" + entry
with zipfile.ZipFile(GAME / "base/content/game_mechanics.zip") as archive:
    stock_util = archive.read("game_mechanics/fun_elements/custom_entity_util.tl").decode()
    stock_gs = archive.read("game_mechanics/fun_elements/fun_elements.gs.lua").decode()
    for field in ("updateScript", "postUpdateScript", "handleEventScript"):
        assert field in stock_gs
    for api_name in ("makeCustomEntityCreateCmd", "makeCustomEntityDestroyCmd", "makeCustomEntityUpdateTransformationCmd"):
        assert api_name in stock_util
engine_defs = (GAME / "api/tealdef/api/engine.d.tl").read_text()
system_defs = (GAME / "api/tealdef/api/engine/system.d.tl").read_text()
assert "getNode2TrackEdgeMap : function()" in system_defs and "streetSystem : StreetSystem" in system_defs
assert "api.engine.getEntitiesWithComponent(" not in source
for field in ("roadTemplate", "roadType", "position0", "position1", "tangent0", "tangent1", "distance"):
    assert field in engine_defs
checks.append("Native .gs registration, BaseEdge fields and custom-entity command contract")
report = {"result": "PASS", "revision": REVISION, "luaRuntime": lua.lua_version, "scenarioCount": len(checks),
          "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
          "checks": checks,
          "inGameBoardTest": "Revision 5 rendering and section updates user-confirmed on 2026-09-30; see TRACK-SPEED-RESTRICTIONS.md for scope"}
(ROOT / "game_build/speed_boundary_validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
