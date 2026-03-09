
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)
vehicle.mav.send(dialect.MAVLink_mission_request_list_message(
    vehicle.target_system,
    vehicle.target_component,
    dialect.MAV_MISSION_TYPE_MISSION 
))
message=vehicle.recv_match(type=dialect.MAVLink_mission_count_message.msgname,blocking=True)
message = message.to_dict()

count=message["count"]
print("Total mission item count ::", count)

# create mission clear all message
message = dialect.MAVLink_mission_clear_all_message(target_system=vehicle.target_system,
                                                    target_component=vehicle.target_component,
                                                    mission_type=dialect.MAV_MISSION_TYPE_MISSION)

# send mission clear all command to the vehicle
vehicle.mav.send(message)

# create mission request list message
message = dialect.MAVLink_mission_request_list_message(target_system=vehicle.target_system,
                                                       target_component=vehicle.target_component,
                                                       mission_type=dialect.MAV_MISSION_TYPE_MISSION)

# send the message to the vehicle
vehicle.mav.send(message)

# wait mission count message
message = vehicle.recv_match(type=dialect.MAVLink_mission_count_message.msgname,
                             blocking=True)

# convert this message to dictionary
message = message.to_dict()

# get the mission item count
count = message["count"]
print("Total mission item count:", count)