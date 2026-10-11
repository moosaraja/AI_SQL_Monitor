CPU_WARNING_THRESHOLD = 30
CPU_CRITICAL_THRESHOLD = 50
CPU_RECOVERY_THRESHOLD = 25

REQUIRED_SAMPLES = 3


def evaluate_cpu_history(cpu_values):
    """
    Evaluate consecutive CPU measurements.

    cpu_values:
        List of CPU percentages, oldest to newest.

    Returns:
        severity and message.
    """

    if len(cpu_values) < REQUIRED_SAMPLES:
        return {
            "severity": "PENDING",
            "message": "Waiting for sufficient CPU samples"
        }

    recent = cpu_values[-REQUIRED_SAMPLES:]

    if all(
        cpu >= CPU_CRITICAL_THRESHOLD
        for cpu in recent
    ):
        return {
            "severity": "CRITICAL",
            "message": (
                f"SQL Server CPU remained above "
                f"{CPU_CRITICAL_THRESHOLD}% "
                f"for {REQUIRED_SAMPLES} readings"
            )
        }

    if all(
        cpu >= CPU_WARNING_THRESHOLD
        for cpu in recent
    ):
        return {
            "severity": "WARNING",
            "message": (
                f"SQL Server CPU remained above "
                f"{CPU_WARNING_THRESHOLD}% "
                f"for {REQUIRED_SAMPLES} readings"
            )
        }

    if all(
        cpu < CPU_RECOVERY_THRESHOLD
        for cpu in recent
    ):
        return {
            "severity": "OK",
            "message": "SQL Server CPU returned to normal"
        }

    return {
        "severity": "PENDING",
        "message": "CPU readings have not met a sustained threshold"
    }