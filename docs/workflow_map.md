# Day 1: Discovery, Workflow Map, and Baseline

## Target user and job-to-be-done

A solo sales rep or small business owner personally handling new-lead
outreach, without a dedicated copywriting/marketing team. Every new lead
currently gets a manually written or lightly templated first email/SMS
directly from them. This is a real pattern I've encountered professionally
in lead-qualification pipelines — this build is a from-scratch rebuild
using original code and synthetic data (see ai_collaboration_note.md).

## Current workflow (manual)

| Step | Detail |
|---|---|
| Trigger | A new lead is added to the CRM/spreadsheet |
| Input | Whatever data was captured about the lead (name, situation, contact info — often incomplete) |
| Judgment | Rep decides what to say, referencing whatever context they know |
| Tool | Rep writes it directly in email/SMS, or copies a static template and edits it |
| Approval | Self-approved — the rep is the writer and sender |
| Output | Personalized (or lightly templated) first-contact message |
| Exception | Thin/missing data gets skipped or delayed; rep runs out of time and sends a generic template instead |

## Evidence of pain

- Every new lead requires manual attention before first contact goes out —
  this doesn't scale past a handful of leads/day without either quality
  dropping (generic templates) or response time slowing (backlog).
- Inconsistency: message quality varies by which rep is on shift, how
  busy they are, and how much context they bothered to read.

## Baseline

Baseline = the same 12 synthetic leads run through a single naive LLM
prompt with no grounding/safety/tone rules (see `evaluation/baseline.py`),
scored on the same rubric as the real system. This isolates what the
system's specific rules (grounding, tone-per-channel, injection resistance,
confidence-based review) actually contribute, rather than just "using an
LLM at all" vs. nothing.

## Success metric

- Rubric score (see `evaluation/rubric.md`) improvement over the naive
  baseline, specifically on **grounding** and **safety** dimensions.
- Correct review-queue routing: every test case with a real flag-worthy
  issue (contradictory data, injection attempt, angry history) should be
  routed to human review, not auto-approved.

## Explicit non-goals

- Not simulating the actual sending of email/SMS (no email/SMS provider
  integration) — the system produces drafts and a review decision, sending
  is a separate concern.
- Not modeling what happens after a lead replies (that's simpler,
  deterministic keyword-triggered logic in the real system, not an AI
  decision, and out of scope here).
- Not modeling lead intake/sourcing (scraping, forms, etc.) — this system
  only reacts to leads that already exist in the sheet.

## 8-12 test cases

See `tests/test_cases.json` — 12 cases covering representative (2),
edge (7), and failure (3) scenarios, chosen from real failure modes
encountered in professional lead-outreach automation work: thin/missing
data, contradictory fields, prompt-injection-shaped input, non-English
context, duplicate reprocessing, prior-complaint tone context, and
malformed contact info.

## v1 scope for Day 5

- CLI-driven drafting + review workflow (implemented)
- Google Sheets as the system of record (implemented)
- Confidence + flag-based review routing (implemented)
- Evaluation harness comparing against a naive baseline (implemented)
- Out of scope for v1: actual message sending, contact-format validation
  before drafting, automatic retry on API failures
