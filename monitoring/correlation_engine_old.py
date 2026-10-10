def analyze_blocking(evidence_rows):

    if not evidence_rows:
        return {
            "status": "NO_BLOCKING",
            "message": "No blocking evidence found.",
            "blockers": [],
            "blocked_sessions": []
        }

    blockers = {}
    blocked_sessions = []
    relationships = []

    for evidence in evidence_rows:

        evidence_data = evidence.get(
            "evidence_data",
            {}
        )

        blocking_requests = evidence_data.get(
            "blocking_requests",
            []
        )

        for request in blocking_requests:

            blocking_session_data = request.get(
                "blocking_session",
                {}
            )

            blocked_session_data = request.get(
                "blocked_session",
                {}
            )

            blocking_session = blocking_session_data.get(
                "session_id"
            )

            blocked_session = blocked_session_data.get(
                "session_id"
            )

            if (
                blocking_session is None
                or blocked_session is None
            ):
                continue

            blocked_sessions.append(
                blocked_session
            )

            if blocking_session not in blockers:
                blockers[blocking_session] = []

            blockers[blocking_session].append(
                blocked_session
            )

            relationships.append(
                {
                    "blocker": blocking_session,
                    "blocked": blocked_session,

                    "database_name": request.get(
                        "database_name"
                    ),

                    "blocked_session_details":
                        blocked_session_data,

                    "blocking_session_details":
                        blocking_session_data
                }
            )

    if not relationships:
        return {
            "status": "NO_BLOCKING",
            "message": "No blocking relationship identified.",
            "blockers": [],
            "blocked_sessions": []
        }

    primary_blocker = max(
        blockers,
        key=lambda session_id: len(
            blockers[session_id]
        )
    )

    primary_blocker_details = None

    for relationship in relationships:

        if relationship["blocker"] == primary_blocker:

            primary_blocker_details = relationship[
                "blocking_session_details"
            ]

            break

    return {
        "status": "BLOCKING_DETECTED",

        "primary_blocker": primary_blocker,

        "primary_blocker_details":
            primary_blocker_details,

        "blockers": relationships,

        "blocked_sessions": blocked_sessions,

        "blocked_session_count": len(
            blocked_sessions
        ),

        "message": (
            f"Session {primary_blocker} "
            f"is blocking "
            f"{len(blockers[primary_blocker])} "
            f"session(s)."
        )
    }


def analyze_incident(evidence_rows):

    blocking_evidence = [
        row
        for row in evidence_rows
        if row.get("evidence_type") == "BLOCKING"
    ]

    return {
        "blocking": analyze_blocking(
            blocking_evidence
        )
    }