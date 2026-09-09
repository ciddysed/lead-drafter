"""
Regression test for a real bug: run_eval.py read test_cases.json with the
platform default encoding, which is cp1252 on Windows and can't decode the
Vietnamese text in TC07 -- crashed immediately on Windows, never even
reaching the API calls.
"""
import json
from evaluation.run_eval import TEST_CASES_PATH


def test_test_cases_file_is_valid_utf8_json():
    cases = json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    assert len(cases) >= 8  # brief requires 8-12
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
