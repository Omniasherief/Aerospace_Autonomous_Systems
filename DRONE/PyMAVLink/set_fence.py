'''
LOGIC: Backups FENCE_ACTION -> Disables Fence (Safety) -> Clears memory (FENCE_TOTAL=0) -> 
       Uploads new points scaled by 1e7 -> Verifies each point -> Restores FENCE_ACTION.

'''
"""
VERSION: Legacy Fence Protocol (works with set only)
METHOD: Uses 'MAVLink_fence_point_message' and 'MAVLink_fence_fetch_point_message'.
CHARACTERISTICS: 
- Sends coordinates as Floats (Decimal numbers).
- Uses older message types that might not be supported by modern ArduPilot (4.0+) for GETting data.
- Directly addresses the fence storage without treating it as a mission.
"""

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# 1. PARAMETER DEFINITIONS
# FENCE_TOTAL: The total number of points in the fence.
# FENCE_ACTION: The action the drone takes when the fence is breached (e.g., RTL, Land).
FENCE_TOTAL = "FENCE_TOTAL".encode(encoding="utf-8")
FENCE_ACTION = "FENCE_ACTION".encode(encoding="utf8")
PARAM_INDEX = -1 # Use -1 to search by Name instead of Index

# 2. DEFINE THE FENCE POINTS
# Index 0: Return Point (The safe location the drone flies to if it breaks the fence).
# Index 1: The first corner of the polygon.
# Index N: The last corner (Must be identical to Index 1 to close the polygon).
fence_list = [
    (-35.363152, 149.164795),  # Point 0: Return Point
    (-35.361019, 149.161057),  # Point 1: Start of Polygon
    (-35.360817, 149.168533),
    (-35.365364, 149.168686),
    (-35.365486, 149.160919),
    (-35.363792, 149.160919),
    (-35.363747, 149.163574),
    (-35.362366, 149.163666),
    (-35.362286, 149.161011),
    (-35.361019, 149.161057)   # Point 9: Closing Point (Matches Point 1)
]

# 3. ESTABLISH CONNECTION
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print(f"Connected to System: {vehicle.target_system}, Component: {vehicle.target_component}")

# 4. BACKUP ORIGINAL FENCE ACTION
# Before modifying anything, we save the current FENCE_ACTION to restore it later.
print("Fetching original FENCE_ACTION...")
param_read = dialect.MAVLink_param_request_read_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    param_id=FENCE_ACTION,
    param_index=PARAM_INDEX
)
vehicle.mav.send(param_read)

while True:
    message = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    message_dict = message.to_dict()
    if message_dict["param_id"] == "FENCE_ACTION":
        fence_action_original = int(message_dict["param_value"])
        break

print(f"Original FENCE_ACTION saved: {fence_action_original}")

# 5. DISABLE FENCE FOR SAFETY
# We set FENCE_ACTION to 0 (None) so the drone doesn't trigger an alarm while we are changing points.
print("Disabling fence monitoring for upload...")
while True:
    set_action_none = dialect.MAVLink_param_set_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        param_id=FENCE_ACTION,
        param_value= 0,            #dialect.FENCE_ACTION_NONE, # 0
        param_type=dialect.MAV_PARAM_TYPE_REAL32
    )
    vehicle.mav.send(set_action_none)
    
    # Confirm the change
    msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    if msg.to_dict()["param_id"] == "FENCE_ACTION" and int(msg.param_value) == 0:
        print("Fence disabled successfully.")
        break

# 6. RESET AND PREPARE MEMORY (FENCE_TOTAL)
# We set FENCE_TOTAL to 0 to clear old data, then set it to the new list size.
print("Clearing old fence and allocating space...")
for value in [0, len(fence_list)]:
    while True:
        set_total = dialect.MAVLink_param_set_message(
            target_system=vehicle.target_system,
            target_component=vehicle.target_component,
            param_id=FENCE_TOTAL,
            param_value=value,
            param_type=dialect.MAV_PARAM_TYPE_REAL32
        )
        vehicle.mav.send(set_total)
        msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
        if msg.to_dict()["param_id"] == "FENCE_TOTAL" and int(msg.param_value) == value:
            break
print(f"FENCE_TOTAL set to {len(fence_list)}.")

# 7. UPLOAD POINTS LOOP
# We send each point and immediately ask the drone to send it back to verify it was saved correctly.
idx = 0
while idx < len(fence_list):
    # Send the point
    point_msg = dialect.MAVLink_fence_point_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        idx=idx,
        count=len(fence_list),
        lat=fence_list[idx][0],
        lng=fence_list[idx][1]
    )
    vehicle.mav.send(point_msg)

    # Fetch the point back to verify
    fetch_msg = dialect.MAVLink_fence_fetch_point_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        idx=idx
    )
    vehicle.mav.send(fetch_msg)

    # Wait for confirmation
    check_msg = vehicle.recv_match(type=dialect.MAVLink_fence_point_message.msgname, blocking=True)
    if check_msg:
        print(f"Confirmed Point #{idx}: Lat={check_msg.lat}, Lng={check_msg.lng}")
        idx += 1

print("All fence items uploaded successfully!")

