from datetime import date
from src.journal.models import JournalEntry
from src.journal.storage import init_db, create_entry, close_entry, list_entries_by_status
from src.settings import Settings

def test_close_entry(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(Settings(database_url=f"sqlite:///{db_path}"))

    j = create_entry(symbol="AAPL", side="long", entry_date=date(2025,1,1), entry_price=100.0, size=10)
    assert j.status == "open"

    closed = close_entry(j.id, exit_price=110.0, exit_date=date(2025,1,2))
    assert closed.status == "closed"
    assert closed.exit_price == 110.0

    closed_list = list_entries_by_status("closed")
    assert any(x.id == j.id for x in closed_list)
    assert closed.realized_pl == 100.0  # (110-100)*10
