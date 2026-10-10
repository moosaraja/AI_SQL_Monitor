from deadlock_collector import get_deadlocks
from server_health import get_server_health

from telemetry_repository import save_snapshot

from incident_repository import (
    create_incident,
    resolve_incident
)

from evidence_repository import (
    save_evidence,
    evidence_event_exists
)

CHECKED_DEADLOCK_EVENTS = set()

def get_deadlock_database(deadlock):
    """
    Extract the database name from the deadlock
    resource object name.

    Example:
        Vehicle.dbo.DeadlockTest
        -> Vehicle
    """

    resources = deadlock.get(
        "deadlock",
        {}
    ).get(
        "resources",
        []
    )

    for resource in resources:

        object_name = resource.get(
            "objectname"
        )

        if not object_name:
            continue

        parts = object_name.split(".")

        if len(parts) >= 2:
            return parts[0]

    return None


def build_deadlock_snapshot(
    deadlock,
    server_name,
    database_name
):

    return {
        "server_health": {
            "server": server_name,
            "database": database_name
        },
        "deadlock": deadlock
    }


def build_deadlock_evidence(
    deadlock,
    database_name
):

    return {
        "event_id": deadlock["event_id"],
        "deadlock_time": deadlock["deadlock_time"],
        "file_name": deadlock["file_name"],
        "file_offset": deadlock["file_offset"],
        "database_name": database_name,
        "deadlocks": [
            deadlock["deadlock"]
        ]
    }


def process_deadlocks():

    deadlocks = get_deadlocks()

    print(
        f"\nDeadlock events found: {len(deadlocks)}"
    )

    if not deadlocks:
        return []

    server_health = get_server_health()

    server_name = server_health.get(
        "server"
    )

    print(
        f"Server: {server_name}"
    )

    processed = []

    for deadlock in deadlocks:

        event_id = deadlock["event_id"]

        # Already checked during this scheduler process
        if event_id in CHECKED_DEADLOCK_EVENTS:
            continue

        # Remember this event to avoid checking it repeatedly
        CHECKED_DEADLOCK_EVENTS.add(event_id)

        # Check whether it was processed in an earlier run
        if evidence_event_exists(event_id):
            continue

        print(f"\nProcessing new deadlock event: {event_id}")

        # --------------------------------------------------
        # Determine the actual affected database
        # --------------------------------------------------

        database_name = get_deadlock_database(
            deadlock
        )

        if not database_name:

            print(
                "WARNING: Could not determine "
                "deadlock database. Skipping event."
            )

            continue

        print(
            f"Deadlock database: {database_name}"
        )

        # --------------------------------------------------
        # Build snapshot
        # --------------------------------------------------

        snapshot = build_deadlock_snapshot(
            deadlock,
            server_name,
            database_name
        )

        snapshot_id = save_snapshot(
            snapshot
        )

        print(
            f"Snapshot created: {snapshot_id}"
        )

        # --------------------------------------------------
        # Create incident
        # --------------------------------------------------

        incident_id = create_incident(
            snapshot_id,
            server_name,
            database_name,
            "deadlock",
            "CRITICAL",
            "SQL Server deadlock detected."
        )

        print(
            f"Incident created: {incident_id}"
        )

        # --------------------------------------------------
        # Build evidence
        # --------------------------------------------------

        evidence = build_deadlock_evidence(
            deadlock,
            database_name
        )

        # --------------------------------------------------
        # Save evidence
        # --------------------------------------------------

        evidence_rows = save_evidence(
            incident_id,
            snapshot_id,
            "DEADLOCK",
            evidence,
            "CRITICAL"
        )

        print(
            f"Deadlock evidence saved: "
            f"{evidence_rows} row(s)"
        )
        
        CHECKED_DEADLOCK_EVENTS.add(event_id)

        # --------------------------------------------------
        # Deadlock is an event.
        # It has already completed, so resolve it.
        # --------------------------------------------------

        resolve_incident(
            incident_id,
            snapshot_id
        )

        print(
            f"Incident resolved: {incident_id}"
        )

        processed.append({
            "event_id": event_id,
            "snapshot_id": snapshot_id,
            "incident_id": incident_id,
            "database_name": database_name
        })

    return processed


if __name__ == "__main__":

    print(
        "\n========== DEADLOCK MONITOR ==========\n"
    )

    results = process_deadlocks()

    print(
        f"\nNew deadlocks processed: {len(results)}"
    )

    for result in results:

        print(
            f"\nEvent ID: "
            f"{result['event_id']}"
        )

        print(
            f"Snapshot ID: "
            f"{result['snapshot_id']}"
        )

        print(
            f"Incident ID: "
            f"{result['incident_id']}"
        )

        print(
            f"Database: "
            f"{result['database_name']}"
        )

    print(
        "\n=======================================\n"
    )