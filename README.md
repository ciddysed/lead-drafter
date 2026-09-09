# Lead Outreach Drafter

An AI system that drafts personalized first-contact outreach (email + SMS)
for new leads, with a confidence-based human review queue before anything
is marked ready to send.

## The problem

A sales rep or small business owner handling new-lead outreach personally
writes (or lightly customizes a template for) every first message. This is
slow, inconsistent, and doesn't scale — every new lead deserves a message
that references their actual situation, but doing that by hand for every
lead takes real time.

## What this does

Given a new lead's data (name + whatever context is known), it drafts a
personalized email and SMS, self-assesses its own confidence, and flags
anything unusual. Low-confidence or flagged drafts go to a human review
queue instead of auto-sending. See `docs/case_study.md` for the full
problem writeup, architecture, and results.

## Setup (3 steps)

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Configure your credentials**
   - Copy `.env.example` to `.env`
   - Add your OpenAI or Anthropic API key
   - Set up a Google Sheet with two tabs: `Leads` and `Drafts` (see
     `docs/runbook.md` for the exact columns and how to get a Google
     service-account credentials file)
   - Fill in `GOOGLE_SHEET_ID` and `GOOGLE_SHEETS_CREDS_PATH` in `.env`

3. **Run it**
   ```
   python -m lead_drafter.cli draft-new    # draft outreach for any new leads
   python -m lead_drafter.cli review       # review/approve pending drafts
   ```

## Running the evaluation

```
python -m evaluation.run_eval
```

This runs all 12 test cases (`tests/test_cases.json`) through both a naive
baseline and the real system, writing side-by-side results to
`evaluation/results.csv` for manual scoring against `evaluation/rubric.md`.

## Project structure

```
lead_drafter/
  config.py          — env var loading and validation
  drafter.py         — core LLM drafting logic (the system prompt lives here)
  sheets_client.py   — Google Sheets read/write (acts as the CRM)
  cli.py             — the non-developer-facing interface
evaluation/
  rubric.md           — scoring dimensions and baseline definition
  baseline.py         — naive-prompt comparison logic
  run_eval.py         — runs test cases through both systems
tests/
  test_cases.json     — 12 synthetic test cases (representative/edge/failure)
docs/
  case_study.md        — full problem/architecture/results writeup
  runbook.md            — operator guide (Google Sheet setup, troubleshooting)
  workflow_map.md       — Day 1 discovery output
  ai_collaboration_note.md
```

## Important note on scope

This is a from-scratch rebuild of a pattern I've worked with professionally,
built entirely with original code and 100% synthetic lead data — no
employer systems, code, or real lead data were used. See
`docs/ai_collaboration_note.md` and `docs/case_study.md` for full context.
