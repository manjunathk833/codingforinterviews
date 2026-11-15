"""Reference Solution — Capstone Layer 1/4: Core Config & Worker Tenant Isolation Context."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class SuiteConfig:
    base_url: str = "http://127.0.0.1:8085"
    timeout_s: float = 2.0
    max_retries: int = 2

    def validate(self) -> "SuiteConfig":
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        return self


@dataclass(frozen=True)
class WorkerContext:
    worker_id: int
    run_id: str

    def tenant_id(self) -> str:
        if self.worker_id < 0 or not self.run_id.strip():
            raise ValueError("worker_id must be >= 0 and run_id non-empty")
        return f"tenant-{self.run_id.strip()}-w{self.worker_id}"

    def isolated_email(self, prefix: str = "qa") -> str:
        clean = prefix.strip() or "qa"
        return f"{clean}+w{self.worker_id}.{self.run_id.strip()}@aerocart.test"

    def build_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Test-Tenant-ID": self.tenant_id(),
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers
