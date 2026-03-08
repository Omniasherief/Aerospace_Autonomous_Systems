import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# create mission item list
## Waypoints to visit (Lat, Lon, Alt)
target_locations = ((-35.361297, 149.161120, 50.0),
                    (-35.360780, 149.167151, 50.0),
                    (-35.365115, 149.167647, 50.0),
                    (-35.364419, 149.161575, 50.0))
# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

#inform drone how many items we are uploading
#count for waypoints
#count=len(target_locations)+2 #as 0 home location , 1 takeooff 
message=dialect.MAVLink_mission_count_message(target_system=vehicle.target_system,
                                                target_component=vehicle.target_component,
                                                count=len(target_locations)+2,
                                                mission_type=dialect.MAV_MISSION_TYPE_MISSION)

# send mission count message to the vehicle
vehicle.mav.send(message)
# this loop will run until receive a valid MISSION_ACK message

"""
MISSION UPLOAD HANDSHAKE LOGIC:
1. The script waits for a message from the vehicle (Drone).
2. If 'MISSION_REQUEST': The drone is asking for a specific waypoint (seq).
   - The script identifies the sequence number and sends the corresponding 
     mission item (Home, Takeoff, or Waypoint).
3. If 'MISSION_ACK': The drone has received all items.
   - The script checks if 'MAV_MISSION_ACCEPTED' is returned to confirm 
     a successful upload and breaks the loop.
"""
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

            seq=message["seq"]
            ## [script -> DRONE] : Prepare the data based on what the drone asked for
            if seq==0:
                # create mission item int message that contains the home location (0th mission item)
                message = dialect.MAVLink_mission_item_int_message(target_system=vehicle.target_system,
                                                                   target_component=vehicle.target_component,
                                                                   seq=seq,
                                                                   frame=dialect.MAV_FRAME_GLOBAL,
                                                                   command=dialect.MAV_CMD_NAV_WAYPOINT,
                                                                   current=0,
                                                                   autocontinue=0,
                                                                   param1=0,
                                                                   param2=0,
                                                                   param3=0,
                                                                   param4=0,
                                                                   x=0,
                                                                   y=0,
                                                                   z=0,
                                                                   mission_type=dialect.MAV_MISSION_TYPE_MISSION)
             # send takeoff mission item
            elif seq==1 :

                # create mission item int message that contains the takeoff command
                message = dialect.MAVLink_mission_item_int_message(target_system=vehicle.target_system,
                                                                   target_component=vehicle.target_component,
                                                                   seq=seq,
                                                                   frame=dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                   command=dialect.MAV_CMD_NAV_TAKEOFF,
                                                                   current=0,
                                                                   autocontinue=0,
                                                                   param1=0,
                                                                   param2=0,
                                                                   param3=0,
                                                                   param4=0,
                                                                   x=0,
                                                                   y=0,
                                                                   z=target_locations[0][2],
                                                                   mission_type=dialect.MAV_MISSION_TYPE_MISSION)                                                 
            else:

                # create mission item int message that contains a target location
                message = dialect.MAVLink_mission_item_int_message(target_system=vehicle.target_system,
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
                                                                   x=int(target_locations[seq - 2][0] * 1e7),
                                                                   y=int(target_locations[seq - 2][1] * 1e7),
                                                                   z=target_locations[seq - 2][2], mission_type=dialect.MAV_MISSION_TYPE_MISSION)
        # send the mission item int message to the vehicle
        ## IMPORTANT: SEND the item we just created!
        vehicle.mav.send(message)
        # check this message is MISSION_ACK
    elif message["mavpackettype"] == dialect.MAVLink_mission_ack_message.msgname:

        # check this acknowledgement is for mission and it is accepted
        if message["mission_type"] == dialect.MAV_MISSION_TYPE_MISSION and \
                message["type"] == dialect.MAV_MISSION_ACCEPTED:
            # break the loop since the upload is successful
            print("Mission upload is successful")
            break                                                        