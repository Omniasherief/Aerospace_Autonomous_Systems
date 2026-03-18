import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

RALLY_TOTAL="RALLY_TOTAL".encode(encoding="utf-8")
PARAM_INDEX=-1
# create rally point item list
rally_list = [(-35.361235, 149.161052, 40.000000),
              (-35.362089, 149.164452, 40.000000),
              (-35.364099, 149.161712, 40.000000),
              (-35.363649, 149.166642, 40.000000),
              (-35.359978, 149.168170, 40.000000)]


# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

while True:
    message=dialect.MAVLink_param_set_message(target_system=vehicle.target_system,
                                               target_component=vehicle.target_component,
                                               param_id=RALLY_TOTAL,
                                               param_value=len(rally_list),
                                               param_type=dialect.MAV_PARAM_TYPE_REAL32)

    vehicle.mav.send(message)
    message=vehicle.recv_match(type=dialect.MAVLink_param_value_message.msgname, blocking =True)
    message=message.to_dict()
    if message["param_id"]=="RALLY_TOTAL":
        if int(message["param_value"])==len(rally_list):
            print("RALLY_POINT set to {0} Sucessfully".format(len(rally_list)))
            break
        else:
            print("Failed to set RALLY_TOTAL to {0}".format(len(rally_list)))

idx = 0

while idx < len(rally_list):
    message=dialect.MAVLink_rally_point_message(target_system=vehicle.target_system,
                                                  target_component=vehicle.target_component,
                                                  idx=idx,
                                                  count=len(rally_list),
                                                  lat=int(rally_list[idx][0] * 1e7),
                                                  lng=int(rally_list[idx][1] * 1e7),
                                                  alt=int(rally_list[idx][2]),
                                                  break_alt=0,
                                                  land_dir=0,
                                                  flags=0)
     # send RALLY_POINT message to the vehicle
    vehicle.mav.send(message)

     # create RALLY_FETCH_POINT message
    message = dialect.MAVLink_rally_fetch_point_message(target_system=vehicle.target_system,
                                                        target_component=vehicle.target_component,
                                                        idx=idx)

    # send this message to vehicle
    vehicle.mav.send(message)

    # wait for RALLY_POINT message
    message = vehicle.recv_match(type=dialect.MAVLink_rally_point_message.msgname,
                                 blocking=True)

    # convert the message to dictionary
    message = message.to_dict()
    
    if message["idx"]==idx and message["count"] == len(rally_list) and \
       message["lat"] == int(rally_list[idx][0] * 1e7) and \
       message["lng"] == int(rally_list[idx][1] * 1e7) and \
       message["alt"] == int(rally_list[idx][2]):
    
        # increment rally point item index counter
        idx += 1
         # inform user
        print("Rally point {0} uploaded successfully".format(idx))
    # should send RALLY_POINT message again
    else:
        print("Failed to upload rally point {0}".format(idx))

print("All the rally point items uploaded successfully")