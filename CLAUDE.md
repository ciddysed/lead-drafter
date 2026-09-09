# Project Instructions for Claude Code

Read this whole file before doing anything. This is a hiring-assessment
project with a hard deadline and specific integrity constraints — follow
the constraints section exactly, not just the technical steps.

## What this project is

A 5-day take-home technical assessment for "Applied AI Engineer (AI OS &
Workflow Automation)" at a company called MUST. The task: pick one real,
recurring operational bottleneck and build a small, evaluable AI system
around it in 5 days, then submit a working repo + evaluation package +
case study + AI collaboration note + 5-minute demo video.

**The chosen problem:** a system that drafts personalized first-contact
outreach (email + SMS) for new sales leads, using an LLM, with a
confidence-based human review queue before anything is marked ready to
send. This is inspired by a real system the candidate (the user you're
working with) has built professionally, but is being rebuilt here from
scratch — original code, 100% synthetic data.

## Hard constraints — do not violate these

1. **No real employer code or data, ever.** The user has professional
   experience with a similar system at their job. Nothing from that real
   system — actual code, actual prompts, actual business logic specifics,
   actual company/client names — should appear here. If the user pastes
   in anything that looks like it might be from their actual employer's
   system, flag it and suggest a generic/synthetic equivalent instead of
   using it verbatim.
2. **All lead data must be synthetic.** Fabricated names, fabricated
   scenarios. Never use real people's names, real phone numbers, real
   email addresses, or real property/financial details.
3. **The user must be able to explain every decision personally.** This
   assessment explicitly scores "can you explain and modify AI-generated
   outputs and code" and requires an honest "AI Collaboration Note." Don't
   just generate finished artifacts silently — explain what you're doing
   and why as you go, so the user can defend it in conversation with MUST
   later. Prefer working WITH the user interactively over dumping large
   unexplained blocks of finished work.
4. **Don't fabricate evaluation results.** The `evaluation/results.csv`
   and the numbers/observations in `docs/case_study.md` must come from an
   actual run against the user's real API key and real (synthetic) test
   data — never invent plausible-looking results to fill in a placeholder.
   If asked to "fill in the case study," first check whether
   `evaluation/results.csv` actually exists and has real content; if not,
   say so and help the user run the eval first.

## Current state of the repo (as of handoff)

Everything below was built and syntax/logic-tested (with mocked LLM
responses) by Claude in a sandboxed environment with no real API keys or
Google credentials — so the code is believed correct, but has NOT been
run against a real LLM or real Google Sheet yet. Treat first real runs as
genuinely unverified until you see them work.

```
lead_drafter/
  config.py          — DONE. Loads secrets from .env, validates on startup.
  drafter.py          — DONE. Core LLM call, system prompt with grounding/
                          safety rules, confidence + flags -> needs_review logic.
  sheets_client.py    — DONE, UNTESTED against a real sheet. Read/write
                          wrapper for Leads and Drafts tabs.
  cli.py               — DONE. `draft-new` and `review` commands.
evaluation/
  rubric.md             — DONE. 4-dimension scoring rubric (grounding, tone,
                            failure handling, safety), 0-2 each.
  baseline.py            — DONE. Naive-prompt comparison, no safety rules.
  run_eval.py             — DONE, UNTESTED end-to-end. Runs all 12 test
                              cases through both baseline and real system,
                              writes evaluation/results.csv with empty
                              score columns for manual rubric scoring.
tests/
  test_cases.json          — DONE. 12 synthetic cases: 2 representative,
                              7 edge, 3 failure. See file for details.
docs/
  README.md                 — DONE.
  workflow_map.md             — DONE (Day 1 deliverable).
  runbook.md                   — DONE. Google Sheet + service account setup
                                  steps, troubleshooting table.
  case_study.md                  — SKELETON ONLY. Has [FILL IN] placeholders
                                    for Results, Failures/changes/limitations,
                                    and the iteration plan — these need REAL
                                    output from an actual eval run.
  ai_collaboration_note.md         — SKELETON ONLY. Same situation — needs
                                    the user's real answers about what they
                                    verified/rejected/decided.
.env.example                       — DONE. Copy to .env and fill in.
requirements.txt                    — DONE.
.gitignore                           — DONE. Excludes .env and credentials.json.
.github/workflows/draft-leads.yml     — DONE, UNTESTED (needs real GitHub
                                        Secrets to run). Scheduled every
                                        5 min + manual "Run workflow" button.
```

