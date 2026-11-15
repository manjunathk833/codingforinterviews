"""Blank Workspace — Lab 08: API Contract Schema Validator & Concierge Grounding Guard."""
from typing import Any, Dict
from apps.aerocart.server import dispatch_request


def validate_order_contract(payload: Dict[str, Any]) -> bool:
    """Raise ValueError if `orderId`, `status`, or `seat` violate the Order API schema."""
    raise NotImplementedError("Implement validate_order_contract()")


def verify_concierge_grounding(query: str, mode: str = "grounded") -> bool:
    """Query AeroCart `/api/v1/concierge/chat` and return True iff `answer` is faithful to `retrievedContexts`."""
    raise NotImplementedError("Implement verify_concierge_grounding()")
