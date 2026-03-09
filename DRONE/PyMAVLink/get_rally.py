import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# introduce RALLY_TOTAL as byte array and do not use parameter index
RALLY_TOTAL = "RALLY_TOTAL".encode(encoding="utf-8")
PARAM_INDEX = -1

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
# wait for a heartbeat
vehicle.wait_heartbeat()
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

# create PARAM_REQUEST_READ message
message=dialect.MAVLink_param_request_read_message(vehicle.target_system,
                                                   vehicle.target_component,
                                                    param_id=RALLY_TOTAL,
                                                    param_index=PARAM_INDEX)
print(message)
vehicle.mav.send(message)
# receive PARAM_VALUE message until get RALLY_TOTAL value
while True:
    
    message=vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking=True)
    print(message)
    message = message.to_dict()
    if message["param_id"] == "RALLY_TOTAL":
    # get total rally point count number
        rally_count = int(message["param_value"])

        # break the loop
        break
     #debug rally count
print("Total rally item count:", rally_count)

# create rally point item list
rally_list = []

for idx in range(rally_count):
     # create RALLY_FETCH_POINT message
    message = dialect.MAVLink_rally_fetch_point_message(target_system=vehicle.target_system,
                                                        target_component=vehicle.target_component,
                                                        idx=idx)

    # send this message to vehicle
    vehicle.mav.send(message)

    # wait until receive RALLY_POINT message
    message = vehicle.recv_match(type=dialect.MAVLink_rally_point_message.msgname,
                                 blocking=True)

    # convert the message to dictionary
    message = message.to_dict()

    # append the rally point to the list
    rally_list.append((message["lat"] * 1e-7, message["lng"] * 1e-7, message["alt"]))

# for each rally point item
for rally_item in rally_list:
    # debug rally item
    print("Latitude:", rally_item[0], "Longitude:", rally_item[1], "Altitude:", rally_item[2])
