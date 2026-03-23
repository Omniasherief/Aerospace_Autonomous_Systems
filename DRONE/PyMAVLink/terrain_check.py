# ----------------------------------------------------------------------------------
# TERRAIN DATA CHECKING LOGIC:
# ----------------------------------------------------------------------------------
# Terrain Following: Allows the drone to maintain a safe height above ground level.
# MAVLink_terrain_check_message: Asks the drone if it has altitude data for a specific Lat/Lon.
# MAVLink_terrain_report_message: The drone's response containing the ground elevation.
#
# Key Fields in Report:
# - lat/lon: Location coordinates (scaled by 10^7).
# - terrain_height: Absolute height of the ground at this location (meters).
# - spacing: The resolution of the terrain grid data.
# ----------------------------------------------------------------------------------

import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect


# define the location
#mansoura in egypt

terrain_location=(31.0409,31.3785)
terrain_location=(int(terrain_location[0]*1e7), int (terrain_location[1]*1e7))

print("Terrain location (lat, lon):", terrain_location)


vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)


message=dialect.MAVLink_terrain_check_message(lat=terrain_location[0], lon=terrain_location[1])

# send the message to the vehicle
vehicle.mav.send(message)
while True:

    # capture TERRAIN_REPORT messages
    message = vehicle.recv_match(type=dialect.MAVLink_terrain_report_message.msgname,
                                 blocking=True)

    # convert the captured message to dictionary
    message = message.to_dict()

    # check the message is specifically sent for our terrain location
    if message["lat"] == terrain_location[0] and message["lon"] == terrain_location[1]:
        break

# print the capture message
print(message)