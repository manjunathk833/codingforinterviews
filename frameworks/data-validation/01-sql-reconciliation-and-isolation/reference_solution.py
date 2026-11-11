#!/usr/bin/env python3
"""
Deterministic Local Verification Lab for Course 09 (SQL, PostgreSQL & Data Validation Engineering):
AeroLedger v1.0 — Grain-Safe Joins, Window Dedup, Sargable Covering Indexes,
Concurrent Seat-12A Isolation, and Double-Entry Ledger + Outbox Reconciliation.
"""

from __future__ import annotations

import sqlite3
import tempfile
import threading
import pathlib


def verify_1_join_fanout_vs_cte_grain() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE bookings (
            booking_id TEXT PRIMARY KEY,
            fare_cents INTEGER NOT NULL CHECK (fare_cents >= 0)
        );
        CREATE TABLE baggage_items (
            bag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL REFERENCES bookings(booking_id),
            weight_kg INTEGER NOT NULL
        );
        INSERT INTO bookings VALUES ('BK-101', 40000), ('BK-102', 25000);
        INSERT INTO baggage_items (booking_id, weight_kg) VALUES
            ('BK-101', 20), ('BK-101', 23), ('BK-101', 15);
        """
    )
    naive_sum = conn.execute(
        """
        SELECT SUM(b.fare_cents)
        FROM bookings b
        LEFT JOIN baggage_items bg ON bg.booking_id = b.booking_id
        """
    ).fetchone()[0]
    assert naive_sum == 145000, f"Expected naive 3x fan-out inflation (145000), got {naive_sum}"

    safe_row = conn.execute(
        """
        WITH bag_summary AS (
            SELECT booking_id, COUNT(*) AS bag_count
            FROM baggage_items
            GROUP BY booking_id
        )
        SELECT SUM(b.fare_cents), COALESCE(SUM(bs.bag_count), 0)
        FROM bookings b
        LEFT JOIN bag_summary bs ON bs.booking_id = b.booking_id
        """
    ).fetchone()
    assert safe_row == (65000, 3), f"Expected exact (65000, 3), got {safe_row}"
    conn.close()


def verify_2_window_dedup_and_lag_state_audit() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE webhook_events (
            event_id INTEGER PRIMARY KEY,
            booking_id TEXT NOT NULL,
            idempotency_key TEXT NOT NULL,
            status TEXT NOT NULL
        );
        INSERT INTO webhook_events VALUES
            (1, 'BK-201', 'idem-1', 'PENDING'),
            (2, 'BK-201', 'idem-1', 'PENDING'),
            (3, 'BK-201', 'idem-2', 'CANCELLED'),
            (4, 'BK-201', 'idem-3', 'CONFIRMED');
        """
    )
    duplicates = conn.execute(
        """
        WITH ranked AS (
            SELECT event_id, idempotency_key,
                   ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id ASC) AS rn
            FROM webhook_events
        )
        SELECT event_id FROM ranked WHERE rn > 1
        """
    ).fetchall()
    assert [r[0] for r in duplicates] == [2], f"Expected duplicate event_id [2], got {duplicates}"

    illegal_transitions = conn.execute(
        """
        WITH deduped AS (
            SELECT event_id, booking_id, status,
                   ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id ASC) AS rn
            FROM webhook_events
        ),
        ordered AS (
            SELECT booking_id,
                   LAG(status) OVER (PARTITION BY booking_id ORDER BY event_id ASC) AS prev_status,
                   status AS next_status
            FROM deduped
            WHERE rn = 1
        )
        SELECT prev_status, next_status
        FROM ordered
        WHERE prev_status = 'CANCELLED' AND next_status = 'CONFIRMED'
        """
    ).fetchall()
    assert illegal_transitions == [("CANCELLED", "CONFIRMED")], f"Unexpected transitions: {illegal_transitions}"
    conn.close()


