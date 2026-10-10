from server_health import get_server_health
from cpu import get_cpu_usage
from memory import get_memory_status
from sessions import get_user_sessions
from active_requests import get_active_requests
from blocking import get_blocking_requests
from locks import get_locks


from telemetry_repository import save_snapshot
from rule_engine import evaluate_snapshot
from alert_repository import create_alert
from evidence_repository import save_evidence

from incident_repository import (
    find_open_incident,
    create_incident,
    update_incident,
    resolve_incident
)


def collect_snapshot():

    snapshot = {
        "server_health": get_server_health(),
        "cpu": get_cpu_usage(),
        "memory": get_memory_status(),
        "sessions": get_user_sessions(),
        "requests": get_active_requests(),
        "blocking": get_blocking_requests(),
        "locks": get_locks()
    }

    return snapshot


def process_snapshot():

    # -------------------------------------------------
    # 1. Collect telemetry
    # -------------------------------------------------

    snapshot = collect_snapshot()

    # -------------------------------------------------
    # 2. Save telemetry snapshot
    # -------------------------------------------------

    snapshot_id = save_snapshot(snapshot)

    # -------------------------------------------------
    # 3. Evaluate monitoring rules
    # -------------------------------------------------

    evaluation = evaluate_snapshot(snapshot)

    server_name = snapshot.get(
        "server_health", {}
    ).get("server")

    database_name = snapshot.get(
        "server_health", {}
    ).get("database")

    # -------------------------------------------------
    # 4. Process each metric
    # -------------------------------------------------

    for metric, result in evaluation.items():

        severity = result["severity"]
        message = result["message"]

        # -------------------------------------------------
        # Problem detected
        # -------------------------------------------------

        if severity in ("WARNING", "CRITICAL"):

            existing_incident = find_open_incident(
                server_name,
                database_name,
                metric
            )

            # ---------------------------------------------
            # Existing OPEN incident
            # ---------------------------------------------

            if existing_incident:

                incident_id = existing_incident[0]

                update_incident(
                    incident_id,
                    snapshot_id,
                    severity,
                    message
                )

                print(
                    f"INCIDENT UPDATED: "
                    f"id={incident_id}, "
                    f"metric={metric}, "
                    f"severity={severity}"
                )

            # ---------------------------------------------
            # No OPEN incident
            # ---------------------------------------------

            else:

                incident_id = create_incident(
                    snapshot_id,
                    server_name,
                    database_name,
                    metric,
                    severity,
                    message
                )

                print(
                    f"INCIDENT CREATED: "
                    f"id={incident_id}, "
                    f"metric={metric}, "
                    f"severity={severity}"
                )

                alert_id = create_alert(
                    snapshot_id=snapshot_id,
                    server_name=server_name,
                    database_name=database_name,
                    metric=metric,
                    severity=severity,
                    message=message
                )

                print(
                    f"ALERT CREATED: "
                    f"id={alert_id}"
                )

            # ---------------------------------------------
            # Save incident evidence
            # ---------------------------------------------

            metric_evidence = snapshot.get(metric)

            if isinstance(metric_evidence, list):

                for evidence in metric_evidence:

                    evidence_id = save_evidence(
                        incident_id=incident_id,
                        snapshot_id=snapshot_id,
                        evidence_type=metric.upper(),
                        evidence=evidence,
                        severity=severity
                    )

                    print(
                        f"EVIDENCE SAVED: "
                        f"id={evidence_id}, "
                        f"type={metric.upper()}"
                    )

            elif isinstance(metric_evidence, dict):

                evidence_id = save_evidence(
                    incident_id=incident_id,
                    snapshot_id=snapshot_id,
                    evidence_type=metric.upper(),
                    evidence=metric_evidence,
                    severity=severity
                )

                print(
                    f"EVIDENCE SAVED: "
                    f"id={evidence_id}, "
                    f"type={metric.upper()}"
                )

        # -------------------------------------------------
        # Condition is normal
        # -------------------------------------------------

        else:

            existing_incident = find_open_incident(
                server_name,
                database_name,
                metric
            )

            if existing_incident:

                incident_id = existing_incident[0]

                resolve_incident(
                    incident_id,
                    snapshot_id
                )

                print(
                    f"INCIDENT RESOLVED: "
                    f"id={incident_id}, "
                    f"metric={metric}"
                )

    return snapshot, evaluation


if __name__ == "__main__":

    snapshot, evaluation = process_snapshot()

    print("\n========== RULE ENGINE ==========\n")

    for metric, result in evaluation.items():

        print(
            f"{metric}: "
            f"{result['severity']} - "
            f"{result['message']}"
        )

    print("\nMonitoring snapshot saved successfully.")

