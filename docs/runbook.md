# Operator Runbook

## Google Sheet setup

1. Create a new Google Sheet.
2. Create two tabs, named exactly `Leads` and `Drafts`.
3. In `Leads`, add this header row: `lead_id | name | context | contact_email | contact_sms`
4. Add a few rows of lead data below it (see `tests/test_cases.json` for
   realistic examples to copy in).
5. Leave `Drafts` empty — the system creates its header row automatically
   on first run.
6. Get the Sheet ID from its URL: `docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
   — put that in `.env` as `GOOGLE_SHEET_ID`.

## Google service account credentials

1. In Google Cloud Console, create a project (or use an existing one).
2. Enable the "Google Sheets API".
3. Create a Service Account, then create a JSON key for it — download it
   as `credentials.json` and place it in the project root.
4. Open your Google Sheet, click Share, and share it with the service
   account's email address (found inside `credentials.json`, the
   `client_email` field) with Editor access.
5. Set `GOOGLE_SHEETS_CREDS_PATH` in `.env` to point at this file.

## Running it live on a schedule (GitHub Actions)

The workflow at `.github/workflows/draft-leads.yml` runs `draft-new`
automatically every hour (adjust the cron schedule as needed), and can
also be triggered manually from the repo's Actions tab.

Setup, in your GitHub repo settings → Secrets and variables → Actions:

1. Add these repository secrets:
   - `LLM_PROVIDER` — `openai` or `anthropic`
   - `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`
   - `LLM_MODEL`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_CREDENTIALS_B64` — your `credentials.json`, base64-encoded
     (run `base64 -i credentials.json | tr -d '\n'` locally and paste the
     output as the secret value — never commit the raw file)
2. Push to GitHub. The schedule starts automatically; you can also click
   "Run workflow" on the Actions tab to trigger it immediately for a demo.
3. Check the Actions tab's run logs to see what happened on each run —
   this is your production monitoring/logging for this workflow.

This is genuinely free (GitHub Actions free minutes on a public repo)
and has no cold-start/sleep issue, unlike a free-tier web service —
appropriate since this workflow is trigger/batch-style, not
request-response.

## Day-to-day operation

- Run `python -m lead_drafter.cli draft-new` whenever new leads have been
  added to the `Leads` tab. This drafts outreach for each one and logs it
  to `Drafts`.
- Run `python -m lead_drafter.cli review` to see anything flagged for
  review and approve/reject with a keypress.
- Approved drafts are marked `approved` in the sheet — actually sending
  the message (via an email/SMS provider) is intentionally out of scope
  for this build; see case_study.md's "non-goals" section for why.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `RuntimeError: Missing required config` | `.env` isn't filled in, or wasn't copied from `.env.example` |
| `LLM returned non-JSON output, cannot parse` | Rare model formatting slip — re-run `draft-new`, it will retry that lead on the next pass since it still shows as "pending" |
| `No lead found with lead_id=...` | Typo in the sheet, or the row was deleted after the CLI already read the list |
| Google Sheets permission error | The sheet wasn't shared with the service account's email — see setup step 4 above |

## Known limitations (see case_study.md for full list)

- Does not validate email/phone format before drafting (drafts anyway;
  a "ready to send" format check would be the next iteration)
- Confidence scoring is self-reported by the LLM, not independently verified
- No retry/backoff on API rate limits yet — a failed call for one lead is
  logged as an error and skipped, not automatically retried
