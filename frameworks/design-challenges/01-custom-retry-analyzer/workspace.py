"""Blank Workspace — Lab 02: Custom Retry Analyzer & Flaky Quarantine Engine."""
from typing import Any, Callable, Dict


class RetryAnalyzer:
    def __init__(self, max_retries: int = 2, base_delay_ms: int = 20) -> None:
        self.max_retries = max_retries
        self.base_delay_ms = base_delay_ms

    def should_retry(self, exc: BaseException, attempt: int) -> bool:
        raise NotImplementedError("Implement should_retry()")

    def backoff_ms(self, attempt: int) -> int:
        raise NotImplementedError("Implement backoff_ms()")

    def execute(self, fn: Callable[[], Any]) -> Dict[str, Any]:
        """Return `{'passed': bool, 'attempts': int, 'flaky': bool, 'result': Any}` or re-raise final error."""
        raise NotImplementedError("Implement execute()")
