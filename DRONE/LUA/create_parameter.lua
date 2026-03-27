-- Description: This script shows how to create and use a parameter

-- create and use a parameter
function create_parameter()

    -- define the table key
    local TABLE_KEY = 94

    -- create parameter table
    if not param:add_table(TABLE_KEY, "ASD_", 3) then
        gcs:send_text(7, "Unable to add ASD_ table")
        return
    end
    gcs:send_text(7, "Successfully added ASD_ table")

    -- add first parameter
    if not param:add_param(TABLE_KEY, 1, "PARM_1", 1.0) then
        gcs:send_text(7, "Unable to add ASD_PARM_1 parameter")
        return
    end
    gcs:send_text(7, "Added ASD_PARM_1 parameter successfully")

    -- add second parameter
    if not param:add_param(TABLE_KEY, 2, "PARM_2", 2.0) then
        gcs:send_text(7, "Unable to add ASD_PARM_2 parameter")
        return
    end
    gcs:send_text(7, "Added ASD_PARM_2 parameter successfully")

    -- add third parameter
    if not param:add_param(TABLE_KEY, 3, "PARM_3", 3.0) then
        gcs:send_text(7, "Unable to add ASD_PARM_3 parameter")
        return
    end
    gcs:send_text(7, "Added ASD_PARM_3 parameter successfully")

    -- create ASD_PARM_1 parameter object
    local ASD_PARM_1 = Parameter()
    if not ASD_PARM_1:init("ASD_PARM_1") then
        gcs:send_text(7, "Failed to initialize the parameter")
        return
    end

    -- notify the user about the parameter value
    gcs:send_text(7, "Value of ASD_PARM_1: " .. ASD_PARM_1:get())

    -- set the parameter
    local result = ASD_PARM_1:set(1.5)

    -- notify the user about the result
    gcs:send_text(7, "Parameter set operation result: " .. tostring(result))

    -- notify the user about the parameter value
    gcs:send_text(7, "Value of ASD_PARM_1: " .. ASD_PARM_1:get())

    -- schedule the next call to this function
    return create_parameter, 1000
end

-- start the script
return create_parameter()
--param show ASD_*


-- -- Configuration
-- -- Description: Super Simple Speed Sync 
-- -- Written for ArduPilot Lua 

-- local TABLE_KEY = 93
-- local PREFIX = "ASD_"
-- local last_speed = -1

-- function update()
--     -- 1. Create Table (Using pcall to prevent crashes)
--     local status = param:add_table(TABLE_KEY, PREFIX, 3)
    
--     if status then
--         param:add_param(TABLE_KEY, 1, "SPEED", 15.0)
--         param:add_param(TABLE_KEY, 2, "ALT",   20.0)
--         param:add_param(TABLE_KEY, 3, "FLAG",  0.0)
--     end

--     -- 2. Initialize Parameters
--     local my_speed_ptr = Parameter()
--     local nav_speed_ptr = Parameter()

--     -- Check if both parameters exist before doing anything
--     if my_speed_ptr:init(PREFIX .. "SPEED") and nav_speed_ptr:init("WP_NAV_SPEED") then
--         local current_speed = my_speed_ptr:get()

--         -- 3. Only Update if value changed
--         if current_speed ~= last_speed then
--             nav_speed_ptr:set(current_speed)
--             gcs:send_text(6, "OMN: Speed is now " .. tostring(current_speed))
--             last_speed = current_speed
--         end
--     end

--     --return update, 1000 -- Run again in 1 second
-- end

-- -- Force a message to GCS as soon as the file is read
-- gcs:send_text(6, "LUA: Script Started Successfully!")

-- return update()