def verify_3_composite_index_sargability_plan() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE ledger_orders (
            order_id INTEGER PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            status TEXT NOT NULL,
            booked_at TEXT NOT NULL,
            fare_cents INTEGER NOT NULL
        );
        CREATE INDEX idx_orders_covering
            ON ledger_orders (tenant_id, status, booked_at, fare_cents);
        """
    )
    sargable_plan = " ".join(
        row[3]
        for row in conn.execute(
            """
            EXPLAIN QUERY PLAN
            SELECT fare_cents
            FROM ledger_orders
            WHERE tenant_id = 't-airline'
              AND status = 'CONFIRMED'
              AND booked_at >= '2026-11-10T00:00:00Z'
              AND booked_at <  '2026-11-11T00:00:00Z'
            """
        ).fetchall()
    )
    assert "USING COVERING INDEX idx_orders_covering" in sargable_plan, sargable_plan
    conn.close()


def verify_4_concurrent_seat_12a_isolation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_file = pathlib.Path(tmp) / "seat_lock.db"
        setup_conn = sqlite3.connect(str(db_file))
        setup_conn.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE seat_inventory (
                flight_id TEXT NOT NULL,
                seat_no TEXT NOT NULL,
                passenger_id TEXT,
                version INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (flight_id, seat_no)
            );
            INSERT INTO seat_inventory VALUES ('AI-302', '12A', NULL, 0);
            """
        )
        setup_conn.close()

        barrier = threading.Barrier(16)
        winners: list[str] = []
        lock = threading.Lock()

        def attempt_claim(worker_idx: int) -> None:
            c = sqlite3.connect(str(db_file), timeout=10.0, isolation_level=None)
            try:
                barrier.wait()
                c.execute("BEGIN IMMEDIATE")
                cur = c.execute(
                    """
                    UPDATE seat_inventory
                    SET passenger_id = ?, version = version + 1
                    WHERE flight_id = 'AI-302' AND seat_no = '12A' AND passenger_id IS NULL
                    """,
                    (f"PAX-{worker_idx:02d}",),
                )
                c.execute("COMMIT")
                if cur.rowcount == 1:
                    with lock:
                        winners.append(f"PAX-{worker_idx:02d}")
            finally:
                c.close()

        threads = [threading.Thread(target=attempt_claim, args=(i,)) for i in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(winners) == 1, f"Seat 12A double-booking detected! Winners: {winners}"


def verify_5_double_entry_ledger_and_outbox_reconciliation() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE bookings (booking_id TEXT PRIMARY KEY, total_cents INTEGER NOT NULL);
        CREATE TABLE ledger_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_id TEXT NOT NULL,
            account_code TEXT NOT NULL,
            debit_cents INTEGER NOT NULL DEFAULT 0,
            credit_cents INTEGER NOT NULL DEFAULT 0,
            CHECK (debit_cents >= 0 AND credit_cents >= 0),
            CHECK ((debit_cents > 0 AND credit_cents = 0) OR (credit_cents > 0 AND debit_cents = 0))
        );
        CREATE TABLE outbox_events (event_id TEXT PRIMARY KEY, aggregate_id TEXT NOT NULL);

        INSERT INTO bookings VALUES ('BK-900', 45000), ('BK-901', 32000);
        INSERT INTO ledger_entries (tx_id, account_code, debit_cents, credit_cents) VALUES
            ('TX-900', 'CUSTOMER_CLEARING', 45000, 0),
            ('TX-900', 'AIRLINE_REVENUE',   0, 45000),
            ('TX-901', 'CUSTOMER_CLEARING', 32000, 0),
            ('TX-901', 'AIRLINE_REVENUE',   0, 32000);
        INSERT INTO outbox_events VALUES ('EVT-900', 'BK-900');
        """
    )
    imbalance = conn.execute(
        "SELECT COALESCE(SUM(debit_cents) - SUM(credit_cents), 0) FROM ledger_entries"
    ).fetchone()[0]
    assert imbalance == 0, f"Double-entry ledger out of balance by {imbalance} cents!"

    missing_outbox = conn.execute(
        """
        SELECT b.booking_id
        FROM bookings b
        LEFT JOIN outbox_events o ON o.aggregate_id = b.booking_id
        WHERE o.event_id IS NULL
        """
    ).fetchall()
    assert [r[0] for r in missing_outbox] == ["BK-901"], f"Expected orphan ['BK-901'], got {missing_outbox}"
    conn.close()


def main() -> None:
    verify_1_join_fanout_vs_cte_grain()
    verify_2_window_dedup_and_lag_state_audit()
    verify_3_composite_index_sargability_plan()
    verify_4_concurrent_seat_12a_isolation()
    verify_5_double_entry_ledger_and_outbox_reconciliation()
    print(
        "✓ AeroLedger SQL & Data Validation Lab PASSED: "
        "1:N Join Grain, Window Dedup/LAG, Covering B-Tree Plan, 16-Thread Seat-12A Lock & Double-Entry Reconciliation verified!"
    )


if __name__ == "__main__":
    main()
