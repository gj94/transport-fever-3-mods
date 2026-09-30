-- Retain stock wheels/rail behaviour and select the trailing pantograph.
local stock = ug_require "::/vehicle/train/shared/transformator_train.script.tl" as any

local updateFn = function(captureParams: NativeLuaTable, params: TransformatorParams, output: Transformator.TransfOutput)
    stock.train.updateFn(captureParams, params, output)
    if params.currentInfo.landVehicle ~= nil then
        local height = params.landVehicleApi:getAverageCatenaryHeight(10, -20)
        local frame = math.max(0, math.min(1000, (height - 4.255) / (5.917 - 4.255) * 1000))
        local frontFrame = 0
        local rearFrame = frame
        if params.currentInfo.landVehicle.reversed then frontFrame = frame; rearFrame = 0 end
        output:addAnimationState("pantograph_front", -1, frontFrame, false, false)
        output:addAnimationState("pantograph_rear", -1, rearFrame, false, false)
    end
end

return {wag9 = {updateFn = updateFn}}
