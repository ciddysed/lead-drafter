"""
Regression test for a real bug found on the first live draft-new run:
a transient provider error (Gemini 503 UNAVAILABLE) wasn't a ValueError
or RuntimeError, so it went uncaught and crashed the whole batch,
silently dropping every lead still queued behind the failing one.
"""
from unittest.mock import patch

from lead_drafter import cli


LEADS = [
    {"lead_id": "L001", "name": "A"},
    {"lead_id": "L002", "name": "B"},
    {"lead_id": "L003", "name": "C"},
]


@patch("lead_drafter.cli.sheets")
@patch("lead_drafter.cli.draft_outreach")
@patch("lead_drafter.cli.config")
def test_one_lead_api_error_does_not_stop_the_batch(mock_config, mock_draft, mock_sheets):
    mock_sheets.list_pending_leads.return_value = LEADS

    def side_effect(lead):
        if lead["lead_id"] == "L002":
            raise RuntimeError("simulated transient provider error")  # any non-ValueError
        return {
            "email_draft": "e", "sms_draft": "s", "confidence": 0.9,
            "flags": [], "reasoning": "ok", "needs_review": False,
        }

    mock_draft.side_effect = side_effect

    cli.cmd_draft_new()

    # L001 and L003 must still get logged even though L002's call blew up
    logged_ids = [call.args[0] for call in mock_sheets.log_draft.call_args_list]
    assert logged_ids == ["L001", "L003"]


@patch("lead_drafter.cli.sheets")
@patch("lead_drafter.cli.draft_outreach")
@patch("lead_drafter.cli.config")
def test_generic_exception_from_provider_is_caught(mock_config, mock_draft, mock_sheets):
    mock_sheets.list_pending_leads.return_value = [{"lead_id": "L001", "name": "A"}]
    mock_draft.side_effect = Exception("503 UNAVAILABLE: high demand")

    cli.cmd_draft_new()  # must not raise

    mock_sheets.log_draft.assert_not_called()
