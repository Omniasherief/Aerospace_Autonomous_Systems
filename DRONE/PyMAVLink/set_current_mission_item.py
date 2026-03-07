
# Previous Script---> go_to_locations.py (Guided Waypoint): Sends a single coordinate directly to the drone to move NOW.
# Current Script (Mission Control): Interacts with a PRE-LOADED list of points (Mission) stored in the Flight Controller's memory.
# This script uses 'MAV_CMD_DO_SET_MISSION_CURRENT' to jump between existing mission indexes.
#Pre-requisite: A mission (way.txt)must be uploaded to the drone and mode set to AUTO.
#wp load way.txt--> mode AUTO
#module load misseditor --> add points and save (gui)
#wp list , wp clear bla bla 
import sys
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect


if len(sys.argv) <2:
    print("Usage: python3 set_current_mission_item.py <waypoint_index>")
    sys.exit(1)

seq_desired=int(sys.argv[1])

vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print(f"Connected! Target WP: {seq_desired}")

# 1. Listen for the MISSION_CURRENT message to see where the drone is now
msg=vehicle.recv_match(type="MISSION_CURRENT",blocking=True)
print(f"Current Waypoint before jump: {msg.seq}")
# 2. Send the Jump Command (DO_SET_MISSION_CURRENT)
# We use COMMAND_LONG because it is a standard action request


# WHY COMMAND_LONG?
# We use COMMAND_LONG for 'Action Commands' that don't require high-precision GPS coordinates.
# MAV_CMD_DO_SET_MISSION_CURRENT only needs the sequence index (Param 1),
# which fits perfectly in the 7-parameter structure of a LONG message.

vehicle.mav.command_long_send(
    vehicle.target_system,
    vehicle.target_component,
    dialect.MAV_CMD_DO_SET_MISSION_CURRENT, # Command ID: 190
    0,              # Confirmation
    seq_desired,    # Param 1: The sequence number to jump to
    0, 0, 0, 0, 0, 0 # Unused parameters
)
# 3. Verify if the jump was successful
time.sleep(1) # Small delay for processing
msg = vehicle.recv_match(type='MISSION_CURRENT', blocking=True)

if msg.seq == seq_desired:
    print(f"Success! Drone is now heading to Waypoint #{msg.seq}")
else:
    print(f"Failed. Drone is still at Waypoint #{msg.seq}")

vehicle.close()