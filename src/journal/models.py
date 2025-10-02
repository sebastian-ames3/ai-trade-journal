from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    symbol: str
    direction: str
    strategy: str
    notes: str = ""
    tags_csv: str = ""  # internal storage

    @property
    def tags(self) -> List[str]:
        return [t for t in self.tags_csv.split(",") if t] if self.tags_csv else []

    @tags.setter
    def tags(self, values: List[str]) -> None:
        self.tags_csv = ",".join(v.strip() for v in values if v.strip())


