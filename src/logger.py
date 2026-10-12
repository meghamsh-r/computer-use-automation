import json
from datetime import datetime, timezone
from pathlib import Path


EVIDENCE_DIR = Path("evidence")
EVIDENCE_DIR.mkdir(exist_ok=True)


def save_run_log(filename: str, data: dict):
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **data,
    }

    path = EVIDENCE_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return str(path)