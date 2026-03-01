'''

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)

while True:
    try:
        # receive a message
        msg=vehicle.recv_match(type=dialect.MAVLink_system_time_message.msgname, blocking=True)
        #it is object so convert to dict for easy access
        msg = msg.to_dict()
        
        for field_name in dialect.MAVLink_system_time_message.fieldnames:
            print(field_name)
            if field_name == "time_boot_ms":
                # print field name and contained field value
                print(field_name, msg[field_name])




    # exit on Ctrl+C
    except KeyboardInterrupt:
        print("User interrupt received, exiting.")
        exit(0)

    # bare except to catch all the exceptions
    except Exception as e:

        # print error message
        print(f"Error occurred: {e}")

    # tiny sleep to cool down the terminal
    time.sleep(0.010)

'''

import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

# Connect to the output stream from MAVProxy
# MAVProxy will forward data to this port
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

print("Waiting for MAVProxy to forward heartbeat...")
vehicle.wait_heartbeat()
print(f"Connected to System {vehicle.target_system}")

while True:
    try:
        # Catch any incoming message
        msg = vehicle.recv_match(blocking=True)
        if not msg:
            continue

        # Print System Time
        if msg.get_type() == 'SYSTEM_TIME':
            print(f"Time since boot: {msg.time_boot_ms} ms")

        # Print Altitude from Global Position
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            # relative_alt is in mm, convert to meters
            alt = msg.relative_alt / 1000.0
            print(f"Current Altitude: {alt} meters")

    except KeyboardInterrupt:
        print("Closing...")
        break
    time.sleep(0.05)