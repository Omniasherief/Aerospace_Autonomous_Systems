import drone_setup
# Apply the compatibility fix for Python 3.10+
drone_setup.fix_compatibility()

import dronekit
import time

# --- Connection Section ---
# Connect to the local SITL simulator
print("Trying to connect to the vehicle...")
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("Connected Successfully!")

# --- Setup Parameters ---
# Set the speed for the mission (m/s)
vehicle.airspeed = 5.0
vehicle.groundspeed = 5.0
print(f"Speeds set to: Air={vehicle.airspeed}, Ground={vehicle.groundspeed}")

# --- Mode Change Section ---
# Change flight mode to GUIDED
# The drone must be in GUIDED mode to accept computer commands
vehicle.mode = dronekit.VehicleMode("GUIDED")
while not vehicle.mode.name == 'GUIDED':
    print("Waiting for GUIDED mode...")
    time.sleep(1)
print("Vehicle is now in GUIDED mode.")

# --- Arming Section ---
# Arming means starting the motors
# We check if the vehicle is "armable" (GPS lock, healthy sensors)
while not vehicle.is_armable:
    print("Waiting for vehicle to initialize (GPS lock, etc.)...")
    time.sleep(1)

print("Arming motors...")
vehicle.armed = True

# Wait until the vehicle reports that it is armed
while not vehicle.armed:
    print("Waiting for arming...")
    time.sleep(1)
print("MOTORS ARMED!")

# --- Takeoff Section ---
target_altitude = 10.0
print(f"Taking off to {target_altitude} meters...")
# simple_takeoff sends the command to climb
vehicle.simple_takeoff(target_altitude)

# --- Monitoring Loop ---
# Monitor altitude during climb
while True:
    current_altitude = vehicle.location.global_relative_frame.alt
    print(f" Current Altitude: {current_altitude:.2f}m")
    
    # Break the loop when target altitude is reached (within 5% margin)
    if current_altitude >= target_altitude * 0.95:
        print("Reached target altitude.")
        break
    time.sleep(1)

# --- Landing Section ---
print("Hovering for 5 seconds...")
time.sleep(5)

print("Changing mode to LAND...")
vehicle.mode = dronekit.VehicleMode("LAND")

# Wait for the drone to touch the ground
while vehicle.armed:
    print(f" Landing... Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

# --- Shutdown Section ---
print("Drone has landed and disarmed.")
vehicle.close()
print("Connection closed.")