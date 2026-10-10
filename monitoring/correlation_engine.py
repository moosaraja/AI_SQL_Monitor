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

    return {
        "status": "ANALYSIS_COMPLETE",
        "evidence_types": sorted(evidence_types),
        "analyses": analyses
    }