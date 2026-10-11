from cpu_rules import evaluate_cpu_history

test_cases = {
    "Normal CPU": [30, 35, 40],
    "Temporary spike": [30, 95, 40],
    "Sustained warning": [75, 80, 78],
    "Sustained critical": [91, 94, 96],
    "Recovering": [92, 60, 50],
    "Recovered": [50, 45, 40]
}

for name, values in test_cases.items():

    result = evaluate_cpu_history(values)

    print(
        f"{name}: "
        f"{result['severity']} - "
        f"{result['message']}"
    )