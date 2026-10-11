from datetime import datetime, timezone

from cpu import get_cpu_usage
from memory import get_memory_status
from sessions import get_user_sessions
from active_requests import get_active_requests
from blocking import get_blocking_requests
from server_health import get_server_health


def get_live_health():

    return {
        "collected_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "server_health": get_server_health(),

        "cpu": get_cpu_usage(),

        "memory": get_memory_status(),

        "sessions": get_user_sessions(),

        "requests": get_active_requests(),

        "blocking": get_blocking_requests()
    }


if __name__ == "__main__":
    import json

    print(json.dumps(
        get_live_health(),
        indent=2,
        default=str
    ))