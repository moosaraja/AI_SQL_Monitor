def analyze_deadlock(evidence_rows):

    if not evidence_rows:
        return {
            "status": "NO_DEADLOCK_EVIDENCE",
            "message": "No deadlock evidence available.",
            "deadlocks": [],
            "deadlock_count": 0
        }

    deadlocks = []

    for row in evidence_rows:

        evidence_data = row.get("evidence_data", {})

        deadlock_data = evidence_data.get("deadlocks", [])

        if not isinstance(deadlock_data, list):
            continue

        for deadlock in deadlock_data:

            deadlocks.append(deadlock)

    if not deadlocks:
        return {
            "status": "NO_DEADLOCK_DETECTED",
            "message": "No deadlock events were found in the supplied evidence.",
            "deadlocks": [],
            "deadlock_count": 0
        }

    return {
        "status": "DEADLOCK_DETECTED",
        "message": f"{len(deadlocks)} deadlock event(s) detected.",
        "deadlocks": deadlocks,
        "deadlock_count": len(deadlocks)
    }