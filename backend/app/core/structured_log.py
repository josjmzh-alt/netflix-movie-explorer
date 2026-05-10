import json
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


def log_event(event: str, *, debug: bool = False, **fields: Any) -> None:
    if debug and not settings.debug_drive_logs:
        return

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, default=str), flush=True)
