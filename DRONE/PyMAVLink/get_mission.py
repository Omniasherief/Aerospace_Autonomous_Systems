#~/ardu-sim$ mavproxy.py --master=127.0.0.1:14550 
#wp load way.txt
'''
This script mimics the MAVProxy 'wp list' command by:
1. Sending MISSION_REQUEST_LIST (Asking for count)
2. Handling MISSION_COUNT (Getting total items)
3. Requesting individual MISSION_ITEM_INT (Downloading data)
'''

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

#mission request list message
message=dialect.MAVLink_mission_request_list_message(target_system=vehicle.target_system,
                                                       target_component=vehicle.target_component,
                                                       mission_type=dialect.MAV_MISSION_TYPE_MISSION)
# send the message to the vehicle
vehicle.mav.send(message)
#wait mission count the message
message=vehicle.recv_match(type=dialect.MAVLink_mission_count_message.msgname, blocking =True)
# convert this message to dictionary
message = message.to_dict()
# get the mission item count
count = message["count"]
print("Total mission item count:", count)

# ,ission item list
mission_item_list=[]
for i in range (count) :
    message=dialect.MAVLink_mission_request_int_message(target_system=vehicle.target_system,
                                                          target_component=vehicle.target_component,
                                                          seq=i,
                                                          mission_type=dialect.MAV_MISSION_TYPE_MISSION)
    
    # send mission request int message to the vehicle
    vehicle.mav.send(message)

    # wait mission item int message
    message = vehicle.recv_match(type=dialect.MAVLink_mission_item_int_message.msgname,
                                 blocking=True)

    # convert this message to dictionary
    message = message.to_dict()
    # add mission item to the list
    mission_item_list.append(message)

# print mission items
for mission_item in mission_item_list:
    print("Seq", mission_item["seq"],
          "Latitude", mission_item["x"] * 1e-7,
          "Longitude", mission_item["y"] * 1e-7,
          "Altitude", mission_item["z"])