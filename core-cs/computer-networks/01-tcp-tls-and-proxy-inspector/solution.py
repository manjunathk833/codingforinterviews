#!/usr/bin/env python3
"""
Networks Lab 01: TCP/TLS Handshakes, SYN Backlogs & SASE Proxy Inspector.
"""

from typing import Dict, Any


class Solution:
    def evaluate_network_profile(
        self,
        rtt_ms: float,
        num_requests: int,
        tls_version: str = "1.3",
        keep_alive: bool = True,
        concurrent_burst: int = 1,
        server_backlog: int = 128,
    ) -> Dict[str, Any]:
        """
        Compute end-to-end protocol latency and detect TCP SYN backlog overflow.

        Handshake RTT cost per new connection:
          - TCP 3-way handshake: 1 RTT
          - TLS 1.2: 2 RTTs
          - TLS 1.3: 1 RTT
          - Application HTTP request/response: 1 RTT per request
        """
        tcp_rtts = 1
        tls_rtts = 1 if tls_version == "1.3" else 2
        handshake_ms = (tcp_rtts + tls_rtts) * rtt_ms
        request_ms = rtt_ms

        if keep_alive:
            # Handshake paid once, followed by num_requests over persistent connection
            total_latency_ms = handshake_ms + (num_requests * request_ms)
        else:
            # Every request pays full TCP + TLS handshake + HTTP roundtrip
            total_latency_ms = num_requests * (handshake_ms + request_ms)

        dropped_connections = max(0, concurrent_burst - server_backlog)
        syn_backlog_overflow = dropped_connections > 0

        return {
            "total_latency_ms": round(total_latency_ms, 2),
            "handshake_overhead_ms": round(
                handshake_ms if keep_alive else num_requests * handshake_ms, 2
            ),
            "syn_backlog_overflow": syn_backlog_overflow,
            "dropped_connections": dropped_connections,
        }


if __name__ == "__main__":
    sol = Solution()

    # Case 1: Unpooled HTTP/1.1 + TLS 1.2 across 10 requests at 50ms RTT
    # Each request = (1 TCP + 2 TLS + 1 HTTP) * 50ms = 200ms -> 10 requests = 2000ms
    unpooled = sol.evaluate_network_profile(
        rtt_ms=50.0, num_requests=10, tls_version="1.2", keep_alive=False
    )
    assert unpooled["total_latency_ms"] == 2000.0, f"Unexpected latency: {unpooled}"
    assert unpooled["handshake_overhead_ms"] == 1500.0

    # Case 2: Pooled HTTP/2 + TLS 1.3 across 10 requests at 50ms RTT
    # Initial handshake = (1 TCP + 1 TLS) * 50ms = 100ms + (10 * 50ms) = 600ms (70% faster!)
    pooled = sol.evaluate_network_profile(
        rtt_ms=50.0, num_requests=10, tls_version="1.3", keep_alive=True
    )
    assert pooled["total_latency_ms"] == 600.0, f"Unexpected latency: {pooled}"
    assert pooled["handshake_overhead_ms"] == 100.0

    # Case 3: Linux Default TCPServer Backlog (5) vs 32 Concurrent CI Workers
    overflow = sol.evaluate_network_profile(
        rtt_ms=10.0, num_requests=32, concurrent_burst=32, server_backlog=5
    )
    assert overflow["syn_backlog_overflow"] is True
    assert overflow["dropped_connections"] == 27

    print("All 3 Python Computer Networks TCP/TLS & Backlog test cases passed!")

