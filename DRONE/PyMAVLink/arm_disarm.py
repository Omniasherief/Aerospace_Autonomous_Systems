
#BASED ON ACK
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# arm disarm definitions
VEHICLE_ARM = 1
VEHICLE_DISARM = 0


# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")


vehicle_arm_message=dialect.MAVLink_command_long_message(
vehicle.target_system,
vehicle.target_component,
dialect.MAV_CMD_COMPONENT_ARM_DISARM, # command
0,
VEHICLE_ARM, # param1
0,0,0,0,0,0)


vehicle_disarm_message=dialect.MAVLink_command_long_message(
vehicle.target_system,
vehicle.target_component,
dialect.MAV_CMD_COMPONENT_ARM_DISARM, # command
0,
VEHICLE_DISARM, # param1
0,0,0,0,0,0)

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)


while True:



    # observe the SYS_STATUS messages
    message=vehicle.recv_match(type=dialect.MAVLink_sys_status_message.msgname, blocking=True)


    # convert to dictionary
    message=message.to_dict()

    # get sensor health
    onboard_control_sensors_health = message["onboard_control_sensors_health"]

    # get pre-arm healthy bit
    # 1. Extract the raw 32-bit health status integer from the SYS_STATUS message
    onboard_control_sensors_health = message["onboard_control_sensors_health"]

    # 2. Perform a bitwise AND operation to isolate the pre-arm check bit
    # This acts as a mask to filter out all other sensor data except the pre-arm status
    preArm_status_bit = onboard_control_sensors_health & dialect.MAV_SYS_STATUS_PREARM_CHECK

    # 3. Compare the isolated bit with the expected "healthy" constant
    # If the result matches, it means the specific bit for pre-arm safety is set to 1 (Healthy)
    preArm_status = preArm_status_bit == dialect.MAV_SYS_STATUS_PREARM_CHECK

# 4. Final boolean check: If true, the vehicle has passed all internal safety diagnostics

    # check prearm
    if preArm_status:

        # vehicle can be armable
        print("Vehicle is armable")

        # break the prearm check loop
        break

'''
while True:

    # arm the vehicle
    print("Vehicle is arming...")

    # send arm message
    vehicle.mav.send(vehicle_arm_message)

    # wait COMMAND_ACK message
    message = vehicle.recv_match(type=dialect.MAVLink_command_ack_message.msgname, blocking=True)

    # convert the message to dictionary
    message = message.to_dict()

    # check if the vehicle is armed
    if message["result"] == dialect.MAV_RESULT_ACCEPTED and message["command"] == dialect.MAV_CMD_COMPONENT_ARM_DISARM:

        # print that vehicle is armed
        print("Vehicle is armed!")

    else:

        # print that vehicle is not armed
        print("Vehicle is not armed!")

    # wait some time
  # wait some time
    time.sleep(10)

    # disarm the vehicle
    print("Vehicle is disarming...")

    # send disarm message
    vehicle.mav.send(vehicle_disarm_message)

    # check if the vehicle is disarmed
    # Verify if the ACK matches our specific command and if it was accepted
    # message["command"] == 400 (ARM/DISARM)
    # message["result"] == 0 (ACCEPTED)
    if message["result"] == dialect.MAV_RESULT_ACCEPTED and message["command"] == dialect.MAV_CMD_COMPONENT_ARM_DISARM:

        # print that vehicle is disarmed
        print("Vehicle is disarmed!")

    else:

        # print that vehicle is not disarmed
        print("Vehicle is not disarmed!")

    # wait some time
    time.sleep(10)
'''

