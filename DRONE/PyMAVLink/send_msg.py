import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")
vehicle.wait_heartbeat()
print("connected to system: ", vehicle.target_system , "component:",vehicle.target_component)



# Create a COMMAND_LONG message object
msg = dialect.MAVLink_command_long_message(
    target_system=vehicle.target_system,    # The ID of the drone (e.g., 1)
    target_component=vehicle.target_component, # The ID of the component (e.g., 1 for Autopilot)
    command=dialect.MAV_CMD_DO_SEND_BANNER, # The specific command ID to execute
    confirmation=0, # 0: First time sending this command. >0: Retries
    param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0 # Parameters for the command
)


#send command to the vehicle
vehicle.mav.send(msg)

while True:
    try:
        #receive a msg The Handshake)
        ## Filter for STATUSTEXT (text notifications) and COMMAND_ACK (command result)
        msg=vehicle.recv_match(type=[dialect.MAVLink_statustext_message.msgname,
                                        dialect.MAVLink_command_ack_message.msgname],
                                    blocking=True)

        
        #convert msg to dict

        msg = msg.to_dict()

        # show the raw message
        print(msg)
        # Check if it is an Acknowledgment
        if msg['mavpackettype'] == 'COMMAND_ACK':
            # result 0 means SUCCESS
            print(f" Command Result: {msg['result']}")


    except KeyboardInterrupt:
        print("Exiting...")
        break    






'''
# sending to msg banner , arm 


import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# 1. Establish connection
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# 2. Wait for heartbeat
print("Waiting for heartbeat...")
vehicle.wait_heartbeat()
print(f"Connected to System {vehicle.target_system}")

# --- FUNCTION TO SEND COMMANDS (To avoid repeating code) ---
def send_command(command_id, p1=0, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0):
    msg = dialect.MAVLink_command_long_message(
        target_system=vehicle.target_system,
        target_component=vehicle.target_component,
        command=command_id,
        confirmation=0,
        param1=p1, param2=p2, param3=p3, param4=p4, param5=p5, param6=p6, param7=p7
    )
    vehicle.mav.send(msg)

# 3. Send First Command: SEND_BANNER (Information request)
print("\n[STEP 1] Sending Banner Request...")
send_command(dialect.MAV_CMD_DO_SEND_BANNER, p1=1)

# Wait a bit so the messages don't overlap too fast
time.sleep(3)

# 4. Send Second Command: ARM (Action request)
print("\n[STEP 2] Sending ARM Command...")
send_command(dialect.MAV_CMD_COMPONENT_ARM_DISARM, p1=1)

# 5. Continuous Loop to receive all responses
print("\nMonitoring responses (Press Ctrl+C to stop)...")
while True:
    try:
        # Receive any message that is Status Text or Command Acknowledgment
        msg = vehicle.recv_match(type=[
            dialect.MAVLink_statustext_message.msgname,
            dialect.MAVLink_command_ack_message.msgname
        ], blocking=True)

        if msg:
            data = msg.to_dict()
            
            # Logic to handle Command Acknowledgments
            if data['mavpackettype'] == 'COMMAND_ACK':
                cmd_name = data['command']
                result = data['result']
                print(f"-> ACK: Command ID {cmd_name} | Result: {result} (0=Success)")

            # Logic to handle Status Text (Banner info or Arming status)
            if data['mavpackettype'] == 'STATUSTEXT':
                print(f"-> NOTIFY: {data['text']}")

    except KeyboardInterrupt:
        print("\nStopping script...")
        break
    
    time.sleep(0.1)

'''
