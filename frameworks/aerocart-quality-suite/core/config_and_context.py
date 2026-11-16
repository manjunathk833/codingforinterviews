"""
Capstone Layer 1/4: Core Config & Worker Tenant Isolation Context
File: frameworks/aerocart-quality-suite/core/config_and_context.py

Goal:
Build the foundational immutable configuration (`SuiteConfig`) and parallel worker
namespace (`WorkerContext`) imported by both the API Client (Layer 2) and UI Page Object (Layer 3).
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class SuiteConfig:
    base_url: str = "http://127.0.0.1:8085"
    timeout_s: float = 2.0
    max_retries: int = 2

    def validate(self) -> "SuiteConfig":
        """Raise ValueError if timeout_s <= 0, max_retries < 0, or base_url does not start with http."""
        raise NotImplementedError("Implement SuiteConfig.validate()")


@dataclass(frozen=True)
class WorkerContext:
    worker_id: int
    run_id: str

    def tenant_id(self) -> str:
        """Return deterministic tenant namespace: `tenant-{run_id}-w{worker_id}`."""
        raise NotImplementedError("Implement WorkerContext.tenant_id()")

    def isolated_email(self, prefix: str = "qa") -> str:
        """Return collision-free email: `{prefix}+w{worker_id}.{run_id}@aerocart.test`."""
        raise NotImplementedError("Implement WorkerContext.isolated_email()")

    def build_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Return HTTP headers containing `X-Test-Tenant-ID` and optional `Idempotency-Key`."""
        raise NotImplementedError("Implement WorkerContext.build_headers()")
