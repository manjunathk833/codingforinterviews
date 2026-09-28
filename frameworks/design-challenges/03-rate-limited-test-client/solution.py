"""SDET Challenge: Thread-Safe Rate-Limited Test Client (Token Bucket Algorithm)"""
import threading
import time


class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_tokens_per_second: float):
        self.capacity = float(capacity)
        self.refill_rate_per_sec = refill_tokens_per_second
        self.available_tokens = float(capacity)
        self.last_refill_timestamp = time.perf_counter()
        self.lock = threading.Lock()

    def try_acquire(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.available_tokens >= tokens:
                self.available_tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.perf_counter()
        elapsed = now - self.last_refill_timestamp
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate_per_sec
            self.available_tokens = min(self.capacity, self.available_tokens + tokens_to_add)
            self.last_refill_timestamp = now


if __name__ == "__main__":
    limiter = TokenBucketRateLimiter(capacity=5, refill_tokens_per_second=10.0)

    # Test 1: Immediate burst consumes 5 tokens
    for i in range(5):
        assert limiter.try_acquire(1) is True, f"Test 1 Failed: Token {i} should be acquired"

    # Test 2: 6th request immediately fails
    assert limiter.try_acquire(1) is False, "Test 2 Failed: Burst should be exhausted"

    # Test 3: Wait 250ms -> refills ~2.5 tokens, acquiring 2 succeeds
    time.sleep(0.25)
    assert limiter.try_acquire(2) is True, "Test 3 Failed: Refilled tokens should be acquirable"

    print("All 3 Python Token Bucket Rate Limiter test cases passed!")
