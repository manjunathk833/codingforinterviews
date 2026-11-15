"""Blank Workspace — Lab 06: Stateful Microservice Stub & Contract Verifier."""
from typing import Any, Dict, List, Tuple


class StatefulServiceStub:
    def __init__(self) -> None:
        self.journal: List[Dict[str, Any]] = []

    def stub_sequence(self, method: str, path: str, responses: List[Tuple[int, Dict[str, Any]]]) -> None:
        raise NotImplementedError("Implement stub_sequence()")

    def handle(self, method: str, path: str, body: Any = None) -> Dict[str, Any]:
        raise NotImplementedError("Implement handle()")

    def verify_called(self, method: str, path: str, times: int) -> None:
        raise NotImplementedError("Implement verify_called()")
