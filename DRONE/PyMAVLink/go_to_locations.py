
"""
FLIGHT MISSION SEQUENCE:
1.  CONNECTION: Establish link with the vehicle (SITL/Drone).
2.  MODE CHANGE: Set mode to 'GUIDED' (Mandatory for computer-controlled flight).
3.  ARMING: Unlock the motors (ARM THROTTLE).
4.  TAKEOFF: Command the drone to climb to 10 meters.
5.  ALTITUDE CHECK: Wait until the drone reaches the takeoff altitude.
6.  NAVIGATION: Send the first GPS Waypoint (MISSION_ITEM_INT).
7.  DISTANCE MONITORING: Calculate real-time distance to target using Geopy.
8.  LOOPING: If distance < 1m, switch to the next target using Modulo (%).
"""
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
import geopy.distance


TARGET_LOCATIONS=[{"latitude":-35.36130812,"longitude": 149.16114736,
        "altitude": 30},{ "latitude": -35.36579988,
        "longitude": 149.16302080,
        "altitude": 40}]

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)
# vehicle's current location
current_location = {
    "latitude": 0.0,
    "longitude": 0.0
}
# vehicle's target location
target_location = {
    "latitude": 0.0,
    "longitude": 0.0,
    "distance": 0.0
}




'''
# Set vehicle speed in GUIDED mode
vehicle.mav.command_long_send(
    vehicle.target_system,    # target_system
    vehicle.target_component, # target_component
    dialect.MAV_CMD_DO_CHANGE_SPEED, # command ID: 178
    0,          # confirmation
    0,          # param1: Speed type (0=Ground speed, 1=Airspeed)
    10,         # param2: Speed value in m/s (e.g., 10 meters per second)
    -1,         # param3: Throttle (-1 = no change)
    0,          # param4: Relative (0=Absolute, 1=Relative)
    0, 0, 0     # params 5, 6, 7 (unused)
)

'''
message=dialect.MAVLink_mission_item_int_message(target_system=vehicle.target_system,
                                                target_component=vehicle.target_component,
                                                seq=0,
                                                frame=dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                                                command=dialect.MAV_CMD_NAV_WAYPOINT,
                                                current=2,
                                                autocontinue=0,
                                                param1=0,
                                                param2=0,
                                                param3=0,
                                                param4=0,
                                                x=int(TARGET_LOCATIONS[0]["latitude"]* 1e7),
                                                y=int(TARGET_LOCATIONS[0]["longitude"] * 1e7),
                                                z=TARGET_LOCATIONS[0]["altitude"]      )

vehicle.mav.send(message)
target_counter=0

while True:
    #catch a message
    message=vehicle.recv_match(type=[dialect.MAVLink_position_target_global_int_message.msgname,
                                       dialect.MAVLink_global_position_int_message.msgname],
                                 blocking=True)
    
    message = message.to_dict()
    # get vehicle's current location
    if message["mavpackettype"] == dialect.MAVLink_global_position_int_message.msgname:
        current_location["latitude"] = message["lat"] * 1e-7
        current_location["longitude"] = message["lon"] * 1e-7
         # debug message
        print("Vehicle current location",
              "Latitude:", current_location["latitude"],
              "Longitude:", current_location["longitude"])
    # get vehicle's target location
    if message["mavpackettype"] == dialect.MAVLink_position_target_global_int_message.msgname:
        target_location["latitude"] = message["lat_int"] * 1e-7
        target_location["longitude"] = message["lon_int"] * 1e-7
        
        #calc target location distance
        distance = geopy.distance.GeodesicDistance((current_location["latitude"],current_location["longitude"]),(target_location["latitude"],
                                                    target_location["longitude"])).meters
        
        target_location["distance"] = distance

        #reached target
        if distance <1:

            target_counter +=1
            #create target location message

            '''
            # Send a movement command to a specific GPS coordinate
vehicle.mav.command_int_send(
    vehicle.target_system,    # target_system
    vehicle.target_component, # target_component
    dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame: Use GPS but altitude relative to home
    dialect.MAV_CMD_NAV_WAYPOINT, # command ID: 16 (Navigation Waypoint)
    2,          # current: 2 means "Guided Mode" target (Go now!)
    0,          # autocontinue: 0 (not part of a stored mission)
    0,          # param1: Hold time at waypoint (seconds)
    0,          # param2: Acceptance radius (meters)
    0,          # param3: Pass radius (meters)
    0,          # param4: Yaw angle (0 = forward)
    int(TARGET_LAT * 1e7), # x: Latitude multiplied by 10^7
    int(TARGET_LON * 1e7), # y: Longitude multiplied by 10^7
    30          # z: Altitude in meters
)
            
            
            '''
            message =dialect.MAVLink_mission_item_int_message(
                target_system=vehicle.target_system,
                target_component=vehicle.target_component,
                seq=0,
                frame=dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                command=dialect.MAV_CMD_NAV_WAYPOINT,
                current=2,
                autocontinue=0,
                param1=0,
                param2=0,
                param3=0,
                param4=0,
                # target_counter starts at 0, 1, 2, 3...
                # TARGETS has 2 items [Point_A, Point_B]
                # target_counter % 2 will ALWAYS return 0 or 1
                # This creates a "Circular Index" to switch between targets forever
                #index = target_counter % len(TARGETS)
                x=int(TARGET_LOCATIONS[target_counter % 2]["latitude"] * 1e7),
                y=int(TARGET_LOCATIONS[target_counter % 2]["longitude"] * 1e7),
                z=TARGET_LOCATIONS[target_counter % 2]["altitude"]
            )
          # send target location command to the vehicle
            vehicle.mav.send(message)

     # debug message
    print("Vehicle target location",
        "Latitude:", target_location["latitude"],
        "Longitude:", target_location["longitude"],
        "Distance:", target_location["distance"])    