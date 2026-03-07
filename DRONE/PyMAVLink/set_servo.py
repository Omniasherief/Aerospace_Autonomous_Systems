"""
=============================================================================
SERVO CONTROL MISSION: MANUAL PWM OVERRIDE
=============================================================================
DESCRIPTION:
- This script demonstrates how to control auxiliary hardware (Servos/Relays).
- It uses MAV_CMD_DO_SET_SERVO and MAV_CMD_DO_REPEAT_SERVO.

PRE-FLIGHT SETUP (MAVProxy Terminal):
1. Load Graph: mavproxy.py --master=127.0.0.1:14550 --load-module="graph"
2. Check Channels: status SERVO_OUTPUT_RAW
3. Manual Override: param set SERVO6_FUNCTION 0 (Required for Channel 6)
4. Visualize: graph SERVO_OUTPUT_RAW.servo6_raw

CHANNEL AVAILABILITY RULES:
- CH 1-4 : Reserved (Flight Control: Roll, Pitch, Thr, Yaw).
- CH 5   : Reserved (Flight Mode Switching).
- CH 6-16: Available for Manual Control (After setting SERVOx_FUNCTION to 0).
=============================================================================
"""

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# --- 1. CONNECTION ---
# Connect to the simulated vehicle (SITL)
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# Wait for the first heartbeat to confirm connection
vehicle.wait_heartbeat()
print(f"Connected to System: {vehicle.target_system}, Component: {vehicle.target_component}")

# --- 2. SINGLE SERVO COMMAND (SET ONCE) ---
# MAV_CMD_DO_SET_SERVO: Sets a servo to a specific PWM value immediately.
set_servo_cmd = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_SET_SERVO,
    confirmation=0,
    param1=6,       # Servo Channel (6)
    param2=1900,    # PWM Value (1000 to 2000)
    param3=0, param4=0, param5=0, param6=0, param7=0
)

# Send the single set command
print("Sending: DO_SET_SERVO (Channel 6 -> 1900 PWM)")
vehicle.mav.send(set_servo_cmd)

# Small delay between commands
time.sleep(2)

# --- 3. REPEAT SERVO COMMAND (CYCLE) ---
# MAV_CMD_DO_REPEAT_SERVO: Toggles the servo between current and target PWM.
repeat_servo_cmd = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_REPEAT_SERVO,
    confirmation=0,
    param1=6,       # Servo Channel (6)
    param2=1900,    # Target PWM Value
    param3=4,       # Cycle Count (Number of times to repeat)
    param4=4,       # Period (Time in seconds between cycles)
    param5=0, param6=0, param7=0
)

# Send the repeat command
print("Sending: DO_REPEAT_SERVO (Channel 6 | Cycles: 4 | Period: 4s)")
vehicle.mav.send(repeat_servo_cmd)

print("\nMission Sent! Monitor the output in MAVProxy Graph.")