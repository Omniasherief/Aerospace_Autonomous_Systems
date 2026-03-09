import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

FENCE_TOTAL="FENCE_TOTAL".encode(encoding="utf-8")
# PARAM_INDEX = -1 tells the drone: "Ignore the numerical index, search by NAME instead."
# In MAVLink, if param_index is -1, the drone looks at 'param_id' (FENCE_TOTAL).
PARAM_INDEX = -1

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

param_request_read_message=dialect.MAVLink_param_request_read_message(target_system=vehicle.target_system,
                                                                        target_component=vehicle.target_component,
                                                                        param_id=FENCE_TOTAL,
                                                                        param_index=PARAM_INDEX)

# send PARAM_REQUEST_READ message to vehicle
vehicle.mav.send(param_request_read_message)

# receive PARAM_VALUE message until get FENCE_TOTAL value
while True:
    message=vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname,blocking =True)
    # convert the message to dictionary
    message = message.to_dict()
    if message["param_id"]=="FENCE_TOTAL":
         # check this parameter value message is for FENCE_TOTAL
        fence_count=int(message["param_value"])
        
        break
# debug fence count
print("Total fence item count:", fence_count)

# create fence item list
fence_list = [] 
#create for loop to get the fence items
for idx in range(fence_count):

    # create FENCE_FETCH_POINT message
    '''
    message = dialect.MAVLink_fence_fetch_point_message(target_system=vehicle.target_system,
                                                        target_component=vehicle.target_component,
                                                        idx=idx
                                                        )
    '''
    # NEW LOGIC: We use mission_request_int because modern ArduPilot treats Fence as a Mission Type.
    # The 'seq' parameter is the index of the fence point we are requesting.
    message =  dialect.MAVLink_mission_request_int_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        seq=idx,
        mission_type=dialect.MAV_MISSION_TYPE_FENCE # This is the magic key
    )
    # send this message to vehicle
    vehicle.mav.send(message)
    
    '''
    # wait until receive FENCE_POINT message
    message = vehicle.recv_match(type=dialect.MAVLink_fence_point_message.msgname,
                                 blocking=True,timeout=2)
    '''

    # NEW LOGIC: When requesting with 'mission_request_int', the drone responds with 'MISSION_ITEM_INT'.
    # We added a 2-second timeout to prevent the script from hanging if a point doesn't exist.
    message = vehicle.recv_match(type=dialect.MAVLink_mission_item_int_message.msgname,
                                 blocking=True, timeout=2)
    
    if message is not None:
        message = message.to_dict()
        '''
        fence_list.append((message["lat"], message["lng"]))
         print(f"Fetched Point #{idx}: Lat={message['lat']}, Lng={message['lng']}")
        '''
        # NEW LOGIC: MISSION_ITEM_INT uses 'x' for Latitude and 'y' for Longitude.
        # Coordinates are sent as large Integers (e.g., -353613165).
        # We divide by 10,000,000 (1e7) to restore the decimal point for degrees.
        lat = message["x"] / 1e7
        lng = message["y"] / 1e7
        fence_list.append((lat, lng))
        print(f"Fetched Point #{idx}: Lat={lat}, Lng={lng}")
    else:
        # If no message arrives within 2 seconds, the drone likely doesn't have more points.
        # This explains why you saw '9' in parameters but only '7' points in memory.
        print(f"Timeout: Drone did not send Point #{idx}")

# for each fence item
for fence_item in fence_list:
    # debug fence item
    print("Latitude:", fence_item[0], "Longitude:", fence_item[1])