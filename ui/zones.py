"""ui/zones.py — single source of truth for zone metadata.

Used by pages/*.py (for chrome) and app.py's postMessage bridge
(the `key` values here must match the `zone` field the game sends).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ZoneMeta:
    key: str            # matches config.ZONE_SPACE_IDS key + game zone id
    title: str
    icon: str
    tagline: str
    sample_questions: tuple[str, ...]
    production: bool    # True only for Placement per CONTEXT.md


ZONES: dict[str, ZoneMeta] = {
    "placement": ZoneMeta(
        key="placement",
        title="Placement Cell",
        icon="💼",
        tagline="Ask about companies, drives, CTC, and placement stats.",
        sample_questions=(
            "How many CSE students were placed in 2024?",
            "What's the average CTC for ISE this year?",
            "Which companies visited with tier 1 packages?",
        ),
        production=True,
    ),
    "library": ZoneMeta(
        key="library",
        title="Library",
        icon="📚",
        tagline="Ask about books, study rooms, research papers, and hours.",
        sample_questions=(
            "Is the reading room open on Sundays?",
            "How many copies of Introduction to Algorithms are available?",
        ),
        production=False,
    ),
    "canteen": ZoneMeta(
        key="canteen",
        title="Canteen",
        icon="🍽️",
        tagline="Ask about the menu, timings, and dietary options.",
        sample_questions=(
            "What's on the menu today?",
            "Is there a gluten-free option?",
        ),
        production=False,
    ),
    "rd": ZoneMeta(
        key="rd",
        title="R&D Lab",
        icon="🔬",
        tagline="Ask about projects, publications, equipment, and openings.",
        sample_questions=(
            "What active research projects are in AI/ML?",
            "Is the 3D printer available this week?",
        ),
        production=False,
    ),
}
