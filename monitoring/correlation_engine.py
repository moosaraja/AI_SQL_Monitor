from analyzer_registry import get_analyzer


def analyze_incident(evidence_rows):

    if not evidence_rows:
        return {
            "status": "NO_EVIDENCE",
            "message": "No evidence available for correlation.",
            "evidence_types": [],
            "analyses": {}
        }

    analyses = {}
    evidence_types = set()

    for row in evidence_rows:

        evidence_type = row.get("evidence_type")

        if not evidence_type:
            continue

        evidence_type = evidence_type.upper()

        evidence_types.add(evidence_type)

    for evidence_type in evidence_types:

        analyzer = get_analyzer(evidence_type)

        if not analyzer:
            continue

        matching_evidence = [
            row
            for row in evidence_rows
            if row.get("evidence_type", "").upper() == evidence_type
        ]

        analyses[evidence_type.lower()] = analyzer(matching_evidence)

    query_candidates = summarize_query_evidence(evidence_rows)
    if query_candidates:
        analyses["query_performance"] = {
            "status": "POTENTIAL_CONTRIBUTORS",
            "candidate_count": len(query_candidates),
            "candidates": query_candidates[:10],
            "message": "Historical/cached CPU ranking is not causal attribution."
        }

    return {
        "status": "ANALYSIS_COMPLETE",
        "evidence_types": sorted(evidence_types),
        "analyses": analyses
    }

def summarize_query_evidence(evidence_rows):
    """Summarize persisted query candidates without asserting causality."""
    candidates = []
    for row in evidence_rows:
        source = (row.get("evidence_type") or "").upper()
        if source not in ("TOP_CPU_CACHED", "TOP_CPU_QUERY_STORE"):
            continue
        data = row.get("evidence_data") or {}
        if not isinstance(data, dict):
            data = {}
        candidates.append({
            "source": source,
            "database_name": row.get("database_name") or data.get("database_name"),
            "sql_text": row.get("sql_text") or data.get("sql_text"),
            "total_cpu_ms": data.get("total_cpu_ms", row.get("cpu_time_ms")),
            "execution_count": data.get("execution_count"),
            "total_logical_reads": data.get("total_logical_reads", row.get("logical_reads")),
            "last_execution_time": data.get("last_execution_time"),
            "plan_cached_at": data.get("plan_cached_at"),
            "query_id": data.get("query_id"),
            "plan_id": data.get("plan_id"),
            "captured_at": str(row.get("captured_at") or ""),
            "interpretation": (
                "Cumulative CPU since plan entered cache; not incident-specific."
                if source == "TOP_CPU_CACHED" else
                "Aggregated Query Store CPU over overlapping historical intervals; "
                "not proof of incident causation."
            )
        })
    candidates.sort(key=lambda x: float(x.get("total_cpu_ms") or 0), reverse=True)
    return candidates
