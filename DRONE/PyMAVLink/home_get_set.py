'''    
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# new home location
new_home_location = (-35.36210556, 149.16373661, 583.9)

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

"""
# create home position request message
command = dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
                                               target_component=vehicle.target_component,
                                               command=dialect.MAV_CMD_SET_MESSAGE_INTERVAL,
                                               confirmation=0,
                                               param1=dialect.MAVLINK_MSG_ID_HOME_POSITION,
                                               param2=1e6,
                                               param3=0,
                                               param4=0,
                                               param5=0,
                                               param6=0,
                                               param7=0)

# send command to the vehicle
vehicle.mav.send(command)
"""

# create set home position command
command = dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
                                               target_component=vehicle.target_component,
                                               command=dialect.MAV_CMD_DO_SET_HOME,
                                               confirmation=0,
                                               param1=0,
                                               param2=0,
                                               param3=0,
                                               param4=0,
                                               param5=new_home_location[0],
                                               param6=new_home_location[1],
                                               param7=new_home_location[2])

# send command to the vehicle
vehicle.mav.send(command)

# infinite loop
while True:

    # get HOME_POSITION message
    message = vehicle.recv_match(type=dialect.MAVLink_home_position_message.msgname,
                                 blocking=True)

    # convert this message to dictionary
    message = message.to_dict()

    # debug the message
    print("Home Position >",
          "Latitude:", message["latitude"] * 1e-7,
          "Longitude:", message["longitude"] * 1e-7,
          "Altitude:", message["altitude"] * 1e-3)

    """
    # disable HOME_POSITION message stream
    command = dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
                                                   target_component=vehicle.target_component,
                                                   command=dialect.MAV_CMD_SET_MESSAGE_INTERVAL,
                                                   confirmation=0,
                                                   param1=dialect.MAVLINK_MSG_ID_HOME_POSITION,
                                                   param2=-1,
                                                   param3=0,
                                                   param4=0,
                                                   param5=0,
                                                   param6=0,
                                                   param7=0)

    # send command to the vehicle
    vehicle.mav.send(command)
    """


''' 

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# New home coordinates (Canberra SITL Area)
new_home_location = (-35.363261, 149.165230, 40.0)

# Connect to SITL and wait for heartbeat
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print(f"Connected: System {vehicle.target_system}")

# 1. Enable HOME_POSITION stream every 1 second (1e6 us)
request_stream = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_SET_MESSAGE_INTERVAL,
    confirmation=0,
    param1=dialect.MAVLINK_MSG_ID_HOME_POSITION,
    param2=1e6, 
    param3=0, param4=0, param5=0, param6=0, param7=0)
vehicle.mav.send(request_stream)

# 2. Set new Home location (p5=Lat, p6=Lon, p7=Alt)
set_home_cmd = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_SET_HOME,
    confirmation=0,
    param1=0, 
    param2=0, param3=0, param4=0,
    param5=new_home_location[0],
    param6=new_home_location[1],
    param7=new_home_location[2])
vehicle.mav.send(set_home_cmd)

# 3. Monitoring Loop: Receive and verify update
print("Verifying home update...")
while True:
    message = vehicle.recv_match(type=dialect.MAVLink_home_position_message.msgname, blocking=True)
    msg_dict = message.to_dict()

    # Scaling: Lat/Lon * 1e-7, Alt * 1e-3 (mm to m)
    current_lat = msg_dict['latitude'] * 1e-7
    current_lon = msg_dict['longitude'] * 1e-7
    current_alt = msg_dict['altitude'] * 1e-3

    print(f"Current Home: {current_lat:.6f}, {current_lon:.6f}, {current_alt:.2f}m")

    # Exit loop once Latitude matches target
    if abs(current_lat - new_home_location[0]) < 0.00001:
        print("Home updated successfully!")
        break

# 4. Disable HOME_POSITION stream (param2 = -1)
stop_stream = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_SET_MESSAGE_INTERVAL,
    confirmation=0,
    param1=dialect.MAVLINK_MSG_ID_HOME_POSITION,
    param2=-1, 
    param3=0, param4=0, param5=0, param6=0, param7=0)
vehicle.mav.send(stop_stream)