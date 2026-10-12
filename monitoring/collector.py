"""SQL Server telemetry collector and incident processor.

Collect/evaluate every scheduler cycle; persist selectively.
"""
from datetime import datetime, timezone
from time import monotonic
from collections import defaultdict, deque
import json
import logging

from server_health import get_server_health
from cpu import get_cpu_usage
from memory import get_memory_status
from sessions import get_user_sessions
from active_requests import get_active_requests
from blocking import get_blocking_requests
from locks import get_locks

from telemetry_repository import save_snapshot, get_last_snapshot_time
from rule_engine import evaluate_snapshot
from alert_repository import create_alert
from evidence_repository import save_evidence
from incident_repository import (
    find_open_incident, create_incident, update_incident, resolve_incident
)
from cpu_rules import evaluate_cpu_history
from telemetry_policy import should_save_snapshot
from top_cpu_queries import get_top_cpu_queries
from query_store import get_query_store_top_cpu

logger = logging.getLogger(__name__)


def capture_cpu_query_evidence(incident_id, snapshot_id, severity, database_name):
    """Capture potential query contributors once when a CPU incident is created."""
    sources = (
        ("TOP_CPU_CACHED", lambda: get_top_cpu_queries(limit=10)),
        ("TOP_CPU_QUERY_STORE", lambda: get_query_store_top_cpu(
            database=database_name or "Vehicle", hours=1, limit=10)),
    )
    for evidence_type, fetch in sources:
        try:
            queries = fetch()
            for query in queries:
                evidence = json.loads(json.dumps(query, default=str))
                print("DEBUG SOURCE:", evidence_type)
                print("DEBUG DATABASE:", repr(evidence.get("database_name")))
                print("DEBUG SQL:", str(evidence.get("sql_text"))[:100])
                evidence["source"] = evidence_type
                evidence["attribution"] = "potential_contributor_not_confirmed"
                evidence["cpu_scope"] = (
                    "cumulative_since_plan_cached" if evidence_type == "TOP_CPU_CACHED"
                    else "aggregated_query_store_intervals_last_hour"
                )
                evidence["cpu_time_ms"] = evidence.get("total_cpu_ms")
                evidence["logical_reads"] = evidence.get("total_logical_reads")
                save_evidence(
                    incident_id=incident_id,
                    snapshot_id=snapshot_id,
                    evidence_type=evidence_type,
                    evidence=evidence,
                    severity=severity,
                )
            print(f"QUERY EVIDENCE: {evidence_type} saved {len(queries)} rows")
        except Exception:
            logger.exception("Unable to capture %s for incident %s", evidence_type, incident_id)


# psutil measures SQL Server process CPU during each collection cycle.
# Allow one independent observation per scheduler cycle (~10 seconds).
# A minimum gap avoids double counting if the collector is called rapidly.
CPU_SAMPLE_MIN_SECONDS = 8
_cpu_history = defaultdict(lambda: deque(maxlen=3))
_cpu_last_sample_at = {}


def collect_snapshot():
    return {
        "server_health": get_server_health(),
        "cpu": get_cpu_usage(),
        "memory": get_memory_status(),
        "sessions": get_user_sessions(),
        "requests": get_active_requests(),
        "blocking": get_blocking_requests(),
        "locks": get_locks(),
    }


def evaluate_sustained_cpu(server_name, cpu_data):
    """Use spaced live CPU observations, independent of DB storage."""
    value = cpu_data.get("value")
    if value is None:
        return {"severity": "PENDING", "message": "CPU measurement unavailable"}

    try:
        value = float(value)
    except (TypeError, ValueError):
        return {"severity": "PENDING", "message": "Invalid CPU measurement"}

    now = monotonic()
    last = _cpu_last_sample_at.get(server_name)
    if last is None or now - last >= CPU_SAMPLE_MIN_SECONDS:
        _cpu_history[server_name].append(value)
        _cpu_last_sample_at[server_name] = now

    values = list(_cpu_history[server_name])
    result = evaluate_cpu_history(values)
    print(f"CPU RULE: values={values}, severity={result['severity']}")
    return result


def process_snapshot():
    snapshot = collect_snapshot()
    evaluation = evaluate_snapshot(snapshot)
    server_name = snapshot.get("server_health", {}).get("server")
    database_name = snapshot.get("server_health", {}).get("database")
    if not server_name:
        raise ValueError("Missing server name in server_health; refusing to mix CPU histories")

    # Override only CPU; preserve memory, requests, blocking and locks rules.
    evaluation["cpu"] = evaluate_sustained_cpu(server_name, snapshot.get("cpu", {}))

    # Read existing incidents BEFORE deciding whether this cycle needs a snapshot.
    # This ensures incident recovery always has a valid snapshot_id.
    open_incidents = {}
    for metric, result in evaluation.items():
        if result["severity"] not in ("PENDING", "UNKNOWN"):
            open_incidents[metric] = find_open_incident(
                server_name, database_name, metric
            )

    last_saved_at = get_last_snapshot_time(server_name)
    save_needed = should_save_snapshot(
        evaluation=evaluation,
        last_saved_at=last_saved_at,
        cpu_value=snapshot.get("cpu", {}).get("value"),
        has_open_incident=any(bool(incident) for incident in open_incidents.values()),
        now=datetime.now(timezone.utc),
    )

    if not save_needed:
        print("Healthy telemetry skipped (storage policy)")
        return snapshot, evaluation

    snapshot_id = save_snapshot(snapshot)
    print(f"SNAPSHOT SAVED: id={snapshot_id}")

    for metric, result in evaluation.items():
        severity = result["severity"]
        message = result["message"]
        if severity in ("PENDING", "UNKNOWN"):
            continue
        existing_incident = open_incidents.get(metric)
        # -------------------------------------------------
        # Problem detected
        # -------------------------------------------------

        if severity in ("WARNING", "CRITICAL"):

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

                # Capture only when a NEW CPU incident opens; not every scheduler cycle.
                if metric == "cpu":
                    capture_cpu_query_evidence(
                        incident_id, snapshot_id, severity, database_name
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
        print(f"{metric}: {result['severity']} - {result['message']}")
