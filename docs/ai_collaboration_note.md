# AI Collaboration Note

## AI tools used and the role of each

- **Claude (Anthropic)**: used throughout the 5 days as a pair-programmer
  and planning partner. Scoping the problem down from an initial
  over-broad idea, drafting the Python code structure, writing the test
  case set, and drafting this documentation set.
- **Google Gemini API** (`gemini-3.5-flash-lite`): the actual production
  system under test. The `drafter.py` module calls this API to generate
  the outreach drafts being evaluated. Picked over OpenAI/Anthropic
  specifically for a workable free tier. `drafter.py` and `baseline.py`
  also support OpenAI/Anthropic as alternate providers if needed.

## Work delegated to AI (Claude)

- First-draft Python code for `drafter.py`, `sheets_client.py`, `cli.py`,
  `run_eval.py`, and the evaluation rubric structure.
- First-draft synthetic test cases, informed by real failure modes I
  described from professional experience with a similar system
  (ambiguous/contradictory data, thin data, injection-shaped input, tone
  given prior complaint history).
- First-draft documentation structure (README, runbook, case study
  skeleton).

## How I verified AI-generated results

- Ran the full eval against my own real Gemini key and Google Sheet,
  then hand-scored all 12 draft outputs against the written rubric
  myself, reading the actual email/SMS text and matching it to the
  rubric's specific 0/1/2 wording, not going by gut feel or accepting
  Claude's first proposed score.
- Did not trust the model's self-reported confidence or flags at face
  value: when NC02 (emoji-only context) flagged "Contact SMS is provided
  as a numeric value rather than a formatted string," I checked it
  against the actual input myself (`+15551110002`). It's a string, not a
  number (it has a `+` prefix, which couldn't even be valid in a numeric
  type), and it's already properly formatted. The flag's own claim was
  factually wrong, a reminder that even the system's own flags can
  contain incorrect reasoning, not just its drafts.
- Personally ran the real CLI commands (`draft-new`, `review`) myself
  against the live sheet, rather than only reviewing Claude's runs, to
  get genuine non-developer-execution evidence.

## Important results I rejected or manually corrected

- My own first-pass rubric score for TC04 (a lead with zero data at all)
  gave the baseline all 2s. After re-reading the actual baseline output
  (it drafted a full, polished-sounding pitch for a lead with no name,
  no context, and no contact info whatsoever) I corrected that to 3/8
  (Grounding=0, Failure Handling=0), since a draft fabricated from
  literally nothing shouldn't score as if nothing went wrong.
- Confirmed the NC02 flag-accuracy issue above by checking the raw input
  data directly rather than accepting the system's own flag text as true.

## Core decisions I personally owned

- The choice to scope this to outbound drafting only (not reply
  classification), based on how the real-world equivalent system
  actually splits AI vs. deterministic logic.
- The choice to hold drafts for human review rather than auto-send,
  reasoned from responsible-AI judgment about outbound content to real
  people, not just because the rubric asks for approval points.
- The decision to use fully synthetic data and freshly written code
  throughout, to avoid any IP conflict with a real system I've worked on
  professionally.
- Choosing Google Gemini as the LLM provider, specifically for a
  workable free tier over OpenAI/Anthropic's paid-only APIs.
- Requiring a branch, tests, PR, green CI, merge workflow (with branch
  protection actually enforcing it) for every change to this repo,
  including my own. Not just documentation, an enforced rule.
- Confirming the "surplus fund recovery" outreach scenario is a fair,
  generic description of my real professional domain rather than
  something that crosses into actual employer-specific business logic.
- Prioritizing "add retry/backoff to the live CLI" as the top item in
  the next two-week iteration plan, based on hitting a real transient
  API failure (a live `503`) during actual testing, not a hypothetical.
- Choosing manual-trigger-only for the GitHub Actions workflow over an
  automatic schedule, to avoid burning the free-tier quota on unattended
  runs that would mostly find nothing new.
- Initially proposed hardcoding the business type ("you are a surplus
  recovery business") directly into the system prompt for more
  consistent framing. After Claude flagged that this would break the
  system's general-purpose design and risk reintroducing grounding
  violations for unrelated leads, I agreed to use config
  (`BUSINESS_DESCRIPTION`) instead. A case of accepting pushback on my
  own idea rather than just going with what I first suggested.
