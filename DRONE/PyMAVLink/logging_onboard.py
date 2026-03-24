#./ardu-sim.sh 
# omnia@omnia-Victus-by-HP-Laptop-16-d1xxx:~/ardu-sim$ cd logs/
# omnia@omnia-Victus-by-HP-Laptop-16-d1xxx:~/ardu-sim/logs$ mavlogdump.py 00000015.BIN --types=MSG
#screen -wipe
# killall screen
import time
import random
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect

vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560",
                                     source_system=1,
                                     source_component=1)

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)



while True:

    # create STATUSTEXT message
    text = f"CUSTOM:{random.randint(1,6)},{random.randint(0,1)},{random.random()}"
    message = dialect.MAVLink_statustext_message(severity=dialect.MAV_SEVERITY_DEBUG,
                                                 text=text.encode("utf-8"))
    print(text)

    # send the message to the vehicle
    vehicle.mav.send(message)

    # wait for 1 second
    time.sleep(1)

