"""pages/library_chat.py — library zone Genie chat page.

All logic lives in ui.render.run_zone_page so every zone stays on the
identical architecture (see CONTEXT.md). Zone-specific copy lives in
ui/zones.py, not here.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.render import run_zone_page

run_zone_page("library")
