# MAVProxy Professional Command-Line Ground Station Guide

This is a comprehensive, professional guide for using MAVProxy as a command-line ground control station (GCS) for UAVs. It merges official documentation with practical examples, including telemetry forwarding, vehicle control, mission editing, geofencing, plotting, and advanced MAVLink commands. This guide is ideal for both simulation (SITL) and real-world UAV testing.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Running MAVProxy](#running-mavproxy)
3. [Telemetry Forwarding](#telemetry-forwarding)
4. [Vehicle Control](#vehicle-control)
5. [Mission Editor & Waypoints](#mission-editor--waypoints)
6. [Geofencing](#geofencing)
7. [Rally Points](#rally-points)
8. [Graph Module](#graph-module)
9. [Advanced Commands](#advanced-commands)
10. [Servo & Relay Control](#servo--relay-control)
11. [Modules](#modules)
12. [Link Management & Outputs](#link-management--outputs)
13. [System Commands & Logging](#system-commands--logging)
14. [Additional References](#additional-references)

---

## Installation & Setup

### Install Required Packages

```bash
sudo apt-get update
sudo apt-get install python3-pip screen nano
```

### Install MAVProxy

```bash
sudo python3 -m pip install MAVProxy
```

> Optional: Configure automated startup using `screen` and `rc.local` if you want MAVProxy to start on boot. You can skip this if you just want to test manually.

---

## Running MAVProxy

### Basic Command

```bash
#./ardu-sim.sh 
mavproxy.py --master=127.0.0.1:14550 --console --map
```

* `--master` → Source of telemetry (vehicle or SITL)
* `--console` → Opens command-line interface
* `--map` → Displays map with mission waypoints

### Forwarding Telemetry Streams

```bash
mavproxy.py --master=SOURCE --out=DEST1 --out=DEST2
```

* `SOURCE` can be serial (`/dev/ttyUSB0` or `COM3`) or network (`tcp:IP:PORT`, `udp:IP:PORT`)
* Always prefer UDP for telemetry streaming for low latency
* Example:

```bash
mavproxy.py --master=127.0.0.1:14550 --out=127.0.0.1:10000 --out=127.0.0.1:20000
```

### Serial Connection with Baud Rate

```bash
--master=/dev/ttyUSB0,57600 --out=udp:127.0.0.1:14550
```

---

## Vehicle Control

### Arm/Disarm

```bash
arm throttle       # Arm the vehicle
disarm             # Disarm the vehicle
param show DISARM_DELAY  # Check auto disarm delay
param set DISARM_DELAY 10  # Set disarm delay to 10s
```

### Flight Modes

```bash
mode GUIDED
mode LOITER
mode RTL
mode LAND
```

### Takeoff

```bash
takeoff 10   # Altitude in meters
```

### Guided Flight to Coordinates

```bash
guided LATITUDE LONGITUDE ALTITUDE
```

### RC Override

```bash
rc 1 1600  # Roll
rc 2 1400  # Pitch
rc 3 1500  # Throttle
rc 4 1550  # Yaw
```

* 1500 = neutral, above/below = control input

---

## Mission Editor & Waypoints

### Load Mission Editor Module

```bash
load misseditor
```

### Mission Commands

```bash
wp clear            # Clear all waypoints
wp ftp              # Fetch mission from vehicle
wp ftpload FILE      # Upload mission from FILE
wp list             # List mission
wp save FILE        # Save mission to FILE
wp load FILE        # Load mission from FILE
```

### Start Mission (Without RC)

```bash
long MAV_CMD_MISSION_START 0 0 0 0 0 0 0 0
```

> Note: 0th waypoint = home location

---

## Geofencing

### Enable/Disable Fences

```bash
param set FENCE_ENABLE 1  # Enable
param set FENCE_ENABLE 0  # Disable
```

### Fence Configuration

```bash
param set FENCE_TYPE 15       # Enable min/max/circle/polygon
param set FENCE_RADIUS 300    # Radius in meters
param set FENCE_ALT_MAX 50    # Max altitude
param set FENCE_ALT_MIN 10    # Min altitude
param set LAND_REPOSITION 0   # Disable user input during landing
```

> Default behavior on breach: RTL

---

## Rally Points

```bash
rally list
rally add               # Add rally point at clicked location
rally remove INDEX
rally save FILE
rally load FILE
set rallyalt 50          # Default altitude
param set RALLY_LIMIT_KM 0  # Use closest rally point
```

---

## Graph Module

### Load Graph Module

```bash
module load graph
```

### Plotting Data

```bash
graph MESSAGE.FIELD
graph legend MESSAGE.FIELD "Legend Name"
graph timespan 10
graph tickresolution 0.1
```

### Examples

* Relative Altitude (VFR_HUD)

```bash
graph legend (VFR_HUD.alt-584) "Relative Altitude"
graph (VFR_HUD.alt-584)
```

* Relative Altitude (GLOBAL_POSITION_INT)

```bash
graph legend (GLOBAL_POSITION_INT.relative_alt/1000.0) "Relative Altitude"
graph (GLOBAL_POSITION_INT.relative_alt/1000.0)
```

* Vibration on all axes

```bash
graph legend VIBRATION.vibration_x "Vibration X"
graph legend VIBRATION.vibration_y "Vibration Y"
graph legend VIBRATION.vibration_z "Vibration Z"
graph VIBRATION.vibration_x VIBRATION.vibration_y VIBRATION.vibration_z
```

> Homework: Fly guided, plot roll, pitch, yaw, and compare desired vs actual.

---

## Advanced Commands

### COMMAND_INT

```bash
command_int FRAME COMMAND CURRENT AUTOCONTINUE PARAM1 PARAM2 PARAM3 PARAM4 X Y Z
```

* Example: Reposition

```bash
command_int MAV_FRAME_GLOBAL_RELATIVE_ALT_INT MAV_CMD_DO_REPOSITION 0 0 0 0 0 0 LAT*1e7 LON*1e7 ALT
```

### COMMAND_LONG

```bash
long MAV_CMD_NAV_TAKEOFF 0 0 0 0 0 0 10
```

* 7th parameter = takeoff altitude in meters

---

## Servo & Relay Control

### Servo

```bash
servo set CHANNEL VALUE
servo repeat CHANNEL VALUE COUNT PERIOD
```

### Relay

```bash
relay set 0 1   # Open
relay set 0 0   # Close
relay repeat 0 COUNT PERIOD
```

> SITL: Uses SIM_PIN_MASK. Set RELAY_PINx appropriately for real devices.

---

## Modules

| Module      | Description                                    |
| ----------- | ---------------------------------------------- |
| sensors     | Access and monitor sensors                     |
| speech      | Text-to-speech integration (requires speechd)  |
| system_time | Synchronize vehicle time with autopilot        |
| terrain     | Provides terrain data for terrain-aware flight |
| map         | Show map with waypoints                        |
| horizon     | Artificial horizon visualization               |
| graph       | Plot live telemetry data                       |

---

## Link Management & Outputs

```bash
link list
link add CONNECTION:LABEL
link remove INDEX|LABEL
output add CONNECTION
output remove INDEX
output list
link hl on|off  # High latency mode
link resetstats
```

---

## System Commands & Logging

```bash
reboot             # Restart autopilot
time               # Show autopilot time
script FILE        # Run commands from file
shell COMMAND      # Run shell command
status             # Show latest packets
watch MESSAGE      # Watch updating message
exit               # Exit MAVProxy
```

### Log Module

```bash
module load log
log help
log list
log download INDEX FILE
log erase
log resume
log status
log cancel
```

---

## Additional Tips

* Always use UDP for telemetry for low latency.
* Use `screen` for detached sessions if you want MAVProxy to run in background.
* Parameters can be set or viewed using `param set NAME VALUE` or `param show NAME`.
* For automated scripts, use `startup.sh` and optionally configure with `rc.local`.
* Use the official ArduPilot MAVProxy docs for updated commands: [MAVProxy Modules](https://ardupilot.org/mavproxy/modules.html)

---


