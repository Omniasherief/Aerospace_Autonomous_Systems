function add()
    --return 1 + "a"
     return 1 + 2
end

function protected_call()

    -- pcall(add) executes the 'add' function in "Protected Mode"
    -- It returns TWO values:
    -- success: A boolean (true if function ran fine, false if it crashed)
    -- result: The return value (if success) OR the error message (if failure)
    local success, result = pcall(add)
    if not success then
        gcs:send_text(7, "Caught, error: " .. result)
    else
        gcs:send_text(7, "Success, result: " .. result)
    end
    gcs:send_text(7, "Called the function")
end

return protected_call()