# Placeholder for storage; later swap to SQLModel
from typing import List, Dict
from .models import JournalEntry
from datetime import datetime

_DB: Dict[int, JournalEntry] = {}
_SEQ = 1

def create_entry(**kwargs) -> JournalEntry:
    global _SEQ
    now = datetime.utcnow()
    entry = JournalEntry(id=_SEQ, created_at=now, updated_at=now, **kwargs)
    _DB[_SEQ] = entry
    _SEQ += 1
    return entry

def list_entries() -> List[JournalEntry]:
    return list(_DB.values())

def update_entry(entry_id: int, **patch) -> JournalEntry:
    e = _DB[entry_id]
    for k, v in patch.items():
        setattr(e, k, v)
    e.updated_at = datetime.utcnow()
    return e
