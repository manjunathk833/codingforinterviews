"""Blank Workspace — Lab 11: Dockerfile Cache Auditor & K8s OOMKilled (Exit 137) Guard."""
from typing import Any, Dict, List


def audit_container_spec(
    dockerfile_lines: List[str],
    pod_limit_mb: int,
    jvm_heap_mb: int,
) -> Dict[str, Any]:
    """Return `{'passed': bool, 'findings': List[str]}` using codes `CACHE_BUST`, `FLOATING_TAG`, `OOM_RISK_137`."""
    raise NotImplementedError("Implement audit_container_spec()")