# 8. RESTORE ORIGINAL FENCE ACTION
# Re-enable the fence by setting FENCE_ACTION back to its original value.
print(f"Restoring FENCE_ACTION to {fence_action_original}...")
while True:
    restore_msg = dialect.MAVLink_param_set_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        param_id=FENCE_ACTION,
        param_value=fence_action_original,
        param_type=dialect.MAV_PARAM_TYPE_REAL32
    )
    vehicle.mav.send(restore_msg)
    msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    if msg.to_dict()["param_id"] == "FENCE_ACTION" and int(msg.param_value) == fence_action_original:
        print("Fence re-enabled. Process Complete.")
        break




"""
VERSION: Modern Mission Protocol (INT)
METHOD: Uses 'MAVLink_mission_item_int_message' and 'MAVLink_mission_request_int_message'.
CHARACTERISTICS:
- High Precision: Scales coordinates by 10,000,000 (1e7) and sends them as Integers.
- Mission-Based: Treats the Geo-Fence as a specific type of mission (MAV_MISSION_TYPE_FENCE).
- Universal: Works reliably for both SETting and GETting data on all modern ArduPilot firmware.
"""
'''
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# 1. PARAMETER DEFINITIONS
FENCE_TOTAL = "FENCE_TOTAL".encode(encoding="utf-8")
FENCE_ACTION = "FENCE_ACTION".encode(encoding="utf8")
PARAM_INDEX = -1 

# 2. DEFINE THE FENCE POINTS
# Reminder: Point 0 is the Return Point. Point 1 to N-1 are polygon corners.
fence_list = [
    (-35.363152, 149.164795),  # Return Point
    (-35.361019, 149.161057),  # Polygon Start
    (-35.360817, 149.168533),
    (-35.365364, 149.168686),
    (-35.365486, 149.160919),
    (-35.361019, 149.161057)   # Polygon Close (Matches Point 1)
]

# 3. CONNECT TO VEHICLE
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print(f"Connected to System: {vehicle.target_system}")

# 4. BACKUP AND DISABLE FENCE ACTION (Safety Step)
# We fetch the original action (like RTL or Land) and then set it to 0 (None)
# to prevent the drone from reacting while we update the points.
print("Fetching and disabling FENCE_ACTION for safety...")
vehicle.mav.send(dialect.MAVLink_param_request_read_message(
    target_system=vehicle.target_system, target_component=vehicle.target_component,
    param_id=FENCE_ACTION, param_index=PARAM_INDEX))

# Wait for original value
msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
fence_action_original = int(msg.param_value)

# Set FENCE_ACTION to 0 (None)
vehicle.mav.send(dialect.MAVLink_param_set_message(
    target_system=vehicle.target_system, target_component=vehicle.target_component,
    param_id=FENCE_ACTION, param_value=0, param_type=dialect.MAV_PARAM_TYPE_REAL32))
print(f"Original action {fence_action_original} saved. Monitoring disabled.")

# 5. PREPARE MEMORY (FENCE_TOTAL)
# We clear old fence data by setting total to 0, then set it to our new list length.
for val in [0, len(fence_list)]:
    vehicle.mav.send(dialect.MAVLink_param_set_message(
        target_system=vehicle.target_system, target_component=vehicle.target_component,
        param_id=FENCE_TOTAL, param_value=val, param_type=dialect.MAV_PARAM_TYPE_REAL32))
    vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
print(f"Memory ready for {len(fence_list)} points.")

# 6. MODERN UPLOAD LOOP (Using Mission Protocol / INT)
# We replaced MAVLink_fence_point_message with MISSION_ITEM_INT.
# This protocol is more robust and uses 1e7 scaling for high precision.
idx = 0
while idx < len(fence_list):
    # Convert lat/lng to integers (Scaling by 10,000,000)
    lat_int = int(fence_list[idx][0] * 1e7)
    lng_int = int(fence_list[idx][1] * 1e7)

    # Send Point as MISSION_ITEM_INT
    # Note: mission_type must be MAV_MISSION_TYPE_FENCE (2)
    item_msg = dialect.MAVLink_mission_item_int_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        seq=idx,
        frame=dialect.MAV_FRAME_GLOBAL_INT,
        command=dialect.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION, # Defining it as a vertex
        current=0, autocontinue=0, param1=0, param2=0, param3=0, param4=0,
        x=lat_int, # Latitude as INT
        y=lng_int, # Longitude as INT
        z=0,
        mission_type=dialect.MAV_MISSION_TYPE_FENCE
    )
    vehicle.mav.send(item_msg)

    # VERIFICATION: Request the point back to ensure the drone saved it correctly.
    fetch_msg = dialect.MAVLink_mission_request_int_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        seq=idx,
        mission_type=dialect.MAV_MISSION_TYPE_FENCE
    )
    vehicle.mav.send(fetch_msg)

    # Confirm response
    check = vehicle.recv_match(type=dialect.MAVLink_mission_item_int_message.msgname, blocking=True, timeout=1)
    if check and check.seq == idx:
        print(f"Verified Point #{idx}: {check.x/1e7}, {check.y/1e7}")
        idx += 1

print("Upload Complete!")

# 7. RESTORE ORIGINAL FENCE ACTION
# Re-enable the drone's fence protection with its original behavior.
vehicle.mav.send(dialect.MAVLink_param_set_message(
    target_system=vehicle.target_system, target_component=vehicle.target_component,
    param_id=FENCE_ACTION, param_value=float(fence_action_original), 
    param_type=dialect.MAV_PARAM_TYPE_REAL32))
print("Fence protection re-enabled.")
'''