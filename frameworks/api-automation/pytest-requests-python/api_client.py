"""Lightweight, production-grade API Client using Python standard library."""
import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class ApiResponse:
    def __init__(self, status_code: int, body: Any, headers: dict, latency_ms: float):
        self.status_code = status_code
        self.body = body
        self.headers = headers
        self.latency_ms = latency_ms

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300


class BaseApiClient:
    def __init__(self, base_url: str = "", default_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = {**self.default_headers, **(headers or {})}

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=merged_headers, method=method.upper())

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw_body = resp.read().decode("utf-8")
                elapsed_ms = (time.perf_counter() - start) * 1000
                parsed_body = json.loads(raw_body) if raw_body else {}
                return ApiResponse(
                    status_code=resp.status,
                    body=parsed_body,
                    headers=dict(resp.headers),
                    latency_ms=elapsed_ms,
                )
        except urllib.error.HTTPError as e:
            raw_body = e.read().decode("utf-8")
            elapsed_ms = (time.perf_counter() - start) * 1000
            try:
                parsed_body = json.loads(raw_body)
            except Exception:
                parsed_body = {"raw": raw_body}
            return ApiResponse(
                status_code=e.code,
                body=parsed_body,
                headers=dict(e.headers),
                latency_ms=elapsed_ms,
            )
