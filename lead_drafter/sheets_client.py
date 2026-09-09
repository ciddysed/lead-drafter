"""
Google Sheets acts as our lightweight "CRM" for this project — a real,
external system of record, not a mocked database. Two tabs expected:

  "Leads"   — columns: lead_id | name | context | contact_email | contact_sms
  "Drafts"  — columns: lead_id | timestamp | email_draft | sms_draft |
                        confidence | flags | status

status values: "pending_review" | "approved" | "rejected" | "sent"
"""
import gspread
from datetime import datetime, timezone
from lead_drafter.config import config

DRAFTS_HEADER = [
    "lead_id", "timestamp", "email_draft", "sms_draft",
    "confidence", "flags", "reasoning", "status",
]


def _client():
    gc = gspread.service_account(filename=config.google_sheets_creds_path)
    return gc.open_by_key(config.google_sheet_id)


def get_lead(lead_id: str) -> dict:
    sh = _client()
    ws = sh.worksheet("Leads")
    records = ws.get_all_records()
    for r in records:
        if str(r.get("lead_id")) == str(lead_id):
            return r
    raise KeyError(f"No lead found with lead_id={lead_id}")


def list_pending_leads() -> list[dict]:
    """Leads that don't have a draft logged yet."""
    sh = _client()
    leads = sh.worksheet("Leads").get_all_records()
    drafts = sh.worksheet("Drafts").get_all_records()
    drafted_ids = {str(d["lead_id"]) for d in drafts}
    return [l for l in leads if str(l["lead_id"]) not in drafted_ids]


def _ensure_drafts_header(ws):
    """
    Make sure row 1 is exactly DRAFTS_HEADER before any data row is appended.

    Checking "is the sheet empty?" (e.g. get_all_values() == []) to decide
    whether to write the header is fragile — a freshly created Google Sheets
    tab isn't always byte-empty (stray formatting/whitespace from tab
    creation), so that check can silently evaluate false on the very first
    real write and leave every subsequent row without a header at all.
    Checking row 1's actual content directly is the reliable version.
    """
    first_row = ws.row_values(1)
    if first_row == DRAFTS_HEADER:
        return
    if first_row:
        # Row 1 has content but it's not our header — a data row already
        # landed there (the original bug's failure mode). Push it down
        # rather than overwrite it.
        ws.insert_row(DRAFTS_HEADER, 1)
    else:
        ws.append_row(DRAFTS_HEADER, table_range="A1")


def log_draft(lead_id: str, result: dict):
    sh = _client()
    ws = sh.worksheet("Drafts")
    _ensure_drafts_header(ws)
    status = "pending_review" if result.get("needs_review") else "approved"
    # table_range="A1" pins the append to start at column A. Without it,
    # the Sheets API auto-detects "the table" to append below, and once a
    # sheet has inconsistently-shaped rows (as ours briefly did from the
    # header bug above), that guess can drift — real rows were observed
    # landing 6 columns to the right of A on this project's first live run.
    ws.append_row([
        lead_id,
        datetime.now(timezone.utc).isoformat(),
        result.get("email_draft", ""),
        result.get("sms_draft", ""),
        result.get("confidence", 0.0),
        "; ".join(result.get("flags", [])),
        result.get("reasoning", ""),
        status,
    ], table_range="A1")


def update_draft_status(lead_id: str, new_status: str):
    sh = _client()
    ws = sh.worksheet("Drafts")
    cell = ws.find(str(lead_id))
    if not cell:
        raise KeyError(f"No draft row found for lead_id={lead_id}")
    header = ws.row_values(1)
    status_col = header.index("status") + 1
    ws.update_cell(cell.row, status_col, new_status)


def list_pending_review() -> list[dict]:
    sh = _client()
    drafts = sh.worksheet("Drafts").get_all_records()
    return [d for d in drafts if d.get("status") == "pending_review"]
