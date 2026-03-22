
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
PAUSE = 0
RESUME = 1

# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)


# ----------------------------------------------------------------------------------
# MAV_CMD_DO_PAUSE_CONTINUE Command Explanation:
# ----------------------------------------------------------------------------------
# This command allows the user to pause/resume an ongoing autonomous mission.
#
# Param 1: [0] = PAUSE (The vehicle stops at current location and hovers).
#          [1] = RESUME (The vehicle continues the mission toward the next waypoint).
#
# Usage Scenarios:
# 1. Inspecting a target during flight.
# 2. Releasing a payload at a specific dynamic location.
# 3. Taking samples or high-quality photos at an interesting spot.
# ----------------------------------------------------------------------------------

command = dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
                                               target_component=vehicle.target_component,
                                               command=dialect.MAV_CMD_DO_PAUSE_CONTINUE,
                                               confirmation=0,
                                               param1=RESUME,
                                               param2=0,
                                               param3=0,
                                               param4=0,
                                               param5=0,
                                               param6=0,
                                               param7=0)

# send this command to the vehicle
vehicle.mav.send(command)