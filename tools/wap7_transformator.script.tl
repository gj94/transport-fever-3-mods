-- Preserve the installed game's train behaviour and add two independent rigs.
local stock = ug_require "::/vehicle/train/shared/transformator_train.script.tl" as any

local updateFn = function(captureParams: NativeLuaTable, params: TransformatorParams, output: Transformator.TransfOutput)
    stock.train.updateFn(captureParams, params, output)
    if params.currentInfo.landVehicle ~= nil then
        local reversed = params.currentInfo.landVehicle.reversed
        -- The selected pantograph is behind the centre in either travel direction.
        local offset = -5
        local height = params.landVehicleApi:getAverageCatenaryHeight(15 + offset, -15 + offset)
        local frame = math.max(0, math.min(1000, (height - 4.254758) / (5.944412 - 4.254758) * 1000))
        local frontFrame = 0
        local rearFrame = frame
        if reversed then frontFrame = frame; rearFrame = 0 end
        output:addAnimationState("pantograph_front", -1, frontFrame, false, false)
        output:addAnimationState("pantograph_rear", -1, rearFrame, false, false)
    end
end

return {wap7 = {updateFn = updateFn}}
