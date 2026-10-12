from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json


class ControlState(str, Enum):
    AUTOMATION = "AUTOMATION"
    PAUSED = "PAUSED"
    HUMAN = "HUMAN"
    COMPLETE = "COMPLETE"


class HandoffManager:
    def __init__(self):
        self.state = ControlState.AUTOMATION
        self.events = []

    def _record(self, event, reason=None):
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "state": self.state.value,
            "reason": reason,
        })

    def request_human(self, reason, surface):
        self.state = ControlState.PAUSED
        self._record("intervention_requested", reason)

        surface.screenshot(
            "evidence/handoff_requested.png"
        )

        print("\n=== HUMAN INTERVENTION REQUIRED ===")
        print("Reason:", reason)
        print("The existing browser remains open.")

        self.state = ControlState.HUMAN
        self._record("control_transferred_to_human")

    def wait_for_human(self):
        input(
            "\nUse the SAME browser window manually. "
            "When finished, return here and press ENTER..."
        )

        self._record("human_actions_completed")

        self.state = ControlState.AUTOMATION
        self._record("control_returned_to_automation")

    def complete(self):
        self.state = ControlState.COMPLETE
        self._record("run_completed")

    def save(self):
        Path("evidence").mkdir(exist_ok=True)

        with open(
            "evidence/handoff_log.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                {"events": self.events},
                file,
                indent=2,
            )