"""Blank Workspace — Lab 04: Token Bucket Rate-Limited Test Client & Backpressure."""
import threading


class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_per_sec: float, initial_ts: float = 0.0) -> None:
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self._lock = threading.Lock()

    def try_acquire(self, now_ts: float) -> bool:
        """Refill tokens up to `now_ts`, honor cooldown, and consume 1 token if >= 1.0 available."""
        raise NotImplementedError("Implement try_acquire()")

    def on_retry_after(self, retry_after_s: float, now_ts: float) -> None:
        """Pause acquisitions until `now_ts + retry_after_s`."""
        raise NotImplementedError("Implement on_retry_after()")
