from datetime import datetime, timedelta, timezone

from telemetry_policy import should_save_snapshot

now = datetime.now(timezone.utc)

normal = {
    "cpu": {
        "severity": "OK",
        "message": "CPU normal"
    }
}

critical = {
    "cpu": {
        "severity": "CRITICAL",
        "message": "CPU high"
    }
}

tests = [
    (
        "First snapshot",
        normal,
        None
    ),
    (
        "Normal after 10 seconds",
        normal,
        now - timedelta(seconds=10)
    ),
    (
        "Normal after 5 minutes",
        normal,
        now - timedelta(minutes=5)
    ),
    (
        "Critical CPU",
        critical,
        now - timedelta(seconds=10)
    )
]

for name, evaluation, last_saved in tests:

    result = should_save_snapshot(
        evaluation,
        last_saved,
        now
    )

    print(f"{name}: Save = {result}")