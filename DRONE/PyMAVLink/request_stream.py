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






#Clean Way

'''
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# --- Connection ---
# Establish connection to the flight controller (SITL or Real Drone)
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# Wait for the first heartbeat to confirm connection
vehicle.wait_heartbeat()
print(f"Connected to System: {vehicle.target_system}")

# --- Data Stream Configuration ---
# Instead of waiting for random messages, we strictly request EXTENDED_SYS_STATE
# We use the direct 'command_long_send' method to keep the code short
vehicle.mav.command_long_send(
    vehicle.target_system,
    vehicle.target_component,
    dialect.MAV_CMD_SET_MESSAGE_INTERVAL, # Command ID
    0,                                    # Confirmation
    dialect.MAVLINK_MSG_ID_EXTENDED_SYS_STATE, # Param 1: Message ID (245)
    1e6,                                  # Param 2: Interval in microseconds (1 sec)
    0, 0, 0, 0, 0                         # Params 3-7: Unused
)

print("Requested EXTENDED_SYS_STATE at 1Hz frequency...")

# --- Monitoring Loop ---
try:
    while True:
        # Wait specifically for the message by its string name 'EXTENDED_SYS_STATE'
        # This is much cleaner than using the long dialect path
        msg = vehicle.recv_match(type='EXTENDED_SYS_STATE', blocking=True)
        
        if msg:
            # ACCESS DATA AS OBJECT ATTRIBUTES
            # No need for .to_dict() or ["key"] - we use msg.field_name
            state = msg.landed_state

            # Mapping the numeric state to human-readable text
            if state == dialect.MAV_LAND_ED_STATE_ON_GROUND:
                status_text = "ON THE GROUND"
            elif state == dialect.MAV_LANDED_STATE_TAKEOFF:
                status_text = "TAKING OFF..."
            elif state == dialect.MAV_LANDED_STATE_IN_AIR:
                status_text = "IN THE AIR"
            elif state == dialect.MAV_LANDED_STATE_LANDING:
                status_text = "LANDING..."
            else:
                status_text = f"UNKNOWN STATE ({state})"

            print(f">>> Current Drone Status: {status_text}")

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")

finally:
    # It's good practice to close the connection if your script ends
    vehicle.close()
    print("Connection closed.")



'''
