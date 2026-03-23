# --out 127.0.0.1:14560:
# The Simulator SENDS data to this port. Your script is a "Listener".

# --master 127.0.0.1:14560:
# The Simulator RECEIVES data from this port. Your script is a "Source" (Companion Computer).

# Why the change?
# To allow your script to inject new messages (like STATUSTEXT) into the MAVLink network.

import time
import random
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

#change in-->out

my_process = utility.mavlink_connection(device="udpout:127.0.0.1:14560", source_system=1, source_component=1)

print("serving a system:", my_process.source_system  ," component:",my_process.source_component)
while True:
    text = f"Roll a dice: {random.randint(1,6)} flip a coin: {random.randint(0,1)}"


  # create STATUSTEXT message
    message = dialect.MAVLink_statustext_message(severity=dialect.MAV_SEVERITY_INFO,
                                                 text=text.encode("utf-8"))

    # send message to the GCS
    my_process.mav.send(message)

    # sleep a bit
    time.sleep(5)