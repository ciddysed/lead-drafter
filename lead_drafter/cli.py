"""
Non-developer-facing CLI. Two commands:

    python -m lead_drafter.cli draft-new
        Finds leads in the sheet with no draft yet, drafts outreach for
        each, and logs the result. Anything below the confidence threshold
        (or flagged) is marked "pending_review" instead of auto-approved.

    python -m lead_drafter.cli review
        Shows all pending-review drafts one at a time and lets a human
        approve or reject each with a single keypress.

No coding knowledge needed to run either — just the two commands above.
"""
import sys
from lead_drafter.config import config
from lead_drafter.drafter import draft_outreach
from lead_drafter import sheets_client as sheets


def cmd_draft_new():
    config.validate()
    pending = sheets.list_pending_leads()
    if not pending:
        print("No new leads waiting for a draft. Nothing to do.")
        return

    print(f"Found {len(pending)} lead(s) needing a draft.\n")
    for lead in pending:
        lead_id = lead.get("lead_id")
        print(f"--- Drafting for lead {lead_id} ({lead.get('name', 'unknown')}) ---")
        try:
            result = draft_outreach(lead)
        except ValueError as e:
            print(f"  SKIPPED — {e}\n")
            continue
        except RuntimeError as e:
            print(f"  ERROR — {e}\n")
            continue

        sheets.log_draft(lead_id, result)
        status = "NEEDS REVIEW" if result["needs_review"] else "auto-approved"
        print(f"  Confidence: {result['confidence']:.2f}  |  Status: {status}")
        if result["flags"]:
            print(f"  Flags: {', '.join(result['flags'])}")
        print()

    print("Done. Run `python -m lead_drafter.cli review` to check anything pending review.")


def cmd_review():
    config.validate()
    pending = sheets.list_pending_review()
    if not pending:
        print("Nothing pending review. All caught up.")
        return

    for row in pending:
        print("=" * 60)
        print(f"Lead ID: {row['lead_id']}")
        print(f"Confidence: {row['confidence']}  |  Flags: {row['flags'] or 'none'}")
        print(f"Reasoning: {row['reasoning']}")
        print(f"\nEMAIL DRAFT:\n{row['email_draft']}")
        print(f"\nSMS DRAFT:\n{row['sms_draft']}")
        choice = input("\nApprove this draft? [y/n/skip]: ").strip().lower()
        if choice == "y":
            sheets.update_draft_status(row["lead_id"], "approved")
            print("Approved.\n")
        elif choice == "n":
            sheets.update_draft_status(row["lead_id"], "rejected")
            print("Rejected.\n")
        else:
            print("Skipped — left pending.\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("draft-new", "review"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "draft-new":
        cmd_draft_new()
    else:
        cmd_review()


if __name__ == "__main__":
    main()
