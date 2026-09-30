-- Stock wheels, doors and rail behaviour plus one independent trailer rig.
local stock = ug_require "::/vehicle/train/shared/transformator_train.script.tl" as any

local updateFn = function(captureParams: NativeLuaTable, params: TransformatorParams, output: Transformator.TransfOutput)
    stock.train.updateFn(captureParams, params, output)
    if params.currentInfo.landVehicle ~= nil then
        local height = params.landVehicleApi:getAverageCatenaryHeight(8, -8)
        local frame = math.max(0, math.min(1000, (height - 4.079122) / (5.917 - 4.079122) * 1000))
        output:addAnimationState("pantograph", -1, frame, false, false)
    end
end

return {vb = {updateFn = updateFn}}
