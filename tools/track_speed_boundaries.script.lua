-- Passive entrance boards: +X is numbered and must face OUT of the section.
-- Only visual custom entities are changed. Track edges, decorations and signals
-- are never changed by this script.
function data()
local owner = getOwningModId()
local prefix = owner .. "::/track/"
local allowed = { [15]=true, [25]=true, [40]=true, [60]=true, [80]=true,
    [100]=true, [120]=true, [130]=true, [160]=true }
local enums = api.type["enum"]

local function message(text)
    if debugPrint then debugPrint("[Track Speed Restrictions] " .. text) end
end

local function cap(edge)
    local name = edge.roadTemplate or ""
    if name:sub(1, #prefix) ~= prefix then return nil end
    local speed = tonumber(name:sub(#prefix + 1):match("^[a-z_]+_(%d+)"))
    return allowed[speed] and speed or nil
end

local function keys(tableValue)
    local result = {}
    for key in pairs(tableValue) do result[#result+1] = key end
    table.sort(result)
    return result
end

local function positionAndTangent(edge, t)
    local h00, h10 = 2*t^3-3*t^2+1, t^3-2*t^2+t
    local h01, h11 = -2*t^3+3*t^2, t^3-t^2
    local d00, d10 = 6*t^2-6*t, 3*t^2-4*t+1
    local d01, d11 = -6*t^2+6*t, 3*t^2-2*t
    local position, tangent = {}, {}
    for _, axis in ipairs({"x","y","z"}) do
        local a, b, ta, tb = edge.position0[axis], edge.position1[axis], edge.tangent0[axis], edge.tangent1[axis]
        position[axis] = h00*a+h10*ta+h01*b+h11*tb
        tangent[axis] = d00*a+d10*ta+d01*b+d11*tb
    end
    return position, tangent
end

local function placement(edge, endIndex)
    -- Place the board slightly INSIDE the capped edge, keeping its number
    -- toward incoming trains. Small edges use a proportionally smaller inset.
    local inset = math.min(0.20, 1.2 / math.max(edge.distance or 1, 1))
    local p, tangent = positionAndTangent(edge, endIndex == 0 and inset or 1-inset)
    local length = math.sqrt(tangent.x^2 + tangent.y^2)
    if length < 1e-6 then return nil end
    local sign = endIndex == 0 and -1 or 1
    local x, y = sign*tangent.x/length, sign*tangent.y/length
    -- Local +Y is on the incoming train's right. Leave clearance from trains.
    local side = 2.8
    local px, py = p.x-y*side, p.y+x*side
    local z = p.z
    if edge.type == enums.BaseEdgeType.NORMAL then
        z = api.engine.terrain.getHeightAt(api.type.Vec2f.new(px, py))
    end
    return {x,y,0,0, -y,x,0,0, 0,0,1,0, px,py,z,1}
end

local function collect()
    -- BASE_EDGE cannot be enumerated with getEntitiesWithComponent in TF3.
    -- The native track graph supplies the exact edge IDs, including all nodes.
    local adjacency = api.engine.system.streetSystem.getNode2TrackEdgeMap()
    local edges, edgeIds, trackCount, cappedCount = {}, {}, 0, 0
    for _, incident in pairs(adjacency) do
        for _, entity in ipairs(incident) do edgeIds[entity] = true end
    end
    for _, entity in ipairs(keys(edgeIds)) do
        local edge = api.engine.getComponent(entity, api.type.ComponentType.BASE_EDGE)
        if edge then
            edges[entity] = edge
            trackCount = trackCount + 1
            if cap(edge) then cappedCount = cappedCount + 1 end
        end
    end
    local desired = {}
    for _, entity in ipairs(keys(edges)) do
        local edge = edges[entity]
        local speed = cap(edge)
        if speed and edge.type ~= enums.BaseEdgeType.TUNNEL then
            for endIndex = 0, 1 do
                local node = endIndex == 0 and edge.node0 or edge.node1
                local hasNeighbour, isBoundary = false, false
                for _, neighbour in ipairs(adjacency[node] or {}) do
                    if neighbour ~= entity and edges[neighbour] then
                        hasNeighbour = true
                        if cap(edges[neighbour]) ~= speed then isBoundary = true end
                    end
                end
                if not hasNeighbour or isBoundary then
                    local transform = placement(edge, endIndex)
                    if transform then
                        desired[tostring(entity) .. ":" .. tostring(endIndex)] = {
                            speed = speed, transf = transform,
                        }
                    end
                end
            end
        end
    end
    return {boards = desired, trackCount = trackCount, cappedCount = cappedCount}
end

local function matrix(values)
    local v = api.type.Vec4f.new
    return api.type.Mat4f.new(v(values[1],values[2],values[3],values[4]),
        v(values[5],values[6],values[7],values[8]), v(values[9],values[10],values[11],values[12]),
        v(values[13],values[14],values[15],values[16]))
end

local function sameTransform(a, b)
    if not a or not b then return false end
    for i = 1, 16 do
        if math.abs(a[i]-b[i]) > 1e-4 then return false end
    end
    return true
end

return {
    update = function(_userParams, state, dt)
        if not state:hasEventSubscriptions() then
            state:subscribeToEvent("builder.proposalApply")
        end
        local saved = state:get() or {}
        saved.boards = saved.boards or {}
        saved.elapsed = (saved.elapsed or 0) + math.max(dt or 0, 0)
        -- Script resources run in multiple simulation Lua contexts. Persist
        -- scan and error flags in game state, rather than per-context locals.
        local refresh = not saved.scanAttempted or saved.dirty or saved.elapsed >= 2.0
        state:set(saved)
        if not refresh then return nil end
        local ok, desired = pcall(collect)
        saved.scanAttempted, saved.dirty, saved.elapsed = true, false, 0
        if not ok then
            local error = tostring(desired)
            if saved.lastError ~= error then message("Entrance-board scan failed: " .. error) end
            saved.lastError = error
            state:set(saved)
            return nil
        end
        saved.lastError = nil
        state:set(saved)
        return desired
    end,

    postUpdate = function(_userParams, state, _dt, plan)
        if plan == nil then return end
        local desired = plan.boards
        local saved = state:get() or {}
        local boards = saved.boards or {}
        local missingModels = 0
        -- Remove stale markers before adding new ones, including when Default
        -- is restored, a capped section is extended, split or bulldozed.
        for _, key in ipairs(keys(boards)) do
            local board, target = boards[key], desired[key]
            local exists = api.engine.entityExists(board.entity)
            if not exists or not target or target.speed ~= board.speed then
                if exists then api.cmd.sendCommand(api.cmd.makeCustomEntityDestroyCmd(board.entity)) end
                boards[key] = nil
            end
        end
        for _, key in ipairs(keys(desired)) do
            local target, board = desired[key], boards[key]
            if board then
                if not sameTransform(board.transf, target.transf) then
                    api.cmd.sendCommand(api.cmd.makeCustomEntityUpdateTransformationCmd(board.entity, matrix(target.transf)))
                    board.transf = target.transf
                end
            else
                local model = owner .. "::/boards/speed_" .. string.format("%03d", target.speed) .. ".mdl"
                local modelId = api.res.modelRep.find(model)
                if modelId >= 0 then
                    -- Engine-state callbacks execute immediately, as in the
                    -- stock custom_entity_util.spawn implementation.
                    api.cmd.sendCommand(api.cmd.makeCustomEntityCreateCmd(modelId), function(result, success)
                        if success and result.resultEntity then
                            local entity = result.resultEntity
                            api.cmd.sendCommand(api.cmd.makeCustomEntityUpdateTransformationCmd(entity, matrix(target.transf)))
                            boards[key] = {entity = entity, speed = target.speed, transf = target.transf}
                        end
                    end)
                else
                    missingModels = missingModels + 1
                end
            end
        end
        saved.boards, saved.dirty, saved.elapsed = boards, false, 0
        local summary = string.format("tracks=%d; capped=%d; entrances=%d; boards=%d; missingModels=%d",
            plan.trackCount, plan.cappedCount, #keys(desired), #keys(boards), missingModels)
        if saved.lastSummary ~= summary then
            message("Entrance boards initialized: " .. summary)
            saved.lastSummary = summary
        end
        state:set(saved)
    end,

    handleEvent = function(_userParams, state, _src, _id, name, _param)
        if name == "builder.proposalApply" then
            local saved = state:get() or {}
            saved.dirty = true
            state:set(saved)
        end
    end,
}
end
