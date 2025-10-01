from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class JournalEntry:
    id: int
    created_at: datetime
    updated_at: datetime
    symbol: str
    direction: str  # long/short/neutral
    strategy: str   # e.g., iron fly, credit put spread
    notes: str
    tags: List[str]
