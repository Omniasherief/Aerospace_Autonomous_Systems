import time
import drone_setup
drone_setup.fix_compatibility()
import dronekit
import geopy.distance 

# --- CALLBACK FUNCTION ---
def location_callback(self, attribute_name, message):
    """
    This function triggers automatically every time the drone's GPS location changes.
    It updates the 'target_distance' attribute on the vehicle object.
    """
    global target_location 
    
    # GeodesicDistance calculates the distance over the earth's curved surface using Lat/Lon.
    # We use .meters to get the result in a readable format for our logic.
    distance = geopy.distance.GeodesicDistance(target_location,
                                                (self.location.global_relative_frame.lat,
                                                self.location.global_relative_frame.lon)).meters
    
    # Storing the calculated distance back into the vehicle object for use in the main loops.
    self.target_distance = distance


# Target coordinates: (Latitude, Longitude)
target_location = (-35.364262, 149.165637)

# --- CONNECTION ---
print("Trying to connect to the vehicle ....")
# Connecting to SITL (Simulator) on local IP. wait_ready=True ensures all attributes are loaded.
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("Connected to the vehicle")

# --- INITIALIZATION & PARAMETERS ---
vehicle.target_distance = -1.0 # Initialize with -1 until the first callback update
vehicle.add_attribute_listener("location", location_callback) # Start monitoring location

# RTL_ALT: Return To Launch Altitude. 
# 3000 cm = 30 meters. This is the safety height the drone climbs to before returning home.
vehicle.parameters["RTL_ALT"] = 3000 

# --- PRE-FLIGHT ---
# Switch to GUIDED mode to allow computer/script control.
while vehicle.mode.name != "GUIDED":
    vehicle.mode = dronekit.VehicleMode("GUIDED")
    time.sleep(1)

print("Vehicle mode:", vehicle.mode.name)

# Barometer Calibration: Sets the current air pressure as 'Zero' altitude.
# Essential for accurate altitude readings during takeoff and flight.
vehicle.send_calibrate_barometer()

# Wait for GPS lock and internal checks to pass.
while not vehicle.is_armable:
    print(" Waiting for vehicle to become armable...")
    time.sleep(1)

print("Vehicle is armable:", vehicle.is_armable)

# Arming: Starting the motors.
while not vehicle.armed:
    vehicle.armed = True
    time.sleep(1)

print("Vehicle is armed:", vehicle.armed)

# --- TAKEOFF ---
# Logic: Keep sending takeoff command until the drone reaches at least 5 meters.
while vehicle.location.global_relative_frame.alt < 5.0:
    vehicle.simple_takeoff(20) # Target altitude is 20m
    print("Altitude: ", vehicle.location.global_relative_frame.alt,
          "Target Distance: ", vehicle.target_distance)
    time.sleep(1)

# --- NAVIGATION ---
# Calculate the initial distance to target before starting the movement loop.
distance = geopy.distance.GeodesicDistance(target_location,
                                           (vehicle.location.global_relative_frame.lat,
                                            vehicle.location.global_relative_frame.lon)).meters

# Logic: Repeat simple_goto until we confirm the drone has actually started moving.
# If (Initial Distance - Current Distance) < 5, it means the drone hasn't moved 5 meters yet.
while distance - vehicle.target_distance < 5.0:
    location = dronekit.LocationGlobalRelative(lat=target_location[0], lon=target_location[1], alt=20.0)
    vehicle.simple_goto(location)
    print("Starting mission... Current Distance to target:", vehicle.target_distance)
    time.sleep(1)

# Logic: Wait while the drone is still far from the target.

while vehicle.target_distance > 5.0:
    print("Moving to target... Distance remaining:", vehicle.target_distance)
    time.sleep(1)

# --- RETURN HOME ---
# After reaching the target, switch to RTL to come back and land.
while vehicle.mode.name != "RTL":
    vehicle.mode = dronekit.VehicleMode("RTL")
    time.sleep(1)

print("Vehicle mode changed to RTL successful")

# --- MONITORING ---
try:
    while True:
        print("Final Phase - Altitude:", vehicle.location.global_relative_frame.alt,
              "Distance from target:", vehicle.target_distance)
        time.sleep(1)
except KeyboardInterrupt:
    # Cleanup connection on manual exit (Ctrl+C).
    print("Closing the vehicle...")
    vehicle.close()
    print("Closed.")