-- mode enumerations, helper, constants, configurations
local COPTER_MODES = { [0] = "STABILIZE", [4] = "GUIDED", [6] = "RTL"}
local COPTER_MODE_STABILIZE = 0
local COPTER_MODE_GUIDED = 4
local COPTER_MODE_RTL = 6
local ALT_FRAME_ABOVE_HOME = 1
local TAKEOFF_ALTITUDE = 30
local TARGET_DECISION_DISTANCE = 5
local LOOP_DELAY = 1000
local SEVERITY = 7
local navigation_index = 1

-- target locations
local target_locations = { { -35.36573684, 149.16312254, 30.0 },
                           { -35.36135212, 149.16115359, 45.0 },
                           { -35.36022811, 149.16580334, 20.0 },
                           { -35.36565041, 149.16683329, 35.0 } }


function createLocation(lat, lng, alt)
    local location = Location()
    location:relative_alt(true)
    location:lat(math.floor(lat * 1e7))
    location:lng(math.floor(lng * 1e7))
    location:alt(math.floor(alt * 1e2))
    return location
end

function multi_location_mission()

     -- notify user
    gcs:send_text(SEVERITY, "Starting the mission")

    -- call flight mode change step
    return change_flight_mode, LOOP_DELAY
end
-- Step 1: Initialize the mission and ensure the drone is in GUIDED mode
function change_flight_mode()

    -- get flight mode
    local mode_number = vehicle:get_mode()
    local mode_name = COPTER_MODES[mode_number]
--local mode_name = COPTER_MODES[mode_number] or "UNKNOWN (" .. tostring(mode_number) .. ")"
    gcs:send_text(SEVERITY, "Flight mode: " .. mode_name)
    -- Check if we are already in GUIDED mode (Mode 4)
     if mode_number ~= COPTER_MODE_GUIDED then
        vehicle:set_mode(COPTER_MODE_GUIDED)
        return change_flight_mode, LOOP_DELAY
    end
    local is_flying = vehicle:get_likely_flying()

    -- jump start to do navigation if already flying
    if is_flying then
        gcs:send_text(SEVERITY, "Jump starting to do navigation")
        navigation_index = 1
        return do_navigation(), LOOP_DELAY
    end

    -- If mode is GUIDED, proceed to the next step: Arming
    -- call arm vehicle step
    return arm_vehicle, LOOP_DELAY
end

-- Step 2: Check pre-arm safety and arm the motors
function arm_vehicle()
    -- get armable N arming status
    local is_armable = arming:pre_arm_checks()
    local is_armed = arming:is_armed()

    -- arm the vehicle
    if not is_armed and is_armable then
        gcs:send_text(SEVERITY, "Arming the vehicle...")
        arming:arm()
    end

    -- call this function again if it is not is_armed
    if not is_armed then
        return arm_vehicle, LOOP_DELAY
    end

    -- notify user
    gcs:send_text(SEVERITY, "Armed the vehicle")

    -- call takeoff vehicle step
    return takeoff_vehicle, LOOP_DELAY
end

-- Step 3: Initiate the takeoff process
function takeoff_vehicle()
    -- Check if the vehicle has already started the takeoff command
    local is_taking_off = vehicle:is_taking_off()

    -- If not taking off yet, send the takeoff command
    if not is_taking_off then
        gcs:send_text(SEVERITY, "Trying to take off to " .. TAKEOFF_ALTITUDE .. " meters...")
        vehicle:start_takeoff(TAKEOFF_ALTITUDE) -- Command the drone to rise to the set altitude
        return takeoff_vehicle, LOOP_DELAY      -- Stay in this function until takeoff starts
    end

    -- Notify the user that the command was accepted and takeoff is in progress
    gcs:send_text(SEVERITY, "Takeoff is successful")

    -- Transition to the next state: Waiting to reach the altitude
    return wait_takeoff, LOOP_DELAY
end

