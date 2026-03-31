-- Description: This script checks the Firmware version and type for safety.
-- It ensures the script only runs on the correct vehicle and version.

-- [[ 1. CONFIGURATION & CONSTANTS ]]
local VEHICLE_TYPE_COPTER = 2       -- In ArduPilot, '2' represents a Copter
local MINIMUM_REQUIRED_VERSION = 4.5 -- The script needs at least version 4.5
local REQUIRED_VERSION_HASH = "73480438" -- The unique fingerprint of the firmware

-- [[ 2. MAIN CHECK FUNCTION ]]
function get_firmware()

    -- A. EXTRACTING FIRMWARE DATA
    -- We use the 'FWVersion' object to pull data from the flight controller
    local VERSION_MAJOR  = FWVersion:major()  -- The main version number (e.g., 4)
    local VERSION_MINOR  = FWVersion:minor()  -- The minor version number (e.g., 5)
    local VERSION_PATCH  = FWVersion:patch()  -- The specific patch/update number
    local VERSION_HASH   = FWVersion:hash()   -- The unique Git Hash (Fingerprint)
    local VERSION_STRING = FWVersion:string() -- The full descriptive name of the firmware
    local VEHICLE_TYPE   = FWVersion:type()   -- Returns the type of vehicle (Copter, Plane, etc.)

    -- B. REPORTING TO THE USER (GCS)
    -- Using string.format to display the version clearly in the terminal
    gcs:send_text(7, string.format("Detected Version: %d.%d.%d", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH))
    gcs:send_text(7, "Firmware Hash: " .. VERSION_HASH)
    gcs:send_text(7, "Vehicle Type ID: " .. VEHICLE_TYPE)

    -- C. SAFETY GUARD: VEHICLE TYPE CHECK
    -- '~=' means 'Not Equal To'. This stops the script if it's not a Copter.
    if VEHICLE_TYPE ~= VEHICLE_TYPE_COPTER then
        gcs:send_text(7, "ERROR: This script is intended for Copters ONLY!")
        return -- Exit the function and stop the script
    end

    -- D. SAFETY GUARD: VERSION NUMBER CHECK
    -- We calculate a decimal value to compare with our minimum requirement
    if (VERSION_MAJOR + (VERSION_MINOR * 0.1)) < MINIMUM_REQUIRED_VERSION then
        gcs:send_text(7, "ERROR: Firmware too old. Please update to 4.5+")
        return -- Exit
    end

    -- E. SAFETY GUARD: HASH (FINGERPRINT) CHECK
    -- This ensures the firmware matches our tested environment exactly
    if REQUIRED_VERSION_HASH ~= VERSION_HASH then
        gcs:send_text(7, "WARNING: Version Hash mismatch! Proceed with caution.")
        -- We don't 'return' here, just giving a warning
    end

    -- F. DEVELOPMENT VERSION CHECK
    -- Searches for the word "dev" in the version name to alert the pilot
    if string.find(VERSION_STRING, "dev") then
        gcs:send_text(7, "ALERT: You are using a Development build. Not stable!")
    end

    -- If all checks pass:
    gcs:send_text(7, "Firmware check passed. Starting main operations...")

    -- Note: We don't return the function name here because 
    -- we only need to check the firmware ONCE at the start.
end

-- [[ 3. START THE SCRIPT ]]
return get_firmware()