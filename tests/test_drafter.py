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
def test_default_provider_is_openai(mock_call, monkeypatch):
    monkeypatch.setattr(config, "llm_provider", "some-unrecognized-value")
    mock_call.return_value = {
        "email_draft": "...", "sms_draft": "...", "confidence": 0.8, "flags": [],
    }
    drafter.draft_outreach(SAMPLE_LEAD)
    mock_call.assert_called_once()
