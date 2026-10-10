from evidence_repository import get_incident_evidence
from correlation_engine import analyze_incident
from incident_repository import get_incident
from llm_engine import analyze_incident_with_llm
from rag_engine import retrieve_relevant_knowledge
from rag_context import build_rag_context


def investigate_incident(incident_id):

    print(
        f"\nInvestigating incident #{incident_id}..."
    )

    incident = get_incident(
    incident_id
    )

    if not incident:

        return {
            "incident_id": incident_id,
            "status": "INCIDENT_NOT_FOUND",
            "message": (
                f"Incident {incident_id} "
                "was not found."
            )
        }

    # ---------------------------------------------
    # Get evidence from PostgreSQL
    # ---------------------------------------------

    evidence = get_incident_evidence(
        incident_id
    )

    #print("Moosa")
    #print("Evidence\n",evidence)
    print("\n")

    if not evidence:

        return {
            "incident_id": incident_id,
            "status": "NO_EVIDENCE",
            "message": "No evidence found for this incident."
        }

    # ---------------------------------------------
    # Run correlation
    # ---------------------------------------------

    analysis = analyze_incident(evidence)

     # Build a query for RAG retrieval
    rag_query = (
        f"SQL Server {incident['metric']} "
        f"incident in database {incident['database_name']}. "
        f"{incident['message']}"
    )

    print("\nRAG query:")
    print(rag_query)

    rag_results = retrieve_relevant_knowledge(
        rag_query,
        limit=3
    )

    print(f"\nRAG chunks retrieved: {len(rag_results)}")

    rag_context = build_rag_context(rag_results)

    llm_input = {
        "incident": incident,
        "investigation": analysis,
        "rag_context": rag_context
    }

    llm_analysis = analyze_incident_with_llm(llm_input)

    return {
        "incident_id": incident_id,
        "evidence_count": len(evidence),
        "analysis": analysis,
        "rag_results": rag_results,
        "rag_context": rag_context,
        "llm_analysis": llm_analysis
    }

def print_investigation(result):

    print("\n========================================")
    print("        SQL INCIDENT INVESTIGATION")
    print("========================================")

    #print(result)

    print(
        f"Incident ID: "
        f"{result['incident_id']}"
    )

    print(
        f"Evidence count: "
        f"{result.get('evidence_count', 0)}"
    )

    analysis = result.get(
    "analysis",
    {}
    )

    analyses = analysis.get(
    "analyses",
    {}
    )

    blocking = analyses.get(
    "blocking",
    {}
    )

    print("\n--- BLOCKING ANALYSIS ---")

    print(
        f"Status: "
        f"{blocking.get('status')}"
    )

    if blocking.get("primary_blocker"):

        print(
            f"Primary blocker: "
            f"Session "
            f"{blocking['primary_blocker']}"
        )

    print(
        f"Blocked session count: "
        f"{blocking.get('blocked_session_count', 0)}"
    )

    print(
        f"Message: "
        f"{blocking.get('message')}"
    )

    print("\nBlocker relationships:")

    for item in blocking.get("blockers", []):

        print(
            f"\n  Session {item['blocker']} "
            f"→ Session {item['blocked']}"
        )

        print(
            f"    Database: "
            f"{item.get('database_name')}"
        )

        blocked = item.get(
            "blocked_session_details",
            {}
        )

        blocker = item.get(
            "blocking_session_details",
            {}
        )

        print(
            f"    Blocked session status: "
            f"{blocked.get('status')}"
        )

        print(
            f"    Wait type: "
            f"{blocked.get('wait_type')}"
        )

        print(
            f"    Wait time: "
            f"{blocked.get('wait_time_ms')} ms"
        )

        print(
            f"    Blocked login: "
            f"{blocked.get('login_name')}"
        )

        print(
            f"    Blocked host: "
            f"{blocked.get('host_name')}"
        )

        print(
            f"    Blocked program: "
            f"{blocked.get('program_name')}"
        )

        print(
            f"    Blocking session status: "
            f"{blocker.get('status')}"
        )

        print(
            f"    Blocking login: "
            f"{blocker.get('login_name')}"
        )

        print(
            f"    Blocking host: "
            f"{blocker.get('host_name')}"
        )

        print(
            f"    Blocking program: "
            f"{blocker.get('program_name')}"
        )

        print(
            f"    SQL: "
            f"{blocked.get('sql_text')}"
        )

if __name__ == "__main__":

    # Change this to an existing incident ID
    incident_id = int(
        input("Enter incident ID: ")
    )

    result = investigate_incident(incident_id)

    print_investigation(result)

    print("\n========== AI DBA ANALYSIS ==========\n")

    print(
        result.get("llm_analysis")
    )

    print("\n=====================================\n")

    #print("\n========== INVESTIGATION RESULT ==========\n")

    