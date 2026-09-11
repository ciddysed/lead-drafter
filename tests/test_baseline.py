"""
Unit test for baseline.py's sender-identity fairness fix: baseline should
have access to the same company/sender identity as the real system, since
a real person doing "simple ChatGPT use" would type their company name
into the prompt too -- otherwise the comparison would conflate "does the
naive prompt happen to know your company name" with what the system's
actual grounding/safety/tone rules contribute.
"""
from lead_drafter.config import config
from evaluation.baseline import _build_naive_content


SAMPLE_LEAD = {"name": "Jordan Rivers", "context": "Requested a callback about pricing."}


def test_sender_identity_included_when_configured(monkeypatch):
    monkeypatch.setattr(config, "company_name", "Acme Recovery Co")
    monkeypatch.setattr(config, "sender_name", "Sam Rivera")
    content = _build_naive_content(SAMPLE_LEAD)
    assert "Acme Recovery Co" in content
    assert "Sam Rivera" in content


def test_sender_identity_omitted_when_not_configured(monkeypatch):
    monkeypatch.setattr(config, "company_name", "")
    monkeypatch.setattr(config, "sender_name", "")
    content = _build_naive_content(SAMPLE_LEAD)
    assert "Sender" not in content


def test_business_description_included_when_configured(monkeypatch):
    monkeypatch.setattr(config, "business_description", "Helps homeowners recover unclaimed surplus funds.")
    content = _build_naive_content(SAMPLE_LEAD)
    assert "Helps homeowners recover unclaimed surplus funds." in content


def test_business_description_omitted_when_not_configured(monkeypatch):
    monkeypatch.setattr(config, "business_description", "")
    content = _build_naive_content(SAMPLE_LEAD)
    assert "Business:" not in content
