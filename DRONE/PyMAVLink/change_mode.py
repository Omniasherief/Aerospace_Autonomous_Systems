import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# 1. Establish a MAVLink connection over UDP
# device="udpin:127.0.0.1:14560" connects to a local GCS or SITL simulator
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# 2. Block execution until the first HEARTBEAT is received
# This populates vehicle.target_system and vehicle.target_component automatically
vehicle.wait_heartbeat()

# Define the target flight mode string
FLIGHT_MODE = "GUIDED"

# 3. Retrieve a dictionary of supported flight modes from the autopilot
# Keys are strings (e.g., "GUIDED"), values are integers (e.g., 4)
flight_modes = vehicle.mode_mapping()

# 4. Safety Check: Verify if the desired mode exists in the autopilot's firmware
if FLIGHT_MODE not in flight_modes.keys():
    print(FLIGHT_MODE, "is not supported")
    exit(1)

# 5. Construct the MAV_CMD_DO_SET_MODE command
# This uses the COMMAND_LONG message format to request a mode change
set_mode_msg = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,
    target_component=vehicle.target_component,
    command=dialect.MAV_CMD_DO_SET_MODE,
    confirmation=0,
    # param1=1 tells the drone to use the 'custom_mode' integer provided in param2
    param1=dialect.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    # param2 is the integer ID mapped to "GUIDED"
    param2=flight_modes[FLIGHT_MODE],
    param3=0, param4=0, param5=0, param6=0, param7=0
)

# Display connection details
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

# 6. Capture the current state before sending the change command
# Listen for a HEARTBEAT and convert the binary object to a Python dictionary


   #### msg = vehicle.recv_match(type='HEARTBEAT', blocking=True)
message = vehicle.recv_match(type=dialect.MAVLink_heartbeat_message.msgname, blocking=True)
message = message.to_dict()

# Extract the current numerical mode ID
mode_id = message["custom_mode"]

# 7. Reverse Lookup: Convert numerical mode ID back to a human-readable name
# We convert dict keys/values to lists to find the name by its index
flight_mode_names = list(flight_modes.keys())
flight_mode_ids = list(flight_modes.values())
flight_mode_index = flight_mode_ids.index(mode_id)
flight_mode_name = flight_mode_names[flight_mode_index]

print("Mode name before:", flight_mode_name)

# 8. Send the mode change request to the vehicle
vehicle.mav.send(set_mode_msg)

# 9. Enter a loop to wait for the drone's response (Acknowledgment)
while True:
    # Filter incoming messages for COMMAND_ACK
    message = vehicle.recv_match(type=dialect.MAVLink_command_ack_message.msgname, blocking=True)
    message = message.to_dict()

    # Verify if this ACK is specifically for the DO_SET_MODE command
    if message["command"] == dialect.MAV_CMD_DO_SET_MODE:
        # Check if the autopilot accepted the request (MAV_RESULT_ACCEPTED = 0)
        if message["result"] == dialect.MAV_RESULT_ACCEPTED:
            print("Changing mode to", FLIGHT_MODE, "accepted from the vehicle")
        else:
            # Rejection might happen if failsafes are active (e.g., no GPS fix)
            print("Changing mode to", FLIGHT_MODE, "failed")
        
        # Exit the loop once the specific ACK is handled
        break

# 10. Verification: Capture a new HEARTBEAT to confirm the change is active
message = vehicle.recv_match(type=dialect.MAVLink_heartbeat_message.msgname, blocking=True)
message = message.to_dict()

# Get the new mode ID from the latest heartbeat
mode_id = message["custom_mode"]

# Repeat the reverse lookup logic to get the string name of the current mode
flight_mode_names = list(flight_modes.keys())
flight_mode_ids = list(flight_modes.values())
flight_mode_index = flight_mode_ids.index(mode_id)
flight_mode_name = flight_mode_names[flight_mode_index]

print("Mode name after:", flight_mode_name)





#the repetition (DRY - Don't Repeat Yourself principle) and the fragility of the logic.
'''
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
import sys

class DroneController:
    def __init__(self, connection_string):
        # Initialize connection
        self.vehicle = utility.mavlink_connection(connection_string)
        self.vehicle.wait_heartbeat()
        # Cache mode mapping for quick lookups
        self.mode_map = self.vehicle.mode_mapping() 
        print(f"Connected to System: {self.vehicle.target_system}")

    def get_current_mode(self):
        """Captures a heartbeat and returns the human-readable mode name."""
        msg = self.vehicle.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
        if not msg:
            return "Unknown"
        
        custom_mode = msg.custom_mode
        # Professional way to reverse lookup a dictionary key by value
        for name, id in self.mode_map.items():
            if id == custom_mode:
                return name
        return "Unknown"

    def set_mode(self, mode_name):
        """Changes the flight mode and verifies success."""
        if mode_name not in self.mode_map:
            print(f"Error: {mode_name} is not supported by this firmware.")
            return False

        print(f"Attempting to change mode from {self.get_current_mode()} to {mode_name}...")

        # Construct the command
        mode_id = self.mode_map[mode_name]
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            dialect.MAV_CMD_DO_SET_MODE,
            0, 
            dialect.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 
            mode_id, 0, 0, 0, 0, 0
        )

        # Wait for ACK
        while True:
            ack = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
            if not ack:
                print("ACK Timeout: Drone did not respond.")
                return False
            
            if ack.command == dialect.MAV_CMD_DO_SET_MODE:
                if ack.result == dialect.MAV_RESULT_ACCEPTED:
                    print(f"Success: Mode changed to {mode_name}")
                    return True
                else:
                    print(f"Failed: Drone rejected mode change (Result Code: {ack.result})")
                    return False

# --- Execution Block ---
if __name__ == "__main__":
    # Create an instance of our pro controller
    drone = DroneController("udpin:127.0.0.1:14560")

    # Change mode with a single, clean line
    success = drone.set_mode("GUIDED")

    if success:
        print(f"Final Verification: Current mode is now {drone.get_current_mode()}")
    else:
        print("Mode change sequence failed.")
'''