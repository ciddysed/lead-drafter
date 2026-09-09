"""
Unit tests for sheets_client's header-safety logic, using a fake worksheet
object instead of a real gspread connection (no network/API key needed).

Regression coverage for a real bug found on the first live run: a fresh
Google Sheets tab isn't always byte-empty, so checking
`get_all_values() == []` to decide whether to write the header silently
skipped it, leaving every drafted row without a header row at all.
"""
from lead_drafter.sheets_client import _ensure_drafts_header, DRAFTS_HEADER


class FakeWorksheet:
    def __init__(self, rows):
        self._rows = rows  # list of row-value lists
        self.inserted = None
        self.appended = None

    def row_values(self, n):
        idx = n - 1
        return self._rows[idx] if idx < len(self._rows) else []

    def insert_row(self, values, index):
        self.inserted = (values, index)
        self._rows.insert(index - 1, values)

    def append_row(self, values, table_range=None):
        self.appended = values
        self.append_table_range = table_range
        self._rows.append(values)


def test_writes_header_on_truly_empty_sheet():
    ws = FakeWorksheet(rows=[])
    _ensure_drafts_header(ws)
    assert ws.appended == DRAFTS_HEADER
    assert ws.inserted is None


def test_does_nothing_when_header_already_correct():
    ws = FakeWorksheet(rows=[DRAFTS_HEADER, ["L001", "...", "...", "...", "1", "", "", "approved"]])
    _ensure_drafts_header(ws)
    assert ws.appended is None
    assert ws.inserted is None


def test_inserts_header_when_data_row_landed_in_row_one():
    # Reproduces the actual bug: row 1 is a real data row, not a header.
    data_row = ["L001", "2026-09-09T...", "email...", "sms...", "1", "", "reason", "approved"]
    ws = FakeWorksheet(rows=[data_row])
    _ensure_drafts_header(ws)
    assert ws.inserted == (DRAFTS_HEADER, 1)
    assert ws.appended is None
    assert ws.row_values(1) == DRAFTS_HEADER
    assert ws.row_values(2) == data_row
