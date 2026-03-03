
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()
# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

request_message_command= dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_REQUEST_MESSAGE,
    confirmation=0,
    param1=dialect.MAVLINK_MSG_ID_AUTOPILOT_VERSION,
    param2=0,param3=0,param4=0,param5=0,param6=0,param7=0
)

#send command to the vehicle
vehicle.mav.send(request_message_command)

while True :
    #catch the msg
    msg=vehicle.recv_match(type=dialect.MAVLink_autopilot_version_message.msgname,blocking=True)
     # convert the message to dictionary
    msg = msg.to_dict()
    print(msg)
    #| Byte 3 | Byte 2 | Byte 1 | Byte 0 |
    #  Major  | Minor  | Patch  |  Dev   |
    # right shift -- masking

    print("major:", msg["flight_sw_version"] >> 24 & 0xFF)
    print("minor:", msg["flight_sw_version"] >> 16 & 0xFF)
    print("Patch:", msg["flight_sw_version"] >> 8 & 0xFF)

    # Convert MAVLink flight_custom_version (uint8[8]) from bytes to ASCII string
    print("hash: ", "".join([chr(i)for i in msg["flight_custom_version"]]))
    

#ArduPilot 4.7.0  
#major: 4
#minor: 7
#Patch: 0
#hash:  a667b8f8

