from correlation.blocking_analyzer import analyze_blocking
from correlation.deadlock_analyzer import analyze_deadlock


ANALYZER_REGISTRY = {
    "BLOCKING": analyze_blocking,
    "DEADLOCK": analyze_deadlock,
}


def get_analyzer(evidence_type):
    return ANALYZER_REGISTRY.get(evidence_type.upper())