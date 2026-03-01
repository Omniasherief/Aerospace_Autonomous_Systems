import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)


# ---  DATA STREAM REQUEST ---
# 1. We use 'MAV_CMD_SET_MESSAGE_INTERVAL' to tell the drone: "I want a specific message."
# 2. 'param1' defines the MESSAGE_ID (The ID of the data packet we need).
# 3. 'param2' defines the INTERVAL in microseconds (1,000,000 us = 1 message per second).
# 4. This is efficient because the drone only sends what we actually ask for.

## Request EXTENDED_SYS_STATE message every 1 second (1,000,000 microseconds)
set_msg_interval_command= dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_SET_MESSAGE_INTERVAL, # The command to change message frequency
    confirmation=0,
    param1=dialect.MAVLINK_MSG_ID_EXTENDED_SYS_STATE, # The ID of the message we want (245)
    param2=1e6, # Interval in microseconds (1,000,000 us = 1 second)
    param3=0, param4=0, param5=0, param6=0, param7=0 )

# Send the interval command to the autopilot
vehicle.mav.send(set_msg_interval_command)
while True:
    try:
        # Wait specifically for the requested message
        msg = vehicle.recv_match(type=dialect.MAVLink_extended_sys_state_message.msgname, blocking=True)
        
        if msg:
            # Convert to dictionary for easy access
            print("raw data        \n ",msg)
            msg_data = msg.to_dict()
            state = msg_data["landed_state"]

            # Evaluate the landing state based on MAVLink enum values
            if state == dialect.MAV_LANDED_STATE_ON_GROUND:
                print(">>> Vehicle status: ON THE GROUND")
            elif state == dialect.MAV_LANDED_STATE_TAKEOFF:
                print(">>> Vehicle status: TAKING OFF...")
            elif state == dialect.MAV_LANDED_STATE_IN_AIR:
                print(">>> Vehicle status: IN THE AIR")
            elif state == dialect.MAV_LANDED_STATE_LANDING:
                print(">>> Vehicle status: LANDING...")

    except KeyboardInterrupt:
        print("Stopping monitor...")
        break

    # Tiny sleep for stability
    time.sleep(0.1)