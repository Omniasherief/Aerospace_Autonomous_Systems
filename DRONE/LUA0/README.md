
---

# 🛸 ArduPilot Lua Scripting & SITL Integration Guide
### *On-Board Autonomy*

---

## 🏗️ System Architecture
In this setup, we bridge the gap between high-level logic and low-level flight control:
* **Firmware:** ArduPilot (C++).
* **Scripting Engine:** Lua (Sandboxed, Low Priority).
* **Interface:** MAVProxy for GCS communication and debugging.



---

## 🛠️ Technical Setup & Environment

### 1. Requirements
* **Hardware:** Flight Controller with $\geq$ 2MB Flash and $\geq$ 70kB allocated RAM.
* **Software:** ArduPilot SITL (Software In The Loop).

### 2. Parameters Configuration
To enable the scripting engine, the following parameters must be set via MAVProxy or Mission Planner:
```bash
param set SCR_ENABLE 1        # Enables the Lua VM
param set SCR_HEAP_SIZE 102400 # Allocates RAM (in bytes) for scripts
param set SCR_VM_I_COUNT 10000 # Max instructions per time slice
reboot                        # Required to initialize the engine
```

### 3. File System & Symlinking
To maintain a clean workflow, we use a **Symbolic Link** between the development folder and the ArduPilot SITL directory.

**Structure:**
* **Source:** `/home/omnia/DRONE/LUA`
* **Target:** `/home/omnia/ardu-sim/scripts`

**Command:**
```bash
rm -rf ~/ardu-sim/scripts  # Remove default folder
ln -s ~/DRONE/LUA ~/ardu-sim/scripts
```
*Note: ArduPilot only scans the top-level directory. Do not place scripts in subfolders.*

---

## 💻 Development Workflow

### 📋 The "Hello World" Script
Create `hello.lua` in your scripts folder:
```lua
-- Periodic update function
function update()
  -- Send message to GCS (Severity 6 = Informational)
  gcs:send_text(6, "Hello Omnia! Lua is Active") 
  
  -- Reschedule this function in 5000ms
  return update, 5000 
end

return update() -- Initial call
```

### 🔍 Debugging Commands (MAVProxy)
Use these commands to monitor the health of your scripts:
* `status SCR_MEM`: Shows current RAM usage (Critical for preventing OOM).
* `scripting restart/stop [name]`: Halts a misbehaving script in real-time.

---

## ⚠️ Critical Lessons Learned
> **The docs.lua Trap:** Never place the `docs.lua` (API bindings) inside the `/scripts` folder. The flight controller will attempt to load its 1000+ lines into the 70kB RAM, causing an `Insufficient memory` crash loop. Keep it in your project root for IDE autocompletion only.
`U can name it as docs.lua.txt or make new floder like i did in LUA0`
---

