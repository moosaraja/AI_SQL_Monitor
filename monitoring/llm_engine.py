import os
import json
import requests
from dotenv import load_dotenv


# Load variables from the project root .env file
load_dotenv()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL"
)


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


def analyze_incident_with_llm(incident_data):

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is not configured."
        )

    if not OPENROUTER_MODEL:
        raise ValueError(
            "OPENROUTER_MODEL is not configured."
        )

    system_prompt = """
You are an experienced SQL Server DBA assistant.

Analyze the SQL Server incident using only the
incident information, investigation results, and
evidence provided.

The incident may involve different SQL Server
problems such as:

- blocking
- CPU pressure
- memory pressure
- long-running queries
- deadlocks
- I/O problems
- session problems
- other monitoring conditions

Do not assume the incident is a blocking incident.

Identify the incident type from the supplied data.

Your analysis should:

1. Identify the likely cause.
2. Explain the evidence supporting the conclusion.
3. Identify affected SQL Server resources, sessions,
   queries, or databases when available.
4. Explain the impact.
5. Recommend safe DBA investigation steps.
6. Clearly distinguish facts from assumptions.

Do not invent facts that are not present in the evidence.

Do not recommend killing sessions automatically.

Any potentially disruptive DBA action must be presented
as a step that requires DBA verification.
"""

    user_prompt = f"""
Analyze the following SQL Server incident.

Incident information and investigation results:

{json.dumps(incident_data, indent=2, default=str)}

Provide the response in this structure:

INCIDENT TYPE
PROBLEM
LIKELY CAUSE
EVIDENCE
IMPACT
RECOMMENDED DBA INVESTIGATION
CAUTIONS
"""

    headers = {
        "Authorization": (
            f"Bearer {OPENROUTER_API_KEY}"
        ),
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]


if __name__ == "__main__":

    test_incident = {
        "incident_id": 11,
        "problem": "SQL Server blocking",
        "severity": "WARNING",
        "primary_blocker": 69,
        "blocked_sessions": [
            {
                "session_id": 62,
                "database": "Vehicle",
                "wait_type": "LCK_M_IS",
                "wait_time_ms": 6959,
                "sql_text": (
                    "SELECT TOP 1 * "
                    "FROM dbo.Electric_Vehicle_Population_Data"
                )
            }
        ],
        "blocker": {
            "session_id": 69,
            "status": "sleeping",
            "program_name": (
                "Microsoft SQL Server Management Studio - Query"
            )
        }
    }

    print("\n========== LLM ANALYSIS ==========\n")

    result = analyze_incident_with_llm(
        test_incident
    )

    print(result)

    print("\n==================================\n")
