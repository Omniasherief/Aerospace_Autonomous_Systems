
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

#partial mission list
target_locations={"3":(-35.36088422, 149.17235277, 50.0),"4":(-35.36547152, 149.17320997, 50.0)}
vehicle=utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print("connected to system: ", vehicle.target_system, " component",vehicle.target_component)

message=dialect.MAVLink_mission_write_partial_list_message(target_system=vehicle.target_system,
                                                             target_component=vehicle.target_component,
                                                             start_index=3,
                                                             end_index=4,
                                                             mission_type=dialect.MAV_MISSION_TYPE_MISSION)
vehicle.mav.send(message)

while True:
    message=vehicle.recv_match(type=['MISSION_REQUEST', 'MISSION_ACK'],blocking=True)
    #debugging
    print("Received Message:", message.get_type())
    # convert this message to dictionary
    message = message.to_dict()
    # check this message is MISSION_REQUEST
    if message["mavpackettype"]==dialect.MAVLink_mission_request_message.msgname:
        #check for mission items
        #
        if message["mission_type"]==dialect.MAV_MISSION_TYPE_MISSION:
            # get the sequence number of requested mission item
            seq = message["seq"]

            message=dialect.MAVLink_mission_item_int_message(target_system=vehicle.target_system,
                                                               target_component=vehicle.target_component,
                                                               seq=seq,
                                                               frame=dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                               command=dialect.MAV_CMD_NAV_WAYPOINT,
                                                               current=0,
                                                               autocontinue=0,
                                                               param1=0,
                                                               param2=0,
                                                               param3=0,
                                                               param4=0,
                                                               x=int(target_locations[str(seq)][0] * 1e7),
                                                               y=int(target_locations[str(seq)][1] * 1e7),
                                                               z=target_locations[str(seq)][2],
                                                               mission_type=dialect.MAV_MISSION_TYPE_MISSION)

            # send the mission item int message to the vehicle
            vehicle.mav.send(message)
        # check this message is MISSION_ACK
    elif message["mavpackettype"] == dialect.MAVLink_mission_ack_message.msgname:

        # check this acknowledgement is for mission and it is accepted
        if message["mission_type"] == dialect.MAV_MISSION_TYPE_MISSION and \
                message["type"] == dialect.MAV_MISSION_ACCEPTED:
            # break the loop since the upload is successful
            print("Mission upload is successful")
            break
