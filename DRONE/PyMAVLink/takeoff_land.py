import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

#arm throttle maunal then run this 
# --- Global Configurations ---
# Target altitude in meters
TAKEOFF_ALTITUDE = 50
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# Wait for the first heartbeat to ensure the vehicle is active before sending commands
vehicle.wait_heartbeat()
print(f"Connected to system: {vehicle.target_system}, component: {vehicle.target_component}")

takeoff_command=dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
    target_component=vehicle.target_component,command=dialect.MAV_CMD_NAV_TAKEOFF,confirmation=0,
    param1=0, param2=0, param3=0, param4=0, param5=0, param6=0,
    param7=TAKEOFF_ALTITUDE)

land_command = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_NAV_LAND,
    confirmation=0,
    param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0
)

# Send the takeoff command to the flight controller
vehicle.mav.send(takeoff_command)

print("Sent takeoff command to vehicle")
while True:
    msg=vehicle.recv_match(type=dialect.MAVLink_global_position_int_message.msgname, blocking=True)
    data = msg.to_dict()
    # Convert relative altitude from millimeters to meters (1e-3 = 0.001)
    relative_altitude = data["relative_alt"] * 1e-3
    print(f"Current Altitude: {relative_altitude:.2f} meters")
    # Check if the drone has reached the target altitude (within 1-meter tolerance)
    if TAKEOFF_ALTITUDE - relative_altitude < 1:
        print(f"Takeoff to {TAKEOFF_ALTITUDE} meters successful!")
        break

# --- Pause ---
# Let the drone hover for 10 seconds
print("Hovering for 10 seconds...")
time.sleep(10)

# Send the landing command
vehicle.mav.send(land_command)
print("Sent land command to vehicle")

# Monitoring loop for landing
while True:
    message = vehicle.recv_match(type=dialect.MAVLink_global_position_int_message.msgname, blocking=True)
    data = message.to_dict()
    relative_altitude = data["relative_alt"] * 1e-3

    print(f"Landing... Altitude: {relative_altitude:.2f} meters")

    # If altitude is near zero (less than 1 meter), consider it landed
    if relative_altitude < 1:
        print("Vehicle reached ground level.")
        break

# Final wait for physical landing and disarming
time.sleep(10)
print("Landed successfully")








# another simple way 


'''

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# Configuration
TAKEOFF_ALTITUDE = 10
VEHICLE_ARM = 1
VEHICLE_DISARM = 0

vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print("Connected!")

# 1. Set Mode to GUIDED
# Using the direct send method
vehicle.mav.set_mode_send(
    vehicle.target_system,
    dialect.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4 # 4 is GUIDED in ArduPilot
)

# 2. Arm the Vehicle
# We use the direct send method here for simplicity
vehicle.mav.command_long_send(
    vehicle.target_system,
    vehicle.target_component,
    dialect.MAV_CMD_COMPONENT_ARM_DISARM,
    0,           # confirmation
    VEHICLE_ARM, # param1: 1 to arm
    0, 0, 0, 0, 0, 0 # unused params
)

# 3. CRITICAL STEP: Wait for the vehicle to be Armed
print("Waiting for motors to arm...")
while True:
    # Wait for a HEARTBEAT message to check system status
    msg = vehicle.recv_match(type='HEARTBEAT', blocking=True)
    # Check if the armed flag is set in the system status
    is_armed = msg.base_mode & dialect.MAV_MODE_FLAG_SAFETY_ARMED
    if is_armed:
        print("Vehicle is ARMED and ready!")
        break
    time.sleep(1)

# 4. Now Send Takeoff Command
print("Taking off...")
vehicle.mav.command_long_send(
    vehicle.target_system,
    vehicle.target_component,
    dialect.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0,
    TAKEOFF_ALTITUDE # param7
)

# 5. Monitor Altitude
while True:
    message = vehicle.recv_match(type=dialect.MAVLink_global_position_int_message.msgname, blocking=True)
    relative_altitude = message.relative_alt * 1e-3
    print(f"Current Altitude: {relative_altitude:.2f} meters")

    if relative_altitude >= TAKEOFF_ALTITUDE * 0.95: # 95% of target
        print("Reached target altitude!")
        break

# ... Proceed to land or wait









'''