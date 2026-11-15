"""Blank Workspace — Lab 05: Fluent Immutable Test Data Builder & Tenant Factory."""
from dataclasses import dataclass, replace
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class BookingFixtureBuilder:
    flight_number: str = "AI-202"
    seat: str = "1A"
    tenant_id: str = "tenant-default"
    bags_kg: Tuple[int, ...] = ()

    def with_flight(self, flight_number: str) -> "BookingFixtureBuilder":
        raise NotImplementedError("Implement with_flight()")

    def with_seat(self, seat: str) -> "BookingFixtureBuilder":
        raise NotImplementedError("Implement with_seat()")

    def with_tenant(self, tenant_id: str) -> "BookingFixtureBuilder":
        raise NotImplementedError("Implement with_tenant()")

    def add_bag(self, weight_kg: int) -> "BookingFixtureBuilder":
        raise NotImplementedError("Implement add_bag()")

    def build(self) -> Dict[str, Any]:
        raise NotImplementedError("Implement build()")
