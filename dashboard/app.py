import os
import sys


from flask import Flask, render_template, request, jsonify

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(
    0,
    os.path.join(PROJECT_ROOT, "monitoring")
)

from investigation import investigate_incident
from live_health import get_live_health

from dashboard_repository import (
    get_recent_incidents,
    get_incident_summary,
    get_latest_server_health,
    get_health_history
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template(
        "investigation.html",
        result=None,
        error=None
    )


@app.route("/investigate", methods=["POST"])
def investigate():
    try:
        incident_id = int(request.form["incident_id"])

        if incident_id <= 0:
            raise ValueError("Incident ID must be positive.")

        result = investigate_incident(incident_id)

        return render_template(
            "investigation.html",
            result=result,
            error=None
        )

    except ValueError:
        return render_template(
            "investigation.html",
            result=None,
            error="Enter a valid positive incident ID."
        ), 400

    except Exception:
        app.logger.exception("Investigation failed")

        return render_template(
            "investigation.html",
            result=None,
            error="Investigation failed. Check the Flask console for details."
        ), 500

@app.route("/incidents")
def incidents():
    incident_rows = get_recent_incidents()
    summary = get_incident_summary()

    return render_template(
        "incidents.html",
        incidents=incident_rows,
        summary=summary
    )

@app.route("/api/incidents")
def api_incidents():

    incidents = get_recent_incidents()
    summary = get_incident_summary()

    return jsonify({
        "incidents": incidents,
        "summary": summary
    })

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/api/health")
def api_health():

    result = get_latest_server_health()

    if not result:
        return jsonify({
            "status": "NO_DATA"
        })

    return jsonify({
        "status": "OK",
        "snapshot_id": result["id"],
        "server_name": result["server_name"],
        "database_name": result["database_name"],
        "metrics": result["snapshot"]
    })

@app.route("/api/health/live")
def api_health_live():
    try:
        metrics = get_live_health()
        return jsonify({"status": "OK", "metrics": metrics})
    except Exception:
        app.logger.exception("Live health collection failed")
        return jsonify({"status": "ERROR", "message": "Live health unavailable"}), 503


@app.route("/api/health/history")
def api_health_history():

    rows = get_health_history(limit=60)

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True,port=1111)   