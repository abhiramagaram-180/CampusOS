"""
CampusOS — smoke test for the Genie client.

OWNER: Person 1.

Run this to prove the wire works, WITHOUT involving the UI. This is how you
tell "the backend is broken" apart from "the frontend is broken" at 2am.

    python test_client.py                    # mock mode (default)
    CAMPUSOS_MOCK=false python test_client.py  # live Databricks

For live mode you need, in your environment:
    DATABRICKS_HOST=https://dbc-xxxx.cloud.databricks.com
    DATABRICKS_TOKEN=dapi...            (never commit this)
    GENIE_SPACE_PLACEMENT=01f1...
"""

from config import MOCK_MODE, ZONE_SPACE_IDS
from genie_client import ask_genie

QUESTIONS = [
    "Which companies made the most offers last year?",
    "What is the average package for CSE?",
]

FOLLOW_UP = "Now break that down by branch"


def show(label, ans):
    print("=" * 70)
    print(label)
    print("=" * 70)
    if ans.error:
        print("ERROR:", ans.error)
        return
    print("TEXT:", ans.text)
    print("\nSQL:", (ans.sql or "(none)"))
    if ans.df is not None:
        print(f"\nROWS: {len(ans.df)}  COLUMNS: {list(ans.df.columns)}")
        print(ans.df.head())
    else:
        print("\nROWS: none (text-only answer)")
    print("\nconversation_id:", ans.conversation_id)
    print()


def main():
    print(f"\nMODE: {'MOCK' if MOCK_MODE else 'LIVE DATABRICKS'}")
    if not MOCK_MODE:
        print(f"placement space id: {ZONE_SPACE_IDS.get('placement') or '(NOT SET)'}\n")

    last = None
    for q in QUESTIONS:
        last = ask_genie("placement", q)
        show(f"Q: {q}", last)

    if last and last.conversation_id and not last.error:
        follow = ask_genie("placement", FOLLOW_UP, last.conversation_id)
        show(f"FOLLOW-UP: {FOLLOW_UP}", follow)
        if follow.conversation_id == last.conversation_id:
            print("Conversation state carried over correctly.\n")

    # Error path — the UI must handle this without crashing.
    show("Q: (empty)", ask_genie("placement", ""))
    show("Q: unbuilt zone", ask_genie("library", "How many books?"))


if __name__ == "__main__":
    main()
