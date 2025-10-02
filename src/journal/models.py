from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    symbol: str
    direction: str  # long/short/neutral
    strategy: str   # e.g., iron fly, credit put spread
    notes: str = ""
    # Store tags as a comma-separated string for MVP; we can normalize later.
    tags_csv: str = ""

    @property
    def tags(self) -> List[str]:
        return [t for t in (self.tags_csv.split(",") if self.tags_csv else []) if t]

    @tags.setter
    def tags(self, values: List[str]) -> None:
        self.tags_csv = ",".join([v.strip() for v in values if v.strip()])

