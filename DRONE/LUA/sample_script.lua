local loop_counter = 0
function simple_loop()
    gcs:send_text(7,"loop_counter : ".. loop_counter)
    -- 7 is for severity --> debug

    gcs:send_named_float("COUNTER", loop_counter)
    --watch NAMED_VALUE_FLOAT to appear on terminal 
    
    gcs:send_named_float("CNT", loop_counter)

    loop_counter= loop_counter +1
    return simple_loop ,1000
end

return simple_loop()