-- Step 4: Monitor altitude until takeoff is finished
function wait_takeoff()
    -- Check if the drone is still in the "taking off" state
    local is_taking_off = vehicle:is_taking_off()

    -- Get current location and convert altitude to meters above home
    local current_location = ahrs:get_location()
    current_location:change_alt_frame(ALT_FRAME_ABOVE_HOME)
    local current_altitude = current_location:alt() * 1e-2 -- Convert centimeters to meters

    -- If still rising, display progress and repeat this check
    if is_taking_off then
        gcs:send_text(SEVERITY, "Waiting for altitude: " .. math.floor(current_altitude) .. "/" .. TAKEOFF_ALTITUDE .. " meters...")
        return wait_takeoff, LOOP_DELAY
    end

    -- Once the target altitude is reached, ArduPilot exits 'is_taking_off' state
    gcs:send_text(SEVERITY, "Takeoff is complete")

    -- Move to the Navigation stage to visit waypoints
    return do_navigation, LOOP_DELAY
end

-- Step 5: Navigate through the list of waypoints
function do_navigation()
    -- Create a location object for the current target waypoint using our helper function
    local target_location = createLocation(target_locations[navigation_index][1], 
                                           target_locations[navigation_index][2], 
                                           target_locations[navigation_index][3])

    -- Send the movement command to the drone (Go to this coordinate)
    vehicle:set_target_location(target_location)

    -- Get the drone's current position to calculate the remaining distance
    local current_location = ahrs:get_location()
    local target_distance = current_location:get_distance(target_location)

    -- Log the distance to the current waypoint for monitoring
    gcs:send_text(SEVERITY, "Waypoint " .. navigation_index .. " distance: " .. math.floor(target_distance) .. "m")

    -- If the drone is close enough to the waypoint, move to the next one
    if target_distance < TARGET_DECISION_DISTANCE then
        gcs:send_text(SEVERITY, "Reached to waypoint: " .. navigation_index)
        navigation_index = navigation_index + 1 -- Increment the index to the next location
    end

    -- If all waypoints have been visited, start the Return to Launch (RTL) sequence
    if navigation_index > #target_locations then
        gcs:send_text(SEVERITY, "Mission is complete")
        return return_to_launch, LOOP_DELAY
    end

    -- Repeat this function to continue flying toward the current waypoint
    return do_navigation, LOOP_DELAY
end

-- Step 6: Return the drone to the takeoff point (Home)
function return_to_launch()
    -- Get current flight mode
    local mode_number = vehicle:get_mode()
    local mode_name = COPTER_MODES[mode_number]

    -- Calculate how far we are from the Home position
    local home_location = ahrs:get_home()
    local current_location = ahrs:get_location()
    local home_distance = current_location:get_distance(home_location)

    -- Inform the user about the return progress
    gcs:send_text(SEVERITY, "Returning to home, flight mode: " .. mode_name .. ", distance: " .. math.floor(home_distance) .. " meters")

    -- Change mode to RTL (Mode 6) to trigger automatic landing at Home
    if mode_number ~= COPTER_MODE_RTL then
        vehicle:set_mode(COPTER_MODE_RTL)
    end

    -- Once the drone is almost back at home, switch to the final landing check
    if home_distance < TARGET_DECISION_DISTANCE then
        gcs:send_text(SEVERITY, "Reached to home")
        return wait_disarm, LOOP_DELAY
    end

    -- Keep monitoring until the drone arrives home
    return return_to_launch, LOOP_DELAY
end

-- Final Step: Monitor the drone until it lands and disarms
function wait_disarm()
    -- Get current arming and landing status
    local is_armed = arming:is_armed()
    local is_landing = vehicle:is_landing()

    -- Monitor current altitude during descent
    local current_location = ahrs:get_location()
    current_location:change_alt_frame(ALT_FRAME_ABOVE_HOME)
    local current_altitude = current_location:alt() * 1e-2

    -- Display final stage telemetry
    gcs:send_text(SEVERITY, "Final stage, armed:" .. tostring(is_armed) .. " landing:" .. tostring(is_landing) .. " altitude:" .. math.floor(current_altitude) .. "m")

    -- Continue looping until the user stops the script or the drone is safely on the ground
    return wait_disarm, LOOP_DELAY
end

-- Main Execution: Start the mission sequence by calling the first function
return multi_location_mission()