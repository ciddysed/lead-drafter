"""
Regression test for a real bug: a full 12-case eval run (24 calls) hit
Gemini's free-tier per-minute rate limit (15 rpm) with only a 1-second
sleep between cases, and run_eval.py had no retry -- it just recorded
"429 RESOURCE_EXHAUSTED" as the result for every case still queued.
"""
from unittest.mock import patch

import pytest

from evaluation.run_eval import _call_with_retry


def test_succeeds_immediately_when_no_error():
    calls = []

    def fn(lead):
        calls.append(lead)
        return {"ok": True}

    result = _call_with_retry(fn, {"lead_id": "L1"})
    assert result == {"ok": True}
    assert len(calls) == 1


@patch("evaluation.run_eval.time.sleep")
def test_retries_on_rate_limit_then_succeeds(mock_sleep):
    attempts = {"n": 0}

    def fn(lead):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("429 RESOURCE_EXHAUSTED. quota exceeded, retryDelay: '5s'")
        return {"ok": True}

    result = _call_with_retry(fn, {"lead_id": "L1"}, max_retries=3)
    assert result == {"ok": True}
    assert attempts["n"] == 3
    assert mock_sleep.call_count == 2


@patch("evaluation.run_eval.time.sleep")
def test_gives_up_after_max_retries(mock_sleep):
    def fn(lead):
        raise RuntimeError("429 RESOURCE_EXHAUSTED. quota exceeded")

    with pytest.raises(RuntimeError):
        _call_with_retry(fn, {"lead_id": "L1"}, max_retries=2)
    assert mock_sleep.call_count == 2


def test_non_rate_limit_error_raises_immediately_without_retry():
    calls = []

    def fn(lead):
        calls.append(lead)
        raise ValueError("some real bug, not a rate limit")

    with pytest.raises(ValueError):
        _call_with_retry(fn, {"lead_id": "L1"}, max_retries=3)
    assert len(calls) == 1  # must not retry a real error
