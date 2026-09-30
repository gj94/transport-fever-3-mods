-- Reversed section is the trailing cab of the opposed, two-section MU.
local stock = ug_require "::/vehicle/train/shared/transformator_train.script.tl" as any

local updateFn = function(captureParams: NativeLuaTable, params: TransformatorParams, output: Transformator.TransfOutput)
    stock.train.updateFn(captureParams, params, output)
    if params.currentInfo.landVehicle ~= nil then
        local frame = 0
        if params.currentInfo.landVehicle.reversed then
            local height = params.landVehicleApi:getAverageCatenaryHeight(3.3, -12.7)
            frame = math.max(0, math.min(1000, (height - 4.245) / (7.520 - 4.245) * 1000))
        end
        output:addAnimationState("pantograph", -1, frame, false, false)
    end
end

return {wag12b = {updateFn = updateFn}}
