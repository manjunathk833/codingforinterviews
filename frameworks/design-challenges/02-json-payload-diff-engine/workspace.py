"""Blank Workspace — Lab 03: Recursive JSON Payload & Schema Diff Engine."""
from typing import Any, Dict, List, Optional, Set


def diff_payloads(
    expected: Any,
    actual: Any,
    ignore_keys: Optional[Set[str]] = None,
    path: str = "$",
) -> List[Dict[str, Any]]:
    """Recursively diff `expected` vs `actual` and return JSONPath mismatch entries."""
    raise NotImplementedError("Implement diff_payloads()")
