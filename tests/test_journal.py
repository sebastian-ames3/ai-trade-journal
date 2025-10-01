from src.journal.storage import create_entry, list_entries, update_entry

def test_create_and_list():
    e = create_entry(symbol="SPY", direction="long", strategy="CSP", notes="Test", tags=["#test"])  # type: ignore
    assert e.id == 1
    assert len(list_entries()) == 1

def test_update():
    e = update_entry(1, notes="Updated")
    assert e.notes == "Updated"
