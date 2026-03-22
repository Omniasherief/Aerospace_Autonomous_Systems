

# ----------------------------------------------------------------------------------
# RC_CHANNELS vs SERVO_OUTPUT_RAW Explanation:
# ----------------------------------------------------------------------------------
# RC_CHANNELS: 
#   Represents the INPUT values coming from the Pilot's transmitter (Remote Control).
#   Used to trigger software tasks (Task 1, Task 2) based on switch positions.
#   Each channel sends a PWM value between 1000 (Min) and 2000 (Max).
#
# SERVO_OUTPUT_RAW:
#   Represents the OUTPUT values sent by the Autopilot to the motors/servos.
#   Used to monitor motor health and behavior. 
#   In a Quadcopter: Servo 1-4 usually correspond to Motors 1-4.
# ----------------------------------------------------------------------------------

# RC_CHANNELS (Input): Supports up to 18 channels.
# These represent signals from the transmitter to the drone.
# We monitor Channel 16 ("chan16_raw") for custom tasks.

# SERVO_OUTPUT_RAW (Output): Supports up to 16 channels.
# These represent signals from the drone's autopilot to the motors/servos.
# Usually, Servos 1-4 control the 4 motors of a quadcopter.


# We chose Channel 16 because:
# 1. Channels 1-4 are reserved for fligh for Flight Mode switching.
# 3. Channel 16 is an At controls (Roll, Pitch, Throttle, Yaw).
# 2. Channel 5 is usually reserveduxiliary (AUX) channel, typically free for custom tasks.
# 4. Using high-numbered channels prevents accidental triggering of flight functions.



#test 
# rc 16 1600
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

def task1():
    print("Running task 1...")

def task2():
    print("Running task 2...")


# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

# while True:

#     # capture SERVO_OUTPUT_RAW message
#     message = vehicle.recv_match(type=dialect.MAVLink_servo_output_raw_message.msgname,
#                                  blocking=True)

#     # convert the message to dictionary
#     message = message.to_dict()

#     # print the message
#     print("Motor 1:", message["servo1_raw"],
#           "Motor 2:", message["servo2_raw"],
#           "Motor 3:", message["servo3_raw"],
#           "Motor 4:", message["servo4_raw"])
    
while True:
    message=vehicle.recv_match(type=dialect.MAVLink_rc_channels_message.msgname,blocking=True)
    print(message)
    # convert the message to dictionary
    message = message.to_dict()
    if 1200< message["chan16_raw"] <1500:
        task1()


    elif 1500 < message["chan16_raw"] <1700:
       task2()
    
    else:
      print("Invalid channel 16 value:", message["chan16_raw"])

