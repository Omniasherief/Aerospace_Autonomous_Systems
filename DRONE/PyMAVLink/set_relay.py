"""
=============================================================================
RELAY CONTROL MISSION: DIGITAL ON/OFF SWITCHING
=============================================================================
DESCRIPTION:
- This script controls Relays (Digital Switches) instead of PWM Servos.
- Relays are used for simple ON/OFF tasks like lights or pumps.

SITL SIMULATION NOTE (SIM_PIN_MASK):
- In simulation, we monitor the 'SIM_PIN_MASK' parameter to see changes.
- Setting Relay 0 to ON  -> SIM_PIN_MASK becomes 1 (2^0)
- Setting Relay 1 to ON  -> SIM_PIN_MASK becomes 2 (2^1)

PRE-FLIGHT SETUP (MAVProxy):
1. Configure Relay Pin: param set RELAY_PIN 0
2. Monitor Changes: watch SIM_PIN_MASK
=============================================================================
"""

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# --- 1. CONNECTION ---
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print(f"Connected to System: {vehicle.target_system}")

# --- 2. SET RELAY (SINGLE ACTION) ---
# This command turns a specific relay ON or OFF.
set_relay_cmd = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_SET_RELAY,
    confirmation=0,
    param1=0,  # Relay Instance 0 (First Relay)
    param2=1,  # 1 = ON, 0 = OFF
    param3=0, param4=0, param5=0, param6=0, param7=0
)

# vehicle.mav.send(set_relay_cmd) # Commented out to focus on repeat command

# --- 3. REPEAT RELAY (TOGGLE CYCLE) ---
# MAV_CMD_DO_REPEAT_RELAY: Automatically toggles the relay state multiple times.
repeat_relay_cmd = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_REPEAT_RELAY,
    confirmation=0,
    param1=0,   # Relay Instance 0
    param2=3,   # Cycle Count: Toggle 3 times
    param3=10,  # Period: 10 seconds between toggles
    param4=0, param5=0, param6=0, param7=0
)

print("Sending: DO_REPEAT_RELAY (Instance 0 | Cycles: 3 | Period: 10s)")
vehicle.mav.send(repeat_relay_cmd)

print("\nRelay Command Sent! Check MAVProxy 'SIM_PIN_MASKxxxxx--->watch PARAM_VALUE' to see it toggle.")

#watch PARAM_VALUE