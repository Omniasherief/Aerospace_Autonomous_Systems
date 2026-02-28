import time
import drone_setup
drone_setup.fix_compatibility()
import dronekit

# --- CONNECTION PHASE ---
print("Trying to connect to the vehicle...")
# Create a 'Vehicle' Object. wait_ready ensures all attributes are synchronized.
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("Connected to the vehicle.")

# Allow telemetry (data flow) to settle
time.sleep(5)

# Accessing Nested Attributes: vehicle (Object) -> location -> global_relative_frame -> alt
print("Altitude before calibration: ", vehicle.location.global_relative_frame.alt)

# --- CALIBRATION PHASE (Calling Methods) ---
# We use time.sleep(2) between methods to avoid "TEMPORARILY_REJECTED" errors from the CPU.

# Method 1: Reset Barometer (Altitude)
vehicle.send_calibrate_barometer()
print("Requested barometer calibration")
time.sleep(2) 

# Method 2: Calibrate Accelerometer (Gravity/Force)
vehicle.send_calibrate_accelerometer()
print("Requested accelerometer calibration")
time.sleep(2) 

# Method 3: Calibrate Gyroscope (Rotation)
vehicle.send_calibrate_gyro()
print("Requested gyroscope calibration")
time.sleep(2) 

# Method 4: Calibrate Magnetometer (Compass)
vehicle.send_calibrate_magnetometer()
print("Requested magnetometer calibration")
time.sleep(2) 

# Method 5: Set Vehicle Level (Horizon)
vehicle.send_calibrate_vehicle_level()
print("Requested vehicle level calibration")
time.sleep(2) 

# --- POST-CALIBRATION MONITORING ---
time.sleep(5) # Wait for final calibration processing
print("Altitude after calibration: ", vehicle.location.global_relative_frame.alt)

# --- CLEANUP ---
print("Closing the vehicle...")
# Method: Close the connection object to free the port
vehicle.close()
print("Closed the vehicle.")