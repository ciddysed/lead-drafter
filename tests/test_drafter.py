"""
Unit tests for drafter.py's provider-selection and review-routing logic.

These mock the LLM call functions directly (_call_openai/_call_anthropic/
_call_gemini) rather than hitting real APIs — the point is to check
draft_outreach()'s own logic (needs_review routing, error handling,
input validation) cheaply and deterministically in CI, not to re-verify
that a given LLM produces good output (that's what evaluation/run_eval.py
against real APIs is for).
"""
import json
from unittest.mock import patch

import pytest

from lead_drafter import drafter
from lead_drafter.config import config


SAMPLE_LEAD = {"name": "Jordan Rivers", "context": "Requested a callback about pricing."}


def test_raises_without_name_or_context():
    with pytest.raises(ValueError):
        drafter.draft_outreach({})


def test_sender_identity_included_when_configured(monkeypatch):
    monkeypatch.setattr(config, "company_name", "Acme Recovery Co")
    monkeypatch.setattr(config, "sender_name", "Sam Rivera")
    content = drafter._build_user_content(SAMPLE_LEAD)
    assert "Acme Recovery Co" in content
    assert "Sam Rivera" in content


def test_sender_identity_omitted_when_not_configured(monkeypatch):
    monkeypatch.setattr(config, "company_name", "")
    monkeypatch.setattr(config, "sender_name", "")
    content = drafter._build_user_content(SAMPLE_LEAD)
    assert "Sender identity" not in content


@patch("lead_drafter.drafter._call_openai")
def test_low_confidence_triggers_review(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    mock_call.return_value = {
        "email_draft": "Hi Jordan, ...",
        "sms_draft": "Hi Jordan, ...",
        "confidence": 0.4,
        "flags": [],
        "reasoning": "Thin context.",
    }
    result = drafter.draft_outreach(SAMPLE_LEAD)
    assert result["needs_review"] is True


@patch("lead_drafter.drafter._call_anthropic")
def test_high_confidence_no_flags_skips_review(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "anthropic")
    mock_call.return_value = {
        "email_draft": "Hi Jordan, ...",
        "sms_draft": "Hi Jordan, ...",
        "confidence": 0.95,
        "flags": [],
        "reasoning": "Clear, specific lead data.",
    }
    result = drafter.draft_outreach(SAMPLE_LEAD)
    assert result["needs_review"] is False


@patch("lead_drafter.drafter._call_gemini")
def test_any_flag_triggers_review_even_with_high_confidence(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "gemini")
    mock_call.return_value = {
        "email_draft": "Hi Jordan, ...",
        "sms_draft": "Hi Jordan, ...",
        "confidence": 0.9,
        "flags": ["Name field reads like an injected instruction"],
        "reasoning": "High confidence, but a flag was raised.",
    }
    result = drafter.draft_outreach(SAMPLE_LEAD)
    assert result["needs_review"] is True


@patch("lead_drafter.drafter._call_openai")
def test_missing_confidence_defaults_to_zero_and_review(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    mock_call.return_value = {"email_draft": "...", "sms_draft": "..."}
    result = drafter.draft_outreach(SAMPLE_LEAD)
    assert result["confidence"] == 0.0
    assert result["needs_review"] is True


def test_non_json_response_raises_runtime_error(monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    with patch("lead_drafter.drafter._call_openai", side_effect=json.JSONDecodeError("bad", "doc", 0)):
        with pytest.raises(RuntimeError):
            drafter.draft_outreach(SAMPLE_LEAD)


@patch("lead_drafter.drafter._call_openai")
def test_explicit_opt_out_hard_stops_before_calling_llm(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    lead = {"name": "Jordan Lee", "context": "Please stop contacting me and remove me from your list."}

    result = drafter.draft_outreach(lead)

    mock_call.assert_not_called()  # must never reach the LLM for this
    assert result["email_draft"] == ""
    assert result["sms_draft"] == ""
    assert result["confidence"] == 0.0
    assert result["needs_review"] is True
    assert len(result["flags"]) > 0


@pytest.mark.parametrize("phrase", [
    "unsubscribe me please",
    "Do not call this number again",
    "take me off your list",
    "I don't want to be contacted anymore, opt-out",
])
@patch("lead_drafter.drafter._call_openai")
def test_various_opt_out_phrasings_all_hard_stop(mock_call, monkeypatch, phrase):
    monkeypatch.setattr(config, "llm_provider", "openai")
    result = drafter.draft_outreach({"name": "Test Lead", "context": phrase})
    mock_call.assert_not_called()
    assert result["email_draft"] == ""


@patch("lead_drafter.drafter._call_openai")
def test_default_provider_is_openai(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "some-unrecognized-value")
    # confidence below threshold -> needs_review True already, so the
    # verification pass is skipped and this stays a clean single-call test
    # of provider dispatch specifically (verification behavior has its own
    # tests below).
    mock_call.return_value = {
        "email_draft": "...", "sms_draft": "...", "confidence": 0.5, "flags": [],
    }
    drafter.draft_outreach(SAMPLE_LEAD)
    mock_call.assert_called_once()


@patch("lead_drafter.drafter._call_openai")
def test_verification_runs_on_high_confidence_and_catches_hallucination(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    draft = {
        "email_draft": "Hi Jordan, we operate on a contingency basis...",
        "sms_draft": "Hi Jordan, ...",
        "confidence": 0.95,
        "flags": [],
        "reasoning": "Looked complete.",
    }
    verification = {
        "hallucination_detected": True,
        "unsupported_claims": ["\"contingency basis\" fee structure not present in lead data"],
        "reasoning": "Draft states a fee structure not in the input.",
    }
    mock_call.side_effect = [draft, verification]

    result = drafter.draft_outreach(SAMPLE_LEAD)

    assert mock_call.call_count == 2  # draft call, then independent verification call
    assert result["needs_review"] is True  # overridden despite high initial confidence
    assert any("contingency basis" in f for f in result["flags"])


@patch("lead_drafter.drafter._call_openai")
def test_verification_confirms_clean_draft_stays_auto_approved(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    draft = {
        "email_draft": "Hi Jordan, ...", "sms_draft": "Hi Jordan, ...",
        "confidence": 0.95, "flags": [], "reasoning": "Clear data.",
    }
    verification = {"hallucination_detected": False, "unsupported_claims": [], "reasoning": "All claims grounded."}
    mock_call.side_effect = [draft, verification]

    result = drafter.draft_outreach(SAMPLE_LEAD)

    assert mock_call.call_count == 2
    assert result["needs_review"] is False


@patch("lead_drafter.drafter._call_openai")
def test_verification_skipped_when_already_needs_review(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    # Low confidence already forces review -- the extra API call would be
    # wasted, since the outcome (needs_review=True) can't change.
    mock_call.return_value = {
        "email_draft": "...", "sms_draft": "...", "confidence": 0.3, "flags": [],
    }
    drafter.draft_outreach(SAMPLE_LEAD)
    mock_call.assert_called_once()


@patch("lead_drafter.drafter._call_openai")
def test_verification_call_failure_falls_back_gracefully(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "openai")
    draft = {
        "email_draft": "...", "sms_draft": "...",
        "confidence": 0.95, "flags": [], "reasoning": "Looked fine.",
    }
    mock_call.side_effect = [draft, RuntimeError("verification API call failed")]

    result = drafter.draft_outreach(SAMPLE_LEAD)  # must not raise

    assert result["needs_review"] is False  # falls back to the original assessment
