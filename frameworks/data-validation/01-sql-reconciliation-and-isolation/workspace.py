"""Blank Workspace — Lab 10: AeroLedger SQL Webhook Deduplication & Double-Entry Audit."""
import sqlite3
from typing import Any, Dict


def reconcile_ledger(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Tables on `conn`:
      - `webhook_events(event_id TEXT, seq INT, status TEXT, amount_cents INT)`
      - `journal_entries(tx_id TEXT, debit_cents INT, credit_cents INT)`
    Return `{'dedupCapturedCents': int, 'totalDebits': int, 'totalCredits': int, 'balanced': bool}`.
    """
    raise NotImplementedError("Implement reconcile_ledger()")
