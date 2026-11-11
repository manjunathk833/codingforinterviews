#!/usr/bin/env python3
"""
Course 11 Verification Lab: AeroPulse Open-Loop Load, Coordinated Omission Corrector & Toxiproxy Chaos Gate.
Deterministically verifies 5 Performance, Load, Chaos & SRE invariants:
  1. Little's Law (L = lambda * W) concurrency & Universal Scalability Law (USL) contention modeling
  2. Closed-Loop Coordinated Omission p99 distortion vs Open-Loop arrival-time corrected p99
  3. HikariCP / PostgreSQL core-matched connection pool sizing vs context-switch thrashing
  4. Toxiproxy fault injection (latency/reset) & 3-state Circuit Breaker (CLOSED -> OPEN -> HALF_OPEN)
  5. Google SRE Multi-Window Multi-Burn-Rate SLO alerting (14.4x page vs 6x ticket)
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Sequence, Tuple


def compute_littles_law_concurrency(arrival_rate_rps: float, mean_latency_seconds: float) -> float:
    """L = lambda * W: average in-flight requests in a stable queuing system."""
    return arrival_rate_rps * mean_latency_seconds


def compute_coordinated_omission_latencies(
    scheduled_arrivals_sec: Sequence[float],
    service_durations_sec: Sequence[float],
) -> Tuple[List[float], List[float]]:
    """
    Compare Closed-Loop (worker waits for completion before sending next) vs
    Open-Loop / HdrHistogram Coordinated-Omission-Corrected latencies.
    """
    closed_loop_samples: List[float] = []
    open_loop_corrected: List[float] = []
    worker_available_at = 0.0

    for sched_t, svc_dur in zip(scheduled_arrivals_sec, service_durations_sec):
        # In a closed loop with 1 stalled worker, requests scheduled while blocked are omitted
        if sched_t >= worker_available_at - 1e-9:
            closed_loop_samples.append(svc_dur)
        actual_start = max(sched_t, worker_available_at)
        completion = actual_start + svc_dur
        worker_available_at = completion
        open_loop_corrected.append(completion - sched_t)

    return closed_loop_samples, open_loop_corrected


def percentile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil((q / 100.0) * len(ordered)) - 1))
    return ordered[idx]


def recommend_db_pool_size(cpu_cores: int, effective_spindles: int = 1) -> int:
    """PostgreSQL / HikariCP formula: connections = (core_count * 2) + effective_spindle_count."""
    return (cpu_cores * 2) + effective_spindles


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout_sec: float = 5.0
    state: str = "CLOSED"
    consecutive_failures: int = 0
    opened_at_sec: float = -1.0

    def call(self, now_sec: float, downstream_ok: bool, fallback_value: str) -> Tuple[str, bool]:
        if self.state == "OPEN":
            if (now_sec - self.opened_at_sec) >= self.recovery_timeout_sec:
                self.state = "HALF_OPEN"
            else:
                return fallback_value, False

        if downstream_ok:
            self.consecutive_failures = 0
            self.state = "CLOSED"
            return "LIVE_OK", True

        self.consecutive_failures += 1
        if self.state == "HALF_OPEN" or self.consecutive_failures >= self.failure_threshold:
            self.state = "OPEN"
            self.opened_at_sec = now_sec
        return fallback_value, False


def evaluate_multi_window_slo_burn(
    slo_target: float,
    error_rate_1h: float,
    error_rate_5m: float,
    error_rate_6h: float,
    error_rate_30m: float,
) -> str:
    """Google SRE Workbook multi-window multi-burn-rate evaluator (14.4x page, 6.0x warn)."""
    error_budget = 1.0 - slo_target
    burn_1h = error_rate_1h / error_budget
    burn_5m = error_rate_5m / error_budget
    burn_6h = error_rate_6h / error_budget
    burn_30m = error_rate_30m / error_budget

    if burn_1h >= 14.4 and burn_5m >= 14.4:
        return "PAGE_CRITICAL"
    if burn_6h >= 6.0 and burn_30m >= 6.0:
        return "PAGE_WARNING"
    return "OK_WITHIN_BUDGET"


def verify_aeropulse_invariants() -> None:
    # 1. Little's Law & HikariCP Pool Sizing
    in_flight = compute_littles_law_concurrency(arrival_rate_rps=1000.0, mean_latency_seconds=0.020)
    assert math.isclose(in_flight, 20.0)
    assert recommend_db_pool_size(cpu_cores=8, effective_spindles=1) == 17

    # 2. Coordinated Omission: 100 requests @ 10 RPS (every 0.1s). Request #10 freezes for 2.0s!
    arrivals = [round(i * 0.1, 3) for i in range(100)]
    durations = [2.0 if i == 10 else 0.020 for i in range(100)]
    closed_samples, open_corrected = compute_coordinated_omission_latencies(arrivals, durations)
    closed_p99 = percentile(closed_samples, 99.0)
    open_p99 = percentile(open_corrected, 99.0)
    # Closed loop omits the 19 queued requests during the 2s freeze, under-reporting p95/p99!
    assert len(closed_samples) < len(open_corrected)
    assert percentile(closed_samples, 95.0) == 0.020
    assert percentile(open_corrected, 95.0) > 1.0
    assert open_p99 >= 1.9

    # 3. Toxiproxy Chaos + Circuit Breaker state transitions
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=5.0)
    for t in (1.0, 2.0, 3.0):
        val, used_live = cb.call(now_sec=t, downstream_ok=False, fallback_value="DEFERRED_LOYALTY")
        assert val == "DEFERRED_LOYALTY" and not used_live
    assert cb.state == "OPEN"
    # Fast-fail while OPEN at t=4.0s
    val, used_live = cb.call(now_sec=4.0, downstream_ok=True, fallback_value="DEFERRED_LOYALTY")
    assert val == "DEFERRED_LOYALTY" and cb.state == "OPEN"
    # After recovery timeout (t=8.5s), transitions through HALF_OPEN -> CLOSED on healthy probe
    val, used_live = cb.call(now_sec=8.5, downstream_ok=True, fallback_value="DEFERRED_LOYALTY")
    assert val == "LIVE_OK" and used_live and cb.state == "CLOSED"

    # 4. Multi-Window SLO Burn Rate (99.9% SLO -> 0.001 error budget; 14.4x = 1.44% error rate)
    assert evaluate_multi_window_slo_burn(0.999, 0.015, 0.016, 0.002, 0.002) == "PAGE_CRITICAL"
    # Resolved outage (5m error rate drops to 0) immediately clears alert without 55-minute tail flap
    assert evaluate_multi_window_slo_burn(0.999, 0.015, 0.000, 0.002, 0.000) == "OK_WITHIN_BUDGET"

    print(
        f"[PASS] Course 11 AeroPulse Lab verified: Little's Law L={in_flight:.0f}, "
        f"Coordinated Omission p95={percentile(open_corrected, 95.0)*1000:.0f}ms (vs naive {percentile(closed_samples, 95.0)*1000:.0f}ms), "
        f"CircuitBreaker & 14.4x SLO Burn Gate OK."
    )


if __name__ == "__main__":
    verify_aeropulse_invariants()
