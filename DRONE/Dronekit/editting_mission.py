
import time
import drone_setup
drone_setup.fix_compatibility()
import dronekit


target_locations = ((-35.362048, 149.164489, 30),
                    (-35.362184, 149.162649, 20),
                    (-35.363580, 149.162826, 25),
                    (-35.363496, 149.165149, 10))

print("Trying to connect to the vehicle...")
vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
print("Connected to the vehicle.")

vehicle.parameters["RTL_ALT"]=3000 #CM

mission_items=vehicle.commands #an attribute holdsthe list of waypoints on the plane
mission_items.download()
mission_items.wait_ready()
mission_items.clear()


# --- BUILDING THE MISSION ---

# --- MAVLink Command Structure Reference ---
'''
mission_item = dronekit.Command(
    0,                                 # 1. target_system: System ID (0 for the vehicle itself)
    0,                                 # 2. target_component: Component ID (0 for the main autopilot)
    0,                                 # 3. seq: Sequence number (Order in the mission list)
    dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # 4. frame: Coordinate system (Altitude relative to home)
    dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,          # 5. command: The ID of the specific task (Waypoint, Takeoff, etc.)
    0,                                 # 6. current: Status (0: not active, 1: currently executing)
    0,                                 # 7. autocontinue: (0: stop after finishing, 1: proceed to next item)
    0,                                 # 8. param1: Varies by command (e.g., Hold time in seconds for Waypoints)
    0,                                 # 9. param2: Varies by command (e.g., Acceptance radius in meters)
    0,                                 # 10. param3: Varies by command (e.g., 0 to pass through, CCW/CW for Orbit)
    0,                                 # 11. param4: Varies by command (e.g., Desired yaw/heading angle)
    -35.362048,                        # 12. x: Latitude coordinate
    149.164489,                        # 13. y: Longitude coordinate
    30,                                # 14. z: Altitude in meters
    0                                  # 15. mission_type: Type of mission (0 for the primary mission)
)
'''


#takeoff command object
mission_item=dronekit.Command(0,0,0,
                               dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
                              ,dronekit.mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,0, 0, 0, 0, 0, 0, 0, 30)


mission_items.add(mission_item)

#navigation locations

for location in target_locations:
    mission_item=dronekit.Command(0,0,0,dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                  dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                    0, 0, 0, 0, 0, 0,
                                    location[0], location[1], location[2])
    mission_items.add(mission_item)


# return to launch command
mission_item = dronekit.Command(0, 0, 0,
                                dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                dronekit.mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
                                0, 0, 0, 0, 0, 0, 0, 0, 0)
mission_items.add(mission_item)

# land command
mission_item = dronekit.Command(0, 0, 0,
                                dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                dronekit.mavutil.mavlink.MAV_CMD_NAV_LAND,
                                0, 0, 0, 0, 0, 0, 0, 0, 0)
mission_items.add(mission_item)

mission_items.upload()
print("uploaded all missions")

while vehicle.mode.name != "GUIDED":
    vehicle.mode = dronekit.VehicleMode("GUIDED")
    time.sleep(1)
print("Vehicle is in GUIDED mode.")

vehicle.send_calibrate_barometer()

while not vehicle.is_armable:
    time.sleep(1)

print("Vehicle is armable:", vehicle.is_armable)

while not vehicle.armed:
    vehicle.armed = True
    time.sleep(1)

print("Vehicle is armed:", vehicle.armed)

while vehicle.mode.name !="AUTO":
    vehicle.mode=dronekit.VehicleMode("AUTO")
    time.sleep(1)

print("vehicle is in Auto mode ")


# Start the mission: Use message_factory to encode a MAV_CMD_MISSION_START 
# and send_mavlink to physically transmit the packet

vehicle.send_mavlink(vehicle.message_factory.command_long_encode(0,0,dronekit.mavutil.mavlink.MAV_CMD_MISSION_START, 0,0,0,0,0,0,0,0))


try:
    while True:
        print("Latitude:", vehicle.location.global_relative_frame.lat,
              "Longitude:", vehicle.location.global_relative_frame.lat,
              "Altitude:", vehicle.location.global_relative_frame.alt,
              "Target Number:", vehicle.commands.next)
        time.sleep(3)
except KeyboardInterrupt:
    print("Closing the vehicle...")
    vehicle.close()
    print("Closed the vehicle.")