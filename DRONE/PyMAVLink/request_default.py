
import time
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

print("wait for heartbeat")
# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)
# 4. Construct the REQUEST_DATA_STREAM message
# This tells the autopilot what data we want and how fast we want it.
message = dialect.MAVLink_request_data_stream_message(
    target_system=vehicle.target_system,    # The ID of the drone we are talking to
    target_component=vehicle.target_component, # The ID of the specific autopilot component
    req_stream_id=0,      # 0 = Request ALL available data streams (Raw sensors, GPS, etc.)
    req_message_rate=4,   # Frequency in Hertz (Send data 4 times per second)
    start_stop=1          # 1 = Start sending data, 0 = Stop sending data
)

# send request data stream message to the vehicle
vehicle.mav.send(message)
# infinite loop to catch all messages from simulated vehicle
while True:

    # catch all messages
    message = vehicle.recv_match(blocking=True)

    # convert this messages to dictionary
    message = message.to_dict()

    # debug the message
    print(message)