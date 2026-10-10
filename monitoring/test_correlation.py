from correlation_engine import analyze_incident


evidence = [
    {
        "evidence_type": "BLOCKING",
        "session_id": 73,
        "blocking_session_id": 71,
        "wait_type": "LCK_M_IS",
        "wait_time_ms": 217805,
        "database_name": "Vehicle"
    },
    {
        "evidence_type": "BLOCKING",
        "session_id": 52,
        "blocking_session_id": 71,
        "wait_type": "LCK_M_IS",
        "wait_time_ms": 6188,
        "database_name": "Vehicle"
    }
]


result = analyze_incident(evidence)


print("\n========== CORRELATION RESULT ==========\n")

print(result)