local soundsetutil = require "::/scripts/soundsetutil.lua"
local stock = "::/vehicle/train/shared/sound/"

function data()
    local result = soundsetutil.makeSoundSet()
    local speed = { "vehicle", "speed01" }
    soundsetutil.addTrackParam01(result, stock .. "train_electric_modern/train_electric_modern_idle.wav", 25.0,
        { { 0.0, 1.0 }, { 0.8, 0.5 } },
        { { 0.0, 0.9 }, { 1.0, 1.1 } }, speed)
    soundsetutil.addTrackParam01(result, stock .. "train_electric_modern/train_electric_modern_drive.wav", 25.0,
        { { 0.0, 0.0 }, { 0.1, 0.5 }, { 1.0, 1.1 } },
        { { 0.0, 0.8 }, { 1.0, 1.3 } }, speed)
    soundsetutil.addTrackCustom(result, stock .. "train_electric_modern/train_electric_modern_accelerate.wav", 25.0,
        { { 0.0, 0.0 }, { 0.05, 1.0 }, { 0.5, 0.8 }, { 0.9, 0.0 } },
        { { 0.05, 0.5 }, { 0.15, 0.9 }, { 0.15, 0.7 }, { 0.5, 1.0 } }, speed, speed,
        "::/vehicle/shared/sound/multiplyTrackUpdate.script@updateFn")
    soundsetutil.addTrackSqueal(result, stock .. "train/wheels_ringing1.wav", 25.0)
    soundsetutil.addTrackBrake(result, stock .. "train_electric_modern/_brakes.wav", 25.0, 0.5)
    local clacks = {}
    for i = 1, 10 do
        clacks[i] = stock .. "clack/modern/part_" .. i .. ".wav"
    end
    soundsetutil.addEventClacks(result, clacks, 25.0, 10000.0)
    soundsetutil.addEvent(result, "horn", { "wap7_horn.wav" }, 50.0)
    return result
end
