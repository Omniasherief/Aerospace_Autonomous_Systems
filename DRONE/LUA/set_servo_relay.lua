-- param show SERVO*_FUNCTION
-- param set SERVO8_FUNCTION 94
-- module load graph
-- graph SERVO_OUTPUT_RAW.servo8_raw
local MAV_SEVERITY_DEBUG = 7
local LOOP_DELAY_IN_MS = 1000
local RELAY_INSTANCE = 0
local SERVO_FUNCTION = 94
local flipflop = true
local servo_channel

-- set servo and relay outputs
function set_servo_relay()

    -- check if servo does exist
    if not servo_channel then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Servo does not exist for function " .. SERVO_FUNCTION)
        return set_servo_relay, LOOP_DELAY_IN_MS
    end

    -- check if relay does exist
    if not relay:enabled(RELAY_INSTANCE) then
        gcs:send_text(MAV_SEVERITY_DEBUG, "Relay instance " .. RELAY_INSTANCE .." is not enabled")
        return set_servo_relay, LOOP_DELAY_IN_MS
    end

    -- flipflop is true
    if flipflop then

        -- set servo
        SRV_Channels:set_output_pwm_chan(servo_channel, 2000)

        -- set relay
        relay:on(RELAY_INSTANCE)

    -- flipflop is false
    else

        -- clear servo
        SRV_Channels:set_output_pwm_chan(servo_channel, 1000)

        -- clear relay
        relay:off(RELAY_INSTANCE)

    end

    -- notify the user about the servo state
    local servo_state = SRV_Channels:get_output_pwm(SERVO_FUNCTION)
    gcs:send_text(MAV_SEVERITY_DEBUG, "Servo current state: " .. servo_state)

    -- notify the user about the relay state
    local relay_state = relay:get(RELAY_INSTANCE)
    gcs:send_text(MAV_SEVERITY_DEBUG, "Relay current state: " .. relay_state)

    -- flip the flipflop
    flipflop = not flipflop

    -- schedule the next call to this function
    return set_servo_relay, LOOP_DELAY_IN_MS
end

-- get servo channel number
servo_channel = SRV_Channels:find_channel(SERVO_FUNCTION)

-- start the script
return set_servo_relay()