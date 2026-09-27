"""SDET Challenge: Custom Retry Analyzer with Exponential Backoff"""
from typing import Callable, Type, Any


class RetryConfig:
    def __init__(self, max_retries: int = 3, initial_delay_ms: int = 10, backoff_multiplier: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay_ms = initial_delay_ms
        self.backoff_multiplier = backoff_multiplier


class Solution:
    def execute_with_retry(
        self,
        task: Callable[[], Any],
        config: RetryConfig,
        retriable_exception: Type[BaseException],
    ) -> Any:
        """Executes task with exponential backoff on retriable exceptions."""
        attempt = 0
        delay = config.initial_delay_ms

        while True:
            try:
                attempt += 1
                return task()
            except BaseException as e:
                if not isinstance(e, retriable_exception) or attempt > config.max_retries:
                    raise e
                delay *= config.backoff_multiplier


if __name__ == "__main__":
    engine = Solution()
    config = RetryConfig(max_retries=3, initial_delay_ms=10, backoff_multiplier=2.0)

    # Test 1: Succeeds on attempt 3
    count1 = [0]

    def flaky_task():
        count1[0] += 1
        if count1[0] < 3:
            raise ConnectionError("503 Gateway Timeout")
        return "SUCCESS_DATA"

    res1 = engine.execute_with_retry(flaky_task, config, ConnectionError)
    assert res1 == "SUCCESS_DATA" and count1[0] == 3, f"Test 1 Failed: count={count1[0]}"

    # Test 2: Fails immediately on non-retriable exception
    count2 = [0]

    def bad_request_task():
        count2[0] += 1
        raise ValueError("400 Bad Request")

    caught_non_retriable = False
    try:
        engine.execute_with_retry(bad_request_task, config, ConnectionError)
    except ValueError:
        caught_non_retriable = True
    assert caught_non_retriable and count2[0] == 1, f"Test 2 Failed: count={count2[0]}"

    # Test 3: Exhausts retries and re-raises
    count3 = [0]

    def always_fail_task():
        count3[0] += 1
        raise ConnectionError("Hard outage")

    caught_exhausted = False
    try:
        engine.execute_with_retry(always_fail_task, config, ConnectionError)
    except ConnectionError:
        caught_exhausted = True
    assert caught_exhausted and count3[0] == 4, f"Test 3 Failed: expected 4 attempts, got {count3[0]}"

    print("All 3 Python Retry Analyzer test cases passed!")
