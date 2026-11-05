# 🖥️ OS Lab 01: Desktop Daemon Memory & File-Descriptor Leak Detector

**Domain:** Operating Systems Internals (macOS, Linux & Windows)  
**Target Role:** Senior / Staff SDET (Endpoint Security, Desktop Clients & Daemon Profiling)  
**Interactive Visualizer:** `cs-os-leak-detector` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

When testing a short-lived CLI script, leaking `2 MB` of RAM or `5` file handles is invisible because the OS reclaims all process resources upon `exit(0)`.

When testing a **24/7 background endpoint daemon** (such as Netskope Client, CrowdStrike Falcon, or Docker Desktop):
1. **The GC Sawtooth Illusion**: A rising memory graph over 10 minutes is often just uncollected garbage in JVM/Python/C# heaps. A true memory leak is only proven when the **Post-GC Baseline Floor** exhibits a positive linear regression slope ($\Delta \text{RSS} / \Delta t > \text{threshold}$) across multiple garbage collection cycles.
2. **File Descriptor / Handle Exhaustion (`EMFILE`)**: Even if Resident Set Size (RSS) RAM stays completely flat at `50 MB`, forgetting to close sockets, pipes, or log files leaks kernel file descriptors (`lsof -p <pid>` on macOS/Linux; `GetProcessHandleCount` on Windows). Once open handles hit `ulimit -n` (typically `1024` or `4096`), the daemon crashes with `Errno 24: Too many open files`.
3. **Kernel vs. User-Space Hooks**:
   - **macOS**: Modern agents use Apple's user-space **EndpointSecurity (`ES`)** framework and `NetworkExtension` (replacing deprecated kernel extensions `kexts`). If an ES client fails to respond to an `ES_EVENT_TYPE_AUTH_EXEC` callback within the deadline, the kernel terminates the daemon!
   - **Windows**: Agents use kernel-mode **File System Minifilter Drivers** (`FltMgr.sys`) communicating with a user-space C#/.NET service over Filter Communication Ports. Non-paged pool leaks in kernel mode cause a Blue Screen of Death (BSOD).

---

## 🔬 2. Telemetry Invariants We Validate in This Lab

Given a time-series stream of telemetry snapshots from a soak test:
- `timestamp_min`: Elapsed soak time in minutes
- `rss_mb`: Resident Set Size (physical RAM in MB)
- `gc_triggered`: Whether a full Garbage Collection just completed (`True`/`False`)
- `open_fds`: Current open file descriptors / OS handles
- `max_fd_limit`: OS `ulimit -n` ceiling (e.g., `1024`)

### Detection Rules:
1. **Post-GC Slope ($\text{MB/hour}$)**:
   Filter only snapshots where `gc_triggered == True` (the true live-object heap floor). Compute the rate of growth from the first post-GC snapshot to the last post-GC snapshot:
   $$\text{Slope}_{\text{MB/hr}} = \frac{\text{RSS}_{\text{last\_gc}} - \text{RSS}_{\text{first\_gc}}}{\Delta t_{\text{hours}}}$$
   Flag `MEMORY_LEAK` if $\text{Slope}_{\text{MB/hr}} > 5.0\text{ MB/hr}$.
2. **Handle Exhaustion Risk**:
   Compute the handle utilization ratio $\text{max}(\text{open\_fds}) / \text{max\_fd\_limit}$ and monotonic handle growth across GC boundaries. Flag `FD_LEAK` if utilization $\ge 0.80$ ($80\%$) or handles grow monotonically across $\ge 3$ post-GC checkpoints.
3. **Verdict**:
   - `"HEALTHY"` if neither leak is present (even if raw RSS fluctuates wildly between GCs!).
   - `"MEMORY_LEAK"`, `"FD_LEAK"`, or `"CRITICAL_DUAL_LEAK"`.

---

## 🧪 3. Running Verification

```bash
./run.sh test 01-memory-and-handle-leak-detector
```

