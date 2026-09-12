# Demo Script (5 minutes)

Speak this in your own words. This is a timing/content skeleton, not a
script to read verbatim. Have these open before recording: the GitHub
repo, the Google Sheet (Leads + Drafts tabs), a terminal, and the GitHub
Actions tab.

## 0:00 to 0:50: The problem and baseline

- "A solo rep or small business manually writes the first outreach
  message for every new lead. That doesn't scale, and quality gets
  inconsistent under time pressure."
- "The baseline for comparison is simple ChatGPT-style use: one generic
  prompt, no rules." (Show one baseline example on screen. TC01's
  baseline output with the invented "contingency basis, no upfront
  costs" claim highlighted.)
- "Even on the easiest case, it invents business terms nobody gave it.
  That's not a quality nitpick. A real business sending fabricated fee
  claims is a trust and legal-exposure risk."

## 0:50 to 2:00: Live flow, real input to output

- "In a real deployment, new leads would land in your actual CRM. I'm
  using a Google Sheet to simulate that here: it's a real external
  system the code reads and writes to, not a mocked database, just
  lightweight enough to inspect directly for this project. Two tabs:
  `Leads` is the input, where new leads get added; `Drafts` is the
  output, where the system logs every generated draft along with its
  confidence, flags, and review status."
- Show the Google Sheet's `Leads` tab. Add one new synthetic lead live
  (or point to one already there).
- Switch to the GitHub Actions tab. Click "Run workflow." Show it
  running, then succeeding.
- Switch back to the Sheet's `Drafts` tab and show the new row: draft
  text, confidence score, flags, status.
- "This is the same command as running it locally, just triggered from
  a web button instead of a terminal. That's the point for a
  non-developer user."

## 2:00 to 3:00: The non-developer user experience

- Run `python -m lead_drafter.cli review` live in the terminal.
- Walk through one pending-review draft on screen: show the confidence
  score, the flag, the reasoning, and approve/reject it with a
  keypress.
- "The human is always the last step before anything reaches a real
  lead. The system drafts and routes, it never sends."

## 3:00 to 4:00: Evaluation and failure handling

- Show the Evaluation Package (the results table). State the headline:
  "Baseline passed 5 of 12 test cases. System passed all 12."
- Pick ONE concrete failure to narrate (TC11 is the clearest story: a
  $310,000 lead, and baseline addresses them personally, "Dear Robert,"
  while repeating the dollar figure twice in five sentences, pressure on
  someone whose own data says they just went through a foreclosure. The
  system treated it like any other lead, no manufactured pressure).
- Mention one real bug found during actual testing (the Drafts sheet
  silently missing its header on the very first live write) to show
  this was actually stress-tested, not just demoed once and shipped.

## 4:00 to 4:45: Results and the most important limitation

- Restate the headline number once more for emphasis.
- State the single most important limitation, plainly: "The whole
  human-review gate depends on the LLM's own self-reported confidence
  score. Nothing independently verifies that number is honest. I added
  a second LLM call that checks the draft for unsupported claims, but
  that's a partial mitigation, not a complete fix. It's still one more
  LLM checking another LLM, not a deterministic guarantee."

## 4:45 to 5:00: Close

- "Next priority is adding retry/backoff to the live CLI. I hit a real
  transient API failure during testing today, so that's not a
  hypothetical, it's something that already happened once."
- End.
