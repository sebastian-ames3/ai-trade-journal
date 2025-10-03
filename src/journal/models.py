from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"
    
    id: Optional[int] = Field(default=None, primary_key=True)    
    
    # housekeeping
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # risk mgmt (optional but useful)
    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    # lifecycle
    status: str = "open"  # "open" | "closed"
    exit_date: Optional[date] = None
    exit_price: Optional[float] = None

    # core trade details
    symbol: str
    direction: str
    strategy: str
    entry_date: date = Field(default_factory=date.today)
    entry_price: float = 0.0
    size: int = 1
    notes: str = ""
    tags_csv: str = ""  # internal storage

    # options workflow: how the position was opened
    # 'BTO' (debit) or 'STO' (credit)
    entry_action: str = "BTO"  # allowed: "BTO" | "STO"

    @property
    def tags(self) -> List[str]:
        return [t for t in self.tags_csv.split(",") if t] if self.tags_csv else []

    @tags.setter
    def tags(self, values: List[str]) -> None:
        self.tags_csv = ",".join(v.strip() for v in values if v.strip())

    def expected_exit_action(self) -> str:
    
    # What the close action should be, given entry_action
        return "STC" if self.entry_action == "BTO" else "BTC"

@property
def holding_days(self) -> Optional[int]:
    if not self.exit_date:
        return None
    return (self.exit_date - self.entry_date).days

@property
def realized_pl(self) -> Optional[float]:
    """Options P&L with 100x contract multiplier.
    BTO -> STC:   (exit - entry) * contracts * 100
    STO -> BTC:   (entry - exit) * contracts * 100
    """
    if self.status != "closed" or self.exit_price is None:
        return None
    multiplier = 100
    if self.entry_action == "BTO":
        pnl = (self.exit_price - self.entry_price) * self.size * multiplier
    else:  # STO
        pnl = (self.entry_price - self.exit_price) * self.size * multiplier
    return round(pnl, 2)