##DEPENDS ON HEARTBEAT
while True:

    # arm the vehicle
    print("Vehicle is arming...")

    # send arm message
    vehicle.mav.send(vehicle_arm_message)

    # wait until vehicle is armed
    while True:
        #catch a heart beat msg 
        msg= vehicle.recv_match(type=dialect.MAVLink_heartbeat_message.msgname,blocking =True)
        # convert message to dictionary
        msg=msg.to_dict()

        # get base mode
        base_mode = msg["base_mode"]
        # get armed status
        armed_bit = base_mode & dialect.MAV_MODE_FLAG_SAFETY_ARMED
        arm_status = armed_bit == dialect.MAV_MODE_FLAG_SAFETY_ARMED
         # check armed status
        if arm_status:

            # vehicle is armed, exit from infinite loop
            break
      # print arm status
    print("Vehicle is armed!")

    # wait some time
    time.sleep(10)

    # disarm the vehicle
    print("Vehicle is disarming...")

    # send disarm message
    vehicle.mav.send(vehicle_disarm_message)

    # wait until vehicle is disarmed
    while True:

        # catch a heartbeat message
        message = vehicle.recv_match(type=dialect.MAVLink_heartbeat_message.msgname, blocking=True)

        # convert message to dictionary
        message = message.to_dict()

        # get base mode
        base_mode = message["base_mode"]

        # get armed status
        armed_bit = base_mode & dialect.MAV_MODE_FLAG_SAFETY_ARMED
        arm_status = armed_bit == dialect.MAV_MODE_FLAG_SAFETY_ARMED

        # check armed status
        if not arm_status:

            # vehicle is disarmed, exit from infinite loop
            break

    # print arm status
    print("Vehicle is disarmed!")

    # wait some time
    time.sleep(10)
























'''


import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# Arm/Disarm definitions
VEHICLE_ARM = 1
VEHICLE_DISARM = 0

# Connect to the vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# Wait for the first heartbeat to confirm connection
vehicle.wait_heartbeat()
print(f"Connected to system: {vehicle.target_system}, component: {vehicle.target_component}")

def send_arm_disarm_and_verify(arm_code):
    """
    Sends ARM/DISARM command, checks for ACK, and verifies the final state via Heartbeat.
    """
    action_name = "ARMING" if arm_code == VEHICLE_ARM else "DISARMING"
    print(f"Vehicle is {action_name}...")

    # 1. Send the command
    vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        dialect.MAV_CMD_COMPONENT_ARM_DISARM,
        0, arm_code, 0, 0, 0, 0, 0, 0
    )

    # 2. Wait for Command Acknowledgment (ACK)
    # This ensures the drone received and accepted the command
    ack_received = False
    while not ack_received:
        msg = vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=2)
        if msg and msg.command == dialect.MAV_CMD_COMPONENT_ARM_DISARM:
            if msg.result == dialect.MAV_RESULT_ACCEPTED:
                print(f"Command ACCEPTED: {action_name}")
                ack_received = True
            else:
                print(f"Command REJECTED or FAILED with result code: {msg.result}")
                return False
        else:
            # If timeout or wrong message, resend the command (safety retry)
            print("Wait for ACK timeout, resending command...")
            vehicle.mav.command_long_send(
                vehicle.target_system, vehicle.target_component,
                dialect.MAV_CMD_COMPONENT_ARM_DISARM, 0, arm_code, 0, 0, 0, 0, 0, 0
            )

    # 3. Verify the final state via Heartbeat (The "Golden Source" of truth)
    print(f"Verifying {action_name} status via Heartbeat...")
    while True:
        msg = vehicle.recv_match(type='HEARTBEAT', blocking=True)
        # Check the MAV_MODE_FLAG_SAFETY_ARMED bit in base_mode
        is_armed = bool(msg.base_mode & dialect.MAV_MODE_FLAG_SAFETY_ARMED)
        
        if arm_code == VEHICLE_ARM and is_armed:
            print("CRITICAL CONFIRMATION: Vehicle is ARMED and ready!")
            break
        elif arm_code == VEHICLE_DISARM and not is_armed:
            print("CRITICAL CONFIRMATION: Vehicle is DISARMED and safe!")
            break

# --- Main Logic ---

# Check Pre-arm health first
print("Checking pre-arm health status...")
while True:
    msg = vehicle.recv_match(type='SYS_STATUS', blocking=True)
    health = msg.onboard_control_sensors_health
    if (health & dialect.MAV_SYS_STATUS_PREARM_CHECK) == dialect.MAV_SYS_STATUS_PREARM_CHECK:
        print("Vehicle is armable (Pre-arm checks passed)")
        break

# Execute the combined loop
while True:
    # Perform ARM with verification
    send_arm_disarm_and_verify(VEHICLE_ARM)
    
    time.sleep(5) # Stay armed for 5 seconds
    
    # Perform DISARM with verification
    send_arm_disarm_and_verify(VEHICLE_DISARM)
    
    time.sleep(5) # Wait before next cycle

'''
