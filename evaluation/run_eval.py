"""
Runs every test case in tests/test_cases.json through BOTH the naive
baseline and the real drafter, and writes results to evaluation/results.csv.

This does NOT auto-score the rubric dimensions (grounding/tone/failure-
handling/safety) — that requires human judgment per the rubric, since an
LLM-graded eval of an LLM's output has its own reliability problems worth
avoiding in a 5-day scope. Instead this script produces the raw outputs
side by side, and results.csv has empty columns for you to score by hand
against evaluation/rubric.md. This is a deliberate, defensible scope
decision — documented here so it's easy to explain if asked.

Run: python -m evaluation.run_eval
"""
import json
import csv
import re
import time
from pathlib import Path
from lead_drafter.config import config
from lead_drafter.drafter import draft_outreach
from evaluation.baseline import draft_naive

TEST_CASES_PATH = Path(__file__).parent.parent / "tests" / "test_cases.json"
RESULTS_PATH = Path(__file__).parent / "results.csv"


def _call_with_retry(fn, lead, max_retries=3):
    """
    Retry on a provider rate-limit error (e.g. Gemini free tier's
    15-requests/minute cap) with backoff, since a full 12-case eval run
    (24 calls) easily exceeds a per-minute limit that individual live
    usage rarely would. Anything else (a real bug) raises immediately --
    this is specifically for "the request was fine, just too soon."
    """
    for attempt in range(max_retries + 1):
        try:
            return fn(lead)
        except Exception as e:
            msg = str(e)
            is_rate_limit = "RESOURCE_EXHAUSTED" in msg or "429" in msg
            if not is_rate_limit or attempt == max_retries:
                raise
            match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", msg)
            delay = int(match.group(1)) + 3 if match else (attempt + 1) * 15
            print(f"  Rate limited, waiting {delay}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(delay)

FIELDS = [
    "test_id", "category", "expected_behavior",
    "baseline_email", "baseline_sms", "baseline_error",
    "system_email", "system_sms", "system_confidence", "system_flags", "system_error",
    "baseline_grounding_score", "baseline_tone_score",
    "baseline_failure_handling_score", "baseline_safety_score", "baseline_total",
    "system_grounding_score", "system_tone_score",
    "system_failure_handling_score", "system_safety_score", "system_total",
    "notes",
]


def run():
    config.validate()
    cases = json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    rows = []

    for case in cases:
        lead = case["lead"]
        row = {
            "test_id": case["id"],
            "category": case["category"],
            "expected_behavior": case["expected_behavior"],
            "baseline_email": "", "baseline_sms": "", "baseline_error": "",
            "system_email": "", "system_sms": "", "system_confidence": "",
            "system_flags": "", "system_error": "",
            "baseline_grounding_score": "", "baseline_tone_score": "",
            "baseline_failure_handling_score": "", "baseline_safety_score": "", "baseline_total": "",
            "system_grounding_score": "", "system_tone_score": "",
            "system_failure_handling_score": "", "system_safety_score": "", "system_total": "",
            "notes": "SCORE MANUALLY vs rubric.md",
        }

        print(f"Running {case['id']}...")

        try:
            b = _call_with_retry(draft_naive, lead)
            row["baseline_email"] = b.get("email_draft", "")
            row["baseline_sms"] = b.get("sms_draft", "")
        except Exception as e:
            row["baseline_error"] = str(e)

        try:
            s = _call_with_retry(draft_outreach, lead)
            row["system_email"] = s.get("email_draft", "")
            row["system_sms"] = s.get("sms_draft", "")
            row["system_confidence"] = s.get("confidence", "")
            row["system_flags"] = "; ".join(s.get("flags", []))
        except Exception as e:
            row["system_error"] = str(e)

        rows.append(row)
        time.sleep(4)  # stay under free-tier per-minute limits (e.g. 15 rpm)

    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Wrote {len(rows)} rows to {RESULTS_PATH}")
    print("Next step: open results.csv and score each row against evaluation/rubric.md")


if __name__ == "__main__":
    run()
