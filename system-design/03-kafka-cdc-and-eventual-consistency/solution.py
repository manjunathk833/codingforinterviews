#!/usr/bin/env python3
"""
System Design Lab 03: Transactional Outbox, CDC Relay & Idempotent Consumer Deduplication.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class OutboxRecord:
    event_id: str
    aggregate_id: str
    event_type: str
    payload: Dict[str, str]
    published: bool = False


@dataclass
class TransactionalOrderStore:
    orders: Dict[str, Dict[str, str]] = field(default_factory=dict)
    outbox: List[OutboxRecord] = field(default_factory=list)

    def create_order_atomic(self, order_id: str, tenant_id: str, seat: str, fail_before_commit: bool = False) -> None:
        staged_order = {"order_id": order_id, "tenant_id": tenant_id, "seat": seat, "status": "PENDING"}
        staged_event = OutboxRecord(
            event_id=f"evt-{order_id}",
            aggregate_id=order_id,
            event_type="ORDER_CREATED",
            payload={"order_id": order_id, "tenant_id": tenant_id, "seat": seat},
        )
        if fail_before_commit:
            raise RuntimeError("Simulated DB transaction rollback — neither order nor outbox persisted")
        self.orders[order_id] = staged_order
        self.outbox.append(staged_event)


class IdempotentProjectionConsumer:
    def __init__(self) -> None:
        self.processed_event_ids: Set[str] = set()
        self.confirmed_orders: Dict[str, str] = {}
        self.side_effect_executions: int = 0

    def consume(self, event: OutboxRecord) -> bool:
        if event.event_id in self.processed_event_ids:
            return False
        self.processed_event_ids.add(event.event_id)
        self.confirmed_orders[event.aggregate_id] = "CONFIRMED"
        self.side_effect_executions += 1
        return True


def relay_outbox_with_duplicate_delivery(store: TransactionalOrderStore, consumer: IdempotentProjectionConsumer) -> None:
    for rec in store.outbox:
        if not rec.published:
            # Simulate Kafka at-least-once delivery where broker timeout causes 2 deliveries of same event_id
            consumer.consume(rec)
            consumer.consume(rec)
            rec.published = True


if __name__ == "__main__":
    store = TransactionalOrderStore()
    consumer = IdempotentProjectionConsumer()

    # 1. Verify atomic rollback leaves zero zombie outbox messages
    try:
        store.create_order_atomic("ord-rollback", "tenant-a", "1A", fail_before_commit=True)
    except RuntimeError:
        pass
    assert "ord-rollback" not in store.orders
    assert len(store.outbox) == 0

    # 2. Verify atomic commit + duplicate broker delivery executes side effect exactly once
    store.create_order_atomic("ord-101", "tenant-a", "2B")
    store.create_order_atomic("ord-102", "tenant-b", "2B")
    relay_outbox_with_duplicate_delivery(store, consumer)

    assert consumer.side_effect_executions == 2, f"Expected 2 idempotent executions, got {consumer.side_effect_executions}"
    assert consumer.confirmed_orders["ord-101"] == "CONFIRMED"
    assert consumer.confirmed_orders["ord-102"] == "CONFIRMED"
    assert all(r.published for r in store.outbox)

    print("All 3 Python Transactional Outbox, CDC Relay & Idempotent Consumer test cases passed!")
