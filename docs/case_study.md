# Case Study: Lead Outreach Drafter

## User and problem

See `workflow_map.md` for full detail. Short version: a solo rep/small
business owner manually drafts every new lead's first outreach message,
which doesn't scale and produces inconsistent quality.

## Existing workflow and bottleneck

Manual, per-lead message writing — see workflow_map.md's table.

## Scope decisions and non-goals

- **In scope:** drafting personalized email + SMS from lead data, confidence
  self-assessment, flag-based human review routing, evaluation against a
  naive baseline.
- **Out of scope (and why):** sending messages (separate integration
  concern, not the bottleneck being solved), interpreting lead replies
  (deterministic keyword logic in the real-world equivalent, not an AI
  decision), lead sourcing/intake (upstream of this problem).

## Architecture and major trade-offs

- **Python, not a no-code tool (n8n/Make):** the assessment specifically
  asks for API integrations and automation scripts in Python/JS — chose to
  build the core logic in code rather than wire together no-code nodes,
  even though I have real n8n experience I could have leaned on instead.
- **Structured JSON output, not free text:** makes the confidence/flags/
  drafts reliably parseable downstream, rather than regex-parsing a
  freeform response.
- **Google Sheets as the "CRM," not a real CRM platform:** kept the system
  of record lightweight and inspectable for evaluation purposes, while
  still being a genuine external API integration (not a mocked database).
- **Confidence threshold for review, not a fixed rule list:** lets the
  model itself signal uncertainty in unpredictable edge cases, rather
  than requiring me to enumerate every possible flag-worthy condition
  in advance — traded off against the model's confidence self-reports
  being unverified (a documented limitation).
- **No LLM-graded evaluation:** rubric scoring in this case study was done
  by hand against `evaluation/rubric.md`, not by asking an LLM to grade
  its own (or another LLM's) output — avoided introducing a second,
  unvalidated LLM judgment layer into a 5-day scope.

## Work delegated to AI and judgment retained by humans

See `ai_collaboration_note.md` for the full breakdown.

## Results

*[FILL IN AFTER RUNNING `python -m evaluation.run_eval` WITH YOUR OWN API
KEY — paste the actual results.csv summary here: how many of the 12 cases
passed the 6/8 rubric threshold, which specific cases failed and why, and
how the naive baseline compared on the same cases.]*

## Failures, changes, and limitations

*[FILL IN based on your actual Day 4 — which test cases exposed real
problems, what you changed in drafter.py in response, and what's still
a known limitation you're choosing not to fix in this scope.]*

## Next two-week iteration plan

*[Example structure — replace with your own real priorities once you've
seen actual results:]*
1. Add contact-format validation as a pre-send gate (email/phone regex
   check) — currently drafts anyway and defers the check.
2. Add retry/backoff on LLM API failures instead of skip-and-log.
3. Get feedback from a real (or realistic proxy) user running the review
   queue for a week — does the confidence threshold feel right, or are
   too many/too few drafts landing in review?
4. Consider a second LLM call as an independent grounding-check pass on
   high-value leads specifically (e.g. TC11-style), rather than relying
   solely on the drafting model's own self-assessment.
