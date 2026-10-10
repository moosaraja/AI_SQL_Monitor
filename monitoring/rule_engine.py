def evaluate_cpu(cpu_data):
    value = cpu_data.get("value", 0)

    if value > 90:
        return {
            "severity": "CRITICAL",
            "message": f"SQL Server CPU usage is {value}%"
        }

    if value >= 70:
        return {
            "severity": "WARNING",
            "message": f"SQL Server CPU usage is {value}%"
        }

    return {
        "severity": "NORMAL",
        "message": f"SQL Server CPU usage is {value}%"
    }


def evaluate_memory(memory_data):
    total = memory_data.get("total_physical_memory_gb", 0)
    available = memory_data.get("available_physical_memory_gb", 0)

    if total <= 0:
        return {
            "severity": "UNKNOWN",
            "message": "Unable to determine physical memory usage"
        }

    used_percentage = ((total - available) / total) * 100

    if used_percentage > 90:
        return {
            "severity": "CRITICAL",
            "message": f"Physical memory usage is {used_percentage:.1f}%"
        }

    if used_percentage >= 80:
        return {
            "severity": "WARNING",
            "message": f"Physical memory usage is {used_percentage:.1f}%"
        }

    return {
        "severity": "NORMAL",
        "message": f"Physical memory usage is {used_percentage:.1f}%"
    }


def evaluate_requests(requests_data):
    count = requests_data.get("count", 0)

    if count > 50:
        return {
            "severity": "CRITICAL",
            "message": f"Active request count is {count}"
        }

    if count > 20:
        return {
            "severity": "WARNING",
            "message": f"Active request count is {count}"
        }

    return {
        "severity": "NORMAL",
        "message": f"Active request count is {count}"
    }


def evaluate_blocking(blocking_data):
    count = blocking_data.get("count", 0)

    if count > 2:
        return {
            "severity": "CRITICAL",
            "message": f"{count} blocking requests detected"
        }

    if count > 0:
        return {
            "severity": "WARNING",
            "message": f"{count} blocking request(s) detected"
        }

    return {
        "severity": "NORMAL",
        "message": "No blocking requests detected"
    }


def evaluate_locks(locks_data):
    waiting_count = locks_data.get("waiting_count", 0)

    if waiting_count > 10:
        return {
            "severity": "CRITICAL",
            "message": f"{waiting_count} waiting locks detected"
        }

    if waiting_count > 0:
        return {
            "severity": "WARNING",
            "message": f"{waiting_count} waiting lock(s) detected"
        }

    return {
        "severity": "NORMAL",
        "message": "No waiting locks detected"
    }


def evaluate_snapshot(snapshot):

    return {
        "cpu": evaluate_cpu(snapshot.get("cpu", {})),
        "memory": evaluate_memory(snapshot.get("memory", {})),
        "requests": evaluate_requests(snapshot.get("requests", {})),
        "blocking": evaluate_blocking(snapshot.get("blocking", {})),
        "locks": evaluate_locks(snapshot.get("locks", {}))
    }


if __name__ == "__main__":
    print("Rule engine module loaded successfully.")