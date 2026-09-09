# Contributing workflow

This repo requires the following workflow for every change — `main` is
protected and will reject a direct push.

1. **Branch off `main`.**
   ```
   git checkout -b your-change-name
   ```

2. **Write or update tests for your change**, then run the full suite
   locally before pushing:
   ```
   pip install -r requirements-dev.txt
   pytest tests/ -v
   ```
   `tests/test_drafter.py` mocks the LLM calls (`_call_openai` /
   `_call_anthropic` / `_call_gemini`) so it runs free and deterministically
   with no API key required — add new mocked cases there for new logic
   branches (e.g. a new review-routing rule, a new provider). This is
   separate from `evaluation/run_eval.py`, which hits a real LLM API and
   is for judging draft *quality*, not for gating every commit.

3. **Open a pull request** into `main`. Don't commit straight to `main`.

4. **Wait for the `CI` check to go green** (`.github/workflows/ci.yml`
   runs `pytest tests/` on every PR). A red check blocks merging —
   fix the failure, don't bypass it.

5. **Merge only after CI is green.**

## Why

Untested changes to `drafter.py`'s review-routing logic (confidence
threshold, flag handling) directly affect whether a bad draft gets
auto-approved instead of sent to human review. A CI gate that only
requires "code that runs" isn't enough — it needs a test asserting the
specific behavior you're relying on.
