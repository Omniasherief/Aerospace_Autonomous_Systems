# vehicle_connection.py
import drone_setup
drone_setup.fix_compatibility()

import dronekit

print("TRYING TO CONNECT TO THE VEHICLE .....")

try:
    vehicle = dronekit.connect(ip="127.0.0.1:14550", wait_ready=True)
    print("Connected Successfully!")
    print("Vehicle mode: " + vehicle.mode.name)
    vehicle.close()
except Exception as e:
    print(f"Connection failed: {e}")