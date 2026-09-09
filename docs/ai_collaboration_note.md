# AI Collaboration Note

## AI tools used and the role of each

- **Claude (Anthropic)** — used throughout the 5 days as a pair-programmer
  and planning partner: scoping the problem down from an initial over-broad
  idea, drafting the Python code structure, writing the test case set, and
  drafting this documentation set.
- **[OpenAI/Anthropic API — whichever you use]** — the actual production
  system under test: the `drafter.py` module calls this API to generate
  the outreach drafts being evaluated.

## Work delegated to AI (Claude)

- First-draft Python code for `drafter.py`, `sheets_client.py`, `cli.py`,
  `run_eval.py`, and the evaluation rubric structure.
- First-draft synthetic test cases, informed by real failure modes I
  described from professional experience with a similar system (ambiguous/
  contradictory data, thin data, injection-shaped input, tone given prior
  complaint history).
- First-draft documentation structure (README, runbook, case study
  skeleton).

## How I verified AI-generated results

- [Fill in once you've actually run it: e.g. "Ran the full test suite
  against my own OpenAI key and manually read every one of the 12 draft
  outputs against the rubric before recording scores — did not trust the
  model's self-reported confidence score as ground truth, cross-checked
  it against my own read of each draft."]
- Reviewed every line of generated code for logic I could personally
  explain — e.g. why the confidence threshold routes to review, why the
  hard-stop guard exists in `draft_outreach()`, why JSON output was chosen
  over free text.

## Important results I rejected or manually corrected

- [Fill in based on your actual Day 2-4 work — e.g. if Claude's first
  version of the system prompt didn't explicitly forbid inventing details
  and you caught a hallucination in testing, or if a first-draft test case
  wasn't actually a meaningful edge case and you replaced it.]

## Core decisions I personally owned

- The choice to scope this to outbound drafting only (not reply
  classification), based on how the real-world equivalent system actually
  splits AI vs. deterministic logic.
- The choice to hold drafts for human review rather than auto-send,
  reasoned from responsible-AI judgment about outbound content to real
  people, not just because the rubric asks for approval points.
- The decision to use fully synthetic data and freshly written code
  throughout, to avoid any IP conflict with a real system I've worked on
  professionally.
- [Add any specific judgment calls you made during the actual build that
  Claude didn't decide for you — API provider choice, confidence threshold
  number, which test cases to prioritize fixing first on Day 4, etc.]
