"""Blank Workspace — Lab 13: BOLA Tenant Guard, JWT `alg:none` Verifier & Prompt Shield."""
from typing import Any, Dict


def authorize_order_access(
    jwt_header: Dict[str, Any],
    jwt_claims: Dict[str, Any],
    resource_owner_tenant: str,
    now_ts: int = 1700000000,
) -> int:
    """Return HTTP status: 200 (authorized), 401 (bad alg / expired), or 403 (BOLA cross-tenant)."""
    raise NotImplementedError("Implement authorize_order_access()")


def scan_prompt_injection(user_prompt: str) -> Dict[str, Any]:
    """Return `{'blocked': bool, 'reason': str}` catching override / secret-exfiltration prompts."""
    raise NotImplementedError("Implement scan_prompt_injection()")
