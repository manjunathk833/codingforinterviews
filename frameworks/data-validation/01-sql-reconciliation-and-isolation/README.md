# Lab 09: AeroLedger — SQL Join Fan-Out, Window Dedup, Composite Index Plans, Seat-12A Locking & Double-Entry Ledger Reconciliation

**Execution Model**: 100% Local Deterministic Verification (`sqlite3` WAL + Multi-Threaded Concurrency Gate — Strictly Zero AI Dependency)

## Overview

This workbench lab accompanies **Course 09 (`09-sql-and-data-engineering`)** and verifies five production Senior/Staff Data-QA invariants against an isolated `AeroLedger` database:

1. **Grain-Safe Joins (`1:N` Fan-Out Prevention)**: Proves that joining `bookings` directly to `baggage_items` inflates `SUM(fare_cents)` 3x, whereas pre-aggregating child rows inside a CTE preserves exact monetary totals.
2. **Window Function Deduplication & State Audits**: Uses `ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY event_id ASC)` and `LAG(status)` to quarantine duplicate webhook deliveries and catch illegal `CANCELLED -> CONFIRMED` state transitions.
3. **Composite B-Tree Index Sargability (`EXPLAIN QUERY PLAN`)**: Verifies that a sargable `(tenant_id, status, booked_at)` range query triggers `SEARCH ... USING COVERING INDEX`, whereas wrapping `SUBSTR(booked_at, 1, 10)` degrades to a full scan.
4. **16-Thread Concurrent Airline Seat `12A` Reservation**: Proves that atomic `BEGIN IMMEDIATE` + partial/unique seat constraints allow **exactly 1 of 16** simultaneous threads to claim Seat `12A` with zero double-bookings.
5. **Stripe-Style Double-Entry Ledger & Outbox CDC Reconciliation**: Asserts `SUM(debit_cents) == SUM(credit_cents)` across accounts and detects orphaned bookings missing from the Kafka/Warehouse `outbox_events` stream.

## Run Locally

```bash
python3 frameworks/data-validation/01-sql-reconciliation-and-isolation/reference_solution.py
```
