
### Technical Notes: SITL Communication Ports

> * **Port 14550:** Typically reserved for **GCS (Ground Control Stations)** like *Mission Planner*, *QGroundControl*, or high-level APIs like *DroneKit*.
> * **Ports 14560 / 14561:** Usually available for **Raw MAVLink connections** using *PyMAVLink* or other secondary APIs/custom scripts.
> 
> 

---

### Comparison: Changing Flight Mode to GUIDED

This is where you see how **DroneKit** hides the complexity, while **PyMAVLink** requires you to build the raw command packet.

#### 1. Using DroneKit (High-Level Attribute)

DroneKit treats the "Mode" as a simple **Attribute** of the vehicle object.

```python
import dronekit

# Simple and readable: just assign a new VehicleMode object
vehicle.mode = dronekit.VehicleMode("GUIDED")

# Verification is a simple 'if' check on the attribute
if vehicle.mode.name == "GUIDED":
    print("Mode changed successfully!")

```

#### 2. Using PyMAVLink (Low-Level Command)

In PyMAVLink, you must send a **MAV_CMD_DO_SET_MODE** message with specific parameters (Base Mode and Custom Mode ID).

```python
from pymavlink import mavutil

# You must send a 'command_long' or 'set_mode' message
# 4 is the internal ArduPilot ID for 'GUIDED' mode
vehicle.mav.set_mode_send(
    vehicle.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4) 

# Verification requires waiting for a 'HEARTBEAT' message and checking the mode field
msg = vehicle.recv_match(type='HEARTBEAT', blocking=True)
if msg.custom_mode == 4:
    print("Mode changed successfully!")

```

---

### Summary of the Difference

* **DroneKit:** You tell the library **"WHAT"** you want (Change mode to Guided).
* **PyMAVLink:** You tell the drone **"HOW"** to do it (Send a packet with ID #176, set flag to 1, and set custom mode to 4).

**Would you like me to help you write a PyMAVLink script that listens for "StatusText" messages so you can see the calibration errors we talked about earlier?**