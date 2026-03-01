from pymavlink import mavutil

vehicle= mavutil.mavlink_connection("udpin:127.0.0.1:14560")

vehicle.wait_heartbeat(timeout=5)
print("Heartbeat is recieved from the system Target system: %u  unit Target component: %u "% (vehicle.target_system, vehicle.target_component))

