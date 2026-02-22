import math
import drone_setup
drone_setup.fix_compatibility()
import dronekit

#connecting to virtual drone on the local machine
print("Trying to connect to the vehicle ....")
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("conect to the vehicle")

# Global Frame: Latitude/Longitude/Altitude relative to Sea Level (MSL)

print("GLOBAL LOCATION >> LATITUDE :{0}".format(vehicle.location.global_frame.lat))
print("GLOBAL LOCATION >> Longitude :{0}".format(vehicle.location.global_frame.lon))
print("GLOBAL LOCATION >> Altitude :{0}".format(vehicle.location.global_frame.alt))

# Global Relative Frame: Altitude relative to the HOME (Takeoff point)
#(how high am I from the ground?)
print("GLOBAL RELATIVE LOCATION >> LATITUDE :{0}".format(vehicle.location.global_relative_frame.lat))
print("GLOBAL RELATIVE LOCATION >> Longitude :{0}".format(vehicle.location.global_relative_frame.lon))
print("GLOBAL RELATIVE LOCATION >> Altitude :{0}".format(vehicle.location.global_relative_frame.alt))

#Roll: Tilting Left/Right | Pitch: Tilting Forward/Backward | Yaw: Rotating Left/Right

print("Attitude >> ROLL :{0}".format(math.degrees(vehicle.attitude.roll)))
print("Attitude >> PITCH :{0}".format(math.degrees(vehicle.attitude.pitch)))
print("Attitude >> Yaw :{0}".format(math.degrees(vehicle.attitude.yaw)))

# Heading: The compass direction (0-360 degrees)
print("Heading: {0}".format(vehicle.heading))


#System Status & Safety
# Check how many GPS satellites the drone can see (Need more than 6 for safety)
print("visible satellite count :{0}".format(vehicle.gps_0.satellites_visible))
# Battery information to avoid crashing
print("Battery > Level: {0}%".format(vehicle.battery.level))
print("Battery > Voltage: {0}".format(vehicle.battery.voltage))
print("Battery > Current: {0}".format(vehicle.battery.current))

# EKF (Extended Kalman Filter): Checks if sensors (IMU, GPS, Mag) agree with each other
print("EKF is healthy: {0}".format(vehicle.ekf_ok))

# Is the drone ready to arm? (Checks GPS lock, pre-arm checks)
print("Vehicle is armable: {0}".format(vehicle.is_armable))

# Is the drone currently running the motors?
print("Vehicle is armed: {0}".format(vehicle.armed))

print("Speed > Ground speed: {0}".format(vehicle.groundspeed))
print("Speed > Air speed: {0}".format(vehicle.airspeed))
print("Vehicle mode: " + vehicle.mode.name)

while not vehicle.home_location:
    mission_items=vehicle.commands
    mission_items.download() #request commands / home from drone
    mission_items.wait_ready()
    if not vehicle.home_location:
        print("Waiting for home location ...")


print("Global home location > Latitude: {0}".format(vehicle.home_location.lat))
print("Global home location > Longitude: {0}".format(vehicle.home_location.lon))
print("Global home location > Altitude: {0}".format(vehicle.home_location.alt))


print("Closing the vehicle...")
vehicle.close()
print("Closed the vehicle.")