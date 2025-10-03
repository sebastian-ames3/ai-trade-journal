from typing import List, Optional
from datetime import date, datetime
from sqlmodel import SQLModel, create_engine, Session, select

from .models import JournalEntry
from src.settings import Settings
from src.journal.models import JournalEntry

_engine = None
_db_initialized = False


def init_db(settings: Optional[Settings] = None) -> None:
    """Initialize DB engine and create tables if they do not exist."""
    global _engine, _db_initialized
    if _engine is None:
        # SQLite file in project root; adjust path as needed
        _engine = create_engine("sqlite:///ai_trader.sqlite", echo=False)

    if not _db_initialized:
        SQLModel.metadata.create_all(_engine)
        _db_initialized = True

def _session() -> Session:
    if _engine is None:
        init_db()
    return Session(_engine)

from datetime import date  # ensure this import exists

def create_entry(
    *,
    symbol: str,
    strategy: str,
    entry_action: str,            # "BTO" or "STO"
    entry_date: Optional[date] = None,
    entry_price: float = 0.0,
    size: int = 1,
    direction: str = "neutral",   # metadata
    notes: Optional[str] = None,
    tags_csv: Optional[str] = None,
) -> JournalEntry:
    resolved_date = entry_date or date.today()
    normalized_symbol = (symbol or "").strip().upper()
    normalized_tags = (tags_csv or "").strip()

    entry = JournalEntry(
        symbol=normalized_symbol,
        strategy=strategy,
        entry_action=entry_action,
        entry_date=resolved_date,
        entry_price=float(entry_price),
        size=int(size),
        direction=direction,
        notes=notes,
        tags_csv=normalized_tags,
        status="open",
    )

    with _session() as s:
        s.add(entry)
        s.commit()
        s.refresh(entry)
        return entry


def list_entries(tag: Optional[str] = None) -> List[JournalEntry]:
    with _session() as s:
        stmt = select(JournalEntry).order_by(JournalEntry.created_at.desc())
        rows = list(s.exec(stmt))
    if tag:
        return [e for e in rows if tag in e.tags]
    return rows

def update_entry(entry_id: int, **patch) -> JournalEntry:
    with _session() as s:
        obj = s.get(JournalEntry, entry_id)
        if obj is None:
            raise ValueError(f"Journal entry {entry_id} not found")
        for k, v in patch.items():
            setattr(obj, k, v)
        s.add(obj)
        s.commit()
        s.refresh(obj)
        return obj

def get_entry(entry_id: int) -> Optional[JournalEntry]:
    with _session() as s:
        return s.get(JournalEntry, entry_id)

def close_entry(entry_id: int, exit_price: float, exit_date: Optional[date] = None) -> JournalEntry:
    if exit_date is None:
        exit_date = date.today()
    with _session() as s:
        j = s.get(JournalEntry, entry_id)
        if not j:
            raise ValueError(f"Entry {entry_id} not found")
        j.exit_price = float(exit_price)
        j.exit_date = exit_date
        j.status = "closed"
        s.add(j)
        s.commit()
        s.refresh(j)
        return j

def delete_entry(entry_id: int) -> None:
    # hard delete for now (simple dev DB). If you prefer soft delete, add a boolean column.
    with _session() as s:
        j = s.get(JournalEntry, entry_id)
        if j:
            s.delete(j)
            s.commit()

def list_entries_by_status(status: str) -> List[JournalEntry]:
    with _session() as s:
        q = select(JournalEntry).where(JournalEntry.status == status)
        return list(s.exec(q).all())