"""Selective telemetry persistence. Monitoring evaluation always runs."""
from datetime import datetime, timedelta, timezone

NORMAL_SAVE_INTERVAL = timedelta(minutes=5)
CPU_STORAGE_THRESHOLD = 20


def should_save_snapshot(evaluation, last_saved_at, cpu_value=None,
                         has_open_incident=False, now=None):
    if now is None:
        now = datetime.now(timezone.utc)

    # Incident create/update AND recovery need a persisted snapshot FK.
    if has_open_incident:
        return True
    if any(result["severity"] in ("WARNING", "CRITICAL")
           for result in evaluation.values()):
        return True

    # Save routine readings at or above the requested 20% threshold.
    try:
        if cpu_value is not None and float(cpu_value) >= CPU_STORAGE_THRESHOLD:
            return True
    except (TypeError, ValueError):
        pass

    # Retain a sparse baseline, including healthy CPU below 20%.
    if last_saved_at is None:
        return True
    return now - last_saved_at >= NORMAL_SAVE_INTERVAL
