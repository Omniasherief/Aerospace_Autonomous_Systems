import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect



# connect to vehicle
vehicle = utility.mavlink_connection(device="udpin:127.0.0.1:14560")

# wait for a heartbeat
vehicle.wait_heartbeat()

# inform user
print("Connected to system:", vehicle.target_system, ", component:", vehicle.target_component)
'''

    param1: Target angle (0 is north)
    param2: Angular speed (degrees per second)
    param3: Direction (-1: CCW, 0: Default, 1:CW)
    param4: Target angle type (0: Absolute, 1: Relative)


'''

DIRECTION_CCW=-1
DIRECTION_CW=1
DIRECTION_DEFAULT=0
ANGLE_ABSOLUTE=0
ANGLE_RELATIVE=1

message=dialect.MAVLink_command_long_message(target_system=vehicle.target_system,
                                               target_component=vehicle.target_component,
                                               command=dialect.MAV_CMD_CONDITION_YAW,
                                               confirmation=0,
                                               param1=90,param2=0,
                                               param3=DIRECTION_CW,
                                               param4=ANGLE_RELATIVE,
                                               param5=0,
                                               param6=0,
                                               param7=0)

# send yaw command to the vehicle
vehicle.mav.send(message)                                              
# -------------------------------------------------------------------------
# WP_YAW_BEHAVIOR Parameter Explanation:
# This parameter determines how the autopilot controls the drone's heading (Yaw)
# during autonomous flight (missions/waypoints).
#
# Value [0]: NEVER_CHANGE 
#            The drone maintains its current heading. It will not rotate 
#            automatically when moving to the next waypoint.
#
# Value [1]: FACE_NEXT_WAYPOINT (Default)
#            The drone's nose will always point towards the next waypoint 
#            in the mission.
#
# Value [2]: FACE_NEXT_WAYPOINT_EXCEPT_RTL
#            Same as [1], but during "Return to Launch" (RTL), the drone 
#            keeps its current heading and flies back without rotating its nose.
#
# Value [3]: FACE_ALONG_GPS_COURSE
#            The drone points its nose in the actual direction of travel 
#            (the GPS track), which is useful in high-wind conditions.
# -------------------------------------------------------------------------
# To check the current value from the terminal (MAVProxy):
# param show WP_YAW_BEHAVIOR

# To set it manually from the terminal:
# param set WP_YAW_BEHAVIOR 0