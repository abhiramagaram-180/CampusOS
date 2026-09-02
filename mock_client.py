"""mock_client.py — fake Genie client for frontend development.

Every page can build against this without touching Databricks. Returns
deterministic fake data in ~1s per zone so all four zones demo, not just
Placement. Flip MOCK_MODE to False in config.py to use genie_client.py.

NOTE: `zone` param is additive — existing call sites that only pass
`question`/`conversation_id` still work (defaults to "placement"), so this
does not touch the frozen GenieAnswer contract.
"""

from __future__ import annotations

import time

import polars as pl

from config import GenieAnswer


_FAKE_ANSWERS: dict[str, GenieAnswer] = {
    "placement": GenieAnswer(
        answer_text=(
            "In 2024, 340 students from CSE were placed with an average CTC of "
            "₹12.4 LPA. Top recruiters included Google, Microsoft, and Amazon "
            "with 42 combined offers."
        ),
        data=pl.DataFrame(
            {
                "branch": ["CSE", "CSE", "CSE", "ISE", "ECE", "ECE"],
                "placed": [340, 42, 28, 195, 160, 35],
                "avg_ctc_lpa": [12.4, 28.0, 18.5, 10.2, 9.8, 11.5],
                "company": [
                    "Total CSE",
                    "Google/Microsoft/Amazon",
                    "Adobe/Qualcomm",
                    "Total ISE",
                    "Total ECE",
                    "Intel/NVIDIA",
                ],
            }
        ),
        sql=(
            "SELECT branch, COUNT(*) AS placed, ROUND(AVG(ctc_lpa), 1) AS avg_ctc_lpa\n"
            "FROM campus.placement.placements p\n"
            "JOIN campus.placement.students s USING (student_id)\n"
            "WHERE year = 2024 AND branch = 'CSE'\n"
            "GROUP BY branch\n"
            "ORDER BY avg_ctc_lpa DESC"
        ),
        conversation_id="mock-conv-placement",
        error=None,
    ),
    "library": GenieAnswer(
        answer_text=(
            "The reading room is open 8am-10pm on weekdays and 9am-6pm on "
            "weekends. There are 3 copies of the most-requested textbook "
            "currently in circulation."
        ),
        data=pl.DataFrame(
            {
                "resource": ["Reading Room", "Group Study Rooms", "Textbook Copies", "Digital Journals"],
                "availability": ["Open now", "2 of 6 free", "3 in circulation", "1,200+ titles"],
            }
        ),
        sql=(
            "SELECT resource, availability\n"
            "FROM campus.library.resource_status\n"
            "WHERE campus = 'PES'\n"
            "ORDER BY resource"
        ),
        conversation_id="mock-conv-library",
        error=None,
    ),
    "canteen": GenieAnswer(
        answer_text=(
            "Today's menu includes South Indian breakfast until 10am, a "
            "North Indian thali for lunch, and a gluten-free salad bar "
            "available all day."
        ),
        data=pl.DataFrame(
            {
                "meal": ["Breakfast", "Lunch", "Snacks", "Dinner"],
                "item": ["Idli/Dosa", "North Indian Thali", "Samosa/Sandwich", "Fried Rice/Noodles"],
                "gluten_free": ["No", "Yes (on request)", "No", "Yes (rice dishes)"],
            }
        ),
        sql=(
            "SELECT meal, item, gluten_free\n"
            "FROM campus.canteen.daily_menu\n"
            "WHERE menu_date = current_date()\n"
            "ORDER BY meal"
        ),
        conversation_id="mock-conv-canteen",
        error=None,
    ),
    "rd": GenieAnswer(
        answer_text=(
            "There are 6 active AI/ML research projects this semester, "
            "spanning computer vision, NLP, and federated learning. The "
            "3D printer lab has open slots on Wednesday and Friday."
        ),
        data=pl.DataFrame(
            {
                "project": ["Federated Vision", "Campus NLP Assistant", "Low-power Edge ML", "Robotics Arm v3"],
                "lead_dept": ["CSE", "ISE", "ECE", "ME"],
                "status": ["Active", "Active", "Active", "Prototype"],
            }
        ),
        sql=(
            "SELECT project, lead_dept, status\n"
            "FROM campus.rd.projects\n"
            "WHERE status IN ('Active', 'Prototype')\n"
            "ORDER BY lead_dept"
        ),
        conversation_id="mock-conv-rd",
        error=None,
    ),
}


def ask_genie(
    question: str,
    conversation_id: str | None = None,
    zone: str = "placement",
) -> GenieAnswer:
    """Return a fake answer for `zone` after a short simulated delay.

    Args:
        question: The user's question (ignored — mock returns fixed data per zone).
        conversation_id: Previous conversation token (ignored in mock).
        zone: Which zone's canned answer to return. Falls back to "placement"
            for any unrecognized zone so this never raises.

    Returns:
        A GenieAnswer with fake data, SQL, and a mock conversation ID.
    """
    time.sleep(1.0)  # simulate round-trip latency
    return _FAKE_ANSWERS.get(zone, _FAKE_ANSWERS["placement"])
