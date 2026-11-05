#!/usr/bin/env python3
"""
OS Lab 01: Desktop Daemon Memory & File-Descriptor Leak Detector.

Distinguishes benign GC sawtooth oscillations from true post-GC RSS memory leaks
and OS file-descriptor (handle) exhaustion during 24-hour endpoint soak tests.
"""

from typing import List, Dict, Any


class Solution:
    def analyze_soak_telemetry(
        self,
        snapshots: List[Dict[str, Any]],
        max_fd_limit: int = 1024,
        leak_slope_threshold_mb_per_hr: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Analyze endpoint daemon soak-test snapshots.

        Each snapshot dict contains:
          - timestamp_min (int/float): Elapsed minutes since soak start
          - rss_mb (float): Physical Resident Set Size in MB
          - gc_triggered (bool): True if measured immediately after a Full GC
          - open_fds (int): Number of open OS file descriptors / handles
        """
        if not snapshots:
            return {
                "verdict": "HEALTHY",
                "post_gc_slope_mb_per_hr": 0.0,
                "peak_fd_utilization": 0.0,
                "memory_leak": False,
                "fd_leak": False,
            }

        # 1. Isolate Post-GC baseline floor snapshots to eliminate sawtooth noise
        gc_points = [s for s in snapshots if s.get("gc_triggered")]
        if len(gc_points) < 2:
            gc_points = [snapshots[0], snapshots[-1]]

        first_gc = gc_points[0]
        last_gc = gc_points[-1]
        delta_hours = (last_gc["timestamp_min"] - first_gc["timestamp_min"]) / 60.0

        if delta_hours > 0:
            slope_mb_per_hr = round((last_gc["rss_mb"] - first_gc["rss_mb"]) / delta_hours, 2)
        else:
            slope_mb_per_hr = 0.0

        memory_leak = slope_mb_per_hr > leak_slope_threshold_mb_per_hr

        # 2. Evaluate File Descriptor / Handle leak
        peak_fds = max(s["open_fds"] for s in snapshots)
        peak_fd_utilization = round(peak_fds / float(max_fd_limit), 4)

        monotonic_fd_growth = (
            len(gc_points) >= 3
            and all(
                gc_points[i]["open_fds"] < gc_points[i + 1]["open_fds"]
                for i in range(len(gc_points) - 1)
            )
            and (gc_points[-1]["open_fds"] - gc_points[0]["open_fds"]) >= 50
        )

        fd_leak = (peak_fd_utilization >= 0.80) or monotonic_fd_growth

        if memory_leak and fd_leak:
            verdict = "CRITICAL_DUAL_LEAK"
        elif memory_leak:
            verdict = "MEMORY_LEAK"
        elif fd_leak:
            verdict = "FD_LEAK"
        else:
            verdict = "HEALTHY"

        return {
            "verdict": verdict,
            "post_gc_slope_mb_per_hr": slope_mb_per_hr,
            "peak_fd_utilization": peak_fd_utilization,
            "memory_leak": memory_leak,
            "fd_leak": fd_leak,
        }


if __name__ == "__main__":
    sol = Solution()

    # Case 1: Benign GC Sawtooth (RSS spikes to 140MB before GC, but drops back to ~48MB after every GC)
    sawtooth_trace = [
        {"timestamp_min": 0, "rss_mb": 48.0, "gc_triggered": True, "open_fds": 64},
        {"timestamp_min": 30, "rss_mb": 135.0, "gc_triggered": False, "open_fds": 72},
        {"timestamp_min": 60, "rss_mb": 48.5, "gc_triggered": True, "open_fds": 65},
        {"timestamp_min": 90, "rss_mb": 142.0, "gc_triggered": False, "open_fds": 70},
        {"timestamp_min": 120, "rss_mb": 49.0, "gc_triggered": True, "open_fds": 64},
    ]
    res1 = sol.analyze_soak_telemetry(sawtooth_trace)
    assert res1["verdict"] == "HEALTHY", f"Expected HEALTHY for GC sawtooth, got {res1}"
    assert res1["post_gc_slope_mb_per_hr"] == 0.5

    # Case 2: True Post-GC Heap Leak (Post-GC floor climbs from 50MB -> 86MB -> 122MB over 2 hours = 36 MB/hr)
    heap_leak_trace = [
        {"timestamp_min": 0, "rss_mb": 50.0, "gc_triggered": True, "open_fds": 60},
        {"timestamp_min": 60, "rss_mb": 86.0, "gc_triggered": True, "open_fds": 62},
        {"timestamp_min": 120, "rss_mb": 122.0, "gc_triggered": True, "open_fds": 61},
    ]
    res2 = sol.analyze_soak_telemetry(heap_leak_trace)
    assert res2["verdict"] == "MEMORY_LEAK", f"Expected MEMORY_LEAK, got {res2}"
    assert res2["post_gc_slope_mb_per_hr"] == 36.0

    # Case 3: Silent Socket / File Descriptor Leak (RAM flat at 50MB, but open FDs climb monotonically)
    fd_leak_trace = [
        {"timestamp_min": 0, "rss_mb": 50.0, "gc_triggered": True, "open_fds": 80},
        {"timestamp_min": 60, "rss_mb": 50.2, "gc_triggered": True, "open_fds": 340},
        {"timestamp_min": 120, "rss_mb": 50.4, "gc_triggered": True, "open_fds": 890},
    ]
    res3 = sol.analyze_soak_telemetry(fd_leak_trace, max_fd_limit=1024)
    assert res3["verdict"] == "FD_LEAK", f"Expected FD_LEAK, got {res3}"
    assert res3["fd_leak"] is True and res3["memory_leak"] is False

    print("All 3 Python OS Memory & File-Descriptor Leak Detector test cases passed!")

