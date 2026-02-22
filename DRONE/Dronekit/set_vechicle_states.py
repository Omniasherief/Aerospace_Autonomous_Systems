import time
import drone_setup
drone_setup.fix_compatibility()
import dronekit

#connecting to virtual drone on the local machine
print("Trying to connect to the vehicle ....")
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("conect to the vehicle")


# arm the vehicle
vehicle.armed = True
print("Sent arm command.")

time.sleep(5)
print("Arm status:", vehicle.armed)

# disarm the vehicle
vehicle.armed = False
print("Sent disarm command.")

time.sleep(5)
print("Arm status:", vehicle.armed)



# --- Landing Section ---
print("Changing mode to LAND...")

# Change mode to LAND
vehicle.mode = dronekit.VehicleMode("LAND")

# Wait until the vehicle is no longer armed (Touchdown)
while vehicle.armed:
    print(f" Landing... Current Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("Drone has landed and disarmed successfully.")



# change flight mode
vehicle.mode = dronekit.VehicleMode("GUIDED")
print("Sent change mode command.")
time.sleep(5)
print("Vehicle mode:", vehicle.mode.name)

# 1. Wait until the vehicle is armable
while not vehicle.is_armable:
    print(" Waiting for vehicle to be armable (GPS lock)...")
    time.sleep(1)

# 2. Arm the vehicle
vehicle.armed = True
while not vehicle.armed:
    print(" Waiting for arming...")
    time.sleep(1)

print("MOTORS ARMED! TAKING OFF...")

# 3. Takeoff
vehicle.simple_takeoff(20.0) 

# 4. VERY IMPORTANT: Stay connected to watch the altitude rise
while True:
    altitude = vehicle.location.global_relative_frame.alt
    print(f" Current Altitude: {altitude:.2f}m")
    if altitude >= 20.0 * 0.95: # Reach 95% of target
        print("Reached target altitude!")
        break
    time.sleep(1)

print("Hovering for 5 seconds before closing...")
time.sleep(5)

print("Closing the vehicle...")
vehicle.close()