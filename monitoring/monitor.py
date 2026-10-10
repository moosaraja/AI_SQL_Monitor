import time

from collector import process_snapshot


COLLECTION_INTERVAL_SECONDS = 30


def run_monitor():

    print("SQL Server monitoring started.")
    print(
        f"Collection interval: "
        f"{COLLECTION_INTERVAL_SECONDS} seconds"
    )
    print("Press Ctrl+C to stop.\n")

    while True:

        try:

            print("Collecting monitoring snapshot...")

            snapshot, evaluation = process_snapshot()

            print(
                "Snapshot collected and "
                "processed successfully."
            )

            print()

            time.sleep(
                COLLECTION_INTERVAL_SECONDS
            )

        except KeyboardInterrupt:

            print("\nMonitoring stopped by user.")
            break

        except Exception as e:

            print("Monitoring error:")
            print(e)

            print(
                f"Retrying in "
                f"{COLLECTION_INTERVAL_SECONDS} seconds..."
            )

            time.sleep(
                COLLECTION_INTERVAL_SECONDS
            )


if __name__ == "__main__":
    run_monitor()