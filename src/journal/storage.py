from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session, select

from .models import JournalEntry
from src.settings import Settings

_engine = None

def init_db(settings: Optional[Settings] = None) -> None:
    """Initialize DB engine and create tables if they do not exist."""
    global _engine
    if _engine:
        return
    settings = settings or Settings.from_env()
    _engine = create_engine(settings.db_url, echo=False)
    SQLModel.metadata.create_all(_engine)

def _session() -> Session:
    if _engine is None:
        init_db()
    return Session(_engine)

def create_entry(*, symbol: str, direction: str, strategy: str, notes: str = "", tags: List[str] | None = None) -> JournalEntry:
    entry = JournalEntry(symbol=symbol, direction=direction, strategy=strategy, notes=notes)
    if tags:
        entry.tags = tags
    with _session() as s:
        s.add(entry)
        s.commit()
        s.refresh(entry)
    return entry

def list_entries(tag: str | None = None) -> List[JournalEntry]:
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
            raise ValueError(f"Entry {entry_id} not found")
        for k, v in patch.items():
            if k == "tags" and isinstance(v, list):
                obj.tags = v
            else:
                setattr(obj, k, v)
        obj.updated_at = datetime.utcnow()
        s.add(obj)
        s.commit()
        s.refresh(obj)
        return obj
