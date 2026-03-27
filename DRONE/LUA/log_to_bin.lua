local my_data = {}
function save_to_log()
    --fff___> float
    logger:write("OMNI", "latitude,longitude,altitude", "fff", my_data[1], my_data[2], my_data[3])
end


function update()
local current_location = ahrs:get_location()
if current_location then
my_data[1] = current_location:lat() * 1e-7
my_data[2] = current_location:lng() * 1e-7
my_data[3] = current_location:alt() * 1e-2
save_to_log()
end

return update, 1000
  end

return update()

--param set LOG_DISARMED 1
-- to see logs go to --> ls -la ---> ~/ardu-sim/logs$ mavlogdump.py 00000032.BIN 
