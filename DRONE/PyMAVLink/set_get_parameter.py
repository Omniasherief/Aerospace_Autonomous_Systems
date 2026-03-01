import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# We use BATT_MONITOR because we verified it exists in MAVProxy
TARGET_PARAM = "BATT_MONITOR"

# 1. Connect via UDP
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# 2. IMPORTANT: Wait for heartbeat to identify the drone's System ID (e.g., ID 1)
print("Waiting for drone to wake up...")
vehicle.wait_heartbeat()
print(f"Connected! Drone ID: {vehicle.target_system}")

# 3. Create READ request (Asking: What is the current value?)
read_msg = dialect.MAVLink_param_request_read_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    param_id=TARGET_PARAM.encode("utf-8"), # Binary format for MAVLink
    param_index=-1 # Use the name, not the number
)

# 4. Create SET message (Changing value to 0)
set_msg = dialect.MAVLink_param_set_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    param_id=TARGET_PARAM.encode("utf-8"),
    param_value=0, # New value
    param_type=dialect.MAV_PARAM_TYPE_REAL32 # Data type (float)
)

# --- START COMMUNICATION ---

# Step A: Send Read Request
print(f"Reading {TARGET_PARAM}...")
vehicle.mav.send(read_msg)

# Step B: Wait for the answer
while True:
    msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    if msg:
        # We use .strip() to remove hidden null bytes (\x00) from the 16-byte buffer
        if msg.param_id.strip() == TARGET_PARAM:
            print(f"Step 1 Success: Current value is {msg.param_value}")
            break

# Step C: Send Set Request (Change it!)
print(f"Changing {TARGET_PARAM} to 0...")
vehicle.mav.send(set_msg)

# Step D: Wait for confirmation (Drone always sends a PARAM_VALUE after a SET)
while True:
    msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    if msg:
        if msg.param_id.strip() == TARGET_PARAM:
            print(f"Step 2 Success: New value confirmed as {msg.param_value}")
            break

print("All done! Check MAVProxy now.")


# dont forget to enable it again after finishing and testing your code param set BATT_MONITOR 0


















#the parameter SYSID_THISMAV is changed in higher version


# import pymavlink.mavutil as utility
# import pymavlink.dialects.v20.all as dialect

# SYSID_THISMAV= "SYSID_THISMAV"
# # connect to vehicle
# vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
# # vehicle.wait_heartbeat()
# # print("connected to system: ", vehicle.target_system , "component:",vehicle.target_component)


# #parameter request list
# parameter_request_list_message =dialect.MAVLink_param_request_list_message(target_system=vehicle.target_system,
#                                                                            target_component=vehicle.target_component)


# #parameter request

# parameter_request_message = dialect.MAVLink_param_request_read_message(
#     target_system=vehicle.target_system,
#     target_component=vehicle.target_component,
#     param_id=SYSID_THISMAV.encode("utf-8"),
#     param_index=-1
# )


# #param set msg
# parameter_set_message = dialect.MAVLink_param_set_message(
#     target_system=vehicle.target_system,
#     target_component=vehicle.target_component,
#     param_id=SYSID_THISMAV.encode("utf-8"),
#     param_value=2,
#     param_type=dialect.MAV_PARAM_TYPE_REAL32
# )

# vehicle.wait_heartbeat()
# print("connected to system: ", vehicle.target_system , "component:",vehicle.target_component)

# # send param request list message to the vehicle
# ### vehicle.mav.send(parameter_request_list_message)

# # send param request message to the vehicle
# vehicle.mav.send(parameter_request_message)


# # do below always
# while True:

#     # receive parameter value messages
#     message = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)

#     # convert message to dictionary
#     message = message.to_dict()

#     # filter only system id param value message
#     if message["param_id"] == SYSID_THISMAV:

#         # print the message to the screen
#         print(message["param_id"], message["param_value"])

#         # break this loop
#         break

# # send param set message to the vehicle
# vehicle.mav.send(parameter_set_message)

# # do below always
# while True:

#     # receive parameter value messages
#     message = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)

#     # convert message to dictionary
#     message = message.to_dict()

#     # filter only system id param value message
#     if message["param_id"] == SYSID_THISMAV:

#         # print the message to the screen
#         print(message["param_id"], message["param_value"])

#         # break this loop
#         break















# import pymavlink.mavutil as utility
# import pymavlink.dialects.v20.all as dialect
# import time

# # Parameter we are interested in
# PARAM_NAME = "SYSID_THISMAV"

# # 1. Connect to the vehicle (Simulation or Real)
# vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# # 2. Wait for the first heartbeat to confirm connection
# vehicle.wait_heartbeat()
# print(f"Connected to System {vehicle.target_system}. Starting Test...")

# # --- PREPARE THE MESSAGES ---

# # MESSAGE A: Request the FULL list (This will trigger ~1000 messages from drone)
# request_list_msg = dialect.MAVLink_param_request_list_message(
#     target_system=vehicle.target_system,
#     target_component=vehicle.target_component
# )

# # MESSAGE B: Request only ONE specific parameter
# request_single_msg = dialect.MAVLink_param_request_read_message(
#     target_system=vehicle.target_system,
#     target_component=vehicle.target_component,
#     param_id=PARAM_NAME.encode("utf-8"), # Convert string to 16-byte format
#     param_index=-1 # Search by name ID
# )

# # --- EXECUTION ---

# # First: Send the LIST request
# print("!!! Sending REQUEST_LIST now. Watch the traffic !!!")
# vehicle.mav.send(request_list_msg)

# # Second: Send the SINGLE request (It will get lost in the middle of the list)
# vehicle.mav.send(request_single_msg)

# # This counter will help us see how many parameters the drone actually sends
# count = 0

# while True:
#     try:
#         # Receive any parameter value message
#         msg = vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
        
#         if msg:
#             count += 1
#             msg_dict = msg.to_dict()
#             p_id = msg_dict["param_id"]
#             p_val = msg_dict["param_value"]
            
#             # Print every parameter that arrives from the list
#             print(f"[{count}] Received Param: {p_id} = {p_val}")

#             # If we find our specific target, highlight it
#             if p_id == PARAM_NAME:
#                 print(f" >>> FOUND TARGET: {p_id} is currently {p_val} <<< ")
#                 # We won't 'break' yet, let's see how many more are coming!
            
#             # If the count reaches a high number, we can stop
#             if count >= 100: # I set it to 100 so it doesn't run forever in this example
#                 print(f"\nStopped after receiving {count} parameters to show you the 'List' effect.")
#                 break

#     except KeyboardInterrupt:
#         break

# print("\nTest Finished. You saw that 'Request List' sends everything, not just what we need.")