## What's left to do, in order

1. **Get the user's LLM provider choice and API key.** Ask which they
   want (OpenAI or Anthropic) if not already decided, and have them put
   the key in `.env` (copy from `.env.example` first). Never ask them to
   paste the key into chat — have them edit the file directly.

2. **Set up the Google Sheet.** Walk the user through `docs/runbook.md`'s
   setup steps interactively — creating the sheet, the two tabs with the
   right headers, the Google Cloud service account, and sharing the sheet
   with it. Help troubleshoot if `gspread` throws permission errors.

3. **Seed the Leads tab** with a handful of synthetic leads — you can
   reuse the lead data already inside `tests/test_cases.json` as a
   starting point (they're already fully synthetic), or generate a few
   more if the user wants variety.

4. **Run `python -m lead_drafter.cli draft-new`** against the real
   sheet and a real API key. Debug any real issues that come up — the
   code has been logic-tested but never run against a real API, so
   expect to actually fix something here (that's normal, not a sign the
   plan failed).

5. **Run `python -m lead_drafter.cli review`** and walk through
   approving/rejecting at least a couple of drafts, so the review queue
   is demonstrated working end to end.

6. **Run `python -m evaluation.run_eval`.** This produces
   `evaluation/results.csv` with real baseline vs. system outputs for
   all 12 test cases.

7. **Score the results by hand** against `evaluation/rubric.md` — this
   step needs the user's own judgment, not an LLM grading its own output.
   Sit with them and go case by case; ask them what they think before
   suggesting a score, since this is exactly the "evaluation judgment"
   skill the assessment is testing.

8. **Deliberately break the system (Day 4 requirement).** Try feeding it
   something not already in test_cases.json — e.g. an extremely long
   context field, a lead with emoji-only context, two leads with
   identical names but different lead_ids — and document what actually
   happens. This is supposed to surface at least 3 real failure cases
   with root-cause analysis; don't skip this by only using the existing
   12 cases.

9. **Fill in `docs/case_study.md` and `docs/ai_collaboration_note.md`**
   with the user's real observations from steps 6-8 — interview the user
   for their answers rather than writing plausible-sounding content
   yourself. Ask things like "which test case surprised you most?" and
   "was there a moment you didn't trust what I (Claude) generated and
   checked it yourself?"

10. **Set up a GitHub repo** (the user's own account) and push everything.
    Double-check `.gitignore` is working — confirm `.env` and
    `credentials.json` do NOT show up in `git status` before the first
    commit, since a leaked API key in a public repo gets found and abused
    within minutes.

11. **Configure GitHub Actions secrets** (repo Settings → Secrets and
    variables → Actions) so `.github/workflows/draft-leads.yml` can run:
    `LLM_PROVIDER`, `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`,
    `LLM_MODEL`, `GOOGLE_SHEET_ID`, and `GOOGLE_CREDENTIALS_B64` (the
    user's `credentials.json`, base64-encoded — command is in
    `docs/runbook.md`). Then trigger it once manually from the Actions
    tab ("Run workflow") to confirm it actually works end to end against
    real secrets — this has never been tested against a real GitHub
    Actions run, only reasoned through, so treat the first run as a real
    debugging step, not a formality.

12. **Help draft a demo script** (not the video itself — the user records
    that with their own voice/screen) covering: the problem and baseline,
    a live run from real input to output (ideally showing the GitHub
    Actions "Run workflow" button triggering a real run live, which is a
    stronger production-proof moment than a local terminal), the
    review-queue UX, the evaluation results, and the single most
    important limitation to be upfront about. Keep it to something
    deliverable in 5 minutes.

## Style/working notes

- The user prefers concise, direct answers over long explanations —
  match that.
- The user is early-career (~1 year hands-on experience) with real,
  genuine skill in GHL/n8n/Python/API integration, but is newer to formal
  evaluation methodology, deliberate failure-testing, and production
  observability — this project exists specifically to build that muscle,
  so lean toward walking them through reasoning rather than just doing it
  silently for them, even when it would be faster to just do it yourself.
- Time is limited (this is a 5-day sprint) — be efficient, but don't skip
  step 9 (interviewing the user for their real observations) just to save
  time, since a case study that doesn't reflect genuine firsthand
  observations is the single biggest way this submission could fail on
  the "Ownership and Communication" and "Evaluation and Learning Loop"
  scoring dimensions.
