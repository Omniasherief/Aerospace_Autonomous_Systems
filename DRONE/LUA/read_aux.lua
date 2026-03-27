
-- [[
--  RC CHANNEL ASSIGNMENT SUMMARY:
--  1. Primary Channels (RC1 - RC4): 
--     - Reserved for Flight Controls: Roll, Pitch, Throttle, and Yaw.
--     - WARNING: Do NOT set RC1_OPTION to RC4_OPTION to 300. 
--     - If changed, you will LOSE physical control over the vehicle's angles/movement.
--
--  2. Auxiliary Channels (RC5 - RC16):
--     - Used for Scripting and extra functions.
--     - Use these for your Lua scripts (e.g., set RC5_OPTION = 300).
--
--  3. Scripting Options (300 - 307):
--     - 300 (Scripting 1) acts as the bridge between the RC Hardware and this code.
--     - The script uses "rc:find_channel_for_option(300)" to find the physical switch.
--
--  4. PWM Values to Switch Positions:
--     - 1000 PWM = LOW (0)
--     - 1500 PWM = MEDIUM (1)
--     - 2000 PWM = HIGH (2)
-- ]]




-- define global variables
local MAV_SEVERITY_DEBUG = 7
local LOOP_DELAY_IN_MS = 1000
local SCRIPTING_1 = 300 -- The ID that links the script to a Radio Channel (RCx_OPTION)
--307 means AUX8
local LOW = 0    -->1000
local MEDIUM = 1 -->1500
local HIGH = 2   -->2000
local switch_1


switch_1 = rc:find_channel_for_option(SCRIPTING_1)


function read_aux()
if not switch_1 then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Switch does not exist for option " .. SCRIPTING_1)
        return read_aux, LOOP_DELAY_IN_MS
    end
--Get Current Position
local switch_1_value = switch_1:get_aux_switch_pos()

if switch_1_value == LOW then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Switch is LOW") -- Executes if value is 0
        
    elseif switch_1_value == MEDIUM then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Switch is MEDIUM") -- Executes if value is 1
        
    elseif switch_1_value == HIGH then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Switch is HIGH") -- Executes if value is 2
        
    else
        -- This runs if something goes wrong with the RC signal
        gcs:send_text(MAV_SEVERITY_DEBUG, "Switch is in unknown position")
    end


    -- Tell ArduPilot to run this specific function again after 1 second
    return read_aux, LOOP_DELAY_IN_MS
end

return read_aux()

-- i got AP: Scripting: restarted
-- AP: Switch does not exist for option 300
-- AP: Switch does not exist for option 300
-- AP: Switch does not exist for option 300
---   sol ==
--param show RC*_OPTION
-- param set RC5_OPTION 300 
-- rc 5 1000-> low 1500-> mid --> 2000 high

